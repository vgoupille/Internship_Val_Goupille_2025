#!/usr/bin/env python3
"""
Test script to verify gene metadata in enriched AnnData objects.
"""

import anndata as ad
import pandas as pd
import os


def test_enriched_anndata_with_gene_metadata():
    """Test one enriched AnnData object with gene metadata."""

    # Load an enriched AnnData object
    anndata_file = "anndata_objects_with_gene_metadata/Gene_filtered.h5ad"

    print(f"Loading enriched AnnData object: {anndata_file}")
    adata = ad.read_h5ad(anndata_file)

    print(f"\n=== AnnData Object Information ===")
    print(f"Shape: {adata.shape}")
    print(f"Number of cells: {adata.n_obs}")
    print(f"Number of genes: {adata.n_vars}")

    print(f"\n=== Cell Metadata (obs) ===")
    print(f"Number of cell metadata columns: {len(adata.obs.columns)}")
    print(f"Cell metadata columns:")
    for i, col in enumerate(adata.obs.columns, 1):
        print(f"  {i:2d}. {col}")

    print(f"\n=== Gene Metadata (var) ===")
    print(f"Number of gene metadata columns: {len(adata.var.columns)}")
    print(f"Gene metadata columns:")
    for i, col in enumerate(adata.var.columns, 1):
        print(f"  {i:2d}. {col}")

    print(f"\n=== Sample of Gene Metadata ===")
    # Show first few genes with their metadata
    print("First 5 genes with metadata:")
    sample_genes = adata.var.head()
    print(sample_genes)

    print(f"\n=== Gene Metadata Statistics ===")
    # Show some statistics for key gene metadata columns
    if "Gene Type" in adata.var.columns:
        gene_types = adata.var["Gene Type"].value_counts()
        print(f"Gene types distribution (top 10):")
        print(gene_types.head(10))

    if "Chromosome" in adata.var.columns:
        chromosomes = adata.var["Chromosome"].value_counts()
        print(f"\nChromosome distribution:")
        print(chromosomes)

    if "Protein length" in adata.var.columns:
        protein_lengths = adata.var["Protein length"].dropna()
        print(f"\nProtein length statistics:")
        print(f"  Mean: {protein_lengths.mean():.1f}")
        print(f"  Median: {protein_lengths.median():.1f}")
        print(f"  Min: {protein_lengths.min()}")
        print(f"  Max: {protein_lengths.max()}")

    print(f"\n=== Unstructured Metadata (uns) ===")
    print("Keys in adata.uns:")
    for key in adata.uns.keys():
        print(f"  - {key}: {adata.uns[key]}")

    print(f"\n=== Verification ===")
    # Check if gene metadata was properly added
    expected_gene_columns = [
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
        "symbol_old",
        "locus_tag_old",
        "symbol_renamed",
        "final_gene_name",
    ]

    missing_columns = [
        col for col in expected_gene_columns if col not in adata.var.columns
    ]
    if missing_columns:
        print(f"Missing gene metadata columns: {missing_columns}")
    else:
        print("✓ All expected gene metadata columns are present")

    # Check if gene metadata enrichment info is in uns
    if "gene_metadata_added" in adata.uns:
        print("✓ Gene metadata enrichment info is present")
        print(f"  - Genes with metadata: {adata.uns.get('genes_with_metadata', 'N/A')}")
        print(f"  - Total genes: {adata.uns.get('total_genes', 'N/A')}")
    else:
        print("✗ Gene metadata enrichment info is missing")


if __name__ == "__main__":
    test_enriched_anndata_with_gene_metadata()
