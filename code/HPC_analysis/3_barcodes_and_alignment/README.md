# Barcodes and Alignment Analysis

This directory contains tools and pipelines for barcode processing and sequence alignment in microSPLIT single-cell RNA-seq analysis.

## Contents

### 📁 STARsolo/
Complete pipeline for single-cell RNA-seq alignment and quantification using STARsolo.

- **Purpose**: Genome alignment and gene quantification for microSPLIT data
- **Technology**: STAR aligner with single-cell extensions
- **Features**: 3-round barcode processing, automated validation, HPC cluster support
- **Documentation**: See `STARsolo/README.md` for detailed usage instructions

### 📁 BarQC/
Alternative Split-seq processing tool (experimental).

- **Purpose**: Extract, correct, and tag barcodes from Split-seq reads with statistical reports and visualizations
- **Features**: Barcode heatmaps, UMI statistics, quality control, multithreading support  
- **Source**: [mayflylab/barQC](https://github.com/mayflylab/barQC) - MIT licensed tool by Maria Rossello
- **Status**: Alternative method currently in testing phase (not used in production workflow)
- **Note**: Specialized for Split-seq data processing, not integrated into the main STARsolo pipeline

## Workflow

The current production workflow uses:

1. **Alignment and Quantification** (`STARsolo/`) - Primary pipeline for genome alignment and gene quantification with built-in barcode processing

## Support

For detailed usage instructions, refer to the individual README files in each subdirectory. 