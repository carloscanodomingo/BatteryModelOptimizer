#!/usr/bin/env bash
###############################################################################
# This script launches several runs of irace in parallel on a SLURM cluster.
# Execute without parameters to see usage.
###############################################################################
set -e
set -o pipefail
# Find our own location.
BINDIR=$(dirname "$(readlink -f "$(type -P $0 || echo $0)")")
IRACE="$BINDIR/irace"

# This function launches one run of irace.
irace_main() {
    # We would like to use $BASHPID here, but OS X version of bash does not
    # support it.
    JOBNAME="irace-$$-$1"
    # You may need to CUSTOMIZE this part according to the setup of your own cluster: https://slurm.schedmd.com
    exec sbatch <(cat<<EOF

#!/bin/bash
#SBATCH -D .
#SBATCH --error=$EXECDIR/irace.stderr
#SBATCH --output=$EXECDIR/irace.stdout
#SBATCH -J $JOBNAME
#SBATCH --nodes=1
#SBATCH --array=1-$N_RUNS
# Number of desired cpus:
#SBATCH --cpus-per-task=$N_CPUS
#SBATCH --time=48:00:00
#SBATCH --qos=bsc_case
# Find our own location.
BSC_USER="bsc21148"
BSC_GROUP="bsc21"
BASEDIR="$BSC_GROUP/$BSC_USER"
BINDIR=$(dirname "$(readlink -f "$(type -P $0 || echo $0)")")
OUTDIR="/gpfs/scratch/$BASEDIR"
module load miniconda3
module load gcc
module load pcre2
module load R/4.3.0
source activate base
conda activate pybamm

export IRACE_HOME="/gpfs/home/bsc21/bsc21148/R/x86_64-pc-linux-gnu-library/4.3/irace"
export PATH=${IRACE_HOME}/bin/:$PATH
export EV_DATAPATH="/gpfs/home/bsc21/bsc21148/data/battery.h5"
export PYBAMM_RESULTS_PATH="/gpfs/scratch/bsc21/bsc21148/irace"
# Tell R where to find R_LIBS_USER
# Use the following line only if local installation was forced
export R_LIBS=${R_LIBS_USER}:${R_LIBS}
export OMP_NUM_THREADS=1
IRACE=$IRACE_HOME/bin/irace


# To load some software (you can show the list with 'module avail'):
run=\$SLURM_ARRAY_TASK_ID
exec $IRACE --exec-dir=$EXECDIR --seed $RUNSEED $PARAMS
EOF
                 )
}
## END OF CUSTOMIZATION

error () {
    echo "$0: error: $@" >&2
    exit 1
}

usage() {
    cat <<EOF
Usage: $0 N[-M] [EXECDIR] --parallel NUM [--seed NUM] [IRACE PARAMS]

Parameters:
 N             an integer giving the number of repetitions of irace
               or a sequence N-M giving which repetitions to redo.
 EXECDIR       job M will use EXECDIR-M directory (default: execdir)
               as the execDir (--exec-dir) parameter of irace.
 --parallel NUM    number of parallel jobs (value in scenario.txt is ignored)
 --seed NUM        the seed of each run i will be SEED+i-1 (default: 1234567)
 IRACE PARAMS  additional parameters for irace.
EOF
    exit 1
}

# Issue usage if no parameters are given.
test $# -ge 1 || usage

# Number of repetitions of iRace
# REPETITIONS=$1
# shift
# START=1
# if [[ "$REPETITIONS" =~ ^([0-9]+)-([0-9]+)$ ]] ; then
#     START=${BASH_REMATCH[1]}
#     REPETITIONS=${BASH_REMATCH[2]}
# elif ! [[ "$REPETITIONS" =~ ^[0-9]+$ ]] ; then
#     error "number of repetitions must be an integer"
# fi

# execDir (--exec-dir) directory
EXECDIR_PREFIX=${1:-execdir}
shift
SEED=1234567
N_CPUS=1
PARAMS=
while [ $# -gt 0 ]; do
    case "$1" in
        --parallel) shift; N_CPUS="$1"; shift;;
        --seed) shift; SEED="$1"; shift;;
        *) PARAMS="$PARAMS $1"; shift;;# terminate case
    esac
done

# # FIXME: Use SBATCH --array=$START-$REPETITIONS
# N_RUNS=1
# for i in $(seq $START $REPETITIONS); do
EXECDIR=$(printf '%s-%002d' ${EXECDIR_PREFIX} 1)
echo "execution directory: $EXECDIR"
rm -rf $EXECDIR
mkdir -p $EXECDIR
let RUNSEED=SEED+i-1 
irace_main $(printf '%002d' $i) &
sleep 1
# done
