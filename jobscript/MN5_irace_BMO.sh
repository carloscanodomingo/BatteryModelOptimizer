#!/bin/bash

cleanup_logs() {
    echo "Removing all .log files..."
    find . -type f -name "*.log" -exec rm -f {} \;
}
backup_rdata_files() {
    local extension=".Rdata"
    local counter=1
    local base_name="${ID}_irace"
    export BASE_LOG_FILE="${base_name}${extension}"
    local backup_file="${base_name}_backup${counter}${extension}"

    RECOVERY_OPTION=""
    # Check if baseirace.Rdata exists
    if [ -f $BASE_LOG_FILE ]; then
        # Find the next available backup file number
        while [ -f "$backup_file" ]; do
            ((counter++))
            backup_file="${base_name}${counter}${extension}"
        done

        # Move the file to its new backup name
        echo "Moving base_file to $backup_file"
        mv $BASE_LOG_FILE "$backup_file"
        if [ "$RECOVERY_MODE" -eq 1 ]; then
          RECOVERY_OPTION="--recovery-file \"./$backup_file\""
        fi
    fi
}
load_param() {
    export BASE_PARAM_FILE="param.json"

    # Check if baseirace.Rdata exists
    if [ -f $BASE_PARAM_FILE ]; then
        # Find the next available backup file number
        #
        #
        echo "Loading Param file $BASE_PARAM_FILE"
          export BASE_PARAM_PATH="--base_param_path \"./$BASE_PARAM_FILE\""
        else
          export BASE_PARAM_PATH=""
          echo "Not found param file"
        fi
}



irace_main() {
    JOBNAME=$NAME_ID
    sbatch  <<EOF
#!/bin/bash
#SBATCH -D .
#SBATCH --job-name=$JOBNAME
#SBATCH --cpus-per-task=1
#SBATCH --ntasks=$NB_PARALLEL_PROCESS
#SBATCH --time=$TIME
#SBATCH --qos=$QOS
#SBATCH --account=bsc21

# Find our own location.
ID="MPI"
BSC_USER="bsc021148"
BSC_GROUP="bsc21"
BASEDIR="$BSC_GROUP/$BSC_USER"
BINDIR=$(dirname "$(readlink -f "$(type -P $0 || echo $0)")")
OUTDIR="/gpfs/scratch/$BASEDIR"
module purge 
module load oneapi 
module load gcc
module load R
module load anaconda
source /apps/GPP/ANACONDA/2023.07/etc/profile.d/conda.sh
conda activate pybamm
conda info --envs
# Tell R where to find R_LIBS_USER
# Use the following line only if local installation was forced
export OMP_NUM_THREADS=1
ulimit -s unlimited
export SBATCH_OVERCOMMIT=1
export FI_PROVIDER=verbs

mpirun -n 1 $IRACE_HOME/bin/irace --log-file $BASE_LOG_FILE --mpi 1 --scenario=$SCENARIE_FILE --parallel=$NB_SLAVES $PARAM_OPTION --seed $SEED $RECOVERY_OPTION $PARAMS 
EOF
}


usage() {
    cat <<EOF
Usage: $0 --parallel NUM [--mode MODE] [--seed NUM] [--id STRING] [--debug] [--recovery] [IRACE PARAMS]

Parameters:
 --parallel NUM    Specify the number of parallel jobs. Must be greater than 1.
 --mode MODE       Set the operational mode. Options are 'DB' for Degradation Base, 'DF' for Degradation Full,
                   'ALL' for All Scenarios, 'SIMPLE' for Simple Scenarios, or 'ND' (non-degradation) by default.
 --seed NUM        Set the seed for each run. The seed for run i will be SEED+i-1. Default is 1234567.
 --id STRING       Specify a unique identifier for the session. Default is 'TEST_CASE'.
 --debug           Enable debug mode, which uses different time and QoS settings.
 --recovery        Enable recovery mode to recover from previous runs.
 IRACE PARAMS      Additional parameters for IRACE. These are passed directly to the IRACE command.

Examples:
 $0 --parallel 4 --mode SIMPLE --seed 1000 --id "experiment_1" --debug --recovery --config irace.config
 $0 --parallel 8 --mode DF --seed 2000 --irace "--parameter-file params.txt --test-type 0"

Note: Replace '--irace' with any IRACE-specific parameters you need to pass.

EOF
    exit 1
}
SEED=1234567
PARAMS=
DEBUG_MODE=0
SIMPLE_MODE=0
RECOVERY_MODE=0

ALL_MODE=0
LOAD_PARA_MODE=0
MODE=0
ID=TEST_CASE
while [ $# -gt 0 ]; do
    case "$1" in
        --parallel) shift; NB_SLAVES="$1"; shift;;
        --mode)  shift; MODE=$1; shift;;
        --seed) shift; SEED="$1"; shift;;
        --id) shift; ID="$1"; shift;;
        --debug) DEBUG_MODE=1; shift;;
        --recovery) RECOVERY_MODE=1; shift;;
        *) PARAMS="$PARAMS $1"; shift;;# terminate case

    esac
done
if [ -z "$NB_SLAVES" ] || [ "$NB_SLAVES" -lt 2 ]; then
    echo "Error: --parallel must be larger than 1" >&2
    exit 1
fi

# RDATA_FILE=$(find . -maxdepth 1 -name '*.Rdata' -print -quit)
# if [ "$LOAD_PARA_MODE" -eq 1 ]; then
#   load_param
# fi
echo $MODE
case "$MODE" in
    "DB") SCENARIE_FILE="scenaries/scenaries_degradation_base.txt";;
    "DF") SCENARIE_FILE="scenaries/scenaries_degradation.txt";;
    "ALL") SCENARIE_FILE="scenaries/scenaries_all.txt";;
    "SIMPLE")SCENARIE_FILE="scenaries/scenaries_simple.txt";; 
    "ND")    SCENARIE_FILE="scenaries/scenaries_non_degradation.txt";;
    *) usage;;
  esac

if [ "$DEBUG_MODE" -eq 1 ]; then
  TIME="02:00:00"
  QOS="gp_debug"
else
  TIME="48:00:00"
  QOS="gp_bsccase"
fi
# Call cleanup_logs function at the beginning or end of the script depending on your needs
cleanup_logs
backup_rdata_files
export IRACE_HOME="/gpfs/home/bsc/bsc021148/orca/R_local/irace"
export PATH=${IRACE_HOME}/bin/:$PATH
export R_LIBS=${IRACE_HOME}/bin:$R_LIBS
export EV_DATAPATH="/gpfs/projects/bsc21/bsc021148/nextbat/phase_1/data/battery.h5"

# Replace <IRACE_HOME> with the irace installation path
NAME_ID="IRACE_$ID"
export PYBAMM_RESULTS_PATH="/gpfs/projects/bsc21/bsc021148/nextbat/phase_1/irace/$NAME_ID/results"
mkdir -p $PYBAMM_RESULTS_PATH
export INPUTS_PATH="/gpfs/projects/bsc21/bsc021148/nextbat/phase_1/irace/$NAME_ID/inputs"
export I_MPI_PMI_LIBRARY="/gpfs/home/bsc/bsc021148/R/x86_64-pc-linux-gnu-library/4.3/Rmpi/libs/Rmpi.so"
mkdir -p $INPUTS_PATH
let NB_PARALLEL_PROCESS=NB_SLAVES+1
echo $RECOVERY_OPTION
irace_main 1



