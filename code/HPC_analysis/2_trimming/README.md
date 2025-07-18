# Trimming Pipeline for microSPLIT Data

This pipeline processes FASTQ sequencing data by applying several successive trimming steps to remove adapters, TSO sequences, polyA tails, and other contaminants specific to microSPLIT experiments.

## Overview

The pipeline consists of 6 sequential trimming steps:
1. **TSO trimming** - Removes TSO (Template Switch Oligo) sequences
2. **Initial fastp** - Initial trimming with automatic adapter detection
3. **PolyA trimming** - Removes polyA tails
4. **Specific adapter** - Removes CCACAGTCTCAAGCAC adapter
5. **Linker trimming** - Removes linkers and specific adapters
6. **Final fastp** - Final trimming with specific parameters

## File Structure

### Main files
- **`Trim.sh`** : Main script that submits SLURM jobs
- **`process_sample.sh`** : Script that processes individual samples
- **`create_env_trimming.sh`** : Script to create conda environment
- **`environment_trimming.yml`** : Conda environment definition

### Required tools
- **cutadapt** (v5.0) : For adapter trimming
- **fastp** (v0.24.1) : For trimming and quality control
- **Python** (≥3.6) : For YAML parsing
- **bc** : For memory calculations

## Usage

### 1. Creating the conda environment

```bash
# Submit the environment creation job
sbatch create_env_trimming.sh
```

### 2. Running the pipeline

```bash
# Process all samples
sbatch Trim.sh

# Process a specific sample
sbatch Trim.sh --sample "BC_0076"

# Specify output directory
sbatch Trim.sh --output-dir "/path/to/output"

# Adjust SLURM resources
sbatch Trim.sh --cpus 32 --mem 200G --time 10-00:00:00 --partition bigmem
```

### Available options

- `--output-dir DIR` : Output directory
- `--sample SAMPLE` : Process specific sample
- `--input-type TYPE` : Input type (unzipped/subsampled)
- `--run-id ID` : Run identifier
- `--cpus N` : Number of CPUs (default: 32)
- `--mem MEM` : Memory per node (default: 200G)
- `--time TIME` : Time limit (default: 10-00:00:00)
- `--partition PART` : SLURM partition (genouest/bigmem)

## Input data structure

The pipeline reads samples from a YAML file:
```yaml
samples:
  BC_0076:
    R1:
      unzipped: "/path/to/BC_0076_R1.fastq.gz"
      subsampled: "/path/to/BC_0076_R1_subsampled.fastq.gz"
    R2:
      unzipped: "/path/to/BC_0076_R2.fastq.gz"
      subsampled: "/path/to/BC_0076_R2_subsampled.fastq.gz"
```

## Results structure

For each sample, the pipeline creates the following structure:

```
results/
└── run_TIMESTAMP/
    └── INPUT_TYPE/
        └── SAMPLE_NAME/
            ├── 1_tso_trimming/
            ├── 2_fastp_initial/
            ├── 3_polya_trimming/
            ├── 4_specific_adapter/
            ├── 5_linker_trimming/
            ├── 6_fastp_final/
            ├── resource_usage/
            ├── SAMPLE_NAME_R1_final.fastq.gz -> 6_fastp_final/SAMPLE_NAME_R1.fastq.gz
            └── SAMPLE_NAME_R2_final.fastq.gz -> 6_fastp_final/SAMPLE_NAME_R2.fastq.gz
```

## Trimming parameters

### TSO (Template Switch Oligo)
- Sequences: `AAGCAGTGGTATCAACGCAGAGTGAATGGG`, `CAGAGTGAATGGG`
- Minimum overlap: 6 bp
- Maximum errors: 20%

### Initial fastp
- Minimum length: 91 bp
- PolyG trimming: 10 bp minimum
- PolyX trimming: 12 bp minimum
- Adapters: `ATCTCGTATGCCGTCTTCTGCTTGA`, `AGATCGGAAGAGCACACGTCTGAACTCCAGTCAC`

### PolyA
- Pattern: `A{12}` (12 consecutive A's)
- Minimum overlap: 12 bp
- Maximum errors: 20%

### Specific adapter
- Sequence: `CCACAGTCTCAAGCAC`
- Minimum overlap: 6 bp
- Maximum errors: 10%

### Linkers
- Sequences: `CCACAGTCTCAAGCACGTGGAT`, `AGTCGTACGCCGATGCGAAACATCGGCCAC`, `AGATCGGAAGAGCACACGTCTGAACTCCAGTCA`
- Minimum overlap: 6 bp
- Maximum errors: 20%

### Final fastp
- Trim front R1: 10 bp
- Trim tail R1: 16 bp
- Trim front R2: 0 bp
- Trim tail R2: 0 bp
- Minimum length: 25 bp

## Resource monitoring

The pipeline includes a resource monitoring system:
- Automatic memory requirement estimation based on file sizes
- Memory usage monitoring during processing
- Resource report generation for each sample

## Logs and reports

- **SLURM logs** : `logs/slurm/`
- **Pipeline logs** : `logs/RUN_ID.log`
- **Sample logs** : `logs/RUN_ID_SAMPLE.log`
- **Fastp reports** : HTML and JSON files in each step directory
- **Cutadapt statistics** : JSON files in each step directory

## Issues resolved and corrections made

### ✅ Applied corrections

1. **Relative paths** : All paths are now relative to the script directory
2. **Fixed YAML path** : The environment file is now correctly referenced
3. **Secured SLURM variables** : SLURM variables have default values if not defined
4. **Improved error handling** : Better robustness in non-SLURM environments

### 🔧 Added features

1. **Local compatibility** : The pipeline can now run outside of a SLURM environment
2. **Dynamic paths** : Automatic adaptation to different directory structures
3. **Default values** : Fallback parameters for all execution contexts

## Complete usage example

```bash
# 1. Create the environment
sbatch create_env_trimming.sh

# 2. Wait for environment creation, then run the pipeline
sbatch Trim.sh --sample "BC_0076 BC_0077" --cpus 16 --mem 100G --time 5-00:00:00

# 3. Check results
ls -la results/run_*/unzipped/*/
```

## Prerequisites before use

1. **Directory structure** : Ensure the following directories exist:
   - `../../env/` (for conda environment)
   - `../../data/info/samples/` (for samples YAML file)

2. **Samples YAML file** : Create the file `../../data/info/samples/samples_trimming.yaml` with appropriate structure

3. **Testing** : Always test on one sample before running on all samples

## Maintenance

- Regularly check disk space (intermediate files take up significant space)
- Monitor SLURM logs for errors
- Adjust resource parameters as needed
- Clean up old runs if necessary 