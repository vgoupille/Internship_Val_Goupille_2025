# Data Organization Scripts

This directory contains utility scripts for organizing and managing the AnnData structure. These scripts were essential during the initial setup phase but are no longer required for the main analysis pipeline.

## 📁 Contents

### 🏗️ Structure Creation Scripts
- `create_anndata_structure.py` - Creates the organized AnnData directory structure
- `create_rds_structure.py` - Creates the RDS directory structure for R objects

### 🔄 Migration Scripts
- `migrate_existing_anndata.py` - Migrates existing AnnData files to the new organized structure
- `organize_csv_reports.py` - Organizes CSV reports into subdirectories by processing step
- `cleanup_old_anndata_dirs.py` - Cleans up old AnnData directories after migration

### 📊 Summary Scripts
- `anndata_organization_summary.py` - Displays complete summary of AnnData organization
- `csv_organization_summary.py` - Shows summary of CSV organization changes

## 🎯 Purpose

These scripts were used to:
1. **Restructure** the original flat AnnData organization into a hierarchical structure
2. **Migrate** existing files to the new organization
3. **Organize** CSV reports by processing step
4. **Verify** the successful migration and organization

## 📋 Current Status

- ✅ **Structure created** - All directories are properly organized
- ✅ **Files migrated** - All AnnData objects are in the correct locations
- ✅ **CSV organized** - Reports are sorted by processing step
- ✅ **Documentation complete** - README files with Mermaid diagrams created

## 🚀 Usage

These scripts are now **optional** and only needed if:
- You want to recreate the directory structure from scratch
- You need to migrate additional files to the organized structure
- You want to verify the current organization status

## 🔧 Execution

To run any of these scripts:

```bash
# From the project root directory
python code/A_supplementary/data_organization_scripts/[script_name].py
```

Example:
```bash
python code/A_supplementary/data_organization_scripts/anndata_organization_summary.py
```

---

**Note:** These scripts were moved to A_supplementary because they are no longer essential for the main analysis pipeline. The data structure is now stable and organized.

**Author:** Valentin Goupille  
**Date:** 2025-07-18  
**Project:** Division of Labor - Single Cell Analysis 