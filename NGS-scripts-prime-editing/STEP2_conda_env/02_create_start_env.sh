srun --pty bash

cd /net/bmc-lab2/data/lab/sanchezrivera/kexindong

module load miniconda3/v4
source /home/software/conda/miniconda3/bin/condainit

# conda env create -n sensor_env -f ./sensor_env.yml
conda env create -n crispresso_env -f ./conda_environment_configuration_file/crispresso_env.yml
conda env create -n sensor_env -f ./conda_environment_configuration_file/sensor_env.yml

# mkdir ~/micromamba
# curl -Ls https://micro.mamba.pm/install.sh | bash -s -- -b -u -p ~/micromamba
# echo 'export PATH=$HOME/micromamba/bin:$PATH' >> ~/.bashrc
# source ~/.bashrc
micromamba create -n crispresso_env -f ./conda_environment_configuration_file/crispresso_env.yml
micromamba create -n sensor_env -f ./conda_environment_configuration_file/sensor_env.yml


#----then in the future to actiavte-------
# module load miniconda3/v4
# source /home/software/conda/miniconda3/bin/condainit

conda activate sensor_env
micromamba activate sensor_env
micromamba activate crispresso_env

# conda activate crispresso_env

cd /net/bmc-lab2/data/lab/sanchezrivera/kexindong/