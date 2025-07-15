# Load required libraries
library(shiny)
library(Seurat)
library(tidyverse)
library(ggplot2)
library(viridis)
library(plotly)
library(gridExtra)
library(RColorBrewer)

#' Debug function to print object information
#' @param msg Message to display
#' @param obj Object to inspect
print_debug <- function(msg, obj = NULL) {
    cat("\n[DEBUG] ", msg, "\n")
    if (!is.null(obj)) {
        print(str(obj))
    }
}

#' Filter Seurat object based on metadata columns
#' @param seurat_obj Seurat object to filter
#' @param filter_by_columns List of metadata columns for filtering
#' @param value_column Column to use for threshold filtering
#' @param keep_percentage Percentage of cells to keep (between 0 and 100)
#' @param lower_tail Filter lower values (TRUE) or upper values (FALSE)
#' @param debug Enable debug mode (default: FALSE)
#' @return List containing filtered Seurat object, plots, and statistics
filter_seurat_by_metadata <- function(seurat_obj,
                                      filter_by_columns,
                                      value_column,
                                      keep_percentage = 75,
                                      lower_tail = FALSE,
                                      debug = TRUE) {
    # Input validation with debug info
    print_debug("Starting function with parameters:", list(
        filter_by_columns = filter_by_columns,
        value_column = value_column,
        keep_percentage = keep_percentage,
        lower_tail = lower_tail
    ))

    if (!inherits(seurat_obj, "Seurat")) {
        print_debug("Object class:", class(seurat_obj))
        stop("The provided object is not a valid Seurat object")
    }

    print_debug("Metadata columns available:", colnames(seurat_obj@meta.data))

    if (!value_column %in% colnames(seurat_obj@meta.data)) {
        stop(sprintf("Error: Column '%s' not found in metadata", value_column))
    }

    if (!all(filter_by_columns %in% colnames(seurat_obj@meta.data))) {
        missing_cols <- filter_by_columns[!filter_by_columns %in% colnames(seurat_obj@meta.data)]
        stop(sprintf(
            "Error: The following columns do not exist: %s",
            paste(missing_cols, collapse = ", ")
        ))
    }

    if (keep_percentage <= 0 || keep_percentage >= 100) {
        stop("Error: Percentage must be between 0 and 100")
    }

    # Calculate threshold percentile
    threshold_percentile <- if (lower_tail) {
        (100 - keep_percentage) / 100
    } else {
        keep_percentage / 100
    }
    print_debug("Threshold percentile:", threshold_percentile)

    # Initialize results
    cells_to_keep <- colnames(seurat_obj)
    filtering_stats <- list()
    plots <- list()
    all_thresholds <- list()

    # Process each filtering column
    for (col in filter_by_columns) {
        print_debug(sprintf("Processing column: %s", col))

        # Get unique values
        unique_values <- unique(seurat_obj@meta.data[[col]])
        print_debug("Unique values found:", unique_values)
        column_cells <- c()

        # Store statistics for this column
        col_stats <- data.frame(
            group = character(),
            initial_cells = numeric(),
            kept_cells = numeric(),
            threshold = numeric(),
            stringsAsFactors = FALSE
        )

        # Create plot data
        plot_data <- data.frame(
            value = seurat_obj@meta.data[[value_column]],
            group = factor(seurat_obj@meta.data[[col]])
        )
        print_data("Plot data summary:", summary(plot_data))

        # Filter for each unique value
        for (val in unique_values) {
            print_debug(sprintf("Processing value: %s", val))

            # Get cells for this group using direct subsetting
            group_mask <- seurat_obj@meta.data[[col]] == val
            group_cells <- rownames(seurat_obj@meta.data)[group_mask]

            print_debug("Number of cells in group:", length(group_cells))

            # Get values for these cells
            group_values <- seurat_obj@meta.data[group_cells, value_column]
            print_debug("Group values summary:", summary(group_values))

            # Calculate threshold
            threshold <- quantile(group_values, probs = threshold_percentile, na.rm = TRUE)
            print_debug("Calculated threshold:", threshold)

            # Select cells
            selected_cells <- if (lower_tail) {
                group_cells[group_values < threshold]
            } else {
                group_cells[group_values > threshold]
            }
            print_debug("Number of selected cells:", length(selected_cells))

            # Store statistics
            col_stats <- rbind(col_stats, data.frame(
                group = val,
                initial_cells = length(group_cells),
                kept_cells = length(selected_cells),
                threshold = threshold
            ))

            column_cells <- c(column_cells, selected_cells)
            all_thresholds[[col]][[as.character(val)]] <- threshold
        }

        # Update cells to keep
        cells_to_keep <- intersect(cells_to_keep, column_cells)
        print_debug("Total cells to keep after this column:", length(cells_to_keep))

        # Create visualization
        tryCatch(
            {
                # Define colors for each group
                n_colors <- length(unique_values)
                group_colors <- brewer.pal(n = max(3, n_colors), name = "Set1")[1:n_colors]
                names(group_colors) <- levels(plot_data$group)

                p <- ggplot(plot_data, aes(x = value, fill = group)) +
                    geom_density(alpha = 0.5) +
                    theme_bw() +
                    labs(
                        title = sprintf("Distribution of %s by %s", value_column, col),
                        x = value_column,
                        y = "Density",
                        fill = "Group"
                    ) +
                    theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
                    scale_fill_manual(values = group_colors)

                # Add threshold lines with matching colors
                for (val in names(all_thresholds[[col]])) {
                    p <- p + geom_vline(
                        xintercept = all_thresholds[[col]][[val]],
                        linetype = "dashed",
                        color = group_colors[val],
                        alpha = 0.8
                    )
                }

                plots[[col]] <- p
            },
            error = function(e) {
                warning(sprintf("Error creating plot for column %s: %s", col, e$message))
            }
        )

        filtering_stats[[col]] <- col_stats
    }

    # Create filtered object
    print_debug("Creating filtered object with cells:", length(cells_to_keep))
    seurat_filtered <- subset(seurat_obj, cells = cells_to_keep)

    # Add filtering information to metadata
    seurat_filtered$Filtered <- TRUE
    seurat_obj$Filtered <- FALSE
    seurat_obj$Filtered[colnames(seurat_obj) %in% cells_to_keep] <- TRUE

    # Create before/after comparison plot
    tryCatch(
        {
            comparison_plot <- ggplot(data.frame(
                value = seurat_obj@meta.data[[value_column]],
                filtered = factor(seurat_obj$Filtered,
                    levels = c(FALSE, TRUE),
                    labels = c("Before filtering", "After filtering")
                )
            ), aes(x = value, fill = filtered)) +
                geom_density(alpha = 0.5) +
                theme_bw() +
                labs(
                    title = sprintf("Distribution of %s before and after filtering", value_column),
                    x = value_column,
                    y = "Density",
                    fill = "Status"
                ) +
                scale_fill_manual(values = c("grey", "blue"))

            plots[["comparison"]] <- comparison_plot
        },
        error = function(e) {
            warning(sprintf("Error creating comparison plot: %s", e$message))
        }
    )

    # Calculate percentage of kept cells
    percent_kept <- (ncol(seurat_filtered) / ncol(seurat_obj)) * 100
    print_debug("Final statistics:", list(
        initial_cells = ncol(seurat_obj),
        filtered_cells = ncol(seurat_filtered),
        removed_cells = ncol(seurat_obj) - ncol(seurat_filtered),
        percent_kept = percent_kept
    ))

    return(list(
        seurat_filtered = seurat_filtered,
        plots = plots,
        stats = list(
            initial_cells = ncol(seurat_obj),
            filtered_cells = ncol(seurat_filtered),
            removed_cells = ncol(seurat_obj) - ncol(seurat_filtered),
            percent_kept = round(percent_kept, 2),
            detailed_stats = filtering_stats,
            thresholds = all_thresholds
        )
    ))
}

#' Filter Seurat object using knee point method
#' @param seurat_obj Seurat object to filter
#' @param threshold A numeric value between 0 and 1 (default: 0.5) that controls the filtering stringency
#' @param debug Enable debug mode (default: FALSE)
#' @return List containing filtered Seurat object, plots, and statistics
filter_seurat_knee_point <- function(seurat_obj, threshold = 0.5, debug = FALSE) {
    if (debug) print_debug("Starting knee point filtering with threshold:", threshold)

    # Get the expression matrix
    counts_matrix <- GetAssayData(seurat_obj, layer = "counts")

    # Calculate the sum of reads per cell
    cell_sums <- colSums(counts_matrix)
    cell_sums <- cell_sums[cell_sums > 0] # Remove cells with zero counts

    # Sort sums in decreasing order
    sorted_sums <- sort(cell_sums, decreasing = TRUE)

    # Calculate log values
    y <- log1p(sorted_sums)
    x <- log1p(seq_along(y))

    # Calculate the slope of the trend line
    slope <- (y[length(y)] - y[1]) / (x[length(x)] - x[1])
    yline <- slope * x + y[1]

    # Calculate distances to the trend line
    d <- sqrt((y - yline)^2)

    # Find points that exceed the threshold
    d2 <- d[which(d >= d[which.max(d)] * threshold)]
    x2 <- x[which(d >= d[which.max(d)] * threshold)]

    # Determine the filtering threshold
    threshold_value <- expm1(y[which(x == x2[which.max(x2)])])

    # Filter cells
    cells_to_keep <- names(cell_sums)[cell_sums >= threshold_value]
    seurat_filtered <- subset(seurat_obj, cells = cells_to_keep)

    # Create diagnostic plots
    knee_plot <- ggplot(data.frame(x = x, y = y, yline = yline), aes(x = x, y = y)) +
        geom_point(alpha = 0.5) +
        geom_line(aes(y = yline), color = "red") +
        theme_bw() +
        labs(
            title = paste("Read distribution per cell (threshold =", threshold, ")"),
            x = "Log(Rank)",
            y = "Log(Number of reads)"
        )

    distance_plot <- ggplot(data.frame(x = x, d = d), aes(x = x, y = d)) +
        geom_point(alpha = 0.5) +
        geom_point(data = data.frame(x = x2, d = d2), color = "green") +
        theme_bw() +
        labs(
            title = paste("Distances to trend line (threshold =", threshold, ")"),
            x = "Log(Rank)",
            y = "Distance"
        )

    # Ajouter un nouveau graphique de distribution des UMIs
    umi_distribution_plot <- ggplot(data.frame(umis = cell_sums), aes(x = umis)) +
        geom_histogram(bins = 100, fill = "steelblue", alpha = 0.7) +
        geom_vline(xintercept = threshold_value, color = "red", linetype = "dashed", size = 1) +
        scale_x_log10() +
        theme_bw() +
        labs(
            title = "UMI Distribution per Cell",
            x = "Number of UMIs (log10 scale)",
            y = "Number of cells",
            caption = paste("Red line: filtering threshold (", round(threshold_value, 2), " UMIs)")
        ) +
        annotate("text",
            x = threshold_value,
            y = max(hist(cell_sums, breaks = 100, plot = FALSE)$counts),
            label = paste("Threshold:", round(threshold_value, 2), "UMIs"),
            hjust = -0.1,
            vjust = 1,
            color = "red"
        )

    # Calculate statistics
    stats <- list(
        initial_cells = ncol(seurat_obj),
        filtered_cells = ncol(seurat_filtered),
        removed_cells = ncol(seurat_obj) - ncol(seurat_filtered),
        percent_kept = round((ncol(seurat_filtered) / ncol(seurat_obj)) * 100, 2),
        knee_threshold = threshold,
        umi_threshold = threshold_value,
        mean_umis = mean(cell_sums),
        median_umis = median(cell_sums),
        max_umis = max(cell_sums),
        # Ajouter des statistiques sur la distribution
        cells_below_threshold = sum(cell_sums < threshold_value),
        cells_above_threshold = sum(cell_sums >= threshold_value),
        percent_below_threshold = round(sum(cell_sums < threshold_value) / length(cell_sums) * 100, 2),
        percent_above_threshold = round(sum(cell_sums >= threshold_value) / length(cell_sums) * 100, 2)
    )

    return(list(
        seurat_filtered = seurat_filtered,
        plots = list(
            knee_plot = knee_plot,
            distance_plot = distance_plot,
            umi_distribution_plot = umi_distribution_plot
        ),
        stats = stats
    ))
}

#' Filter Seurat object using knee point method for each group
#' @param seurat_obj Seurat object to filter
#' @param group_column Column name to group by (e.g., "Sample_ID")
#' @param threshold A numeric value between 0 and 1 (default: 0.5) that controls the filtering stringency
#' @param debug Enable debug mode (default: FALSE)
#' @return List containing filtered Seurat object, plots, and statistics
filter_seurat_knee_point_by_group <- function(seurat_obj, group_column, threshold = 0.5, debug = FALSE) {
    if (debug) print_debug("Starting knee point filtering by group:", list(group_column = group_column, threshold = threshold))

    # Get unique groups
    groups <- unique(seurat_obj@meta.data[[group_column]])
    if (debug) print_debug("Found groups:", groups)

    # Initialize results
    all_cells_to_keep <- c()
    all_plots <- list()
    all_stats <- list()
    group_thresholds <- list()

    # Process each group
    for (group in groups) {
        if (debug) print_debug(sprintf("Processing group: %s", group))

        # Subset Seurat object for this group
        group_cells <- colnames(seurat_obj)[seurat_obj@meta.data[[group_column]] == group]
        group_obj <- subset(seurat_obj, cells = group_cells)

        # Apply knee point filtering to this group
        group_results <- filter_seurat_knee_point(group_obj, threshold = threshold, debug = debug)

        # Store results
        all_cells_to_keep <- c(all_cells_to_keep, colnames(group_results$seurat_filtered))
        all_plots[[group]] <- group_results$plots
        all_stats[[group]] <- group_results$stats
        group_thresholds[[group]] <- group_results$stats$umi_threshold
    }

    # Create filtered object
    seurat_filtered <- subset(seurat_obj, cells = all_cells_to_keep)

    # Calculate overall statistics
    overall_stats <- list(
        initial_cells = ncol(seurat_obj),
        filtered_cells = ncol(seurat_filtered),
        removed_cells = ncol(seurat_obj) - ncol(seurat_filtered),
        percent_kept = round((ncol(seurat_filtered) / ncol(seurat_obj)) * 100, 2),
        group_stats = all_stats,
        group_thresholds = group_thresholds
    )

    return(list(
        seurat_filtered = seurat_filtered,
        plots = all_plots,
        stats = overall_stats
    ))
}

# Load the Seurat object
seurat_obj <- readRDS("data/big_data/RDS_files/SeuratObject_All_Metadata.rds")

# Get metadata
metadata <- seurat_obj@meta.data

# Convert Rep_tech to factor
metadata$Rep_tech <- as.factor(metadata$Rep_tech)

# Update metadata in Seurat object
seurat_obj@meta.data <- metadata

# Get gene annotations
gene_annotations <- seurat_obj[["RNA"]][[]]

# Get unique values for gene annotation filters, including NA
unique_feature_types <- sort(unique(gene_annotations$feature))
unique_seq_types <- sort(unique(gene_annotations$seq_type))
unique_gene_classes <- sort(unique(gene_annotations$class))

# Create named vectors for choices
feature_choices <- setNames(
    c(unique_feature_types, "NA"),
    c(unique_feature_types, "Not Annotated")
)
seq_choices <- setNames(
    c(unique_seq_types, "NA"),
    c(unique_seq_types, "Not Annotated")
)
class_choices <- setNames(
    c(unique_gene_classes, "NA"),
    c(unique_gene_classes, "Not Annotated")
)

# Detect all columns and their types
all_vars <- colnames(metadata)

# Définir les variables de qualité (pour la sélection multiple)
quality_vars <- c("nCount_RNA", "nFeature_RNA")

# Définir les variables de protocole
protocol_vars <- c(
    "Sample_ID",
    "Condition",
    "Culture_medium",
    "Rep_bio",
    "Rep_tech",
    "OD_timepoint",
    "OD_theoric",
    "OD_measured"
)

# Définir les variables numériques pour la logique interne
numeric_vars <- c("nCount_RNA", "nFeature_RNA", "OD_theoric", "OD_measured")

# Définir les variables catégorielles pour la logique interne
categorical_vars <- c("Sample_ID", "Condition", "Culture_medium", "Rep_bio", "Rep_tech", "OD_timepoint")

# Define value columns for thresholding with descriptions
threshold_columns <- list(
    "nCount_RNA" = "Total number of UMIs (Unique Molecular Identifiers) per cell. Represents the sequencing depth.",
    "nFeature_RNA" = "Number of unique genes detected per cell. Represents the complexity of the transcriptome.",
    "OD_theoric" = "Theoretical Optical Density value.",
    "OD_measured" = "Measured Optical Density value."
)

# Function to create plate visualization
create_plate_plot <- function(data, value_column, numeric_operation = "mean",
                              min_nCount = NULL, max_nCount = NULL,
                              min_nFeature = NULL, max_nFeature = NULL,
                              feature_types = NULL, seq_types = NULL, gene_classes = NULL,
                              barcode_round = 1) {
    # Copy metadata for manipulation
    filtered_data <- data

    # Définir la colonne de localisation en fonction du round
    well_loc_column <- paste0("Well_loc_rd", barcode_round)
    barcode_column <- paste0("barcode.rd", barcode_round)

    # Apply gene annotation filters dynamically
    if (!is.null(feature_types) || !is.null(seq_types) || !is.null(gene_classes)) {
        # Dynamically select genes to keep based on filters
        genes_to_keep <- rownames(gene_annotations)[
            (is.null(feature_types) |
                (gene_annotations$feature %in% feature_types) |
                ("NA" %in% feature_types & is.na(gene_annotations$feature))) &
                (is.null(seq_types) |
                    (gene_annotations$seq_type %in% seq_types) |
                    ("NA" %in% seq_types & is.na(gene_annotations$seq_type))) &
                (is.null(gene_classes) |
                    (gene_annotations$class %in% gene_classes) |
                    ("NA" %in% gene_classes & is.na(gene_annotations$class)))
        ]
        # Extract the expression matrix for the selected genes
        expr_data <- GetAssayData(seurat_obj, assay = "RNA", layer = "counts")[genes_to_keep, , drop = FALSE]
        # Recalculate nCount_RNA and nFeature_RNA for each cell based on filtered genes
        filtered_data$nCount_RNA <- Matrix::colSums(expr_data)
        filtered_data$nFeature_RNA <- Matrix::colSums(expr_data > 0)
    }

    # Apply cell filters
    if (!is.null(min_nCount)) filtered_data <- filtered_data %>% filter(nCount_RNA >= min_nCount)
    if (!is.null(max_nCount)) filtered_data <- filtered_data %>% filter(nCount_RNA <= max_nCount)
    if (!is.null(min_nFeature)) filtered_data <- filtered_data %>% filter(nFeature_RNA >= min_nFeature)
    if (!is.null(max_nFeature)) filtered_data <- filtered_data %>% filter(nFeature_RNA <= max_nFeature)

    # Create a data frame with all possible well positions
    all_wells <- expand.grid(
        row = LETTERS[1:8],
        col = 1:12
    ) %>%
        mutate(!!sym(well_loc_column) := paste0(row, col))

    # Calculate value for each well based on column type
    if (value_column %in% numeric_vars) {
        well_values <- filtered_data %>%
            group_by(!!sym(well_loc_column)) %>%
            summarise(
                value = case_when(
                    numeric_operation == "mean" ~ mean(!!sym(value_column), na.rm = TRUE),
                    numeric_operation == "median" ~ median(!!sym(value_column), na.rm = TRUE),
                    numeric_operation == "min" ~ min(!!sym(value_column), na.rm = TRUE),
                    numeric_operation == "max" ~ max(!!sym(value_column), na.rm = TRUE),
                    numeric_operation == "q1" ~ quantile(!!sym(value_column), 0.25, na.rm = TRUE),
                    numeric_operation == "q3" ~ quantile(!!sym(value_column), 0.75, na.rm = TRUE)
                ),
                n_cells = n(),
                unique_barcodes = n_distinct(!!sym(barcode_column)),
                sample_ids = paste(unique(Sample_ID), collapse = ", "),
                culture_medium = paste(unique(Culture_medium), collapse = ", "),
                rep_bio = paste(unique(Rep_bio), collapse = ", "),
                rep_tech = paste(unique(Rep_tech), collapse = ", "),
                od_timepoint = paste(unique(OD_timepoint), collapse = ", ")
            )
    } else {
        well_values <- filtered_data %>%
            group_by(!!sym(well_loc_column)) %>%
            count(!!sym(value_column)) %>%
            slice_max(n, n = 1) %>%
            select(!!sym(well_loc_column), value = !!sym(value_column)) %>%
            left_join(
                filtered_data %>%
                    group_by(!!sym(well_loc_column)) %>%
                    summarise(
                        n_cells = n(),
                        unique_barcodes = n_distinct(!!sym(barcode_column)),
                        sample_ids = paste(unique(Sample_ID), collapse = ", "),
                        culture_medium = paste(unique(Culture_medium), collapse = ", "),
                        rep_bio = paste(unique(Rep_bio), collapse = ", "),
                        rep_tech = paste(unique(Rep_tech), collapse = ", "),
                        od_timepoint = paste(unique(OD_timepoint), collapse = ", ")
                    ),
                by = well_loc_column
            )
    }

    # Merge with all wells to ensure all positions are shown
    plot_data <- all_wells %>%
        left_join(well_values, by = well_loc_column) %>%
        mutate(
            row = factor(row, levels = LETTERS[8:1]),
            col = factor(col, levels = 1:12),
            hover_text = paste(
                "Well:", !!sym(well_loc_column), "\n",
                if (value_column %in% numeric_vars) {
                    operation_label <- case_when(
                        numeric_operation == "mean" ~ "Mean",
                        numeric_operation == "median" ~ "Median",
                        numeric_operation == "min" ~ "Minimum",
                        numeric_operation == "max" ~ "Maximum",
                        numeric_operation == "q1" ~ "First quartile (Q1)",
                        numeric_operation == "q3" ~ "Third quartile (Q3)"
                    )
                    paste(operation_label, "of", value_column, ":", round(value, 2), "\n")
                } else {
                    paste("Value:", value, "\n")
                },
                "Cells after filtering:", n_cells, "\n",
                "Unique barcodes in round", barcode_round, ":", unique_barcodes, "\n",
                "Sample ID:", sample_ids, "\n",
                "Culture medium:", culture_medium, "\n",
                "Biological replicate:", rep_bio, "\n",
                "Technical replicate:", rep_tech, "\n",
                "OD timepoint:", od_timepoint,
                if (!is.null(feature_types)) paste("\nFeature types:", paste(feature_types, collapse = ", ")),
                if (!is.null(seq_types)) paste("\nSequence types:", paste(seq_types, collapse = ", ")),
                if (!is.null(gene_classes)) paste("\nGene classes:", paste(gene_classes, collapse = ", "))
            )
        )

    # Create the plot
    p <- ggplot(plot_data, aes(x = col, y = row, fill = value, text = hover_text)) +
        geom_tile(color = "black", size = 0.5) +
        theme_minimal() +
        theme(
            panel.grid = element_blank(),
            axis.title = element_blank(),
            plot.title = element_text(hjust = 0.5, size = 14),
            legend.position = "right"
        ) +
        labs(title = paste(
            "96-well Plate Visualization - Round", barcode_round, "-", value_column,
            if (value_column %in% numeric_vars) {
                operation_label <- case_when(
                    numeric_operation == "mean" ~ "(Mean)",
                    numeric_operation == "median" ~ "(Median)",
                    numeric_operation == "min" ~ "(Minimum)",
                    numeric_operation == "max" ~ "(Maximum)",
                    numeric_operation == "q1" ~ "(Q1)",
                    numeric_operation == "q3" ~ "(Q3)"
                )
                paste(
                    operation_label, "\nFiltered cells:",
                    if (!is.null(min_nCount)) paste("nCount_RNA >=", min_nCount),
                    if (!is.null(max_nCount)) paste("nCount_RNA <=", max_nCount),
                    if (!is.null(min_nFeature)) paste("nFeature_RNA >=", min_nFeature),
                    if (!is.null(max_nFeature)) paste("nFeature_RNA <=", max_nFeature),
                    if (!is.null(feature_types)) paste("\nFeature types:", paste(feature_types, collapse = ", ")),
                    if (!is.null(seq_types)) paste("\nSequence types:", paste(seq_types, collapse = ", ")),
                    if (!is.null(gene_classes)) paste("\nGene classes:", paste(gene_classes, collapse = ", "))
                )
            } else {
                ""
            }
        )) +
        coord_fixed()

    # Add appropriate scale based on variable type
    if (value_column %in% numeric_vars) {
        operation_label <- case_when(
            numeric_operation == "mean" ~ "Mean",
            numeric_operation == "median" ~ "Median",
            numeric_operation == "min" ~ "Minimum",
            numeric_operation == "max" ~ "Maximum",
            numeric_operation == "q1" ~ "Q1",
            numeric_operation == "q3" ~ "Q3"
        )
        p <- p + scale_fill_viridis(name = paste(value_column, "\n", operation_label), na.value = "white")
    } else {
        p <- p + scale_fill_viridis_d(name = value_column, na.value = "white")
    }

    # Convert to plotly
    ggplotly(p, tooltip = "text") %>%
        layout(
            hoverlabel = list(bgcolor = "white"),
            showlegend = TRUE
        )
}

# Define UI
ui <- fluidPage(
    titlePanel("Seurat Object Visualization and Filtering"),
    tabsetPanel(
        tabPanel(
            "Current Filtering",
            fluidRow(
                # Left sidebar for filters
                column(
                    3,
                    sidebarPanel(
                        # Onglets pour différents types de filtrage
                        tabsetPanel(
                            tabPanel(
                                "Basic Filters",
                                # Filtres de base existants
                                checkboxInput("apply_filters", "Apply cell filters", value = FALSE),
                                conditionalPanel(
                                    condition = "input.apply_filters == true",
                                    h4("Cell Filters"),
                                    numericInput("min_nCount", "Minimum nCount_RNA:", value = 200, min = 0),
                                    numericInput("max_nCount", "Maximum nCount_RNA:", value = 50000, min = 0),
                                    numericInput("min_nFeature", "Minimum nFeature_RNA:", value = 200, min = 0),
                                    numericInput("max_nFeature", "Maximum nFeature_RNA:", value = 5000, min = 0)
                                ),
                                hr(),
                                # Filtres d'annotation des gènes existants
                                checkboxInput("apply_gene_filters", "Apply gene annotation filters", value = FALSE),
                                conditionalPanel(
                                    condition = "input.apply_gene_filters == true",
                                    h4("Gene Annotation Filters"),
                                    checkboxGroupInput("feature_types", "Feature Types:",
                                        choices = feature_choices,
                                        selected = NULL
                                    ),
                                    checkboxGroupInput("seq_types", "Sequence Types:",
                                        choices = seq_choices,
                                        selected = NULL
                                    ),
                                    checkboxGroupInput("gene_classes", "Gene Classes:",
                                        choices = class_choices,
                                        selected = NULL
                                    )
                                )
                            ),
                            tabPanel(
                                "Threshold Filter",
                                checkboxInput("apply_threshold_filter", "Apply threshold filtering", value = FALSE),
                                conditionalPanel(
                                    condition = "input.apply_threshold_filter == true",
                                    h4("Threshold Filter Settings"),
                                    selectInput("threshold_variable",
                                        "Select variable for threshold filtering:",
                                        choices = c("Sample_ID", categorical_vars),
                                        selected = "Sample_ID"
                                    ),
                                    numericInput("threshold_percentage",
                                        "Percentage of cells to keep (0-100):",
                                        value = 75,
                                        min = 0,
                                        max = 100,
                                        step = 0.01
                                    ),
                                    radioButtons("threshold_direction",
                                        "Filter direction:",
                                        choices = c(
                                            "Keep lower values" = "lower",
                                            "Keep higher values" = "higher"
                                        ),
                                        selected = "higher"
                                    ),
                                    verbatimTextOutput("threshold_stats")
                                )
                            ),
                            tabPanel(
                                "Plate Protocol",
                                h4("Protocol Variables"),
                                selectInput("protocol_variable",
                                    "Select protocol variable to visualize:",
                                    choices = protocol_vars,
                                    selected = protocol_vars[1]
                                ),
                                hr(),
                                plotlyOutput("protocol_plot", height = "400px")
                            )
                        ),
                        hr(),
                        # Add RDS download button
                        h4("Download Filtered Seurat Object"),
                        downloadButton("downloadRDS", "Download Filtered Seurat Object (.rds)"),
                        width = 12
                    )
                ),
                # Main plot area
                column(
                    6,
                    # Add checkbox for multiple plots (only for quality variables)
                    checkboxInput("show_multiple_plots", "Show multiple quality plots", value = FALSE),
                    # Container for plots
                    div(
                        id = "plot_container",
                        # Single plot view
                        conditionalPanel(
                            condition = "!input.show_multiple_plots",
                            plotlyOutput("plate_plot", height = "800px")
                        ),
                        # Multiple plots view (only for quality variables)
                        conditionalPanel(
                            condition = "input.show_multiple_plots",
                            uiOutput("multiple_plots")
                        )
                    )
                ),
                # Right sidebar for visualization controls
                column(
                    3,
                    sidebarPanel(
                        h4("Visualization Controls"),
                        # Single plot controls
                        conditionalPanel(
                            condition = "!input.show_multiple_plots",
                            radioButtons("barcode_round",
                                "Select barcode round:",
                                choices = c(
                                    "Round 1" = 1,
                                    "Round 2" = 2,
                                    "Round 3" = 3
                                ),
                                selected = 1
                            ),
                            hr(),
                            selectInput("variable",
                                "Select quality variable:",
                                choices = quality_vars,
                                selected = quality_vars[1]
                            ),
                            radioButtons("numeric_operation",
                                "Statistics for quality variables:",
                                choices = c(
                                    "Median" = "median",
                                    "Mean" = "mean",
                                    "Minimum" = "min",
                                    "Maximum" = "max",
                                    "First quartile (Q1)" = "q1",
                                    "Third quartile (Q3)" = "q3"
                                ),
                                selected = "median"
                            ),
                            hr(),
                            downloadButton("downloadPlot", "Download quality plot")
                        ),
                        # Multiple plots controls
                        conditionalPanel(
                            condition = "input.show_multiple_plots",
                            # Rounds selection
                            h5("Select Rounds"),
                            checkboxGroupInput("selected_rounds",
                                "Barcode rounds:",
                                choices = c(
                                    "Round 1" = 1,
                                    "Round 2" = 2,
                                    "Round 3" = 3
                                ),
                                selected = 1
                            ),
                            hr(),
                            # Dynamic UI for variable and statistics selection
                            uiOutput("round_variable_selection"),
                            hr(),
                            downloadButton("downloadMultiplePlots", "Download all quality plots")
                        ),
                        width = 12
                    )
                )
            )
        ),
        tabPanel(
            "Knee Point Filtering",
            sidebarLayout(
                sidebarPanel(
                    div(
                        style = "margin-bottom: 20px;",
                        h4("Knee Point Threshold"),
                        # Ajouter un sélecteur pour le mode de filtrage
                        radioButtons("knee_filter_mode",
                            "Filtering mode:",
                            choices = c(
                                "Global filtering" = "global",
                                "Group-specific filtering" = "group"
                            ),
                            selected = "global"
                        ),
                        # Ajouter un sélecteur de groupe conditionnel
                        conditionalPanel(
                            condition = "input.knee_filter_mode == 'group'",
                            selectInput("knee_group_column",
                                "Select grouping variable:",
                                choices = c("Sample_ID", "Condition", "Culture_medium", "Rep_bio", "Rep_tech"),
                                selected = "Sample_ID"
                            ),
                            # Ajouter un sélecteur de groupes
                            conditionalPanel(
                                condition = "input.knee_group_column == 'Sample_ID'",
                                div(
                                    style = "margin-top: 10px;",
                                    h5("Select groups to display (max 4):"),
                                    selectizeInput("selected_groups",
                                        NULL,
                                        choices = NULL,
                                        multiple = TRUE,
                                        options = list(maxItems = 4)
                                    ),
                                    helpText("Select up to 4 groups to display. Other groups will still be processed but not shown.")
                                )
                            )
                        ),
                        div(
                            style = "background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 15px;",
                            p("The knee point threshold (0-1) determines where the transition point is located in the read distribution. A higher value (e.g., 0.999) identifies a stricter knee point, which translates to a higher filtering threshold in UMI counts."),
                            p("For example, a threshold of 0.999 might correspond to a filtering threshold of 248 UMIs, meaning that only cells with 248 or more UMIs will be kept.")
                        ),
                        div(
                            style = "display: flex; align-items: center; gap: 10px;",
                            numericInput("knee_threshold",
                                label = NULL,
                                value = 0.5,
                                min = 0,
                                max = 1,
                                step = 0.0001,
                                width = "100%"
                            )
                        ),
                        div(
                            style = "display: flex; justify-content: space-between; margin-top: 5px;",
                            actionButton("decrease_threshold", "-0.0001", style = "width: 48%;"),
                            actionButton("increase_threshold", "+0.0001", style = "width: 48%;")
                        ),
                        div(
                            style = "display: flex; justify-content: space-between; margin-top: 5px;",
                            actionButton("decrease_threshold_10", "-0.001", style = "width: 48%;"),
                            actionButton("increase_threshold_10", "+0.001", style = "width: 48%;")
                        ),
                        div(
                            style = "display: flex; justify-content: space-between; margin-top: 5px;",
                            actionButton("decrease_threshold_100", "-0.01", style = "width: 48%;"),
                            actionButton("increase_threshold_100", "+0.01", style = "width: 48%;")
                        ),
                        helpText("Adjust the threshold with precision (0-1)"),
                        tags$small("Use the buttons for precise adjustments or enter a value directly")
                    ),
                    actionButton("apply_knee_filter", "Apply Knee Point Filter"),
                    hr(),
                    verbatimTextOutput("knee_stats"),
                    width = 3
                ),
                mainPanel(
                    fluidRow(
                        column(6, plotOutput("knee_plot")),
                        column(6, plotOutput("distance_plot"))
                    ),
                    fluidRow(
                        column(12, plotOutput("umi_distribution_plot", height = "400px"))
                    ),
                    fluidRow(
                        column(
                            12,
                            h4("Filtering Statistics"),
                            tableOutput("knee_filtering_table")
                        )
                    )
                )
            )
        )
    )
)

# Define server
server <- function(input, output, session) {
    # Reactive function to get filtered cells based on threshold
    thresholdFilteredCells <- reactive({
        if (!input$apply_threshold_filter) {
            return(NULL)
        }

        # Get the variable to filter on
        filter_var <- input$threshold_variable
        threshold_pct <- input$threshold_percentage
        keep_lower <- input$threshold_direction == "lower"

        # Get cells after applying other filters
        filtered_metadata <- seurat_obj@meta.data

        # Apply basic filters if enabled
        if (input$apply_filters) {
            filtered_metadata <- filtered_metadata %>%
                filter(
                    nCount_RNA >= input$min_nCount,
                    nCount_RNA <= input$max_nCount,
                    nFeature_RNA >= input$min_nFeature,
                    nFeature_RNA <= input$max_nFeature
                )
        }

        # Apply gene filters if enabled
        if (input$apply_gene_filters) {
            # Get genes to keep based on filters
            genes_to_keep <- rownames(gene_annotations)

            if (!is.null(input$feature_types) && length(input$feature_types) > 0) {
                genes_to_keep <- genes_to_keep[gene_annotations$feature %in% input$feature_types | is.na(gene_annotations$feature)]
            }
            if (!is.null(input$seq_types) && length(input$seq_types) > 0) {
                genes_to_keep <- genes_to_keep[gene_annotations$seq_type %in% input$seq_types | is.na(gene_annotations$seq_type)]
            }
            if (!is.null(input$gene_classes) && length(input$gene_classes) > 0) {
                genes_to_keep <- genes_to_keep[gene_annotations$class %in% input$gene_classes | is.na(gene_annotations$class)]
            }

            # Subset the Seurat object and get cells
            filtered_obj <- subset(seurat_obj, features = genes_to_keep)
            filtered_metadata <- filtered_metadata[filtered_metadata$barcode.rd1 %in% colnames(filtered_obj), ]
        }

        # Calculate threshold for each group
        cells_to_keep <- c()
        stats <- data.frame(
            group = character(),
            initial_cells = integer(),
            kept_cells = integer(),
            percentage_kept = numeric(),
            stringsAsFactors = FALSE
        )

        # Get unique groups, handling NA values
        unique_groups <- unique(filtered_metadata[[filter_var]])
        unique_groups <- unique_groups[!is.na(unique_groups)]

        for (group in unique_groups) {
            # Get cells for this group
            group_mask <- filtered_metadata[[filter_var]] == group
            group_cells <- filtered_metadata[group_mask, ]
            initial_count <- nrow(group_cells)

            if (initial_count > 0) {
                # Calculate threshold value
                threshold_value <- quantile(
                    group_cells$nCount_RNA,
                    probs = if (keep_lower) threshold_pct / 100 else (1 - threshold_pct / 100),
                    na.rm = TRUE
                )

                # Select cells based on threshold
                if (keep_lower) {
                    selected_mask <- group_cells$nCount_RNA <= threshold_value
                } else {
                    selected_mask <- group_cells$nCount_RNA > threshold_value
                }

                selected_cells <- group_cells$barcode.rd1[selected_mask]
                cells_to_keep <- c(cells_to_keep, selected_cells)

                # Store statistics
                stats <- rbind(stats, data.frame(
                    group = as.character(group),
                    initial_cells = initial_count,
                    kept_cells = sum(selected_mask),
                    percentage_kept = round(sum(selected_mask) / initial_count * 100, 2)
                ))
            }
        }

        # Update threshold statistics
        output$threshold_stats <- renderPrint({
            cat("Threshold Filtering Statistics:\n")
            cat("---------------------------\n")
            print(stats)
            cat("\nTotal cells before threshold filtering:", sum(stats$initial_cells), "\n")
            cat("Total cells after threshold filtering:", sum(stats$kept_cells), "\n")
            cat("Overall percentage kept:", round(sum(stats$kept_cells) / sum(stats$initial_cells) * 100, 2), "%\n")
        })

        return(cells_to_keep)
    })

    # Function to create a single plot
    create_single_plot <- function(data, value_column, numeric_operation, barcode_round, ...) {
        create_plate_plot(
            data = data,
            value_column = value_column,
            numeric_operation = numeric_operation,
            barcode_round = barcode_round,
            ...
        )
    }

    # Get filtered data - make it reactive to barcode round
    get_filtered_data <- reactive({
        # Get filter values
        min_nCount <- if (input$apply_filters) input$min_nCount else NULL
        max_nCount <- if (input$apply_filters) input$max_nCount else NULL
        min_nFeature <- if (input$apply_filters) input$min_nFeature else NULL
        max_nFeature <- if (input$apply_filters) input$max_nFeature else NULL

        # Get gene annotation filters
        feature_types <- if (input$apply_gene_filters && !is.null(input$feature_types)) input$feature_types else NULL
        seq_types <- if (input$apply_gene_filters && !is.null(input$seq_types)) input$seq_types else NULL
        gene_classes <- if (input$apply_gene_filters && !is.null(input$gene_classes)) input$gene_classes else NULL

        # Get threshold filtered cells
        threshold_cells <- thresholdFilteredCells()

        # Create filtered metadata
        filtered_metadata <- seurat_obj@meta.data

        # Apply all filters in sequence
        if (!is.null(threshold_cells)) {
            filtered_metadata <- filtered_metadata[filtered_metadata$barcode.rd1 %in% threshold_cells, ]
        }

        return(filtered_metadata)
    })

    # Single plot output - make it reactive to barcode round
    output$plate_plot <- renderPlotly({
        req(input$variable, input$barcode_round)
        filtered_data <- get_filtered_data()

        create_single_plot(
            data = filtered_data,
            value_column = input$variable,
            numeric_operation = input$numeric_operation,
            barcode_round = as.numeric(input$barcode_round),
            min_nCount = if (input$apply_filters) input$min_nCount else NULL,
            max_nCount = if (input$apply_filters) input$max_nCount else NULL,
            min_nFeature = if (input$apply_filters) input$min_nFeature else NULL,
            max_nFeature = if (input$apply_filters) input$max_nFeature else NULL,
            feature_types = if (input$apply_gene_filters) input$feature_types else NULL,
            seq_types = if (input$apply_gene_filters) input$seq_types else NULL,
            gene_classes = if (input$apply_gene_filters) input$gene_classes else NULL
        )
    })

    # Dynamic UI for variable selection per round
    output$round_variable_selection <- renderUI({
        req(input$selected_rounds)

        # Create a list of UI elements for each round
        round_ui <- lapply(input$selected_rounds, function(round) {
            div(
                style = "margin-bottom: 20px;",
                h5(paste("Round", round, "Settings")),
                # Pour chaque variable de qualité, créer un groupe de sélection
                lapply(quality_vars, function(var) {
                    div(
                        style = "margin-left: 10px; margin-bottom: 15px;",
                        h6(var, style = "margin-bottom: 5px;"),
                        # Sélection des statistiques pour cette variable
                        checkboxGroupInput(
                            paste0("statistics_", round, "_", var),
                            NULL, # Remove label since we have h6
                            choices = c(
                                "Median" = "median",
                                "Mean" = "mean",
                                "Minimum" = "min",
                                "Maximum" = "max",
                                "First quartile (Q1)" = "q1",
                                "Third quartile (Q3)" = "q3"
                            ),
                            selected = "median",
                            inline = TRUE # Display checkboxes horizontally
                        )
                    )
                })
            )
        })

        # Return all UI elements
        do.call(tagList, round_ui)
    })

    # Multiple plots output
    output$multiple_plots <- renderUI({
        req(input$selected_rounds)

        # Créer une liste de toutes les combinaisons valides
        valid_combinations <- do.call(rbind, lapply(input$selected_rounds, function(round) {
            # Pour chaque variable de qualité
            do.call(rbind, lapply(quality_vars, function(var) {
                # Récupérer les statistiques sélectionnées pour cette variable
                selected_stats <- input[[paste0("statistics_", round, "_", var)]]
                if (!is.null(selected_stats) && length(selected_stats) > 0) {
                    # Créer une ligne pour chaque statistique sélectionnée
                    data.frame(
                        round = round,
                        variable = var,
                        statistic = selected_stats,
                        stringsAsFactors = FALSE
                    )
                }
            }))
        }))

        if (is.null(valid_combinations) || nrow(valid_combinations) == 0) {
            return(h4("Please select at least one statistic for each variable"))
        }

        # Calculate number of plots and rows needed
        n_plots <- nrow(valid_combinations)
        n_cols <- 2 # Number of columns in the grid
        n_rows <- ceiling(n_plots / n_cols)

        # Create a list of plot outputs
        plot_outputs <- lapply(seq_len(nrow(valid_combinations)), function(i) {
            combo <- valid_combinations[i, ]

            plot_output <- plotlyOutput(
                paste0("plot_", i),
                height = paste0(800 / n_rows, "px")
            )

            # Render the plot
            output[[paste0("plot_", i)]] <- renderPlotly({
                filtered_data <- get_filtered_data()

                create_single_plot(
                    data = filtered_data,
                    value_column = combo$variable,
                    numeric_operation = combo$statistic,
                    barcode_round = as.numeric(combo$round),
                    min_nCount = if (input$apply_filters) input$min_nCount else NULL,
                    max_nCount = if (input$apply_filters) input$max_nCount else NULL,
                    min_nFeature = if (input$apply_filters) input$min_nFeature else NULL,
                    max_nFeature = if (input$apply_filters) input$max_nFeature else NULL,
                    feature_types = if (input$apply_gene_filters) input$feature_types else NULL,
                    seq_types = if (input$apply_gene_filters) input$seq_types else NULL,
                    gene_classes = if (input$apply_gene_filters) input$gene_classes else NULL
                )
            })

            return(plot_output)
        })

        # Create the grid layout
        do.call(tagList, lapply(seq_len(n_rows), function(row) {
            fluidRow(
                lapply(seq_len(n_cols), function(col) {
                    idx <- (row - 1) * n_cols + col
                    if (idx <= n_plots) {
                        column(6, plot_outputs[[idx]])
                    }
                })
            )
        }))
    })

    # Update download handler for multiple plots
    output$downloadMultiplePlots <- downloadHandler(
        filename = function() {
            # Get all valid combinations
            valid_combinations <- do.call(rbind, lapply(input$selected_rounds, function(round) {
                do.call(rbind, lapply(quality_vars, function(var) {
                    selected_stats <- input[[paste0("statistics_", round, "_", var)]]
                    if (!is.null(selected_stats) && length(selected_stats) > 0) {
                        data.frame(
                            round = round,
                            variable = var,
                            statistic = selected_stats,
                            stringsAsFactors = FALSE
                        )
                    }
                }))
            }))

            # Create filename
            paste("plate_plots_",
                paste(unique(valid_combinations$round), collapse = "_"),
                "_",
                paste(unique(valid_combinations$variable), collapse = "_"),
                "_",
                paste(unique(valid_combinations$statistic), collapse = "_"),
                ".pdf",
                sep = ""
            )
        },
        content = function(file) {
            # Get all valid combinations
            valid_combinations <- do.call(rbind, lapply(input$selected_rounds, function(round) {
                do.call(rbind, lapply(quality_vars, function(var) {
                    selected_stats <- input[[paste0("statistics_", round, "_", var)]]
                    if (!is.null(selected_stats) && length(selected_stats) > 0) {
                        data.frame(
                            round = round,
                            variable = var,
                            statistic = selected_stats,
                            stringsAsFactors = FALSE
                        )
                    }
                }))
            }))

            # Create PDF
            pdf(file, width = 12, height = 8 * ceiling(nrow(valid_combinations) / 2))
            filtered_data <- get_filtered_data()

            for (i in seq_len(nrow(valid_combinations))) {
                combo <- valid_combinations[i, ]
                p <- create_single_plot(
                    data = filtered_data,
                    value_column = combo$variable,
                    numeric_operation = combo$statistic,
                    barcode_round = as.numeric(combo$round),
                    min_nCount = if (input$apply_filters) input$min_nCount else NULL,
                    max_nCount = if (input$apply_filters) input$max_nCount else NULL,
                    min_nFeature = if (input$apply_filters) input$min_nFeature else NULL,
                    max_nFeature = if (input$apply_filters) input$max_nFeature else NULL,
                    feature_types = if (input$apply_gene_filters) input$feature_types else NULL,
                    seq_types = if (input$apply_gene_filters) input$seq_types else NULL,
                    gene_classes = if (input$apply_gene_filters) input$gene_classes else NULL
                )
                print(p)
            }
            dev.off()
        }
    )

    # Reactive function to create filtered Seurat object
    filteredSeuratObject <- reactive({
        tryCatch(
            {
                # Start with the original Seurat object
                filtered_obj <- seurat_obj

                # Apply gene filters if specified
                if (input$apply_gene_filters) {
                    # Get genes to keep based on filters
                    genes_to_keep <- rownames(gene_annotations)[
                        (is.null(input$feature_types) || length(input$feature_types) == 0 || gene_annotations$feature %in% input$feature_types) &
                            (is.null(input$seq_types) || length(input$seq_types) == 0 || gene_annotations$seq_type %in% input$seq_types) &
                            (is.null(input$gene_classes) || length(input$gene_classes) == 0 || gene_annotations$class %in% input$gene_classes)
                    ]

                    # Subset the Seurat object to keep only selected genes
                    filtered_obj <- subset(filtered_obj, features = genes_to_keep)
                }

                # Apply cell filters if specified
                if (input$apply_filters) {
                    # Get cells that pass the filters
                    cells_to_keep <- metadata %>%
                        filter(
                            nCount_RNA >= input$min_nCount,
                            nCount_RNA <= input$max_nCount,
                            nFeature_RNA >= input$min_nFeature,
                            nFeature_RNA <= input$max_nFeature
                        ) %>%
                        pull(barcode.rd1)

                    # Subset the Seurat object to keep only selected cells
                    filtered_obj <- subset(filtered_obj, cells = cells_to_keep)
                }

                return(filtered_obj)
            },
            error = function(e) {
                stop(e$message)
            }
        )
    })

    # Download handler for the filtered Seurat object
    output$downloadRDS <- downloadHandler(
        filename = function() {
            tryCatch(
                {
                    # Create filename based on applied filters
                    filters <- c()

                    if (input$apply_filters) {
                        filters <- c(
                            filters,
                            paste0("cells_nCount_", input$min_nCount, "-", input$max_nCount),
                            paste0("nFeature_", input$min_nFeature, "-", input$max_nFeature)
                        )
                    }

                    if (input$apply_gene_filters) {
                        if (!is.null(input$feature_types) && length(input$feature_types) > 0) {
                            filters <- c(filters, paste0("features_", paste(input$feature_types, collapse = "-")))
                        }
                        if (!is.null(input$seq_types) && length(input$seq_types) > 0) {
                            filters <- c(filters, paste0("seq_", paste(input$seq_types, collapse = "-")))
                        }
                        if (!is.null(input$gene_classes) && length(input$gene_classes) > 0) {
                            filters <- c(filters, paste0("class_", paste(input$gene_classes, collapse = "-")))
                        }
                    }

                    # If no filters applied, indicate it's the full object
                    if (length(filters) == 0) {
                        filters <- "full_object"
                    }

                    filename <- paste0("SeuratObject_filtered_", paste(filters, collapse = "_"), ".rds")
                    return(filename)
                },
                error = function(e) {
                    return("SeuratObject_filtered.rds") # Fallback filename
                }
            )
        },
        content = function(file) {
            tryCatch(
                {
                    # Get the filtered Seurat object
                    filtered_obj <- filteredSeuratObject()
                    # Save the object
                    saveRDS(filtered_obj, file = file)
                },
                error = function(e) {
                    writeLines(paste("Error creating filtered Seurat object:", e$message), file)
                }
            )
        }
    )

    # Protocol plot output - make it reactive to barcode round
    output$protocol_plot <- renderPlotly({
        req(input$protocol_variable, input$barcode_round)
        filtered_data <- get_filtered_data()
        is_numeric <- input$protocol_variable %in% numeric_vars

        create_single_plot(
            data = filtered_data,
            value_column = input$protocol_variable,
            numeric_operation = if (is_numeric) "median" else "median",
            barcode_round = as.numeric(input$barcode_round),
            min_nCount = if (input$apply_filters) input$min_nCount else NULL,
            max_nCount = if (input$apply_filters) input$max_nCount else NULL,
            min_nFeature = if (input$apply_filters) input$min_nFeature else NULL,
            max_nFeature = if (input$apply_filters) input$max_nFeature else NULL,
            feature_types = if (input$apply_gene_filters) input$feature_types else NULL,
            seq_types = if (input$apply_gene_filters) input$seq_types else NULL,
            gene_classes = if (input$apply_gene_filters) input$gene_classes else NULL
        )
    })

    # Knee point filtering
    knee_filter_results <- reactiveVal(NULL)

    # Gestionnaires pour les ajustements fins
    observeEvent(input$decrease_threshold, {
        new_value <- max(0, input$knee_threshold - 0.0001)
        updateNumericInput(session, "knee_threshold", value = new_value)
    })

    observeEvent(input$increase_threshold, {
        new_value <- min(1, input$knee_threshold + 0.0001)
        updateNumericInput(session, "knee_threshold", value = new_value)
    })

    # Gestionnaires pour les ajustements moyens
    observeEvent(input$decrease_threshold_10, {
        new_value <- max(0, input$knee_threshold - 0.001)
        updateNumericInput(session, "knee_threshold", value = new_value)
    })

    observeEvent(input$increase_threshold_10, {
        new_value <- min(1, input$knee_threshold + 0.001)
        updateNumericInput(session, "knee_threshold", value = new_value)
    })

    # Gestionnaires pour les ajustements plus larges
    observeEvent(input$decrease_threshold_100, {
        new_value <- max(0, input$knee_threshold - 0.01)
        updateNumericInput(session, "knee_threshold", value = new_value)
    })

    observeEvent(input$increase_threshold_100, {
        new_value <- min(1, input$knee_threshold + 0.01)
        updateNumericInput(session, "knee_threshold", value = new_value)
    })

    # Modifier l'observeEvent existant pour utiliser directement la valeur
    observeEvent(input$apply_knee_filter, {
        withProgress(message = "Applying knee point filter...", {
            if (input$knee_filter_mode == "global") {
                results <- filter_seurat_knee_point(
                    seurat_obj,
                    threshold = input$knee_threshold,
                    debug = TRUE
                )
            } else {
                results <- filter_seurat_knee_point_by_group(
                    seurat_obj,
                    group_column = input$knee_group_column,
                    threshold = input$knee_threshold,
                    debug = TRUE
                )
            }
            knee_filter_results(results)
        })
    })

    # Observer pour mettre à jour les choix de groupes
    observe({
        req(input$knee_group_column)
        groups <- sort(unique(seurat_obj@meta.data[[input$knee_group_column]]))
        updateSelectizeInput(session, "selected_groups",
            choices = groups,
            selected = if (length(groups) <= 4) groups else groups[1:4]
        )
    })

    output$knee_plot <- renderPlot({
        req(knee_filter_results())
        results <- knee_filter_results()

        if (input$knee_filter_mode == "global") {
            results$plots$knee_plot
        } else {
            # Filtrer les groupes à afficher
            if (input$knee_group_column == "Sample_ID") {
                groups_to_show <- input$selected_groups
                if (is.null(groups_to_show)) {
                    return(plot.new() + text(0.5, 0.5, "Please select groups to display"))
                }
                plot_list <- lapply(groups_to_show, function(group) {
                    if (group %in% names(results$plots)) {
                        results$plots[[group]]$knee_plot +
                            ggtitle(paste("Knee Plot -", group))
                    }
                })
                plot_list <- plot_list[!sapply(plot_list, is.null)]
            } else {
                plot_list <- lapply(names(results$plots), function(group) {
                    results$plots[[group]]$knee_plot +
                        ggtitle(paste("Knee Plot -", group))
                })
            }

            # Ajuster le nombre de colonnes en fonction du nombre de graphiques
            n_plots <- length(plot_list)
            n_cols <- min(2, n_plots)
            grid.arrange(grobs = plot_list, ncol = n_cols)
        }
    })

    output$distance_plot <- renderPlot({
        req(knee_filter_results())
        results <- knee_filter_results()

        if (input$knee_filter_mode == "global") {
            results$plots$distance_plot
        } else {
            # Filtrer les groupes à afficher
            if (input$knee_group_column == "Sample_ID") {
                groups_to_show <- input$selected_groups
                if (is.null(groups_to_show)) {
                    return(plot.new() + text(0.5, 0.5, "Please select groups to display"))
                }
                plot_list <- lapply(groups_to_show, function(group) {
                    if (group %in% names(results$plots)) {
                        results$plots[[group]]$distance_plot +
                            ggtitle(paste("Distance Plot -", group))
                    }
                })
                plot_list <- plot_list[!sapply(plot_list, is.null)]
            } else {
                plot_list <- lapply(names(results$plots), function(group) {
                    results$plots[[group]]$distance_plot +
                        ggtitle(paste("Distance Plot -", group))
                })
            }

            n_plots <- length(plot_list)
            n_cols <- min(2, n_plots)
            grid.arrange(grobs = plot_list, ncol = n_cols)
        }
    })

    output$umi_distribution_plot <- renderPlot({
        req(knee_filter_results())
        results <- knee_filter_results()

        if (input$knee_filter_mode == "global") {
            results$plots$umi_distribution_plot
        } else {
            # Filtrer les groupes à afficher
            if (input$knee_group_column == "Sample_ID") {
                groups_to_show <- input$selected_groups
                if (is.null(groups_to_show)) {
                    return(plot.new() + text(0.5, 0.5, "Please select groups to display"))
                }
                plot_list <- lapply(groups_to_show, function(group) {
                    if (group %in% names(results$plots)) {
                        results$plots[[group]]$umi_distribution_plot +
                            ggtitle(paste("UMI Distribution -", group))
                    }
                })
                plot_list <- plot_list[!sapply(plot_list, is.null)]
            } else {
                plot_list <- lapply(names(results$plots), function(group) {
                    results$plots[[group]]$umi_distribution_plot +
                        ggtitle(paste("UMI Distribution -", group))
                })
            }

            n_plots <- length(plot_list)
            n_cols <- min(2, n_plots)
            grid.arrange(grobs = plot_list, ncol = n_cols)
        }
    })

    output$knee_stats <- renderPrint({
        req(knee_filter_results())
        results <- knee_filter_results()

        cat("Filtering Statistics:\n")
        cat("-------------------\n")

        if (input$knee_filter_mode == "global") {
            # Afficher les statistiques globales existantes
            cat("Knee Point Settings:\n")
            cat("- Knee threshold (transition point):", results$stats$knee_threshold, "\n")
            cat("- UMI threshold (filtering cutoff):", round(results$stats$umi_threshold, 2), "UMIs\n")
            # ... reste des statistiques globales ...
        } else {
            # Afficher les statistiques par groupe
            cat("Group-specific Knee Point Settings:\n")
            cat("--------------------------------\n")
            for (group in names(results$stats$group_stats)) {
                cat(sprintf("\nGroup: %s\n", group))
                cat("- Knee threshold:", results$stats$group_stats[[group]]$knee_threshold, "\n")
                cat("- UMI threshold:", round(results$stats$group_stats[[group]]$umi_threshold, 2), "UMIs\n")
                cat("- Initial cells:", results$stats$group_stats[[group]]$initial_cells, "\n")
                cat("- Filtered cells:", results$stats$group_stats[[group]]$filtered_cells, "\n")
                cat("- Percentage kept:", results$stats$group_stats[[group]]$percent_kept, "%\n")
            }

            cat("\nOverall Statistics:\n")
            cat("-----------------\n")
            cat("- Total initial cells:", results$stats$initial_cells, "\n")
            cat("- Total filtered cells:", results$stats$filtered_cells, "\n")
            cat("- Total removed cells:", results$stats$removed_cells, "\n")
            cat("- Overall percentage kept:", results$stats$percent_kept, "%\n")
        }
    })

    output$knee_filtering_table <- renderTable(
        {
            req(knee_filter_results())
            results <- knee_filter_results()

            if (input$knee_filter_mode == "global") {
                # Tableau pour le mode global
                data.frame(
                    Category = c(
                        "Knee Point Settings",
                        "Knee Point Settings",
                        "Cell Statistics",
                        "Cell Statistics",
                        "Cell Statistics",
                        "Cell Statistics",
                        "UMI Distribution",
                        "UMI Distribution",
                        "UMI Distribution"
                    ),
                    Metric = c(
                        "Knee threshold (transition point)",
                        "UMI threshold (filtering cutoff)",
                        "Initial cells",
                        "Filtered cells",
                        "Removed cells",
                        "Percentage kept",
                        "Mean UMIs per cell",
                        "Median UMIs per cell",
                        "Maximum UMIs per cell"
                    ),
                    Value = c(
                        as.character(results$stats$knee_threshold),
                        paste(round(results$stats$umi_threshold, 2), "UMIs"),
                        as.character(results$stats$initial_cells),
                        as.character(results$stats$filtered_cells),
                        as.character(results$stats$removed_cells),
                        paste0(results$stats$percent_kept, "%"),
                        as.character(round(results$stats$mean_umis, 2)),
                        as.character(round(results$stats$median_umis, 2)),
                        as.character(results$stats$max_umis)
                    )
                )
            } else {
                # Tableau pour le mode par groupe
                # Créer une liste pour stocker les données
                table_data <- list()

                # Ajouter les statistiques pour chaque groupe
                for (group in names(results$stats$group_stats)) {
                    group_stats <- results$stats$group_stats[[group]]
                    table_data[[group]] <- data.frame(
                        Group = group,
                        Category = c(
                            "Knee Point Settings",
                            "Knee Point Settings",
                            "Cell Statistics",
                            "Cell Statistics",
                            "Cell Statistics"
                        ),
                        Metric = c(
                            "Knee threshold",
                            "UMI threshold",
                            "Initial cells",
                            "Filtered cells",
                            "Percentage kept"
                        ),
                        Value = c(
                            as.character(group_stats$knee_threshold),
                            paste(round(group_stats$umi_threshold, 2), "UMIs"),
                            as.character(group_stats$initial_cells),
                            as.character(group_stats$filtered_cells),
                            paste0(group_stats$percent_kept, "%")
                        )
                    )
                }

                # Ajouter les statistiques globales
                table_data[["Overall"]] <- data.frame(
                    Group = "Overall",
                    Category = c(
                        "Overall Statistics",
                        "Overall Statistics",
                        "Overall Statistics",
                        "Overall Statistics"
                    ),
                    Metric = c(
                        "Total initial cells",
                        "Total filtered cells",
                        "Total removed cells",
                        "Overall percentage kept"
                    ),
                    Value = c(
                        as.character(results$stats$initial_cells),
                        as.character(results$stats$filtered_cells),
                        as.character(results$stats$removed_cells),
                        paste0(results$stats$percent_kept, "%")
                    )
                )

                # Combiner tous les tableaux
                do.call(rbind, table_data)
            }
        },
        striped = TRUE,
        hover = TRUE,
        bordered = TRUE
    )
}

# Run the app
shinyApp(ui = ui, server = server)
