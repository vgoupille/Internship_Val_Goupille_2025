# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains a complete bioinformatics workflow for analyzing bacterial single-cell RNA sequencing data using microsplit technology. The project investigates division of labor in Pseudomonas bacteria using single-cell RNA-seq analysis.

## Project Structure

### Core Directories

- **`code/HPC_analysis/`** - High-performance computing scripts for data processing
- **`code/Local_analysis/`** - Local analysis scripts using Python (scanpy, pandas)
- **`data/`** - All data files organized by processing stage
- **`internship_deliverables/`** - Thesis and presentation materials

### Key Analysis Pipeline

The analysis follows this sequence:
1. **Quality Control** (`1_QC_multiqc_fastqc/`) - FastQC and MultiQC analysis
2. **Trimming** (`2_trimming/`) - Adapter trimming using cutadapt
3. **Alignment** (`3_barcodes_and_alignment/STARsolo/`) - STARsolo alignment with barcode processing
4. **Local Analysis** - Python-based filtering and analysis using AnnData/Scanpy

## Common Development Commands

### HPC Analysis (SLURM-based)

```bash
# Run MultiQC analysis
cd code/HPC_analysis/1_QC_multiqc_fastqc/
sbatch launch_multiQC_jobs.sh

# Run STARsolo alignment
cd code/HPC_analysis/3_barcodes_and_alignment/STARsolo/
sbatch run_all_samples.sh

# Run specific sample
./run_all_samples.sh --sample BC_0076 --type merged_trimmed
```

### Local Analysis

```bash
# Convert STARsolo to AnnData
cd code/Local_analysis/
python 2a_starsolo_to_anndata.py

# Run filtering pipeline
python 3a_filtering_100UMIs.py
python 3b_filtering_advanced_cell_v2.py
python 3c_filtering_advanced_gene.py

# Launch Jupyter for interactive analysis
jupyter lab
```

### Thesis Building

```bash
# Build thesis (Quarto)
cd internship_deliverables/Msc_thesis/
quarto render

# Preview thesis
quarto preview
```

## Environment Management

### HPC Environments
- **MultiQC**: `environment_multiQC.yml` - FastQC and MultiQC tools
- **Trimming**: `environment_trimming.yml` - cutadapt and trimming tools
- **STARsolo**: `environment_STARsolo.yml` - STAR aligner and dependencies

### Local Environment
The project uses standard bioinformatics Python packages:
- `scanpy` - Single-cell analysis
- `anndata` - Data structures for single-cell data
- `pandas`, `numpy` - Data manipulation
- `matplotlib`, `seaborn` - Visualization

## Data Organization

### Input Data Structure
- YAML configuration files in `data/info/samples/` define sample paths and metadata
- Raw FASTQ files referenced through YAML configs
- Multiple processing stages tracked (unzipped, trimmed, merged)

### Key Data Files
- **`data/info/experiment/experiment.yaml`** - Complete experimental protocol and library structure
- **`data/info/samples/samples_all.yaml`** - Sample paths and metadata
- **`data/Anndata/`** - AnnData objects at different filtering stages
- **`data/barcodes_result/`** - Extracted barcodes and metadata

### BacSC Module
Custom Python module (`code/Local_analysis/BacSC/`) provides:
- `ClusterDE.py` - Differential expression analysis
- `scTransform.py` - Data transformation
- `countsplit.py` - Count splitting for validation
- `clustering_opt.py` - Clustering optimization
- `util.py` - General utilities

## Architecture Notes

### HPC Integration
- All HPC scripts use SLURM workload manager
- Scripts automatically handle conda environment creation/activation
- Resource allocation optimized for bacterial scRNA-seq data sizes
- Extensive error handling and logging

### Data Flow
1. Raw FASTQ files → Quality control (FastQC/MultiQC)
2. Trimmed reads → STARsolo alignment with barcode extraction  
3. Count matrices → AnnData objects with metadata integration
4. Filtered data → Downstream analysis (clustering, differential expression)

### Configuration System
- YAML-based configuration throughout the pipeline
- Centralized sample management in `samples_all.yaml`
- Experimental protocol documented in `experiment.yaml`
- Flexible path management for different processing stages

## Development Notes

### Key Analysis Scripts
- **`2a_starsolo_to_anndata.py`** - Converts STARsolo output to AnnData format
- **`3a_filtering_100UMIs.py`** - Initial UMI-based filtering
- **`3b_filtering_advanced_cell_v2.py`** - Advanced cell quality filtering
- **`3c_filtering_advanced_gene.py`** - Gene-level filtering

### Jupyter Integration
- Interactive versions of analysis scripts in `code/Local_analysis/jupyter/`
- Main analysis notebooks: `6a_scanpy.ipynb`, `6b_Global_BacSC_tutorial_general_Val.ipynb`, `7_seurat.ipynb`

### Visualization Functions
- Custom plotting functions in `visualization_functions.py`
- Standardized figure generation for thesis

When working on this codebase, prioritize understanding the YAML configuration system and the sequential data processing pipeline from raw reads to filtered single-cell data objects.