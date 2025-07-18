# Test script for interactive HTML widgets
# Example based on the RamiKrispin/vscode-r repo

# Load required packages
library(plotly)
library(dplyr)

# Create example data for bioinformatics
set.seed(42)

# Simulate gene expression data
gene_count <- 100
sample_count <- 20

# Expression matrix
expression_data <- matrix(
    rnorm(gene_count * sample_count, mean = 5, sd = 2),
    nrow = gene_count,
    ncol = sample_count
)

# Add names
gene_names <- paste0("Gene_", 1:gene_count)
sample_names <- paste0("Sample_", 1:sample_count)
rownames(expression_data) <- gene_names
colnames(expression_data) <- sample_names

# Simulate experimental conditions
conditions <- factor(rep(c("Control", "Treatment"), each = sample_count / 2))
names(conditions) <- sample_names

# Convert to data frame for Plotly
expression_df <- as.data.frame(t(expression_data))
expression_df$Sample <- rownames(expression_df)
expression_df$Condition <- conditions

# Select a few genes for a heatmap
selected_genes <- gene_names[1:20]

# Create an interactive heatmap with plotly
heatmap_data <- expression_df %>%
    select(c("Sample", "Condition", all_of(selected_genes))) %>%
    tidyr::pivot_longer(
        cols = all_of(selected_genes),
        names_to = "Gene",
        values_to = "Expression"
    )

# Create the interactive plot
p <- plot_ly(
    data = heatmap_data,
    x = ~Gene,
    y = ~Sample,
    z = ~Expression,
    color = ~Expression,
    type = "heatmap",
    colors = colorRamp(c("blue", "white", "red")),
    text = ~ paste(
        "Gene:", Gene, "<br>Sample:", Sample,
        "<br>Expression:", round(Expression, 2),
        "<br>Condition:", Condition
    )
) %>%
    layout(
        title = "Gene Expression Heatmap",
        xaxis = list(title = "Genes"),
        yaxis = list(title = "Samples")
    )

# Display the plot
p

# Create an interactive boxplot by condition
p2 <- plot_ly(
    data = heatmap_data,
    y = ~Expression,
    color = ~Condition,
    type = "box",
    boxpoints = "all",
    jitter = 0.3,
    pointpos = 0
) %>%
    layout(
        title = "Expression Distribution by Condition",
        xaxis = list(title = "Condition"),
        yaxis = list(title = "Expression Level")
    )

# Display the boxplot
p2

# Create an interactive scatter plot
# Simulate metadata
metadata <- data.frame(
    Sample = sample_names,
    Age = runif(sample_count, min = 20, max = 80),
    Sex = sample(c("M", "F"), sample_count, replace = TRUE),
    Condition = conditions
)

# Reduce dimensionality for visualization (PCA simulation)
pca_data <- data.frame(
    Sample = sample_names,
    PC1 = rnorm(sample_count),
    PC2 = rnorm(sample_count)
)

# Combine with metadata
pca_data <- merge(pca_data, metadata, by = "Sample")

# Create the scatter plot
p3 <- plot_ly(
    data = pca_data,
    x = ~PC1,
    y = ~PC2,
    color = ~Condition,
    symbol = ~Sex,
    size = ~Age,
    type = "scatter",
    mode = "markers",
    marker = list(
        opacity = 0.7,
        line = list(width = 1, color = "black")
    ),
    text = ~ paste(
        "Sample:", Sample, "<br>Age:", round(Age),
        "<br>Sex:", Sex, "<br>Condition:", Condition
    )
) %>%
    layout(
        title = "PCA of Gene Expression Data",
        xaxis = list(title = "PC1"),
        yaxis = list(title = "PC2")
    )

# Display the scatter plot
p3
