ssh youraccount@luria.mit.edu
srun --pty bash
# lab server: 
cd /net/bmc-lab2/data/lab/sanchezrivera/yourname/
# save sequencing data to the server:
srun rsync -av /net/bmc-pub17/data/bmc/public/datahub/datafolder /net/bmc-lab2/data/lab/sanchezrivera/yourname/