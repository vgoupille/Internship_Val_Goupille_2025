# %%
data_all.var

# Remplacer les noms de gènes dans l'objet AnnData
data_all.var["original_gene_ids"] = (
    data_all.var_names
)  # Optionnel : garder les anciens noms
data_all.var_names = data_all.var["final_gene_name"]

print("✅ Les noms de gènes ont été remplacés avec succès par 'final_gene_name'.")

data_all.var.head()


# %%

# Check what groups are actually available
print("Available groups:", data_all.obs["Group"].unique())

# Filter for the correct group name - adjust based on what's actually available
# Based on the pattern, it might be "M9F_OD1" instead of "M9F_0D1"
adata_M9F_OD1 = data_all[data_all.obs["Group"] == "M9F_OD1"]

print(f"Filtered data shape: {adata_M9F_OD1.shape}")


#### BACSC

# %%

### Filter cells

"""
Cell and Gene Filtering

This section performs basic quality filtering on the data with manually set parameters:

1. Cell filtering:
   - Removes cells with less than 100 genes expressed
   - Filters outliers based on median absolute deviation of counts

2. Gene filtering:
   - Removes genes present in less than 5 cells

Note: The outlier filtering based on count MAD does not remove any additional cells in this case.
"""


data_gene = ut.filter_outliers(data_all, nmads=5, min_cells=2, min_genes=100)
print(data_all.obs.outlier.value_counts())
print(f"Total number of cells: {data_all.n_obs}")
print(f"Number of cells after filtering: {data_gene.n_obs}")
data_gene


g = sc.pl.scatter(
    data_all,
    x="total_counts",
    y="n_genes_by_counts",
    color="outlier",
    show=False,
    size=15,
    color_map="flare",
    title="Sequencing depth of cells (before outlier removal)",
)
g.set(xlabel="Sequencing depth")
g.set(ylabel="Number of unique genes")
plt.tight_layout()
plt.show()


sc.pl.scatter(data_gene, x="total_counts", y="n_genes_by_counts", show=False, size=15)
plt.title("Sequencing depth of cells (after outlier removal)")
plt.xlabel("Sequencing depth")
plt.ylabel("Number of unique genes")
plt.show()


# %%
# Create a scatter plot for each culture medium
for medium in data_gene.obs["CultureMedium"].unique():
    # Filter data for current medium
    data_medium = data_gene[data_gene.obs["CultureMedium"] == medium]

    # Create scatter plot
    sc.pl.scatter(
        data_medium, x="total_counts", y="n_genes_by_counts", show=False, size=15
    )
    plt.title(f"Sequencing depth of cells - {medium} medium")
    plt.xlabel("Sequencing depth")
    plt.ylabel("Number of unique genes")
    plt.show()


# %%


# %%

data_gene.var["gene_pass_union_OD_15pct"].value_counts()

# %%
# Filter genes that are expressed in at least 15% of cells in any condition

# Create a mask for genes that pass the 15% threshold and are present in current data
genes_to_keep_mask = data_gene.var["gene_pass_union_OD_15pct"] == True
data_gene_filtered_15pct = data_gene[:, genes_to_keep_mask]
# %%
# Update the data object with filtered genes
data_gene = data_gene_filtered_15pct.copy()


# %%
data_gene.var
