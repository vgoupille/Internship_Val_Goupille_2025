#!/usr/bin/env python3
"""
Optimized script to process ncbi_dataset.tsv with duplicate handling.
Removes redundant columns and keeps only useful ones.
annotation file from:
https://www.ncbi.nlm.nih.gov/datasets/gene/GCA_030064105.1/

Author: Valentin Goupille  
Date: Bioinfo_internship_2025

=============================================================================
SCRIPT PURPOSE AND WORKFLOW EXPLANATION
=============================================================================

This script processes gene annotation data from NCBI to prepare it for
single-cell RNA sequencing analysis. Here's why this preprocessing is needed:

1. PROBLEM: Raw NCBI annotation files often contain:
   - Duplicate gene symbols (same gene name appearing multiple times)
   - Inconsistent naming conventions (underscores vs hyphens)
   - Many redundant columns that are not needed for downstream analysis
   - Missing or inconsistent gene identifiers

2. SOLUTION: This script:
   - Detects and resolves duplicate gene symbols by adding numeric suffixes
   - Standardizes locus tag formatting (replaces underscores with hyphens)
   - Creates a unified "final_gene_name" column for consistent gene identification
   - Removes unnecessary columns to optimize file size and processing speed
   - Maintains traceability by keeping original values in separate columns

3. WORKFLOW:
   Input: data/ncbi/ncbi_dataset.tsv (raw NCBI annotation file)
   ↓
   Process: Handle duplicates, standardize names, optimize columns
   ↓
   Output: data/ncbi/ncbi_dataset_with_id.tsv (clean, optimized annotation file)

4. KEY FEATURES:
   - Duplicate symbol resolution: geneA → geneA_1, geneA_2, etc.
   - Locus tag standardization: ABC_001 → ABC-001
   - Final gene name creation: uses Symbol if available, otherwise Locus tag
   - Column optimization: keeps only essential columns for downstream analysis
   - Comprehensive statistics and logging for quality control

5. USAGE IN BIOINFORMATICS PIPELINE:
   This processed annotation file is typically used for:
   - Single-cell RNA-seq gene annotation
   - Gene expression analysis
   - Functional annotation studies
   - Integration with other genomic datasets

=============================================================================
"""

import pandas as pd
import os

# =============================================================================
# USER CONFIGURATION: COLUMNS TO KEEP IN THE OUTPUT FILE
# =============================================================================
# You can modify this list to choose which columns to keep in the final output.
# The columns will appear in the output file in the order specified below.
# Note: 'symbol_old', 'locus_tag_old', 'symbol_renamed', and 'final_gene_name'
# are created by this script and will be added automatically.

COLUMNS_TO_KEEP = [
    # Core gene identification columns (created by this script)
    "Locus tag",  # Modified locus tag
    "final_gene_name",  # Primary gene identifier (Symbol or Locus tag)
    "symbol_renamed",  # Boolean: was the symbol renamed due to duplicates?
    # Gene information columns
    "Gene Type",  # Type of gene (protein-coding, etc.)
    "Name",  # Gene name/description
    "Protein accession",  # protein reference
    # Optional: Add any of these columns by uncommenting them:
    # "Accession",          # Gene accession number
    # "Begin",              # Start position on chromosome
    # "End",                # End position on chromosome
    # "Chromosome",         # Chromosome location
    # "Orientation",        # Strand orientation
    # "Symbol",             # Modified gene symbol
    # "Gene ID",            # NCBI Gene ID
    # "Transcripts accession",  # Transcript accession
    # "Transcript name",    # Transcript name
    # "Protein accession",  # Protein accession
    # "Protein length",     # Protein length in amino acids
    # "symbol_old",         # Original symbol before processing
    # "locus_tag_old",      # Original locus tag before processing
]

# =============================================================================


def handle_duplicate_symbols_optimized(df):
    """
    Handle duplicate symbols and create optimized columns.

    Args:
        df (pandas.DataFrame): Input dataframe

    Returns:
        pandas.DataFrame: Modified dataframe with only useful columns
    """
    # Create a copy of original symbols
    df["symbol_old"] = df["Symbol"].copy()

    # Create a copy of original locus_tag and modify it
    if "Locus tag" in df.columns:
        df["locus_tag_old"] = df["Locus tag"].copy()
        # Replace underscores with hyphens in locus_tag
        df["Locus tag"] = df["Locus tag"].str.replace("_", "-", regex=False)
        print("Modified locus_tag: replaced underscores with hyphens")
    else:
        print("Warning: Locus tag column not found in annotation file")

    # Find duplicates in symbol column
    symbol_counts = df["Symbol"].value_counts()
    duplicates = symbol_counts[symbol_counts > 1].index.tolist()

    print(f"Found {len(duplicates)} duplicate symbols")

    if len(duplicates) > 0:
        # Process each duplicate symbol
        for dup_symbol in duplicates:
            if pd.notna(dup_symbol) and dup_symbol != "":  # Skip empty symbols
                # Find rows with this duplicate symbol
                dup_indices = df[df["Symbol"] == dup_symbol].index

                # Rename symbols with suffixes (_1, _2, etc.)
                for i, idx in enumerate(dup_indices, 1):
                    df.loc[idx, "Symbol"] = f"{dup_symbol}_{i}"

                print(f"Renamed {len(dup_indices)} instances of '{dup_symbol}'")

    # Add column indicating if symbol was renamed
    df["symbol_renamed"] = df["Symbol"] != df["symbol_old"]

    # Create final_gene_name column: use symbol if exists and not empty, otherwise use locus_tag
    df["final_gene_name"] = df.apply(
        lambda row: (
            row["Symbol"]
            if pd.notna(row["Symbol"]) and row["Symbol"] != ""
            else row["Locus tag"]
        ),
        axis=1,
    )

    return df


def add_id_column_optimized(input_file, output_file):
    """
    Process TSV file with duplicate handling and optimized columns.

    Args:
        input_file (str): Path to input TSV file
        output_file (str): Path to output TSV file
    """
    # Read the TSV file
    print(f"Reading input file: {input_file}")
    df = pd.read_csv(input_file, sep="\t")

    # Check if required columns exist
    if "Locus tag" not in df.columns:
        print("Error: 'Locus tag' column not found in the file")
        return
    if "Symbol" not in df.columns:
        print("Warning: 'Symbol' column not found in the file")

    # Handle duplicates and create optimized columns
    print("Processing duplicate symbols and creating optimized columns...")
    df = handle_duplicate_symbols_optimized(df)

    # Use user-configured columns list
    columns_to_keep = COLUMNS_TO_KEEP.copy()

    # Always add the columns created by this script (if not already in the list)
    script_created_columns = [
        "symbol_old",
        "locus_tag_old",
        "symbol_renamed",
        "final_gene_name",
    ]
    for col in script_created_columns:
        if col not in columns_to_keep:
            columns_to_keep.append(col)

    # Keep only columns that exist in the dataframe
    existing_columns = [col for col in columns_to_keep if col in df.columns]
    df_optimized = df[existing_columns]

    print(f"\nStatistics:")
    print(f"  - Total entries: {len(df_optimized)}")
    print(f"  - Total symbols renamed: {df_optimized['symbol_renamed'].sum()}")

    # Check for duplicates in final_gene_name
    final_gene_name_counts = df_optimized["final_gene_name"].value_counts()
    final_duplicates = final_gene_name_counts[final_gene_name_counts > 1]
    print(f"  - Duplicates in final_gene_name: {len(final_duplicates)}")

    # Show column comparison
    print(f"\nColumns kept ({len(existing_columns)}):")
    for col in existing_columns:
        print(f"  - {col}")

    # Show missing columns if any
    missing_columns = [col for col in columns_to_keep if col not in df.columns]
    if missing_columns:
        print(
            f"\nColumns requested but not found in input file ({len(missing_columns)}):"
        )
        for col in missing_columns:
            print(f"  - {col}")

    # Save the optimized dataframe to output file
    print(f"\nSaving output file: {output_file}")
    df_optimized.to_csv(output_file, sep="\t", index=False)
    print("Done!")


def main():
    """Main function to run the optimized script."""
    # Define file paths
    input_file = "data/ncbi/ncbi_dataset.tsv"
    output_file = "data/ncbi/ncbi_dataset_with_id.tsv"

    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found!")
        return

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Process the file
    add_id_column_optimized(input_file, output_file)


if __name__ == "__main__":
    main()
