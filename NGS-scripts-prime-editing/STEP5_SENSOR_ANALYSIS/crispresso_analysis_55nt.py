import pandas as pd
import os
import sys
from pathlib import Path


#-------Loading in system args
# Parse command-line arguments to read in files of interest
if len(sys.argv) != 3:
    print("Usage: python3 crispresso_analysis_55nt.py <input_df> <sample_name>")
    sys.exit(1)

#example usage
df = pd.read_csv(Path(sys.argv[1]))
sample_name = str(sys.argv[2]) 

#------run it for all guides
for i, val in df.iterrows():
    guide_id = val['pegRNA_id']
    wt = val['sensor_wt']
    edited = val['sensor_alt']
    proto = val['Protospacer'][1:] #19 bp (excluding G start)
    wt_qwc = val['wt_qwc']
    edit_qwc = val['edit_qwc']

    #generating crispresso command
    f_path = f"./{sample_name}/{guide_id}.fastq"
    start = f"CRISPResso --fastq_r1 {f_path} "

    #qwc is 5nt upstream and 5nt downstream of 20 nt guide sequence
    #default alignment parameters (60%)
    p2 = f'--amplicon_seq {wt} --expected_hdr_amplicon_seq {edited} --guide_seq {proto} --quantification_window_coordinates {wt_qwc},{edit_qwc} --exclude_bp_from_left 0 --exclude_bp_from_right 0 --prime_editor_output --plot_window_size 15 --suppress_report --suppress_plots '
    
    out_path = f"-o ./crispresso/{sample_name} -n {guide_id}"

    command = start+ p2 + out_path

    #running the crispresso command
    #apparently this is bad practice (but subprocess module didn't work...)
    os.system(command)
