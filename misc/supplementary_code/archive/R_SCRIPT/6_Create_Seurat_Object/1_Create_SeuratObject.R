# Load libraries
library(Seurat) # For single-cell RNA-seq data manipulation
library(Matrix) # For matrix manipulation



# _____Attention_____
# float error STARsolo UniqueAndMult-Uniform.mtx which is a float matrix that cause error in Seurat ReadMtx, ReadSARsolo, Read10X...

# https://github.com/alexdobin/STAR/issues/1397


# Define the data directory
data_dir <- "data/big_data/raw_starsolo"
# data_dir <- "/projects/microsplit/data/processed_data/STARsolo_result/merged_trimmed/merged/Output_DOL_microsplit_starsolo2/starsolo_output2/Solo.out/GeneFull/raw"
# Verify if the data directory exists
if (!dir.exists(data_dir)) {
  stop("The specified directory does not exist: ", data_dir)
}

# Construct the file paths
matrix_file <- file.path(data_dir, "UniqueAndMult-Uniform.mtx")
# awk '{if (NR>3) $3=int($3+0.5); print}' matrix.mtx | sed 's/float/integer/' > matrix_rounded.mtx
# change float to integer without rounding
output_matrix <- sub(".mtx$", "_integer.mtx", matrix_file) #
system(paste("sed '1,3s/float/integer/'", matrix_file, ">", output_matrix))

matrix_file <- output_matrix

features_file <- file.path(data_dir, "features.tsv")
barcodes_file <- file.path(data_dir, "barcodes.tsv")

# Verify if the necessary files exist
if (!file.exists(matrix_file)) stop("Missing file: ", matrix_file)
if (!file.exists(features_file)) stop("Missing file: ", features_file)
if (!file.exists(barcodes_file)) stop("Missing file: ", barcodes_file)

# Start timing the main process
cat("\nStarting data processing...\n")
processing_time <- system.time({
  # Read the data using Seurat's ReadMtx function
  cat("Reading data with ReadMtx...\n")
  expression_matrix <- ReadMtx(
    mtx = matrix_file,
    features = features_file,
    cells = barcodes_file
  )

  # Create Seurat object
  cat("Creating Seurat object...\n")
  seurat_object <- CreateSeuratObject(counts = expression_matrix)

  # Remove orig.ident column if it exists
  if ("orig.ident" %in% colnames(seurat_object@meta.data)) {
    seurat_object$orig.ident <- NULL
  }

  # Add barcode columns by extracting parts from the barcodes
  cat("Extracting barcode information...\n")
  barcodes <- colnames(expression_matrix)
  barcode_parts <- strsplit(barcodes, "_")

  # Extract rd1, rd2, and rd3 barcodes
  barcode_rd1 <- sapply(barcode_parts, function(x) x[length(x)])
  barcode_rd2 <- sapply(barcode_parts, function(x) x[2])
  barcode_rd3 <- sapply(barcode_parts, function(x) x[1])

  # Add barcode columns to Seurat object
  seurat_object$barcode.rd1 <- barcode_rd1
  seurat_object$barcode.rd2 <- barcode_rd2
  seurat_object$barcode.rd3 <- barcode_rd3

  # Print diagnostic information about barcode extraction
  cat("\nBarcode extraction information:\n")
  cat("Number of unique rd1 barcodes:", length(unique(barcode_rd1)), "\n")
  cat("Number of unique rd2 barcodes:", length(unique(barcode_rd2)), "\n")
  cat("Number of unique rd3 barcodes:", length(unique(barcode_rd3)), "\n")
  cat("\nFirst few barcodes:\n")
  print(head(data.frame(
    rd1 = barcode_rd1,
    rd2 = barcode_rd2,
    rd3 = barcode_rd3
  )))
})

# Print timing information
cat("\nProcessing time:\n")
cat("User time:", processing_time["user.self"], "seconds\n")
cat("System time:", processing_time["sys.self"], "seconds\n")
cat("Elapsed time:", processing_time["elapsed"], "seconds\n")

# Print a summary of the Seurat object
print(seurat_object)

# create directory if not exists
dir.create("data/big_data/RDS_files", showWarnings = FALSE, recursive = TRUE)
# Save the Seurat object to an RDS file
# output_file <- "data/processed/Seurat_object/SeuratObject_All.rds"
output_file <- "data/big_data/RDS_files/SeuratObject_All.rds"
saveRDS(seurat_object, file = output_file)

# Verify if the file was successfully created
if (file.exists(output_file)) {
  # Get file information
  file_info <- file.info(output_file)

  # Display file information
  cat("✓ File successfully created:", output_file, "\n")
  cat("File size:", round(file_info$size / 1024 / 1024, 2), "MB\n")
  cat("Creation date:", format(file_info$mtime, "%Y-%m-%d %H:%M:%S"), "\n")

  # Display Seurat object dimensions
  cat("\nSeurat object information:\n")
  cat("Number of cells:", ncol(seurat_object), "\n")
  cat("Number of genes:", nrow(seurat_object), "\n")
} else {
  cat("❌ Error: The file was not created.")
}
