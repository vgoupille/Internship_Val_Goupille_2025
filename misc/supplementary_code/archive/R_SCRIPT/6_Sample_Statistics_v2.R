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
    group_by(Sample_ID, Rep_bio, Rep_tech, OD_timepoint) %>%
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
write.csv(sample_stats, "results/sample_statistics_v2.csv", row.names = FALSE)

# =============================================
# Create Plots with Facets
# =============================================

# Create a combined replicate column for x-axis
metadata <- metadata %>%
    mutate(replicate = paste("Rep", Rep_bio, Rep_tech, sep = "_"))

# Function to create faceted plots
create_faceted_plot <- function(data, y_var, title, y_label) {
    # Boxplot
    p_box <- ggplot(data, aes(x = replicate, y = .data[[y_var]], fill = replicate)) +
        geom_boxplot() +
        facet_grid(Culture_medium ~ OD_timepoint, scales = "free_x") +
        theme_minimal() +
        labs(
            title = paste(title, "by Replicate (Faceted by Culture Medium and Timepoint)"),
            x = "Replicate (RepBio_RepTech)",
            y = y_label,
            fill = "Replicate"
        ) +
        theme(
            axis.text.x = element_text(angle = 45, hjust = 1, size = 8),
            legend.position = "none",
            strip.text = element_text(size = 10),
            panel.spacing = unit(1, "lines")
        )

    if (y_var == "nCount_RNA") {
        p_box <- p_box + scale_y_log10() + annotation_logticks(sides = "l")
    }

    # Violin plot
    p_violin <- ggplot(data, aes(x = replicate, y = .data[[y_var]], fill = replicate)) +
        geom_violin() +
        facet_grid(Culture_medium ~ OD_timepoint, scales = "free_x") +
        theme_minimal() +
        labs(
            title = paste(title, "Distribution (Violin Plot) by Culture Medium and Timepoint"),
            x = "Replicate (RepBio_RepTech)",
            y = y_label,
            fill = "Replicate"
        ) +
        theme(
            axis.text.x = element_text(angle = 45, hjust = 1, size = 8),
            legend.position = "none",
            strip.text = element_text(size = 10),
            panel.spacing = unit(1, "lines")
        )

    if (y_var == "nCount_RNA") {
        p_violin <- p_violin + scale_y_log10() + annotation_logticks(sides = "l")
    }

    return(list(box = p_box, violin = p_violin))
}

# Create faceted plots for nCount_RNA
nCount_plots <- create_faceted_plot(
    metadata,
    "nCount_RNA",
    "RNA Counts",
    "Number of RNA Counts"
)

# Create faceted plots for nFeature_RNA
nFeature_plots <- create_faceted_plot(
    metadata,
    "nFeature_RNA",
    "RNA Features",
    "Number of RNA Features"
)

# Create faceted scatter plot
p_scatter <- ggplot(metadata, aes(x = nCount_RNA, y = nFeature_RNA, color = replicate)) +
    geom_point(alpha = 0.5) +
    facet_grid(Culture_medium ~ OD_timepoint) +
    theme_minimal() +
    labs(
        title = "RNA Counts vs Features by Culture Medium and Timepoint",
        x = "Number of RNA Counts",
        y = "Number of RNA Features",
        color = "Replicate"
    ) +
    scale_x_log10() +
    annotation_logticks(sides = "bl") +
    theme(
        strip.text = element_text(size = 10),
        panel.spacing = unit(1, "lines")
    )

# Save all plots with adjusted dimensions for better readability
pdf("results/sample_statistics_plots_v2.pdf", width = 25, height = 20)
# Arrange plots
print(nCount_plots$box)
print(nCount_plots$violin)
print(nFeature_plots$box)
print(nFeature_plots$violin)
print(p_scatter)
dev.off()

# Create summary tables by different groupings
summary_by_rep_bio <- sample_stats %>%
    group_by(Rep_bio, OD_timepoint) %>%
    summarise(
        mean_nCount = mean(mean_nCount),
        median_nCount = median(median_nCount),
        mean_nFeature = mean(mean_nFeature),
        median_nFeature = median(median_nFeature),
        total_barcodes = sum(n_barcodes),
        .groups = "drop"
    ) %>%
    mutate(
        mean_nCount = round(mean_nCount, 2),
        median_nCount = round(median_nCount, 2),
        mean_nFeature = round(mean_nFeature, 2),
        median_nFeature = round(median_nFeature, 2)
    )

summary_by_timepoint <- sample_stats %>%
    group_by(OD_timepoint) %>%
    summarise(
        mean_nCount = mean(mean_nCount),
        median_nCount = median(median_nCount),
        mean_nFeature = mean(mean_nFeature),
        median_nFeature = median(median_nFeature),
        total_barcodes = sum(n_barcodes),
        .groups = "drop"
    ) %>%
    mutate(
        mean_nCount = round(mean_nCount, 2),
        median_nCount = round(median_nCount, 2),
        mean_nFeature = round(mean_nFeature, 2),
        median_nFeature = round(median_nFeature, 2)
    )

# Save summary tables
write.csv(summary_by_rep_bio, "results/sample_statistics_by_rep_bio.csv", row.names = FALSE)
write.csv(summary_by_timepoint, "results/sample_statistics_by_timepoint.csv", row.names = FALSE)

cat("\nResults have been saved in:\n")
cat("- results/sample_statistics_v2.csv (detailed statistics)\n")
cat("- results/sample_statistics_by_rep_bio.csv (summary by replicate and timepoint)\n")
cat("- results/sample_statistics_by_timepoint.csv (summary by timepoint)\n")
cat("- results/sample_statistics_plots_v2.pdf (faceted visualizations)\n")
