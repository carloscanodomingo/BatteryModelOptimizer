#!/bin/bash

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



process_value() {
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
module load anaconda
source /apps/GPP/ANACONDA/2023.07/etc/profile.d/conda.sh
conda activate pybamm
conda info --envs
# Tell R where to find R_LIBS_USER
# Use the following line only if local installation was forced
ulimit -s unlimited
export SBATCH_OVERCOMMIT=1
echo "N CYCLES IS $N_CYCLES"
./ScriptGetPerformance.py  --battery_id $1  --param_path $2 --n_cycles  $N_CYCLES
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
LOAD_PARA_MODE=0
DEGRADATION_MODE=0
NB_PARALLEL_PROCESS=1
ID=TEST_CASE
while [ $# -gt 0 ]; do
    case "$1" in
        --parallel) shift; NB_PARALLEL_PROCESS=$1; shift;;
        --param_folder_path) shift; PARAM_FOLDER_PATH="$1"; shift;;
        --id) shift; ID="$1"; shift;;
        --debug) DEBUG_MODE=1; shift;;
        --n_cycles) shift; N_CYCLES=$1; shift;;
        *) PARAMS="$PARAMS $1"; shift;;# terminate case

    esac
done


if [ "$DEBUG_MODE" -eq 1 ]; then
  TIME="02:00:00"
  QOS="gp_debug"
else
  TIME="48:00:00"
  QOS="gp_bsccase"
fi
export N_CYCLES
export NB_PARALLEL_PROCESS
echo $NB_PARALLEL_PROCESS
# Call cleanup_logs function at the beginning or end of the script depending on your needs
export EV_DATAPATH="/gpfs/projects/bsc21/bsc021148/nextbat/phase_1/data/battery.h5"
# Replace <IRACE_HOME> with the irace installation path
NAME_ID="episode_$ID"
export ScriptFile="/home/bsc/bsc021148/nextbat/phase_1/ScriptGetPerformance.py"
export RESULT_PATH="/gpfs/projects/bsc21/bsc021148/nextbat/phase_1/episode/$NAME_ID/results"
mkdir -p $RESULT_PATH
export INPUTS_PATH="/gpfs/projects/bsc21/bsc021148/nextbat/phase_1/episode/$NAME_ID/inputs"

export I_MPI_PMI_LIBRARY="/gpfs/home/bsc/bsc021148/R/x86_64-pc-linux-gnu-library/4.3/Rmpi/libs/Rmpi.so"
mkdir -p $INPUTS_PATH
export N_CYCLES
# Initialize an array with full paths of files
mapfile -t param_files < <(find "$PARAM_FOLDER_PATH" -type f -name "*.json")
values=("W04" "W08" "W09" "W10")
# Iterate over the array, using full paths
for file in "${param_files[@]}"; do
  for value in "${values[@]}"; do
	  echo "VALUE $value File $file"
    process_value "$value" "$file" 
  done
done



