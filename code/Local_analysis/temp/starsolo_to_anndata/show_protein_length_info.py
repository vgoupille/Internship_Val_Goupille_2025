#!/usr/bin/env python3
"""
Script to show where protein length information is stored in the enriched AnnData objects.
"""

import anndata as ad
import pandas as pd


def show_protein_length_info():
    """Show where protein length information is stored."""

    # Load an enriched AnnData object
    anndata_file = "anndata_objects_with_gene_metadata/Gene_filtered.h5ad"

    print(f"Loading: {anndata_file}")
    adata = ad.read_h5ad(anndata_file)

    print(f"\n=== Où se trouve l'info 'Protein length' ? ===")
    print(f"Cette information est dans la table des gènes (adata.var)")
    print(f"Colonne: 'Protein length'")

    print(f"\n=== Vérification de la colonne ===")
    if "Protein length" in adata.var.columns:
        print("✓ La colonne 'Protein length' existe")
        print(f"  Type de données: {adata.var['Protein length'].dtype}")
        print(
            f"  Nombre de valeurs non-nulles: {adata.var['Protein length'].notna().sum()}"
        )
        print(f"  Nombre de valeurs nulles: {adata.var['Protein length'].isna().sum()}")

        # Show first few values
        print(f"\n=== Premières valeurs ===")
        protein_lengths = adata.var["Protein length"].dropna()
        print("Premières 10 valeurs de longueur de protéines:")
        for i, (gene, length) in enumerate(protein_lengths.head(10).items()):
            print(f"  {i+1:2d}. {gene}: {length} acides aminés")

    else:
        print("✗ La colonne 'Protein length' n'existe pas")
        print("Colonnes disponibles dans adata.var:")
        for col in adata.var.columns:
            print(f"  - {col}")

    print(f"\n=== Comment accéder à cette info ===")
    print("Dans Python, vous pouvez faire:")
    print("  adata.var['Protein length']  # Toutes les longueurs")
    print("  adata.var.loc['QLH64-00005', 'Protein length']  # Pour un gène spécifique")


if __name__ == "__main__":
    show_protein_length_info()
