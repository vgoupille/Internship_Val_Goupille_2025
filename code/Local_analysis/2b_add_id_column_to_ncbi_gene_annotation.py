#!/usr/bin/env python3
"""
Optimized script to process ncbi_dataset.tsv with duplicate handling.
Removes redundant columns and keeps only useful ones.
"""

import pandas as pd
import os


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

    # Remove redundant columns
    columns_to_keep = [
        "Accession",
        "Begin",
        "End",
        "Chromosome",
        "Orientation",
        "Name",
        "Symbol",
        "Gene ID",
        "Gene Type",
        "Transcripts accession",
        "Transcript name",
        "Protein accession",
        "Protein name",
        "Protein length",
        "Locus tag",
        "symbol_old",
        "locus_tag_old",
        "symbol_renamed",
        "final_gene_name",
    ]

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
    print(f"\nColonnes conservées ({len(existing_columns)}):")
    for col in existing_columns:
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
