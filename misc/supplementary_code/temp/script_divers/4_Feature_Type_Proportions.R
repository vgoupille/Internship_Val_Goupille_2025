# Load required packages
library(Seurat)
library(dplyr)
library(ggplot2)
library(tidyr)
library(scales) # For percentages

# =============================================
# Data Loading
# =============================================

# Path to the Seurat object
pathSeuratObject <- "data/big_data/RDS_files/SeuratObject_All_Metadata.rds"

# Check if file exists
if (!file.exists(pathSeuratObject)) {
    stop(paste("Error: The file", pathSeuratObject, "does not exist"))
}

# Load Seurat object
seurat_object <- readRDS(pathSeuratObject)

# =============================================
# Calculate Feature Type Proportions
# =============================================

# Get feature annotations
feature_annotations <- seurat_object[["RNA"]][[]]

# Calculate total counts per feature type
feature_counts <- data.frame(
    feature_type = feature_annotations$feature,
    gene = rownames(feature_annotations)
) %>%
    group_by(feature_type) %>%
    summarise(
        total_reads = sum(Matrix::colSums(GetAssayData(seurat_object, assay = "RNA", slot = "counts")[gene, ])),
        n_genes = n(),
        .groups = "drop"
    )

# Calculate proportions
feature_counts <- feature_counts %>%
    mutate(
        proportion_reads = total_reads / sum(total_reads) * 100,
        proportion_genes = n_genes / sum(n_genes) * 100,
        # Add labels for pie charts
        label_reads = paste0(feature_type, "\n", round(proportion_reads, 1), "%"),
        label_genes = paste0(feature_type, "\n", round(proportion_genes, 1), "%")
    )

# Print results
cat("\nFeature type proportions:\n")
print(feature_counts)

# =============================================
# Create Plots
# =============================================

# Define a custom color palette
color_palette <- c(
    "CDS" = "#1f77b4",
    "rRNA" = "#ff7f0e",
    "tRNA" = "#2ca02c",
    "NA" = "#d62728"
)

# Bar plots
p_reads_bar <- ggplot(feature_counts, aes(x = feature_type, y = proportion_reads, fill = feature_type)) +
    geom_bar(stat = "identity") +
    scale_fill_manual(values = color_palette) +
    theme_minimal() +
    labs(
        title = "Read Proportion by Feature Type",
        x = "Feature Type",
        y = "Proportion (%)",
        fill = "Feature Type"
    ) +
    theme(axis.text.x = element_text(angle = 45, hjust = 1))

p_genes_bar <- ggplot(feature_counts, aes(x = feature_type, y = proportion_genes, fill = feature_type)) +
    geom_bar(stat = "identity") +
    scale_fill_manual(values = color_palette) +
    theme_minimal() +
    labs(
        title = "Gene Proportion by Feature Type",
        x = "Feature Type",
        y = "Proportion (%)",
        fill = "Feature Type"
    ) +
    theme(axis.text.x = element_text(angle = 45, hjust = 1))

# Pie charts
p_reads_pie <- ggplot(feature_counts, aes(x = "", y = proportion_reads, fill = feature_type)) +
    geom_bar(stat = "identity", width = 1) +
    coord_polar("y", start = 0) +
    scale_fill_manual(values = color_palette) +
    theme_minimal() +
    labs(
        title = "Read Distribution by Feature Type",
        fill = "Feature Type"
    ) +
    theme(
        axis.text = element_blank(),
        axis.title = element_blank(),
        panel.grid = element_blank()
    ) +
    geom_text(aes(label = label_reads),
        position = position_stack(vjust = 0.5),
        color = "white",
        fontface = "bold"
    )

p_genes_pie <- ggplot(feature_counts, aes(x = "", y = proportion_genes, fill = feature_type)) +
    geom_bar(stat = "identity", width = 1) +
    coord_polar("y", start = 0) +
    scale_fill_manual(values = color_palette) +
    theme_minimal() +
    labs(
        title = "Gene Distribution by Feature Type",
        fill = "Feature Type"
    ) +
    theme(
        axis.text = element_blank(),
        axis.title = element_blank(),
        panel.grid = element_blank()
    ) +
    geom_text(aes(label = label_genes),
        position = position_stack(vjust = 0.5),
        color = "white",
        fontface = "bold"
    )

# Save all plots
pdf("results/feature_type_proportions.pdf", width = 15, height = 12)
# Arrange plots in a 2x2 grid
gridExtra::grid.arrange(
    p_reads_bar, p_genes_bar,
    p_reads_pie, p_genes_pie,
    ncol = 2
)
dev.off()

# Save numerical results
write.csv(feature_counts, "results/feature_type_proportions.csv", row.names = FALSE)

cat("\nResults have been saved in 'results/feature_type_proportions.csv'\n")
cat("Plots have been saved in 'results/feature_type_proportions.pdf'\n")
