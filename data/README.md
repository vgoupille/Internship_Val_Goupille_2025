# Data Directory Organization

> **MicroSPLiT Single-Cell RNA-seq Data for Pseudomonas brassicacearum R401**  
> This directory contains all processed and intermediate data files from the bacterial single-cell transcriptomics experiment investigating Division of Labor under contrasting iron conditions.

## 📁 Directory Structure Overview

### `Anndata/`
**Python single-cell data objects for Scanpy analysis**
- `raw/` - Direct STARsolo conversion outputs (6 different matrix types)
- `with_metadata/` - Data objects enriched with experimental metadata 
- `filtered/` - High-quality datasets after quality filtering pipeline (3a→3b→3c)
- `csv/` - Filtering statistics and metadata summaries

**Key files:**
- `GeneFull_raw_unique_mult_with_metadata_grouped_filtered_100UMI_3c.h5ad` - Final filtered dataset

### `barcodes_result/`
**Cell barcode processing and metadata generation**
- `barcodeSTARsolo/filtered/` - Clean barcodes for STARsolo alignment (3 rounds)
- `combinations/` - Barcode combination analyses and filtering
- `extracted_barcodes/` - Raw and filtered barcode extractions
- `metadata_DOL_Exp1_complete.csv` - Complete cell metadata with experimental conditions

### `genome_annotation/` & `genome_ref/`
**Reference genome files for *Pseudomonas brassicacearum* R401**
- `GCA_030064105.1_ASM3006410v1_genomic.gff` - Genome annotation
- `GCA_030064105.1_ASM3006410v1_genomic.fna` - Reference genome sequence
- `ncbi_dataset_with_id.tsv` - Gene information and annotations

### `info/`
**Experiment configuration and sample information**
- `experiment/experiment.yaml` - Complete experimental protocol and library structure
- `samples/samples_trimming.yaml` - Sample paths and processing information

### `meta/`
**Original experimental metadata**
- `metadata_DOL_rep1.xlsx` - Raw experimental design and cell assignments
- `plan_exp.xlsx` - Growth curve data and sampling timepoints

### `QC_file/`
**Quality control reports from FastQC and MultiQC**
- `multiqc_results_unzipped/` - QC on raw data (R1/R2 reports)
- `multiqc_results_trimmed/` - QC on merged trimmed data
- `multiqc_results_trimmed_individual/` - QC on individual trimmed samples

### `RDS/`
**R/Seurat objects for R-based analysis**
- `GeneFull_raw_unique_mult_with_metadata_grouped_filtered_100UMI_3c_SeuratV5.rds` - Seurat V5 object

### `STARsolo_result/`
**Genome alignment and quantification outputs**
- `merged_trimmed/merged/` - STARsolo results for merged libraries
- Contains count matrices, barcodes, features, and alignment statistics
- **Note:** Large BAM files (>250GB) remain on HPC cluster

### `subsampled_data/`
**Test datasets for pipeline development**
- `first_reads/5000_reads/` - Subsampled FASTQ files (5000 reads per library) for testing

---

## 🔄 Data Processing Pipeline Flow

The data organization reflects the sequential processing steps of the microSPLiT pipeline:

1. **Raw Data** → **Quality Control** (`QC_file/`)
2. **Barcode Processing** (`barcodes_result/`) 
3. **Trimming & Merging** → **Alignment** (`STARsolo_result/`)
4. **Data Conversion** (`Anndata/raw/`, `RDS/`)
5. **Metadata Integration** (`Anndata/with_metadata/`)
6. **Quality Filtering** (`Anndata/filtered/`)
7. **Analysis Ready Data** 

## 📊 Key Data Files for Analysis

**For Python/Scanpy users:**
- `Anndata/filtered/GeneFull_raw_unique_mult_with_metadata_grouped_filtered_100UMI_3c.h5ad`

**For R/Seurat users:**
- `RDS/GeneFull_raw_unique_mult_with_metadata_grouped_filtered_100UMI_3c_SeuratV5.rds`

**Metadata and configuration:**
- `barcodes_result/metadata_DOL_Exp1_complete.csv`
- `info/experiment/experiment.yaml`

---

## ⚠️ Data Availability Notes

**Complete dataset location:** This repository contains processed and analysis-ready data. Large intermediate files are stored on the HPC cluster due to GitHub's file size limitations.

**Missing from repository:**
- Raw FASTQ files (multi-GB, available on HPC)
- Large BAM alignment files (>250GB, available on HPC) 
- Some large intermediate processing files

**Available in repository:**
- All analysis-ready datasets (filtered AnnData, Seurat objects)
- Quality control reports and statistics
- Metadata and configuration files
- Reference genome and annotations
- Barcode processing results

**To access complete data:** Contact the project maintainer or access the HPC cluster at GenOuest where the full dataset is archived.