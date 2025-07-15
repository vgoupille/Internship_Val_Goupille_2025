#!/usr/bin/env python3
"""
Modify metadata Excel file with column fusion logic

This script applies the same logic as in the notebook to modify the metadata Excel file:
- Make Rep_bio unique by merging with Culture_medium
- Make OD_timepoint unique by merging with Rep_bio
- Make Rep_tech unique by merging with OD_timepoint

Author: Valentin Goupille
Date: 2025-05-25
"""

import pandas as pd
from pathlib import Path


def modify_metadata_xlsx(
    input_file: str = "metadata_DOL_rep1.xlsx",
    output_file: str = "metadata_DOL_rep1_modified.xlsx",
):
    """
    Modify the metadata Excel file with column fusion logic

    Args:
        input_file: Input Excel file path
        output_file: Output Excel file path
    """
    print(f"=== Modification du fichier Excel {input_file} ===")
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

        # Display original values
        print("\n=== VALEURS ORIGINALES ===")
        print("\nColonnes concernées :")
        if "Culture_medium" in df.columns:
            print(f"Culture_medium : {df['Culture_medium'].unique()}")
        if "Rep_bio" in df.columns:
            print(f"Rep_bio : {df['Rep_bio'].unique()}")
        if "OD_timepoint" in df.columns:
            print(f"OD_timepoint : {df['OD_timepoint'].unique()}")
        if "Rep_tech" in df.columns:
            print(f"Rep_tech : {df['Rep_tech'].unique()}")

        # Apply the same logic as in the notebook
        print("\n=== APPLICATION DE LA LOGIQUE DE FUSION ===")

        # Make Rep_bio unique by merging with Culture_medium
        if "Culture_medium" in df.columns and "Rep_bio" in df.columns:
            print("1. Fusion Rep_bio avec Culture_medium...")
            df["Rep_bio"] = (
                df["Culture_medium"].astype(str) + "_" + df["Rep_bio"].astype(str)
            )
            print(f"   Nouveaux Rep_bio : {df['Rep_bio'].unique()}")

        # Create ODt column (original OD_timepoint values)
        if "OD_timepoint" in df.columns:
            print("2. Création de la colonne ODt...")
            df["ODt"] = df["OD_timepoint"].astype(str)
            print(f"   ODt créé avec les valeurs : {df['ODt'].unique()}")

        # Make OD_timepoint unique by merging with Rep_bio
        if "Rep_bio" in df.columns and "OD_timepoint" in df.columns:
            print("3. Fusion OD_timepoint avec Rep_bio...")
            df["OD_timepoint"] = (
                df["Rep_bio"].astype(str) + "_" + df["OD_timepoint"].astype(str)
            )
            print(f"   Nouveaux OD_timepoint : {df['OD_timepoint'].unique()}")

        # Make Rep_tech unique by merging with OD_timepoint
        if "OD_timepoint" in df.columns and "Rep_tech" in df.columns:
            print("4. Fusion Rep_tech avec OD_timepoint...")
            df["Rep_tech"] = (
                df["OD_timepoint"].astype(str) + "_" + df["Rep_tech"].astype(str)
            )
            print(f"   Nouveaux Rep_tech : {df['Rep_tech'].unique()}")

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
            display_cols = [
                "Culture_medium",
                "Rep_bio",
                "ODt",
                "OD_timepoint",
                "Rep_tech",
            ]
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
    output_file = "metadata_DOL_rep1_modified.xlsx"

    modify_metadata_xlsx(input_file, output_file)


if __name__ == "__main__":
    main()
