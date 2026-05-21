#!/bin/bash
#SBATCH -N 1                      # Number of nodes. You must always set -N 1 unless you receive special instruction from the system admin
#SBATCH -n 1                      # Number of tasks (really number of CPU Cores/task). Don't specify more than 16 unless approved by the system admin
#SBATCH --array=1-188    #change this to match up with the number of parallel computing jobs; also generate a config file 
#SBATCH --mail-type=END           # Type of email notification- BEGIN,END,FAIL,ALL. Equivalent to the -m option in SGE 
#SBATCH --mail-user=XXX@mit.edu           # Email to which notifications will be sent. Equivalent to the -M option in SGE. You must replace [] with your email address.
#SBATCH --exclude=c[5-22]
#SBATCH --nice=100000

#############################################
# Revised version 2
# 2026 March 10, KD
# QC strategy updated to check only required regions
# added a threshold for quality for each base
#############################################

# enter interactive session
srun --pty bash

# activate the environment
cd /net/bmc-lab2/data/lab/sanchezrivera/kexindong/
eval "$(micromamba shell hook --shell bash)"
micromamba activate sensor_env

#####if using conda environment#####
# cd /net/bmc-lab2/data/lab/sanchezrivera/kexindong/
# module load miniconda3/v4
# source /home/software/conda/miniconda3/bin/condainit
# conda activate sensor_env
#####if using conda environment#####

#go to the sequence folder
cd /net/bmc-lab2/data/lab/sanchezrivera/kexindong/251030Hem

#access the config file
config=./CONFIG_BALL_VALIDATION_SCREEN.txt

# Extract file names
R1_FILE=$(awk -v ArrayTaskID=$SLURM_ARRAY_TASK_ID '$1==ArrayTaskID {print $2}' $config)
R2_FILE=$(awk -v ArrayTaskID=$SLURM_ARRAY_TASK_ID '$1==ArrayTaskID {print $3}' $config)
folder_name=$(awk -v ArrayTaskID=$SLURM_ARRAY_TASK_ID '$1==ArrayTaskID {print $4}' $config)

# Paramters for the script (NO SPACES ALLOWED)
splitby='protospacer' #options: 'protospacer', 'barcode'; recommend using 'protospacer'
proto_mismatches_allowed=2
bc_len=15
sensor_len=42
quality_check_mode='region_average' #options: 'full_average', 'region_average', 'region_average_and_threshold'; recommend using 'region_average' or 'region_average_and_threshold'

python3 sensor_extraction_42nt_trimming_quality.py FINAL_focused_library.csv ${R1_FILE} ${R2_FILE} ${splitby} ${proto_mismatches_allowed} ${bc_len} ${sensor_len} ${quality_check_mode} -o ${folder_name}