#!/bin/bash

# Assign input arguments to variables
sample_sheet="test/samplesheet.csv"
output_base_dir="test/output"  
input_fasta_file="/mnt/data/referenceGenome/Homo_sapiens/refdata-gex-GRCh38-2020-A/fasta/genome.fa"  

# Create a log file
log_file="${output_base_dir}/process.log"
echo "Process started on $(date)" > "$log_file"

# Read the sample sheet line by line
while IFS=',' read -r sample_id input_bam input_barcodes; do
    echo "-----------------------------------" >> "$log_file"
    echo "Processing sample: $sample_id" | tee -a "$log_file"

    # Create a directory for the sample_id within the specified output directory
    pseudobulk_output_dir="${output_base_dir}/preprocess/${sample_id}/1.pseudobulk"
    echo "Creating directory for pseudobulk: $pseudobulk_output_dir" | tee -a "$log_file"
    mkdir -p "$pseudobulk_output_dir"

    # Step 1: Run the pseudobulk script
    echo "Running pseudobulk script for sample: $sample_id" | tee -a "$log_file"
    bash bin/1.make_pseudobulk.sh "$input_bam" "$input_barcodes" "$pseudobulk_output_dir" >> "$log_file" 2>&1

    # Create output directory for polyA reads
    polyA_output_dir="${output_base_dir}/preprocess/${sample_id}/2.polyA_bed"
    echo "Creating directory for polyA reads: $polyA_output_dir" | tee -a "$log_file"
    mkdir -p "$polyA_output_dir"

    # Step 2: Loop through the output BAM files in the pseudobulk directory
    for bam_file in "${pseudobulk_output_dir}"/*.bam; do
        echo "Starting processing of BAM file: $bam_file" | tee -a "$log_file"
        bash bin/2.count_polyA_reads.sh "$bam_file" "$polyA_output_dir" >> "$log_file" 2>&1 &
    done

    # Wait for all background processes to finish
    wait
    echo "Finished preprocessing sample: $sample_id" | tee -a "$log_file"

done < "$sample_sheet"

# Combine all polyA BedGraph files
polyA_cluster_output_dir="${output_base_dir}/3.polyA_cluster"
echo "Creating directory for combined polyA BedGraph files: $polyA_cluster_output_dir" | tee -a "$log_file"
mkdir -p "$polyA_cluster_output_dir"

# Step 3: Run the call_polyA_cluster script
echo "Running call_polyA_cluster script" | tee -a "$log_file"
bash bin/3.call_polyA_cluster.sh "$polyA_output_dir" "$polyA_cluster_output_dir" >> "$log_file" 2>&1

# Filter internal priming sites
internal_priming_output_dir="${output_base_dir}/4.filter_internal_priming"
echo "Creating directory for internal priming filter: $internal_priming_output_dir" | tee -a "$log_file"
mkdir -p "$internal_priming_output_dir"

# Step 4: Run the filter_internal_priming script
echo "Running filter_internal_priming script" | tee -a "$log_file"
bash bin/4.filter_internal_priming.sh "$polyA_cluster_output_dir/final_combined_polyA_cluster_output.tsv" "$internal_priming_output_dir" "$input_fasta_file" >> "$log_file" 2>&1

# Annotate polyA peaks
polyA_cluster_annotation_output_dir="${output_base_dir}/5.polyA_cluster_annotation"
echo "Creating directory for polyA peak annotation: $polyA_cluster_annotation_output_dir" | tee -a "$log_file"
mkdir -p "$polyA_cluster_annotation_output_dir"

# Step 5: Run the annotate_polyA_cluster script
echo "Running annotate_polyA_cluster script" | tee -a "$log_file"
bash bin/5.annotate_polyA_cluster.sh "$internal_priming_output_dir/final_combined_positive_polyA.bed" "$polyA_cluster_output_dir/final_combined_polyA.bedGraph" "$polyA_cluster_annotation_output_dir" >> "$log_file" 2>&1

# Generate pseudobulk counts
pseudobulk_polyA_cluster_matrix_output_dir="${output_base_dir}/6.pseudobulk_polyA_cluster_matrix"
echo "Creating directory for pseudobulk polyA cluster matrix: $pseudobulk_polyA_cluster_matrix_output_dir" | tee -a "$log_file"

# Step 6: Run the generate_pseudobulk_polyA_matrix script
echo "Running generate_pseudobulk_polyA_matrix script" | tee -a "$log_file"
bash bin/6.generate_pseudobulk_polyA_matrix.sh "$internal_priming_output_dir/final_combined_positive_polyA.bed" "${output_base_dir}/preprocess" "$pseudobulk_polyA_cluster_matrix_output_dir" >> "$log_file" 2>&1

echo "-----------------------------------" >> "$log_file"
echo "Process completed on $(date)" | tee -a "$log_file"
