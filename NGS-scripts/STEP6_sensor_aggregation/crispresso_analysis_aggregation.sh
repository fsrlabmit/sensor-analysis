#!/bin/bash
#SBATCH -N 1                      # Number of nodes. You must always set -N 1 unless you receive special instruction from the system admin
#SBATCH -n 1                      # Number of tasks (really number of CPU Cores/task). Don't specify more than 16 unless approved by the system admin
#SBATCH --array=1-188    #change this to match up with the number of parallel computing jobs; also generate a config file 
#SBATCH --mail-type=END           # Type of email notification- BEGIN,END,FAIL,ALL. Equivalent to the -m option in SGE 
#SBATCH --mail-user=kexindon@mit.edu           # Email to which notifications will be sent. Equivalent to the -M option in SGE. You must replace [] with your email address.
#SBATCH --exclude=c[5-22]
#SBATCH --nice=100000
#############################################
cd /net/bmc-lab2/data/lab/sanchezrivera/kexindong/
#go to correct directory
eval "$(micromamba shell hook --shell bash)"
micromamba activate crispresso_env

cd /net/bmc-lab2/data/lab/sanchezrivera/kexindong/251030Hem

#access the config file
#config=./config.txt
config=./CONFIG_BALL_VALIDATION_SCREEN.txt

# Extract R1_FILE name for the current $SLURM_ARRAY_TASK_ID
#R1 and R2 File unnecessary here, but didn't want to change the config file
R1_FILE=$(awk -v ArrayTaskID=$SLURM_ARRAY_TASK_ID '$1==ArrayTaskID {print $2}' $config)
R2_FILE=$(awk -v ArrayTaskID=$SLURM_ARRAY_TASK_ID '$1==ArrayTaskID {print $3}' $config)
folder_name=$(awk -v ArrayTaskID=$SLURM_ARRAY_TASK_ID '$1==ArrayTaskID {print $4}' $config)

python3 crispresso_analysis_aggregation.py FINAL_focused_library.csv ${folder_name} crispresso_quant_blank.csv

#test 
#echo "This is array task ${SLURM_ARRAY_TASK_ID}, the sample name is ${R1_FILE} and ${R2_FILE} and the output folder is ${folder_name}" >> output.txt