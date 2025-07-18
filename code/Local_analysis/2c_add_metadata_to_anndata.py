#!/usr/bin/env python3
"""
Add cell and gene metadata to AnnData objects.

Author: Valentin Goupille
Date: 2025-07-16
"""

import anndata as ad
import pandas as pd
import numpy as np
from pathlib import Path
import glob
import os


def load_barqc_files(barqc_dir: str = "data/barcodes_result/barqc"):
    """
    Load BarQC files for all three rounds

    Args:
        barqc_dir: Directory containing BarQC files

    Returns:
        Dictionary with DataFrames for each round
    """
    print(f"Loading BarQC files from: {barqc_dir}")

    barqc_files = {
        "rd1": f"{barqc_dir}/barcode_rd1_barqc.csv",
        "rd2": f"{barqc_dir}/barcode_rd2_barqc.csv",
        "rd3": f"{barqc_dir}/barcode_rd3_barqc.csv",
    }

    barqc_data = {}

    for round_name, file_path in barqc_files.items():
        if Path(file_path).exists():
            df = pd.read_csv(file_path)
            barqc_data[round_name] = df
            print(f"✓ {round_name}: {len(df)} barcodes loaded")
        else:
            print(f"❌ File not found: {file_path}")
            return None

    return barqc_data


def load_metadata_file(
    metadata_file: str = "data/barcodes_result/metadata_DOL_Exp1_complete.xlsx",
):
    """
    Load the metadata file and apply the column fusion logic

    Args:
        metadata_file: Path to metadata Excel file

    Returns:
        DataFrame with processed metadata
    """
    print(f"Loading metadata file: {metadata_file}")

    if not Path(metadata_file).exists():
        print(f"❌ Metadata file not found: {metadata_file}")
        return None

    # Load the original file - try without sheet_name first, then with "Exp1" if it fails
    try:
        df = pd.read_excel(metadata_file)
    except:
        try:
            df = pd.read_excel(metadata_file, sheet_name="Exp1")
        except:
            print(f"❌ Cannot load metadata file: {metadata_file}")
            return None

    print(f"✓ Metadata loaded: {len(df)} rows")

    # Remove Sample_ID if present
    if "Sample_ID" in df.columns:
        df = df.drop(columns=["Sample_ID"])

    return df


def extract_barcodes_from_cell_barcodes(cell_barcodes):
    """
    Extract individual round barcodes from combined cell barcodes

    Args:
        cell_barcodes: List of combined cell barcodes (rd3_rd2_rd1 format)

    Returns:
        Dictionary with barcodes for each round
    """
    print("Extracting individual barcodes from cell barcodes...")

    rd1_barcodes = []
    rd2_barcodes = []
    rd3_barcodes = []

    for barcode in cell_barcodes:
        parts = barcode.split("_")
        if len(parts) >= 3:
            rd3_barcodes.append(parts[0])
            rd2_barcodes.append(parts[1])
            rd1_barcodes.append(parts[2])
        else:
            rd3_barcodes.append(np.nan)
            rd2_barcodes.append(np.nan)
            rd1_barcodes.append(np.nan)

    return {"rd1": rd1_barcodes, "rd2": rd2_barcodes, "rd3": rd3_barcodes}


def match_barcodes_and_add_wells(adata, barqc_data, extracted_barcodes):
    """
    Match barcodes and add well information to AnnData object

    Args:
        adata: AnnData object
        barqc_data: Dictionary with BarQC DataFrames
        extracted_barcodes: Dictionary with extracted barcodes for each round

    Returns:
        AnnData object with added metadata
    """
    print("Matching barcodes and adding well information...")

    # Add well information for each round
    for round_name in ["rd1", "rd2", "rd3"]:
        if round_name in barqc_data and round_name in extracted_barcodes:
            # Create mapping from barcode to well
            barcode_to_well = dict(
                zip(
                    barqc_data[round_name]["Barcode"],
                    barqc_data[round_name]["WellPosition"],
                )
            )

            # Match barcodes and get wells
            wells = []
            for barcode in extracted_barcodes[round_name]:
                if pd.isna(barcode):
                    wells.append(np.nan)
                else:
                    wells.append(barcode_to_well.get(barcode, np.nan))

            # Add to AnnData
            well_col_name = f"Well_loc_{round_name}"
            adata.obs[well_col_name] = wells

            # Count matches
            matches = sum(1 for well in wells if not pd.isna(well))
            print(f"✓ {round_name}: {matches}/{len(wells)} cells matched")

    return adata


def add_experimental_metadata(adata, metadata_df):
    """
    Add experimental metadata based on well locations

    Args:
        adata: AnnData object
        metadata_df: DataFrame with experimental metadata

    Returns:
        AnnData object with added experimental metadata
    """
    print("Adding experimental metadata...")

    # Use file columns directly
    well_to_metadata = {row["Well_loc_rd1"]: row for _, row in metadata_df.iterrows()}
    metadata_columns = [col for col in metadata_df.columns if col != "Well_loc_rd1"]
    for col in metadata_columns:
        adata.obs[col] = [
            well_to_metadata.get(well, {}).get(col, np.nan)
            for well in adata.obs["Well_loc_rd1"]
        ]
    cells_with_metadata = sum(
        1
        for well in adata.obs["Well_loc_rd1"]
        if not pd.isna(well) and well in well_to_metadata
    )
    print(f"✓ {cells_with_metadata}/{len(adata)} cells with experimental metadata")
    return adata


def add_gene_metadata_to_anndata(adata, ncbi_df):
    """
    Add gene metadata from NCBI dataset to AnnData object.

    Args:
        adata (anndata.AnnData): AnnData object to enrich
        ncbi_df (pandas.DataFrame): NCBI dataset with gene metadata

    Returns:
        anndata.AnnData: Enriched AnnData object
    """
    print(f"Adding gene metadata...")

    # Get the gene names from AnnData (var_names)
    gene_names = adata.var_names.tolist()

    # Filter NCBI dataset to only include genes present in AnnData
    ncbi_filtered = ncbi_df[ncbi_df["Locus tag"].isin(gene_names)].copy()

    # Sort NCBI data to match the order of genes in AnnData
    ncbi_filtered = (
        ncbi_filtered.set_index("Locus tag").reindex(gene_names).reset_index()
    )

    # Add all NCBI columns to var (except Locus tag which is already the index)
    ncbi_columns_to_add = [col for col in ncbi_filtered.columns if col != "Locus tag"]

    for col in ncbi_columns_to_add:
        adata.var[col] = ncbi_filtered[col].values

    # Remove redundant columns
    columns_to_remove = ["feature_id", "feature_type"]
    for col in columns_to_remove:
        if col in adata.var.columns:
            adata.var = adata.var.drop(columns=[col])
            print(f"✓ Removed redundant column: {col}")

    # Add metadata about the enrichment
    adata.uns["gene_metadata_added"] = True
    adata.uns["gene_metadata_source"] = "ncbi_dataset_with_id.tsv"
    adata.uns["genes_with_metadata"] = len(ncbi_filtered)
    adata.uns["total_genes"] = len(gene_names)

    print(f"✓ {len(ncbi_columns_to_add)} metadata columns added")
    print(f"✓ Genes with metadata: {len(ncbi_filtered)}/{len(gene_names)}")

    # Use final_gene_name as new reference column (index)
    if "final_gene_name" in adata.var.columns:
        print("✓ Setting final_gene_name as new gene index...")
        adata.var.index = adata.var["final_gene_name"]
        adata.var.index.name = "gene_name"  # Set a descriptive name for the new index

        # Check for duplicate gene names
        duplicates = adata.var.index.duplicated()
        if duplicates.any():
            print(f"⚠️  Warning: Found {duplicates.sum()} duplicate gene names")
        else:
            print("✓ No duplicate gene names found")
    else:
        print("⚠️  Warning: final_gene_name column not found, keeping original index")

    return adata


def check_columns_after_metadata_addition(adata, filename):
    """
    Check and display detailed information about columns after metadata addition

    Args:
        adata: AnnData object with metadata
        filename: Name of the file being processed
    """
    print(f"\n=== DETAILED COLUMN CHECK FOR {filename} ===")

    # Cell metadata (obs) check
    print("\n🔍 CELL METADATA (obs) COLUMNS:")
    print(f"Total columns: {len(adata.obs.columns)}")
    print("-" * 60)

    for i, col in enumerate(adata.obs.columns, 1):
        dtype = str(adata.obs[col].dtype)
        n_missing = adata.obs[col].isna().sum()
        n_unique = adata.obs[col].nunique()

        print(
            f"{i:2d}. {col:<25} | Type: {dtype:<10} | Missing: {n_missing:>4} | Unique: {n_unique:>4}"
        )

        # Show some example values for categorical columns
        if dtype == "object" and n_unique < 20:
            unique_vals = adata.obs[col].dropna().unique()
            if len(unique_vals) > 0:
                vals_str = ", ".join(str(v) for v in unique_vals[:5])
                if len(unique_vals) > 5:
                    vals_str += f" ... (+{len(unique_vals)-5} more)"
                print(f"     Values: {vals_str}")

    # Gene metadata (var) check
    print(f"\n🔍 GENE METADATA (var) COLUMNS:")
    print(f"Total columns: {len(adata.var.columns)}")
    print("-" * 60)

    for i, col in enumerate(adata.var.columns, 1):
        dtype = str(adata.var[col].dtype)
        n_missing = adata.var[col].isna().sum()
        n_unique = adata.var[col].nunique()

        print(
            f"{i:2d}. {col:<25} | Type: {dtype:<10} | Missing: {n_missing:>4} | Unique: {n_unique:>4}"
        )

        # Show some example values for categorical columns
        if dtype == "object" and n_unique < 20 and n_unique > 1:
            unique_vals = adata.var[col].dropna().unique()
            if len(unique_vals) > 0:
                vals_str = ", ".join(str(v) for v in unique_vals[:5])
                if len(unique_vals) > 5:
                    vals_str += f" ... (+{len(unique_vals)-5} more)"
                print(f"     Values: {vals_str}")

    # Additional information
    print(f"\n📊 ADDITIONAL INFORMATION:")
    print(f"- Total cells: {adata.n_obs}")
    print(f"- Total genes: {adata.n_vars}")

    # Check for metadata-related columns
    well_columns = [col for col in adata.obs.columns if col.startswith("Well_loc_")]
    if well_columns:
        print(f"- Well location columns: {len(well_columns)}")
        for col in well_columns:
            n_filled = (~adata.obs[col].isna()).sum()
            print(f"  * {col}: {n_filled}/{adata.n_obs} cells with well info")

    # Check for key experimental columns
    key_columns = ["Condition", "CultureMedium", "Strain", "Treatment"]
    present_key_cols = [col for col in key_columns if col in adata.obs.columns]
    if present_key_cols:
        print(f"- Key experimental columns present: {present_key_cols}")
        for col in present_key_cols:
            n_filled = (~adata.obs[col].isna()).sum()
            unique_vals = adata.obs[col].dropna().unique()
            print(
                f"  * {col}: {n_filled}/{adata.n_obs} cells, {len(unique_vals)} unique values"
            )

    # Check uns for metadata info
    if "gene_metadata_added" in adata.uns:
        print(
            f"- Gene metadata source: {adata.uns.get('gene_metadata_source', 'Unknown')}"
        )
        print(
            f"- Genes with metadata: {adata.uns.get('genes_with_metadata', 'Unknown')}/{adata.uns.get('total_genes', 'Unknown')}"
        )

    print("=" * 60)


def process_anndata_objects(
    anndata_dir: str = "data/Anndata/raw",
    barqc_dir: str = "data/barcodes_result/barqc",
    metadata_file: str = "data/barcodes_result/metadata_DOL_Exp1_complete.xlsx",
    ncbi_file: str = "data/ncbi/ncbi_dataset_with_id.tsv",
    output_dir: str = "data/Anndata/with_metadata",
):
    """
    Process all AnnData objects and add both cell and gene metadata

    Args:
        anndata_dir: Directory containing AnnData objects
        barqc_dir: Directory containing BarQC files
        metadata_file: Path to metadata file
        ncbi_file: Path to NCBI dataset file
        output_dir: Directory to save enriched AnnData objects
    """
    print("=== Adding complete metadata to AnnData objects ===")
    print()

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Load BarQC files
    barqc_data = load_barqc_files(barqc_dir)
    if barqc_data is None:
        print("❌ Unable to load BarQC files")
        return

    # Load and process metadata file
    metadata_df = load_metadata_file(metadata_file)
    if metadata_df is None:
        print("❌ Unable to load metadata file")
        return

    # Load NCBI dataset
    print(f"Loading NCBI dataset from {ncbi_file}...")
    if not Path(ncbi_file).exists():
        print(f"❌ NCBI file not found: {ncbi_file}")
        return

    ncbi_df = pd.read_csv(ncbi_file, sep="\t")
    print(f"✓ {len(ncbi_df)} gene entries loaded with {len(ncbi_df.columns)} columns")
    print(f"✓ Columns: {list(ncbi_df.columns)}")

    # Find AnnData files
    anndata_files = glob.glob(f"{anndata_dir}/*.h5ad")
    if not anndata_files:
        print(f"❌ No AnnData files found in {anndata_dir}")
        return

    print(f"\nProcessing {len(anndata_files)} AnnData objects...")

    for file_path in anndata_files:
        print(f"\n--- Processing {Path(file_path).name} ---")

        try:
            # Load AnnData object
            adata = ad.read_h5ad(file_path)
            print(f"✓ Object loaded: {adata.n_obs} cells, {adata.n_vars} genes")

            # STEP 1: Add cell metadata
            print("\n1. Adding cell metadata...")

            # Extract barcodes from cell barcodes
            extracted_barcodes = extract_barcodes_from_cell_barcodes(adata.obs_names)

            # Match barcodes and add well information
            adata = match_barcodes_and_add_wells(adata, barqc_data, extracted_barcodes)

            # Add experimental metadata
            adata = add_experimental_metadata(adata, metadata_df)

            # STEP 2: Add gene metadata
            print("\n2. Adding gene metadata...")
            adata = add_gene_metadata_to_anndata(adata, ncbi_df)

            # STEP 3: Check columns after metadata addition
            input_filename = Path(file_path).stem
            output_filename = f"{input_filename}_with_metadata.h5ad"
            check_columns_after_metadata_addition(adata, output_filename)

            # Save completely enriched object with metadata suffix
            output_file = Path(output_dir) / output_filename
            adata.write_h5ad(output_file)
            print(f"\n✅ Completely enriched object saved: {output_file}")

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")

    print(f"\n=== Processing completed ===")
    print(f"Completely enriched objects saved in: {output_dir}")
    print(f"Each object now contains:")
    print(f"  - Cell metadata (experimental information)")
    print(f"  - Gene metadata (NCBI annotations)")


def main():
    """
    Main function
    """
    # Configuration
    anndata_dir = "data/Anndata/raw"
    barqc_dir = "data/barcodes_result/barqc"
    metadata_file = "data/barcodes_result/metadata_DOL_Exp1_complete.xlsx"
    ncbi_file = "data/ncbi/ncbi_dataset_with_id.tsv"
    output_dir = "data/Anndata/with_metadata"

    process_anndata_objects(
        anndata_dir, barqc_dir, metadata_file, ncbi_file, output_dir
    )


if __name__ == "__main__":
    main()
