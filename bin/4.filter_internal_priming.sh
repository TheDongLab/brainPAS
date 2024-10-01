#!/bin/bash

# Automatically detect the Conda base directory
CONDA_BASE=$(conda info --base)

# Source Conda functions
source "$CONDA_BASE/etc/profile.d/conda.sh"

# Activate the desired Conda environment
conda activate scTail

# Check if activation was successful
if [ $? -ne 0 ]; then
    echo "Failed to activate Conda environment. Make sure it's initialized."
    exit 1
fi

# Check if the correct number of arguments is provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <input_paraclu_file> <output_dir> <input_fasta_file>"
    exit 1
fi

# Assign arguments to variables
input_paraclu_file="$1"  
output_dir="$2"
input_fasta_file="$3"

# Create output directory if it doesn't exist
mkdir -p "$output_dir"

# Filter internal priming sites
python3 utils/remove_internal.py "$input_paraclu_file" "$output_dir" "$input_fasta_file"
if [ $? -ne 0 ]; then
    echo "Error: Failed to filter internal priming sites."
    exit 1
fi

