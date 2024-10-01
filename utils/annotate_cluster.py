import pandas as pd
import numpy as np
import pybedtools
import os
import sys

# Check if the correct number of arguments is provided
if len(sys.argv) != 4:
    print("Usage: python annotate_clusters.py <input_cluster_bed_file> <input_bedGraph_file> <output_dir>")
    sys.exit(1)

# Get input and output directories from command-line arguments
input_cluster_bed_file = sys.argv[1]  # This file contains cluster data in BED format
input_bedGraph_file = sys.argv[2]      # This file contains the BedGraph data for intersecting
output_dir = sys.argv[3]                # Directory where output files will be saved

# Validate input files
if not os.path.exists(input_cluster_bed_file):
    print(f"Input cluster BED file does not exist: {input_cluster_bed_file}")
    sys.exit(1)
if not os.path.exists(input_bedGraph_file):
    print(f"Input BedGraph file does not exist: {input_bedGraph_file}")
    sys.exit(1)

# Input files and parameters
annotation_bed = pybedtools.BedTool("ref/annotation/polyadb32.hg38.bed")

# Print out input and output requirements
print(f"Input Cluster BED File: {input_cluster_bed_file}")
print(f"Input BedGraph File: {input_bedGraph_file}")
print(f"Output Directory: {output_dir}")

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Read in cluster BED file
cluster_bed = pybedtools.BedTool(input_cluster_bed_file)

# Read in input bedGraph file
input_bedGraph = pybedtools.BedTool(input_bedGraph_file)

# Perform bed intersect
intersection = cluster_bed.intersect(input_bedGraph, wa=True, wb=True)

# Convert to dataframe
intersection_df = intersection.to_dataframe()

# Rename columns
columns = ['chrom1', 'start1', 'end1', 'chrom2', 'start2', 'end2', 'value']
intersection_df.columns = columns

# Group by chrom1, start1, end1 and keep the row with the maximum value
result_df = intersection_df.loc[intersection_df.groupby(['chrom1', 'start1', 'end1'])['value'].idxmax()]

# Remove chrom2 and value columns
result_df = result_df.drop(columns=['chrom2', 'value'])

# Generate the new column names
new_column_names = [f'polyA_cluster_{i + 1}' for i in range(len(result_df))]

# Insert the new column as the fourth column
result_df.insert(3, 'name', new_column_names)

# Convert to BedTool
result_bed = pybedtools.BedTool.from_dataframe(result_df)

# Intersect with annotation bed file
result_annotation = result_bed.intersect(annotation_bed, wa=True, wb=True)

# Convert to dataframe
result_annotation_df = result_annotation.to_dataframe()

# Rename columns for clarity
result_annotation_df.columns = ['chr', 'start', 'end', 'name', 'summit_start', 'summit_end', 'chr2', 'polyA_start', 'polyA_end', 'annotation']

# Calculate the distance from summit to polyA start
result_annotation_df['summit_polyA_distance'] = (result_annotation_df['summit_start'] - result_annotation_df['polyA_start']).abs()

# Group by the name column and retain the row with the smallest absolute difference
result_annotation_df = result_annotation_df.loc[result_annotation_df.groupby('name')['summit_polyA_distance'].idxmin()]

# Remove unnecessary columns
result_annotation_df = result_annotation_df.drop(columns=['chr2', 'summit_polyA_distance'])

# Sort by chromosome, start, end
result_annotation_df = result_annotation_df.sort_values(by=['chr', 'start', 'end'])

# Save annotated results to file
result_annotation_df.to_csv(os.path.join(output_dir, "annotated_polyA_cluster.tsv"), sep="\t", index=False, header=True)

# Identify non-overlapping clusters
novel_clusters = result_df[~result_df['name'].isin(result_annotation_df['name'])]

# Rename columns for consistency
novel_clusters.columns = ['chr', 'start', 'end', 'name', 'summit_start', 'summit_end']

# Save novel clusters to file
novel_clusters.to_csv(os.path.join(output_dir, "novel_polyA_cluster.tsv"), sep="\t", index=False, header=True)

# Display shapes of results
print(f"Result DataFrame shape: {result_df.shape}")
print(f"Annotated DataFrame shape: {result_annotation_df.shape}")
print(f"Novel Clusters shape: {novel_clusters.shape}")
