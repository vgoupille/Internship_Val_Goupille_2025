#!/usr/bin/env python3
"""
Script to convert STARsolo output to AnnData objects.
Creates 6 different AnnData objects for Gene/GeneFull, raw/filtered, and different matrix types.

Author: Valentin Goupille
Date: Bioinfo_internship_2025

Usage:
    Configure the input path in the main() function's CONFIGURATION section.
    Default input: data/STARsolo_result/merged_trimmed/merged/Output_DOL_microsplit_starsolo2/starsolo_output2/Solo.out

Output:
    6 AnnData objects saved as .h5ad files in data/anndata_objects/
"""

import pandas as pd
import numpy as np
import scipy.io
import anndata as ad
import os
from pathlib import Path


def load_and_modify_features(features_path):
    """
    Load features.tsv and modify column 2 in memory (not on disk).

    Args:
        features_path (str): Path to features.tsv file

    Returns:
        pandas.DataFrame: Modified features dataframe
    """
    # Load features file
    features_df = pd.read_csv(features_path, sep="\t", header=None)

    # Modify column 2 in memory: remove 'gene-' prefix and replace _ with -
    features_df[1] = features_df[0].str.replace("gene-", "").str.replace("_", "-")

    return features_df


def load_matrix_and_convert(matrix_path, matrix_type="integer"):
    """
    Load matrix and convert if needed.

    Args:
        matrix_path (str): Path to matrix file
        matrix_type (str): 'integer' or 'float' (for UniqueAndMult-Uniform)

    Returns:
        scipy.sparse.csr_matrix: Loaded matrix (transposed for AnnData format)
    """
    # Load matrix
    if matrix_type == "float":
        # For float matrices, read manually to handle the format
        print(f"  Reading float matrix manually...")
        with open(matrix_path, "r") as f:
            lines = f.readlines()

        # Skip header lines
        data_lines = [
            line for line in lines if not line.startswith("%") and line.strip()
        ]

        # Parse dimensions from the first data line
        dims = data_lines[0].strip().split()
        n_genes, n_cells, n_entries = int(dims[0]), int(dims[1]), int(dims[2])

        # Parse the data
        data = []
        row_indices = []
        col_indices = []

        for line in data_lines[1:]:
            parts = line.strip().split()
            if len(parts) == 3:
                gene_idx = int(parts[0]) - 1  # Convert to 0-based indexing
                cell_idx = int(parts[1]) - 1  # Convert to 0-based indexing
                value = float(parts[2])

                # Round float values to integers
                value = int(round(value))

                if value > 0:  # Only store non-zero values
                    data.append(value)
                    row_indices.append(gene_idx)
                    col_indices.append(cell_idx)

        # Create sparse matrix
        from scipy.sparse import csr_matrix

        matrix = csr_matrix(
            (data, (row_indices, col_indices)), shape=(n_genes, n_cells)
        )

    else:
        # For integer matrices, use scipy.io.mmread
        matrix = scipy.io.mmread(matrix_path)
        matrix = matrix.tocsr()

    # Transpose matrix for AnnData format (cells x genes)
    matrix = matrix.T

    return matrix


def create_anndata_object(
    matrix_path, barcodes_path, features_path, matrix_type="integer", name=""
):
    """
    Create AnnData object from STARsolo files.

    Args:
        matrix_path (str): Path to matrix file
        barcodes_path (str): Path to barcodes file
        features_path (str): Path to features file
        matrix_type (str): 'integer' or 'float'
        name (str): Name for the object

    Returns:
        anndata.AnnData: Created AnnData object
    """
    print(f"Creating {name}...")

    # Load and modify features
    features_df = load_and_modify_features(features_path)

    # Load barcodes
    barcodes_df = pd.read_csv(barcodes_path, sep="\t", header=None)

    # Load and convert matrix
    matrix = load_matrix_and_convert(matrix_path, matrix_type)

    # Create AnnData object
    adata = ad.AnnData(X=matrix, obs=barcodes_df, var=features_df)

    # Set column names
    adata.obs.columns = ["barcode"]
    adata.var.columns = ["feature_id", "gene_id", "feature_type"]

    # Set gene names as index
    adata.var_names = adata.var["gene_id"]
    adata.obs_names = adata.obs["barcode"]

    # Add metadata
    adata.uns["matrix_type"] = matrix_type
    adata.uns["source"] = "STARsolo"
    adata.uns["name"] = name

    print(f"  Shape: {adata.shape}")
    print(f"  Non-zero entries: {adata.X.nnz}")

    return adata


def main():
    """Main function to create all 6 AnnData objects."""

    # ================================
    # CONFIGURATION - MODIFY HERE
    # ================================
    # Input path to Solo.out directory
    solo_out_path = "data/STARsolo_result/merged_trimmed/merged/Output_DOL_microsplit_starsolo2/starsolo_output2/Solo.out"

    # Output directory for AnnData objects
    output_dir = "data/Anndata/raw"
    # ================================

    # Verify input directory exists
    if not os.path.exists(solo_out_path):
        print(f"Error: Input directory not found: {solo_out_path}")
        return

    print(f"Using input directory: {solo_out_path}")
    print(f"Output directory: {output_dir}")
    print("-" * 60)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Define the 6 objects to create
    objects_to_create = [
        {
            "name": "Gene_raw_matrix",
            "matrix_path": f"{solo_out_path}/Gene/raw/matrix.mtx",
            "barcodes_path": f"{solo_out_path}/Gene/raw/barcodes.tsv",
            "features_path": f"{solo_out_path}/Gene/raw/features.tsv",
            "matrix_type": "integer",
        },
        {
            "name": "Gene_raw_unique_mult",
            "matrix_path": f"{solo_out_path}/Gene/raw/UniqueAndMult-Uniform.mtx",
            "barcodes_path": f"{solo_out_path}/Gene/raw/barcodes.tsv",
            "features_path": f"{solo_out_path}/Gene/raw/features.tsv",
            "matrix_type": "float",
        },
        {
            "name": "Gene_filtered",
            "matrix_path": f"{solo_out_path}/Gene/filtered/matrix.mtx",
            "barcodes_path": f"{solo_out_path}/Gene/filtered/barcodes.tsv",
            "features_path": f"{solo_out_path}/Gene/filtered/features.tsv",
            "matrix_type": "integer",
        },
        {
            "name": "GeneFull_raw_matrix",
            "matrix_path": f"{solo_out_path}/GeneFull/raw/matrix.mtx",
            "barcodes_path": f"{solo_out_path}/GeneFull/raw/barcodes.tsv",
            "features_path": f"{solo_out_path}/GeneFull/raw/features.tsv",
            "matrix_type": "integer",
        },
        {
            "name": "GeneFull_raw_unique_mult",
            "matrix_path": f"{solo_out_path}/GeneFull/raw/UniqueAndMult-Uniform.mtx",
            "barcodes_path": f"{solo_out_path}/GeneFull/raw/barcodes.tsv",
            "features_path": f"{solo_out_path}/GeneFull/raw/features.tsv",
            "matrix_type": "float",
        },
        {
            "name": "GeneFull_filtered",
            "matrix_path": f"{solo_out_path}/GeneFull/filtered/matrix.mtx",
            "barcodes_path": f"{solo_out_path}/GeneFull/filtered/barcodes.tsv",
            "features_path": f"{solo_out_path}/GeneFull/filtered/features.tsv",
            "matrix_type": "integer",
        },
    ]

    # Create each AnnData object
    for obj_config in objects_to_create:
        try:
            # Check if files exist
            if not all(
                os.path.exists(obj_config[f"{key}_path"])
                for key in ["matrix", "barcodes", "features"]
            ):
                print(
                    f"Warning: Some files missing for {obj_config['name']}, skipping..."
                )
                continue

            # Create AnnData object
            adata = create_anndata_object(
                matrix_path=obj_config["matrix_path"],
                barcodes_path=obj_config["barcodes_path"],
                features_path=obj_config["features_path"],
                matrix_type=obj_config["matrix_type"],
                name=obj_config["name"],
            )

            # Save to file
            output_file = f"{output_dir}/{obj_config['name']}.h5ad"
            adata.write(output_file)
            print(f"  Saved to: {output_file}")
            print()

        except Exception as e:
            print(f"Error creating {obj_config['name']}: {str(e)}")
            print()

    print("Conversion completed!")
    print(f"AnnData objects saved in: {output_dir}/")


if __name__ == "__main__":
    main()
