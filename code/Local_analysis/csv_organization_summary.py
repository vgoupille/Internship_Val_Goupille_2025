#!/usr/bin/env python3
"""
Summary of CSV organization in the AnnData structure.

Author: Valentin Goupille
Date: 2025-01-13
"""

import os
from pathlib import Path


def print_csv_organization_summary():
    """
    Print a summary of the CSV organization changes.
    """
    print("=" * 80)
    print("📊 CSV ORGANIZATION SUMMARY")
    print("=" * 80)

    print("\n🎯 OBJECTIVE:")
    print("Organize CSV reports in subdirectories based on processing step")
    print("to improve clarity and maintainability.")

    print("\n📋 WHAT WAS DONE:")
    print("• ✅ Modified scripts 3a, 3b, 3c to save CSV in specific subdirectories")
    print("• ✅ Created organize_csv_reports.py script")
    print("• ✅ Migrated existing CSV files to new structure")
    print("• ✅ Updated README.md with new structure documentation")
    print("• ✅ Updated summary scripts to reflect new organization")

    print("\n📁 NEW CSV STRUCTURE:")
    print("data/Anndata/filtered/")
    print("├── *.h5ad files (AnnData objects)")
    print("└── csv/")
    print("    ├── 3a_filtering_100UMIs/")
    print("    │   ├── *_filtering_stats.csv")
    print("    │   └── *_metadata.csv")
    print("    ├── 3b_filtering_advanced_cell/")
    print("    │   └── filtering_summary_report_v2.csv")
    print("    └── 3c_filtering_advanced_gene/")
    print("        ├── gene_filtering_summary_report.csv")
    print("        └── gene_annotation_summary.csv")

    print("\n🔄 SCRIPT MODIFICATIONS:")
    modifications = [
        ("3a_filtering_100UMIs.py", "Saves CSV to csv/3a_filtering_100UMIs/"),
        (
            "3b_filtering_advanced_cell_v2.py",
            "Saves CSV to csv/3b_filtering_advanced_cell/",
        ),
        (
            "3c_filtering_advanced_gene.py",
            "Saves CSV to csv/3c_filtering_advanced_gene/",
        ),
    ]

    for script, description in modifications:
        print(f"• {script}: {description}")

    print("\n📊 CSV FILES BY STEP:")
    csv_base_path = Path("data/Anndata/filtered/csv")

    if csv_base_path.exists():
        for step_dir in sorted(csv_base_path.iterdir()):
            if step_dir.is_dir():
                csv_files = list(step_dir.glob("*.csv"))
                print(f"\n📁 {step_dir.name}/ ({len(csv_files)} files):")

                for csv_file in csv_files:
                    size = csv_file.stat().st_size / (1024 * 1024)  # MB
                    print(f"   📊 {csv_file.name} ({size:.1f} MB)")
    else:
        print("❌ CSV directory not found!")

    print("\n💡 ADVANTAGES OF NEW STRUCTURE:")
    print("• 🎯 Clear separation by processing step")
    print("• 📚 Easier to find reports for specific analyses")
    print("• 🔄 Cleaner main filtered/ directory")
    print("• 📖 Self-documenting organization")
    print("• 🚀 Scalable for future processing steps")

    print("\n🎯 USAGE:")
    print("CSV reports are now organized by the script that generated them:")
    print("• For 100 UMI filtering reports → csv/3a_filtering_100UMIs/")
    print("• For advanced cell filtering reports → csv/3b_filtering_advanced_cell/")
    print("• For gene filtering reports → csv/3c_filtering_advanced_gene/")

    print("\n" + "=" * 80)
    print("🎉 CSV ORGANIZATION COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    print_csv_organization_summary()
