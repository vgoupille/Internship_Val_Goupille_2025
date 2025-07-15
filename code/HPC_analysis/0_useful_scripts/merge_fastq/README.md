# Merge FASTQ Scripts

This set of scripts is designed to merge multiple FASTQ.gz files from different samples into a single pair of files (R1 and R2). The scripts use SLURM for job management and are optimized for handling large FASTQ files.

## Quick Start

```bash
# Example with real data
bash scripts/0_useful_scripts/merge_fastq/merge_fastq_wrapper.sh -i data/raw_data/unzipped_data/fastq -o merged_samples
```

This will create:
- `data/raw_data/merged_data/merged_samples.R1.fastq.gz`
- `data/raw_data/merged_data/merged_samples.R2.fastq.gz`

## Directory Structure

```
scripts/0_useful_scripts/merge_fastq/
├── README.md
└── merge_fastq_wrapper.sh    # Main wrapper script that generates and submits SLURM jobs
```

Note: The wrapper script dynamically generates temporary SLURM job scripts for R1 and R2 processing, which are automatically deleted after job submission.

## Input/Output Structure

```
project/
├── data/
│   └── raw_data/
│       ├── unzipped_data/
│       │   └── fastq/                    # Input directory
│       │       ├── BC_0076_R1.fastq.gz
│       │       ├── BC_0076_R2.fastq.gz
│       │       ├── BC_0077_R1.fastq.gz
│       │       └── BC_0077_R2.fastq.gz
│       └── merged_data/                  # Output directory
│           ├── merged_samples.R1.fastq.gz  # Merged R1 file
│           └── merged_samples.R2.fastq.gz  # Merged R2 file
└── logs/                                # SLURM logs
    ├── merge_fastq_R1_*.log
    └── merge_fastq_R2_*.log
```

## Requirements

- SLURM job scheduler
- Bash shell
- Input files must be in FASTQ.gz format
- Input files must follow the naming pattern: `BC_*_R1.fastq.gz` and `BC_*_R2.fastq.gz`

## Usage

```bash
bash scripts/0_useful_scripts/merge_fastq/merge_fastq_wrapper.sh -i <input_dir> -o <output_name>
```

### Options

- `-i`: Input directory containing the FASTQ.gz files (required)
- `-o`: Output name for the merged files (required)

### SLURM Parameters

The scripts use the following SLURM parameters:
- Time limit: 12 hours
- Memory: 32GB
- CPUs: 8
- Output/Error logs: stored in `logs/` directory

## Examples

### Real Example

```bash
# Merge all FASTQ files into a single pair of files named 'merged_samples'
bash scripts/0_useful_scripts/merge_fastq/merge_fastq_wrapper.sh -i data/raw_data/unzipped_data/fastq -o merged_samples
```

### Expected Output

After running the script, you should see:
```
Launching merge jobs for R1 and R2 files...
Submitting R1 job... 14141477
Submitting R2 job... 14141478

Jobs submitted successfully:
  R1 merge job ID: 14141477
  R2 merge job ID: 14141478

Monitor jobs with: squeue -j 14141477,14141478
```

## Monitoring

1. Check job status:
```bash
squeue -j 14141477,14141478
```

2. Check logs:
```bash
# R1 logs
cat logs/merge_fastq_R1_14141477.log
cat logs/merge_fastq_R1_14141477.err

# R2 logs
cat logs/merge_fastq_R2_14141478.log
cat logs/merge_fastq_R2_14141478.err
```

## Notes

- The script automatically creates necessary directories (`logs/` and output directory)
- Temporary SLURM scripts are automatically deleted after job submission
- Each read type (R1 and R2) is processed in a separate SLURM job
- The script checks for the existence of input files before starting
- Progress and timing information is logged for each merge operation

## Error Handling

The script includes several error checks:
- Validates input directory existence
- Verifies presence of required FASTQ files
- Checks job submission success
- Monitors merge operation completion

If any error occurs, appropriate error messages will be displayed and the script will exit with a non-zero status code. 