# Local Analysis Scripts

> **Python-based analysis pipeline for microSPLiT bacterial single-cell RNA-seq data**  
> This directory contains all local analysis scripts for processing *Pseudomonas brassicacearum* R401 single-cell transcriptomics data from STARsolo outputs to analysis-ready datasets.

## 📜 Script Overview

### `0_growth_bacteria_fig.py`
**Purpose:** Genome and transcriptome description analysis (before filtering)

- Analyzes bacterial growth curves from experimental data
- Generates growth visualization plots for M9 vs M9F conditions
- Processes optical density measurements across timepoints and replicates
- Creates figures showing sampling points for single-cell analysis
- **Input:** `data/meta/plan_exp.xlsx`
- **Output:** Growth curve plots and experimental timeline visualizations

### `1_barcode_processing.py` 
**Purpose:** Generate metadata and barcodes for downstream analysis

- Extracts and processes 3-round microSPLiT barcodes from experimental metadata
- Creates filtered barcode files for STARsolo alignment
- Generates comprehensive cell metadata linking barcodes to experimental conditions
- Essential prerequisite for all subsequent analysis scripts
- **Input:** `data/meta/metadata_DOL_rep1.xlsx`
- **Output:** 
  - `data/barcodes_result/barcodeSTARsolo/filtered/` - Clean barcodes
  - `data/barcodes_result/metadata_DOL_Exp1_complete.csv` - Cell metadata

### `2a_starsolo_to_anndata.py`
**Purpose:** Convert STARsolo output to AnnData format

- Converts STARsolo count matrices to AnnData objects for Python analysis
- Creates multiple data objects (Gene/GeneFull, raw/filtered, different mapping strategies)
- Preserves all STARsolo metadata and statistics
- **Input:** `data/STARsolo_result/merged_trimmed/merged/`
- **Output:** `data/Anndata/raw/` - 6 different AnnData objects

### `2b_correct_ncbi_gene_annotation.py`
**Purpose:** Correct and enhance gene annotations

- Fixes NCBI gene annotation inconsistencies
- Adds gene symbols and functional annotations
- Standardizes gene naming across the dataset
- **Input:** Raw gene annotations
- **Output:** Corrected annotation files

### `2c_add_metadata_to_anndata.py`
**Purpose:** Integrate experimental metadata into AnnData objects

- Adds cell metadata (conditions, timepoints, replicates) to AnnData objects
- Links barcode combinations to experimental conditions
- Creates analysis-ready data objects with complete metadata
- **Input:** Raw AnnData objects + metadata from step 1
- **Output:** `data/Anndata/with_metadata/` - Metadata-enriched objects

### `3a_filtering_100UMIs.py`
**Purpose:** Initial UMI-based quality filtering

- Removes cells with fewer than 100 UMIs (low-quality cells)
- First step in the quality filtering pipeline
- Generates filtering statistics and visualizations
- **Input:** Metadata-enriched AnnData objects
- **Output:** `data/Anndata/filtered/` - UMI-filtered datasets

### `3b_filtering_advanced_cell_v2.py`
**Purpose:** Advanced cell quality filtering

- Identifies and removes doublets (technical artifacts)
- Removes low-quality cells based on multiple metrics
- Selects best-performing technical replicates
- **Input:** UMI-filtered datasets from step 3a
- **Output:** Cell-filtered datasets with quality statistics

### `3c_filtering_advanced_gene.py`
**Purpose:** Advanced gene filtering and annotation

- Filters to protein-coding genes only
- Removes lowly expressed genes (<5 cells)
- Adds gene expression threshold annotations (5%, 10%, 15%)
- Generates comprehensive filtering reports
- **Input:** Cell-filtered datasets from step 3b
- **Output:** Final filtered datasets ready for analysis

### `4a_anndata_to_RDS.py`
**Purpose:** Convert AnnData to Seurat RDS format

- Converts filtered Python datasets to Seurat V5 format for R users
- Preserves all cell and gene metadata
- Creates R-compatible single-cell objects
- **Input:** Final filtered AnnData objects
- **Output:** `data/RDS/` - Seurat objects for R analysis

### `5_genome_transcriptome_description.py`
**Purpose:** Genome and transcriptome characterization

- Analyzes genome composition and gene content
- Generates transcriptome statistics and visualizations
- Characterizes gene types and functional categories
- **Input:** Genome annotation and filtered datasets
- **Output:** Genome/transcriptome description plots and statistics

## 📓 Analysis Notebooks

### Main Analysis Notebooks:
- `6a_scanpy.ipynb` - Standard Scanpy single-cell analysis workflow
- `6b_Global_BacSC_tutorial_general_Val.ipynb` - Bacterial-specific analysis with BacSC
  - ⚠️ **Note:** This notebook was used to generate figures for the thesis but is currently disorganized and not up-to-date with the latest pipeline
  - Uses partially modified and non-optimized BacSC scripts
  - Contains exploratory analysis and preliminary results
  - Recommended to use for reference only, not as a final analysis workflow
- `7_seurat.ipynb` - R/Seurat-based analysis (alternative workflow)

## 📁 Supporting Modules

### `BacSC/`
**Custom bacterial single-cell RNA-seq analysis module**

- `scTransform.py` - Bacterial-optimized normalization
- `ClusterDE.py` - Differential expression analysis
- `clustering_opt.py` - Clustering optimization tools
- `countsplit.py` - Count splitting for validation
- `util.py` - General utilities

### `visualization_functions.py`
**Standardized plotting functions**

- Consistent visualization across all analysis scripts
- Quality control plots and statistics
- Growth curves and experimental design figures

## 🔄 Analysis Pipeline Flow

The scripts should be executed in numerical order:

```bash
0_ (optional) → 1_ → 2a_ → 2b_ → 2c_ → 3a_ → 3b_ → 3c_ → 4a_ (optional) → 5_ → 6_/7_
```

**Dependencies:**

- Scripts 2b, 2c, 3a, 3b, 3c must be run sequentially
- Script 1 is required before all STARsolo processing
- Script 4a is optional (only needed for R analysis)
- Notebooks 6_/7_ use outputs from the complete pipeline

## ⚡ Quick Start

**For Python/Scanpy analysis:**

1. Run scripts 1 → 2a → 2c → 3a → 3b → 3c
2. Open `6a_scanpy.ipynb` (recommended) or `6b_Global_BacSC_tutorial_general_Val.ipynb` (reference only)

**For R/Seurat analysis:**

1. Complete Python pipeline through 3c
2. Run script 4a for RDS conversion
3. Open `7_seurat.ipynb`