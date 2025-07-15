#!/usr/bin/env python3
"""
Script to examine the enriched AnnData object in detail.
"""

import anndata as ad
import pandas as pd
import numpy as np


def examine_enriched_object():
    """Examine the enriched AnnData object in detail."""

    # Load the enriched AnnData object
    anndata_file = "anndata_objects_with_gene_metadata/Gene_filtered.h5ad"

    print(f"Loading enriched AnnData object: {anndata_file}")
    adata = ad.read_h5ad(anndata_file)

    print(f"\n{'='*60}")
    print(f"EXAMEN DÉTAILLÉ DE L'OBJET ANNDATA ENRICHIE")
    print(f"{'='*60}")

    # Basic information
    print(f"\n📊 INFORMATIONS DE BASE")
    print(f"  Shape: {adata.shape}")
    print(f"  Nombre de cellules: {adata.n_obs}")
    print(f"  Nombre de gènes: {adata.n_vars}")
    print(f"  Type de matrice: {type(adata.X)}")
    print(f"  Type de données: {adata.X.dtype}")

    # Cell metadata (obs)
    print(f"\n🧬 MÉTADONNÉES DES CELLULES (obs)")
    print(f"  Nombre de colonnes: {len(adata.obs.columns)}")
    print(f"  Colonnes disponibles:")
    for i, col in enumerate(adata.obs.columns, 1):
        print(f"    {i:2d}. {col}")

    # Show sample of cell metadata
    print(f"\n  📋 Exemple de métadonnées des cellules (premières 5):")
    print(adata.obs.head())

    # Gene metadata (var)
    print(f"\n🧬 MÉTADONNÉES DES GÈNES (var)")
    print(f"  Nombre de colonnes: {len(adata.var.columns)}")
    print(f"  Colonnes disponibles:")
    for i, col in enumerate(adata.var.columns, 1):
        print(f"    {i:2d}. {col}")

    # Show sample of gene metadata
    print(f"\n  📋 Exemple de métadonnées des gènes (premières 5):")
    print(adata.var.head())

    # Unstructured metadata (uns)
    print(f"\n📋 MÉTADONNÉES NON STRUCTURÉES (uns)")
    print(f"  Nombre de clés: {len(adata.uns)}")
    print(f"  Clés disponibles:")
    for key, value in adata.uns.items():
        print(f"    - {key}: {value}")

    # Data layers
    print(f"\n📊 COUCHES DE DONNÉES (layers)")
    if adata.layers:
        print(f"  Nombre de couches: {len(adata.layers)}")
        for layer_name in adata.layers.keys():
            print(f"    - {layer_name}: {adata.layers[layer_name].shape}")
    else:
        print(f"  Aucune couche de données")

    # Sample of expression data
    print(f"\n📈 EXEMPLE DE DONNÉES D'EXPRESSION")
    print(f"  Forme de la matrice X: {adata.X.shape}")
    print(f"  Type de données: {adata.X.dtype}")
    print(f"  Valeurs non-nulles: {np.count_nonzero(adata.X)}")
    print(f"  Sparsité: {1 - np.count_nonzero(adata.X) / adata.X.size:.2%}")

    # Show a small sample of expression data
    print(f"\n  📋 Exemple de données d'expression (5x5):")
    sample_data = adata.X[:5, :5]
    print(sample_data)

    # Summary statistics
    print(f"\n📊 STATISTIQUES RÉSUMÉES")

    # Cell statistics
    print(f"\n  🧬 Statistiques des cellules:")
    if "OD" in adata.obs.columns:
        od_values = pd.to_numeric(adata.obs["OD"], errors="coerce")
        print(f"    - OD moyen: {od_values.mean():.3f}")
        print(f"    - OD médian: {od_values.median():.3f}")
        print(f"    - OD min: {od_values.min()}")
        print(f"    - OD max: {od_values.max()}")

    # Gene statistics
    print(f"\n  🧬 Statistiques des gènes:")
    if "Protein length" in adata.var.columns:
        protein_lengths = adata.var["Protein length"].dropna()
        print(f"    - Longueur protéine moyenne: {protein_lengths.mean():.1f}")
        print(f"    - Longueur protéine médiane: {protein_lengths.median():.1f}")

    if "Gene Type" in adata.var.columns:
        gene_types = adata.var["Gene Type"].value_counts()
        print(f"    - Types de gènes:")
        for gene_type, count in gene_types.head(5).items():
            print(f"      * {gene_type}: {count}")

    print(f"\n{'='*60}")
    print(f"EXAMEN TERMINÉ")
    print(f"{'='*60}")


if __name__ == "__main__":
    examine_enriched_object()
