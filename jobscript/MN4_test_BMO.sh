#!/bin/bash
#SBATCH -D .
#SBATCH --job-name=pybamm
#SBATCH --error=%jSweep.err
#SBATCH --output=%jSweep.out
#SBATCH --nodes=1
#SBATCH --cpus-per-task=300
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

# Replace <IRACE_HOME> with the irace installation path
export IRACE_HOME="/gpfs/home/bsc21/bsc21148/R/x86_64-pc-linux-gnu-library/4.3/irace"
export PATH=${IRACE_HOME}/bin/:$PATH
export EV_DATAPATH="/gpfs/home/bsc21/bsc21148/data/battery.h5"
export PYBAMM_RESULTS_PATH="/gpfs/scratch/bsc21/bsc21148/irace"
# Tell R where to find R_LIBS_USER
# Use the following line only if local installation was forced
export R_LIBS=${R_LIBS_USER}:${R_LIBS}
export OMP_NUM_THREADS=1

$IRACE_HOME/bin/irace --scenario="scenaries/scenaries_non_degradation.txt" --parallel=42
 #srun ./BMO_CLI.py 1 2 30 --negative_current_collector_thickness 1.2e-05 --negative_electrode_thickness 8.52e-05 --initial_temperature 270 --n_cycles_per_experiments 1 --n_experiments 2 --battery_id W07 --verbose True
