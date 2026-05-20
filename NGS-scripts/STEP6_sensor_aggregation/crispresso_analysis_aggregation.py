import pandas as pd
import os
import sys
from pathlib import Path


#-------Loading in system args
# Parse command-line arguments to read in files of interest
if len(sys.argv) != 4:
    print("Usage: python3 crispresso_analysis_aggregation.py <input_df> <folder_name> <quant_zero>")
    sys.exit(1)

#example usage
df = pd.read_csv(Path(sys.argv[1]))
sample_name = str(sys.argv[2])
quant_zero = pd.read_csv(Path(sys.argv[3]))

#runnnig it to create a large dataframe
fp = './crispresso' #path to output folders


#--------run it for all of the pegRNAs
rows = []
for i, val in df.iterrows():
    guide_id = val['gRNA_id']
    output_folder_x = os.listdir(fp + '/' + sample_name + f"/CRISPResso_on_{guide_id}")
    #peg_id = 'peg_' + str(peg_num)

    if 'CRISPResso_quantification_of_editing_frequency.txt' in output_folder_x:
        quant = pd.read_csv(fp + '/' + sample_name + f"/CRISPResso_on_{guide_id}" + '/' + 'CRISPResso_quantification_of_editing_frequency.txt', sep='\t')
        quant['Guide_ID'] = guide_id

    else:
        quant = quant_zero.copy()
        quant['Guide_ID'] = guide_id
    
    rows.append(quant)

output = pd.concat(rows)  
output.to_csv(f"./crispresso/{sample_name}_crispresso_aggregated.csv", index=False)