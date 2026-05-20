# NOT meant to be executed end-to-end
# COPY LINES MANUALLY

# Sets up micromamba envs (sensor_env for STEP4, and crispresso_env for STEP5 & 6) on the cluster.

# ---- 1. Start an interactive session and go to your working dir ----
srun --pty bash
cd /net/bmc-lab2/data/lab/sanchezrivera/$USER/

# ---- 2. One-time micromamba install (skip if already installed) ----
mkdir ~/micromamba
curl -Ls https://micro.mamba.pm/install.sh | bash -s -- -b -u -p ~/micromamba
echo 'export PATH=$HOME/micromamba/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# ---- 3. Create the envs from the YAML specs ----
micromamba create -n crispresso_env -f ./conda_environment_configuration_file/crispresso_env.yml
micromamba create -n sensor_env     -f ./conda_environment_configuration_file/sensor_env.yml

# ---- 4. Activate the env you need ----
micromamba activate crispresso_env
micromamba activate sensor_env