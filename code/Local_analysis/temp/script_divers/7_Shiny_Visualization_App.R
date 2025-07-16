# Load required packages
library(shiny)
library(Seurat)
library(dplyr)
library(ggplot2)
library(tidyr)
library(scales)
library(shinythemes)

# =============================================
# Data Loading and Preparation
# =============================================

# Path to the Seurat object
pathSeuratObject <- "data/big_data/RDS_files/SeuratObject_All_Metadata.rds"

# Check if file exists
if (!file.exists(pathSeuratObject)) {
    stop(paste("Error: The file", pathSeuratObject, "does not exist"))
}

# Load Seurat object
seurat_object <- readRDS(pathSeuratObject)

# Get metadata
metadata <- seurat_object@meta.data

# Get all available columns
all_columns <- colnames(metadata)

# Create combined columns for different grouping options
metadata <- metadata %>%
    mutate(
        # Basic combinations
        replicate = paste("Rep", Rep_bio, Rep_tech, sep = "_"),
        timepoint = OD_timepoint,
        culture = Culture_medium,
        sample = Sample_ID,

        # Advanced combinations
        rep_bio_time = paste(Rep_bio, OD_timepoint, sep = "_"),
        rep_tech_time = paste(Rep_tech, OD_timepoint, sep = "_"),
        culture_time = paste(Culture_medium, OD_timepoint, sep = "_"),
        rep_bio_culture = paste(Rep_bio, Culture_medium, sep = "_"),
        rep_tech_culture = paste(Rep_tech, Culture_medium, sep = "_"),
        full_condition = paste(Culture_medium, Rep_bio, Rep_tech, OD_timepoint, sep = "_")
    )

# Get all available columns including combined ones
all_columns <- c(
    # Original columns
    all_columns,
    # Combined columns
    "replicate", "timepoint", "culture", "sample",
    "rep_bio_time", "rep_tech_time", "culture_time",
    "rep_bio_culture", "rep_tech_culture", "full_condition"
)

# =============================================
# Shiny App UI
# =============================================

ui <- fluidPage(
    theme = shinytheme("flatly"),
    titlePanel("Microsplit Data Visualization"),
    sidebarLayout(
        sidebarPanel(
            width = 3,

            # Plot type selection
            selectInput("plot_type", "Plot Type:",
                choices = c(
                    "Box Plot" = "box",
                    "Violin Plot" = "violin",
                    "Scatter Plot" = "scatter"
                )
            ),

            # Y-axis variable selection
            selectInput("y_var", "Y-axis Variable:",
                choices = c(
                    "RNA Counts" = "nCount_RNA",
                    "RNA Features" = "nFeature_RNA"
                )
            ),

            # X-axis grouping selection
            selectInput("x_group", "X-axis Grouping:",
                choices = list(
                    "Original Columns" = all_columns[!grepl("^rep_|^culture_|^full_", all_columns)],
                    "Combined Columns" = c(
                        "Replicate (Rep_bio_Rep_tech)" = "replicate",
                        "Timepoint" = "timepoint",
                        "Culture Medium" = "culture",
                        "Sample ID" = "sample",
                        "Rep Bio + Timepoint" = "rep_bio_time",
                        "Rep Tech + Timepoint" = "rep_tech_time",
                        "Culture + Timepoint" = "culture_time",
                        "Rep Bio + Culture" = "rep_bio_culture",
                        "Rep Tech + Culture" = "rep_tech_culture",
                        "Full Condition" = "full_condition"
                    )
                )
            ),

            # Facet row selection
            selectInput("facet_row", "Facet Row:",
                choices = c(
                    "None" = ".",
                    all_columns[!grepl("^nCount_|^nFeature_", all_columns)]
                )
            ),

            # Facet column selection
            selectInput("facet_col", "Facet Column:",
                choices = c(
                    "None" = ".",
                    all_columns[!grepl("^nCount_|^nFeature_", all_columns)]
                )
            ),

            # Log scale option
            checkboxInput("log_scale", "Log Scale", value = TRUE),

            # Point size for scatter plot
            conditionalPanel(
                condition = "input.plot_type == 'scatter'",
                sliderInput("point_size", "Point Size:",
                    min = 0.1, max = 2, value = 0.5, step = 0.1
                )
            ),

            # Download button
            downloadButton("download_plot", "Download Plot")
        ),
        mainPanel(
            width = 9,
            plotOutput("plot", height = "800px")
        )
    )
)

# =============================================
# Shiny App Server
# =============================================

server <- function(input, output, session) {
    # Create reactive plot
    plot_reactive <- reactive({
        # Base plot
        p <- ggplot(metadata, aes(
            x = .data[[input$x_group]],
            y = .data[[input$y_var]],
            fill = .data[[input$x_group]]
        )) +
            theme_minimal() +
            theme(
                axis.text.x = element_text(angle = 45, hjust = 1, size = 10),
                strip.text = element_text(size = 12),
                panel.spacing = unit(1, "lines"),
                legend.position = "none"
            )

        # Add plot type
        if (input$plot_type == "box") {
            p <- p + geom_boxplot()
        } else if (input$plot_type == "violin") {
            p <- p + geom_violin()
        } else if (input$plot_type == "scatter") {
            p <- p + geom_point(alpha = input$point_size) +
                aes(color = .data[[input$x_group]]) +
                theme(legend.position = "right")
        }

        # Add faceting
        if (input$facet_row != "." || input$facet_col != ".") {
            # Check if the same variable is selected for both facets
            if (input$facet_row != "." && input$facet_col != "." &&
                input$facet_row == input$facet_col) {
                # If same variable, only use it once
                facet_formula <- paste(input$facet_row, "~ .")
            } else {
                facet_formula <- paste(input$facet_row, "~", input$facet_col)
            }
            p <- p + facet_grid(as.formula(facet_formula), scales = "free_x")
        }

        # Add log scale if selected
        if (input$log_scale && input$y_var == "nCount_RNA") {
            p <- p + scale_y_log10() + annotation_logticks(sides = "l")
        }

        # Update labels
        p <- p + labs(
            title = paste(
                "Distribution of",
                ifelse(input$y_var == "nCount_RNA", "RNA Counts", "RNA Features"),
                "by", input$x_group
            ),
            x = input$x_group,
            y = ifelse(input$y_var == "nCount_RNA", "Number of RNA Counts", "Number of RNA Features")
        )

        return(p)
    })

    # Render plot
    output$plot <- renderPlot({
        plot_reactive()
    })

    # Download plot
    output$download_plot <- downloadHandler(
        filename = function() {
            paste("microsplit_plot_", format(Sys.time(), "%Y%m%d_%H%M%S"), ".pdf", sep = "")
        },
        content = function(file) {
            pdf(file, width = 15, height = 10)
            print(plot_reactive())
            dev.off()
        }
    )
}

# Run the app
shinyApp(ui = ui, server = server)
