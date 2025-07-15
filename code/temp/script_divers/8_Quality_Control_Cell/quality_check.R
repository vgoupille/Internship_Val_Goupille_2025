# Import the libraries
library(Seurat)
library(ggplot2)
library(patchwork)




# Import the rds file

seurat_object <- readRDS("data/big_data/RDS_files/Seurat_Object_filtered-CDS_Metadata.rds")
# Show the first 6 rows of the object
head(seurat_object)
# show the number of cells
ncol(seurat_object)
# show the number of genes
nrow(seurat_object)



# Filter the cells with less than 200 counts
seurat_object_filtered <- subset(seurat_object, subset = nCount_RNA > 200)
# Show the number of cells after filtering
ncol(seurat_object_filtered)

# show the max and min of the counts
max(seurat_object_filtered$nCount_RNA)
min(seurat_object_filtered$nCount_RNA)
mean(seurat_object_filtered$nCount_RNA)
median(seurat_object_filtered$nCount_RNA)

# show the max and min of the genes
max(seurat_object_filtered$nFeature_RNA)
min(seurat_object_filtered$nFeature_RNA)





seurat_object_filtered
str(seurat_object_filtered)
head(seurat_object_filtered)


VlnPlot(seurat_object_filtered, features = c("nFeature_RNA", "nCount_RNA"), ncol = 2, pt.size = 0.1, group.by = "Condition", raster = TRUE) # group by the Condition

FeatureScatter(seurat_object_filtered, feature1 = "nCount_RNA", feature2 = "nFeature_RNA", group.by = "Condition", split.by = "Condition", raster = TRUE)



# cela va crash car il y trop de point
VlnPlot(seurat_object, features = c("nFeature_RNA", "nCount_RNA"), ncol = 2, pt.size = 0.1, group.by = "Condition", raster = TRUE) # group by the Condition

FeatureScatter(seurat_object, feature1 = "nCount_RNA", feature2 = "nFeature_RNA", group.by = "Condition", split.by = "Condition", raster = TRUE)





# Save the seurat object
