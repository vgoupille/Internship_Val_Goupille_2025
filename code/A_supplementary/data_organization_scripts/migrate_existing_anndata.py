#!/usr/bin/env python3
"""
Script to migrate existing AnnData files to the new organized structure.

Author: Valentin Goupille
Date: 2025-07-18
"""

import os
import shutil
from pathlib import Path


def migrate_existing_anndata():
    """
    Migrate existing AnnData files to the new organized structure.
    """
    print("📦 Migrating existing AnnData files to new structure...")

    # Define migration mappings
    migrations = [
        {
            "source": "data/anndata_objects/",
            "destination": "data/Anndata/raw/",
            "description": "Raw AnnData objects",
        },
        {
            "source": "data/anndata_objects_with_complete_metadata/",
            "destination": "data/Anndata/with_metadata/",
            "description": "Objects with metadata",
        },
        {
            "source": "data/anndata_objects_with_complete_metadata_filtered/",
            "destination": "data/Anndata/filtered/",
            "description": "Filtered objects",
        },
    ]

    for migration in migrations:
        source_path = Path(migration["source"])
        dest_path = Path(migration["destination"])

        print(f"\n🔄 Migrating {migration['description']}...")
        print(f"   From: {source_path}")
        print(f"   To: {dest_path}")

        if not source_path.exists():
            print(f"   ⚠️  Source directory does not exist: {source_path}")
            continue

        # Create destination directory if it doesn't exist
        dest_path.mkdir(parents=True, exist_ok=True)

        # Find all .h5ad files in source
        h5ad_files = list(source_path.glob("*.h5ad"))
        csv_files = list(source_path.glob("*.csv"))

        if not h5ad_files and not csv_files:
            print(f"   ℹ️  No files found in {source_path}")
            continue

        # Copy files
        files_copied = 0
        for file_path in h5ad_files + csv_files:
            dest_file = dest_path / file_path.name

            if dest_file.exists():
                print(f"   ⚠️  File already exists: {dest_file.name}")
                continue

            shutil.copy2(file_path, dest_file)
            print(f"   ✅ Copied: {file_path.name}")
            files_copied += 1

        print(f"   📊 Total files copied: {files_copied}")

        # Optionally remove source directory if empty
        if source_path.exists() and not any(source_path.iterdir()):
            print(f"   🗑️  Removing empty source directory: {source_path}")
            source_path.rmdir()

    print("\n🎉 Migration completed!")
    print("\nNew structure:")
    print("data/Anndata/")
    print("├── raw/")
    print("├── with_metadata/")
    print("├── filtered/")
    print("└── README.md")


def list_current_files():
    """
    List current files in the new structure.
    """
    print("\n📋 Current files in new structure:")

    base_path = Path("data/Anndata")
    if not base_path.exists():
        print("   ⚠️  Anndata directory does not exist")
        return

    for subdir in ["raw", "with_metadata", "filtered"]:
        subdir_path = base_path / subdir
        if subdir_path.exists():
            files = list(subdir_path.glob("*"))
            print(f"\n📁 {subdir}/:")
            if files:
                for file in files:
                    print(f"   - {file.name}")
            else:
                print("   (empty)")


if __name__ == "__main__":
    migrate_existing_anndata()
    list_current_files()
