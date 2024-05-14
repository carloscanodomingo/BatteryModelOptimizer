#!/bin/bash
#SBATCH -D .
#SBATCH --job-name=test_script
#SBATCH --cpus-per-task=$3
#SBATCH --ntasks=1
#SBATCH --time=02:00:00
#SBATCH --qos=gp_debug
#SBATCH --account=bsc21

# Find our own location.
BSC_USER="bsc021148"
BSC_GROUP="bsc21"
BASEDIR="$BSC_GROUP/$BSC_USER"
BINDIR=$(dirname "$(readlink -f "$(type -P $0 || echo $0)")")
OUTDIR="/gpfs/scratch/$BASEDIR"
module load miniconda
module load gcc
module load R/4.3.2
source activate base
conda activate pybamm
echo $IRACE_HOME
export IRACE_HOME="/gpfs/home/bsc21/bsc021148/R/x86_64-pc-linux-gnu-library/4.3/irace"
# Replace <IRACE_HOME> with the irace installation path
#
export PATH=${IRACE_HOME}/bin/:$PATH
export R_LIBS=${IRACE_HOME}/bin:$R_LIBS
export NAME_ID="TEST_BASE"
export EV_DATAPATH="/gpfs/projects/bsc21/bsc021148/nextbat/phase_1/data/battery.h5"
export PYBAMM_RESULTS_PATH="/gpfs/projects/bsc21/bsc021148/nextbat/phase_1/irace/$NAME_ID/results"
mkdir -p $PYBAMM_RESULTS_PATH
export INPUTS_PATH="/gpfs/projects/bsc21/bsc021148/nextbat/phase_1/irace/$NAME_ID/inputs"
mkdir -p $INPUTS_PATH
#Tell R where to find R_LIBS_USER
# Use the following line only if local installation was forced
export OMP_NUM_THREADS=$3

export SBATCH_OVERCOMMIT=1
srun --qos=gp_debug --account=bsc21 ./BMO_CLI.py $1 2 30 --negative_current_collector_thickness 1.2e-05 --negative_electrode_thickness 8.52e-05 --initial_temperature 270 --n_cycles_per_experiments 1 --n_experiments 10 --battery_id W04 --verbose True --n_cycle $2 --log_to_file False
