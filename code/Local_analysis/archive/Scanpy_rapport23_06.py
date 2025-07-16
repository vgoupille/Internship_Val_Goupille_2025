# %% [markdown]
# # 1. Set up the environment

# %%
import sys
import os
import pprint as pp
import numpy as np

os.chdir("/Users/valentingoupille/Desktop/microsplit_DOL")


# %% [markdown]
# # 2. Import packages

# %%

import anndata as ad
import pandas as pd
import scanpy as sc
import matplotlib.pyplot as plt
import seaborn as sns

# %%
# Store the path in a variable
path_to_anndata = "data/anndata_objects_with_complete_metadata/"
# Check the directory with the anndata objects
print("Available anndata objects:")
print(os.listdir(path_to_anndata))
# %%
adata_original = ad.read_h5ad(
    path_to_anndata + "GeneFull_raw_unique_mult_with_metadata.h5ad"
)

# %%
adata = adata_original.copy()


# %% Load annotation file and update Chromosome column
print("Loading annotation file...")
annotation_df = pd.read_csv("data/tab/extracted_features_no_duplicates.tsv", sep="\t")
print(
    f"Annotation file loaded with {len(annotation_df)} rows and columns: {annotation_df.columns.tolist()}"
)

# Check if final_gene_name column exists in annotation
if "final_gene_name" in annotation_df.columns:
    print("'final_gene_name' column found in annotation file")

    # Create a mapping from final_gene_name to seq_type
    gene_to_seqtype = dict(
        zip(annotation_df["final_gene_name"], annotation_df["seq_type"])
    )

    # Check how many genes in adata.var_names are in the annotation
    genes_in_annotation = [gene for gene in adata.var_names if gene in gene_to_seqtype]
    print(
        f"Number of genes in adata that are in annotation: {len(genes_in_annotation)} out of {len(adata.var_names)}"
    )

    # Update the Chromosome column in adata.var
    if "Chromosome" in adata.var.columns:
        print("Updating existing Chromosome column...")
        # Create a new chromosome mapping
        new_chromosome_values = []
        for gene in adata.var_names:
            if gene in gene_to_seqtype:
                new_chromosome_values.append(gene_to_seqtype[gene])
            else:
                new_chromosome_values.append("unknown")

        adata.var["Chromosome"] = new_chromosome_values
        print("Chromosome column updated successfully!")

        # Show unique values in the updated Chromosome column
        unique_chromosomes = adata.var["Chromosome"].unique()
        print(f"Unique values in updated Chromosome column: {unique_chromosomes}")

        # Count genes per chromosome
        chromosome_counts = adata.var["Chromosome"].value_counts()
        print("Number of genes per chromosome:")
        for chrom, count in chromosome_counts.items():
            print(f"  {chrom}: {count} genes")
    else:
        print("Chromosome column not found in adata.var, creating new column...")
        # Create new chromosome mapping
        new_chromosome_values = []
        for gene in adata.var_names:
            if gene in gene_to_seqtype:
                new_chromosome_values.append(gene_to_seqtype[gene])
            else:
                new_chromosome_values.append("unknown")

        adata.var["Chromosome"] = new_chromosome_values
        print("New Chromosome column created successfully!")

        # Show unique values in the new Chromosome column
        unique_chromosomes = adata.var["Chromosome"].unique()
        print(f"Unique values in new Chromosome column: {unique_chromosomes}")

        # Count genes per chromosome
        chromosome_counts = adata.var["Chromosome"].value_counts()
        print("Number of genes per chromosome:")
        for chrom, count in chromosome_counts.items():
            print(f"  {chrom}: {count} genes")
else:
    print("'final_gene_name' column not found in annotation file!")
    print("Available columns in annotation file:")
    pp.pprint(annotation_df.columns.tolist())

# %%
adata


# %%
for col in ["CultureMedium", "OD", "RepBio", "RepTech"]:
    print(f"🧬 Column: {col}")
    print(f"🔢 Number of unique values: {len(adata.obs[col].unique())}")
    print(f"📋 Unique values: {adata.obs[col].unique()}\n")


# %%
# Calculate simple statistics
adata.obs["n_counts"] = adata.X.sum(axis=1).A1  # total counts
adata.obs["n_genes"] = (adata.X > 0).sum(axis=1).A1  # number of detected genes

# %%
# Filter cells with n_counts < 100
print(f"📊 Before filtering: {adata.n_obs} cells")

# Create mask for cells to keep (n_counts >= 100)
cells_to_keep = adata.obs["n_counts"] >= 100

# Apply filtering
adata_filtered = adata[cells_to_keep, :].copy()

print(f"📊 After filtering (n_counts >= 100): {adata_filtered.n_obs} cells")
print(f"🗑️ Removed {adata.n_obs - adata_filtered.n_obs} cells")

# Update adata to the filtered version
adata = adata_filtered

# Show summary statistics after filtering
print(f"\n📈 Summary statistics after filtering:")
print(f"   Mean n_counts: {adata.obs['n_counts'].mean():.2f}")
print(f"   Median n_counts: {adata.obs['n_counts'].median():.2f}")
print(f"   Min n_counts: {adata.obs['n_counts'].min():.2f}")
print(f"   Max n_counts: {adata.obs['n_counts'].max():.2f}")

# %%
# Get unique culture mediums and create color map
culture_mediums = adata.obs["CultureMedium"].unique()
# Create color map with red for M9 and green for M9F
color_map = {}
for medium in culture_mediums:
    if "M9" in medium and "F" not in medium:  # M9
        color_map[medium] = "#FF6B6B"  # Red
    elif "M9F" in medium:  # M9F
        color_map[medium] = "#2ECC71"  # Green
    else:  # Other mediums
        color_map[medium] = "#95A5A6"  # Gray for other

# Print statistics by culture medium
print(f"\n🍽️ Statistics by Culture Medium:")
for medium in culture_mediums:
    mask = adata.obs["CultureMedium"] == medium
    medium_data = adata.obs.loc[mask]
    print(f"\n   {medium}:")
    print(f"     Cells: {len(medium_data):,}")
    print(f"     Mean n_counts: {medium_data['n_counts'].mean():.0f}")
    print(f"     Mean n_genes: {medium_data['n_genes'].mean():.0f}")

# %%
# Create separate scatter plots for each culture medium
n_mediums = len(culture_mediums)
n_cols = min(3, n_mediums)  # Maximum 3 columns
n_rows = (n_mediums + n_cols - 1) // n_cols  # Calculate number of rows needed

fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows))
if n_rows == 1:
    axes = axes.reshape(1, -1)
if n_cols == 1:
    axes = axes.reshape(-1, 1)

# Flatten axes for easier iteration
axes_flat = axes.flatten()

# Calculate global min/max for consistent scaling
global_x_min = adata.obs["n_counts"].min()
global_x_max = adata.obs["n_counts"].max()
global_y_min = adata.obs["n_genes"].min()
global_y_max = adata.obs["n_genes"].max()

# Add 5% padding to global limits
x_padding = (global_x_max - global_x_min) * 0.05
y_padding = (global_y_max - global_y_min) * 0.05

global_x_lim = (global_x_min - x_padding, global_x_max + x_padding)
global_y_lim = (global_y_min - y_padding, global_y_max + y_padding)

for i, medium in enumerate(culture_mediums):
    ax = axes_flat[i]

    # Get data for this medium
    mask = adata.obs["CultureMedium"] == medium
    medium_data = adata.obs.loc[mask]

    # Create scatter plot
    ax.scatter(
        medium_data["n_counts"],
        medium_data["n_genes"],
        alpha=0.7,
        s=15,
        c=color_map[medium],
        edgecolors="none",
    )

    # Calculate correlation for this medium
    if len(medium_data) > 1:
        corr = np.corrcoef(medium_data["n_counts"], medium_data["n_genes"])[0, 1]
        # Position correlation text in upper right corner
        ax.text(
            0.98,
            0.98,
            f"Correlation: {corr:.3f}",
            transform=ax.transAxes,
            fontsize=9,
            ha="right",
            va="top",
            bbox=dict(
                boxstyle="round,pad=0.3", facecolor="white", alpha=0.9, edgecolor="gray"
            ),
        )

    # Add barcode count in upper left corner
    barcode_text = f"Barcodes: {len(medium_data):,}"
    ax.text(
        0.02,
        0.98,
        barcode_text,
        transform=ax.transAxes,
        fontsize=8,
        ha="left",
        va="top",
        bbox=dict(
            boxstyle="round,pad=0.3", facecolor="white", alpha=0.9, edgecolor="gray"
        ),
    )

    # Customize subplot
    ax.set_xlabel("Total Counts", fontsize=10, fontweight="bold")
    ax.set_ylabel("Number of Genes", fontsize=10, fontweight="bold")
    ax.set_title(f"{medium}", fontsize=12, fontweight="bold", pad=10)
    ax.grid(True, alpha=0.3, linestyle="--")

    # Set consistent axis limits for all subplots
    ax.set_xlim(global_x_lim)
    ax.set_ylim(global_y_lim)

# Hide empty subplots
for i in range(len(culture_mediums), len(axes_flat)):
    axes_flat[i].set_visible(False)

plt.suptitle(
    "Cell Quality by Culture Medium (Filtered: n_counts ≥ 100)",
    fontsize=16,
    fontweight="bold",
    y=0.98,
)
plt.tight_layout()
plt.show()

# Print detailed statistics for each medium
print(f"\n📊 Detailed Statistics by Culture Medium (After filtering: n_counts ≥ 100):")
for medium in culture_mediums:
    mask = adata.obs["CultureMedium"] == medium
    medium_data = adata.obs.loc[mask]

    print(f"\n🍽️ {medium}:")
    print(f"   📊 Total cells: {len(medium_data):,}")
    print(
        f"   📈 n_counts - Mean: {medium_data['n_counts'].mean():.0f}, Median: {medium_data['n_counts'].median():.0f}"
    )
    print(
        f"   📈 n_counts - Min: {medium_data['n_counts'].min():.0f}, Max: {medium_data['n_counts'].max():.0f}"
    )
    print(
        f"   🧬 n_genes - Mean: {medium_data['n_genes'].mean():.0f}, Median: {medium_data['n_genes'].median():.0f}"
    )
    print(
        f"   🧬 n_genes - Min: {medium_data['n_genes'].min():.0f}, Max: {medium_data['n_genes'].max():.0f}"
    )

    if len(medium_data) > 1:
        corr = np.corrcoef(medium_data["n_counts"], medium_data["n_genes"])[0, 1]
        print(f"   🔗 Correlation n_counts vs n_genes: {corr:.3f}")

# %%
# Create violin plots comparing M9 and M9F
# Filter data for M9 and M9F only
m9_m9f_mask = adata.obs["CultureMedium"].isin(["M9", "M9F"])
adata_m9_m9f = adata[m9_m9f_mask].copy()

if len(adata_m9_m9f) > 0:
    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    # Violin plot for n_counts (top)
    sns.violinplot(
        data=adata_m9_m9f.obs,
        x="CultureMedium",
        y="n_counts",
        ax=ax1,
        palette=["#FF6B6B", "#2ECC71"],
    )
    ax1.set_title(
        "Distribution of Total Counts per Barcode (cell) by Culture Medium",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    ax1.set_xlabel("Culture Medium", fontsize=12, fontweight="bold")
    ax1.set_ylabel("Total Counts per Barcode", fontsize=12, fontweight="bold")
    ax1.grid(True, alpha=0.3, linestyle="--")

    # Add statistics on the plot
    for i, medium in enumerate(["M9", "M9F"]):
        if medium in adata_m9_m9f.obs["CultureMedium"].values:
            medium_data = adata_m9_m9f.obs[adata_m9_m9f.obs["CultureMedium"] == medium]
            median_val = medium_data["n_counts"].median()
            q1_val = medium_data["n_counts"].quantile(0.25)
            q3_val = medium_data["n_counts"].quantile(0.75)

            # Position M9 on the left, M9F on the right
            if medium == "M9":
                ax1.text(
                    0.02,
                    0.98,
                    f"{medium}:\nMedian: {median_val:.0f}\nQ1: {q1_val:.0f}\nQ3: {q3_val:.0f}",
                    transform=ax1.transAxes,
                    fontsize=10,
                    ha="left",
                    va="top",
                    bbox=dict(
                        boxstyle="round,pad=0.3",
                        facecolor="white",
                        alpha=0.9,
                        edgecolor="gray",
                    ),
                )
            else:  # M9F
                ax1.text(
                    0.98,
                    0.98,
                    f"{medium}:\nMedian: {median_val:.0f}\nQ1: {q1_val:.0f}\nQ3: {q3_val:.0f}",
                    transform=ax1.transAxes,
                    fontsize=10,
                    ha="right",
                    va="top",
                    bbox=dict(
                        boxstyle="round,pad=0.3",
                        facecolor="white",
                        alpha=0.9,
                        edgecolor="gray",
                    ),
                )

    # Violin plot for n_genes (bottom)
    sns.violinplot(
        data=adata_m9_m9f.obs,
        x="CultureMedium",
        y="n_genes",
        ax=ax2,
        palette=["#FF6B6B", "#2ECC71"],
    )
    ax2.set_title(
        "Distribution of Genes Detected per Barcode (cell) by Culture Medium",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    ax2.set_xlabel("Culture Medium", fontsize=12, fontweight="bold")
    ax2.set_ylabel("Genes per Barcode", fontsize=12, fontweight="bold")
    ax2.grid(True, alpha=0.3, linestyle="--")

    # Add statistics on the plot
    for i, medium in enumerate(["M9", "M9F"]):
        if medium in adata_m9_m9f.obs["CultureMedium"].values:
            medium_data = adata_m9_m9f.obs[adata_m9_m9f.obs["CultureMedium"] == medium]
            median_val = medium_data["n_genes"].median()
            q1_val = medium_data["n_genes"].quantile(0.25)
            q3_val = medium_data["n_genes"].quantile(0.75)

            # Position M9 on the left, M9F on the right
            if medium == "M9":
                ax2.text(
                    0.02,
                    0.98,
                    f"{medium}:\nMedian: {median_val:.0f}\nQ1: {q1_val:.0f}\nQ3: {q3_val:.0f}",
                    transform=ax2.transAxes,
                    fontsize=10,
                    ha="left",
                    va="top",
                    bbox=dict(
                        boxstyle="round,pad=0.3",
                        facecolor="white",
                        alpha=0.9,
                        edgecolor="gray",
                    ),
                )
            else:  # M9F
                ax2.text(
                    0.98,
                    0.98,
                    f"{medium}:\nMedian: {median_val:.0f}\nQ1: {q1_val:.0f}\nQ3: {q3_val:.0f}",
                    transform=ax2.transAxes,
                    fontsize=10,
                    ha="right",
                    va="top",
                    bbox=dict(
                        boxstyle="round,pad=0.3",
                        facecolor="white",
                        alpha=0.9,
                        edgecolor="gray",
                    ),
                )

    plt.suptitle(
        "Comparison of Cell Quality Metrics: M9 vs M9F (Filtered: n_counts ≥ 100)",
        fontsize=16,
        fontweight="bold",
        y=0.98,
    )
    plt.tight_layout()
    plt.show()

    # Print comparison statistics
    print(f"\n🎻 Violin Plot Comparison: M9 vs M9F")
    print(f"📊 Total cells in comparison: {len(adata_m9_m9f):,}")

    for medium in ["M9", "M9F"]:
        if medium in adata_m9_m9f.obs["CultureMedium"].values:
            medium_data = adata_m9_m9f.obs[adata_m9_m9f.obs["CultureMedium"] == medium]
            print(f"\n🍽️ {medium}:")
            print(f"   📊 Cells: {len(medium_data):,}")
            print(
                f"   📈 n_counts - Mean: {medium_data['n_counts'].mean():.0f}, Median: {medium_data['n_counts'].median():.0f}"
            )
            print(f"   📈 n_counts - Std: {medium_data['n_counts'].std():.0f}")
            print(
                f"   🧬 n_genes - Mean: {medium_data['n_genes'].mean():.0f}, Median: {medium_data['n_genes'].median():.0f}"
            )
            print(f"   🧬 n_genes - Std: {medium_data['n_genes'].std():.0f}")
else:
    print("⚠️ No M9 or M9F data found for violin plot comparison")

# %%
# Create beautiful plot of number of cells per culture medium
plt.figure(figsize=(14, 8))

# Count cells per culture medium BEFORE filtering
cell_counts_before = adata_original.obs["CultureMedium"].value_counts()

# Count cells per culture medium AFTER filtering
cell_counts_after = adata.obs["CultureMedium"].value_counts()

# Create color palette
colors = []
for medium in cell_counts_before.index:
    if "M9" in medium and "F" not in medium:  # M9
        colors.append("#FF6B6B")  # Red
    elif "M9F" in medium:  # M9F
        colors.append("#2ECC71")  # Green
    else:  # Other mediums
        colors.append("#95A5A6")  # Gray for other

# Set up the bar positions
x = np.arange(len(cell_counts_before))
width = 0.35

# Create bar plot
bars_before = plt.bar(
    x - width / 2,
    cell_counts_before.values,
    width,
    color=colors,
    alpha=0.7,
    edgecolor="black",
    linewidth=1,
)
bars_after = plt.bar(
    x + width / 2,
    cell_counts_after.values,
    width,
    color=colors,
    alpha=0.9,
    edgecolor="black",
    linewidth=1,
)

# Customize the plot
plt.title(
    "Number of Barcodes per Culture Medium: Not Filtered vs Filtered (n_counts > 100)",
    fontsize=16,
    fontweight="bold",
    pad=20,
)
plt.xlabel("Culture Medium", fontsize=14, fontweight="bold")
plt.ylabel("Number of Barcodes", fontsize=14, fontweight="bold")

# Set x-axis labels
plt.xticks(
    x, cell_counts_before.index, rotation=0, ha="center", fontsize=12, fontweight="bold"
)

# Add "Before" and "After" labels under each bar group
for i, medium in enumerate(cell_counts_before.index):
    plt.text(
        x[i] - width / 2,
        -max(cell_counts_before.values) * 0.05,
        "Not filtered",
        ha="center",
        va="top",
        fontsize=10,
        fontweight="bold",
    )
    plt.text(
        x[i] + width / 2,
        -max(cell_counts_before.values) * 0.05,
        "Filtered\n(n_counts > 100)",
        ha="center",
        va="top",
        fontsize=10,
        fontweight="bold",
    )

# Add value labels on top of each bar
for bar, count in zip(bars_before, cell_counts_before.values):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + max(cell_counts_before.values) * 0.01,
        f"{count:,}",
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="bold",
    )

for bar, count in zip(bars_after, cell_counts_after.values):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + max(cell_counts_before.values) * 0.01,
        f"{count:,}",
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="bold",
    )

# Add percentage labels inside bars
total_before = cell_counts_before.sum()
total_after = cell_counts_after.sum()

for bar, count in zip(bars_before, cell_counts_before.values):
    percentage = (count / total_before) * 100
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() / 2,
        f"{percentage:.1f}%",
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
        color="black",
        bbox=dict(
            boxstyle="round,pad=0.3", facecolor="white", alpha=0.9, edgecolor="gray"
        ),
    )

for bar, count in zip(bars_after, cell_counts_after.values):
    percentage = (count / total_after) * 100
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() / 2,
        f"{percentage:.1f}%",
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
        color="black",
        bbox=dict(
            boxstyle="round,pad=0.3", facecolor="white", alpha=0.9, edgecolor="gray"
        ),
    )

# Add grid for better readability
plt.grid(True, alpha=0.3, linestyle="--", axis="y")

# Add total counts in the upper right corner
total_text = f"Total Not filtered: {total_before:,}\nTotal Filtered: {total_after:,}\nRemoved: {total_before - total_after:,}"
plt.text(
    0.98,
    0.98,
    total_text,
    transform=plt.gca().transAxes,
    fontsize=11,
    fontweight="bold",
    ha="right",
    va="top",
    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9, edgecolor="gray"),
)

# Show the plot
plt.show()

# Print detailed statistics
print(f"\n📊 Cell Count Summary: Before vs After Filtering (n_counts ≥ 100):")
print(f"📈 Total barcodes before filtering: {total_before:,}")
print(f"📈 Total barcodes after filtering: {total_after:,}")
print(
    f"🗑️ Barcodes removed: {total_before - total_after:,} ({(total_before - total_after)/total_before*100:.1f}%)"
)

print(f"\n🍽️ Breakdown by Culture Medium:")
for medium in cell_counts_before.index:
    before_count = cell_counts_before[medium]
    after_count = cell_counts_after.get(medium, 0)
    removed_count = before_count - after_count
    removed_percentage = (removed_count / before_count) * 100 if before_count > 0 else 0

    print(f"\n   {medium}:")
    print(f"     Before: {before_count:,} barcodes")
    print(f"     After: {after_count:,} barcodes")
    print(f"     Removed: {removed_count:,} barcodes ({removed_percentage:.1f}%)")

# %%

# Create a beautiful plot showing number of remaining barcodes vs n_counts threshold
print("🔍 Creating threshold analysis plot...")

# Calculate n_counts for the original dataset if not already present
if "n_counts" not in adata_original.obs.columns:
    print("📊 Calculating n_counts for original dataset...")
    adata_original.obs["n_counts"] = adata_original.X.sum(axis=1).A1

# Define threshold range - go up to find threshold for 3000 cells
max_threshold = 5000  # Increase max threshold to find 3000 cells threshold
thresholds = np.arange(
    0, max_threshold + 1, 10
)  # From 0 to max_threshold with step of 10

# Calculate number of cells remaining for each threshold
cells_remaining = []
for threshold in thresholds:
    cells_above_threshold = (adata_original.obs["n_counts"] >= threshold).sum()
    cells_remaining.append(cells_above_threshold)

# Convert to numpy array for easier manipulation
cells_remaining = np.array(cells_remaining)

# Find threshold for 3000 cells
target_cells = 3000
threshold_3000 = None
for i, threshold in enumerate(thresholds):
    if cells_remaining[i] <= target_cells:
        threshold_3000 = threshold
        break

if threshold_3000 is None:
    print(
        f"⚠️ Warning: Could not find threshold for {target_cells} cells. Using max threshold."
    )
    threshold_3000 = max_threshold

print(f"🎯 Threshold for {target_cells} cells: {threshold_3000}")

# Create the plot
plt.figure(figsize=(16, 10))

# Main plot
plt.plot(
    thresholds,
    cells_remaining,
    linewidth=3,
    color="#3498db",
    alpha=0.8,
    label="Total cells",
)

# Add a vertical line at the current threshold (100)
current_threshold = 100
current_cells = cells_remaining[thresholds == current_threshold][0]
plt.axvline(
    x=current_threshold,
    color="#e74c3c",
    linestyle="--",
    linewidth=2,
    alpha=0.8,
    label=f"Current threshold ({current_threshold})",
)
plt.axhline(y=current_cells, color="#e74c3c", linestyle="--", linewidth=2, alpha=0.8)

# Add vertical line at the 3000 cells threshold
cells_at_3000_threshold = cells_remaining[thresholds == threshold_3000][0]
plt.axvline(
    x=threshold_3000,
    color="#27ae60",
    linestyle="--",
    linewidth=3,
    alpha=0.8,
    label=f"3000 cells threshold ({threshold_3000})",
)
plt.axhline(
    y=cells_at_3000_threshold, color="#27ae60", linestyle="--", linewidth=2, alpha=0.8
)

# Add horizontal line at 50% of total cells
total_cells = cells_remaining[0]
fifty_percent_cells = total_cells * 0.5
plt.axhline(
    y=fifty_percent_cells,
    color="#f39c12",
    linestyle=":",
    linewidth=2,
    alpha=0.8,
    label="50% of total cells",
)

# Add horizontal line at 25% of total cells
twenty_five_percent_cells = total_cells * 0.25
plt.axhline(
    y=twenty_five_percent_cells,
    color="#9b59b6",
    linestyle=":",
    linewidth=2,
    alpha=0.8,
    label="25% of total cells",
)

# Add horizontal line at 10% of total cells
ten_percent_cells = total_cells * 0.1
plt.axhline(
    y=ten_percent_cells,
    color="#34495e",
    linestyle=":",
    linewidth=2,
    alpha=0.8,
    label="10% of total cells",
)

# Find threshold for 50%, 25%, and 10% of cells
threshold_50 = (
    thresholds[cells_remaining <= fifty_percent_cells][0]
    if len(thresholds[cells_remaining <= fifty_percent_cells]) > 0
    else None
)
threshold_25 = (
    thresholds[cells_remaining <= twenty_five_percent_cells][0]
    if len(thresholds[cells_remaining <= twenty_five_percent_cells]) > 0
    else None
)
threshold_10 = (
    thresholds[cells_remaining <= ten_percent_cells][0]
    if len(thresholds[cells_remaining <= ten_percent_cells]) > 0
    else None
)

# Add vertical lines for these thresholds
if threshold_50:
    plt.axvline(x=threshold_50, color="#f39c12", linestyle=":", linewidth=2, alpha=0.8)
if threshold_25:
    plt.axvline(x=threshold_25, color="#9b59b6", linestyle=":", linewidth=2, alpha=0.8)
if threshold_10:
    plt.axvline(x=threshold_10, color="#34495e", linestyle=":", linewidth=2, alpha=0.8)

# Add annotations for key points
plt.annotate(
    f"Current: {current_cells:,} cells\nat threshold {current_threshold}",
    xy=(current_threshold, current_cells),
    xytext=(current_threshold + 100, current_cells + total_cells * 0.1),
    arrowprops=dict(arrowstyle="->", color="#e74c3c", alpha=0.8),
    fontsize=10,
    fontweight="bold",
    bbox=dict(
        boxstyle="round,pad=0.3", facecolor="white", alpha=0.9, edgecolor="#e74c3c"
    ),
)

# Add annotation for 3000 cells threshold
plt.annotate(
    f"{target_cells} cells: {cells_at_3000_threshold:,} cells\nat threshold {threshold_3000}",
    xy=(threshold_3000, cells_at_3000_threshold),
    xytext=(threshold_3000 + 100, cells_at_3000_threshold + total_cells * 0.05),
    arrowprops=dict(arrowstyle="->", color="#27ae60", alpha=0.8),
    fontsize=10,
    fontweight="bold",
    bbox=dict(
        boxstyle="round,pad=0.3", facecolor="white", alpha=0.9, edgecolor="#27ae60"
    ),
)

if threshold_50:
    cells_at_50 = cells_remaining[thresholds == threshold_50][0]
    plt.annotate(
        f"50%: {cells_at_50:,} cells\nat threshold {threshold_50}",
        xy=(threshold_50, cells_at_50),
        xytext=(threshold_50 + 100, cells_at_50 + total_cells * 0.05),
        arrowprops=dict(arrowstyle="->", color="#f39c12", alpha=0.8),
        fontsize=9,
        fontweight="bold",
        bbox=dict(
            boxstyle="round,pad=0.3", facecolor="white", alpha=0.9, edgecolor="#f39c12"
        ),
    )

if threshold_25:
    cells_at_25 = cells_remaining[thresholds == threshold_25][0]
    plt.annotate(
        f"25%: {cells_at_25:,} cells\nat threshold {threshold_25}",
        xy=(threshold_25, cells_at_25),
        xytext=(threshold_25 + 100, cells_at_25 + total_cells * 0.05),
        arrowprops=dict(arrowstyle="->", color="#9b59b6", alpha=0.8),
        fontsize=9,
        fontweight="bold",
        bbox=dict(
            boxstyle="round,pad=0.3", facecolor="white", alpha=0.9, edgecolor="#9b59b6"
        ),
    )

if threshold_10:
    cells_at_10 = cells_remaining[thresholds == threshold_10][0]
    plt.annotate(
        f"10%: {cells_at_10:,} cells\nat threshold {threshold_10}",
        xy=(threshold_10, cells_at_10),
        xytext=(threshold_10 + 100, cells_at_10 + total_cells * 0.05),
        arrowprops=dict(arrowstyle="->", color="#34495e", alpha=0.8),
        fontsize=9,
        fontweight="bold",
        bbox=dict(
            boxstyle="round,pad=0.3", facecolor="white", alpha=0.9, edgecolor="#34495e"
        ),
    )

# Customize the plot
plt.title(
    "Impact of n_counts Threshold on Cell Retention",
    fontsize=18,
    fontweight="bold",
    pad=20,
)
plt.xlabel("n_counts Threshold", fontsize=14, fontweight="bold")
plt.ylabel("Number of Remaining Cells", fontsize=14, fontweight="bold")

# Set axis limits
plt.xlim(0, max_threshold)
plt.ylim(0, total_cells * 1.05)

# Add grid
plt.grid(True, alpha=0.3, linestyle="--")

# Add legend
plt.legend(loc="upper right", fontsize=12, framealpha=0.9)

# Add statistics in the upper left corner
stats_text = f"Total cells: {total_cells:,}\nCurrent threshold: {current_threshold}\nCells retained: {current_cells:,} ({(current_cells/total_cells)*100:.1f}%)\n{target_cells} cells threshold: {threshold_3000}\nCells at {target_cells} threshold: {cells_at_3000_threshold:,}"
plt.text(
    0.02,
    0.98,
    stats_text,
    transform=plt.gca().transAxes,
    fontsize=11,
    fontweight="bold",
    ha="left",
    va="top",
    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9, edgecolor="gray"),
)

# Show the plot
plt.tight_layout()
plt.show()

# Print detailed statistics
print(f"\n📊 Threshold Analysis Summary:")
print(f"📈 Total cells in dataset: {total_cells:,}")
print(
    f"🎯 Current threshold (n_counts ≥ {current_threshold}): {current_cells:,} cells ({(current_cells/total_cells)*100:.1f}%)"
)
print(
    f"🎯 {target_cells} cells threshold (n_counts ≥ {threshold_3000}): {cells_at_3000_threshold:,} cells ({(cells_at_3000_threshold/total_cells)*100:.1f}%)"
)

if threshold_50:
    print(
        f"🎯 50% threshold (n_counts ≥ {threshold_50}): {cells_remaining[thresholds == threshold_50][0]:,} cells"
    )
if threshold_25:
    print(
        f"🎯 25% threshold (n_counts ≥ {threshold_25}): {cells_remaining[thresholds == threshold_25][0]:,} cells"
    )
if threshold_10:
    print(
        f"🎯 10% threshold (n_counts ≥ {threshold_10}): {cells_remaining[thresholds == threshold_10][0]:,} cells"
    )

# Create a table with more threshold values
print(f"\n📋 Detailed Threshold Table:")
print(
    f"{'Threshold':<10} {'Cells Remaining':<15} {'Percentage':<12} {'Cells Removed':<15}"
)
print("-" * 60)
for threshold in [0, 50, 100, 200, 300, 400, 500, 750, 1000, threshold_3000]:
    if threshold <= max(thresholds):
        cells_remaining_at_threshold = cells_remaining[thresholds == threshold][0]
        percentage = (cells_remaining_at_threshold / total_cells) * 100
        cells_removed = total_cells - cells_remaining_at_threshold
        print(
            f"{threshold:<10} {cells_remaining_at_threshold:<15,} {percentage:<11.1f}% {cells_removed:<15,}"
        )

# %%

# Filter data with the 3000 cells threshold and create violin plots by CultureMedium
print(
    f"\n🎻 Creating violin plots after filtering with threshold {threshold_3000} (target: {target_cells} cells)..."
)

# Filter data with the new threshold
cells_to_keep_3000 = adata_original.obs["n_counts"] >= threshold_3000
adata_filtered_3000 = adata_original[cells_to_keep_3000, :].copy()

print(
    f"📊 After filtering (n_counts ≥ {threshold_3000}): {adata_filtered_3000.n_obs:,} cells"
)

# Calculate n_genes for filtered data
adata_filtered_3000.obs["n_genes"] = (adata_filtered_3000.X > 0).sum(axis=1).A1

# Get unique culture mediums and create color map
culture_mediums_3000 = adata_filtered_3000.obs["CultureMedium"].unique()
color_map_3000 = {}
for medium in culture_mediums_3000:
    if "M9" in medium and "F" not in medium:  # M9
        color_map_3000[medium] = "#FF6B6B"  # Red
    elif "M9F" in medium:  # M9F
        color_map_3000[medium] = "#2ECC71"  # Green
    else:  # Other mediums
        color_map_3000[medium] = "#95A5A6"  # Gray for other

# Create violin plots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

# Violin plot for n_counts (top)
sns.violinplot(
    data=adata_filtered_3000.obs,
    x="CultureMedium",
    y="n_counts",
    ax=ax1,
    palette=color_map_3000,
)
ax1.set_title(
    f"Distribution of Total Counts per Barcode by Culture Medium\n(Filtered: n_counts ≥ {threshold_3000}, {adata_filtered_3000.n_obs:,} cells)",
    fontsize=14,
    fontweight="bold",
    pad=15,
)
ax1.set_xlabel("Culture Medium", fontsize=12, fontweight="bold")
ax1.set_ylabel("Total Counts per Barcode", fontsize=12, fontweight="bold")
ax1.grid(True, alpha=0.3, linestyle="--")

# Add statistics on the plot for n_counts
for i, medium in enumerate(culture_mediums_3000):
    medium_data = adata_filtered_3000.obs[
        adata_filtered_3000.obs["CultureMedium"] == medium
    ]
    median_val = medium_data["n_counts"].median()
    q1_val = medium_data["n_counts"].quantile(0.25)
    q3_val = medium_data["n_counts"].quantile(0.75)
    count_val = len(medium_data)

    # Position text based on medium position
    if i == 0:  # First medium
        ax1.text(
            0.02,
            0.98,
            f"{medium}:\nMedian: {median_val:.0f}\nQ1: {q1_val:.0f}\nQ3: {q3_val:.0f}\nCells: {count_val:,}",
            transform=ax1.transAxes,
            fontsize=10,
            ha="left",
            va="top",
            bbox=dict(
                boxstyle="round,pad=0.3", facecolor="white", alpha=0.9, edgecolor="gray"
            ),
        )
    else:  # Other mediums
        ax1.text(
            0.98,
            0.98 - (i * 0.15),
            f"{medium}:\nMedian: {median_val:.0f}\nQ1: {q1_val:.0f}\nQ3: {q3_val:.0f}\nCells: {count_val:,}",
            transform=ax1.transAxes,
            fontsize=10,
            ha="right",
            va="top",
            bbox=dict(
                boxstyle="round,pad=0.3", facecolor="white", alpha=0.9, edgecolor="gray"
            ),
        )

# Violin plot for n_genes (bottom)
sns.violinplot(
    data=adata_filtered_3000.obs,
    x="CultureMedium",
    y="n_genes",
    ax=ax2,
    palette=color_map_3000,
)
ax2.set_title(
    f"Distribution of Genes Detected per Barcode by Culture Medium\n(Filtered: n_counts ≥ {threshold_3000}, {adata_filtered_3000.n_obs:,} cells)",
    fontsize=14,
    fontweight="bold",
    pad=15,
)
ax2.set_xlabel("Culture Medium", fontsize=12, fontweight="bold")
ax2.set_ylabel("Genes per Barcode", fontsize=12, fontweight="bold")
ax2.grid(True, alpha=0.3, linestyle="--")

# Add statistics on the plot for n_genes
for i, medium in enumerate(culture_mediums_3000):
    medium_data = adata_filtered_3000.obs[
        adata_filtered_3000.obs["CultureMedium"] == medium
    ]
    median_val = medium_data["n_genes"].median()
    q1_val = medium_data["n_genes"].quantile(0.25)
    q3_val = medium_data["n_genes"].quantile(0.75)
    count_val = len(medium_data)

    # Position text based on medium position
    if i == 0:  # First medium
        ax2.text(
            0.02,
            0.98,
            f"{medium}:\nMedian: {median_val:.0f}\nQ1: {q1_val:.0f}\nQ3: {q3_val:.0f}\nCells: {count_val:,}",
            transform=ax2.transAxes,
            fontsize=10,
            ha="left",
            va="top",
            bbox=dict(
                boxstyle="round,pad=0.3", facecolor="white", alpha=0.9, edgecolor="gray"
            ),
        )
    else:  # Other mediums
        ax2.text(
            0.98,
            0.98 - (i * 0.15),
            f"{medium}:\nMedian: {median_val:.0f}\nQ1: {q1_val:.0f}\nQ3: {q3_val:.0f}\nCells: {count_val:,}",
            transform=ax2.transAxes,
            fontsize=10,
            ha="right",
            va="top",
            bbox=dict(
                boxstyle="round,pad=0.3", facecolor="white", alpha=0.9, edgecolor="gray"
            ),
        )

plt.suptitle(
    f"Cell Quality Metrics by Culture Medium\n(Filtered: n_counts ≥ {threshold_3000}, Target: {target_cells} cells)",
    fontsize=16,
    fontweight="bold",
    y=0.98,
)
plt.tight_layout()
plt.show()

# Print detailed statistics for each medium after 3000 threshold filtering
print(f"\n🎻 Violin Plot Statistics (After filtering: n_counts ≥ {threshold_3000}):")
print(f"📊 Total cells after filtering: {len(adata_filtered_3000):,}")

for medium in culture_mediums_3000:
    medium_data = adata_filtered_3000.obs[
        adata_filtered_3000.obs["CultureMedium"] == medium
    ]
    print(f"\n🍽️ {medium}:")
    print(f"   📊 Cells: {len(medium_data):,}")
    print(
        f"   📈 n_counts - Mean: {medium_data['n_counts'].mean():.0f}, Median: {medium_data['n_counts'].median():.0f}"
    )
    print(f"   📈 n_counts - Std: {medium_data['n_counts'].std():.0f}")
    print(
        f"   🧬 n_genes - Mean: {medium_data['n_genes'].mean():.0f}, Median: {medium_data['n_genes'].median():.0f}"
    )
    print(f"   🧬 n_genes - Std: {medium_data['n_genes'].std():.0f}")

# %%

# Create interactive figure with threshold selection
print("🎛️ Creating interactive threshold analysis...")

import ipywidgets as widgets
from IPython.display import display, clear_output
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="seaborn")
warnings.filterwarnings("ignore", category=UserWarning, message=".*missing from font.*")

# Calculate n_counts for the original dataset if not already present
if "n_counts" not in adata_original.obs.columns:
    print("📊 Calculating n_counts for original dataset...")
    adata_original.obs["n_counts"] = adata_original.X.sum(axis=1).A1

# Get the range of possible thresholds
max_n_counts = int(adata_original.obs["n_counts"].max())
min_n_counts = int(adata_original.obs["n_counts"].min())

# Create slider widget
threshold_slider = widgets.IntSlider(
    value=100,
    min=min_n_counts,
    max=max_n_counts,
    step=10,
    description="Threshold:",
    style={"description_width": "initial"},
    layout=widgets.Layout(width="600px"),
)

# Create output widget for plots
output_widget = widgets.Output()


def update_plots(threshold):
    """Update plots based on selected threshold"""
    with output_widget:
        clear_output(wait=True)

        # Filter data with selected threshold
        cells_to_keep = adata_original.obs["n_counts"] >= threshold
        adata_filtered = adata_original[cells_to_keep, :].copy()

        # Calculate n_genes for filtered data
        adata_filtered.obs["n_genes"] = (adata_filtered.X > 0).sum(axis=1).A1

        # Get unique culture mediums and create color map
        culture_mediums = adata_filtered.obs["CultureMedium"].unique()
        color_map = {}
        for medium in culture_mediums:
            if "M9" in medium and "F" not in medium:  # M9
                color_map[medium] = "#FF6B6B"  # Red
            elif "M9F" in medium:  # M9F
                color_map[medium] = "#2ECC71"  # Green
            else:  # Other mediums
                color_map[medium] = "#95A5A6"  # Gray for other

        # Create figure with 3 subplots
        fig = plt.figure(figsize=(20, 12))

        # Violin plots (top row)
        ax1 = plt.subplot(2, 3, 1)
        sns.violinplot(
            data=adata_filtered.obs,
            x="CultureMedium",
            y="n_counts",
            hue="CultureMedium",
            ax=ax1,
            palette=color_map,
            legend=False,
        )
        ax1.set_title(
            f"n_counts Distribution (Threshold: {threshold})",
            fontsize=12,
            fontweight="bold",
        )
        ax1.set_xlabel("Culture Medium", fontsize=10)
        ax1.set_ylabel("Total Counts per Barcode", fontsize=10)
        ax1.tick_params(axis="x", rotation=45)
        ax1.grid(True, alpha=0.3)

        ax2 = plt.subplot(2, 3, 2)
        sns.violinplot(
            data=adata_filtered.obs,
            x="CultureMedium",
            y="n_genes",
            hue="CultureMedium",
            ax=ax2,
            palette=color_map,
            legend=False,
        )
        ax2.set_title(
            f"n_genes Distribution (Threshold: {threshold})",
            fontsize=12,
            fontweight="bold",
        )
        ax2.set_xlabel("Culture Medium", fontsize=10)
        ax2.set_ylabel("Genes per Barcode", fontsize=10)
        ax2.tick_params(axis="x", rotation=45)
        ax2.grid(True, alpha=0.3)

        # Cell count barplot (top right)
        ax3 = plt.subplot(2, 3, 3)
        cell_counts = adata_filtered.obs["CultureMedium"].value_counts()
        colors = [color_map[medium] for medium in cell_counts.index]
        bars = ax3.bar(
            range(len(cell_counts)), cell_counts.values, color=colors, alpha=0.8
        )
        ax3.set_title(
            f"Cell Counts by Culture Medium\n(Threshold: {threshold})",
            fontsize=12,
            fontweight="bold",
        )
        ax3.set_xlabel("Culture Medium", fontsize=10)
        ax3.set_ylabel("Number of Cells", fontsize=10)
        ax3.set_xticks(range(len(cell_counts)))
        ax3.set_xticklabels(cell_counts.index, rotation=45)
        ax3.grid(True, alpha=0.3, axis="y")

        # Add value labels on bars
        for bar, count in zip(bars, cell_counts.values):
            ax3.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(cell_counts.values) * 0.01,
                f"{count:,}",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        # Percentage barplot (bottom left)
        ax4 = plt.subplot(2, 3, 4)
        total_cells = len(adata_filtered)
        percentages = (cell_counts / total_cells) * 100
        bars_pct = ax4.bar(
            range(len(percentages)), percentages.values, color=colors, alpha=0.8
        )
        ax4.set_title(
            f"Percentage of Cells by Culture Medium\n(Threshold: {threshold})",
            fontsize=12,
            fontweight="bold",
        )
        ax4.set_xlabel("Culture Medium", fontsize=10)
        ax4.set_ylabel("Percentage (%)", fontsize=10)
        ax4.set_xticks(range(len(percentages)))
        ax4.set_xticklabels(percentages.index, rotation=45)
        ax4.grid(True, alpha=0.3, axis="y")

        # Add percentage labels on bars
        for bar, pct in zip(bars_pct, percentages.values):
            ax4.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1,
                f"{pct:.1f}%",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        # OD table (bottom center)
        ax5 = plt.subplot(2, 3, 5)
        ax5.axis("off")

        # Count cells by OD
        od_counts = adata_filtered.obs["OD"].value_counts().sort_index()
        od_counts_before = adata_original.obs["OD"].value_counts().sort_index()

        # Create OD statistics text
        od_text = f"📊 CELLS BY OD\n"
        od_text += f"Threshold: {threshold}\n"
        od_text += f"Total cells: {total_cells:,}\n\n"

        od_text += f"OD\tBefore\tAfter\tRemoved\tRetention%\n"
        od_text += f"---\t------\t-----\t-------\t----------\n"

        for od in od_counts_before.index:
            before_count = od_counts_before[od]
            after_count = od_counts.get(od, 0)
            removed_count = before_count - after_count
            retention_pct = (
                (after_count / before_count * 100) if before_count > 0 else 0
            )

            od_text += f"{od}\t{before_count:,}\t{after_count:,}\t{removed_count:,}\t{retention_pct:.1f}%\n"

        ax5.text(
            0.05,
            0.95,
            od_text,
            transform=ax5.transAxes,
            fontsize=9,
            verticalalignment="top",
            fontfamily="monospace",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8),
        )

        # Before vs After comparison (bottom right)
        ax6 = plt.subplot(2, 3, 6)

        # Count cells before and after filtering
        counts_before = adata_original.obs["CultureMedium"].value_counts()
        counts_after = adata_filtered.obs["CultureMedium"].value_counts()

        # Create comparison data
        comparison_data = []
        labels = []
        for medium in counts_before.index:
            before_count = counts_before[medium]
            after_count = counts_after.get(medium, 0)
            comparison_data.extend([before_count, after_count])
            labels.extend([f"{medium}\nBefore", f"{medium}\nAfter"])

        # Create comparison barplot with consistent colors
        x_pos = np.arange(len(labels))
        colors_comp = []
        for i, label in enumerate(labels):
            if "After" in label:
                # Use same color as before but lighter for "After"
                medium = label.split("\n")[0]
                if "M9" in medium and "F" not in medium:
                    colors_comp.append("#FFB6B6")  # Light red for M9 After
                elif "M9F" in medium:
                    colors_comp.append("#A8E6A8")  # Light green for M9F After
                else:
                    colors_comp.append("#D3D3D3")  # Light gray for others After
            else:
                # Use original colors for "Before"
                medium = label.split("\n")[0]
                if "M9" in medium and "F" not in medium:
                    colors_comp.append("#FF6B6B")  # Red for M9 Before
                elif "M9F" in medium:
                    colors_comp.append("#2ECC71")  # Green for M9F Before
                else:
                    colors_comp.append("#95A5A6")  # Gray for others Before

        bars_comp = ax6.bar(x_pos, comparison_data, color=colors_comp, alpha=0.8)
        ax6.set_title(
            f"Before vs After Filtering\n(Threshold: {threshold})",
            fontsize=12,
            fontweight="bold",
        )
        ax6.set_xlabel("Culture Medium", fontsize=10)
        ax6.set_ylabel("Number of Cells", fontsize=10)
        ax6.set_xticks(x_pos)
        ax6.set_xticklabels(labels, rotation=45, ha="right")
        ax6.grid(True, alpha=0.3, axis="y")

        # Add value labels
        for bar, count in zip(bars_comp, comparison_data):
            ax6.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(comparison_data) * 0.01,
                f"{count:,}",
                ha="center",
                va="bottom",
                fontsize=8,
                fontweight="bold",
            )

        plt.tight_layout()
        plt.show()

        # Create additional figure for OD analysis
        print(f"\n📊 Creating additional OD analysis figure...")

        # Create figure for OD analysis
        fig_od = plt.figure(figsize=(16, 12))

        # OD distribution violin plot (top left)
        ax_od1 = plt.subplot(2, 3, 1)
        sns.violinplot(
            data=adata_filtered.obs, x="OD", y="n_counts", ax=ax_od1, palette="viridis"
        )
        ax_od1.set_title(
            f"n_counts Distribution by OD\n(Threshold: {threshold})",
            fontsize=12,
            fontweight="bold",
        )
        ax_od1.set_xlabel("Optical Density (OD)", fontsize=10)
        ax_od1.set_ylabel("Total Counts per Barcode", fontsize=10)
        ax_od1.tick_params(axis="x", rotation=45)
        ax_od1.grid(True, alpha=0.3)

        # OD distribution violin plot for n_genes (top center)
        ax_od2 = plt.subplot(2, 3, 2)
        sns.violinplot(
            data=adata_filtered.obs, x="OD", y="n_genes", ax=ax_od2, palette="viridis"
        )
        ax_od2.set_title(
            f"n_genes Distribution by OD\n(Threshold: {threshold})",
            fontsize=12,
            fontweight="bold",
        )
        ax_od2.set_xlabel("Optical Density (OD)", fontsize=10)
        ax_od2.set_ylabel("Genes per Barcode", fontsize=10)
        ax_od2.tick_params(axis="x", rotation=45)
        ax_od2.grid(True, alpha=0.3)

        # Cell count barplot by OD (top right)
        ax_od3 = plt.subplot(2, 3, 3)
        od_cell_counts = adata_filtered.obs["OD"].value_counts().sort_index()
        bars_od = ax_od3.bar(
            range(len(od_cell_counts)),
            od_cell_counts.values,
            color="skyblue",
            alpha=0.8,
        )
        ax_od3.set_title(
            f"Cell Counts by OD\n(Threshold: {threshold})",
            fontsize=12,
            fontweight="bold",
        )
        ax_od3.set_xlabel("Optical Density (OD)", fontsize=10)
        ax_od3.set_ylabel("Number of Cells", fontsize=10)
        ax_od3.set_xticks(range(len(od_cell_counts)))
        ax_od3.set_xticklabels(od_cell_counts.index, rotation=45)
        ax_od3.grid(True, alpha=0.3, axis="y")

        # Add value labels on bars
        for bar, count in zip(bars_od, od_cell_counts.values):
            ax_od3.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(od_cell_counts.values) * 0.01,
                f"{count:,}",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        # Before vs After comparison by OD (bottom left)
        ax_od4 = plt.subplot(2, 3, 4)

        # Count cells before and after filtering by OD
        od_counts_before = adata_original.obs["OD"].value_counts().sort_index()
        od_counts_after = adata_filtered.obs["OD"].value_counts().sort_index()

        # Create comparison data for OD
        od_comparison_data = []
        od_labels = []
        for od in od_counts_before.index:
            before_count = od_counts_before[od]
            after_count = od_counts_after.get(od, 0)
            od_comparison_data.extend([before_count, after_count])
            od_labels.extend([f"{od}\nBefore", f"{od}\nAfter"])

        # Create comparison barplot for OD
        od_x_pos = np.arange(len(od_labels))
        od_colors = []
        for i, label in enumerate(od_labels):
            if "After" in label:
                od_colors.append("#87CEEB")  # Light blue for After
            else:
                od_colors.append("#4682B4")  # Dark blue for Before

        od_bars_comp = ax_od4.bar(
            od_x_pos, od_comparison_data, color=od_colors, alpha=0.8
        )
        ax_od4.set_title(
            f"Before vs After Filtering by OD\n(Threshold: {threshold})",
            fontsize=12,
            fontweight="bold",
        )
        ax_od4.set_xlabel("Optical Density (OD)", fontsize=10)
        ax_od4.set_ylabel("Number of Cells", fontsize=10)
        ax_od4.set_xticks(od_x_pos)
        ax_od4.set_xticklabels(od_labels, rotation=45, ha="right")
        ax_od4.grid(True, alpha=0.3, axis="y")

        # Add value labels
        for bar, count in zip(od_bars_comp, od_comparison_data):
            ax_od4.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(od_comparison_data) * 0.01,
                f"{count:,}",
                ha="center",
                va="bottom",
                fontsize=8,
                fontweight="bold",
            )

        # Retention rate by OD (bottom center)
        ax_od5 = plt.subplot(2, 3, 5)

        # Calculate retention rates
        retention_rates = []
        od_values = []
        for od in od_counts_before.index:
            before_count = od_counts_before[od]
            after_count = od_counts_after.get(od, 0)
            retention_rate = (
                (after_count / before_count * 100) if before_count > 0 else 0
            )
            retention_rates.append(retention_rate)
            od_values.append(od)

        # Create retention rate barplot
        bars_retention = ax_od5.bar(
            range(len(retention_rates)), retention_rates, color="lightgreen", alpha=0.8
        )
        ax_od5.set_title(
            f"Retention Rate by OD\n(Threshold: {threshold})",
            fontsize=12,
            fontweight="bold",
        )
        ax_od5.set_xlabel("Optical Density (OD)", fontsize=10)
        ax_od5.set_ylabel("Retention Rate (%)", fontsize=10)
        ax_od5.set_xticks(range(len(od_values)))
        ax_od5.set_xticklabels(od_values, rotation=45)
        ax_od5.grid(True, alpha=0.3, axis="y")
        ax_od5.set_ylim(0, 100)

        # Add percentage labels on bars
        for bar, rate in zip(bars_retention, retention_rates):
            ax_od5.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1,
                f"{rate:.1f}%",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        # Detailed OD statistics table (bottom right)
        ax_od6 = plt.subplot(2, 3, 6)
        ax_od6.axis("off")

        # Create detailed OD statistics text
        od_stats_text = f"📊 DETAILED OD STATISTICS\n"
        od_stats_text += f"Threshold: {threshold}\n"
        od_stats_text += f"Total cells: {total_cells:,}\n\n"

        od_stats_text += f"OD\tBefore\tAfter\tRemoved\tRetention%\n"
        od_stats_text += f"---\t------\t-----\t-------\t----------\n"

        for od in od_counts_before.index:
            before_count = od_counts_before[od]
            after_count = od_counts_after.get(od, 0)
            removed_count = before_count - after_count
            retention_pct = (
                (after_count / before_count * 100) if before_count > 0 else 0
            )

            od_stats_text += f"{od}\t{before_count:,}\t{after_count:,}\t{removed_count:,}\t{retention_pct:.1f}%\n"

        # Add summary statistics
        od_stats_text += f"\n📈 SUMMARY:\n"
        od_stats_text += f"ODs analyzed: {len(od_counts_before)}\n"
        od_stats_text += f"Best retention: {max(retention_rates):.1f}%\n"
        od_stats_text += f"Worst retention: {min(retention_rates):.1f}%\n"
        od_stats_text += f"Avg retention: {np.mean(retention_rates):.1f}%\n"

        ax_od6.text(
            0.05,
            0.95,
            od_stats_text,
            transform=ax_od6.transAxes,
            fontsize=9,
            verticalalignment="top",
            fontfamily="monospace",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.8),
        )

        plt.tight_layout()
        plt.show()

        # Print OD analysis summary
        print(f"\n📊 OD ANALYSIS SUMMARY:")
        print(f"ODs analyzed: {len(od_counts_before)}")
        print(f"Best retention rate: {max(retention_rates):.1f}%")
        print(f"Worst retention rate: {min(retention_rates):.1f}%")
        print(f"Average retention rate: {np.mean(retention_rates):.1f}%")

        # Print detailed OD breakdown
        print(f"\n📋 DETAILED OD BREAKDOWN:")
        for od in od_counts_before.index:
            before_count = od_counts_before[od]
            after_count = od_counts_after.get(od, 0)
            removed_count = before_count - after_count
            retention_pct = (
                (after_count / before_count * 100) if before_count > 0 else 0
            )
            print(
                f"OD {od}: {before_count:,} → {after_count:,} cells ({removed_count:,} removed, {retention_pct:.1f}% retained)"
            )

        # Print summary
        print(f"\n🎯 INTERACTIVE ANALYSIS SUMMARY:")
        print(f"📊 Threshold selected: {threshold}")
        print(
            f"📈 Total cells: {total_cells:,} ({(total_cells/len(adata_original)*100):.1f}% of original)"
        )
        print(f"🗑️ Cells removed: {len(adata_original) - total_cells:,}")
        print(f"🍽️ Culture mediums: {len(culture_mediums)}")


# Connect the slider to the update function
widgets.interactive(update_plots, threshold=threshold_slider)

# Display the widgets
print(
    "🎛️ Use the slider below to adjust the threshold and see the plots update dynamically:"
)
display(threshold_slider)
display(output_widget)

# Initialize with default threshold
update_plots(100)

# %%

# Create new Group variable by processing OD values
print("🔧 Creating new Group variable from OD column...")


def create_group_from_od(od_value):
    """
    Create Group variable from OD value.
    Extracts the medium and OD parts, removing the middle letter (A, B, C).

    Example: "OD M9_C_OD3" -> "M9_OD3"
    Example: "M9_C_OD3" -> "M9_OD3"
    """
    try:
        # Remove "OD " prefix if present
        if od_value.startswith("OD "):
            od_value = od_value[3:]  # Remove "OD "

        # Split by underscore to get parts
        parts = od_value.split("_")

        if len(parts) >= 3:
            # Get the medium part (first part) and OD part (last part)
            medium_part = parts[0]  # e.g., "M9"
            od_part = parts[-1]  # e.g., "OD3"

            # Combine them, removing the middle letter (A, B, C)
            group = f"{medium_part}_{od_part}"
            return group
        else:
            # If format is different, return original value
            return od_value
    except:
        # If any error occurs, return original value
        return od_value


# Apply the function to create Group variable
adata.obs["Group"] = adata.obs["OD"].apply(create_group_from_od)

# Display the mapping and results
print(f"📋 OD to Group mapping:")
od_to_group = {}
for od_val in adata.obs["OD"].unique():
    group_val = create_group_from_od(od_val)
    od_to_group[od_val] = group_val
    print(f"   {od_val} -> {group_val}")

print(f"\n🧬 New Group column created!")
print(f"🔢 Number of unique Group values: {len(adata.obs['Group'].unique())}")
print(f"📋 Unique Group values: {sorted(adata.obs['Group'].unique())}")

# Show distribution of cells per Group
print(f"\n📊 Distribution of cells per Group:")
group_counts = adata.obs["Group"].value_counts()
for group, count in group_counts.items():
    print(f"   {group}: {count:,} cells")

# %%
import pandas as pd

# Create donut plot for Gene Type distribution from ncbi_dataset.tsv
print("🍩 Creating donut plot for Gene Type distribution...")

# Load the ncbi dataset
ncbi_data = pd.read_csv("code/starsolo_to_anndata/data/ncbi_dataset.tsv", sep="\t")

# Check the data
print(f"📊 Dataset loaded with {len(ncbi_data)} rows")
print(f"📋 Columns: {ncbi_data.columns.tolist()}")

# Count Gene Types
gene_type_counts = ncbi_data["Gene Type"].value_counts()
print(f"\n🧬 Original Gene Type distribution:")
for gene_type, count in gene_type_counts.items():
    percentage = (count / len(ncbi_data)) * 100
    print(f"   {gene_type}: {count:,} genes ({percentage:.1f}%)")

# Transform gene types according to new classification
print(f"\n🔄 Transforming gene types...")


def transform_gene_type(gene_type):
    """
    Transform gene types:
    - protein-coding -> mRNA
    - tRNA and rRNA stay the same
    - everything else -> other
    """
    if gene_type == "protein-coding":
        return "mRNA"
    elif gene_type in ["tRNA", "rRNA"]:
        return gene_type
    else:
        return "other"


# Apply transformation
ncbi_data["Gene Type Transformed"] = ncbi_data["Gene Type"].apply(transform_gene_type)

# Count transformed gene types
expr_by_gene_type = ncbi_data["Gene Type Transformed"].value_counts()
print(f"\n🧬 Transformed Gene Type distribution:")
for gene_type, count in expr_by_gene_type.items():
    percentage = (count / len(ncbi_data)) * 100
    print(f"   {gene_type}: {count:,} genes ({percentage:.1f}%)")

import numpy as np
import matplotlib.pyplot as plt

# Données (utilise les tiennes)
# expr_by_gene_type = ...

# Couleurs
colors = {
    "mRNA": "#E74C3C",  # Bright red
    "rRNA": "#3498DB",  # Bright blue
    "tRNA": "#F39C12",  # Orange
    "other": "#27AE60",  # Green
}
plot_colors = [colors.get(g, "#95A5A6") for g in expr_by_gene_type.index]

# Plot
fig, ax = plt.subplots(figsize=(10, 8))
wedges, texts = ax.pie(
    expr_by_gene_type.values,
    startangle=90,
    colors=plot_colors,
    radius=1.0,
    wedgeprops=dict(width=0.4, edgecolor="white"),
)

# Ajouter le nombre total de gènes au centre
total_genes = expr_by_gene_type.sum()
ax.text(
    0,
    0,
    f"total number of genes \n {total_genes:,}",
    ha="center",
    va="center",
    fontsize=16,
    fontweight="bold",
    color="#2C3E50",
)

# Cercle central (donut)
centre_circle = plt.Circle((0, 0), 0.6, fc="white")
ax.add_artist(centre_circle)

# Placement intelligent des étiquettes
label_positions = []
for i, (wedge, label) in enumerate(zip(wedges, expr_by_gene_type.index)):
    angle = (wedge.theta2 + wedge.theta1) / 2.0
    x = np.cos(np.radians(angle)) * 0.85
    y = np.sin(np.radians(angle)) * 0.85

    # Décalage simple si chevauchement vertical détecté
    for prev_x, prev_y in label_positions:
        if abs(y - prev_y) < 0.1 and abs(x - prev_x) < 0.3:
            y += 0.15
    label_positions.append((x, y))

    ax.text(
        x,
        y,
        label,
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
        bbox=dict(
            boxstyle="round,pad=0.2",
            fc="white",
            ec=colors.get(label, "gray"),
            lw=2,
            alpha=0.8,
        ),
    )

# Titre personnalisé
plt.title(
    "Different types of genes in genome of Ps R401", fontsize=16, fontweight="bold"
)

# Légende avec effectif et pourcentage
total_genes = expr_by_gene_type.sum()
legend_elements = [
    plt.Rectangle(
        (0, 0),
        1,
        1,
        facecolor=colors.get(gene_type, "#95A5A6"),
        label=f"{gene_type}: {count:,} genes ({(count/total_genes)*100:.1f}%)",
    )
    for gene_type, count in expr_by_gene_type.items()
]
ax.legend(
    handles=legend_elements,
    loc="center left",
    bbox_to_anchor=(1.05, 0.5),
    fontsize=11,
    title="Gene Types",
)

plt.tight_layout()
plt.show()
# %%
adata.var


# %%
# Copier la colonne d'origine si nécessaire
adata.var["Gene Type simplified"] = adata.var["Gene Type"].copy()

# Remplacement selon les règles spécifiées
adata.var["Gene Type simplified"] = adata.var["Gene Type simplified"].replace(
    {"protein-coding": "mRNA"}
)
adata.var["Gene Type simplified"] = adata.var["Gene Type simplified"].apply(
    lambda x: x if x in ["mRNA", "tRNA", "rRNA"] else "other"
)
adata.var["Gene Type simplified"].value_counts()
# %%
# Somme de l'expression pour chaque gène
gene_ncounts = pd.Series(np.array(adata.X.sum(axis=0)).flatten(), index=adata.var_names)
adata.var["ncount"] = gene_ncounts

# Grouper par le nouveau type simplifié
expr_by_gene_type = (
    adata.var.groupby("Gene Type simplified")["ncount"]
    .sum()
    .sort_values(ascending=False)
)


# %%

# Couleurs
colors = {
    "mRNA": "#E74C3C",  # Bright red
    "rRNA": "#3498DB",  # Bright blue
    "tRNA": "#F39C12",  # Orange
    "other": "#27AE60",  # Green
}
plot_colors = [colors.get(g, "#95A5A6") for g in expr_by_gene_type.index]

# Plot
fig, ax = plt.subplots(figsize=(10, 8))
wedges, texts = ax.pie(
    expr_by_gene_type.values,
    startangle=90,
    colors=plot_colors,
    radius=1.0,
    wedgeprops=dict(width=0.4, edgecolor="white"),
)

# Cercle central (donut)
centre_circle = plt.Circle((0, 0), 0.6, fc="white")
ax.add_artist(centre_circle)

# Placement intelligent des étiquettes
label_positions = []
for i, (wedge, label) in enumerate(zip(wedges, expr_by_gene_type.index)):
    angle = (wedge.theta2 + wedge.theta1) / 2.0
    x = np.cos(np.radians(angle)) * 0.85
    y = np.sin(np.radians(angle)) * 0.85

    # Décalage simple si chevauchement vertical détecté
    for prev_x, prev_y in label_positions:
        if abs(y - prev_y) < 0.1 and abs(x - prev_x) < 0.3:
            y += 0.15
    label_positions.append((x, y))

    ax.text(
        x,
        y,
        label,
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
        bbox=dict(
            boxstyle="round,pad=0.2",
            fc="white",
            ec=colors.get(label, "gray"),
            lw=2,
            alpha=0.8,
        ),
    )

# Titre personnalisé
plt.title(
    "Number of UMIs per gene type in transcriptome of Ps R401",
    fontsize=16,
    fontweight="bold",
)

# Légende avec effectif et pourcentage
total_genes = expr_by_gene_type.sum()
legend_elements = [
    plt.Rectangle(
        (0, 0),
        1,
        1,
        facecolor=colors.get(gene_type, "#95A5A6"),
        label=f"{gene_type}: {count:,} UMIs ({(count/total_genes)*100:.1f}%)",
    )
    for gene_type, count in expr_by_gene_type.items()
]
ax.legend(
    handles=legend_elements,
    loc="center left",
    bbox_to_anchor=(1.05, 0.5),
    fontsize=11,
    title="Gene Types",
)
# Ajouter le total des ncounts au centre
ax.text(
    0,
    0,
    f"{int(total_genes):,}\nUMIs",
    ha="center",
    va="center",
    fontsize=14,
    fontweight="bold",
)
plt.tight_layout()
plt.show()
# %%

# %%
# Debug: Vérifier les valeurs uniques dans Gene Type
print("🔍 Debug: Valeurs uniques dans Gene Type:")
print(adata.var["Gene Type"].value_counts())

print("\n🔍 Debug: Valeurs uniques dans Gene Type simplified:")
print(adata.var["Gene Type simplified"].value_counts())

# Vérifier si rRNA existe dans les données originales
print("\n🔍 Debug: Recherche de 'rRNA' dans Gene Type:")
rna_genes = adata.var[adata.var["Gene Type"].str.contains("rRNA", case=False, na=False)]
print(f"Nombre de gènes contenant 'rRNA': {len(rna_genes)}")
if len(rna_genes) > 0:
    print("Exemples de gènes rRNA:")
    print(rna_genes["Gene Type"].head(10))

# Vérifier les valeurs exactes
print("\n🔍 Debug: Valeurs exactes contenant 'rRNA':")
rna_values = adata.var["Gene Type"].unique()
rna_values = [val for val in rna_values if "rRNA" in str(val).lower()]
print(rna_values)

# %% do a thresold ncounts de 940
adata_filtered = adata[adata.obs["n_counts"] >= 950]
# %% number of cells per group
adata_filtered.obs["Group"].value_counts()
# %%
# total number of cells
adata_filtered.n_obs


# %% violin plot scanpy per Group
# Create violin plots comparing gene counts and genes detected across Groups
print("🎻 Creating violin plots for gene metrics across Groups...")

# Create figure with 2 subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

# Violin plot for n_counts (top)
sc.pl.violin(adata_filtered, "n_counts", groupby="Group", ax=ax1, show=False)
ax1.set_title(
    "Distribution of Total Counts per Cell by Group",
    fontsize=14,
    fontweight="bold",
    pad=15,
)
ax1.set_xlabel("Group", fontsize=12, fontweight="bold")
ax1.set_ylabel("Total Counts per Cell", fontsize=12, fontweight="bold")
ax1.grid(True, alpha=0.3, linestyle="--")

# Add statistics for n_counts
for i, group in enumerate(adata_filtered.obs["Group"].unique()):
    group_data = adata_filtered.obs[adata_filtered.obs["Group"] == group]
    median = group_data["n_counts"].median()
    q1 = group_data["n_counts"].quantile(0.25)
    q3 = group_data["n_counts"].quantile(0.75)
    n_cells = len(group_data)

    stats_text = f"{group}:\nMedian: {median:.0f}\nQ1: {q1:.0f}\nQ3: {q3:.0f}\nCells: {n_cells:,}"
    ax1.text(
        i,
        ax1.get_ylim()[1],
        stats_text,
        ha="center",
        va="top",
        fontsize=8,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
    )

# Violin plot for n_genes (bottom)
sc.pl.violin(adata_filtered, "n_genes", groupby="Group", ax=ax2, show=False)
ax2.set_title(
    "Distribution of Genes Detected per Cell by Group",
    fontsize=14,
    fontweight="bold",
    pad=15,
)
ax2.set_xlabel("Group", fontsize=12, fontweight="bold")
ax2.set_ylabel("Genes per Cell", fontsize=12, fontweight="bold")
ax2.grid(True, alpha=0.3, linestyle="--")

# Add statistics for n_genes
for i, group in enumerate(adata_filtered.obs["Group"].unique()):
    group_data = adata_filtered.obs[adata_filtered.obs["Group"] == group]
    median = group_data["n_genes"].median()
    q1 = group_data["n_genes"].quantile(0.25)
    q3 = group_data["n_genes"].quantile(0.75)
    n_cells = len(group_data)

    stats_text = f"{group}:\nMedian: {median:.0f}\nQ1: {q1:.0f}\nQ3: {q3:.0f}\nCells: {n_cells:,}"
    ax2.text(
        i,
        ax2.get_ylim()[1],
        stats_text,
        ha="center",
        va="top",
        fontsize=8,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
    )

plt.suptitle(
    f"Cell Quality Metrics by Group (n_counts ≥ 950, {adata_filtered.n_obs:,} cells)",
    fontsize=16,
    fontweight="bold",
    y=1.02,
)
plt.tight_layout()
plt.show()


# %% remove M9_0D2
adata_filtered = adata_filtered[adata_filtered.obs["Group"] != "M9_0D2"]
# %% number of cells per group
adata_filtered.obs["Group"].value_counts()
# %%
# total number of cells
adata_filtered.n_obs


# %% remove the 3 top ncounts cells
print("🗑️ Removing the 3 cells with highest n_counts...")

# Get the 3 highest n_counts values
top_3_ncounts = adata_filtered.obs["n_counts"].nlargest(3)
print(f"📊 Top 3 n_counts values to remove:")
for i, (idx, value) in enumerate(top_3_ncounts.items(), 1):
    print(f"   {i}. Cell {idx}: {value:,} counts")

# Create mask to exclude these 3 cells
cells_to_remove = top_3_ncounts.index
cells_to_keep = ~adata_filtered.obs.index.isin(cells_to_remove)

# Apply filtering
adata_filtered = adata_filtered[cells_to_keep].copy()

print(f"📊 After removing top 3 cells: {adata_filtered.n_obs:,} cells")
print(f"🗑️ Removed {len(cells_to_remove)} cells with highest n_counts")

# Show new summary statistics
print(f"\n📈 New summary statistics:")
print(f"   Mean n_counts: {adata_filtered.obs['n_counts'].mean():.2f}")
print(f"   Median n_counts: {adata_filtered.obs['n_counts'].median():.2f}")
print(f"   Min n_counts: {adata_filtered.obs['n_counts'].min():.2f}")
print(f"   Max n_counts: {adata_filtered.obs['n_counts'].max():.2f}")

# %%
sc.pl.violin(
    adata_filtered,
    ["n_counts"],
    jitter=0.4,
    multi_panel=True,
    groupby="Group",
)
# %%
adata_filtered = adata_filtered[adata_filtered.obs["Group"] != "M9_OD2"]
# %% number of cells per group
adata_filtered.obs["Group"].value_counts()
# %%
adata_filtered = adata_filtered[
    ~adata_filtered.obs.index.isin(adata_filtered.obs["n_counts"].nlargest(3).index)
]
# %% number of cells per group
adata_filtered.obs["Group"].value_counts()
# %%
# total number of cells
adata_filtered.n_obs

# %%
# %%
sc.pl.violin(
    adata_filtered,
    ["n_counts"],
    jitter=0.4,
    multi_panel=True,
    groupby="Group",
)
# %%
# Afficher le nombre de cellules par groupe
print("Nombre de cellules par groupe :")
group_counts = adata_filtered.obs["Group"].value_counts()
for group, count in group_counts.items():
    print(f"   {group}: {count:,} cellules")

# Afficher le total
total_cells = adata_filtered.n_obs
print(f"\n📈 Total: {total_cells:,} cellules")

# Afficher aussi sous forme de tableau
print(f"\n📋 Résumé complet :")
print(f"{'Groupe':<12} {'Cellules':<10} {'%':<8}")
print("-" * 30)
for group, count in group_counts.items():
    percentage = (count / total_cells) * 100
    print(f"{group:<12} {count:<10,} {percentage:<7.1f}%")
print("-" * 30)
print(f"{'TOTAL':<12} {total_cells:<10,} 100.0%")

# %%


# Créer le plot violin avec annotations
fig, ax = plt.subplots(figsize=(12, 6))

# Plot violin
sc.pl.violin(
    adata_filtered, ["n_counts"], jitter=0.4, groupby="Group", ax=ax, show=False
)

# Récupérer l'ordre exact des groupes dans le plot
plot_groups = ax.get_xticklabels()
group_counts = adata_filtered.obs["Group"].value_counts()
total_cells = adata_filtered.n_obs

# Ajouter les annotations dans l'ordre du plot
for i, tick_label in enumerate(plot_groups):
    group = tick_label.get_text()
    count = group_counts.get(group, 0)
    percentage = (count / total_cells) * 100
    ax.text(
        i,
        ax.get_ylim()[1],
        f"n={count:,}\n({percentage:.1f}%)",
        ha="center",
        va="top",
        fontsize=10,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
    )

# Ajouter le titre avec le total
ax.set_title(
    f"Distribution de n_counts par groupe (Total: {total_cells:,} cellules)",
    fontsize=14,
    fontweight="bold",
    pad=20,
)

plt.tight_layout()
plt.show()


# %%
# %%


# Créer le plot violin avec annotations
fig, ax = plt.subplots(figsize=(12, 6))

# Plot violin
sc.pl.violin(adata_filtered, ["n_counts"], jitter=0.4, groupby="OD", ax=ax, show=False)

# Récupérer l'ordre exact des groupes dans le plot
plot_groups = ax.get_xticklabels()
group_counts = adata_filtered.obs["OD"].value_counts()
total_cells = adata_filtered.n_obs

# Ajouter les annotations dans l'ordre du plot
for i, tick_label in enumerate(plot_groups):
    group = tick_label.get_text()
    count = group_counts.get(group, 0)
    percentage = (count / total_cells) * 100
    ax.text(
        i,
        ax.get_ylim()[1],
        f"n={count:,}\n({percentage:.1f}%)",
        ha="center",
        va="top",
        fontsize=10,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
    )

# Ajouter le titre avec le total
ax.set_title(
    f"Distribution de n_counts par groupe (Total: {total_cells:,} cellules)",
    fontsize=14,
    fontweight="bold",
    pad=20,
)

plt.tight_layout()
plt.show()
# %%
adata_filtered.var["Gene Type simplified"].value_counts()

# %%
# Filter to keep only mRNA genes using pandas
adata_filtered = adata_filtered[
    :, adata_filtered.var["Gene Type simplified"].isin(["mRNA"])
]
# adata_filtered.var["Gene Type simplified"].value_counts()

# %%
sc.pp.calculate_qc_metrics(adata_filtered, inplace=True, log1p=True)
# %%
adata_filtered.obs
# %%
# Access QC metrics calculated by scanpy
obs_metrics, var_metrics = sc.pp.calculate_qc_metrics(
    adata_filtered, inplace=False, log1p=True
)

# Display obs_metrics (cell-level metrics)
print("📊 Cell-level QC metrics (obs_metrics):")
print(f"Shape: {obs_metrics.shape}")
print(f"Columns: {obs_metrics.columns.tolist()}")
print(obs_metrics.head())

# Display var_metrics (gene-level metrics)
print(f"\n🧬 Gene-level QC metrics (var_metrics):")
print(f"Shape: {var_metrics.shape}")
print(f"Columns: {var_metrics.columns.tolist()}")
print(var_metrics.head())

# %%
# Access specific metrics from adata.obs
print("📊 Available metrics in adata.obs:")
print(adata_filtered.obs.columns.tolist())

# Show summary of key metrics
print(f"\n📈 Summary of key QC metrics:")
print(f"n_genes_by_counts: {adata_filtered.obs['n_genes_by_counts'].describe()}")
print(f"total_counts: {adata_filtered.obs['total_counts'].describe()}")
print(
    f"pct_counts_in_top_50_genes: {adata_filtered.obs['pct_counts_in_top_50_genes'].describe()}"
)

# %%
sc.pl.scatter(adata_filtered, "total_counts", "n_genes_by_counts", color="Group")

# %%
# Saving count data
adata_filtered.layers["counts"] = adata_filtered.X.copy()
test = adata_filtered.copy()

# %%
sc.pp.normalize_total(test, target_sum=1e4)
sc.pp.log1p(test)

# %%
# Scaling the data (mise à l'échelle)
sc.pp.scale(test, max_value=10000)

# %%
sc.pp.pca(test, svd_solver="arpack")
# %%
sc.pp.highly_variable_genes(test, n_top_genes=2000)
# %%
test.var["highly_variable"]
# %%
sc.pl.highly_variable_genes(test)
# %%
sc.tl.pca(test)
# %%
sc.pl.pca(test)
# %%
sc.pl.pca(test, color="Group")

sc.pl.pca_variance_ratio(test, n_pcs=50, log=True)
# %%
sc.pp.neighbors(test)
# %%
sc.tl.umap(test)
# %%
sc.pl.umap(
    test,
    color="Group",
    # Setting a smaller point size to get prevent overlap
    size=2,
)
# %% filter min = 3 cells
print(f"📊 Nombre de gènes avant filtrage: {test.n_vars:,}")

# Store initial number of genes
n_genes_before = test.n_vars

sc.pp.filter_genes(test, min_cells=30)

print(f"📊 Nombre de gènes après filtrage (min_cells=10): {test.n_vars:,}")
print(f"🗑️ Gènes supprimés: {n_genes_before - test.n_vars:,}")
print(f"📈 Pourcentage conservé: {(test.n_vars/n_genes_before)*100:.1f}%")

# %%

# %%
# Recalculer les métriques QC après filtrage
sc.pp.calculate_qc_metrics(test, inplace=True, log1p=True)

# %%
# Normalisation et transformation
sc.pp.normalize_total(test, target_sum=1e4)
sc.pp.log1p(test)

# %%
# Mise à l'échelle
sc.pp.scale(test, max_value=10000)

# %%
# Sélection des gènes hautement variables
sc.pp.highly_variable_genes(test, n_top_genes=2000)

# %%
# Vérifier les gènes hautement variables
print(f"📊 Nombre de gènes hautement variables: {test.var['highly_variable'].sum():,}")

# %%
# Plot des gènes hautement variables
sc.pl.highly_variable_genes(test)

# %%
# PCA
sc.tl.pca(test)

# %%
# Plot PCA
sc.pl.pca(test, color="Group")

# %%
# Plot variance expliquée par les composantes principales
sc.pl.pca_variance_ratio(test, n_pcs=50, log=True)

# %%
# Calcul des voisins
sc.pp.neighbors(test)

# %%
# UMAP
sc.tl.umap(test)

# %%
# Plot UMAP coloré par groupe
sc.pl.umap(test, color="Group", size=2)
