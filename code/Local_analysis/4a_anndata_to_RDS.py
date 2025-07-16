# %%
import os
import sys
import numpy as np
import pandas as pd
import anndata as ad
import scipy.sparse

# Set up R environment
os.environ["R_HOME"] = "/Library/Frameworks/R.framework/Resources"
r_path = "/Library/Frameworks/R.framework/Resources/bin"
os.environ["PATH"] = r_path + ":" + os.environ["PATH"]

# Import rpy2 for R magic
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri, numpy2ri
from rpy2.robjects.conversion import localconverter
import rpy2.robjects.packages as rpackages

# %%
# Set working directory
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# %%
# Load the filtered data from 3c
print("📂 Loading filtered data from 3c...")
INPUT_PATH = "data/anndata_objects_with_complete_metadata_filtered"
INPUT_FILE = "GeneFull_raw_unique_mult_with_metadata_grouped_filtered_100UMI_3c.h5ad"

# Load the AnnData object
adata_final = ad.read_h5ad(os.path.join(INPUT_PATH, INPUT_FILE))

print(f"📊 Loaded dataset: {adata_final.n_obs:,} cells × {adata_final.n_vars:,} genes")
print(f"🔢 Available obs columns: {list(adata_final.obs.columns)}")
print(f"🔢 Available var columns: {list(adata_final.var.columns)}")

# %%
# Install and load required R packages
print("\n📦 Setting up R packages...")

ro.r(
    """
# Function to install package if not already installed
install_if_missing <- function(package_name) {
    if (!require(package_name, character.only = TRUE, quietly = TRUE)) {
        cat("Installing", package_name, "...\n")
        if (package_name %in% c("Seurat", "SeuratObject")) {
            install.packages(package_name, repos = "https://cloud.r-project.org/")
        } else if (package_name == "anndata") {
            install.packages("reticulate", repos = "https://cloud.r-project.org/")
            reticulate::py_install("anndata")
        }
        library(package_name, character.only = TRUE)
    }
}

# Install required packages
install_if_missing("Seurat")
install_if_missing("SeuratObject")
install_if_missing("Matrix")
install_if_missing("reticulate")

# Load packages
library(Seurat)
library(SeuratObject)  
library(Matrix)
library(reticulate)

cat("✅ R packages loaded successfully\n")
"""
)

# %%
# Convert AnnData to Seurat using R magic
print("\n🔄 Converting AnnData to Seurat V5...")

# Prepare data for R
print("📋 Preparing data for R conversion...")

# Get counts matrix (make sure it's in the right format)
if scipy.sparse.issparse(adata_final.X):
    counts_matrix = adata_final.X.toarray()
else:
    counts_matrix = adata_final.X

# Ensure counts are integers
counts_matrix = counts_matrix.astype(int)

# Get metadata
metadata = adata_final.obs.copy()
gene_names = adata_final.var_names.tolist()
cell_names = adata_final.obs_names.tolist()

print(f"📊 Matrix shape: {counts_matrix.shape}")
print(f"📊 Metadata shape: {metadata.shape}")

# %%
# Convert to R and create Seurat object
print("🔄 Creating Seurat object in R...")

# Transfer data to R using the new converter approach
with localconverter(ro.default_converter + pandas2ri.converter):
    r_metadata = ro.conversion.py2rpy(metadata)

with localconverter(ro.default_converter + numpy2ri.converter):
    r_counts = ro.conversion.py2rpy(counts_matrix.T)  # Transpose for R (genes x cells)

# Set row and column names in R
ro.r.assign("counts_matrix", r_counts)
ro.r.assign("metadata_df", r_metadata)
ro.r.assign("gene_names", ro.StrVector(gene_names))
ro.r.assign("cell_names", ro.StrVector(cell_names))

# Create Seurat object in R
ro.r(
    """
# Set dimensions and names
rownames(counts_matrix) <- gene_names
colnames(counts_matrix) <- cell_names
rownames(metadata_df) <- cell_names

# Convert to sparse matrix for efficiency
counts_sparse <- Matrix::Matrix(counts_matrix, sparse = TRUE)

# Create Seurat object
cat("Creating Seurat object...\n")
seurat_obj <- CreateSeuratObject(
    counts = counts_sparse,
    meta.data = metadata_df,
    project = "BacSC_3c_filtered"
)

# Print basic information
cat("✅ Seurat object created successfully\n")
print(seurat_obj)

# Check version
cat("Seurat version:", as.character(packageVersion("Seurat")), "\n")
"""
)

# %%
# Save as RDS file
print("\n💾 Saving Seurat object as RDS...")

OUTPUT_PATH = "data/anndata_objects_with_complete_metadata_filtered"
OUTPUT_FILE = (
    "GeneFull_raw_unique_mult_with_metadata_grouped_filtered_100UMI_3c_SeuratV5.rds"
)

os.makedirs(OUTPUT_PATH, exist_ok=True)
output_path = os.path.join(OUTPUT_PATH, OUTPUT_FILE)

# Save in R
ro.r.assign("output_path", output_path)
ro.r(
    """
# Save Seurat object as RDS
cat("Saving to:", output_path, "\n")
saveRDS(seurat_obj, file = output_path)

# Verify file was created
if (file.exists(output_path)) {
    cat("✅ RDS file saved successfully\n")
    cat("📊 File size:", file.size(output_path), "bytes\n")
} else {
    cat("❌ Error: RDS file was not created\n")
}
"""
)

# %%
# Verify the saved RDS file
print("\n🔍 Verifying saved RDS file...")

ro.r(
    """
# Test loading the saved RDS file
tryCatch({
    test_obj <- readRDS(output_path)
    cat("✅ RDS file verification successful\n")
    cat("📊 Loaded object dimensions:", dim(test_obj), "\n")
    cat("📊 Object class:", class(test_obj), "\n")
    
    # Show basic info
    cat("\n📋 Basic object information:\n")
    print(test_obj)
    
    # Show available assays
    cat("\n🧬 Available assays:", names(test_obj@assays), "\n")
    
    # Show metadata columns
    cat("\n📊 Metadata columns:", colnames(test_obj@meta.data), "\n")
    
}, error = function(e) {
    cat("❌ Error verifying RDS file:", e$message, "\n")
})
"""
)

# %%
# Final summary
print("\n" + "=" * 80)
print("📊 ANNDATA TO SEURAT V5 CONVERSION SUMMARY")
print("=" * 80)

print(f"✅ Input AnnData: {adata_final.n_obs:,} cells × {adata_final.n_vars:,} genes")
print(f"✅ Output RDS file: {output_path}")
print(f"✅ Seurat version: R packages loaded and used")

if os.path.exists(output_path):
    file_size = os.path.getsize(output_path)
    print(f"✅ File size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
    print("✅ Conversion completed successfully!")
else:
    print("❌ Error: Output file was not created")

print("\n💡 Usage in R:")
print(f"   seurat_obj <- readRDS('{output_path}')")
print("   print(seurat_obj)")
print("   # Available assays: RNA")
print("   # Available metadata: all columns from original AnnData")

print("\n🎉 3d AnnData to Seurat V5 conversion completed!")

# %%
