#!/usr/bin/env python3
"""
Script to create the organized AnnData directory structure.

Author: Valentin Goupille
Date: 2025-01-13
"""

import os
from pathlib import Path


def create_anndata_structure():
    """
    Create the organized AnnData directory structure.
    """
    print("📁 Creating AnnData directory structure...")

    # Define the structure
    base_dir = Path("data/Anndata")
    directories = [
        base_dir / "raw",  # For raw AnnData objects from 2a
        base_dir / "with_metadata",  # For objects with metadata from 2c
        base_dir / "filtered",  # For filtered objects from 3a, 3b, 3c
    ]

    # Create directories
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}")

    # Create a README file explaining the structure
    readme_content = """# AnnData Organization Structure

This directory contains organized AnnData objects from the analysis pipeline:

## Directory Structure

- `raw/` - Raw AnnData objects created from STARsolo output (script 2a)
- `with_metadata/` - Objects enriched with cell and gene metadata (script 2c)
- `filtered/` - Filtered objects from various filtering steps (scripts 3a, 3b, 3c)

## Processing Pipeline

1. **2a_starsolo_to_anndata.py** → `raw/`
   - Converts STARsolo output to AnnData objects
   - Creates 6 different objects (Gene/GeneFull, raw/filtered, matrix types)

2. **2c_add_metadata_to_anndata.py** → `with_metadata/`
   - Adds cell metadata (experimental conditions, well positions)
   - Adds gene metadata (NCBI annotations)

3. **3a_filtering_100UMIs.py** → `filtered/`
   - Filters cells with <100 UMIs
   - Creates grouped variables

4. **3b_filtering_advanced_cell_v2.py** → `filtered/`
   - Advanced cell filtering with balanced subsampling
   - RepTech filtering and outlier removal

5. **3c_filtering_advanced_gene.py** → `filtered/`
   - Gene filtering (protein-coding, min cells per gene)
   - Gene annotation by group expression

## File Naming Convention

Files follow a descriptive naming pattern indicating their processing level:
- `*_raw_*` - Raw data
- `*_with_metadata` - With added metadata
- `*_filtered_*` - Various filtering levels applied
"""

    readme_file = base_dir / "README.md"
    with open(readme_file, "w") as f:
        f.write(readme_content)

    print(f"✅ Created README: {readme_file}")
    print("\n🎉 AnnData directory structure created successfully!")
    print("\nStructure:")
    print("data/Anndata/")
    print("├── raw/")
    print("├── with_metadata/")
    print("├── filtered/")
    print("└── README.md")


if __name__ == "__main__":
    create_anndata_structure()
