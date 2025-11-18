# Unused Multi-Sample Scripts

This directory contains STARsolo scripts that were designed for processing multiple samples individually, but are no longer used in the current workflow.

## Moved Scripts

- **`run_all_samples.sh`** - Script for processing multiple samples from YAML configuration
- **`submit_pipeline.sh`** - SLURM job submission wrapper for individual samples

## Why Moved

The current workflow uses **merged data analysis** approach:
- All samples are pre-merged into `merged_trimmed-R1.fastq.gz` and `merged_trimmed-R2.fastq.gz`
- Single STARsolo run processes all samples together
- Simpler, more efficient for the current dataset

## Current Workflow

Use the main STARsolo scripts in the parent directory:
- `config.sh` - Configuration for merged data analysis
- `starsolo_microsplit_pipeline.sh` - Main pipeline script
- `create_env_STARsolo.sh` - Environment setup

These scripts are optimized for merged data processing with 600GB memory allocation.