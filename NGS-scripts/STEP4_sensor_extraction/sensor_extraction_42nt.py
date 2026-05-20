#importing necessary packages
from collections import defaultdict
import gzip
from Bio.Align import PairwiseAligner
import numpy as np
#import matplotlib.pyplot as plt
import Bio.Seq
import pandas as pd
#import matplotlib.pyplot as plt
#import seaborn as sns
import Bio.Seq
import Bio.SeqIO
from Bio.SeqRecord import SeqRecord
import os
import sys
from pathlib import Path
#package for hamming distance 
import Levenshtein as lv

#-------Loading in system args
# Parse command-line arguments to read in files of interest
if len(sys.argv) != 10:
    print("Usage: python3 sensor_extraction_guide_counts.py <input_df> <R1_FILE> <R2_FILE> splitby proto_mismatches_allowed bc_len sensor_len -o <folder_name>")
    sys.exit(1)

input_df = pd.read_csv(Path(sys.argv[1]))
R1_FILE= Path(sys.argv[2])
R2_FILE= Path(sys.argv[3])
splitby = str(sys.argv[4])
proto_mismatches_allowed = int(sys.argv[5])
bc_len = int(sys.argv[6])
sensor_len = int(sys.argv[7])
folder_name = str(sys.argv[9])

#-----GLOBAL VARIABLES------
MIN_QUALITY = 30 #originally set to 30
GZ=False

#THIS FUNCTION MAY NEED TO BE UPDATED DEPENDING ON HOW THE DATA IS STRUCTURED
def fastq_reader(fname, gz=False):
    _open = gzip.open if gz else open
    proc_read = (lambda line: line.strip().decode()) if gz else (lambda line: line.strip())
    proc_qual = (lambda line: line.strip()) if gz else (lambda line: line.strip().encode('utf-8'))
    with _open(fname, 'r') as f:
        for i, line in enumerate(f):
            if i % 4 == 0:
                identifier = proc_read(line)
            elif i % 4 == 1:
                read = proc_read(line)
            elif i % 4 == 3:
                quality = proc_qual(line)
                yield identifier[-20:], read, quality #protospacer (index2), read, quality score


def quality_checker(q1, q2):
    """ 
    Checks quality score of the reads
    """

    qual1 = (np.frombuffer(q1, dtype=np.uint8) - 33).mean()
    qual2 = (np.frombuffer(q2, dtype=np.uint8) - 33).mean()

    low_qual = []

    if qual1 < MIN_QUALITY:
        low_qual.append('1')
    if qual2 < MIN_QUALITY:
        low_qual.append('2')
    
    if len(low_qual)==0:
        quality_out = 'good quality'
    else:
        quality_out = 'low_qual_r' + ''.join(low_qual)

    return quality_out

'''Prepare fastq records.'''
def to_IOSeq_rec(sensor_seq, i, q1, bc_len, sensor_len):
    """ 
    Modified to only extract 42 nt sensor
    After 15 nt barcode
    """
    qname = 'read_' + str(i)
    record = SeqRecord(Bio.Seq.Seq(sensor_seq[bc_len:bc_len+sensor_len]), id=qname, name=qname, description='', dbxrefs=[])

    #add quality score to the record
    qual = (np.frombuffer(q1, dtype=np.uint8) - 33)
    record.letter_annotations["phred_quality"] = qual[bc_len:bc_len+sensor_len]
    
    return record

def extraction_filtration(folder_name, input_df,R1_FILE,R2_FILE, bc_len, sensor_len, splitby, proto_mismatches_allowed, breakpoint=False):

    """
    Takes in reads and returns dataframe containing pegRNA counts AND sensor outcomes.

    Also returns summary of outcomes including:
    - low quality (and which of the reads are low quality (or if all are low quality))
    - no extension match
    - no protospacer match
    - decoupled extension-protospacer
    - correct identification
    """

    #----------1. generate folders for holding split sensor reads---------------
    os.mkdir(folder_name)#make the new directory (needs to be a non-existent folder)

    #write empty fastq files to a new folder for EACH gRNA
    #need to modify based on where the guide_ID column is/what its name is
    for i in list(input_df['gRNA_id']):
        f_name = i + '.fastq'
        with open(folder_name + '/' + f_name, 'w') as fp:
            pass

    #----------------lists and dicts for matching up reads------------------------
    proto_list = [i[1:] for i in input_df['Protospacer']]
    bc_list = [str(Bio.Seq.Seq(i).reverse_complement()) for i in input_df['Hamming_BC']]

    proto_bc_dict = dict(zip(bc_list, proto_list))
    confusion_mat = np.zeros((len(proto_list), len(bc_list)))

    
    #------initialize a dataframe for holding the pegRNA counts and sensor outcomes
    d1 = pd.DataFrame(dict(zip(['Guide_ID', 'sgRNA_no_Gstart', 'unique_BC'], [list(input_df['gRNA_id']), proto_list, bc_list])))

    cols = ['total_guide_count', 'matched_guide_count', 'bc_count']
    z = np.zeros((len(cols), len(input_df)))
    d2 = pd.DataFrame(dict(zip(cols, z)))
    df1 = pd.concat((d1, d2), axis=1).set_index('Guide_ID')

    #and annotating the duplicate guides
    i, v = np.unique(d1['sgRNA_no_Gstart'], return_counts=True)

    duplicate_dict = dict(zip(i, v>1))
    df1['duplicate_sgRNA'] = [duplicate_dict[i] for i in df1['sgRNA_no_Gstart']]
    df1[df1['duplicate_sgRNA']==True]

    #------initialize a dataframe for holding metadata about the identification of sensors
    outcomes = ['good quality', 'low_qual_r1', 'low_qual_r2', 'low_qual_r12', 
                'no_match_bc',
                'bc_identified',
                'proto_identified_perfect',
                'proto_identified_imperfect',
                'proto_identified_recombined',
                'no_match_proto',
                ]
    
    outcomes_count = np.zeros(len(outcomes))
    class_df = pd.DataFrame(dict(zip(['classification', 'count'],[outcomes, outcomes_count]))).set_index('classification')
    

    #----------iterating through the reads...--------------
    for i, ((proto1, r1, q1), (proto2, r2, q2)) in enumerate(zip(fastq_reader(R1_FILE, gz=GZ), fastq_reader(R2_FILE, gz=GZ)), 1):
        #r1 = sensor read
        #r2 = extension read
        #proto1/2 = protospacer read (index2)

        #first check the quality
        quality_out = quality_checker(q1,q2)
        class_df.loc[quality_out, 'count']+=1
            
        if quality_out=='good quality':
            proto = r2[:19]
            bc = r1[:bc_len]

            if bc in bc_list:
                df1.loc[df1['unique_BC']==bc, 'bc_count']+=1
                class_df.loc['bc_identified', 'count']+=1

                bc_idx = bc_list.index(bc)
                proto_match = proto_bc_dict[bc]

                hamming_distance = lv.hamming(proto, proto_match)

                #perfect protospacer match
                if hamming_distance==0:
                    df1.loc[df1['unique_BC']==bc, 'matched_guide_count']+=1
                    df1.loc[df1['unique_BC']==bc,  'total_guide_count']+=1
                    class_df.loc['proto_identified_perfect', 'count']+=1

                    if splitby != 'barcode':
                        #-----CODE FOR PUTTING THINGS IN SEPARATE FASTQ FILE HERE------
                        #add the sensor read to the appropriate fastq file (numbered according to the pegRNA index)
                        guide_id = df1[df1['unique_BC']==bc].index[0]

                        out_file = folder_name + '/' +  guide_id + '.fastq'

                        record = to_IOSeq_rec(r1, i, q1, bc_len, sensor_len)

                        with open(out_file, 'a') as fq:
                            #and write it to the appropriate file
                            Bio.SeqIO.write(record, fq, 'fastq')

                #imperfect match within allowed hamming distance
                elif hamming_distance<=proto_mismatches_allowed:
                    df1.loc[df1['unique_BC']==bc, 'matched_guide_count']+=1
                    df1.loc[df1['unique_BC']==bc,  'total_guide_count']+=1
                    class_df.loc['proto_identified_imperfect', 'count']+=1

                    if splitby != 'barcode':
                        #-----CODE FOR PUTTING THINGS IN SEPARATE FASTQ FILE HERE------
                        #add the sensor read to the appropriate fastq file (numbered according to the pegRNA index)
                        guide_id = df1[df1['unique_BC']==bc].index[0]

                        out_file = folder_name + '/' +  guide_id + '.fastq'

                        record = to_IOSeq_rec(r1, i, q1, bc_len, sensor_len)

                        with open(out_file, 'a') as fq:
                            #and write it to the appropriate file
                            Bio.SeqIO.write(record, fq, 'fastq')

                #nonmatching (beyond allowed hamming distance)
                elif hamming_distance>proto_mismatches_allowed:

                    if proto in proto_list:
                        df1.loc[df1['sgRNA_no_Gstart']==proto, 'total_guide_count']+=1
                        class_df.loc['proto_identified_recombined', 'count']+=1

                        proto_idx = proto_list.index(proto)
                        confusion_mat[proto_idx][bc_idx]+=1

                    else:
                        #and look for imperfect matches
                        count=0
                        for k in proto_list:
                            count+=1
                            h_dist = lv.hamming(k, proto)
                            if h_dist <=proto_mismatches_allowed:
                                df1.loc[df1['sgRNA_no_Gstart']==k, 'total_guide_count']+=1
                                class_df.loc['proto_identified_recombined', 'count']+=1

                                proto_idx = proto_list.index(k)
                                confusion_mat[proto_idx][bc_idx]+=1
                                break
                        
                        if count==len(proto_list):
                            class_df.loc['no_match_proto', 'count']+=1


                #-------if splitting sensors into different fastq files ONLY by barcode sequence-----
                if splitby=='barcode':
                        #-----CODE FOR PUTTING THINGS IN SEPARATE FASTQ FILE HERE------
                        #add the sensor read to the appropriate fastq file (numbered according to the pegRNA index)
                        guide_id = df1[df1['unique_BC']==bc].index[0]

                        out_file = folder_name + '/' +  guide_id + '.fastq'

                        record = to_IOSeq_rec(r1, i, q1, bc_len, sensor_len)

                        with open(out_file, 'a') as fq:
                            #and write it to the appropriate file
                            Bio.SeqIO.write(record, fq, 'fastq')

            elif bc not in bc_list:
                class_df.loc['no_match_bc', 'count']+=1


            else:
                continue

        if breakpoint != False:
            if i>breakpoint:
                break


    return df1, class_df, confusion_mat

#---RUNNING THE SCRIPT------
count_df, class_df, mat = extraction_filtration(folder_name, input_df,R1_FILE,R2_FILE, bc_len, sensor_len, splitby, proto_mismatches_allowed, breakpoint=False)

#save the counts and classification dataframes
count_df.to_csv('counts/' + folder_name + '_count_df.csv')
class_df.to_csv('classification/' + folder_name + '_classification_df.csv')

confusion_mat = pd.DataFrame(mat)
confusion_mat.to_csv('confusion_mats/' + folder_name + '_confusion_matrix.csv')
