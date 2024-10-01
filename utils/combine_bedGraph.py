import pandas as pd
import glob
import subprocess
import sys
import os
from io import StringIO

# Check if the correct number of arguments is provided
if len(sys.argv) != 3:
    print("Usage: python combine_bedGraph.py <input_dir> <output_dir>")
    sys.exit(1)

# Get input and output directories from command-line arguments
input_dir = sys.argv[1]
output_dir = sys.argv[2]

# Print out input and output requirements
print(f"Input Directory: {input_dir}")
print(f"Output Directory: {output_dir}")

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Find all .bed.gz files in the input directory and its subdirectories
file_paths = glob.glob(os.path.join(input_dir, '**', '*.bed.gz'), recursive=True)

# Check if there are any files found
if not file_paths:
    print(f"No .bed.gz files found in {input_dir}.")
    sys.exit(1)

# Concatenate the .bed.gz files and sort them
cat_command = f"zcat {' '.join(file_paths)} | sort -k1,1 -k2,2n"
try:
    sorted_bed = subprocess.check_output(cat_command, shell=True, text=True)
except subprocess.CalledProcessError as e:
    print(f"Error during concatenation: {e}")
    sys.exit(1)

# Read the sorted data into a pandas DataFrame
df = pd.read_csv(StringIO(sorted_bed), sep='\t', header=None, names=['chromosome', 'start', 'end', 'count'])

# Filter the DataFrame
filtered_df = df[
    (df['chromosome'].str.startswith('chr')) &  # Retain rows where chromosome starts with 'chr'
    (df['start'] >= 0) &  # Retain rows where start >= 0
    (df['end'] >= 1)  # Retain rows where end >= 1
]

# Group by chromosome, start, and end positions and sum the counts
grouped_df = filtered_df.groupby(['chromosome', 'start', 'end'], as_index=False).sum()

# Sort the grouped DataFrame by chromosome and start
grouped_df = grouped_df.sort_values(by=['chromosome', 'start'])

# Define the output file path for bedGraph
output_bedgraph_file = os.path.join(output_dir, 'final_combined_polyA.bedGraph')

# Save the grouped DataFrame to the bedGraph output file
grouped_df.to_csv(output_bedgraph_file, sep='\t', index=False, header=False)

# Convert the 'start' column to string type before assigning '.'
grouped_df['start'] = grouped_df['start'].astype(str)  # Convert to string type
grouped_df['start'] = '.'  # Assign '.' to the entire column

# Define the output file path for the TSV
output_tsv_file = os.path.join(output_dir, 'final_combined_polyA_cluster_input.tsv')

# Save the modified DataFrame to the TSV output file
grouped_df.to_csv(output_tsv_file, sep='\t', index=False, header=False)

print(f"Combined bedGraph file saved to: {output_bedgraph_file}")
print(f"Combined TSV file saved to: {output_tsv_file}")