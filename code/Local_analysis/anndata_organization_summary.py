#!/usr/bin/env python3
"""
Summary script for AnnData organization.

Author: Valentin Goupille
Date: 2025-01-13
"""

import os
from pathlib import Path


def print_summary():
    """
    Print a comprehensive summary of the AnnData organization.
    """
    print("=" * 80)
    print("🧬 ANNDATA ORGANIZATION SUMMARY")
    print("=" * 80)

    print("\n📋 WHAT WAS DONE:")
    print("• ✅ Created new organized directory structure: data/Anndata/")
    print("• ✅ Modified all scripts to use the new structure")
    print("• ✅ Migrated existing files to the new organization")
    print("• ✅ Created documentation and helper scripts")

    print("\n📁 NEW DIRECTORY STRUCTURE:")
    print("data/Anndata/")
    print("├── raw/           # Raw AnnData objects from STARsolo (2a)")
    print("├── with_metadata/ # Objects with cell + gene metadata (2c)")
    print("├── filtered/      # Filtered objects (3a, 3b, 3c)")
    print("│   ├── csv/       # CSV reports organized by step")
    print("│   │   ├── 3a_filtering_100UMIs/")
    print("│   │   ├── 3b_filtering_advanced_cell/")
    print("│   │   └── 3c_filtering_advanced_gene/")
    print("│   └── *.h5ad     # Filtered AnnData files")
    print("└── README.md      # Documentation")

    print("\n🔄 PROCESSING PIPELINE:")
    print("1. 2a_starsolo_to_anndata.py     → data/Anndata/raw/")
    print("2. 2c_add_metadata_to_anndata.py → data/Anndata/with_metadata/")
    print("3. 3a_filtering_100UMIs.py       → data/Anndata/filtered/")
    print("4. 3b_filtering_advanced_cell_v2.py → data/Anndata/filtered/")
    print("5. 3c_filtering_advanced_gene.py → data/Anndata/filtered/")

    print("\n📊 FILE COUNTS:")
    base_path = Path("data/Anndata")

    if base_path.exists():
        for subdir in ["raw", "with_metadata", "filtered"]:
            subdir_path = base_path / subdir
            if subdir_path.exists():
                h5ad_files = list(subdir_path.glob("*.h5ad"))
                csv_files = list(subdir_path.glob("*.csv"))

                # For filtered, also count CSV files in subdirectories
                if subdir == "filtered":
                    csv_subdir = subdir_path / "csv"
                    if csv_subdir.exists():
                        csv_files_in_subdirs = list(csv_subdir.glob("**/*.csv"))
                        print(
                            f"• {subdir}/: {len(h5ad_files)} .h5ad files, {len(csv_files)} .csv files"
                        )
                        print(
                            f"  └── csv/: {len(csv_files_in_subdirs)} .csv files in subdirectories"
                        )

                        # Detail CSV subdirectories
                        for csv_step_dir in csv_subdir.iterdir():
                            if csv_step_dir.is_dir():
                                step_csv_files = list(csv_step_dir.glob("*.csv"))
                                print(
                                    f"      └── {csv_step_dir.name}/: {len(step_csv_files)} .csv files"
                                )
                    else:
                        total_files = len(h5ad_files) + len(csv_files)
                        print(
                            f"• {subdir}/: {len(h5ad_files)} .h5ad files, {len(csv_files)} .csv files ({total_files} total)"
                        )
                else:
                    total_files = len(h5ad_files) + len(csv_files)
                    print(
                        f"• {subdir}/: {len(h5ad_files)} .h5ad files, {len(csv_files)} .csv files ({total_files} total)"
                    )

    print("\n🔧 MODIFIED SCRIPTS:")
    scripts_modified = [
        "2a_starsolo_to_anndata.py",
        "2c_add_metadata_to_anndata.py",
        "3a_filtering_100UMIs.py",
        "3b_filtering_advanced_cell_v2.py",
        "3c_filtering_advanced_gene.py",
    ]

    for script in scripts_modified:
        print(f"• ✅ {script}")

    print("\n🆕 NEW HELPER SCRIPTS:")
    helper_scripts = [
        "create_anndata_structure.py",
        "migrate_existing_anndata.py",
        "organize_csv_reports.py",
        "cleanup_old_anndata_dirs.py",
        "anndata_organization_summary.py",
    ]

    for script in helper_scripts:
        print(f"• ✅ {script}")

    print("\n💡 ADVANTAGES OF NEW STRUCTURE:")
    print("• 🎯 Clear separation by processing stage")
    print("• 📚 Better organization and findability")
    print("• 🔄 Easier maintenance and updates")
    print("• 📖 Self-documenting with README")
    print("• 🚀 Scalable for future processing steps")

    print("\n🎯 NEXT STEPS:")
    print("• Run the modified scripts to test the new structure")
    print("• Optionally clean up old directories with cleanup_old_anndata_dirs.py")
    print("• Update any external references to the old paths")

    print("\n" + "=" * 80)
    print("🎉 ANNDATA ORGANIZATION COMPLETE!")
    print("=" * 80)


def check_all_files():
    """
    Check all files in the new structure.
    """
    print("\n📋 DETAILED FILE LISTING:")
    print("-" * 60)

    base_path = Path("data/Anndata")
    if not base_path.exists():
        print("❌ Anndata directory not found!")
        return

    for subdir in ["raw", "with_metadata", "filtered"]:
        subdir_path = base_path / subdir
        if subdir_path.exists():
            files = sorted(list(subdir_path.iterdir()))
            print(f"\n📁 {subdir}/ ({len(files)} files):")

            for file in files:
                if file.is_file():
                    size = file.stat().st_size / (1024 * 1024)  # MB
                    if file.suffix == ".h5ad":
                        print(f"   🧬 {file.name} ({size:.1f} MB)")
                    elif file.suffix == ".csv":
                        print(f"   📊 {file.name} ({size:.1f} MB)")
                    else:
                        print(f"   📄 {file.name} ({size:.1f} MB)")
                elif file.is_dir() and file.name == "csv":
                    # Show CSV subdirectories
                    csv_subdirs = sorted(list(file.iterdir()))
                    print(f"   📁 csv/ ({len(csv_subdirs)} subdirectories):")

                    for csv_subdir in csv_subdirs:
                        if csv_subdir.is_dir():
                            csv_files = list(csv_subdir.glob("*.csv"))
                            print(
                                f"      📁 {csv_subdir.name}/ ({len(csv_files)} files):"
                            )

                            for csv_file in csv_files:
                                size = csv_file.stat().st_size / (1024 * 1024)  # MB
                                print(f"         📊 {csv_file.name} ({size:.1f} MB)")
        else:
            print(f"\n📁 {subdir}/: NOT FOUND")


if __name__ == "__main__":
    print_summary()
    check_all_files()
