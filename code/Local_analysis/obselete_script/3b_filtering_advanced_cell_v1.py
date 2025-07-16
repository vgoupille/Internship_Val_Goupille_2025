# %%
import os
import sys
import numpy as np
import anndata as ad
import pandas as pd
import scanpy as sc
import matplotlib.pyplot as plt
import seaborn as sns

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import visualization functions
import importlib
import visualization_functions

importlib.reload(visualization_functions)  # Force reload to avoid cache issues

from visualization_functions import (
    plot_stacked_bar_by_odt,
    plot_violin_stripplot_by_group,
    plot_scatter_comparison_m9f_m9,
)

# %%
# Set working directory
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# %%
# Load the filtered data from 3a
print("📂 Loading filtered data from 3a...")
INPUT_PATH = "data/anndata_objects_with_complete_metadata_filtered"
INPUT_FILE = "GeneFull_raw_unique_mult_with_metadata_grouped_filtered_100UMI.h5ad"

# Load the filtered data
adata_raw_filtered_100UMI = ad.read_h5ad(os.path.join(INPUT_PATH, INPUT_FILE))

print(
    f"📊 Loaded dataset: {adata_raw_filtered_100UMI.n_obs:,} cells × {adata_raw_filtered_100UMI.n_vars:,} genes"
)
print(f"🔢 Available obs columns: {list(adata_raw_filtered_100UMI.obs.columns)}")

# %%

# filter Top 5 cells with highest n_counts
##### filter cell
# %%
sc.pl.violin(adata_raw_filtered_100UMI, ["n_counts"], groupby="Group", multi_panel=True)

# %% remove the 5 top ncounts cells
print("🗑️ Removing the 5 cells with highest n_counts...")

# Get the 5 highest n_counts values
top_5_ncounts = adata_raw_filtered_100UMI.obs["n_counts"].nlargest(5)
print(f"📊 Top 5 n_counts values to remove:")
for i, (idx, value) in enumerate(top_5_ncounts.items(), 1):
    print(f"   {i}. Cell {idx}: {value:,} counts")

# Create mask to exclude these 5 cells
cells_to_remove = top_5_ncounts.index
cells_to_keep = ~adata_raw_filtered_100UMI.obs.index.isin(cells_to_remove)

# Apply filtering
adata_filtered_100UMI_no_top5_outliers = adata_raw_filtered_100UMI[cells_to_keep].copy()

print(
    f"📊 After removing top 5 cells: {adata_filtered_100UMI_no_top5_outliers.n_obs:,} cells"
)
print(f"🗑️ Removed {len(cells_to_remove)} cells with highest n_counts")

sc.pl.violin(
    adata_filtered_100UMI_no_top5_outliers,
    ["n_counts"],
    groupby="Group",
    multi_panel=True,
)


# %%
def remove_top_cells_by_group(
    adata: ad.AnnData, group_name: str, n_cells: int = 1, show_plot: bool = True
) -> ad.AnnData:
    """
    Remove the top n cells with highest n_counts from a specific group.

    Args:
        adata (ad.AnnData): Input AnnData object
        group_name (str): Name of the group to filter
        n_cells (int): Number of top cells to remove (default: 1)
        show_plot (bool): Whether to show violin plot after filtering (default: True)

    Returns:
        ad.AnnData: Filtered AnnData object
    """
    # Get cells from the specified group
    group_mask = adata.obs["Group"] == group_name

    if not group_mask.any():
        print(f"⚠️  Warning: No cells found in group '{group_name}'")
        return adata

    # Get the top n_counts values for this group
    top_cells = adata.obs[group_mask]["n_counts"].nlargest(n_cells)

    if len(top_cells) == 0:
        print(f"⚠️  Warning: No cells to remove in group '{group_name}'")
        return adata

    print(f"🗑️ Removing top {n_cells} cell(s) from group '{group_name}':")
    for i, (idx, value) in enumerate(top_cells.items(), 1):
        print(f"   {i}. Cell {idx}: {value:,} counts")

    # Create mask to exclude these cells
    cells_to_remove = top_cells.index
    cells_to_keep = ~adata.obs.index.isin(cells_to_remove)

    # Apply filtering
    adata_filtered = adata[cells_to_keep].copy()

    print(
        f"📊 Remaining cells in '{group_name}': {sum(adata_filtered.obs['Group'] == group_name):,}"
    )

    # Show violin plot if requested
    if show_plot:
        sc.pl.violin(adata_filtered, ["n_counts"], groupby="Group", multi_panel=True)

    return adata_filtered


# %%
# Remove outlier cells from specific groups
# Define groups and number of cells to remove for each
groups_to_filter = [
    ("M9F_OD2", 2),  # Remove 2 cells from M9F_OD2
    ("M9_OD2", 2),  # Remove 2 cells from M9_OD2
    ("M9_OD1", 1),  # Remove 1 cell from M9_OD1
]

print("🔧 Starting group-specific outlier removal...")
print(f"📊 Initial dataset: {adata_filtered_100UMI_no_top5_outliers.n_obs:,} cells")

# Plot is already shown above after removing top 5 outliers - no need to repeat

# Start with the dataset that already has top 5 outliers removed
adata_filtered_100UMI_no_group_outliers = adata_filtered_100UMI_no_top5_outliers.copy()

for group_name, n_cells in groups_to_filter:
    print(f"\n{'='*50}")
    adata_filtered_100UMI_no_group_outliers = remove_top_cells_by_group(
        adata_filtered_100UMI_no_group_outliers,
        group_name,
        n_cells,
        show_plot=False,  # Don't show plot for each step
    )

print(f"\n{'='*50}")
print(f"🎉 Group-specific filtering completed!")
print(f"📊 Final dataset: {adata_filtered_100UMI_no_group_outliers.n_obs:,} cells")

# Show final violin plot
print("\n📊 Final violin plot after all filtering:")
sc.pl.violin(
    adata_filtered_100UMI_no_group_outliers,
    ["n_counts"],
    groupby="Group",
    multi_panel=True,
)


# %%
adata_filtered_100UMI_no_group_outliers.obs["n_counts"].describe()
# %% n cell by group
adata_filtered_100UMI_no_group_outliers.obs["Group"].value_counts()


# %%
def select_cells_by_group(
    adata: ad.AnnData,
    target_total_cells: int,
    group_by: str = "RepBio",
    sort_by: str = "n_counts",
    random: bool = False,
    seed: int = None,
    descending: bool = True,
) -> dict:
    """
    Select cells by group with balanced sampling.

    Args:
        adata (ad.AnnData): Input AnnData object
        target_total_cells (int): Total number of cells to select
        group_by (str): Column name to group by (default: "RepBio")
        sort_by (str): Column name to sort by (default: "n_counts")
        random (bool): Whether to use random sampling (default: False)
        seed (int): Random seed for reproducibility (default: None)
        descending (bool): Sort in descending order (default: True)

    Returns:
        dict: Dictionary containing filtered AnnData object and summary
    """
    meta = adata.obs.copy()
    meta["cell_barcode"] = meta.index

    # Input validation
    if group_by not in meta.columns:
        raise ValueError(f"Group column '{group_by}' not found in adata.obs.")
    if sort_by not in meta.columns:
        raise ValueError(f"Sort column '{sort_by}' not found in adata.obs.")

    n_groups = meta[group_by].nunique()
    target_per_group = target_total_cells // n_groups

    print(f"🎯 Target total cells: {target_total_cells:,}")
    print(f"📁 Group column: '{group_by}' — {n_groups} groups")
    print(f"🧮 Sort by: '{sort_by}' | Descending: {descending}")
    print(f"🔢 Cells per group: {target_per_group:,}")
    if random and seed is not None:
        print(f"🎲 Random sampling with seed {seed}")

    selected_cells = []
    selection_summary = []

    for group, df_group in meta.groupby(group_by):
        n_available = len(df_group)
        print(f"\n🔍 Group '{group}': {n_available:,} cells available")

        if n_available <= target_per_group:
            print(f"✅ Keeping all {n_available:,} cells")
            selected = df_group["cell_barcode"].tolist()
            n_selected = n_available
        else:
            if random:
                if seed is not None:
                    np.random.seed(seed)
                selected = df_group.sample(n=target_per_group, random_state=seed)[
                    "cell_barcode"
                ].tolist()
            else:
                df_sorted = df_group.sort_values(by=sort_by, ascending=not descending)
                selected = df_sorted.head(target_per_group)["cell_barcode"].tolist()
            n_selected = target_per_group
            print(f"📊 Selected {n_selected:,} cells from {n_available:,}")

        selected_cells.extend(selected)
        selection_summary.append(
            {
                "group": group,
                "available": n_available,
                "selected": n_selected,
                "percentage": (n_selected / n_available) * 100,
            }
        )

    # Filter AnnData object
    adata_filtered = adata[selected_cells].copy()

    # Create summary dataframe
    summary_df = pd.DataFrame(selection_summary)

    print(f"\n📊 Selection summary:")
    print(f"   Total cells selected: {len(selected_cells):,}")
    print(f"   Target was: {target_total_cells:,}")

    return {
        "adata": adata_filtered,
        "summary": summary_df,
        "selected_cells": selected_cells,
    }


# %%
# Check current distribution by OD
print("📊 Current distribution by OD:")
print(adata_filtered_100UMI_no_group_outliers.obs["OD"].value_counts().sort_index())

# %%
# Ensure n_counts is properly calculated
print("🧮 Ensuring n_counts is properly calculated...")
if "n_counts" not in adata_filtered_100UMI_no_group_outliers.obs.columns:
    print("⚠️  n_counts column not found, calculating...")
    # Calculate n_counts properly for sparse matrices
    if hasattr(adata_filtered_100UMI_no_group_outliers.X, "toarray"):
        # Sparse matrix
        adata_filtered_100UMI_no_group_outliers.obs["n_counts"] = np.array(
            adata_filtered_100UMI_no_group_outliers.X.sum(axis=1)
        ).flatten()
    else:
        # Dense matrix
        adata_filtered_100UMI_no_group_outliers.obs["n_counts"] = (
            adata_filtered_100UMI_no_group_outliers.X.sum(axis=1)
        )
else:
    print("✅ n_counts column already exists")

# %%
# Perform balanced subsampling by OD
print("\n🎯 Performing balanced subsampling by OD...")
TARGET_CELLS = 3000

result = select_cells_by_group(
    adata=adata_filtered_100UMI_no_group_outliers,
    target_total_cells=TARGET_CELLS,
    group_by="OD",
    sort_by="n_counts",
    random=False,
    seed=42,
    descending=True,
)

# Extract results
adata_filtered_100UMI_balanced_3000cells_by_OD = result["adata"]
summary_df = result["summary"]
selected_cells = result["selected_cells"]

# Display detailed summary
print("\n📊 Detailed selection summary:")
print(summary_df.to_string(index=False))

# %%
# Verify final distribution
print("\n📊 Final distribution by OD after subsampling:")
final_counts = (
    adata_filtered_100UMI_balanced_3000cells_by_OD.obs["OD"].value_counts().sort_index()
)
print(final_counts)

print(f"\n✅ Subsampling completed successfully!")
print(
    f"📊 Final dataset: {adata_filtered_100UMI_balanced_3000cells_by_OD.n_obs:,} cells × {adata_filtered_100UMI_balanced_3000cells_by_OD.n_vars:,} genes"
)

# %%
# Generate stacked bar plot by ODt
print("\n📊 Generating stacked bar plot by ODt...")
total_all, total_by_medium = plot_stacked_bar_by_odt(
    adata_filtered_100UMI_balanced_3000cells_by_OD
)

print(f"✅ Stacked bar plot generated successfully!")
print(f"📊 Total cells analyzed: {total_all:,}")
print(f"📊 Total by medium: {total_by_medium}")


# %%
# Violin + stripplot function
print("\n📊 Violin + stripplot visualizations...")

# Plot for n_counts (UMIs)
print("\n1️⃣ Plotting n_counts (UMIs)...")
plot_violin_stripplot_by_group(
    adata=adata_filtered_100UMI_balanced_3000cells_by_OD,
    y_column="n_counts",
    y_label="Number of UMIs per Cell Barcode",
    title_suffix=" - UMIs",
    figsize_per_plot=6,
)

# Plot for n_genes
print("\n2️⃣ Plotting n_genes...")
plot_violin_stripplot_by_group(
    adata=adata_filtered_100UMI_balanced_3000cells_by_OD,
    y_column="n_genes",
    y_label="Number of Genes per Cell Barcode",
    title_suffix=" - Genes",
    figsize_per_plot=6,
)


# %%
# Scatter comparison function
print("\n📊 Scatter comparison M9F vs M9...")

# Scatter plot with n_counts vs n_genes
print("\n3️⃣ Plotting n_counts vs n_genes comparison...")
plot_scatter_comparison_m9f_m9(
    adata=adata_filtered_100UMI_balanced_3000cells_by_OD,
    x_column="n_counts",
    y_column="n_genes",
    color_column="OD",
    x_label="Total of UMIs per Cell Barcode",
    y_label="Total of Genes per Cell Barcode",
    title_suffix="",
    point_size=20,
    figsize=(12, 5),
    m9f_palette="tab20",
    m9_palette="Set1",
)


# %%
# Analyze n_counts distribution by different groupings
print("📊 Analyzing n_counts distribution by different groupings...")

print("\n1️⃣ Overall n_counts statistics:")
print(adata_filtered_100UMI_balanced_3000cells_by_OD.obs["n_counts"].describe())

print("\n2️⃣ n_counts statistics by RepTech:")
reptech_stats = adata_filtered_100UMI_balanced_3000cells_by_OD.obs.groupby("RepTech")[
    "n_counts"
].describe()
print(reptech_stats)

print("\n3️⃣ n_counts statistics by OD:")
od_stats = adata_filtered_100UMI_balanced_3000cells_by_OD.obs.groupby("OD")[
    "n_counts"
].describe()
print(od_stats)

print("\n4️⃣ RepTech distribution:")
reptech_counts = (
    adata_filtered_100UMI_balanced_3000cells_by_OD.obs["RepTech"]
    .value_counts()
    .sort_index()
)
print(reptech_counts)


# %%
def remove_outliers_by_reptech(
    adata: ad.AnnData,
    outlier_groups: dict,
    sort_by: str = "n_counts",
    descending: bool = True,
) -> ad.AnnData:
    """
    Remove outlier cells from specific RepTech groups.

    Args:
        adata (ad.AnnData): Input AnnData object
        outlier_groups (dict): Dictionary with RepTech as keys and number of cells to remove as values
        sort_by (str): Column to sort by for outlier detection (default: "n_counts")
        descending (bool): Sort in descending order (default: True)

    Returns:
        ad.AnnData: Filtered AnnData object
    """
    print(f"📊 Starting outlier removal by RepTech...")
    print(f"📊 Initial dataset: {adata.n_obs:,} cells")

    # Validate input
    if sort_by not in adata.obs.columns:
        raise ValueError(f"Sort column '{sort_by}' not found in adata.obs")

    cells_to_remove = []
    removal_summary = []

    # Process each group
    for reptech, n_cells in outlier_groups.items():
        if reptech not in adata.obs["RepTech"].values:
            print(f"⚠️  Warning: RepTech '{reptech}' not found in data")
            continue

        # Get cells from this RepTech group
        group_mask = adata.obs["RepTech"] == reptech
        n_available = sum(group_mask)

        if n_available == 0:
            print(f"⚠️  Warning: No cells found for RepTech '{reptech}'")
            continue

        if n_cells > n_available:
            print(
                f"⚠️  Warning: Cannot remove {n_cells} cells from '{reptech}' (only {n_available} available)"
            )
            n_cells = n_available

        # Get the highest n_counts values for this group
        highest_cells = adata.obs[group_mask][sort_by].nlargest(n_cells)

        print(
            f"🔍 RepTech '{reptech}': removing {n_cells} cells from {n_available} available"
        )
        for i, (idx, value) in enumerate(highest_cells.items(), 1):
            print(f"   {i}. Cell {idx}: {value:,} {sort_by}")

        cells_to_remove.extend(highest_cells.index.tolist())
        removal_summary.append(
            {
                "RepTech": reptech,
                "available": n_available,
                "removed": n_cells,
                "remaining": n_available - n_cells,
            }
        )

    # Remove duplicates (shouldn't happen but safety check)
    cells_to_remove = list(set(cells_to_remove))

    print(f"\n🗑️ Total cells to remove: {len(cells_to_remove)}")

    # Apply filtering
    cells_to_keep = ~adata.obs.index.isin(cells_to_remove)
    adata_filtered = adata[cells_to_keep].copy()

    print(f"📊 After outlier removal: {adata_filtered.n_obs:,} cells")
    print(f"🗑️ Total removed: {len(cells_to_remove)} cells")

    # Display summary
    print(f"\n📊 Removal summary by RepTech:")
    summary_df = pd.DataFrame(removal_summary)
    print(summary_df.to_string(index=False))

    return adata_filtered


# %%
# Define outlier groups to process
# Groups are organized by OD level for clarity
OUTLIER_GROUPS = {
    # OD1 groups - remove 1 cell each
    "M9F_A_OD1_1": 1,
    "M9F_A_OD1_5": 1,
    "M9_A_OD1_1": 1,
    "M9_A_OD1_3": 1,
    "M9_C_OD1_2": 1,
    # OD2 groups - remove 1 cell each (except M9F_A_OD2_5 which removes 2)
    "M9F_A_OD2_1": 1,
    "M9F_A_OD2_3": 1,
    "M9F_C_OD2_3": 1,
    "M9F_C_OD2_5": 1,
    "M9F_A_OD2_5": 2,  # Special case: remove 2 cells
    # OD3 groups - remove 1 cell each
    "M9F_B_OD3_1": 1,
    "M9F_B_OD3_4": 1,
    "M9F_C_OD3_3": 1,
    "M9_A_OD3_4": 1,
    "M9_B_OD3_3": 1,
}


# %%
# Apply outlier removal
adata_filtered_100UMI_balanced_no_reptech_outliers = remove_outliers_by_reptech(
    adata_filtered_100UMI_balanced_3000cells_by_OD, OUTLIER_GROUPS
)

# Filter out RepTech groups with less than 6 cells
print("\n🔧 Filtering RepTech groups with less than 6 cells...")
print(
    f"📊 Before RepTech filtering: {adata_filtered_100UMI_balanced_no_reptech_outliers.n_obs:,} cells"
)

# Get RepTech groups with at least 6 cells
reptech_counts = adata_filtered_100UMI_balanced_no_reptech_outliers.obs[
    "RepTech"
].value_counts()
reptech_to_keep = reptech_counts[reptech_counts >= 6].index

print(f"📊 RepTech groups with ≥6 cells: {len(reptech_to_keep)}")
print(f"📊 RepTech groups to remove: {len(reptech_counts) - len(reptech_to_keep)}")

# Apply RepTech filtering
adata_filtered_100UMI_balanced_min6cells_per_RepTech = (
    adata_filtered_100UMI_balanced_no_reptech_outliers[
        adata_filtered_100UMI_balanced_no_reptech_outliers.obs["RepTech"].isin(
            reptech_to_keep
        )
    ].copy()
)

print(
    f"📊 After RepTech filtering: {adata_filtered_100UMI_balanced_min6cells_per_RepTech.n_obs:,} cells"
)
print(
    f"🗑️ Removed {adata_filtered_100UMI_balanced_no_reptech_outliers.n_obs - adata_filtered_100UMI_balanced_min6cells_per_RepTech.n_obs} cells"
)

# %%
# Final summary of the filtering process
print("\n" + "=" * 80)
print("📊 FINAL SUMMARY OF FILTERING PROCESS")
print("=" * 80)

print(f"1️⃣ Initial dataset (100UMI filtered): {adata_raw_filtered_100UMI.n_obs:,} cells")
print(
    f"2️⃣ After removing top 5 outliers: {adata_filtered_100UMI_no_top5_outliers.n_obs:,} cells"
)
print(
    f"3️⃣ After removing group-specific outliers: {adata_filtered_100UMI_no_group_outliers.n_obs:,} cells"
)
print(
    f"4️⃣ After balanced subsampling (3000 cells): {adata_filtered_100UMI_balanced_3000cells_by_OD.n_obs:,} cells"
)
print(
    f"5️⃣ After RepTech-specific outlier removal: {adata_filtered_100UMI_balanced_no_reptech_outliers.n_obs:,} cells"
)
print(
    f"6️⃣ Final dataset (min 6 cells per RepTech): {adata_filtered_100UMI_balanced_min6cells_per_RepTech.n_obs:,} cells"
)

print(
    f"\n🎯 Total cells removed: {adata_raw_filtered_100UMI.n_obs - adata_filtered_100UMI_balanced_min6cells_per_RepTech.n_obs:,}"
)
print(
    f"📊 Final dataset: {adata_filtered_100UMI_balanced_min6cells_per_RepTech.n_obs:,} cells × {adata_filtered_100UMI_balanced_min6cells_per_RepTech.n_vars:,} genes"
)

# %%
# Save the final filtered dataset
print("\n💾 Saving final filtered dataset...")
OUTPUT_PATH = "data/anndata_objects_with_complete_metadata_filtered"
OUTPUT_FILE = "GeneFull_raw_unique_mult_with_metadata_filtered_100UMI_balanced_3000cells_min6RepTech.h5ad"

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_PATH, exist_ok=True)

# Save the final dataset
adata_filtered_100UMI_balanced_min6cells_per_RepTech.write_h5ad(
    os.path.join(OUTPUT_PATH, OUTPUT_FILE)
)

print(f"✅ Final dataset saved to: {os.path.join(OUTPUT_PATH, OUTPUT_FILE)}")
print(
    f"📊 Final dataset contains: {adata_filtered_100UMI_balanced_min6cells_per_RepTech.n_obs:,} cells × {adata_filtered_100UMI_balanced_min6cells_per_RepTech.n_vars:,} genes"
)

# %%
# Create a summary report of the filtering process
print("\n📋 Creating filtering summary report...")

filtering_summary = {
    "Step": [
        "1. Initial dataset (100UMI filtered)",
        "2. After removing top 5 outliers",
        "3. After removing group-specific outliers",
        "4. After balanced subsampling (3000 cells)",
        "5. After RepTech-specific outlier removal",
        "6. Final dataset (min 6 cells per RepTech)",
    ],
    "n_cells": [
        adata_raw_filtered_100UMI.n_obs,
        adata_filtered_100UMI_no_top5_outliers.n_obs,
        adata_filtered_100UMI_no_group_outliers.n_obs,
        adata_filtered_100UMI_balanced_3000cells_by_OD.n_obs,
        adata_filtered_100UMI_balanced_no_reptech_outliers.n_obs,
        adata_filtered_100UMI_balanced_min6cells_per_RepTech.n_obs,
    ],
    "n_genes": [
        adata_raw_filtered_100UMI.n_vars,
        adata_filtered_100UMI_no_top5_outliers.n_vars,
        adata_filtered_100UMI_no_group_outliers.n_vars,
        adata_filtered_100UMI_balanced_3000cells_by_OD.n_vars,
        adata_filtered_100UMI_balanced_no_reptech_outliers.n_vars,
        adata_filtered_100UMI_balanced_min6cells_per_RepTech.n_vars,
    ],
}

# Create DataFrame
summary_df = pd.DataFrame(filtering_summary)
summary_df["cells_removed"] = summary_df["n_cells"].diff().fillna(0) * -1
summary_df["cells_removed"] = summary_df["cells_removed"].astype(int)

print("\n📊 Filtering Summary Report:")
print("=" * 80)
print(summary_df.to_string(index=False))
print("=" * 80)

# Calculate percentages
initial_cells = adata_raw_filtered_100UMI.n_obs
final_cells = adata_filtered_100UMI_balanced_min6cells_per_RepTech.n_obs
retention_percentage = (final_cells / initial_cells) * 100

print(f"\n📈 Overall Statistics:")
print(f"   Initial cells: {initial_cells:,}")
print(f"   Final cells: {final_cells:,}")
print(f"   Cells removed: {initial_cells - final_cells:,}")
print(f"   Retention rate: {retention_percentage:.1f}%")

# Save summary report
summary_report_path = os.path.join(OUTPUT_PATH, "filtering_summary_report.csv")
summary_df.to_csv(summary_report_path, index=False)
print(f"\n📋 Summary report saved to: {summary_report_path}")

print("\n🎉 3b Advanced cell filtering completed successfully!")

# %%
# Save filtered AnnData object (similar to 3a)
print("\n💾 Saving filtered AnnData object...")
OUTPUT_PATH_ANNDATA = "data/anndata_objects_with_complete_metadata_filtered"
OUTPUT_FILE_ANNDATA = (
    "GeneFull_raw_unique_mult_with_metadata_grouped_filtered_100UMI_3b.h5ad"
)

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_PATH_ANNDATA, exist_ok=True)

# Save the final filtered AnnData object
output_file_anndata = os.path.join(OUTPUT_PATH_ANNDATA, OUTPUT_FILE_ANNDATA)
adata_filtered_100UMI_balanced_min6cells_per_RepTech.write(output_file_anndata)

print(f"📁 Created directory: {OUTPUT_PATH_ANNDATA}")
print(f"💾 Saved filtered anndata object to: {output_file_anndata}")
print(
    f"📊 Saved {adata_filtered_100UMI_balanced_min6cells_per_RepTech.n_obs:,} cells and {adata_filtered_100UMI_balanced_min6cells_per_RepTech.n_vars:,} genes (3b filtering)"
)

# %%
# Final summary
print("\n🎉 3b analysis completed successfully!")
print(
    f"📊 Final dataset: {adata_filtered_100UMI_balanced_min6cells_per_RepTech.n_obs:,} cells × {adata_filtered_100UMI_balanced_min6cells_per_RepTech.n_vars:,} genes"
)
print(f"💾 Saved to: {output_file_anndata}")

# %%
