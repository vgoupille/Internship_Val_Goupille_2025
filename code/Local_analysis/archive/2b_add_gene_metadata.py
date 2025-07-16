#!/usr/bin/env python3
"""
Script to add gene metadata from ncbi_dataset_with_id.tsv to all enriched AnnData objects.
Joins on Locus tag column and saves enriched objects in anndata_objects_with_gene_metadata/ folder.
"""

import pandas as pd
import anndata as ad
import os
from pathlib import Path


def add_gene_metadata_to_anndata(adata, ncbi_df):
    """
    Add gene metadata from NCBI dataset to AnnData object.

    Args:
        adata (anndata.AnnData): AnnData object to enrich
        ncbi_df (pandas.DataFrame): NCBI dataset with gene metadata

    Returns:
        anndata.AnnData: Enriched AnnData object
    """
    print(f"  Adding gene metadata...")

    # Create a copy of the AnnData object
    adata_enriched = adata.copy()

    # Get the gene names from AnnData (var_names)
    gene_names = adata_enriched.var_names.tolist()

    # Filter NCBI dataset to only include genes present in AnnData
    ncbi_filtered = ncbi_df[ncbi_df["Locus tag"].isin(gene_names)].copy()

    # Sort NCBI data to match the order of genes in AnnData
    ncbi_filtered = (
        ncbi_filtered.set_index("Locus tag").reindex(gene_names).reset_index()
    )

    # Add all NCBI columns to var (except Locus tag which is already the index)
    ncbi_columns_to_add = [col for col in ncbi_filtered.columns if col != "Locus tag"]

    for col in ncbi_columns_to_add:
        adata_enriched.var[col] = ncbi_filtered[col].values

    # Add metadata about the enrichment
    adata_enriched.uns["gene_metadata_added"] = True
    adata_enriched.uns["gene_metadata_source"] = "ncbi_dataset_with_id.tsv"
    adata_enriched.uns["genes_with_metadata"] = len(ncbi_filtered)
    adata_enriched.uns["total_genes"] = len(gene_names)

    print(f"    Added {len(ncbi_columns_to_add)} metadata columns")
    print(f"    Genes with metadata: {len(ncbi_filtered)}/{len(gene_names)}")

    return adata_enriched


def main():
    """Main function to add gene metadata to all enriched AnnData objects."""

    # Paths
    anndata_folder = "anndata_objects_with_metadata"  # Changed to use enriched objects
    ncbi_file = "data/ncbi_dataset_with_id.tsv"
    output_folder = "anndata_objects_with_gene_metadata"  # New output folder

    # Create output directory
    os.makedirs(output_folder, exist_ok=True)

    # Load NCBI dataset
    print(f"Loading NCBI dataset from {ncbi_file}...")
    ncbi_df = pd.read_csv(ncbi_file, sep="\t")
    print(f"  Loaded {len(ncbi_df)} gene entries with {len(ncbi_df.columns)} columns")
    print(f"  Columns: {list(ncbi_df.columns)}")

    # Get all AnnData files
    anndata_files = [f for f in os.listdir(anndata_folder) if f.endswith(".h5ad")]
    anndata_files.sort()

    print(f"\nFound {len(anndata_files)} enriched AnnData files to process:")
    for f in anndata_files:
        print(f"  - {f}")

    # Process each AnnData file
    for filename in anndata_files:
        print(f"\n--- Processing {filename} ---")

        try:
            # Load AnnData object
            input_path = os.path.join(anndata_folder, filename)
            adata = ad.read_h5ad(input_path)
            print(f"  Loaded AnnData: {adata.shape}")
            print(f"  Cell metadata columns: {len(adata.obs.columns)}")
            print(f"  Gene metadata columns: {len(adata.var.columns)}")

            # Add gene metadata
            adata_enriched = add_gene_metadata_to_anndata(adata, ncbi_df)

            # Save enriched AnnData
            output_path = os.path.join(output_folder, filename)
            adata_enriched.write(output_path)
            print(f"  Saved enriched AnnData to: {output_path}")

        except Exception as e:
            print(f"  Error processing {filename}: {str(e)}")

    print(f"\nEnrichment completed!")
    print(f"Enriched AnnData objects saved in: {output_folder}/")

    # Show summary of what was added
    print(f"\nMetadata columns added to all objects:")
    ncbi_columns = [col for col in ncbi_df.columns if col != "Locus tag"]
    for col in ncbi_columns:
        print(f"  - {col}")


if __name__ == "__main__":
    main()
