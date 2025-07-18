# Quality Control Pipeline for FASTQ Files

This pipeline performs quality control analysis on FASTQ files using FastQC and MultiQC. It is designed to work with different types of processed data (unzipped, trimmed, subsampled) and can analyze both R1 and R2 reads.

## Scripts Overview

The pipeline consists of five main scripts:

1. **`create_env_multiQC.sh`** : SLURM script to create the conda environment
2. **`launch_multiQC_jobs.sh`** : Main launcher script that submits jobs to the cluster
3. **`run_multiQC.sh`** : SLURM job script that sets up the environment and runs the analysis
4. **`run_multiQC.py`** : Python script that performs the actual FastQC and MultiQC analysis
5. **`environment_multiQC.yml`** : Conda environment file with dependencies
6. **`validate_config.py`** : Configuration validation utility script

## Installation and Configuration

### 1. Create conda environment

```bash
# Submit environment creation job
sbatch create_env_multiQC.sh
```

### 2. Verify configuration files

Ensure the sample YAML file exists:
- `data/info/samples/samples_trimming.yaml` (used by default)
- Required format described in "YAML File Format" section

### 3. Configuration validation

Use the validation script to check that everything is properly configured:

```bash
# Basic validation
python validate_config.py

# Validation with FASTQ file checking
python validate_config.py --check_fastq --data_type unzipped
```

The script checks:
- ✓ Presence of all pipeline files
- ✓ YAML file format
- ✓ Existence of required directories
- ✓ Existence of FASTQ files (optional)

## Configuration Validation Script

The `validate_config.py` script is a comprehensive validation utility that ensures your pipeline configuration is correct before running the actual analysis.

### Features

- **File verification**: Checks that all required pipeline files exist
- **YAML validation**: Verifies the format and content of the sample configuration file
- **Directory checking**: Confirms output directories exist or can be created
- **FASTQ file validation**: Optionally checks that specified FASTQ files exist
- **Sample counting**: Reports the number of samples found in the configuration
- **Clear reporting**: Provides detailed status messages and summary

### Usage Examples

```bash
# Basic validation (recommended before first use)
python validate_config.py

# Validate with FASTQ file checking for specific data type
python validate_config.py --check_fastq --data_type unzipped

# Validate for trimmed data
python validate_config.py --check_fastq --data_type trimmed
```

### Output Interpretation

The script provides color-coded output:
- ✓ **Green checkmarks**: Everything is working correctly
- ✗ **Red X marks**: Issues that need to be fixed
- ? **Question marks**: Items that will be created automatically

### Exit Codes

- **0**: All checks passed, pipeline ready to use
- **1**: Issues detected, need fixing before running pipeline

### When to Use

- **Before first pipeline run**: Verify complete setup
- **After configuration changes**: Ensure changes are valid
- **Troubleshooting**: Identify configuration issues
- **Regular maintenance**: Periodic health checks

## Usage

### Basic Usage

```bash
./launch_multiQC_jobs.sh --data_type TYPE [--read_type TYPE] [--output_dir DIR]
```

### Parameters

- **`--data_type`** (required): Type of data to process
  - `unzipped`: Raw FASTQ files
  - `trimmed_simple`: Simply trimmed FASTQ files
  - `trimmed_complex`: Complex trimmed FASTQ files
  - `subsampled`: Subsampled FASTQ files
  - Or any other type defined in the YAML file

- **`--read_type`** (optional): Reads to process
  - `R1`: Process only R1 reads
  - `R2`: Process only R2 reads
  - `both`: Process both R1 and R2 (default)

- **`--output_dir`** (optional): Custom output directory
  - Default: `data/processed_data/multiqc_results_${DATA_TYPE}`

### Usage Examples

1. **Process unzipped data (R1 and R2):**
```bash
./launch_multiQC_jobs.sh --data_type unzipped
```

2. **Process only R1 reads for trimmed data:**
```bash
./launch_multiQC_jobs.sh --data_type trimmed_simple --read_type R1
```

3. **Process with custom output directory:**
```bash
./launch_multiQC_jobs.sh --data_type subsampled --output_dir /path/to/custom/output
```

## Output Structure

The pipeline creates the following directory structure:

```
multiqc_results_${DATA_TYPE}/
├── R1/
│   ├── sample1_R1_fastqc.html
│   ├── sample1_R1_fastqc.zip
│   ├── sample2_R1_fastqc.html
│   ├── sample2_R1_fastqc.zip
│   └── multiqc_report.html
└── R2/
    ├── sample1_R2_fastqc.html
    ├── sample1_R2_fastqc.zip
    ├── sample2_R2_fastqc.html
    ├── sample2_R2_fastqc.zip
    └── multiqc_report.html
```

## Log Files

Log files are stored in `logs/`:
- `multiqc_R1_${DATA_TYPE}_%j.out`: Standard output for R1 jobs
- `multiqc_R1_${DATA_TYPE}_%j.err`: Error output for R1 jobs
- `multiqc_R2_${DATA_TYPE}_%j.out`: Standard output for R2 jobs
- `multiqc_R2_${DATA_TYPE}_%j.err`: Error output for R2 jobs

Where `%j` is the SLURM job ID.

## Requirements

- **SLURM job scheduler**
- **Conda** installed and configured
- **Python 3.9+** with required packages
- **YAML file** containing sample information

### Conda dependencies

The conda environment includes:
- `fastqc=0.12.1`
- `multiqc=1.28`
- `python=3.9`
- `tqdm`
- `pyyaml`
- `yq`

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

## Job Monitoring

### Check job status:
```bash
squeue -u $USER
```

### View logs in real-time:
```bash
tail -f logs/multiqc_R1_${DATA_TYPE}_${JOB_ID}.out
```

## Technical Specifications

### SLURM Resources
- **CPUs**: 32 cores per job
- **Memory**: 64 GB per job
- **Max time**: 4 hours
- **Partition**: bigmem

### Optimizations
- **Parallel processing**: FastQC uses all available cores
- **Memory management**: Allocation adapted for large FASTQ files
- **Error handling**: File verification and stop on error

## Troubleshooting

### Quick Diagnosis

First, run the validation script to identify issues:
```bash
python validate_config.py --check_fastq --data_type your_data_type
```

### Common problems and solutions

1. **Job failure**:
   - Check log files in `logs/`
   - Run `python validate_config.py` to identify configuration issues
   - Verify that the YAML file exists and is correctly formatted
   - Verify that all specified FASTQ files exist

2. **Conda environment**:
   ```bash
   # Recreate environment
   rm -rf env/envMultiQC
   sbatch create_env_multiQC.sh
   ```

3. **Missing files**:
   - Check paths in the YAML file
   - Check read permissions on files

4. **Insufficient memory**:
   - Increase allocated memory in `run_multiQC.sh`
   - Use subsampled files for testing

### Common error messages

- **"YAML file not found"**: Check path to YAML file
- **"No samples found"**: Verify that `data_type` exists in YAML
- **"FastQ file not found"**: Check FASTQ file paths
- **"Cannot create output directory"**: Check write permissions

## Results Validation

### Points to verify:
1. **Output files**: Presence of FastQC and MultiQC reports
2. **Logs**: No errors in log files
3. **MultiQC reports**: HTML files open correctly
4. **Consistency**: Number of FastQC reports = number of processed samples

## Maintenance

### Update environment:
```bash
# Modify environment_multiQC.yml then:
sbatch create_env_multiQC.sh
```

### Clean up logs:
```bash
# Remove old logs (optional)
rm logs/multiqc_*
```
