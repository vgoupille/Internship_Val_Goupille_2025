# Useful Scripts for HPC Analysis

This directory contains a collection of utility scripts designed for high-performance computing (HPC) environments, specifically for processing single-cell RNA sequencing data. All scripts are optimized for SLURM job scheduler and use conda environments for dependency management.

## Directory Structure

### 📁 `create_subsamples_fastq_reads/`
Scripts for creating subsamples of FASTQ files for testing and development purposes.

#### Subdirectories:
- **`first_reads/`** - Extract the first N reads from FASTQ files
  - `extract_first_reads.py` - Python script for extracting first reads
  - `run_extract_reads.sh` - SLURM wrapper script
  - `README.md` - Detailed documentation
  
- **`random_reads/`** - Extract random reads from FASTQ files
  - `run_subsampling_random.sh` - SLURM script using seqtk for random sampling
  - `README.md` - Detailed documentation

#### Configuration files:
- `create_env_subsampling.sh` - Script to create conda environment
- `environment_subsampling.yml` - Conda environment specification

**Use cases:**
- Creating test datasets with reduced file sizes
- Developing and testing pipelines with smaller datasets
- Quality control and validation of processing steps

---

### 📁 `download_and_transfert_data/`
Scripts for downloading and transferring data between repositories.

#### Scripts:
- `download_script.sh` - Downloads NTS-412 FASTQ data with retry mechanism
- `download_script2.sh` - Alternative download script
- `transfert_data_repo_to_repo.sh` - Transfer data between repositories

**Use cases:**
- Automated data retrieval from external sources
- Moving data between different storage locations
- Backup and synchronization operations

---

### 📁 `explore_files/`
Utility scripts for exploring and inspecting file contents.

#### Scripts:
- `list_zip.sh` - Lists contents of ZIP archives
- `view_fastq_head.sh` - Displays the first lines of gzipped FASTQ files

**Use cases:**
- Quick inspection of compressed files
- Validating file contents before processing
- Debugging file format issues

---

### 📁 `extract_decompress/`
Scripts for extracting and decompressing various file formats.

#### Scripts:
- `extract_script.sh` - Extracts ZIP files (specifically NTS-412 data)
- `extract_specific.sh` - Extracts specific files from archives
- `decompress_fastq.sh` - Decompresses FASTQ.gz files with options

**Use cases:**
- Automated extraction of compressed datasets
- Selective extraction of specific files
- Batch decompression with optional cleanup

---

### 📁 `merge_fastq/`
Scripts for merging multiple FASTQ files into single consolidated files.

#### Scripts:
- `merge_fastq_wrapper.sh` - Main wrapper script for merging R1 and R2 files
- `README.md` - Detailed documentation and usage examples

**Use cases:**
- Combining multiple samples into a single dataset
- Preparing merged datasets for downstream analysis
- Reducing file management complexity

---

## General Usage Guidelines

### Prerequisites
- SLURM workload manager
- Conda package manager
- Appropriate file permissions and storage access
- YAML configuration files for sample information

### Common Workflow
1. **Data Download**: Use `download_and_transfert_data/` scripts
2. **Data Extraction**: Use `extract_decompress/` scripts
3. **Data Exploration**: Use `explore_files/` scripts for validation
4. **Data Subsampling**: Use `create_subsamples_fastq_reads/` for testing
5. **Data Merging**: Use `merge_fastq/` for consolidation

### SLURM Integration
All scripts are designed to work with SLURM job scheduler:
- Job submission with appropriate resource allocation
- Automatic log file generation
- Error handling and retry mechanisms
- Parallel processing when applicable

### Configuration
Most scripts use YAML configuration files located in `data/info/samples/`:
- `samples_all.yaml` - Complete sample information
- `samples_subsampled.yaml` - Subsampled datasets
- `samples_trimming.yaml` - Trimmed datasets

## Support
For detailed information about specific scripts, refer to the README files in each subdirectory. Each script contains usage examples and parameter descriptions.

## Notes
- All scripts assume a specific project directory structure
- Paths are relative to the project root
- Scripts are optimized for bacterial single-cell RNA sequencing data
- Some scripts are specific to NTS-412 dataset but can be adapted for other datasets 