#!/usr/bin/env python3
"""
Add cell metadata to AnnData objects (version sans modification des colonnes)

Ce script ajoute les métadonnées des cellules aux objets AnnData en utilisant les colonnes déjà présentes dans le fichier metadata_DOL_rep1.xlsx.

Author: Valentin Goupille
Date: 2025-05-25
"""

import anndata as ad
import pandas as pd
import numpy as np
from pathlib import Path
import glob


def load_barqc_files(barqc_dir: str = "processed_barcodes/barqc"):
    """
    Load BarQC files for all three rounds

    Args:
        barqc_dir: Directory containing BarQC files

    Returns:
        Dictionary with DataFrames for each round
    """
    print(f"Chargement des fichiers BarQC depuis : {barqc_dir}")

    barqc_files = {
        "rd1": f"{barqc_dir}/barcode_rd1_barqc.csv",
        "rd2": f"{barqc_dir}/barcode_rd2_barqc.csv",
        "rd3": f"{barqc_dir}/barcode_rd3_barqc.csv",
    }

    barqc_data = {}

    for round_name, file_path in barqc_files.items():
        if Path(file_path).exists():
            df = pd.read_csv(file_path)
            barqc_data[round_name] = df
            print(f"✓ {round_name}: {len(df)} barcodes chargés")
        else:
            print(f"❌ Fichier non trouvé : {file_path}")
            return None

    return barqc_data


def load_metadata_file(metadata_file: str = "metadata_DOL_rep1.xlsx"):
    """
    Load the metadata file and apply the column fusion logic

    Args:
        metadata_file: Path to metadata Excel file

    Returns:
        DataFrame with processed metadata
    """
    print(f"Chargement du fichier de métadonnées : {metadata_file}")

    if not Path(metadata_file).exists():
        print(f"❌ Fichier de métadonnées non trouvé : {metadata_file}")
        return None

    # Load the original file
    df = pd.read_excel(metadata_file, sheet_name="Exp1")
    print(f"✓ Métadonnées chargées : {len(df)} lignes")

    # Remove Sample_ID if present
    if "Sample_ID" in df.columns:
        df = df.drop(columns=["Sample_ID"])

    return df


def extract_barcodes_from_cell_barcodes(cell_barcodes):
    """
    Extract individual round barcodes from combined cell barcodes

    Args:
        cell_barcodes: List of combined cell barcodes (rd3_rd2_rd1 format)

    Returns:
        Dictionary with barcodes for each round
    """
    print("Extraction des barcodes individuels depuis les barcodes de cellules...")

    rd1_barcodes = []
    rd2_barcodes = []
    rd3_barcodes = []

    for barcode in cell_barcodes:
        parts = barcode.split("_")
        if len(parts) >= 3:
            rd3_barcodes.append(parts[0])
            rd2_barcodes.append(parts[1])
            rd1_barcodes.append(parts[2])
        else:
            rd3_barcodes.append(np.nan)
            rd2_barcodes.append(np.nan)
            rd1_barcodes.append(np.nan)

    return {"rd1": rd1_barcodes, "rd2": rd2_barcodes, "rd3": rd3_barcodes}


def match_barcodes_and_add_wells(adata, barqc_data, extracted_barcodes):
    """
    Match barcodes and add well information to AnnData object

    Args:
        adata: AnnData object
        barqc_data: Dictionary with BarQC DataFrames
        extracted_barcodes: Dictionary with extracted barcodes for each round

    Returns:
        AnnData object with added metadata
    """
    print("Matching des barcodes et ajout des informations de puits...")

    # Add well information for each round
    for round_name in ["rd1", "rd2", "rd3"]:
        if round_name in barqc_data and round_name in extracted_barcodes:
            # Create mapping from barcode to well
            barcode_to_well = dict(
                zip(
                    barqc_data[round_name]["Barcode"],
                    barqc_data[round_name]["WellPosition"],
                )
            )

            # Match barcodes and get wells
            wells = []
            for barcode in extracted_barcodes[round_name]:
                if pd.isna(barcode):
                    wells.append(np.nan)
                else:
                    wells.append(barcode_to_well.get(barcode, np.nan))

            # Add to AnnData
            well_col_name = f"Well_loc_{round_name}"
            adata.obs[well_col_name] = wells

            # Count matches
            matches = sum(1 for well in wells if not pd.isna(well))
            print(f"✓ {round_name}: {matches}/{len(wells)} cellules matchées")

    return adata


def add_experimental_metadata(adata, metadata_df):
    """
    Add experimental metadata based on well locations

    Args:
        adata: AnnData object
        metadata_df: DataFrame with experimental metadata

    Returns:
        AnnData object with added experimental metadata
    """
    print("Ajout des métadonnées expérimentales...")

    # Utilise directement les colonnes du fichier
    well_to_metadata = {row["Well_loc_rd1"]: row for _, row in metadata_df.iterrows()}
    metadata_columns = [col for col in metadata_df.columns if col != "Well_loc_rd1"]
    for col in metadata_columns:
        adata.obs[col] = [
            well_to_metadata.get(well, {}).get(col, np.nan)
            for well in adata.obs["Well_loc_rd1"]
        ]
    cells_with_metadata = sum(
        1
        for well in adata.obs["Well_loc_rd1"]
        if not pd.isna(well) and well in well_to_metadata
    )
    print(
        f"✓ {cells_with_metadata}/{len(adata)} cellules avec métadonnées expérimentales"
    )
    return adata


def process_anndata_objects(
    anndata_dir: str = "anndata_objects",
    barqc_dir: str = "processed_barcodes/barqc",
    metadata_file: str = "metadata_DOL_rep1.xlsx",
    output_dir: str = "anndata_objects_with_metadata",
):
    """
    Process all AnnData objects and add cell metadata

    Args:
        anndata_dir: Directory containing AnnData objects
        barqc_dir: Directory containing BarQC files
        metadata_file: Path to metadata file
        output_dir: Directory to save enriched AnnData objects
    """
    print("=== Ajout des métadonnées des cellules aux objets AnnData ===")
    print()

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Load BarQC files
    barqc_data = load_barqc_files(barqc_dir)
    if barqc_data is None:
        print("❌ Impossible de charger les fichiers BarQC")
        return

    # Load and process metadata file
    metadata_df = load_metadata_file(metadata_file)
    if metadata_df is None:
        print("❌ Impossible de charger le fichier de métadonnées")
        return

    # Find AnnData files
    anndata_files = glob.glob(f"{anndata_dir}/*.h5ad")
    if not anndata_files:
        print(f"❌ Aucun fichier AnnData trouvé dans {anndata_dir}")
        return

    print(f"\nTraitement de {len(anndata_files)} objets AnnData...")

    for file_path in anndata_files:
        print(f"\n--- Traitement de {Path(file_path).name} ---")

        try:
            # Load AnnData object
            adata = ad.read_h5ad(file_path)
            print(f"✓ Objet chargé : {adata.n_obs} cellules, {adata.n_vars} gènes")

            # Extract barcodes from cell barcodes
            extracted_barcodes = extract_barcodes_from_cell_barcodes(adata.obs_names)

            # Match barcodes and add well information
            adata = match_barcodes_and_add_wells(adata, barqc_data, extracted_barcodes)

            # Add experimental metadata
            adata = add_experimental_metadata(adata, metadata_df)

            # Save enriched object
            output_file = Path(output_dir) / Path(file_path).name
            adata.write_h5ad(output_file)
            print(f"✓ Objet enrichi sauvegardé : {output_file}")

            # Display summary
            print(
                f"  - Cellules avec métadonnées : {sum(~adata.obs['Well_loc_rd1'].isna())}/{len(adata)}"
            )
            if "Condition" in adata.obs:
                print(f"  - Conditions uniques : {adata.obs['Condition'].unique()}")
            if "CultureMedium" in adata.obs:
                print(f"  - Milieux de culture : {adata.obs['CultureMedium'].unique()}")

        except Exception as e:
            print(f"❌ Erreur lors du traitement de {file_path}: {e}")

    print(f"\nTraitement terminé ! Objets enrichis sauvegardés dans : {output_dir}")


def main():
    """
    Main function
    """
    # Configuration
    anndata_dir = "anndata_objects"
    barqc_dir = "processed_barcodes/barqc"
    metadata_file = "metadata_DOL_rep1.xlsx"
    output_dir = "anndata_objects_with_metadata"

    process_anndata_objects(anndata_dir, barqc_dir, metadata_file, output_dir)


if __name__ == "__main__":
    main()
