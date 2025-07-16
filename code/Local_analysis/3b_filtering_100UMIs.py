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

from visualization_functions import (
    plot_cell_counts_comparison,
    plot_stacked_bar_by_odt,
    plot_scatter_and_density_by_medium,
    plot_violin_comparison_m9_m9f,
)

# %%
# Constants for better maintainability
UMI_THRESHOLD = 100
DATA_PATH = "data/anndata_objects_with_complete_metadata/"
OUTPUT_PATH = "data/anndata_objects_with_complete_metadata_filtered"
INPUT_FILE = "GeneFull_raw_unique_mult_with_metadata.h5ad"
OUTPUT_FILE = "GeneFull_raw_unique_mult_with_metadata_grouped_filtered_100UMI.h5ad"


# %%
def create_group_from_od(od_value: str) -> str:
    """
    Create Group variable from OD value.
    Extracts the medium and OD parts, removing the middle letter (A, B, C).

    Example: "OD M9_C_OD3" -> "M9_OD3"
    Example: "M9_C_OD3" -> "M9_OD3"

    Args:
        od_value (str): Original OD value

    Returns:
        str: Processed group name
    """
    if not isinstance(od_value, str):
        return str(od_value)

    # Remove "OD " prefix if present
    processed_value = od_value[3:] if od_value.startswith("OD ") else od_value

    # Split by underscore to get parts
    parts = processed_value.split("_")

    if len(parts) >= 3:
        # Get the medium part (first part) and OD part (last part)
        medium_part = parts[0]  # e.g., "M9"
        od_part = parts[-1]  # e.g., "OD3"
        return f"{medium_part}_{od_part}"

    return od_value


# %%
def add_suffix_columns(adata: ad.AnnData) -> None:
    """
    Add suffix columns for RepTech and RepBio in-place.

    Args:
        adata (ad.AnnData): AnnData object to modify
    """
    # Extract suffixes efficiently using vectorized operations
    adata.obs["RepTech_suffix"] = adata.obs["RepTech"].str.split("_").str[-1]
    adata.obs["RepBio_suffix"] = adata.obs["RepBio"].str.split("_").str[-1]


# %%
def calculate_qc_metrics(adata: ad.AnnData) -> None:
    """
    Calculate QC metrics (n_counts, n_genes) in-place.

    Args:
        adata (ad.AnnData): AnnData object to modify
    """
    # Calculate QC metrics efficiently
    adata.obs["n_counts"] = np.array(adata.X.sum(axis=1)).flatten()
    adata.obs["n_genes"] = np.array((adata.X > 0).sum(axis=1)).flatten()


# %%
def print_group_summary(adata: ad.AnnData) -> None:
    """
    Print summary of Group variable creation.

    Args:
        adata (ad.AnnData): AnnData object to analyze
    """
    print(f"📋 OD to Group mapping:")
    unique_mappings = adata.obs[["OD", "Group"]].drop_duplicates()
    for _, row in unique_mappings.iterrows():
        print(f"   {row['OD']} -> {row['Group']}")

    print(f"\n🧬 New Group column created!")
    print(f"🔢 Number of unique Group values: {len(adata.obs['Group'].unique())}")
    print(f"📋 Unique Group values: {sorted(adata.obs['Group'].unique())}")

    # Show distribution of cells per Group
    print(f"\n📊 Distribution of cells per Group:")
    group_counts = adata.obs["Group"].value_counts()
    for group, count in group_counts.items():
        print(f"   {group}: {count:,} cells")


# %%
def filter_cells_by_umi(
    adata: ad.AnnData, threshold: int = UMI_THRESHOLD
) -> ad.AnnData:
    """
    Filter cells based on UMI count threshold.

    Args:
        adata (ad.AnnData): Input AnnData object
        threshold (int): Minimum UMI count threshold

    Returns:
        ad.AnnData: Filtered AnnData object
    """
    print(f"📊 Before filtering: {adata.n_obs:,} cells")

    # Create mask for cells to keep
    cells_to_keep = adata.obs["n_counts"] >= threshold

    # Apply filtering
    adata_filtered = adata[cells_to_keep, :].copy()

    print(
        f"📊 After filtering (n_counts >= {threshold}): {adata_filtered.n_obs:,} cells"
    )
    print(f"🗑️ Removed {adata.n_obs - adata_filtered.n_obs:,} cells")

    return adata_filtered


# %%
def print_filtering_summary(adata: ad.AnnData) -> None:
    """
    Print summary statistics after filtering.

    Args:
        adata (ad.AnnData): Filtered AnnData object
    """
    n_counts_stats = adata.obs["n_counts"]
    print(f"\n📈 Summary statistics after filtering:")
    print(f"   Mean n_counts: {n_counts_stats.mean():.2f}")
    print(f"   Median n_counts: {n_counts_stats.median():.2f}")
    print(f"   Min n_counts: {n_counts_stats.min():.2f}")
    print(f"   Max n_counts: {n_counts_stats.max():.2f}")


# %%
def run_visualizations(adata: ad.AnnData) -> None:
    """
    Run all visualization functions.

    Args:
        adata (ad.AnnData): AnnData object for visualization
    """
    print("🔧 Running all visualization functions...")

    # 1. Stacked bar plot by ODt
    print("\n1️⃣ Creating stacked bar plot by ODt...")
    total_all, total_by_medium = plot_stacked_bar_by_odt(adata)

    # 2. Scatter plots and density distributions
    print("\n2️⃣ Creating scatter plots and density distributions...")
    plot_scatter_and_density_by_medium(adata)

    # 3. Violin plot comparison M9 vs M9F
    print("\n3️⃣ Creating violin plot comparison...")
    plot_violin_comparison_m9_m9f(adata)

    print("\n✅ All visualization functions completed successfully!")


# %%
# Set working directory
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# %%
# Load data
print("📂 Loading data...")
adata_original = ad.read_h5ad(os.path.join(DATA_PATH, INPUT_FILE))
adata = adata_original.copy()

# %%
# Process Group variable
print("🔧 Creating new Group variable from OD column...")
adata.obs["Group"] = adata.obs["OD"].apply(create_group_from_od)
print_group_summary(adata)

# %%
# Calculate QC metrics
print("\n🧮 Calculating QC metrics...")
calculate_qc_metrics(adata)

# %%
# Add suffix columns
print("🏷️ Adding suffix columns...")
add_suffix_columns(adata)

# %%
# Show basic info about the data
print("\n📊 Basic data exploration:")
print(f"🔢 adata.obs columns: {list(adata.obs.columns)}")
print(f"🔢 adata.var columns: {list(adata.var.columns)}")

# %%
# Show QC metrics statistics
print("\n📈 QC metrics statistics:")
print("n_counts statistics:")
print(adata.obs["n_counts"].describe())
print("\nn_genes statistics:")
print(adata.obs["n_genes"].describe())

# %%
# Show group statistics
print("\n📋 Group statistics by RepTech:")
print(adata.obs.groupby("RepTech")["n_counts"].describe())
print(f"\nCount by RepTech:")
print(adata.obs.groupby("RepTech")["n_counts"].count())

# %%
# Filter cells by UMI threshold
print(f"\n🔍 Filtering cells with n_counts < {UMI_THRESHOLD}...")
adata_filtered = filter_cells_by_umi(adata, UMI_THRESHOLD)
print_filtering_summary(adata_filtered)

# %%
# Create comparison plot
print("\n📊 Creating comparison plot...")
plot_cell_counts_comparison(
    adata_original, adata_filtered, filter_threshold=UMI_THRESHOLD
)

# %%
# Run visualizations
run_visualizations(adata_filtered)

# %%
# Save results
print("\n💾 Saving results...")
os.makedirs(OUTPUT_PATH, exist_ok=True)
output_file = os.path.join(OUTPUT_PATH, OUTPUT_FILE)
adata_filtered.write(output_file)

print(f"📁 Created directory: {OUTPUT_PATH}")
print(f"💾 Saved filtered anndata object to: {output_file}")
print(
    f"📊 Saved {adata_filtered.n_obs:,} cells and {adata_filtered.n_vars:,} genes (filtered at {UMI_THRESHOLD} UMI)"
)

# %%
# Final summary
print("\n🎉 Analysis completed successfully!")
print(
    f"📊 Final dataset: {adata_filtered.n_obs:,} cells × {adata_filtered.n_vars:,} genes"
)
print(f"💾 Saved to: {output_file}")

# %%
