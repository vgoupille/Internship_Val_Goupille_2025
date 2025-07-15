# Quality Control Pipeline for FASTQ Files

This pipeline performs quality control analysis on FASTQ files using FastQC and MultiQC. It is designed to work with different types of processed data (unzipped, trimmed, subsampled) and can analyze both R1 and R2 reads.

## Scripts Overview

The pipeline consists of three main scripts:
- `launch_multiQC_jobs.sh`: Main launcher script that submits jobs to the cluster
- `run_multiQC.sh`: SLURM job script that sets up the environment and runs the analysis
- `run_multiQC.py`: Python script that performs the actual FastQC and MultiQC analysis

## Usage

### Basic Usage

To run quality control on your FASTQ files, use:

```bash
./launch_multiQC_jobs.sh --data_type TYPE [--read_type TYPE] [--output_dir DIR]
```

Where:
- `--data_type` (required): Type of data to process
  - `unzipped`: Raw FASTQ files
  - `trimmed_simple`: Simply trimmed FASTQ files
  - `trimmed_complex`: Complex trimmed FASTQ files
  - `subsampled`: Subsampled FASTQ files
- `--read_type` (optional): Which reads to process
  - `R1`: Process only R1 reads (default)
  - `R2`: Process only R2 reads
  - `both`: Process both R1 and R2 reads (default if not specified)
- `--output_dir` (optional): Custom output directory
  - Default: `data/processed_data/multiqc_results_${DATA_TYPE}`

### Examples

1. Process both R1 and R2 reads for unzipped data:
```bash
./launch_multiQC_jobs.sh --data_type unzipped
```

2. Process only R1 reads for trimmed data:
```bash
./launch_multiQC_jobs.sh --data_type trimmed_simple --read_type R1
```

3. Process both reads with custom output directory:
```bash
./launch_multiQC_jobs.sh --data_type subsampled --output_dir /path/to/custom/output
```

## Output Structure

The pipeline creates the following directory structure:
```
multiqc_results_${DATA_TYPE}/
├── R1/
│   ├── FastQC reports
│   └── MultiQC report
└── R2/
    ├── FastQC reports
    └── MultiQC report
```

## Log Files

Log files are stored in `scripts/1_QC_fastq/logs/`:
- `multiqc_R1_${DATA_TYPE}_%j.out`: Standard output for R1 jobs
- `multiqc_R1_${DATA_TYPE}_%j.err`: Error output for R1 jobs
- `multiqc_R2_${DATA_TYPE}_%j.out`: Standard output for R2 jobs
- `multiqc_R2_${DATA_TYPE}_%j.err`: Error output for R2 jobs

Where `%j` is the SLURM job ID.

## Requirements

- SLURM job scheduler
- Conda environment with FastQC and MultiQC installed
- Python 3.x with required packages (tqdm, pyyaml)
- YAML file containing sample information (`data/info/samples/samples_all.yaml`)

## YAML File Format

The YAML file should have the following structure:
```yaml
samples:
  sample_name:
    R1:
      unzipped: /path/to/R1_unzipped.fastq
      trimmed_simple: /path/to/R1_trimmed.fastq
      trimmed_complex: /path/to/R1_complex_trimmed.fastq
      subsampled: /path/to/R1_subsampled.fastq
    R2:
      unzipped: /path/to/R2_unzipped.fastq
      trimmed_simple: /path/to/R2_trimmed.fastq
      trimmed_complex: /path/to/R2_complex_trimmed.fastq
      subsampled: /path/to/R2_subsampled.fastq
```

## Monitoring Jobs

To monitor the status of your jobs:
```bash
squeue -u $USER
```

## Troubleshooting

1. If jobs fail, check the log files in `scripts/1_QC_fastq/logs/`
2. Ensure the YAML file exists and has the correct format
3. Verify that all FASTQ files specified in the YAML exist
4. Check that the conda environment is properly set up

## Notes

- The pipeline uses parallel processing to speed up FastQC analysis
- Each job is allocated 8 CPUs and 16GB of memory
- Jobs have a maximum runtime of 4 hours
- Email notifications are sent for all job status changes