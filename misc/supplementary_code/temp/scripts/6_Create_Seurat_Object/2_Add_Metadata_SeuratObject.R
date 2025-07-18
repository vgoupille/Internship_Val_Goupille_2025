# Load libraries
library(Seurat)
library(readxl)

# Read the Seurat object
# input_file <- "data/processed/Seurat_object/SeuratObject_All.rds"
input_file <- "data/big_data/RDS_files/SeuratObject_All.rds"
seurat_object <- readRDS(input_file)

# Read barcode QC file for round 1
barcode_qc_file_rd1 <- "data/processed_data/metadata_DOL_Exp1/barqc/barcode_rd1_barqc.csv"
barcode_qc_rd1 <- read.csv(barcode_qc_file_rd1, stringsAsFactors = FALSE)

# Print diagnostic information about barcode QC file
cat("\nBarcode QC file information for round 1:\n")
cat("Number of barcodes in QC file:", nrow(barcode_qc_rd1), "\n")
cat("First few rows of barcode QC file:\n")
print(head(barcode_qc_rd1))

# Match barcodes and add Well_loc_rd1
matching_wells_rd1 <- match(seurat_object$barcode.rd1, barcode_qc_rd1$Barcode)
seurat_object$Well_loc_rd1 <- barcode_qc_rd1$Well[matching_wells_rd1]

# Print diagnostic information about the matching
cat("\nWell location matching information for round 1:\n")
cat("Number of matched cells:", sum(!is.na(matching_wells_rd1)), "\n")
cat("Number of unmatched cells:", sum(is.na(matching_wells_rd1)), "\n")
cat("First few Well_loc_rd1 values:\n")
print(head(seurat_object$Well_loc_rd1))

# Read barcode QC file for round 2
barcode_qc_file <- "data/processed_data/metadata_DOL_Exp1/barqc/barcode_rd2_barqc.csv"
barcode_qc_rd2 <- read.csv(barcode_qc_file, stringsAsFactors = FALSE)

# Print diagnostic information about barcode QC file
cat("\nBarcode QC file information for round 2:\n")
cat("Number of barcodes in QC file:", nrow(barcode_qc_rd2), "\n")
cat("First few rows of barcode QC file:\n")
print(head(barcode_qc_rd2))

# Match barcodes and add Well_loc_rd2
matching_wells_rd2 <- match(seurat_object$barcode.rd2, barcode_qc_rd2$Barcode)
seurat_object$Well_loc_rd2 <- barcode_qc_rd2$Well[matching_wells_rd2]

# Print diagnostic information about the matching
cat("\nWell location matching information for round 2:\n")
cat("Number of matched cells:", sum(!is.na(matching_wells_rd2)), "\n")
cat("Number of unmatched cells:", sum(is.na(matching_wells_rd2)), "\n")
cat("First few Well_loc_rd2 values:\n")
print(head(seurat_object$Well_loc_rd2))

# Read barcode QC file for round 3
barcode_qc_file_rd3 <- "data/processed_data/metadata_DOL_Exp1/barqc/barcode_rd3_barqc.csv"
barcode_qc_rd3 <- read.csv(barcode_qc_file_rd3, stringsAsFactors = FALSE)

# Print diagnostic information about barcode QC file
cat("\nBarcode QC file information for round 3:\n")
cat("Number of barcodes in QC file:", nrow(barcode_qc_rd3), "\n")
cat("First few rows of barcode QC file:\n")
print(head(barcode_qc_rd3))

# Match barcodes and add Well_loc_rd3
matching_wells_rd3 <- match(seurat_object$barcode.rd3, barcode_qc_rd3$Barcode)
seurat_object$Well_loc_rd3 <- barcode_qc_rd3$Well[matching_wells_rd3]

# Print diagnostic information about the matching
cat("\nWell location matching information for round 3:\n")
cat("Number of matched cells:", sum(!is.na(matching_wells_rd3)), "\n")
cat("Number of unmatched cells:", sum(is.na(matching_wells_rd3)), "\n")
cat("First few Well_loc_rd3 values:\n")
print(head(seurat_object$Well_loc_rd3))

# Add metadata from Excel file
metadata_file <- "data/processed_data/metadata_DOL_Exp1/metadata_DOL_Exp1_complete.xlsx"
metadata <- read_excel(metadata_file)

# Print column names of metadata
cat("\nColumns in metadata file:\n")
print(colnames(metadata))

# Print some diagnostic information
cat("\nDiagnostic information:\n")
cat("Number of cells in Seurat object:", length(seurat_object$barcode.rd1), "\n")
cat("Number of rows in metadata:", nrow(metadata), "\n")

# Print some example values to compare
cat("\nFirst few barcode.rd1 values:\n")
head(seurat_object$barcode.rd1)
cat("\nFirst few Extracted_Sequence_rd1 values:\n")
head(metadata$Extracted_Sequence_rd1)

# Match metadata with Seurat object based on barcode.rd1 and Extracted_Sequence.rd1
matching_cells <- match(seurat_object$barcode.rd1, metadata$Extracted_Sequence_rd1)

# Count number of matches
cat("\nNumber of matched cells:", sum(!is.na(matching_cells)), "\n")
cat("Number of unmatched cells:", sum(is.na(matching_cells)), "\n")

# Add metadata columns to Seurat object
seurat_object$Sample_ID <- metadata$Sample_ID[matching_cells]
seurat_object$Culture_medium <- metadata$Culture_medium[matching_cells]
seurat_object$Rep_bio <- metadata$Rep_bio[matching_cells]
seurat_object$Rep_tech <- metadata$Rep_tech[matching_cells]
seurat_object$OD_timepoint <- metadata$OD_timepoint[matching_cells]
seurat_object$OD_theoric <- metadata$OD_theoric[matching_cells]
seurat_object$OD_measured <- metadata$OD_measured[matching_cells]
seurat_object$Condition <- metadata$Condition[matching_cells]

# Add gene annotation from TSV file
annotation_file <- "data/raw_data/genome_annotation/other/extracted_features.tsv"
gene_annotation <- read.delim(annotation_file,
  sep = "\t",
  header = TRUE,
  stringsAsFactors = FALSE,
  quote = "", # Désactive l'interprétation des guillemets
  na.strings = c("NA", "")
) # Gère les valeurs manquantes

# Create a mapping between locus_tag and gene names
# Replace underscores with hyphens in locus_tag to match Seurat object format
gene_annotation$feature_id <- gsub("_", "-", gene_annotation$locus_tag)

# Create a comprehensive mapping that includes both locus tags and symbols
# First, create a mapping for locus tags
locus_mapping <- match(rownames(seurat_object), gene_annotation$feature_id)

# Then, create a mapping for symbols (only for non-empty symbols)
symbol_annotation <- gene_annotation[!is.na(gene_annotation$symbol) & gene_annotation$symbol != "", ]
symbol_mapping <- match(rownames(seurat_object), symbol_annotation$symbol)

# Combine the mappings, prioritizing locus tag matches
matching_genes <- locus_mapping
# For genes that weren't matched by locus tag, use symbol match if available
unmatched_genes <- is.na(matching_genes)
if (any(unmatched_genes)) {
  symbol_matches <- symbol_mapping[unmatched_genes]
  # Convert symbol matches back to original annotation indices
  symbol_indices <- symbol_annotation$feature_id[symbol_matches]
  symbol_to_original <- match(symbol_indices, gene_annotation$feature_id)
  matching_genes[unmatched_genes] <- symbol_to_original
}

# Create a data frame with all annotations
feature_metadata <- data.frame(
  seq_type = gene_annotation$seq_type[matching_genes],
  feature = gene_annotation$feature[matching_genes],
  class = gene_annotation$class[matching_genes],
  product_accession = gene_annotation$product_accession[matching_genes],
  name = gene_annotation$name[matching_genes],
  symbol = gene_annotation$symbol[matching_genes],
  locus_tag = gene_annotation$locus_tag[matching_genes],
  row.names = rownames(seurat_object)
)

# Add feature metadata to Seurat object
seurat_object[["RNA"]] <- AddMetaData(
  object = seurat_object[["RNA"]],
  metadata = feature_metadata
)

# Print some diagnostic information about the gene matching
cat("\nGene annotation information:\n")
cat("Number of features in Seurat object:", nrow(seurat_object), "\n")
cat("Number of genes in annotation file:", nrow(gene_annotation), "\n")
cat("Number of matched genes:", sum(!is.na(matching_genes)), "\n")
cat("Number of unmatched genes:", sum(is.na(matching_genes)), "\n")

# Check specific genes like katG
katg_index <- which(rownames(seurat_object) == "katG")
if (length(katg_index) > 0) {
  cat("\nkatG gene information:\n")
  cat("katG found at index:", katg_index, "\n")
  cat("katG symbol in annotation:", gene_annotation$symbol[matching_genes[katg_index]], "\n")
  cat("katG locus tag in annotation:", gene_annotation$locus_tag[matching_genes[katg_index]], "\n")
  cat("katG name in annotation:", gene_annotation$name[matching_genes[katg_index]], "\n")
}

# Check other known genes with symbols
known_symbols <- c("recC", "recB", "recD", "mmsB", "leuA", "fur", "recN", "grpE", "dnaK", "dnaJ")
for (symbol in known_symbols) {
  symbol_index <- which(rownames(seurat_object) == symbol)
  if (length(symbol_index) > 0) {
    cat("\n", symbol, " gene information:\n")
    cat(symbol, " found at index:", symbol_index, "\n")
    cat(symbol, " symbol in annotation:", gene_annotation$symbol[matching_genes[symbol_index]], "\n")
    cat(symbol, " locus tag in annotation:", gene_annotation$locus_tag[matching_genes[symbol_index]], "\n")
  }
}

# Print unique values in each annotation column
cat("\nUnique values in feature column:\n")
print(unique(seurat_object[["RNA"]][[]]$feature))
cat("\nUnique values in seq_type column:\n")
print(unique(seurat_object[["RNA"]][[]]$seq_type))
cat("\nUnique values in class column:\n")
print(unique(seurat_object[["RNA"]][[]]$class))

# Count number of each feature type
cat("\nCount of each feature type:\n")
print(table(seurat_object[["RNA"]][[]]$feature))

# Save updated Seurat object with metadata in a new file
# output_file <- "data/processed/Seurat_object/SeuratObject_All_Metadata.rds"
output_file <- "data/big_data/RDS_files/SeuratObject_All_Metadata.rds"
saveRDS(seurat_object, file = output_file)

# Verify if the file was successfully created
if (file.exists(output_file)) {
  # Get file information
  file_info <- file.info(output_file)

  # Display file information
  cat("✓ Seurat object with metadata successfully saved:", output_file, "\n")
  cat("File size:", round(file_info$size / 1024 / 1024, 2), "MB\n")
  cat("Creation date:", format(file_info$mtime, "%Y-%m-%d %H:%M:%S"), "\n")

  # Display Seurat object dimensions
  cat("\nSeurat object with metadata information:\n")
  cat("Number of cells:", ncol(seurat_object), "\n")
  cat("Number of genes:", nrow(seurat_object), "\n")
} else {
  cat("❌ Error: The file was not created.")
}

# Print the duplicated features
if (any(duplicated(rownames(seurat_object)))) {
  cat("\nDuplicated features found:\n")
  duplicated_features <- rownames(seurat_object)[duplicated(rownames(seurat_object))]
  print(duplicated_features)
} else {
  cat("\nNo duplicated features found.\n")
}



str(seurat_object)



print(colnames(seurat_object[["RNA"]][[]]))



# Print summary of the Seurat object structure
print(str(seurat_object))

assay_obj <- seurat_object[["RNA"]]
print(assay_obj)

# Print the first few rows of gene metadata
head(assay_obj@meta.data)

# Accéder à l'assay par défaut de l'objet Seurat
head(seurat_object@assays$RNA@meta.data)
# list colnames of the assay
colnames(seurat_object@assays$RNA@meta.data)

# list columns of the metadata
colnames(seurat_object@meta.data)
