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
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <input_dir> <output_dir>"
    exit 1
fi

# Assign arguments to variables
input_dir="$1"  # input_dir contains all bedgraph files that need to be combined
output_dir="$2"

# Create output directory if it doesn't exist
mkdir -p "$output_dir"

# Combine all BedGraph files in the input directory
python3 utils/combine_bedGraph.py "$input_dir" "$output_dir"
if [ $? -ne 0 ]; then
    echo "Error: Failed to combine BedGraph files."
    exit 1
fi

# Paraclu to call polyA clusters from the combined BedGraph file (scTail parameters)
paraclu 50 "$output_dir/final_combined_polyA_cluster_input.tsv" | paraclu-cut -l 100 -d 0 > "$output_dir/final_combined_polyA_cluster_output.tsv"
if [ $? -ne 0 ]; then
    echo "Error: Failed to run paraclu."
    exit 1
fi
