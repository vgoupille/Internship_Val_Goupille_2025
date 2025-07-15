#!/usr/bin/env python3
"""
Script to calculate and display n_counts and n_features statistics by groups.
"""

import anndata as ad
import pandas as pd
import numpy as np
import scanpy as sc


def check_ncounts_nfeatures():
    """Calculate and display n_counts and n_features statistics."""

    # Load the enriched AnnData object
    anndata_file = "anndata_objects_with_gene_metadata/Gene_filtered.h5ad"

    print(f"Loading: {anndata_file}")
    adata = ad.read_h5ad(anndata_file)

    print(f"\n{'='*60}")
    print(f"STATISTIQUES N_COUNTS ET N_FEATURES")
    print(f"{'='*60}")

    # Calculate n_counts and n_features if not already present
    if "n_counts" not in adata.obs.columns:
        print("Calculating n_counts...")
        adata.obs["n_counts"] = np.sum(adata.X, axis=1)

    if "n_features" not in adata.obs.columns:
        print("Calculating n_features...")
        adata.obs["n_features"] = np.sum(adata.X > 0, axis=1)

    print(f"\n📊 STATISTIQUES GÉNÉRALES:")
    print(f"  n_counts - Moyenne: {adata.obs['n_counts'].mean():.1f}")
    print(f"  n_counts - Médiane: {adata.obs['n_counts'].median():.1f}")
    print(f"  n_counts - Min: {adata.obs['n_counts'].min()}")
    print(f"  n_counts - Max: {adata.obs['n_counts'].max()}")

    print(f"  n_features - Moyenne: {adata.obs['n_features'].mean():.1f}")
    print(f"  n_features - Médiane: {adata.obs['n_features'].median():.1f}")
    print(f"  n_features - Min: {adata.obs['n_features'].min()}")
    print(f"  n_features - Max: {adata.obs['n_features'].max()}")

    # Analyze by RepTech
    print(f"\n{'='*50}")
    print(f"ANALYSE PAR RepTech")
    print(f"{'='*50}")

    rep_tech_stats = (
        adata.obs.groupby("RepTech")
        .agg(
            {
                "n_counts": ["mean", "median", "min", "max", "count"],
                "n_features": ["mean", "median", "min", "max"],
            }
        )
        .round(1)
    )

    print("Statistiques par RepTech:")
    print(rep_tech_stats)

    # Analyze by RepBio
    print(f"\n{'='*50}")
    print(f"ANALYSE PAR RepBio")
    print(f"{'='*50}")

    rep_bio_stats = (
        adata.obs.groupby("RepBio")
        .agg(
            {
                "n_counts": ["mean", "median", "min", "max", "count"],
                "n_features": ["mean", "median", "min", "max"],
            }
        )
        .round(1)
    )

    print("Statistiques par RepBio:")
    print(rep_bio_stats)

    # Analyze by CultureMedium
    print(f"\n{'='*50}")
    print(f"ANALYSE PAR CultureMedium")
    print(f"{'='*50}")

    culture_stats = (
        adata.obs.groupby("CultureMedium")
        .agg(
            {
                "n_counts": ["mean", "median", "min", "max", "count"],
                "n_features": ["mean", "median", "min", "max"],
            }
        )
        .round(1)
    )

    print("Statistiques par CultureMedium:")
    print(culture_stats)

    # Analyze by ODt (categorical)
    print(f"\n{'='*50}")
    print(f"ANALYSE PAR ODt")
    print(f"{'='*50}")

    odt_stats = (
        adata.obs.groupby("ODt")
        .agg(
            {
                "n_counts": ["mean", "median", "min", "max", "count"],
                "n_features": ["mean", "median", "min", "max"],
            }
        )
        .round(1)
    )

    print("Statistiques par ODt:")
    print(odt_stats)

    # Show top and bottom cells by n_counts
    print(f"\n{'='*50}")
    print(f"CELLULES AVEC LE PLUS/MOINS DE COUNTS")
    print(f"{'='*50}")

    print("Top 10 cellules par n_counts:")
    top_counts = adata.obs.nlargest(10, "n_counts")[
        ["n_counts", "n_features", "RepTech", "RepBio", "CultureMedium", "ODt"]
    ]
    print(top_counts)

    print("\nBottom 10 cellules par n_counts:")
    bottom_counts = adata.obs.nsmallest(10, "n_counts")[
        ["n_counts", "n_features", "RepTech", "RepBio", "CultureMedium", "ODt"]
    ]
    print(bottom_counts)

    # Show top and bottom cells by n_features
    print(f"\n{'='*50}")
    print(f"CELLULES AVEC LE PLUS/MOINS DE FEATURES")
    print(f"{'='*50}")

    print("Top 10 cellules par n_features:")
    top_features = adata.obs.nlargest(10, "n_features")[
        ["n_counts", "n_features", "RepTech", "RepBio", "CultureMedium", "ODt"]
    ]
    print(top_features)

    print("\nBottom 10 cellules par n_features:")
    bottom_features = adata.obs.nsmallest(10, "n_features")[
        ["n_counts", "n_features", "RepTech", "RepBio", "CultureMedium", "ODt"]
    ]
    print(bottom_features)

    # Distribution analysis
    print(f"\n{'='*50}")
    print(f"DISTRIBUTION DES VALEURS")
    print(f"{'='*50}")

    print("Distribution n_counts (percentiles):")
    percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    for p in percentiles:
        value = np.percentile(adata.obs["n_counts"], p)
        print(f"  {p}%: {value:.0f}")

    print("\nDistribution n_features (percentiles):")
    for p in percentiles:
        value = np.percentile(adata.obs["n_features"], p)
        print(f"  {p}%: {value:.0f}")


if __name__ == "__main__":
    check_ncounts_nfeatures()
