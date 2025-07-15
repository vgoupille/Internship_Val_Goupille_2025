#!/usr/bin/env python3
"""
Barcode Processing for microSPLiT Protocol

This script provides modular functions for processing barcodes from the microSPLiT protocol, including:

Main Features:
- Extraction and filtering of barcodes for each round (rd1, rd2, rd3)
- Creation of BarQC files for quality control
- Generation of barcode combinations (filtered and non-filtered)
- Metadata integration with experimental conditions
- Flexible output directory configuration

Author: Valentin Goupille
Date: 2025-05-25
"""

import pandas as pd
import os
from itertools import product
from typing import List, Dict, Tuple
from pathlib import Path
import re


class OutputConfig:
    """
    Configuration class for output paths
    """

    def __init__(self, base_output_dir: str = "data/processed_data/metadata_DOL_Exp1"):
        """
        Initialize output configuration

        Args:
            base_output_dir: Base directory for all output files
        """
        self.base_dir = Path(base_output_dir)
        self.directories = {
            "starsolo_filtered": self.base_dir / "barcodeSTARsolo/filtered",
            "starsolo_non_filtered": self.base_dir / "barcodeSTARsolo/non_filtered",
            "barqc": self.base_dir / "barqc",
            "metadata": self.base_dir,
            "combinations": self.base_dir / "combinations",
            "extracted_barcodes": self.base_dir / "extracted_barcodes",
        }

    def get_path(self, category: str, filename: str) -> Path:
        """
        Get full path for a file

        Args:
            category: Directory category (e.g., 'extracted_xlsx', 'barqc')
            filename: Name of the file

        Returns:
            Full path to the file
        """
        return self.directories[category] / filename

    def setup_directories(self) -> None:
        """
        Create all necessary directories
        """
        for directory in self.directories.values():
            directory.mkdir(parents=True, exist_ok=True)

    def save_file(
        self,
        df: pd.DataFrame,
        category: str,
        filename: str,
        format: str = "txt",
        include_header: bool = True,
    ) -> None:
        """
        Save DataFrame to file in specified format

        Args:
            df: DataFrame to save
            category: Directory category
            filename: Name of the file
            format: File format ('txt' or 'xlsx')
            include_header: Whether to include column headers (for CSV files)
        """
        output_path = self.get_path(category, filename)
        if format == "txt":
            # Pour les fichiers starsolo, ne jamais inclure d'en-tête
            if category in ["starsolo_filtered", "starsolo_non_filtered"]:
                df.to_csv(output_path, index=False, header=False)
            else:
                df.to_csv(output_path, index=False, header=include_header)
        else:
            df.to_excel(output_path, index=False)


def set_output_directory(base_dir: str) -> OutputConfig:
    """
    Set a new output directory for all files

    Args:
        base_dir: New base directory path

    Returns:
        Updated OutputConfig instance
    """
    global output_config
    output_config = OutputConfig(base_dir)
    output_config.setup_directories()
    return output_config


def find_project_root():
    """
    Trouve le répertoire racine du projet en cherchant le dossier 'data'
    """
    current_dir = Path.cwd()
    while current_dir != current_dir.parent:
        if (current_dir / "data").exists():
            return current_dir
        current_dir = current_dir.parent
    raise FileNotFoundError(
        "Impossible de trouver le répertoire racine du projet.\n"
        "Assurez-vous d'être dans un sous-répertoire du projet."
    )


class PathConfig:
    """
    Configuration class for input and output paths
    """

    def __init__(
        self,
        base_dir: str = None,
        input_file: str = "data/raw_data/metadata_cell/metadata_DOL_rep1.xlsx",
        project_root: Path = None,
    ):
        """
        Initialize path configuration

        Args:
            base_dir: Base directory for output files (if None, uses DEFAULT_OUTPUT_DIR)
            input_file: Path to input Excel file
            project_root: Path to project root directory
        """
        # Set project root directory
        if project_root is None:
            self.project_root = find_project_root()
        else:
            self.project_root = project_root
        print(f"Répertoire racine du projet : {self.project_root}")

        # Set input file path relative to project root
        self.input_file = self.project_root / input_file

        # Set output directory
        if base_dir is None:
            self.base_dir = self.project_root / "data/processed_data/metadata_DOL_Exp1"
        else:
            self.base_dir = Path(base_dir)
            if not self.base_dir.is_absolute():
                self.base_dir = self.project_root / self.base_dir

        # Verify input file exists
        if not self.input_file.exists():
            raise FileNotFoundError(
                f"Le fichier d'entrée n'existe pas : {self.input_file}\n"
                f"Veuillez vérifier que le fichier existe et que le chemin est correct.\n"
                f"Répertoire racine du projet : {self.project_root}\n"
                f"Répertoire de travail actuel : {Path.cwd()}"
            )

        print(f"Fichier d'entrée : {self.input_file}")
        print(f"Répertoire de sortie : {self.base_dir}")


def extract_barcode_sequence(
    df: pd.DataFrame, sequence_col: str, pattern: str
) -> pd.DataFrame:
    """
    Extract barcode sequence between specific motifs

    Args:
        df: Input DataFrame
        sequence_col: Column containing the full sequence
        pattern: Regex pattern for extraction

    Returns:
        DataFrame with extracted sequence
    """
    df_copy = df.copy()
    extracted_col = f'Extracted_Sequence_{sequence_col.split("_")[-1]}'
    df_copy[extracted_col] = df_copy[sequence_col].str.extract(pattern)
    return df_copy


def filter_barcodes_rd1(
    df: pd.DataFrame, sequences_to_remove: List[str]
) -> pd.DataFrame:
    """
    Filter out unnecessary sequences from round 1

    Args:
        df: Input DataFrame with barcodes
        sequences_to_remove: List of sequences to remove

    Returns:
        Filtered DataFrame
    """
    return df[~df["Extracted_Sequence_rd1"].isin(sequences_to_remove)]


def filter_barcodes_rd3(df: pd.DataFrame, barcode_to_remove: str) -> pd.DataFrame:
    """
    Filter out specific barcode from round 3

    Args:
        df: Input DataFrame with barcodes
        barcode_to_remove: Barcode sequence to remove

    Returns:
        Filtered DataFrame
    """
    return df[df["Extracted_Sequence_rd3"] != barcode_to_remove]


def create_barqc_file(
    df: pd.DataFrame, well_col: str, barcode_col: str, filename: str, round_num: int
) -> pd.DataFrame:
    """
    Create BarQC file with required columns

    Args:
        df: Input DataFrame
        well_col: Column name for well positions
        barcode_col: Column name for barcodes
        filename: Name of the output file
        round_num: Round number (1, 2, or 3)

    Returns:
        DataFrame in BarQC format
    """
    # Create new DataFrame with required columns
    barqc_df = pd.DataFrame(
        {
            "WellPosition": df[well_col],
            "Name": [f"Barcode{round_num}" for _ in df[well_col]],
            "Barcode": df[barcode_col],
        }
    )

    # Save to CSV with headers
    output_config.save_file(barqc_df, "barqc", filename, format="txt")
    return barqc_df


def integrate_metadata(
    metadata_df: pd.DataFrame,
    barcode_df: pd.DataFrame,
    well_col: str,
    barcode_col: str,
    base_filename: str,
) -> pd.DataFrame:
    """
    Integrate barcode information into metadata

    Args:
        metadata_df: Metadata DataFrame
        barcode_df: Barcode DataFrame
        well_col: Column name for well positions
        barcode_col: Column name for barcodes
        base_filename: Base name for output files

    Returns:
        Integrated DataFrame
    """
    integrated_df = pd.merge(
        metadata_df, barcode_df[[well_col, barcode_col]], on=well_col, how="left"
    )
    # Save in both formats
    output_config.save_file(
        integrated_df, "metadata", f"{base_filename}.xlsx", format="xlsx"
    )
    output_config.save_file(
        integrated_df, "metadata", f"{base_filename}.csv", format="txt"
    )
    return integrated_df


def main():
    """
    Main function to process barcodes
    """
    print("=== Barcode Processing for microSPLiT Protocol ===")
    print()

    # Configuration des chemins
    print(f"Répertoire de travail actuel : {Path.cwd()}")

    # Configuration avec le chemin absolu du projet
    path_config = PathConfig()

    # Initialisation de la configuration de sortie
    global output_config
    output_config = OutputConfig(str(path_config.base_dir))
    output_config.setup_directories()

    # Afficher le répertoire de sortie configuré
    print(f"\nRÉSUMÉ DE LA CONFIGURATION :")
    print("=" * 50)
    print(f"Répertoire racine du projet : {path_config.project_root}")
    print(f"Répertoire de sortie configuré : {output_config.base_dir}")
    print(f"Tous les fichiers seront générés dans ce répertoire et ses sous-dossiers")
    print("=" * 50)

    # Read input files using the configured path
    print("\nLecture des fichiers d'entrée...")
    df_Metadata_DOL_Exp1 = pd.read_excel(path_config.input_file, sheet_name="Exp1")
    df_Barcode_rd1 = pd.read_excel(path_config.input_file, sheet_name="Barcode.rd1")
    df_Barcode_rd2 = pd.read_excel(path_config.input_file, sheet_name="Barcode.rd2")
    df_Barcode_rd3 = pd.read_excel(path_config.input_file, sheet_name="Barcode.rd3")

    print("✓ Fichiers d'entrée lus avec succès")

    # Extract sequences for each round
    print("\nExtraction des séquences de barcodes...")
    df_Barcode_rd1 = extract_barcode_sequence(
        df_Barcode_rd1, "Sequence", r"/5Phos/ACTGTGG(.*?)TTTTTTTTTTTTTTTVN"
    )
    df_Barcode_rd2 = extract_barcode_sequence(
        df_Barcode_rd2, "Sequence", r"/5Phos/CATCGGCGTACGACT(.*?)ATCCACGTGCTTGAG"
    )
    df_Barcode_rd3 = extract_barcode_sequence(
        df_Barcode_rd3,
        "Sequence",
        r"/5Biosg/CAGACGTGTGCTCTTCCGATCTNNNNNNNNNN(.*?)GTGGCCGATGTTTCG",
    )

    print("✓ Séquences extraites")

    # Save non-filtered barcodes for STARsolo
    print("\nSauvegarde des barcodes non filtrés pour STARsolo...")
    output_config.save_file(
        df_Barcode_rd1[["Extracted_Sequence_rd1"]],
        "starsolo_non_filtered",
        "barcode_rd1.txt",
    )
    output_config.save_file(
        df_Barcode_rd2[["Extracted_Sequence_rd2"]],
        "starsolo_non_filtered",
        "barcode_rd2.txt",
    )
    output_config.save_file(
        df_Barcode_rd3[["Extracted_Sequence_rd3"]],
        "starsolo_non_filtered",
        "barcode_rd3.txt",
    )

    print("✓ Barcodes non filtrés sauvegardés")

    # Filter barcodes
    print("\nFiltrage des barcodes...")
    sequences_to_remove_rd1 = [
        "CGTCTAGG",
        "TCACTTTA",
        "GCTGCATG",
        "GAGGTTGA",
        "GCTATGCG",
        "CTGAAAGG",
    ]
    df_Barcode_rd1_filtered = filter_barcodes_rd1(
        df_Barcode_rd1, sequences_to_remove_rd1
    )
    df_Barcode_rd3_filtered = filter_barcodes_rd3(df_Barcode_rd3, "GCCAAGAC")

    print("✓ Barcodes filtrés")

    # Save filtered barcodes for STARsolo
    print("\nSauvegarde des barcodes filtrés pour STARsolo...")
    output_config.save_file(
        df_Barcode_rd1_filtered[["Extracted_Sequence_rd1"]],
        "starsolo_filtered",
        "barcode_rd1_filtered.txt",
    )
    output_config.save_file(
        df_Barcode_rd2[["Extracted_Sequence_rd2"]],
        "starsolo_filtered",
        "barcode_rd2_filtered.txt",
    )
    output_config.save_file(
        df_Barcode_rd3_filtered[["Extracted_Sequence_rd3"]],
        "starsolo_filtered",
        "barcode_rd3_filtered.txt",
    )

    print("✓ Barcodes filtrés sauvegardés")

    # Create BarQC files for each round
    print("\nCréation des fichiers BarQC...")
    barqc_rd1 = create_barqc_file(
        df_Barcode_rd1_filtered,
        "Well_loc_rd1",
        "Extracted_Sequence_rd1",
        "barcode_rd1_barqc.csv",
        1,
    )

    barqc_rd2 = create_barqc_file(
        df_Barcode_rd2,
        "Well_loc_rd2",
        "Extracted_Sequence_rd2",
        "barcode_rd2_barqc.csv",
        2,
    )

    barqc_rd3 = create_barqc_file(
        df_Barcode_rd3_filtered,
        "Well_loc_rd3",
        "Extracted_Sequence_rd3",
        "barcode_rd3_barqc.csv",
        3,
    )

    print("✓ Fichiers BarQC créés")

    # Metadata Integration
    print("\nIntégration des métadonnées...")
    df_Metadata_DOL_Exp1_complete = pd.merge(
        df_Metadata_DOL_Exp1,
        df_Barcode_rd1_filtered[["Well_loc_rd1", "Extracted_Sequence_rd1"]],
        on="Well_loc_rd1",
        how="left",
    )

    # Save metadata
    output_config.save_file(
        df_Metadata_DOL_Exp1_complete,
        "metadata",
        "metadata_DOL_Exp1_complete.csv",
        format="txt",
        include_header=True,
    )

    output_config.save_file(
        df_Metadata_DOL_Exp1_complete,
        "metadata",
        "metadata_DOL_Exp1_complete.xlsx",
        format="xlsx",
    )

    print("✓ Métadonnées intégrées et sauvegardées")

    # Barcode Combinations Generation
    print("\nGénération des combinaisons de barcodes...")

    # Read the barcodes for combinations
    df_barcode_rd1 = pd.read_csv(
        output_config.get_path("starsolo_non_filtered", "barcode_rd1.txt"),
        header=None,
        names=["Extracted_Sequence_rd1"],
    )
    df_barcode_rd2 = pd.read_csv(
        output_config.get_path("starsolo_non_filtered", "barcode_rd2.txt"),
        header=None,
        names=["Extracted_Sequence_rd2"],
    )
    df_barcode_rd3 = pd.read_csv(
        output_config.get_path("starsolo_non_filtered", "barcode_rd3.txt"),
        header=None,
        names=["Extracted_Sequence_rd3"],
    )

    # Create non-filtered combinations
    final_df_non_filtered = pd.concat(
        [df_barcode_rd1, df_barcode_rd2, df_barcode_rd3], axis=1
    )

    combinations_non_filtered = [
        f"{rd3}_{rd2}_{rd1}"
        for rd3, rd2, rd1 in product(
            final_df_non_filtered["Extracted_Sequence_rd3"].dropna().unique(),
            final_df_non_filtered["Extracted_Sequence_rd2"].dropna().unique(),
            final_df_non_filtered["Extracted_Sequence_rd1"].dropna().unique(),
        )
    ]

    combinations_df_non_filtered = pd.DataFrame(
        {"Combined_Sequence": combinations_non_filtered}
    )

    # Save non-filtered combinations
    output_config.save_file(
        combinations_df_non_filtered,
        "combinations",
        "combinations_sequences_3_rounds.csv",
        format="txt",
    )

    # Read filtered barcodes
    df_barcode_rd1_filtered = pd.read_csv(
        output_config.get_path("starsolo_filtered", "barcode_rd1_filtered.txt"),
        header=None,
        names=["Extracted_Sequence_rd1"],
    )
    df_barcode_rd2_filtered = pd.read_csv(
        output_config.get_path("starsolo_filtered", "barcode_rd2_filtered.txt"),
        header=None,
        names=["Extracted_Sequence_rd2"],
    )
    df_barcode_rd3_filtered = pd.read_csv(
        output_config.get_path("starsolo_filtered", "barcode_rd3_filtered.txt"),
        header=None,
        names=["Extracted_Sequence_rd3"],
    )

    # Create filtered combinations
    final_df_filtered = pd.concat(
        [df_barcode_rd1_filtered, df_barcode_rd2_filtered, df_barcode_rd3_filtered],
        axis=1,
    )

    combinations_filtered = [
        f"{rd3}_{rd2}_{rd1}"
        for rd3, rd2, rd1 in product(
            final_df_filtered["Extracted_Sequence_rd3"].dropna().unique(),
            final_df_filtered["Extracted_Sequence_rd2"].dropna().unique(),
            final_df_filtered["Extracted_Sequence_rd1"].dropna().unique(),
        )
    ]

    combinations_df_filtered = pd.DataFrame(
        {"Combined_Sequence": combinations_filtered}
    )

    # Save filtered combinations
    output_config.save_file(
        combinations_df_filtered,
        "combinations",
        "combinations_sequences_3_rounds_filtered.csv",
        format="txt",
    )

    print("✓ Combinaisons de barcodes générées")

    # Extracted Barcodes Generation
    print("\nGénération des barcodes extraits...")

    # Create extracted barcodes files
    extracted_barcodes_non_filtered = pd.concat(
        [df_barcode_rd1, df_barcode_rd2, df_barcode_rd3], axis=1
    )

    output_config.save_file(
        extracted_barcodes_non_filtered,
        "extracted_barcodes",
        "extracted_barcodes_3_rounds.csv",
        format="txt",
    )

    extracted_barcodes_filtered = pd.concat(
        [df_barcode_rd1_filtered, df_barcode_rd2_filtered, df_barcode_rd3_filtered],
        axis=1,
    )

    output_config.save_file(
        extracted_barcodes_filtered,
        "extracted_barcodes",
        "extracted_barcodes_3_rounds_filtered.csv",
        format="txt",
    )

    print("✓ Barcodes extraits générés")

    # Summary
    print("\n" + "=" * 60)
    print("RÉSUMÉ DES FICHIERS GÉNÉRÉS")
    print("=" * 60)

    categories = {
        "BarQC Files": "barqc",
        "STARsolo Barcode Files (Filtered)": "starsolo_filtered",
        "STARsolo Barcode Files (Non-filtered)": "starsolo_non_filtered",
        "Metadata Files": "metadata",
        "Combinations": "combinations",
        "Extracted Barcodes": "extracted_barcodes",
    }

    for category_name, category in categories.items():
        print(f"\n{category_name} :")
        print("-" * 30)
        directory = output_config.directories[category]
        if directory.exists():
            files = list(directory.glob("*"))
            if files:
                for file in sorted(files):
                    print(f"✓ {file.name}")
            else:
                print("Aucun fichier trouvé")
        else:
            print(f"✗ Répertoire non trouvé : {directory}")

    print(f"\nTous les fichiers sont sauvegardés dans : {output_config.base_dir}")
    print("\nTraitement terminé avec succès ! 🎉")


if __name__ == "__main__":
    main()
