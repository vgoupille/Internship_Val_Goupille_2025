# Test Shiny App for Bioinformatics

library(shiny)
library(ggplot2)
library(dplyr)

# Generate example data for a simulated RNA-seq experiment
set.seed(42)
gene_count <- 1000
sample_count <- 20

# Gene expression data (normalized counts)
gene_ids <- paste0("GENE_", 1:gene_count)
sample_ids <- paste0("SAMPLE_", 1:sample_count)
condition <- rep(c("Control", "Treatment"), each = sample_count/2)

# Create count matrix
counts <- matrix(
  rnbinom(gene_count * sample_count, mu = 100, size = 1),
  nrow = gene_count,
  ncol = sample_count,
  dimnames = list(gene_ids, sample_ids)
)

# Add fold changes for some "differential" genes
de_genes <- sample(1:gene_count, 100)
counts[de_genes, condition == "Treatment"] <- 
  counts[de_genes, condition == "Treatment"] * runif(100, 2, 5)

# Convert to data frame for plotting
counts_df <- as.data.frame(counts)
counts_df$gene_id <- rownames(counts_df)
counts_long <- tidyr::pivot_longer(
  counts_df, 
  cols = -gene_id, 
  names_to = "sample", 
  values_to = "counts"
)

# Add condition information
sample_info <- data.frame(
  sample = sample_ids,
  condition = condition
)
counts_long <- left_join(counts_long, sample_info, by = "sample")

# Define UI
ui <- fluidPage(
  titlePanel("RNA-seq Explorer"),
  
  sidebarLayout(
    sidebarPanel(
      selectInput("gene", "Select Gene:", choices = gene_ids),
      radioButtons("transform", "Transformation:", 
                   choices = c("None", "Log2", "Log10"), selected = "Log2"),
      hr(),
      helpText("This is a sample Shiny app for testing the devcontainer.")
    ),
    
    mainPanel(
      plotOutput("boxPlot"),
      plotOutput("heatmap")
    )
  )
)

# Define server
server <- function(input, output) {
  
  # Get data for selected gene
  selectedData <- reactive({
    gene <- input$gene
    data <- counts_long %>% 
      filter(gene_id == gene)
    
    # Apply transformation
    if(input$transform == "Log2") {
      data$counts <- log2(data$counts + 1)
    } else if(input$transform == "Log10") {
      data$counts <- log10(data$counts + 1)
    }
    
    data
  })
  
  # Box plot
  output$boxPlot <- renderPlot({
    data <- selectedData()
    
    ggplot(data, aes(x = condition, y = counts, fill = condition)) +
      geom_boxplot() +
      geom_jitter(width = 0.2, alpha = 0.6) +
      labs(title = paste("Expression of", input$gene),
           y = paste0("Expression (", input$transform, ")"),
           x = "Condition") +
      theme_minimal()
  })
  
  # Heatmap for related genes
  output$heatmap <- renderPlot({
    # Select 20 random genes including the selected one
    related_genes <- c(input$gene, sample(setdiff(gene_ids, input$gene), 19))
    
    # Get data for these genes
    heat_data <- counts_long %>%
      filter(gene_id %in% related_genes)
    
    # Apply transformation
    if(input$transform == "Log2") {
      heat_data$counts <- log2(heat_data$counts + 1)
    } else if(input$transform == "Log10") {
      heat_data$counts <- log10(heat_data$counts + 1)
    }
    
    # Create heatmap
    ggplot(heat_data, aes(x = sample, y = gene_id, fill = counts)) +
      geom_tile() +
      scale_fill_viridis_c() +
      theme_minimal() +
      theme(axis.text.x = element_text(angle = 90, hjust = 1, size = 8),
            axis.text.y = element_text(size = 8)) +
      labs(title = "Expression Heatmap",
           fill = paste0("Expression (", input$transform, ")"))
  })
}

# Run the application
shinyApp(ui = ui, server = server) 