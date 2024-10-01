import pandas as pd
import numpy as np
import glob
import subprocess
import sys
import os
from io import StringIO
import pybedtools

# Check if the correct number of arguments is provided
if len(sys.argv) != 4:
    print("Usage: python generate_count_matrix.py <input_cluster_bed_file> <input_pseudobulk_beds_dir> <output_dir>")
    sys.exit(1)

# Get input arguments from command-line
input_cluster_bed_path = sys.argv[1]
input_pseudobulk_beds_dir = sys.argv[2]
output_dir = sys.argv[3]

# Print out input requirements
print(f"Input Cluster BED File: {input_cluster_bed_path}")
print(f"Input BED Directory: {input_pseudobulk_beds_dir}")
print(f"Output Directory: {output_dir}")

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load the input cluster BED file
input_cluster_bed_file = pd.read_csv(input_cluster_bed_path, sep="\t", header=None)

# Add new column names
new_column_names = [f'polyA_cluster_{i + 1}' for i in range(len(input_cluster_bed_file))]
input_cluster_bed_file[3] = new_column_names

# Convert DataFrame to BedTool
input_cluster_bed = pybedtools.BedTool.from_dataframe(input_cluster_bed_file)

# Find all .bed.gz files in the input directory and its subdirectories
bed_files = glob.glob(os.path.join(input_pseudobulk_beds_dir, '**', '*.bed.gz'), recursive=True)

# Check if there are any files found
if not bed_files:
    print(f"No .bed.gz files found in {input_pseudobulk_beds_dir}.")
    sys.exit(1)

# Initialize a list to hold DataFrames for each sample
sample_dfs = []

# Loop through each BED file and process
for bed_file in bed_files:
    # Extract sample_id and cell_type from the file path
    sample_id = bed_file.split('/')[-3]  # Adjust index based on your path structure
    cell_type = bed_file.split('/')[-1].replace('.bed.gz', '')  # Extract cell type from file name

    print(f"Processing {sample_id} - {cell_type}")

    # Read the BED file
    query_df = pybedtools.BedTool(bed_file)

    # Convert query_df to DataFrame, filter out lines with -1, then convert back to BedTool
    query_df_df = query_df.to_dataframe()
    query_df_df = query_df_df[(query_df_df['start'] >= 0) & (query_df_df['end'] >= 1)]
    query_df = pybedtools.BedTool.from_dataframe(query_df_df)

    # Use bedtools intersect to find the overlap between the two files
    overlaps = input_cluster_bed.intersect(query_df, wa=True, wb=True)

    # Convert to DataFrame and set column names
    overlaps_df = overlaps.to_dataframe(
        names=['chrom', 'start', 'end', 'name', 'chrom_query', 'start_query', 'end_query', 'count_query']
    )

    # Group by 'name' and count the occurrences of 'count_query'
    grouped = overlaps_df.groupby('name').count_query.count()

    # Create the new row with sample_id, cell_type, and grouped counts
    new_row = {
        "sample_id": sample_id,
        "cell_type": cell_type,
    }

    # Combine new_row with grouped counts in a single operation
    new_row.update(grouped.to_dict())

    # Append the new_row as a DataFrame to the list
    sample_dfs.append(pd.DataFrame([new_row]))

# Concatenate all sample DataFrames into one
new_df = pd.concat(sample_dfs, ignore_index=True)

# Ensure new_df contains all columns from input_cluster_bed_file, filling with NaN where necessary
new_df = new_df.reindex(columns=["sample_id", "cell_type"] + input_cluster_bed_file[3].tolist(), fill_value=np.nan)

# Convert numeric columns to integers, filling NaN with -1
new_df = new_df.apply(lambda x: pd.to_numeric(x, errors='coerce').fillna(-1).astype(int) if x.name in input_cluster_bed_file[3].tolist() else x)

# Define the output file path for the TSV
output_tsv_file = os.path.join(output_dir, 'polyA_cluster_count_matrix.tsv')
new_df.to_csv(output_tsv_file, sep='\t', index=False, header=True)

print(f"Combined TSV file saved to: {output_tsv_file}")
