# Project Data Organization

## Data Directory Structure

### `Anndata/`
Contains AnnData files formatted for Scanpy analysis, organized according to different processing steps.

### `barcodes_result/`
Groups barcodes necessary for STARsolo analysis as well as complete project metadata.

### `genome_annotation/`
Contains the genomic annotation file for the Cologne strain used as reference.

### `genome_ref/`
Stores the reference sequence of the Cologne strain genome.

### `info/`
Includes information about sequencing data structure:
- `experiment/` : summarizes experiment information
- `samples/` : contains absolute links to FASTQ files

### `meta/`
Contains original Excel files with metadata:
- Useful for building STARsolo barcodes and assigning metadata
- `plan_exp.xlsx` is particularly useful for adding timepoints

### `multiqc/`
MultiQC analysis results at different stages:
- Before trimming
- After trimming  
- Merged data after trimming
- Also includes FastQC results

### `RDS/`
Contains files in RDS format for analyses in R.

### `STARsolo_result/`
Contains STARsolo outputs (without ~250 GB BAM files that remain available on the cluster).

---

⚠️ **IMPORTANT: Large files missing from repository**

This GitHub repository does **not** contain all data files due to GitHub's file size limitations (100MB max per file). Several directories appear empty or incomplete because large files are ignored by `.gitignore`.

## Missing files to retrieve

### 📁 Directories mostly empty in the repo:
- **`raw_data/`** - Original FASTQ files (ignored)
- **`Trim_process/`** - Data after trimming (ignored)  
- **`merged_data/`** - Merged files (ignored)
- **`subsampled_data/`** - Subsampled data (partially ignored)

### 📄 File types ignored:
- Files `.fastq`, `.fastq.gz`, `.bam`, `.gz` 
- Files `.h5ad` > 100MB
- Files `.rds`, `.RDS` > 100MB

**→ Go on the HPC server to retrieve complete data**