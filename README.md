# PASpipline

### A pipeline to quantify polyA site (PAS) counts from "TVN"-primed single-cell RNA-Seq Read2.

## Installation
```bash
cd envs
conda env create -f env_APA.yml
conda env create -f env_scraps_conda.yml
conda env create -f env_scTail.yml
```

## Run
```bash
bash main.sh
```

## Workflow
<div>
<img src="PASpipline_workflow.png" width="382" height="480" align="center">
</div> 

## Input
Please edit 3 input variables in main.sh
```bash
sample_sheet="/path/to/your/samplesheet.csv"
output_base_dir="/path/to/your/output"  
input_fasta_file="/path/to/your/genome.fa"  
```
