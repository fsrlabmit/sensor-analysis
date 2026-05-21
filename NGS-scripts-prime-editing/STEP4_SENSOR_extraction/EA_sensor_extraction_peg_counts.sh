#!/bin/bash
#SBATCH -N 1                      # Number of nodes. You must always set -N 1 unless you receive special instruction from the system admin
#SBATCH -n 1                      # Number of tasks (really number of CPU Cores/task). Don't specify more than 16 unless approved by the system admin
#SBATCH --array=1-32    #change this to match up with the number of parallel computing jobs; also generate a config file 
#SBATCH --mail-type=END           # Type of email notification- BEGIN,END,FAIL,ALL. Equivalent to the -m option in SGE 
#SBATCH --mail-user=kexindon@mit.edu           # Email to which notifications will be sent. Equivalent to the -M option in SGE. You must replace [] with your email address.
#SBATCH --exclude=c[5-22]
#SBATCH --nice=100000
#############################################
srun --pty bash
cd /net/bmc-lab2/data/lab/sanchezrivera/kexindong/
# module load miniconda3/v4
# source /home/software/conda/miniconda3/bin/condainit

# mkdir ~/micromamba
# curl -Ls https://micro.mamba.pm/install.sh | bash -s -- -b -u -p ~/micromamba
# echo 'export PATH=$HOME/micromamba/bin:$PATH' >> ~/.bashrc
# source ~/.bashrc
eval "$(micromamba shell hook --shell bash)"
micromamba activate sensor_env
#go to correct directory
cd /net/bmc-lab2/data/lab/sanchezrivera/kexindong/250730Hem

#access the config file
#NEED TO CHANGE THE CONFIG FILE FOR YOUR SPECIFIC RUN
config=./CONFIG_EA_JA_SENSOR_EXTRACTION.txt

# Extract R1_FILE name for the current $SLURM_ARRAY_TASK_ID
R1_FILE=$(awk -v ArrayTaskID=$SLURM_ARRAY_TASK_ID '$1==ArrayTaskID {print $2}' $config)
R2_FILE=$(awk -v ArrayTaskID=$SLURM_ARRAY_TASK_ID '$1==ArrayTaskID {print $3}' $config)
folder_name=$(awk -v ArrayTaskID=$SLURM_ARRAY_TASK_ID '$1==ArrayTaskID {print $4}' $config)

# Paramters for the script (NO SPACES ALLOWED)
splitby='protospacer'
proto_mismatches_allowed=2
bc_len=8
sensor_len=55

python3 EA_sensor_extraction_peg_counts.py pegRNA_library_EA_LUAD_column_renamed.csv ${R1_FILE} ${R2_FILE} ${splitby} ${proto_mismatches_allowed} ${bc_len} ${sensor_len} -o ${folder_name}