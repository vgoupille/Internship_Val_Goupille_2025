# Test script for plotting in R

# Load necessary packages
library(ggplot2)
library(dplyr)

# Create sample data
set.seed(123)
data <- data.frame(
  x = rnorm(100),
  y = rnorm(100),
  group = sample(LETTERS[1:4], 100, replace = TRUE)
)

# Create a basic ggplot visualization
p <- ggplot(data, aes(x = x, y = y, color = group)) +
  geom_point(size = 3, alpha = 0.7) +
  theme_minimal() +
  labs(
    title = "Example Scatter Plot",
    subtitle = "Testing visualization in devcontainer",
    x = "X Variable",
    y = "Y Variable",
    color = "Group"
  )

# Print the plot
print(p)

# Save the plot
ggsave("test_plot.png", p, width = 8, height = 6, dpi = 300) 