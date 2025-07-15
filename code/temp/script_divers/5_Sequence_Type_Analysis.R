# Load required packages
library(Seurat)
library(dplyr)
library(ggplot2)
library(tidyr)
library(scales)

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
# Calculate Sequence Type Proportions
# =============================================

# Get feature annotations
feature_annotations <- seurat_object[["RNA"]][[]]

# Calculate total counts per sequence type
sequence_counts <- data.frame(
    sequence_type = feature_annotations$seq_type,
    gene = rownames(feature_annotations)
) %>%
    group_by(sequence_type) %>%
    summarise(
        total_reads = sum(Matrix::colSums(GetAssayData(seurat_object, assay = "RNA", layer = "counts")[gene, ])),
        n_genes = n(),
        .groups = "drop"
    )

# Calculate proportions
sequence_counts <- sequence_counts %>%
    mutate(
        proportion_reads = total_reads / sum(total_reads) * 100,
        proportion_genes = n_genes / sum(n_genes) * 100,
        # Add labels for pie charts
        label_reads = paste0(sequence_type, "\n", round(proportion_reads, 1), "%"),
        label_genes = paste0(sequence_type, "\n", round(proportion_genes, 1), "%")
    )

# Print results
cat("\nSequence type proportions:\n")
print(sequence_counts)

# =============================================
# Create Plots
# =============================================

# Define a custom color palette
color_palette <- c(
    "chromosome" = "#1f77b4",
    "plasmid" = "#ff7f0e",
    "NA" = "#d62728"
)

# Bar plots
p_reads_bar <- ggplot(sequence_counts, aes(x = sequence_type, y = proportion_reads, fill = sequence_type)) +
    geom_bar(stat = "identity") +
    scale_fill_manual(values = color_palette) +
    theme_minimal() +
    labs(
        title = "Read Proportion by Sequence Type",
        x = "Sequence Type",
        y = "Proportion (%)",
        fill = "Sequence Type"
    ) +
    theme(axis.text.x = element_text(angle = 45, hjust = 1))

p_genes_bar <- ggplot(sequence_counts, aes(x = sequence_type, y = proportion_genes, fill = sequence_type)) +
    geom_bar(stat = "identity") +
    scale_fill_manual(values = color_palette) +
    theme_minimal() +
    labs(
        title = "Gene Proportion by Sequence Type",
        x = "Sequence Type",
        y = "Proportion (%)",
        fill = "Sequence Type"
    ) +
    theme(axis.text.x = element_text(angle = 45, hjust = 1))

# Pie charts
p_reads_pie <- ggplot(sequence_counts, aes(x = "", y = proportion_reads, fill = sequence_type)) +
    geom_bar(stat = "identity", width = 1) +
    coord_polar("y", start = 0) +
    scale_fill_manual(values = color_palette) +
    theme_minimal() +
    labs(
        title = "Read Distribution by Sequence Type",
        fill = "Sequence Type"
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

p_genes_pie <- ggplot(sequence_counts, aes(x = "", y = proportion_genes, fill = sequence_type)) +
    geom_bar(stat = "identity", width = 1) +
    coord_polar("y", start = 0) +
    scale_fill_manual(values = color_palette) +
    theme_minimal() +
    labs(
        title = "Gene Distribution by Sequence Type",
        fill = "Sequence Type"
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
pdf("results/sequence_type_proportions.pdf", width = 15, height = 12)
# Arrange plots in a 2x2 grid
gridExtra::grid.arrange(
    p_reads_bar, p_genes_bar,
    p_reads_pie, p_genes_pie,
    ncol = 2
)
dev.off()

# Save numerical results
write.csv(sequence_counts, "results/sequence_type_proportions.csv", row.names = FALSE)

# Create a simple summary by feature type
feature_summary <- feature_annotations %>%
    group_by(feature) %>%
    summarise(
        n_genes = n(),
        .groups = "drop"
    ) %>%
    mutate(
        proportion_genes = n_genes / sum(n_genes) * 100
    )

# Save feature summary
write.csv(feature_summary, "results/feature_type_summary.csv", row.names = FALSE)

# Print feature summary
cat("\nFeature type summary:\n")
print(feature_summary)

cat("\nResults have been saved in:\n")
cat("- results/sequence_type_proportions.csv\n")
cat("- results/feature_type_summary.csv\n")
cat("- results/sequence_type_proportions.pdf\n")
