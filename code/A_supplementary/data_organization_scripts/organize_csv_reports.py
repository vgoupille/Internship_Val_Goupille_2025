#!/usr/bin/env python3
"""
Script to organize CSV reports into subdirectories based on processing step.

Author: Valentin Goupille
Date: 2025-07-18
"""

import os
import shutil
from pathlib import Path


def organize_csv_reports():
    """
    Organize CSV reports into subdirectories based on processing step.
    """
    print("📊 Organizing CSV reports into subdirectories...")

    # Define the base filtered directory
    filtered_dir = Path("data/Anndata/filtered")

    if not filtered_dir.exists():
        print(f"❌ Filtered directory not found: {filtered_dir}")
        return

    # Define CSV file mappings to their respective subdirectories
    csv_mappings = {
        # 3a files
        "filtering_stats.csv": "3a_filtering_100UMIs",
        "GeneFull_raw_unique_mult_with_metadata_grouped_filtered_100UMI_filtering_stats.csv": "3a_filtering_100UMIs",
        "GeneFull_raw_unique_mult_with_metadata_grouped_filtered_100UMI_metadata.csv": "3a_filtering_100UMIs",
        # 3b files
        "filtering_summary_report_v2.csv": "3b_filtering_advanced_cell",
        # 3c files
        "gene_filtering_summary_report.csv": "3c_filtering_advanced_gene",
        "gene_annotation_summary.csv": "3c_filtering_advanced_gene",
    }

    # Create subdirectories
    csv_base_dir = filtered_dir / "csv"
    subdirs = [
        "3a_filtering_100UMIs",
        "3b_filtering_advanced_cell",
        "3c_filtering_advanced_gene",
    ]

    for subdir in subdirs:
        subdir_path = csv_base_dir / subdir
        subdir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {subdir_path}")

    # Move CSV files to their respective subdirectories
    csv_files = list(filtered_dir.glob("*.csv"))

    if not csv_files:
        print("ℹ️  No CSV files found in filtered directory")
        return

    files_moved = 0
    for csv_file in csv_files:
        filename = csv_file.name

        # Find the appropriate subdirectory
        target_subdir = None
        for pattern, subdir in csv_mappings.items():
            if pattern in filename or filename == pattern:
                target_subdir = subdir
                break

        if target_subdir:
            target_path = csv_base_dir / target_subdir / filename

            # Move the file
            shutil.move(str(csv_file), str(target_path))
            print(f"📁 Moved: {filename} → csv/{target_subdir}/")
            files_moved += 1
        else:
            # If no mapping found, put it in a general folder
            general_dir = csv_base_dir / "general"
            general_dir.mkdir(exist_ok=True)
            target_path = general_dir / filename

            shutil.move(str(csv_file), str(target_path))
            print(f"📁 Moved: {filename} → csv/general/ (no specific mapping)")
            files_moved += 1

    print(f"\n📊 Total files moved: {files_moved}")


def show_new_structure():
    """
    Show the new CSV directory structure.
    """
    print("\n📁 New CSV directory structure:")
    print("=" * 60)

    csv_dir = Path("data/Anndata/filtered/csv")
    if csv_dir.exists():
        print(f"📁 {csv_dir}/")

        for subdir in csv_dir.iterdir():
            if subdir.is_dir():
                files = list(subdir.glob("*.csv"))
                print(f"├── 📁 {subdir.name}/ ({len(files)} files)")

                for file in files:
                    print(f"│   └── 📊 {file.name}")
    else:
        print("❌ CSV directory not found!")

    print("=" * 60)


def verify_organization():
    """
    Verify that the organization was successful.
    """
    print("\n🔍 Verifying CSV organization...")

    csv_dir = Path("data/Anndata/filtered/csv")
    if not csv_dir.exists():
        print("❌ CSV directory not found!")
        return False

    # Check each expected subdirectory
    expected_subdirs = [
        "3a_filtering_100UMIs",
        "3b_filtering_advanced_cell",
        "3c_filtering_advanced_gene",
    ]
    all_good = True

    for subdir in expected_subdirs:
        subdir_path = csv_dir / subdir
        if subdir_path.exists():
            csv_files = list(subdir_path.glob("*.csv"))
            print(f"✅ {subdir}/: {len(csv_files)} CSV files")
        else:
            print(f"❌ {subdir}/: directory not found")
            all_good = False

    # Check if any CSV files remain in the main filtered directory
    remaining_csvs = list(Path("data/Anndata/filtered").glob("*.csv"))
    if remaining_csvs:
        print(f"⚠️  {len(remaining_csvs)} CSV files still in main filtered directory:")
        for csv_file in remaining_csvs:
            print(f"   - {csv_file.name}")
    else:
        print("✅ No CSV files remaining in main filtered directory")

    if all_good and not remaining_csvs:
        print("✅ CSV organization verification successful!")
        return True
    else:
        print("❌ CSV organization verification failed!")
        return False


if __name__ == "__main__":
    organize_csv_reports()
    show_new_structure()
    verify_organization()
    print("\n🎉 CSV organization completed!")
