#!/bin/bash

# Automatically detect the Conda base directory
CONDA_BASE=$(conda info --base)

# Source Conda functions
source "$CONDA_BASE/etc/profile.d/conda.sh"

# Activate the desired Conda environment
conda activate APA

# Check if activation was successful
if [ $? -ne 0 ]; then
    echo "Failed to activate Conda environment. Make sure it's initialized."
    exit 1
fi

# Check if the correct number of arguments is provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <input_cluster_bed_file> <input_pseudobulk_beds_dir> <output_dir>"
    exit 1
fi

# Assign arguments to variables
input_cluster_bed_file="$1"
input_pseudobulk_beds_dir="$2"
output_dir="$3"

# Create output directory if it doesn't exist
mkdir -p "$output_dir"

# generate_pseudobulk_polyA_cluster_matrix
python3 utils/generate_matrix.py "$input_cluster_bed_file" "$input_pseudobulk_beds_dir" "$output_dir"