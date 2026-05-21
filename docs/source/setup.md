# Setup

```{contents}
:local:
:depth: 2
```

---

## STEP 1 — Download NGS data

[`NGS-scripts/STEP1_download_data/STEP1_download_data.sh`](https://github.com/fsrlabmit/sensor-analysis/blob/main/NGS-scripts/STEP1_download_data/STEP1_download_data.sh)

Cheatsheet of commands.

Log into Luria, start an interactive session, then `rsync` the sequencing core's data into your lab folder:

```bash
ssh youraccount@luria.mit.edu
srun --pty bash
cd /net/bmc-lab2/data/lab/sanchezrivera/$USER/
srun rsync -av /net/bmc-pub17/data/bmc/public/datahub/datafolder \
               /net/bmc-lab2/data/lab/sanchezrivera/$USER/
```

```{important}
`$USER` = the name of your existing folder on the cluster; this step won't work otherwise.

Also replace the source path with the one provided in the sequencing core email.
```

---

## STEP 2 — Create micromamba environments

[`NGS-scripts/STEP2_conda_env/02_create_start_env.sh`](https://github.com/fsrlabmit/sensor-analysis/blob/main/NGS-scripts/STEP2_conda_env/02_create_start_env.sh)

In order to run these scripts, you need to create 2 conda/micromamba environments. Conda/micromamba  environments are essentially sandboxes that allow python scripts to run while referencing all of their required packages/package versions. These environments allow the scripts to run on the cluster, otherwise you would get errors of "package not installed" when trying to import the packages.

```{hint}
A lot of us have had trouble configuring conda environments on the cluster — solver runs that hang for hours, mysterious dependency conflicts, and envs that take forever to create. I switched to **micromamba** here because it's a drop-in replacement that uses the same `.yml` spec files but resolves and installs environments dramatically faster (often minutes instead of hours). If you've never set it up before, the one-time install commands at the top of `02_create_start_env.sh` will get you going; skip them if already installed.
```

Two micromamba envs will be needed:

```{list-table}
:header-rows: 1
:widths: 20 40 40

* - Env
  - Used in
  - Spec file
* - `sensor_env`
  - STEP4 (sensor extraction)
  - [`sensor_env.yml`](https://github.com/fsrlabmit/sensor-analysis/blob/main/NGS-scripts/STEP2_conda_env/sensor_env.yml)
* - `crispresso_env`
  - STEP5 (sensor analysis), STEP6 (sensor aggregation)
  - [`crispresso_env.yml`](https://github.com/fsrlabmit/sensor-analysis/blob/main/NGS-scripts/STEP2_conda_env/crispresso_env.yml)
```

To create these environments, **copy these .yml files to your own folder on the server** (I recommend generating a "conda_envs" folder to store all the .yml files), and then run the commands in [`NGS-scripts/STEP2_conda_env/02_create_start_env.sh`](https://github.com/fsrlabmit/sensor-analysis/blob/main/NGS-scripts/STEP2_conda_env/02_create_start_env.sh) by copying lines as commands manually.

To login cluster:

```bash
srun --pty bash
cd /net/bmc-lab2/data/lab/sanchezrivera/$USER/
```

`$USER` = the name of your existing folder on the cluster.

To install micromamba (skip if already installed):

```bash
mkdir ~/micromamba
curl -Ls https://micro.mamba.pm/install.sh | bash -s -- -b -u -p ~/micromamba
echo 'export PATH=$HOME/micromamba/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

To create environments:

```bash
micromamba create -n sensor_env     -f ./conda_envs/sensor_env.yml
micromamba create -n crispresso_env -f ./conda_envs/crispresso_env.yml
```

To activate environments:

```bash
micromamba activate crispresso_env
micromamba activate sensor_env
```

---

## STEP 3 — Generate config file & library file

[`NGS-scripts/STEP3_generate_config_file/03_generate_config_file.ipynb`](https://github.com/fsrlabmit/sensor-analysis/blob/main/NGS-scripts/STEP3_generate_config_file/03_generate_config_file.ipynb)

### Config file

The power of the cluster is that we can run jobs for each of the different samples at the same time, which drastically speeds things up. To do so, we must first generate a config file that provides information about the relevant files so that they can be processed by the python scripts.

To generate config files, follow the Jupyter Notebook above.

The config file is tab/space-separated `.txt` with 4 columns (one row per sample, `ArrayTaskID` numbered from 1):

```{list-table}
:header-rows: 1
:widths: 25 75

* - Column
  - Description
* - `ArrayTaskID`
  - 1, 2, 3, … matches `--array=1-N` in the sbatch scripts
* - `R1_FILE`
  - relative path to R1 fastq
* - `R2_FILE`
  - relative path to R2 fastq
* - `folder_name`
  - output folder name for this sample
```

Here's an example of what a config file looks like:

```{image} figures/config_file.png
:width: 600px
:align: center
```

Note that if your NGS is processed with two lane per sample, you will have two `.fastq` files per sample. So instead, the config file would look like:

```{image} figures/config_file_lanes.png
:width: 600px
:align: center
```

We will proceed these .fastq files of duplicated lanes seperately and combine them at counts level later.

An example is also included as `CONFIG_BALL_VALIDATION_SCREEN.txt` in the folder of STEP3.

### Library file

You'll also need to have the library file with the proper column names:

| `gRNA_id` | `Protospacer` | `Hamming_BC` | `sensor_wt` | `sensor_alt` |
| --- | --- | --- | --- | --- |

Follow the Jupyter Notebook above to check you have proper columns included and correct names for them before proceeding forward.

---

### Actions before running STEP4

In your **sequencing folder on the cluster**,

- Check the length of sensor and the length of barcode of your library by following [`03_generate_config_file.ipynb`](https://github.com/fsrlabmit/sensor-analysis/blob/main/NGS-scripts/STEP3_generate_config_file/03_generate_config_file.ipynb);
- Add the **config file** and **library file**;
- Create these **4 sub-folders** **(names must be exact, lowercase)**:

  1. `classification`
  2. `confusion_mats`
  3. `counts`
  4. `crispresso`

```{note}
Step 4 - 6 will be run on the cluster. For each step, there is a python script and a corresponding `.sh` script that provides instructions to the cluster about which samples to run analysis on/where these files are located. Do not modify the Python script. **The only thing you will need to edit are these .sh scripts.**
```
