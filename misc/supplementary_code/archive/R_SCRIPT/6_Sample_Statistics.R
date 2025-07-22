# Load required packages
library(Seurat)
library(dplyr)
library(ggplot2)
library(tidyr)
library(scales)
library(ggpubr)

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
# Calculate Sample Statistics
# =============================================

# Get metadata
metadata <- seurat_object@meta.data

# Calculate statistics per sample
sample_stats <- metadata %>%
    group_by(Sample_ID) %>%
    summarise(
        # nCount_RNA statistics
        mean_nCount = mean(nCount_RNA),
        median_nCount = median(nCount_RNA),
        sd_nCount = sd(nCount_RNA),
        min_nCount = min(nCount_RNA),
        max_nCount = max(nCount_RNA),
        total_nCount = sum(nCount_RNA),
        # nFeature_RNA statistics
        mean_nFeature = mean(nFeature_RNA),
        median_nFeature = median(nFeature_RNA),
        sd_nFeature = sd(nFeature_RNA),
        min_nFeature = min(nFeature_RNA),
        max_nFeature = max(nFeature_RNA),
        # Number of barcodes
        n_barcodes = n(),
        .groups = "drop"
    )

# Print summary statistics
cat("\nSample statistics summary:\n")
print(sample_stats)

# Save detailed statistics
write.csv(sample_stats, "results/sample_statistics.csv", row.names = FALSE)

# =============================================
# Create Plots
# =============================================

# Boxplot for nCount_RNA by Sample_ID
p_nCount_box <- ggplot(metadata, aes(x = Sample_ID, y = nCount_RNA, fill = Sample_ID)) +
    geom_boxplot() +
    theme_minimal() +
    labs(
        title = "Distribution of RNA Counts by Sample",
        x = "Sample ID",
        y = "Number of RNA Counts",
        fill = "Sample ID"
    ) +
    theme(
        axis.text.x = element_text(angle = 45, hjust = 1),
        legend.position = "none"
    ) +
    scale_y_log10() +
    annotation_logticks(sides = "l")

# Boxplot for nFeature_RNA by Sample_ID
p_nFeature_box <- ggplot(metadata, aes(x = Sample_ID, y = nFeature_RNA, fill = Sample_ID)) +
    geom_boxplot() +
    theme_minimal() +
    labs(
        title = "Distribution of RNA Features by Sample",
        x = "Sample ID",
        y = "Number of RNA Features",
        fill = "Sample ID"
    ) +
    theme(
        axis.text.x = element_text(angle = 45, hjust = 1),
        legend.position = "none"
    )

# Violin plots
p_nCount_violin <- ggplot(metadata, aes(x = Sample_ID, y = nCount_RNA, fill = Sample_ID)) +
    geom_violin() +
    theme_minimal() +
    labs(
        title = "Distribution of RNA Counts by Sample (Violin Plot)",
        x = "Sample ID",
        y = "Number of RNA Counts",
        fill = "Sample ID"
    ) +
    theme(
        axis.text.x = element_text(angle = 45, hjust = 1),
        legend.position = "none"
    ) +
    scale_y_log10() +
    annotation_logticks(sides = "l")

p_nFeature_violin <- ggplot(metadata, aes(x = Sample_ID, y = nFeature_RNA, fill = Sample_ID)) +
    geom_violin() +
    theme_minimal() +
    labs(
        title = "Distribution of RNA Features by Sample (Violin Plot)",
        x = "Sample ID",
        y = "Number of RNA Features",
        fill = "Sample ID"
    ) +
    theme(
        axis.text.x = element_text(angle = 45, hjust = 1),
        legend.position = "none"
    )

# Scatter plot of nCount_RNA vs nFeature_RNA, colored by Sample_ID
p_scatter <- ggplot(metadata, aes(x = nCount_RNA, y = nFeature_RNA, color = Sample_ID)) +
    geom_point(alpha = 0.5) +
    theme_minimal() +
    labs(
        title = "RNA Counts vs Features by Sample",
        x = "Number of RNA Counts",
        y = "Number of RNA Features",
        color = "Sample ID"
    ) +
    scale_x_log10() +
    annotation_logticks(sides = "bl")

# Save all plots
pdf("results/sample_statistics_plots.pdf", width = 15, height = 12)
# Arrange plots in a 2x2 grid
gridExtra::grid.arrange(
    p_nCount_box, p_nFeature_box,
    p_nCount_violin, p_nFeature_violin,
    ncol = 2
)
# Add scatter plot on a new page
print(p_scatter)
dev.off()

# Create a summary table for the README
summary_table <- sample_stats %>%
    select(
        Sample_ID,
        n_barcodes,
        mean_nCount,
        median_nCount,
        mean_nFeature,
        median_nFeature
    ) %>%
    mutate(
        mean_nCount = round(mean_nCount, 2),
        median_nCount = round(median_nCount, 2),
        mean_nFeature = round(mean_nFeature, 2),
        median_nFeature = round(median_nFeature, 2)
    )

# Save summary table
write.csv(summary_table, "results/sample_statistics_summary.csv", row.names = FALSE)

cat("\nResults have been saved in:\n")
cat("- results/sample_statistics.csv (detailed statistics)\n")
cat("- results/sample_statistics_summary.csv (summary table)\n")
cat("- results/sample_statistics_plots.pdf (visualizations)\n")
