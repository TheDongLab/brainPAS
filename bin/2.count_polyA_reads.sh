#!/bin/bash

# Automatically detect the Conda base directory
CONDA_BASE=$(conda info --base)

# Source Conda functions
source "$CONDA_BASE/etc/profile.d/conda.sh"

# Activate the desired Conda environment
conda activate scraps_conda

# Check if activation was successful
if [ $? -ne 0 ]; then
    echo "Failed to activate Conda environment. Make sure it's initialized."
    exit 1
fi

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <input_bam> <output_dir>"
    exit 1
fi

# Assign arguments to variables
input_bam="$1"
output_dir="$2"

# Derive base name from input BAM path
base_name=$(basename "$input_bam" .bam)
temp_bam="${output_dir}/${base_name}_temp.bam"
temp_bai="$temp_bam.bai"
filtered_bam="${output_dir}/${base_name}_filtered.bam"
filtered_bai="${filtered_bam}.bai"
output_bam="${output_dir}/${base_name}.bam"

# Create the output directory if it doesn't exist
mkdir -p "$output_dir"

# Filter BAM file to exclude reads with undefined barcodes
samtools view -h "$input_bam" | grep -v 'CB:Z:-\|UB:Z:-' | samtools view -b - > "$temp_bam"

# Index the temporary BAM file
samtools index "$temp_bam"

# Run the filtering script
python3 utils/filter_bam.py -i "$temp_bam" -o "$filtered_bam"

# Index the filtered BAM file
samtools index "$filtered_bam"

# Run UMI Tools for deduplication
umi_tools dedup \
    --extract-umi-method=tag \
    --umi-tag=UB \
    --per-cell \
    --cell-tag=CB \
    --method=unique \
    -I "$filtered_bam" \
    -S "$output_bam"

# Generate coverage using Bedtools
bedtools genomecov -ibam "$output_bam" -3 -dz | \
awk 'BEGIN { OFS = "\t" } { print $1, $2 - 1, $2, $3 }' | \
gzip > "${output_bam%.bam}.bed.gz"

# Clean up temporary files
rm -rf "$temp_bam"
rm -rf "$temp_bai"
rm -rf "$filtered_bam"
rm -rf "$filtered_bai"  # Remove the index file for filtered BAM
