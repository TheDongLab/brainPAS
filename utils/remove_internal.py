import pandas as pd
import numpy as np
import os
import sys
import argparse
from torch.utils.data import DataLoader
from deep_learning import scDataset, Net, test

# Check if the correct number of arguments is provided
if len(sys.argv) != 4:
    print("Usage: python remove_internal.py <input_paraclu_file> <output_dir> <input_fasta_file>")
    sys.exit(1)

# Get input and output directories from command-line arguments
input_paraclu_file = sys.argv[1]
output_dir = sys.argv[2]
fastafilePath = sys.argv[3]

# Input files and parameters
chrom_sizes = 'ref/model/chrom.sizes'
pretrained_model_path = 'ref/model/human_pretrained_model.pth'
# fastafilePath = "/mnt/data/referenceGenome/Homo_sapiens/refdata-gex-GRCh38-2020-A/fasta/genome.fa"

# Print out input and output requirements
print(f"Input Paraclu File: {input_paraclu_file}")
print(f"Output Directory: {output_dir}")
print(f"Input Fastq File: {fastafilePath}") 

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load the Paraclu output
paracludf = pd.read_csv(input_paraclu_file, header=None, delimiter='\t')
paracludf['cluster_id'] = paracludf[0] + '_' + paracludf[1] + '_' + paracludf[2].astype('str') + '_' + paracludf[3].astype('str')
paracludf['PAS'] = np.where(paracludf[1] == '.', paracludf[3], paracludf[2])

# Prepare input DataFrame for the deep learning model
inputtodeepdf = paracludf[[0, 1, 'PAS', 'cluster_id']]
inputtodeepdf.columns = ['Chromosome', 'Strand', 'PAS', 'cluster_id']
input_to_DP = os.path.join(output_dir, "input_to_DP.tsv")
inputtodeepdf.to_csv(input_to_DP, sep='\t', index=None)

# Load chromosome sizes
chromosizedf = pd.read_csv(chrom_sizes, delimiter='\t', header=None, index_col=0)

# Create dataset and data loader
test_set = scDataset(fastafilePath, input_to_DP, chromosizedf)
test_loader = DataLoader(test_set, batch_size=1, shuffle=False)

# Model setup
predict_result_output = os.path.join(output_dir, 'predict_positive_result.tsv')
device = 'cpu'  # Update this if using multiple GPUs
net = Net().to(device)

# Perform testing
positivedf = test(test_loader, device, net, pretrained_model_path, predict_result_output)

# Post-process predictions
positivedf[['chr', 'strand', 'start', 'end']] = positivedf['PAS'].str.split('_', expand=True)
positivedf['start'] = positivedf['start'].astype(int)
positivedf['end'] = positivedf['end'].astype(int)
positivedf['y_pred'] = positivedf['y_pred'].astype(int)
positivedf['y_score'] = positivedf['y_score'].astype(float)

# Save predictions to output file
positivedf.to_csv(predict_result_output, sep='\t', index=None)

# get column names chr, start, end to a bed file
positivedf[['chr', 'start', 'end']].to_csv(os.path.join(output_dir, 'final_combined_positive_polyA.bed'), sep='\t', index=None, header=None)


