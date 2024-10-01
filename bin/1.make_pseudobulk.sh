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
    echo "Usage: $0 <input_bam> <input_barcodes> <output_dir>"
    exit 1
fi

# Assign arguments to variables
input_bam="$1"
input_barcodes="$2"
output_dir="$3"

# Create pseudobulk samples
sinto filterbarcodes -b "$input_bam" -c "$input_barcodes" --outdir "$output_dir" -p 10
