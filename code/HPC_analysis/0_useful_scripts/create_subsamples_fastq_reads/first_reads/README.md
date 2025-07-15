# FASTQ Read Subsampling Tool

This tool allows you to extract a specified number of reads from FASTQ files for multiple samples. It is designed to work in a SLURM environment and uses conda for dependency management.

## Overview

The script `run_extract_reads.sh` creates subsamples of FASTQ files by extracting the first N reads from each sample. It automatically manages job submission to SLURM with appropriate resource allocation based on the number of reads requested.

## Prerequisites

- SLURM workload manager
- Conda package manager
- Python 3.x
- Access to the required FASTQ files (specified in the YAML configuration)

## Usage

```bash
sbatch run_extract_reads.sh [options]
```

### Options

- `--reads N`: Number of reads to extract (default: 5000, 10000, 1000000)
- `--samples 'SAMPLE1 SAMPLE2 ...'`: Specific samples to process (default: all samples from YAML)
- `--yaml YAML_FILE`: Path to YAML file containing sample information (default: data/info/samples/samples_all.yaml)

### Examples

1. Extract 5000, 10000, 1000000 reads from all samples:
```bash
sbatch run_extract_reads.sh
```

2. Extract 10000 reads from specific samples:
```bash
sbatch run_extract_reads.sh --reads 10000 --samples 'SAMPLE1 SAMPLE2'
```

3. Use a custom YAML file:
```bash
sbatch run_extract_reads.sh --yaml data/info/samples/custom_samples.yaml
```

## Resource Allocation

The script automatically calculates resource requirements based on the number of reads:
- Memory: ~1GB per 1000 reads (capped at 32GB)
- Time: ~1 hour per 5000 reads (capped at 24 hours)
- CPUs: 4 per job

## Output

- Subsampled FASTQ files are generated for each sample
- Log files are stored in `logs/extract_reads/`
- Job-specific logs include both standard output and error logs

## Environment

### Conda Environment

The script uses a conda environment defined in `scripts/0_useful_scripts/create_subsamples_fastq_reads/environment_subsampling.yml`. The environment is automatically created or updated when the script runs.

#### Environment Location
- Environment path: `env/envSubsampling_first_reads`
- Environment definition file: `scripts/0_useful_scripts/create_subsamples_fastq_reads/environment_subsampling.yml`

#### Environment Management
The script automatically handles the conda environment:
1. If the environment doesn't exist, it creates it using the YAML file
2. If the environment exists, it updates it with any new dependencies
3. The environment is activated before running the Python script

#### Manual Environment Management
If you need to manage the environment manually:

```bash
# Create the environment
conda env create -p env/envSubsampling_first_reads -f scripts/0_useful_scripts/create_subsamples_fastq_reads/environment_subsampling.yml

# Update the environment
conda env update -p env/envSubsampling_first_reads -f scripts/0_useful_scripts/create_subsamples_fastq_reads/environment_subsampling.yml --prune

# Activate the environment
conda activate env/envSubsampling_first_reads
```

## Notes

- The script processes samples sequentially for each specified number of reads
- Each sample/read combination is submitted as a separate SLURM job
- Temporary job scripts are automatically cleaned up after submission

## File Organization

### Directory Structure
```
project_root/
├── data/
│   ├── raw_data/
│   │   └── subsampled_data/
│   │       └── first_reads/        # Output directory for subsampled reads
│   │           ├── 5000_reads/     # Directory for 5000 reads subsamples
│   │           │   ├── SAMPLE1.fastq.gz
│   │           │   └── SAMPLE2.fastq.gz
│   │           ├── 10000_reads/    # Directory for 10000 reads subsamples
│   │           │   ├── SAMPLE1.fastq.gz
│   │           │   └── SAMPLE2.fastq.gz
│   │           └── 1000000_reads/  # Directory for 1000000 reads subsamples
│   │               ├── SAMPLE1.fastq.gz
│   │               └── SAMPLE2.fastq.gz
│   └── info/
│       └── samples/
│           └── samples_all.yaml    # Sample information and paths
├── scripts/
│   └── 0_useful_scripts/
│       └── create_subsamples_fastq_reads/
│           └── first_reads/
│               ├── run_extract_reads.sh           # Main script
│               ├── environment_subsampling.yml    # Conda environment definition
│               └── README.md                      # This documentation
└── logs/
    └── extract_reads/             # SLURM job logs
        ├── extract_5000_reads_SAMPLE1_*.log
        ├── extract_5000_reads_SAMPLE1_*.err
        └── ...
```

### File Locations

1. **Input Files**:
   - Original FASTQ files are referenced in the YAML configuration file
   - YAML file location: `data/info/samples/samples_all.yaml`

2. **Output Files**:
   - Subsampled FASTQ files are stored in `data/raw_data/subsampled_data/first_reads/`
   - Files are organized in subdirectories based on the number of reads
   - Each subsampled file is named as `{SAMPLE_NAME}.fastq.gz`

3. **Log Files**:
   - SLURM job logs are stored in `logs/extract_reads/`
   - Each job generates two log files:
     - `*.log`: Standard output
     - `*.err`: Error messages

4. **Scripts and Configuration**:
   - Main script: `scripts/0_useful_scripts/create_subsamples_fastq_reads/first_reads/run_extract_reads.sh`
   - Environment definition: `scripts/0_useful_scripts/create_subsamples_fastq_reads/first_reads/environment_subsampling.yml`

### Naming Conventions

- Subsampled files: `{SAMPLE_NAME}.fastq.gz`
- Log files: `extract_{NUMBER_OF_READS}_reads_{SAMPLE_NAME}_{JOB_ID}.{log|err}`
- Job scripts (temporary): `extract_{NUMBER_OF_READS}_reads_{SAMPLE_NAME}.sh`

## Logs

### Log Directory Structure
```
project_root/
└── logs/
    └── extract_reads/             # Main log directory
        ├── extract_5000_reads_SAMPLE1_*.log    # Standard output logs
        ├── extract_5000_reads_SAMPLE1_*.err    # Error logs
        ├── extract_10000_reads_SAMPLE1_*.log
        ├── extract_10000_reads_SAMPLE1_*.err
        └── ...
```

### Log Files

Each SLURM job generates two types of log files:

1. **Standard Output Logs** (`.log`):
   - Location: `logs/extract_reads/`
   - Naming pattern: `extract_{NUMBER_OF_READS}_reads_{SAMPLE_NAME}_{JOB_ID}.log`
   - Contains: Standard output from the Python script, including:
     - Start and end times of the job
     - Progress information
     - Success messages

2. **Error Logs** (`.err`):
   - Location: `logs/extract_reads/`
   - Naming pattern: `extract_{NUMBER_OF_READS}_reads_{SAMPLE_NAME}_{JOB_ID}.err`
   - Contains: Error messages and warnings, including:
     - SLURM job errors
     - Python script errors
     - Environment activation issues

### Log Management

- Log files are automatically created when the script runs
- The log directory (`logs/extract_reads/`) is created if it doesn't exist
- Each job's logs are uniquely identified by the combination of:
  - Number of reads
  - Sample name
  - SLURM job ID
- Log files are not automatically cleaned up, allowing for post-run analysis

### Example Log Content

```bash
# Standard output log (extract_5000_reads_SAMPLE1_12345.log)
Starting extraction of first 5000 reads for sample SAMPLE1...
Processing file: /path/to/input.fastq.gz
Extracted 5000 reads successfully
Job completed!

# Error log (extract_5000_reads_SAMPLE1_12345.err)
# Empty if no errors occurred
``` 