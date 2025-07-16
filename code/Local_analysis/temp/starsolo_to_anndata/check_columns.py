#!/usr/bin/env python3
"""
Script to check column names and first values in each column.
"""

import anndata as ad
import pandas as pd


def check_columns():
    """Check column names and first values."""

    # Load the enriched AnnData object
    anndata_file = "anndata_objects_with_gene_metadata/Gene_filtered.h5ad"

    print(f"Loading: {anndata_file}")
    adata = ad.read_h5ad(anndata_file)

    print(f"\n{'='*60}")
    print(f"VÉRIFICATION DES COLONNES")
    print(f"{'='*60}")

    # Check obs columns (cell metadata)
    print(f"\n📋 COLONNES DES CELLULES (obs):")
    print(f"Nombre de colonnes: {len(adata.obs.columns)}")
    print(f"Colonnes disponibles:")
    for i, col in enumerate(adata.obs.columns, 1):
        print(f"  {i:2d}. {col}")

    print(f"\n📊 PREMIÈRES VALEURS DE CHAQUE COLONNE:")
    for col in adata.obs.columns:
        first_value = adata.obs[col].iloc[0]
        print(f"  {col}: '{first_value}' (type: {type(first_value)})")

    # Check var columns (gene metadata)
    print(f"\n📋 COLONNES DES GÈNES (var):")
    print(f"Nombre de colonnes: {len(adata.var.columns)}")
    print(f"Colonnes disponibles:")
    for i, col in enumerate(adata.var.columns, 1):
        print(f"  {i:2d}. {col}")

    print(f"\n📊 PREMIÈRES VALEURS DE CHAQUE COLONNE:")
    for col in adata.var.columns:
        first_value = adata.var[col].iloc[0]
        print(f"  {col}: '{first_value}' (type: {type(first_value)})")

    # Check specific columns for OD values
    print(f"\n🔍 VÉRIFICATION SPÉCIFIQUE DES COLONNES OD:")
    od_columns = [col for col in adata.obs.columns if "OD" in col.upper()]
    print(f"Colonnes contenant 'OD': {od_columns}")

    for col in od_columns:
        print(f"\n  Colonne: {col}")
        print(f"    Type: {adata.obs[col].dtype}")
        print(f"    Première valeur: '{adata.obs[col].iloc[0]}'")
        print(
            f"    Valeurs uniques (premières 10): {list(adata.obs[col].unique()[:10])}"
        )
        print(f"    Nombre de valeurs non-nulles: {adata.obs[col].notna().sum()}")
        print(f"    Nombre de valeurs nulles: {adata.obs[col].isna().sum()}")


if __name__ == "__main__":
    check_columns()
