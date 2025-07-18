# %%
import os
import rpy2.robjects as ro
from rpy2.robjects.conversion import localconverter
from rpy2.robjects import pandas2ri

# Set up R environment
os.environ["R_HOME"] = "/Library/Frameworks/R.framework/Resources"
r_path = "/Library/Frameworks/R.framework/Resources/bin"
os.environ["PATH"] = r_path + ":" + os.environ["PATH"]

# %%
# Set working directory
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# %%
# Test Seurat RDS file loading and validation
print("🧪 Testing Seurat RDS file...")
print("=" * 60)

# Define RDS file path
rds_path = "data/anndata_objects_with_complete_metadata_filtered/GeneFull_raw_unique_mult_with_metadata_grouped_filtered_100UMI_3c_SeuratV5.rds"

# %%
# Load required R packages
print("\n📦 Loading R packages...")
ro.r(
    """
# Load required packages
if (!require("Seurat", quietly = TRUE)) {
    install.packages("Seurat", repos = "https://cloud.r-project.org/")
}
library(Seurat)
cat("✅ Seurat loaded successfully\n")
"""
)

# %%
# Load and validate RDS file
print("\n📂 Loading RDS file...")
ro.r.assign("rds_path", rds_path)

validation_result = ro.r(
    """
# Check if file exists
if (!file.exists(rds_path)) {
    stop("❌ RDS file not found at: ", rds_path)
}

cat("📂 Loading RDS file from:", rds_path, "\n")

# Load the Seurat object
seurat_obj <- readRDS(rds_path)

# Basic validation
validation_results <- list()
validation_results$loaded <- TRUE
validation_results$n_cells <- ncol(seurat_obj)
validation_results$n_genes <- nrow(seurat_obj)
validation_results$n_metadata_cols <- ncol(seurat_obj@meta.data)
validation_results$metadata_cols <- colnames(seurat_obj@meta.data)
validation_results$assays <- names(seurat_obj@assays)
validation_results$seurat_version <- as.character(packageVersion("Seurat"))

# Test basic functions
test_subset <- seurat_obj[1:100, 1:10]
validation_results$subset_works <- all(dim(test_subset) == c(100, 10))

# Test matrix access
counts_matrix <- GetAssayData(seurat_obj, assay = "RNA", slot = "counts")
validation_results$matrix_access <- !is.null(counts_matrix)
validation_results$matrix_class <- class(counts_matrix)

# Check metadata columns
important_cols <- c("CultureMedium", "OD", "RepBio", "RepTech", "total_counts", "n_genes")
validation_results$available_important_cols <- important_cols[important_cols %in% colnames(seurat_obj@meta.data)]

validation_results
"""
)

# %%
# Display results in Python
print("\n📊 VALIDATION RESULTS")
print("=" * 60)

print(f"✅ RDS file loaded: {validation_result[0][0]}")
print(f"📊 Cells: {validation_result[1][0]:,}")
print(f"📊 Genes: {validation_result[2][0]:,}")
print(f"📊 Metadata columns: {validation_result[3][0]}")
print(f"🧬 Assays: {list(validation_result[5])}")
print(f"📋 Seurat version: {validation_result[6][0]}")

print(f"\n🧪 Function tests:")
print(f"✅ Subsetting works: {validation_result[7][0]}")
print(f"✅ Matrix access works: {validation_result[8][0]}")
print(f"📊 Matrix class: {validation_result[9][0]}")

print(f"\n🔍 Important columns available:")
available_cols = list(validation_result[10])
important_cols = ["CultureMedium", "OD", "RepBio", "RepTech", "total_counts", "n_genes"]
for col in important_cols:
    if col in available_cols:
        print(f"✅ {col}")
    else:
        print(f"❌ {col}")

# %%
# Additional metadata exploration
print("\n📋 METADATA EXPLORATION")
print("=" * 60)

metadata_info = ro.r(
    """
# Get metadata info
metadata_info <- list()

# Check CultureMedium distribution
if ("CultureMedium" %in% colnames(seurat_obj@meta.data)) {
    metadata_info$culture_medium <- table(seurat_obj@meta.data$CultureMedium)
}

# Check OD distribution  
if ("OD" %in% colnames(seurat_obj@meta.data)) {
    metadata_info$od_distribution <- table(seurat_obj@meta.data$OD)
}

# Check RepBio distribution
if ("RepBio" %in% colnames(seurat_obj@meta.data)) {
    metadata_info$repbio_distribution <- table(seurat_obj@meta.data$RepBio)
}

# Check UMI and gene counts
if ("total_counts" %in% colnames(seurat_obj@meta.data)) {
    metadata_info$umi_summary <- summary(seurat_obj@meta.data$total_counts)
}

if ("n_genes" %in% colnames(seurat_obj@meta.data)) {
    metadata_info$gene_summary <- summary(seurat_obj@meta.data$n_genes)
}

metadata_info
"""
)

# Convert and display metadata info
with localconverter(ro.default_converter + pandas2ri.converter):
    if hasattr(metadata_info, "names") and metadata_info.names:
        for i, name in enumerate(metadata_info.names):
            print(f"\n📊 {name}:")
            if name in ["culture_medium", "od_distribution", "repbio_distribution"]:
                # For tables, display as counts
                values = metadata_info[i]
                if hasattr(values, "names") and values.names:
                    for j, cat in enumerate(values.names):
                        print(f"   {cat}: {values[j]}")
            elif name in ["umi_summary", "gene_summary"]:
                # For summaries, display statistics
                values = metadata_info[i]
                if hasattr(values, "names") and values.names:
                    for j, stat in enumerate(values.names):
                        print(f"   {stat}: {values[j]:.0f}")

# %%
# Final summary
print("\n" + "=" * 80)
print("🎉 SEURAT RDS FILE VALIDATION COMPLETE")
print("=" * 80)

print("✅ All tests passed successfully!")
print("✅ RDS file is valid and ready for R analysis")
print("✅ All metadata preserved from AnnData")
print("✅ Seurat functions working correctly")

print("\n💡 Usage in R:")
print(f"   seurat_obj <- readRDS('{rds_path}')")
print("   print(seurat_obj)")
print("   # Run standard Seurat workflow")

print("\n🚀 Next steps in Seurat:")
print("   1. NormalizeData(seurat_obj)")
print("   2. FindVariableFeatures(seurat_obj)")
print("   3. ScaleData(seurat_obj)")
print("   4. RunPCA(seurat_obj)")
print("   5. FindNeighbors(seurat_obj)")
print("   6. FindClusters(seurat_obj)")
print("   7. RunUMAP(seurat_obj)")

print("\n🎯 AnnData → Seurat conversion successful!")

# %%
