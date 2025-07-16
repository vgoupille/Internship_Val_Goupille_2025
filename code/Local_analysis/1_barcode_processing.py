#!/usr/bin/env python3
"""
Barcode Processing for microSPLiT Protocol
Author: Valentin Goupille
Date: 2025-05-25
"""

import pandas as pd
import os
from itertools import product
from typing import List, Dict, Tuple
from pathlib import Path


class SimpleOutputConfig:
    """
    Simplified configuration for output paths
    """

    def __init__(self, base_output_dir: str = "processed_barcodes"):
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
        """
        output_path = self.get_path(category, filename)
        if format == "txt":
            # For starsolo files, never include header
            if category in ["starsolo_filtered", "starsolo_non_filtered"]:
                df.to_csv(output_path, index=False, header=False)
            else:
                df.to_csv(output_path, index=False, header=include_header)
        else:
            df.to_excel(output_path, index=False)


def extract_barcode_sequence(
    df: pd.DataFrame, sequence_col: str, pattern: str
) -> pd.DataFrame:
    """
    Extract barcode sequence between specific motifs
    """
    df_copy = df.copy()
    extracted_col = f'Extracted_Sequence_{sequence_col.split("_")[-1]}'
    df_copy[extracted_col] = df_copy[sequence_col].str.extract(pattern)
    return df_copy


def filter_barcodes_rd1(
    df: pd.DataFrame, sequences_to_remove: List[str]
) -> pd.DataFrame:
    """
    Filter out problematic sequences from round 1

    Args:
        df: DataFrame containing round 1 barcodes
        sequences_to_remove: List of barcode sequences to exclude

    Returns:
        DataFrame with filtered barcodes (problematic sequences removed)
    """
    initial_count = len(df)
    filtered_df = df[~df["Extracted_Sequence_rd1"].isin(sequences_to_remove)]
    removed_count = initial_count - len(filtered_df)

    print(
        f"    Round 1: {initial_count} → {len(filtered_df)} barcodes ({removed_count} removed)"
    )
    return filtered_df


def filter_barcodes_rd2(
    df: pd.DataFrame, sequences_to_remove: List[str]
) -> pd.DataFrame:
    """
    Filter out problematic sequences from round 2

    Args:
        df: DataFrame containing round 2 barcodes
        sequences_to_remove: List of barcode sequences to exclude

    Returns:
        DataFrame with filtered barcodes (problematic sequences removed)
    """
    initial_count = len(df)
    if sequences_to_remove:
        filtered_df = df[~df["Extracted_Sequence_rd2"].isin(sequences_to_remove)]
    else:
        filtered_df = df  # No filtering if list is empty
    removed_count = initial_count - len(filtered_df)

    print(
        f"    Round 2: {initial_count} → {len(filtered_df)} barcodes ({removed_count} removed)"
    )
    return filtered_df


def filter_barcodes_rd3(df: pd.DataFrame, barcode_to_remove: str) -> pd.DataFrame:
    """
    Filter out problematic barcode from round 3

    Args:
        df: DataFrame containing round 3 barcodes
        barcode_to_remove: Specific barcode sequence to exclude

    Returns:
        DataFrame with filtered barcodes (problematic sequence removed)
    """
    initial_count = len(df)
    filtered_df = df[df["Extracted_Sequence_rd3"] != barcode_to_remove]
    removed_count = initial_count - len(filtered_df)

    print(
        f"    Round 3: {initial_count} → {len(filtered_df)} barcodes ({removed_count} removed)"
    )
    return filtered_df


def create_barqc_file(
    df: pd.DataFrame,
    well_col: str,
    barcode_col: str,
    filename: str,
    round_num: int,
    output_config: SimpleOutputConfig,
) -> pd.DataFrame:
    """
    Create BarQC file with required columns
    """
    barqc_df = pd.DataFrame(
        {
            "WellPosition": df[well_col],
            "Name": [f"Barcode{round_num}" for _ in df[well_col]],
            "Barcode": df[barcode_col],
        }
    )

    output_config.save_file(barqc_df, "barqc", filename, format="txt")
    return barqc_df


def main():
    """
    Main function to process barcodes
    """
    print("=== Barcode Processing for microSPLiT Protocol - Simplified Version ===")
    print()

    # =============================================================================
    # BARCODE FILTERING CONFIGURATION
    # =============================================================================
    # These barcodes will be EXCLUDED from the analysis
    # Modify these lists if you need to add/remove filtered barcodes

    # Round 1 barcodes to REMOVE (not used for the analysis)
    sequences_to_remove_rd1 = [
        "CGTCTAGG",  # Remove this barcode from round 1
        "TCACTTTA",  # Remove this barcode from round 1
        "GCTGCATG",  # Remove this barcode from round 1
        "GAGGTTGA",  # Remove this barcode from round 1
        "GCTATGCG",  # Remove this barcode from round 1
        "CTGAAAGG",  # Remove this barcode from round 1
    ]

    # Round 2 barcodes to REMOVE
    # Currently NO barcodes are filtered for round 2
    # Add sequences here if needed: sequences_to_remove_rd2 = ["SEQUENCE1", "SEQUENCE2"]
    sequences_to_remove_rd2 = []

    # Round 3 barcodes to REMOVE
    # This barcode is removed
    barcode_to_remove_rd3 = "GCCAAGAC"

    print(f"✓ Filtering configuration loaded:")
    print(f"  - Round 1: {len(sequences_to_remove_rd1)} barcodes will be removed")
    print(f"  - Round 2: {len(sequences_to_remove_rd2)} barcodes will be removed")
    print(f"  - Round 3: 1 barcode will be removed ({barcode_to_remove_rd3})")
    print()

    # =============================================================================
    # FILE CONFIGURATION
    # =============================================================================

    # Simple configuration - use Excel file in data/tab directory
    input_file = "data/tab/metadata_DOL_rep1.xlsx"

    # Check if file exists
    if not Path(input_file).exists():
        print(f"❌ Error: The file {input_file} does not exist")
        print(f"Current directory: {Path.cwd()}")
        print("Please ensure the Excel file is in the data/tab/ directory")
        return

    print(f"✓ Input file found: {input_file}")

    # Output configuration
    output_config = SimpleOutputConfig("data/barcodes_result")
    output_config.setup_directories()

    print(f"✓ Output directory configured: {output_config.base_dir}")

    try:
        # Read input files
        print("\nReading input files...")
        df_metadata_dol_exp1 = pd.read_excel(input_file, sheet_name="Exp1")
        df_barcode_rd1 = pd.read_excel(input_file, sheet_name="Barcode.rd1")
        df_barcode_rd2 = pd.read_excel(input_file, sheet_name="Barcode.rd2")
        df_barcode_rd3 = pd.read_excel(input_file, sheet_name="Barcode.rd3")

        print("✓ Input files read successfully")

        # Extract sequences for each round
        print("\nExtracting barcode sequences...")
        df_barcode_rd1 = extract_barcode_sequence(
            df_barcode_rd1, "Sequence", r"/5Phos/ACTGTGG(.*?)TTTTTTTTTTTTTTTVN"
        )
        df_barcode_rd2 = extract_barcode_sequence(
            df_barcode_rd2, "Sequence", r"/5Phos/CATCGGCGTACGACT(.*?)ATCCACGTGCTTGAG"
        )
        df_barcode_rd3 = extract_barcode_sequence(
            df_barcode_rd3,
            "Sequence",
            r"/5Biosg/CAGACGTGTGCTCTTCCGATCTNNNNNNNNNN(.*?)GTGGCCGATGTTTCG",
        )

        print("✓ Sequences extracted")

        # Save non-filtered barcodes for STARsolo
        print("\nSaving non-filtered barcodes for STARsolo...")
        output_config.save_file(
            df_barcode_rd1[["Extracted_Sequence_rd1"]],
            "starsolo_non_filtered",
            "barcode_rd1.txt",
        )
        output_config.save_file(
            df_barcode_rd2[["Extracted_Sequence_rd2"]],
            "starsolo_non_filtered",
            "barcode_rd2.txt",
        )
        output_config.save_file(
            df_barcode_rd3[["Extracted_Sequence_rd3"]],
            "starsolo_non_filtered",
            "barcode_rd3.txt",
        )

        print("✓ Non-filtered barcodes saved")

        # Filter barcodes
        print("\nFiltering barcodes...")
        print(
            f"  - Applying filters to Round 1: removing {len(sequences_to_remove_rd1)} sequences"
        )
        print(
            f"  - Applying filters to Round 2: removing {len(sequences_to_remove_rd2)} sequences"
        )
        print(
            f"  - Applying filters to Round 3: removing 1 sequence ({barcode_to_remove_rd3})"
        )

        df_barcode_rd1_filtered = filter_barcodes_rd1(
            df_barcode_rd1, sequences_to_remove_rd1
        )
        df_barcode_rd2_filtered = filter_barcodes_rd2(
            df_barcode_rd2, sequences_to_remove_rd2
        )
        df_barcode_rd3_filtered = filter_barcodes_rd3(
            df_barcode_rd3, barcode_to_remove_rd3
        )

        print("✓ Barcodes filtered")

        # Save filtered barcodes for STARsolo
        print("\nSaving filtered barcodes for STARsolo...")
        output_config.save_file(
            df_barcode_rd1_filtered[["Extracted_Sequence_rd1"]],
            "starsolo_filtered",
            "barcode_rd1_filtered.txt",
        )
        output_config.save_file(
            df_barcode_rd2_filtered[["Extracted_Sequence_rd2"]],
            "starsolo_filtered",
            "barcode_rd2_filtered.txt",
        )
        output_config.save_file(
            df_barcode_rd3_filtered[["Extracted_Sequence_rd3"]],
            "starsolo_filtered",
            "barcode_rd3_filtered.txt",
        )

        print("✓ Filtered barcodes saved")

        # Create BarQC files for each round
        print("\nCreating BarQC files...")
        barqc_rd1 = create_barqc_file(
            df_barcode_rd1_filtered,
            "Well_loc_rd1",
            "Extracted_Sequence_rd1",
            "barcode_rd1_barqc.csv",
            1,
            output_config,
        )

        barqc_rd2 = create_barqc_file(
            df_barcode_rd2_filtered,
            "Well_loc_rd2",
            "Extracted_Sequence_rd2",
            "barcode_rd2_barqc.csv",
            2,
            output_config,
        )

        barqc_rd3 = create_barqc_file(
            df_barcode_rd3_filtered,
            "Well_loc_rd3",
            "Extracted_Sequence_rd3",
            "barcode_rd3_barqc.csv",
            3,
            output_config,
        )

        print("✓ BarQC files created")

        # Metadata Integration
        print("\nIntegrating metadata...")
        df_metadata_dol_exp1_complete = pd.merge(
            df_metadata_dol_exp1,
            df_barcode_rd1_filtered[["Well_loc_rd1", "Extracted_Sequence_rd1"]],
            on="Well_loc_rd1",
            how="left",
        )

        # Save metadata
        output_config.save_file(
            df_metadata_dol_exp1_complete,
            "metadata",
            "metadata_DOL_Exp1_complete.csv",
            format="txt",
            include_header=True,
        )

        output_config.save_file(
            df_metadata_dol_exp1_complete,
            "metadata",
            "metadata_DOL_Exp1_complete.xlsx",
            format="xlsx",
        )

        print("✓ Metadata integrated and saved")

        # Barcode Combinations Generation
        print("\nGenerating barcode combinations...")

        # Read the barcodes for combinations
        df_barcode_rd1_for_combinations = pd.read_csv(
            output_config.get_path("starsolo_non_filtered", "barcode_rd1.txt"),
            header=None,
            names=["Extracted_Sequence_rd1"],
        )
        df_barcode_rd2_for_combinations = pd.read_csv(
            output_config.get_path("starsolo_non_filtered", "barcode_rd2.txt"),
            header=None,
            names=["Extracted_Sequence_rd2"],
        )
        df_barcode_rd3_for_combinations = pd.read_csv(
            output_config.get_path("starsolo_non_filtered", "barcode_rd3.txt"),
            header=None,
            names=["Extracted_Sequence_rd3"],
        )

        # Create non-filtered combinations
        final_df_non_filtered = pd.concat(
            [
                df_barcode_rd1_for_combinations,
                df_barcode_rd2_for_combinations,
                df_barcode_rd3_for_combinations,
            ],
            axis=1,
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
        df_barcode_rd1_filtered_for_combinations = pd.read_csv(
            output_config.get_path("starsolo_filtered", "barcode_rd1_filtered.txt"),
            header=None,
            names=["Extracted_Sequence_rd1"],
        )
        df_barcode_rd2_filtered_for_combinations = pd.read_csv(
            output_config.get_path("starsolo_filtered", "barcode_rd2_filtered.txt"),
            header=None,
            names=["Extracted_Sequence_rd2"],
        )
        df_barcode_rd3_filtered_for_combinations = pd.read_csv(
            output_config.get_path("starsolo_filtered", "barcode_rd3_filtered.txt"),
            header=None,
            names=["Extracted_Sequence_rd3"],
        )

        # Create filtered combinations
        final_df_filtered = pd.concat(
            [
                df_barcode_rd1_filtered_for_combinations,
                df_barcode_rd2_filtered_for_combinations,
                df_barcode_rd3_filtered_for_combinations,
            ],
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

        print("✓ Barcode combinations generated")

        # Extracted Barcodes Generation
        print("\nGenerating extracted barcodes...")

        # Create extracted barcodes files
        extracted_barcodes_non_filtered = pd.concat(
            [
                df_barcode_rd1_for_combinations,
                df_barcode_rd2_for_combinations,
                df_barcode_rd3_for_combinations,
            ],
            axis=1,
        )

        output_config.save_file(
            extracted_barcodes_non_filtered,
            "extracted_barcodes",
            "extracted_barcodes_3_rounds.csv",
            format="txt",
        )

        extracted_barcodes_filtered = pd.concat(
            [
                df_barcode_rd1_filtered_for_combinations,
                df_barcode_rd2_filtered_for_combinations,
                df_barcode_rd3_filtered_for_combinations,
            ],
            axis=1,
        )

        output_config.save_file(
            extracted_barcodes_filtered,
            "extracted_barcodes",
            "extracted_barcodes_3_rounds_filtered.csv",
            format="txt",
        )

        print("✓ Extracted barcodes generated")

        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY OF GENERATED FILES")
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
            print(f"\n{category_name}:")
            print("-" * 30)
            directory = output_config.directories[category]
            if directory.exists():
                files = list(directory.glob("*"))
                if files:
                    for file in sorted(files):
                        print(f"✓ {file.name}")
                else:
                    print("No files found")
            else:
                print(f"✗ Directory not found: {directory}")

        print(f"\nAll files are saved in: {output_config.base_dir}")
        print("\nProcessing completed successfully! 🎉")

    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        print("Please check that the Excel file contains the correct sheets:")
        print("- Exp1")
        print("- Barcode.rd1")
        print("- Barcode.rd2")
        print("- Barcode.rd3")


if __name__ == "__main__":
    main()
