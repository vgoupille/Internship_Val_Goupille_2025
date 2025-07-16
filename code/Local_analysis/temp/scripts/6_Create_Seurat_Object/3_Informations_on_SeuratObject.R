# Load required packages
library(Seurat)

# =============================================
# Data Loading
# =============================================

# Path to the Seurat object
pathSeuratObject <- "data/processed/Seurat_object/SeuratObject_All_Metadata.rds"
# pathSeuratObject <- "data/big_data/RDS_files/SeuratObject_All_Metadata.rds"
# pathSeuratObject <- "data/big_data/RDS_files/Seurat_Object_filtered-CDS_Metadata.rds"
# Check if file exists
if (!file.exists(pathSeuratObject)) {
  stop(paste("Error: The file", pathSeuratObject, "does not exist"))
}

# Load Seurat object with try-catch
tryCatch(
  {
    seurat_object <- readRDS(pathSeuratObject)
    cat("Seurat object loaded successfully\n")
  },
  error = function(e) {
    stop(paste("Error loading Seurat object:", e$message))
  }
)

# Check if loading was successful
if (is.null(seurat_object)) {
  stop("Error: Seurat object was not loaded correctly")
}

# Verify it's a Seurat object
if (!inherits(seurat_object, "Seurat")) {
  stop("Error: The loaded object is not a Seurat object")
}

# =============================================
# Basic Information about Seurat Object
# =============================================
# Display general information
cat("\nGeneral information about the Seurat object:\n")
print(seurat_object)

# Display dimensions
cat("\nObject dimensions:\n")
cat("Number of cells:", ncol(seurat_object), "\n")
cat("Number of genes:", nrow(seurat_object), "\n")


cat("Assays : ")
Assays(seurat_object)
cat("Layers : ")
Layers(seurat_object)

# =============================================
# Metadata Exploration
# =============================================
# Display first rows of metadata
cat("\nMetadata overview:\n")
print(head(seurat_object@meta.data))

# Display available columns
cat("\nAvailable columns in metadata:\n")
print(colnames(seurat_object@meta.data))

# =============================================
# Expression Layers Exploration
# =============================================
# Display names of different layers
cat("\nNames of different layers:\n")
print(names(seurat_object@assays$RNA@layers))

# =============================================
# Gene Diagnostics
# =============================================
cat("\nGene annotation information:\n")
cat("Number of features in Seurat object:", nrow(seurat_object), "\n")

# Display feature information if available
if ("RNA" %in% names(seurat_object@assays)) {
  # Print unique values in each annotation column
  cat("\nUnique values in feature column:\n")
  print(unique(seurat_object[["RNA"]][[]]$feature))
  cat("\nUnique values in seq_type column:\n")
  print(unique(seurat_object[["RNA"]][[]]$seq_type))
  cat("\nUnique values in class column:\n")
  print(unique(seurat_object[["RNA"]][[]]$class))
}


print("ncount RNA : ")
summary(seurat_object$nCount_RNA) # Statistiques de nCount_RNA
print("nfeature RNA : ")
summary(seurat_object$nFeature_RNA) # Statistiques de nFeature_RNA
