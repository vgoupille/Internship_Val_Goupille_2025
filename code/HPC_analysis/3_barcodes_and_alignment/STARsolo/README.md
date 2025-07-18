# STARsolo Pipeline for microSPLIT Analysis

This folder contains a complete pipeline for single-cell RNA-seq data analysis using microSPLIT technology with STARsolo.

## Overview

The pipeline is designed to process microSPLIT data with:
- **3 barcoding rounds** (3 barcode files)
- **Genome alignment** with STAR
- **Quantification** with STARsolo
- **HPC cluster execution** with SLURM

## System Architecture

### Main Files

1. **`config.sh`** - Central configuration file
2. **`starsolo_microsplit_pipeline.sh`** - Main pipeline script
3. **`submit_pipeline.sh`** - SLURM submission wrapper
4. **`run_all_samples.sh`** - Execution for all samples
5. **`create_env_STARsolo.sh`** - Conda environment creation
6. **`environment_STARsolo.yml`** - Environment specification

### Workflow

```
config.sh → submit_pipeline.sh → starsolo_microsplit_pipeline.sh
    ↓
Environment Setup → Directory Setup → STARsolo Analysis
    ↓
GFF→GTF conversion → Index generation → Alignment & Quantification
```

## Usage

### 1. Configuration

Edit the `config.sh` file to define:
- Input data paths
- FASTQ file names
- Resources (CPU, memory, time)
- Output paths

### 2. Environment Creation (first time)

```bash
sbatch create_env_STARsolo.sh
```

### 3. Single Sample Execution

```bash
# Recommended method
./submit_pipeline.sh --threads 64 --memory 500G --runtime 10-00:00:00

# Or directly with sbatch
sbatch starsolo_microsplit_pipeline.sh
```

### 4. All Samples Execution

```bash
# All samples
sbatch run_all_samples.sh

# Specific sample
sbatch run_all_samples.sh --sample BC_0076

# With specific partition
sbatch run_all_samples.sh --partition bigmem
```

## STARsolo Parameters

The pipeline uses the following parameters for microSPLIT:

```bash
--soloType CB_UMI_Complex
--soloCBposition 0_10_0_17 0_48_0_55 0_78_0_85  # 3 complex barcodes
--soloUMIposition 0_0_0_9                        # UMI at position 0-9
--soloCBwhitelist barcode_round3.txt barcode_round2.txt barcode_round1.txt
--soloCBmatchWLtype 1MM                          # 1 mismatch allowed
--soloUMIdedup 1MM_All                           # UMI deduplication
--soloFeatures Gene GeneFull                     # Gene and exon quantification
```

## Data Structure

### Expected Input
```
data/
├── processed_data/merged_data/trimmed/     # Trimmed FASTQ files
├── raw_data/barcodes/barcodeSTARsolo/filtered/  # Filtered barcodes
├── raw_data/genome_ref/                    # Reference genome
└── raw_data/genome_annotation/             # Genome annotation
```

### Generated Output
```
output_directory/
├── raw_data/                               # Symbolic links
├── Output_DOL_microsplit_starsolo2/
│   ├── genome_index/                       # STAR index
│   └── starsolo_output2/
│       ├── Log.final.out                   # Alignment statistics
│       └── Solo.out/
│           ├── Gene/                       # Gene count matrices
│           └── GeneFull/                   # Exon count matrices
```

## Logic Analysis

### ✅ Strengths

1. **Modularity**: Clear separation of responsibilities
2. **Flexibility**: Configurable parameters via config.sh
3. **Error Handling**: Verification at each step
4. **Multi-sample Support**: Batch processing capability
5. **Isolated Environment**: Clean conda management

### ⚠️ Identified Improvements

1. **Hardcoded Paths**: Some paths reference obsolete structures
2. **Redundancy**: Environment creation in main script AND dedicated script
3. **Template Configuration**: Mix of templates and real values in config.sh
4. **Error Handling**: Could be more robust for missing files

### 🔧 Suggested Improvements

1. **Clean Paths** in config.sh (lines 43-44)
2. **Separate Logic** for environment creation
3. **Improve Validation** of input files
4. **Add Detailed Logs**
5. **Document** STARsolo-specific parameters

## Recommended Resources

- **CPU**: 64 threads minimum (32 may be insufficient)
- **Memory**: 500G (128G minimum, 600G recommended)
- **Time**: 10-48h depending on data size
- **Partition**: `bigmem` for large samples

## Dependencies

- **STAR** v2.7.9 - Aligner
- **cufflinks** v2.2.1 - Analysis tools
- **gffread** v0.12.1 - GFF/GTF conversion
- **yq** - YAML parsing
- **Python** 3.6+

## Troubleshooting

### Common Errors

1. **Conda environment not found**: Check CONDA_ENV_PATH
2. **Missing input files**: Check SOURCE_* paths
3. **Insufficient memory**: Increase MEMORY in config.sh
4. **Timeout**: Increase MAX_RUNTIME

### Verification Commands

```bash
# Check environment
conda env list | grep STARsolo

# Check input files
ls -la /projects/microsplit/data/processed_data/merged_data/trimmed/

# Check barcodes
ls -la /projects/microsplit/data/raw_data/barcodes/barcodeSTARsolo/filtered/
```

## Testing Improvements

After the improvements, you can test the pipeline:

```bash
# 1. Verify configuration
source config.sh
echo "Configuration loaded for: $ANALYSIS_NAME"

# 2. Test YAML validation
./run_all_samples.sh --sample BC_0076 --type merged_trimmed

# 3. Test input file validation
# The pipeline will stop cleanly if files are missing
```

### Applied Improvements ✨

1. **✅ Corrected Paths**: Fixed `SOURCE_GENOME_ANNOTATION` path
2. **✅ Optimized Environment**: Removed redundant environment creation
3. **✅ Robust Validation**: Systematic verification of YAML and input files
4. **✅ Clear Configuration**: Separation of templates and real values
5. **✅ Improved Error Handling**: More informative error messages

## Support

- **Logs**: Check .out and .err files generated by SLURM
- **STARsolo Documentation**: [STAR Manual](https://github.com/alexdobin/STAR/blob/master/doc/STARmanual.pdf)
- **Contact**: valentin.goupille@univ-rennes.fr 