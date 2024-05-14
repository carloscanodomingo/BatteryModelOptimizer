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
        if [ "$RECOVERY_MODE" -eq 1 ]; then
          while [ -f "$backup_file" ]; do
              ((counter++))
              backup_file="${base_name}${counter}${extension}"
          done

          # Move the file to its new backup name
          echo "Moving base_file to $backup_file"
          mv $BASE_LOG_FILE "$backup_file"
          RECOVERY_OPTION="--recovery-file \"./$backup_file\""
        else
          echo "Found Rdata file. Not Recovery mode set deleting $BASE_LOG_FILE"
          rm $BASE_LOG_FILE 
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

# Find our own location.
ID="MPI"
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
# Tell R where to find R_LIBS_USER
# Use the following line only if local installation was forced
export OMP_NUM_THREADS=1
ulimit -s unlimited
export SBATCH_OVERCOMMIT=1
mpiexec -n 1 $IRACE_HOME/bin/irace --log-file $BASE_LOG_FILE --mpi 1 --scenario=$SCENARIE_FILE --parallel=$NB_SLAVES $PARAM_OPTION --seed $SEED $RECOVERY_OPTION $PARAMS 
EOF
}


usage() {
    cat <<EOF
Usage: $0 --parallel NUM [--seed NUM] [IRACE PARAMS]

Parameters:
 --parallel NUM    number of parallel jobs (value in scenario.txt is ignored)
 --seed NUM        the seed of each run i will be SEED+i-1 (default: 1234567)
 IRACE PARAMS      additional parameters for irace.
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
DEGRADATION_MODE=0
ID=TEST_CASE
while [ $# -gt 0 ]; do
    case "$1" in
        --parallel) shift; NB_SLAVES="$1"; shift;;
        --seed) shift; SEED="$1"; shift;;
        --id) shift; ID="$1"; shift;;
        --debug) DEBUG_MODE=1; shift;;
        --simple) SIMPLE_MODE=1; shift;;
        --recovery) RECOVERY_MODE=1; shift;;
        --all) ALL_MODE=1; shift;;
        --degradation) DEGRADATION_MODE=1; shift;;
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

if [ "$SIMPLE_MODE" -eq 1 ]; then
  SCENARIE_FILE="scenaries/scenaries_simple.txt" 
else
    if [ "$DEGRADATION_MODE" -eq 1 ]; then
      SCENARIE_FILE="scenaries/scenaries_degradation.txt" 
    else
    if [ "$ALL_MODE" -eq 1 ]; then
      SCENARIE_FILE="scenaries/scenaries_all.txt"
    else
      SCENARIE_FILE="scenaries/scenaries_non_degradation.txt" 
    fi
  fi
fi

if [ "$DEBUG_MODE" -eq 1 ]; then
  TIME="02:00:00"
  QOS="debug"
else
  TIME="48:00:00"
  QOS="bsc_case"
fi
# Call cleanup_logs function at the beginning or end of the script depending on your needs
cleanup_logs
backup_rdata_files
export IRACE_HOME="/gpfs/home/bsc21/bsc21148/R/x86_64-pc-linux-gnu-library/4.3/irace"
export PATH=${IRACE_HOME}/bin/:$PATH
export R_LIBS=${IRACE_HOME}/bin:$R_LIBS
export EV_DATAPATH="/gpfs/projects/bsc21/bsc21148/nextbat/phase_1/data/battery.h5"

# Replace <IRACE_HOME> with the irace installation path
NAME_ID="IRACE_$ID"
export PYBAMM_RESULTS_PATH="/gpfs/projects/bsc21/bsc21148/nextbat/phase_1/irace/$NAME_ID/results"
mkdir -p $PYBAMM_RESULTS_PATH
export INPUTS_PATH="/gpfs/projects/bsc21/bsc21148/nextbat/phase_1/irace/$NAME_ID/inputs"
mkdir -p $INPUTS_PATH
let NB_PARALLEL_PROCESS=NB_SLAVES+1
echo $RECOVERY_OPTION
irace_main 1



