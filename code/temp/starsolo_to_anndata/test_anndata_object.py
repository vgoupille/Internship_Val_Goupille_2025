#!/usr/bin/env python3
"""
Test AnnData object with cell metadata

This script loads and tests an enriched AnnData object to verify that all metadata
has been properly added and can be used for analysis.

Author: Valentin Goupille
Date: 2025-05-25
"""

import anndata as ad
import pandas as pd
import numpy as np
from pathlib import Path


def test_anndata_object(
    file_path: str = "anndata_objects_with_metadata/Gene_filtered.h5ad",
):
    """
    Test an AnnData object with cell metadata

    Args:
        file_path: Path to the AnnData file to test
    """
    print(f"=== Test de l'objet AnnData : {file_path} ===")
    print()

    # Check if file exists
    if not Path(file_path).exists():
        print(f"❌ Fichier non trouvé : {file_path}")
        return

    try:
        # Load AnnData object
        print("Chargement de l'objet AnnData...")
        adata = ad.read_h5ad(file_path)
        print(f"✓ Objet chargé avec succès")
        print()

        # Basic information
        print("=== INFORMATIONS DE BASE ===")
        print(f"Nombre de cellules : {adata.n_obs}")
        print(f"Nombre de gènes : {adata.n_vars}")
        print(f"Forme de la matrice : {adata.X.shape}")
        print()

        # Check obs columns
        print("=== COLONNES DES MÉTADONNÉES DES CELLULES (obs) ===")
        obs_columns = list(adata.obs.columns)
        print(f"Nombre de colonnes : {len(obs_columns)}")
        for i, col in enumerate(obs_columns, 1):
            print(f"  {i}. {col}")
        print()

        # Check var columns
        print("=== COLONNES DES MÉTADONNÉES DES GÈNES (var) ===")
        var_columns = list(adata.var.columns)
        print(f"Nombre de colonnes : {len(var_columns)}")
        for i, col in enumerate(var_columns, 1):
            print(f"  {i}. {col}")
        print()

        # Test metadata content
        print("=== CONTENU DES MÉTADONNÉES ===")

        # Well locations
        print("Puits (Well_loc) :")
        for round_name in ["rd1", "rd2", "rd3"]:
            col_name = f"Well_loc_{round_name}"
            if col_name in adata.obs.columns:
                unique_wells = adata.obs[col_name].dropna().unique()
                print(f"  {round_name}: {len(unique_wells)} puits uniques")
                print(f"    Exemples : {unique_wells[:5]}")
        print()

        # Experimental conditions
        print("Conditions expérimentales :")
        if "CultureMedium" in adata.obs.columns:
            mediums = adata.obs["CultureMedium"].dropna().unique()
            print(f"  Milieux de culture : {mediums}")
        if "Condition" in adata.obs.columns:
            conditions = adata.obs["Condition"].dropna().unique()
            print(f"  Conditions : {conditions}")
        if "ODt" in adata.obs.columns:
            od_values = adata.obs["ODt"].dropna().unique()
            print(f"  Points OD : {od_values}")
        print()

        # Replicates
        print("Réplicats :")
        if "RepBio" in adata.obs.columns:
            rep_bio = adata.obs["RepBio"].dropna().unique()
            print(f"  Réplicats biologiques : {rep_bio}")
        if "RepTech" in adata.obs.columns:
            rep_tech = adata.obs["RepTech"].dropna().unique()
            print(
                f"  Réplicats techniques : {len(rep_tech)} (premiers: {rep_tech[:3]})"
            )
        print()

        # Cell counts by condition
        print("=== COMPTAGE DES CELLULES PAR CONDITION ===")
        if "CultureMedium" in adata.obs.columns and "ODt" in adata.obs.columns:
            cell_counts = adata.obs.groupby(["CultureMedium", "ODt"]).size()
            print("Cellules par milieu de culture et point OD :")
            print(cell_counts)
        print()

        # Test data access
        print("=== TEST D'ACCÈS AUX DONNÉES ===")

        # Test subsetting by condition
        if "CultureMedium" in adata.obs.columns:
            m9_cells = adata[adata.obs["CultureMedium"] == "M9"]
            print(f"Cellules M9 : {m9_cells.n_obs}")

            m9f_cells = adata[adata.obs["CultureMedium"] == "M9F"]
            print(f"Cellules M9F : {m9f_cells.n_obs}")
        print()

        # Test gene metadata
        if len(adata.var.columns) > 0:
            print("Métadonnées des gènes disponibles :")
            for col in adata.var.columns:
                print(f"  - {col}")
        print()

        # Test uns metadata
        if len(adata.uns) > 0:
            print("Métadonnées globales (uns) :")
            for key in adata.uns.keys():
                print(f"  - {key}")
        print()

        # Summary statistics
        print("=== STATISTIQUES RÉSUMÉES ===")
        print(
            f"Cellules avec métadonnées complètes : {sum(~adata.obs['Well_loc_rd1'].isna())}"
        )
        print(f"Cellules sans métadonnées : {sum(adata.obs['Well_loc_rd1'].isna())}")

        if "CultureMedium" in adata.obs.columns:
            print("\nRépartition par milieu de culture :")
            print(adata.obs["CultureMedium"].value_counts())

        if "ODt" in adata.obs.columns:
            print("\nRépartition par point OD :")
            print(adata.obs["ODt"].value_counts())

        print()
        print("✅ Test terminé avec succès ! L'objet AnnData est prêt pour l'analyse.")

    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")
        import traceback

        traceback.print_exc()


def main():
    """
    Main function
    """
    # Test the filtered gene object
    test_file = "anndata_objects_with_metadata/Gene_filtered.h5ad"
    test_anndata_object(test_file)


if __name__ == "__main__":
    main()
