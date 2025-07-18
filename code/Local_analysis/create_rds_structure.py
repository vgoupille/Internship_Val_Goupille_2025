#!/usr/bin/env python3
"""
Script to create the RDS directory structure for R object storage.

Author: Valentin Goupille
Date: 2025-01-13
"""

import os
from pathlib import Path


def create_rds_structure():
    """
    Create the RDS directory structure for storing R objects.
    """
    print("📁 Creating RDS directory structure...")

    # Define the RDS directory (at the same level as Anndata)
    rds_dir = Path("data/RDS")

    # Create directory
    rds_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created: {rds_dir}")

    # Create a README file explaining the RDS structure
    readme_content = """# RDS Objects Directory

This directory contains R objects (RDS format) converted from AnnData objects.

## Purpose

The RDS format allows seamless integration with R analysis tools, particularly:
- **Seurat** for single-cell RNA-seq analysis
- **SingleCellExperiment** for Bioconductor workflows
- **Custom R scripts** for downstream analysis

## File Naming Convention

RDS files follow this pattern:
```
[original_anndata_name]_[conversion_target].rds
```

Examples:
- `GeneFull_raw_unique_mult_with_metadata_grouped_filtered_100UMI_3c_SeuratV5.rds`
- `GeneFull_raw_unique_mult_with_metadata_grouped_filtered_100UMI_3c_SCE.rds`

## Source Scripts

- `4a_anndata_to_RDS.py` - Converts AnnData to Seurat V5 objects

## Usage in R

```r
# Load Seurat object
library(Seurat)
seurat_obj <- readRDS("data/RDS/GeneFull_raw_unique_mult_with_metadata_grouped_filtered_100UMI_3c_SeuratV5.rds")
print(seurat_obj)

# Access components
counts <- seurat_obj[["RNA"]]@counts
cell_metadata <- seurat_obj@meta.data
gene_metadata <- seurat_obj[["RNA"]]@meta.data
```

## Integration with Pipeline

This directory is part of the organized data structure:
```
data/
├── Anndata/       # Python AnnData objects
│   ├── raw/
│   ├── with_metadata/
│   ├── filtered/
│   └── README.md
└── RDS/          # R objects (RDS format)
    └── README.md
```

---

**Note:** RDS files are generated from the filtered AnnData objects and contain all metadata from the original objects.
"""

    readme_file = rds_dir / "README.md"
    with open(readme_file, "w") as f:
        f.write(readme_content)

    print(f"✅ Created README: {readme_file}")
    print("\n🎉 RDS directory structure created successfully!")
    print("\nStructure:")
    print("data/RDS/")
    print("└── README.md")


def update_main_structure():
    """
    Update the main data structure to include RDS directory.
    """
    print("\n📝 Updating main data structure...")

    # Check if main README exists
    main_readme = Path("data/Anndata/README.md")
    if main_readme.exists():
        print(
            "ℹ️  Main Anndata README found - remember to update it to reference RDS directory"
        )
    else:
        print("⚠️  Main Anndata README not found")

    # Show the new overall structure
    print("\n📁 New overall data structure:")
    print("data/")
    print("├── Anndata/       # Python AnnData objects")
    print("│   ├── raw/")
    print("│   ├── with_metadata/")
    print("│   ├── filtered/")
    print("│   └── README.md")
    print("└── RDS/          # R objects (RDS format)")
    print("    └── README.md")


if __name__ == "__main__":
    create_rds_structure()
    update_main_structure()
