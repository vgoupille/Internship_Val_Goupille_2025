#!/usr/bin/env python3
"""
Script to analyze statistics by RepTech, RepBio, CultureMedium, and ODt groups.
"""

import anndata as ad
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def analyze_by_groups():
    """Analyze statistics by different grouping variables."""

    # Load the enriched AnnData object
    anndata_file = "anndata_objects_with_gene_metadata/Gene_filtered.h5ad"

    print(f"Loading enriched AnnData object: {anndata_file}")
    adata = ad.read_h5ad(anndata_file)

    print(f"\n{'='*80}")
    print(f"ANALYSE PAR GROUPES - RepTech, RepBio, CultureMedium, ODt")
    print(f"{'='*80}")

    # Get cell metadata
    cell_metadata = adata.obs.copy()

    print(f"\n📊 INFORMATIONS GÉNÉRALES")
    print(f"  Nombre total de cellules: {len(cell_metadata)}")
    print(f"  Nombre total de gènes: {adata.n_vars}")

    # Analyze by RepTech
    print(f"\n{'='*50}")
    print(f"ANALYSE PAR RepTech")
    print(f"{'='*50}")

    if "RepTech" in cell_metadata.columns:
        rep_tech_counts = cell_metadata["RepTech"].value_counts()
        print(f"  Répartition par RepTech:")
        for rep_tech, count in rep_tech_counts.items():
            percentage = (count / len(cell_metadata)) * 100
            print(f"    {rep_tech}: {count} cellules ({percentage:.1f}%)")

        # Statistics by RepTech
        print(f"\n  Statistiques par RepTech:")
        for rep_tech in rep_tech_counts.index:
            subset = cell_metadata[cell_metadata["RepTech"] == rep_tech]
            print(f"\n    RepTech {rep_tech}:")
            print(f"      - Nombre de cellules: {len(subset)}")
            if "ODt" in subset.columns:
                odt_values = pd.to_numeric(subset["ODt"], errors="coerce").dropna()
                if len(odt_values) > 0:
                    print(f"      - ODt moyen: {odt_values.mean():.3f}")
                    print(f"      - ODt médian: {odt_values.median():.3f}")
                    print(f"      - ODt min: {odt_values.min()}")
                    print(f"      - ODt max: {odt_values.max()}")
    else:
        print(f"  ❌ Colonne 'RepTech' non trouvée")

    # Analyze by RepBio
    print(f"\n{'='*50}")
    print(f"ANALYSE PAR RepBio")
    print(f"{'='*50}")

    if "RepBio" in cell_metadata.columns:
        rep_bio_counts = cell_metadata["RepBio"].value_counts()
        print(f"  Répartition par RepBio:")
        for rep_bio, count in rep_bio_counts.items():
            percentage = (count / len(cell_metadata)) * 100
            print(f"    {rep_bio}: {count} cellules ({percentage:.1f}%)")

        # Statistics by RepBio
        print(f"\n  Statistiques par RepBio:")
        for rep_bio in rep_bio_counts.index:
            subset = cell_metadata[cell_metadata["RepBio"] == rep_bio]
            print(f"\n    RepBio {rep_bio}:")
            print(f"      - Nombre de cellules: {len(subset)}")
            if "ODt" in subset.columns:
                odt_values = pd.to_numeric(subset["ODt"], errors="coerce").dropna()
                if len(odt_values) > 0:
                    print(f"      - ODt moyen: {odt_values.mean():.3f}")
                    print(f"      - ODt médian: {odt_values.median():.3f}")
                    print(f"      - ODt min: {odt_values.min()}")
                    print(f"      - ODt max: {odt_values.max()}")
    else:
        print(f"  ❌ Colonne 'RepBio' non trouvée")

    # Analyze by CultureMedium
    print(f"\n{'='*50}")
    print(f"ANALYSE PAR CultureMedium")
    print(f"{'='*50}")

    if "CultureMedium" in cell_metadata.columns:
        culture_counts = cell_metadata["CultureMedium"].value_counts()
        print(f"  Répartition par CultureMedium:")
        for culture, count in culture_counts.items():
            percentage = (count / len(cell_metadata)) * 100
            print(f"    {culture}: {count} cellules ({percentage:.1f}%)")

        # Statistics by CultureMedium
        print(f"\n  Statistiques par CultureMedium:")
        for culture in culture_counts.index:
            subset = cell_metadata[cell_metadata["CultureMedium"] == culture]
            print(f"\n    CultureMedium {culture}:")
            print(f"      - Nombre de cellules: {len(subset)}")
            if "ODt" in subset.columns:
                odt_values = pd.to_numeric(subset["ODt"], errors="coerce").dropna()
                if len(odt_values) > 0:
                    print(f"      - ODt moyen: {odt_values.mean():.3f}")
                    print(f"      - ODt médian: {odt_values.median():.3f}")
                    print(f"      - ODt min: {odt_values.min()}")
                    print(f"      - ODt max: {odt_values.max()}")
    else:
        print(f"  ❌ Colonne 'CultureMedium' non trouvée")

    # Analyze by ODt
    print(f"\n{'='*50}")
    print(f"ANALYSE PAR ODt")
    print(f"{'='*50}")

    if "ODt" in cell_metadata.columns:
        odt_values = pd.to_numeric(cell_metadata["ODt"], errors="coerce").dropna()
        print(f"  Statistiques générales ODt:")
        print(f"    - Nombre de cellules avec ODt: {len(odt_values)}")
        print(f"    - ODt moyen: {odt_values.mean():.3f}")
        print(f"    - ODt médian: {odt_values.median():.3f}")
        print(f"    - ODt min: {odt_values.min()}")
        print(f"    - ODt max: {odt_values.max()}")
        print(f"    - Écart-type: {odt_values.std():.3f}")

        # ODt distribution
        print(f"\n  Distribution des valeurs ODt:")
        if len(odt_values) > 0:
            odt_bins = pd.cut(odt_values, bins=10)
            odt_distribution = odt_bins.value_counts().sort_index()
            for bin_range, count in odt_distribution.items():
                percentage = (count / len(odt_values)) * 100
                print(f"    {bin_range}: {count} cellules ({percentage:.1f}%)")
        else:
            print("    Aucune valeur ODt disponible.")
    else:
        print(f"  ❌ Colonne 'ODt' non trouvée")

    # Cross-analysis
    print(f"\n{'='*50}")
    print(f"ANALYSE CROISÉE")
    print(f"{'='*50}")

    if all(
        col in cell_metadata.columns
        for col in ["RepTech", "RepBio", "CultureMedium", "ODt"]
    ):
        print(f"  Tableau croisé RepTech x RepBio:")
        cross_table = pd.crosstab(cell_metadata["RepTech"], cell_metadata["RepBio"])
        print(cross_table)

        print(f"\n  Tableau croisé RepTech x CultureMedium:")
        cross_table2 = pd.crosstab(
            cell_metadata["RepTech"], cell_metadata["CultureMedium"]
        )
        print(cross_table2)

        print(f"\n  Tableau croisé RepBio x CultureMedium:")
        cross_table3 = pd.crosstab(
            cell_metadata["RepBio"], cell_metadata["CultureMedium"]
        )
        print(cross_table3)

    # Summary table
    print(f"\n{'='*50}")
    print(f"TABLEAU RÉSUMÉ")
    print(f"{'='*50}")

    summary_data = []
    for rep_tech in cell_metadata["RepTech"].unique():
        for rep_bio in cell_metadata["RepBio"].unique():
            for culture in cell_metadata["CultureMedium"].unique():
                subset = cell_metadata[
                    (cell_metadata["RepTech"] == rep_tech)
                    & (cell_metadata["RepBio"] == rep_bio)
                    & (cell_metadata["CultureMedium"] == culture)
                ]
                if len(subset) > 0:
                    odt_values = pd.to_numeric(subset["ODt"], errors="coerce").dropna()
                    summary_data.append(
                        {
                            "RepTech": rep_tech,
                            "RepBio": rep_bio,
                            "CultureMedium": culture,
                            "Cellules": len(subset),
                            "ODt_moyen": (
                                odt_values.mean() if len(odt_values) > 0 else np.nan
                            ),
                            "ODt_median": (
                                odt_values.median() if len(odt_values) > 0 else np.nan
                            ),
                        }
                    )

    summary_df = pd.DataFrame(summary_data)
    if not summary_df.empty:
        print(summary_df.to_string(index=False))

    print(f"\n{'='*80}")
    print(f"ANALYSE TERMINÉE")
    print(f"{'='*80}")


if __name__ == "__main__":
    analyze_by_groups()
