#!/usr/bin/env python3
"""
Modify metadata Excel file with column fusion logic - Version 2

This script applies the same logic as in the notebook to modify the metadata Excel file:
- Rename columns to CultureMedium, RepBio, RepTech, OD
- Remove Sample_ID and OD_timepoint columns
- Make RepBio unique by merging with CultureMedium
- Make OD unique by merging with RepBio
- Make RepTech unique by merging with OD

Author: Valentin Goupille
Date: 2025-05-25
"""

import pandas as pd
from pathlib import Path


def modify_metadata_xlsx_v2(
    input_file: str = "metadata_DOL_rep1.xlsx",
    output_file: str = "metadata_DOL_rep1_modified_v2.xlsx",
):
    """
    Modify the metadata Excel file with column fusion logic

    Args:
        input_file: Input Excel file path
        output_file: Output Excel file path
    """
    print(f"=== Modification du fichier Excel {input_file} - Version 2 ===")
    print()

    # Check if input file exists
    if not Path(input_file).exists():
        print(f"❌ Erreur : Le fichier {input_file} n'existe pas")
        return

    print(f"✓ Fichier d'entrée trouvé : {input_file}")

    try:
        # Read the Excel file
        print("\nLecture du fichier Excel...")
        df = pd.read_excel(input_file, sheet_name="Exp1")

        print(f"✓ Fichier lu avec succès")
        print(f"  - Nombre de lignes : {len(df)}")
        print(f"  - Colonnes disponibles : {list(df.columns)}")

        # Rename columns
        print("\n=== RENOMMAGE DES COLONNES ===")
        column_mapping = {
            "Culture_medium": "CultureMedium",
            "Rep_bio": "RepBio",
            "Rep_tech": "RepTech",
            "OD_timepoint": "OD",
        }

        df = df.rename(columns=column_mapping)
        print("✓ Colonnes renommées")

        # Remove unwanted columns
        print("\n=== SUPPRESSION DES COLONNES NON DÉSIRÉES ===")
        columns_to_remove = ["Sample_ID"]
        for col in columns_to_remove:
            if col in df.columns:
                df = df.drop(columns=[col])
                print(f"✓ Colonne '{col}' supprimée")

        print(f"  - Colonnes après suppression : {list(df.columns)}")

        # Display original values
        print("\n=== VALEURS ORIGINALES ===")
        print("\nColonnes concernées :")
        if "CultureMedium" in df.columns:
            print(f"CultureMedium : {df['CultureMedium'].unique()}")
        if "RepBio" in df.columns:
            print(f"RepBio : {df['RepBio'].unique()}")
        if "OD" in df.columns:
            print(f"OD : {df['OD'].unique()}")
        if "RepTech" in df.columns:
            print(f"RepTech : {df['RepTech'].unique()}")

        # Apply the same logic as in the notebook
        print("\n=== APPLICATION DE LA LOGIQUE DE FUSION ===")

        # Make RepBio unique by merging with CultureMedium
        if "CultureMedium" in df.columns and "RepBio" in df.columns:
            print("1. Fusion RepBio avec CultureMedium...")
            df["RepBio"] = (
                df["CultureMedium"].astype(str) + "_" + df["RepBio"].astype(str)
            )
            print(f"   Nouveaux RepBio : {df['RepBio'].unique()}")

        # Create ODt column (original OD values)
        if "OD" in df.columns:
            print("2. Création de la colonne ODt...")
            df["ODt"] = df["OD"].astype(str)
            print(f"   ODt créé avec les valeurs : {df['ODt'].unique()}")

        # Make OD unique by merging with RepBio
        if "RepBio" in df.columns and "OD" in df.columns:
            print("3. Fusion OD avec RepBio...")
            df["OD"] = df["RepBio"].astype(str) + "_" + df["OD"].astype(str)
            print(f"   Nouveaux OD : {df['OD'].unique()}")

        # Make RepTech unique by merging with OD
        if "OD" in df.columns and "RepTech" in df.columns:
            print("4. Fusion RepTech avec OD...")
            df["RepTech"] = df["OD"].astype(str) + "_" + df["RepTech"].astype(str)
            print(f"   Nouveaux RepTech : {df['RepTech'].unique()}")

        # Save the modified file
        print(f"\nSauvegarde du fichier modifié : {output_file}")
        df.to_excel(output_file, index=False, sheet_name="Exp1")

        print("✓ Fichier modifié sauvegardé avec succès")

        # Display summary of changes
        print("\n=== RÉSUMÉ DES MODIFICATIONS ===")
        print(f"Fichier d'entrée : {input_file}")
        print(f"Fichier de sortie : {output_file}")
        print(f"Nombre de lignes : {len(df)}")
        print(f"Nombre de colonnes : {len(df.columns)}")

        print("\nColonnes finales :")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i}. {col}")

        print("\n=== EXEMPLES DE VALEURS FINALES ===")
        if len(df) > 0:
            print("\nPremières lignes :")
            display_cols = ["CultureMedium", "RepBio", "ODt", "OD", "RepTech"]
            available_cols = [col for col in display_cols if col in df.columns]
            if available_cols:
                print(df[available_cols].head().to_string())

        print("\nModification terminée avec succès ! 🎉")

    except Exception as e:
        print(f"\n❌ Erreur lors de la modification : {e}")
        print("Veuillez vérifier que le fichier Excel contient les bonnes colonnes")


def main():
    """
    Main function
    """
    # You can modify these file names if needed
    input_file = "metadata_DOL_rep1.xlsx"
    output_file = "metadata_DOL_rep1_modified_v2.xlsx"

    modify_metadata_xlsx_v2(input_file, output_file)


if __name__ == "__main__":
    main()
