#!/usr/bin/env python3
"""
Script to cleanup old AnnData directories after migration.

Author: Valentin Goupille
Date: 2025-01-13
"""

import os
import shutil
from pathlib import Path


def cleanup_old_directories():
    """
    Clean up old AnnData directories after successful migration.
    """
    print("🧹 Cleaning up old AnnData directories...")

    # Define old directories to clean up
    old_dirs = [
        "data/anndata_objects/",
        "data/anndata_objects_with_complete_metadata/",
        "data/anndata_objects_with_complete_metadata_filtered/",
    ]

    for old_dir in old_dirs:
        old_path = Path(old_dir)

        if not old_path.exists():
            print(f"   ℹ️  Directory does not exist: {old_dir}")
            continue

        # Check if directory is empty
        if not any(old_path.iterdir()):
            print(f"   🗑️  Removing empty directory: {old_dir}")
            old_path.rmdir()
        else:
            # List remaining files
            remaining_files = list(old_path.iterdir())
            print(f"   ⚠️  Directory not empty: {old_dir}")
            print(f"       Remaining files: {len(remaining_files)}")
            for file in remaining_files:
                print(f"       - {file.name}")

            # Ask user if they want to remove the directory
            print(
                f"\n   🤔 Do you want to remove {old_dir} and all its contents? (y/N)"
            )
            response = input().strip().lower()
            if response == "y":
                shutil.rmtree(old_path)
                print(f"   ✅ Removed: {old_dir}")
            else:
                print(f"   ℹ️  Kept: {old_dir}")


def show_final_structure():
    """
    Show the final directory structure.
    """
    print("\n📁 Final AnnData directory structure:")
    print("=" * 60)

    base_path = Path("data/Anndata")
    if base_path.exists():
        print(f"📁 {base_path}/")

        for subdir in ["raw", "with_metadata", "filtered"]:
            subdir_path = base_path / subdir
            if subdir_path.exists():
                files = list(subdir_path.glob("*"))
                print(f"├── 📁 {subdir}/ ({len(files)} files)")

                # Show first few files as examples
                for i, file in enumerate(files[:3]):
                    prefix = "│   ├──" if i < min(2, len(files) - 1) else "│   └──"
                    print(f"{prefix} {file.name}")

                if len(files) > 3:
                    print(f"│   └── ... ({len(files)-3} more files)")

        # Show README
        readme_path = base_path / "README.md"
        if readme_path.exists():
            print("└── 📄 README.md")
    else:
        print("❌ Anndata directory not found!")

    print("=" * 60)


def verify_migration():
    """
    Verify that the migration was successful.
    """
    print("\n🔍 Verifying migration...")

    base_path = Path("data/Anndata")
    if not base_path.exists():
        print("❌ Migration failed: Anndata directory not found!")
        return False

    # Check each subdirectory
    subdirs = ["raw", "with_metadata", "filtered"]
    all_good = True

    for subdir in subdirs:
        subdir_path = base_path / subdir
        if subdir_path.exists():
            files = list(subdir_path.glob("*.h5ad"))
            print(f"✅ {subdir}/: {len(files)} .h5ad files")
        else:
            print(f"❌ {subdir}/: directory not found")
            all_good = False

    if all_good:
        print("✅ Migration verification successful!")
        return True
    else:
        print("❌ Migration verification failed!")
        return False


if __name__ == "__main__":
    verify_migration()
    show_final_structure()
    cleanup_old_directories()
    print("\n🎉 Cleanup completed!")
