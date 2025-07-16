"""
Visualization functions for single-cell analysis.
This module contains functions for creating plots and visualizations of anndata objects.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import gaussian_kde


def plot_cell_counts_comparison(
    adata_before, adata_after, filter_threshold=100, figsize=(14, 8)
):
    """
    Create a beautiful comparison plot of cell counts per culture medium before and after filtering.

    Parameters:
    -----------
    adata_before : AnnData
        AnnData object before filtering
    adata_after : AnnData
        AnnData object after filtering
    filter_threshold : int
        The threshold used for filtering (for title)
    figsize : tuple
        Figure size (width, height)
    """
    plt.figure(figsize=figsize)

    # Count cells per culture medium BEFORE filtering
    cell_counts_before = adata_before.obs["CultureMedium"].value_counts()

    # Count cells per culture medium AFTER filtering
    cell_counts_after = adata_after.obs["CultureMedium"].value_counts()

    # Reorder culture mediums: M9F first (left), M9 second (right)
    culture_mediums_ordered = []
    for medium in cell_counts_before.index:
        if "M9F" in medium:
            culture_mediums_ordered.append(medium)
    for medium in cell_counts_before.index:
        if "M9" in medium and "F" not in medium:
            culture_mediums_ordered.append(medium)
    for medium in cell_counts_before.index:
        if "M9" not in medium:
            culture_mediums_ordered.append(medium)

    # Reorder the data according to the new order
    cell_counts_before_ordered = cell_counts_before.reindex(culture_mediums_ordered)
    cell_counts_after_ordered = cell_counts_after.reindex(culture_mediums_ordered)

    # Create color palette
    colors = []
    for medium in culture_mediums_ordered:
        if "M9" in medium and "F" not in medium:  # M9
            colors.append("#FF6B6B")  # Red
        elif "M9F" in medium:  # M9F
            colors.append("#2ECC71")  # Green
        else:  # Other mediums
            colors.append("#95A5A6")  # Gray for other

    # Set up the bar positions
    x = np.arange(len(culture_mediums_ordered))
    width = 0.35

    # Create bar plot
    bars_before = plt.bar(
        x - width / 2,
        cell_counts_before_ordered.values,
        width,
        color=colors,
        alpha=0.7,
        edgecolor="black",
        linewidth=1,
    )
    bars_after = plt.bar(
        x + width / 2,
        cell_counts_after_ordered.values,
        width,
        color=colors,
        alpha=0.9,
        edgecolor="black",
        linewidth=1,
    )

    # Customize the plot
    plt.title(
        f"Number of Barcodes per Culture Medium: Not Filtered vs Filtered (n_counts > {filter_threshold})",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )
    plt.xlabel("Culture Medium", fontsize=14, fontweight="bold")
    plt.ylabel("Number of Barcodes", fontsize=14, fontweight="bold")

    # Set x-axis labels
    plt.xticks(
        x,
        culture_mediums_ordered,
        rotation=0,
        ha="center",
        fontsize=12,
        fontweight="bold",
    )

    # Add "Before" and "After" labels under each bar group
    for i, medium in enumerate(culture_mediums_ordered):
        plt.text(
            x[i] - width / 2,
            -max(cell_counts_before_ordered.values) * 0.05,
            "Not filtered",
            ha="center",
            va="top",
            fontsize=10,
            fontweight="bold",
        )
        plt.text(
            x[i] + width / 2,
            -max(cell_counts_before_ordered.values) * 0.05,
            f"Filtered\n(n_counts > {filter_threshold})",
            ha="center",
            va="top",
            fontsize=10,
            fontweight="bold",
        )

    # Add value labels on top of each bar
    for bar, count in zip(bars_before, cell_counts_before_ordered.values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(cell_counts_before_ordered.values) * 0.01,
            f"{count:,}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    for bar, count in zip(bars_after, cell_counts_after_ordered.values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(cell_counts_before_ordered.values) * 0.01,
            f"{count:,}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    # Add percentage labels inside bars
    total_before = cell_counts_before_ordered.sum()
    total_after = cell_counts_after_ordered.sum()

    for bar, count in zip(bars_before, cell_counts_before_ordered.values):
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

    for bar, count in zip(bars_after, cell_counts_after_ordered.values):
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
        bbox=dict(
            boxstyle="round,pad=0.3", facecolor="white", alpha=0.9, edgecolor="gray"
        ),
    )

    # Show the plot
    plt.show()

    # Print detailed statistics
    print(
        f"\n📊 Cell Count Summary: Before vs After Filtering (n_counts ≥ {filter_threshold}):"
    )
    print(f"📈 Total barcodes before filtering: {total_before:,}")
    print(f"📈 Total barcodes after filtering: {total_after:,}")
    print(
        f"🗑️ Barcodes removed: {total_before - total_after:,} ({(total_before - total_after)/total_before*100:.1f}%)"
    )

    print(f"\n🍽️ Breakdown by Culture Medium:")
    for medium in culture_mediums_ordered:
        before_count = cell_counts_before_ordered[medium]
        after_count = cell_counts_after_ordered.get(medium, 0)
        removed_count = before_count - after_count
        removed_percentage = (
            (removed_count / before_count) * 100 if before_count > 0 else 0
        )

        print(f"\n   {medium}:")
        print(f"     Before: {before_count:,} barcodes")
        print(f"     After: {after_count:,} barcodes")
        print(f"     Removed: {removed_count:,} barcodes ({removed_percentage:.1f}%)")


def plot_stacked_bar_by_odt(adata, figsize_per_plot=6):
    """
    Create stacked bar plots grouped by ODt showing RepBio and RepTech_suffix distribution.
    Uses group logic combining CultureMedium and ODt (e.g., M9_sampling_t1, M9F_sampling_t2).

    Parameters:
    -----------
    adata : AnnData
        AnnData object with obs containing ODt, RepBio, CultureMedium, and RepTech_suffix columns
    figsize_per_plot : int
        Width of each subplot
    """
    # Ensure RepTech_suffix exists
    if "RepTech_suffix" not in adata.obs.columns:
        adata.obs["RepTech_suffix"] = adata.obs["RepTech"].str.split("_").str[-1]

    # Création de la colonne de regroupement 'group' selon la logique demandée
    def assign_group(row):
        prefix = row["CultureMedium"]  # M9 ou M9F
        odt = row["ODt"]
        if odt == "OD1":
            suffix = "sampling_t1"
        elif odt == "OD2":
            suffix = "sampling_t2"
        elif odt == "OD3":
            suffix = "sampling_t3"
        else:
            suffix = "sampling_unknown"
        return f"{prefix}_{suffix}"

    # Create the group column
    adata.obs["group"] = adata.obs.apply(assign_group, axis=1)

    # Grouper les données par la nouvelle colonne 'group', RepBio et RepTech_suffix
    counts = (
        adata.obs.groupby(["group", "RepBio", "RepTech_suffix"])
        .size()
        .reset_index(name="counts")
    )

    # Obtenir la liste des groupes (panels)
    group_labels = sorted(counts["group"].unique())
    n = len(group_labels)

    # Define fixed order of suffixes to ensure consistent colors across scripts
    ALL_POSSIBLE_SUFFIXES = ["1", "2", "3", "4", "5"]
    available_suffixes = sorted(counts["RepTech_suffix"].unique())

    # Use fixed color mapping based on all possible suffixes
    colors = plt.get_cmap("tab20").colors
    color_map = {
        suffix: colors[i % len(colors)]
        for i, suffix in enumerate(ALL_POSSIBLE_SUFFIXES)
    }

    # Création des sous-graphes
    fig, axes = plt.subplots(1, n, figsize=(figsize_per_plot * n, 8), sharey=True)

    if n == 1:
        axes = [axes]

    total_all = 0

    for ax, group in zip(axes, group_labels):
        df_group = counts[counts["group"] == group]

        # Extraire culture_medium (M9 ou M9F) et temps
        culture_medium = group.split("_")[0]  # M9 ou M9F
        sampling_time = group.split("_")[1]  # sampling_t1, sampling_t2, sampling_t3

        # Définir les RepBio attendus pour ce groupe
        if culture_medium == "M9":
            expected_repbios = ["M9_A", "M9_B", "M9_C"]
        elif culture_medium == "M9F":
            expected_repbios = ["M9F_A", "M9F_B", "M9F_C"]
        else:
            expected_repbios = []

        # Filtrer pour garder seulement les RepBio attendus
        df_group = df_group[df_group["RepBio"].isin(expected_repbios)]

        # Pivot pour format barres empilées
        pivot_df = df_group.pivot(
            index="RepBio", columns="RepTech_suffix", values="counts"
        ).fillna(0)

        # Réorganiser les colonnes dans l'ordre attendu
        pivot_df = pivot_df.reindex(columns=available_suffixes, fill_value=0)

        # Réorganiser les lignes dans l'ordre attendu
        if culture_medium == "M9":
            pivot_df = pivot_df.reindex(index=["M9_A", "M9_B", "M9_C"], fill_value=0)
        elif culture_medium == "M9F":
            pivot_df = pivot_df.reindex(index=["M9F_A", "M9F_B", "M9F_C"], fill_value=0)

        # Plot empilé
        pivot_df.plot(
            kind="bar",
            stacked=True,
            ax=ax,
            color=[color_map[col] for col in pivot_df.columns],
            legend=False,
            width=0.8,
        )
        bar_sums = pivot_df.sum(axis=1)
        total_plot = bar_sums.sum()
        total_all += total_plot

        # Couleur du titre selon le medium
        title_color = "green" if "M9F" in group else "red"
        ax.set_title(
            f"{group}\nTotal barcodes: n={int(total_plot)}",
            fontsize=16,
            fontweight="bold",
            color=title_color,
            pad=20,
            y=1.02,
        )
        ax.set_xlabel("")
        ax.set_ylabel("Total of Barcode Cells", fontsize=14, fontweight="bold")

        # Couleur des étiquettes X : vert si M9F, rouge si M9
        xtick_labels = pivot_df.index.tolist()
        colors_xticks = ["green" if "M9F" in label else "red" for label in xtick_labels]
        ax.set_xticks(np.arange(len(xtick_labels)))
        ax.set_xticklabels(
            xtick_labels, rotation=0, ha="center", fontsize=12, fontweight="bold"
        )

        for label, color in zip(ax.get_xticklabels(), colors_xticks):
            label.set_color(color)

        # Affichage des counts (n=...) au-dessus des barres
        for i, val in enumerate(bar_sums):
            ax.text(
                i,
                val + 1,
                f"(n={int(val)})",
                ha="center",
                va="bottom",
                fontsize=14,
                fontweight="bold",
            )

    # Légende globale
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        title="RepTech",
        loc="center right",
        bbox_to_anchor=(0.85, 0.5),
        fontsize=16,
        title_fontsize=18,
    )

    # Total global en haut à gauche
    fig.text(
        0.01,
        1.02,
        f"Total barcodes across all groups = {int(total_all)}",
        ha="left",
        va="bottom",
        fontsize=14,
        fontweight="bold",
        color="black",
    )

    # Total par CultureMedium
    total_by_medium = (
        adata.obs.groupby("CultureMedium")
        .size()
        .reindex(["M9", "M9F"])
        .fillna(0)
        .astype(int)
    )

    # Affichage juste à droite du total global
    fig.text(
        0.15,
        1.02,
        f"Total M9  = {total_by_medium.get('M9', 0)}",
        ha="left",
        va="bottom",
        fontsize=12,
        fontweight="bold",
    )
    fig.text(
        0.15,
        0.99,
        f"Total M9F = {total_by_medium.get('M9F', 0)}",
        ha="left",
        va="bottom",
        fontsize=12,
        fontweight="bold",
    )

    # Mise en page finale
    plt.tight_layout(rect=[0, 0, 0.78, 1])
    plt.show()

    return total_all, total_by_medium


def plot_scatter_and_density_by_medium(adata, figsize_per_col=5, max_cols=3):
    """
    Create scatter plots and density distributions for each culture medium.

    Parameters:
    -----------
    adata : AnnData
        AnnData object with obs containing n_counts, n_genes, and CultureMedium columns
    figsize_per_col : int
        Width of each column in the plot
    max_cols : int
        Maximum number of columns in the subplot layout
    """
    # Get unique culture mediums and create color map
    culture_mediums = adata.obs["CultureMedium"].unique()
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

    # Reorder culture mediums: M9F first, then M9, then others
    culture_mediums_ordered = []
    for medium in culture_mediums:
        if "M9F" in medium:
            culture_mediums_ordered.append(medium)
    for medium in culture_mediums:
        if "M9" in medium and "F" not in medium:
            culture_mediums_ordered.append(medium)
    for medium in culture_mediums:
        if "M9" not in medium:
            culture_mediums_ordered.append(medium)

    n_mediums = len(culture_mediums_ordered)
    n_cols = min(max_cols, n_mediums)
    n_rows = 2 * n_mediums  # 2 rows per medium (scatter + density)

    fig, axes = plt.subplots(
        n_rows, n_cols, figsize=(figsize_per_col * n_cols, 3 * n_rows)
    )
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

    # Calculate global density limits
    global_density_max = 0
    for medium in culture_mediums_ordered:
        mask = adata.obs["CultureMedium"] == medium
        medium_data = adata.obs.loc[mask]

        if len(medium_data) > 1:
            hist, bins = np.histogram(
                medium_data["n_counts"], bins=30, density=True, range=global_x_lim
            )
            hist_max = hist.max()

            kde = gaussian_kde(medium_data["n_counts"])
            x_range = np.linspace(global_x_lim[0], global_x_lim[1], 100)
            kde_density = kde(x_range)
            kde_max = kde_density.max()

            medium_max = max(hist_max, kde_max)
            global_density_max = max(global_density_max, medium_max)

    global_density_y_lim = (0, global_density_max * 1.1)

    for i, medium in enumerate(culture_mediums_ordered):
        col_idx = i % n_cols
        scatter_row = (i // n_cols) * 2
        density_row = (i // n_cols) * 2 + 1

        mask = adata.obs["CultureMedium"] == medium
        medium_data = adata.obs.loc[mask]

        # Create scatter plot
        scatter_idx = scatter_row * n_cols + col_idx
        ax_scatter = axes_flat[scatter_idx]
        ax_scatter.scatter(
            medium_data["n_counts"],
            medium_data["n_genes"],
            alpha=0.7,
            s=8,
            c=color_map[medium],
            edgecolors="none",
        )

        # Calculate correlation
        if len(medium_data) > 1:
            corr = np.corrcoef(medium_data["n_counts"], medium_data["n_genes"])[0, 1]
            ax_scatter.text(
                0.98,
                0.98,
                f"Correlation: {corr:.3f}",
                transform=ax_scatter.transAxes,
                fontsize=9,
                ha="right",
                va="top",
                bbox=dict(
                    boxstyle="round,pad=0.3",
                    facecolor="white",
                    alpha=0.9,
                    edgecolor="gray",
                ),
            )

        # Add barcode count
        barcode_text = f"Barcodes: {len(medium_data):,}"
        ax_scatter.text(
            0.02,
            0.98,
            barcode_text,
            transform=ax_scatter.transAxes,
            fontsize=8,
            ha="left",
            va="top",
            bbox=dict(
                boxstyle="round,pad=0.3", facecolor="white", alpha=0.9, edgecolor="gray"
            ),
        )

        # Customize scatter subplot
        ax_scatter.set_xlabel("Total of UMIs per Cell", fontsize=10, fontweight="bold")
        ax_scatter.set_ylabel("Total of Genes per Cell", fontsize=10, fontweight="bold")
        ax_scatter.set_title(
            f"{medium} - Scatter Plot", fontsize=12, fontweight="bold", pad=10
        )
        ax_scatter.grid(True, alpha=0.3, linestyle="--")
        ax_scatter.set_xlim(global_x_lim)
        ax_scatter.set_ylim(global_y_lim)

        # Create density plot
        density_idx = density_row * n_cols + col_idx
        ax_density = axes_flat[density_idx]

        ax_density.hist(
            medium_data["n_counts"],
            bins=30,
            alpha=0.7,
            color=color_map[medium],
            edgecolor="black",
            linewidth=0.5,
            density=True,
            range=global_x_lim,
        )

        # Add KDE curve
        if len(medium_data) > 1:
            kde = gaussian_kde(medium_data["n_counts"])
            x_range = np.linspace(global_x_lim[0], global_x_lim[1], 100)
            ax_density.plot(
                x_range, kde(x_range), color="black", linewidth=2, label="KDE"
            )

        # Customize density subplot
        ax_density.set_xlabel("Total of UMIs per Cell", fontsize=10, fontweight="bold")
        ax_density.set_ylabel("Density", fontsize=10, fontweight="bold")
        ax_density.set_title(
            f"{medium} - Distribution", fontsize=12, fontweight="bold", pad=10
        )
        ax_density.grid(True, alpha=0.3, linestyle="--")
        ax_density.legend(fontsize=8)
        ax_density.set_xlim(global_x_lim)
        ax_density.set_ylim(global_density_y_lim)

    # Hide empty subplots
    for i in range(n_mediums * 2, len(axes_flat)):
        axes_flat[i].set_visible(False)

    plt.suptitle(
        "Cell Quality by Culture Medium with Density Distributions (Filtered: n_counts ≥ 100)",
        fontsize=16,
        fontweight="bold",
        y=0.98,
    )
    plt.tight_layout()
    plt.show()

    # Print detailed statistics
    print(
        f"\n📊 Detailed Statistics by Culture Medium (After filtering: n_counts ≥ 100):"
    )
    for medium in culture_mediums_ordered:
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


def plot_violin_comparison_m9_m9f(adata, figsize=(10, 8)):
    """
    Create violin plots comparing M9 and M9F for n_counts and n_genes.

    Parameters:
    -----------
    adata : AnnData
        AnnData object with obs containing n_counts, n_genes, and CultureMedium columns
    figsize : tuple
        Figure size (width, height)
    """
    # Filter data for M9 and M9F only
    m9_m9f_mask = adata.obs["CultureMedium"].isin(["M9", "M9F"])
    adata_m9_m9f = adata[m9_m9f_mask].copy()

    if len(adata_m9_m9f) == 0:
        print("⚠️ No M9 or M9F data found for violin plot comparison")
        return

    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)

    # Violin plot for n_counts (top)
    sns.violinplot(
        data=adata_m9_m9f.obs,
        x="CultureMedium",
        y="n_counts",
        ax=ax1,
        order=["M9F", "M9"],
        palette=["#2ECC71", "#FF6B6B"],
    )
    ax1.set_title(
        "Total of UMIs per Barcode Cell by Culture Medium",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    ax1.set_xlabel("Culture Medium", fontsize=12, fontweight="bold")
    ax1.set_ylabel("Total of UMIs per Barcode Cell", fontsize=12, fontweight="bold")
    ax1.grid(True, alpha=0.3, linestyle="--")

    # Add statistics for n_counts
    for i, medium in enumerate(["M9F", "M9"]):
        if medium in adata_m9_m9f.obs["CultureMedium"].values:
            medium_data = adata_m9_m9f.obs[adata_m9_m9f.obs["CultureMedium"] == medium]
            median_val = medium_data["n_counts"].median()
            q1_val = medium_data["n_counts"].quantile(0.25)
            q3_val = medium_data["n_counts"].quantile(0.75)

            x_pos = 0.02 if medium == "M9F" else 0.98
            ha_align = "left" if medium == "M9F" else "right"

            ax1.text(
                x_pos,
                0.98,
                f"{medium}:\nMedian: {median_val:.0f}\nQ1: {q1_val:.0f}\nQ3: {q3_val:.0f}",
                transform=ax1.transAxes,
                fontsize=10,
                ha=ha_align,
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
        order=["M9F", "M9"],
        palette=["#2ECC71", "#FF6B6B"],
    )
    ax2.set_title(
        "Total of Genes per Barcode Cell by Culture Medium",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    ax2.set_xlabel("Culture Medium", fontsize=12, fontweight="bold")
    ax2.set_ylabel("Total of Genes per Barcode Cell", fontsize=12, fontweight="bold")
    ax2.grid(True, alpha=0.3, linestyle="--")

    # Add statistics for n_genes
    for i, medium in enumerate(["M9F", "M9"]):
        if medium in adata_m9_m9f.obs["CultureMedium"].values:
            medium_data = adata_m9_m9f.obs[adata_m9_m9f.obs["CultureMedium"] == medium]
            median_val = medium_data["n_genes"].median()
            q1_val = medium_data["n_genes"].quantile(0.25)
            q3_val = medium_data["n_genes"].quantile(0.75)

            x_pos = 0.02 if medium == "M9F" else 0.98
            ha_align = "left" if medium == "M9F" else "right"

            ax2.text(
                x_pos,
                0.98,
                f"{medium}:\nMedian: {median_val:.0f}\nQ1: {q1_val:.0f}\nQ3: {q3_val:.0f}",
                transform=ax2.transAxes,
                fontsize=10,
                ha=ha_align,
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

    for medium in ["M9F", "M9"]:
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


def filter_top_n_cells(adata, n=5, metric="n_counts", copy=True):
    """
    Filter the top N cells with highest values for a given metric.

    Parameters:
    -----------
    adata : AnnData
        AnnData object to filter
    n : int
        Number of top cells to keep
    metric : str
        Column name to use for filtering (default: "n_counts")
    copy : bool
        Whether to return a copy or modify in place

    Returns:
    --------
    AnnData or None
        Filtered AnnData object if copy=True, otherwise None
    """
    if metric not in adata.obs.columns:
        raise ValueError(f"Column '{metric}' not found in adata.obs")

    # Get top N cells
    top_cells_idx = adata.obs[metric].nlargest(n).index

    # Filter the data
    if copy:
        adata_filtered = adata[top_cells_idx].copy()

        print(f"🔝 Filtered to top {n} cells by {metric}")
        print(f"📊 Cells before filtering: {adata.n_obs:,}")
        print(f"📊 Cells after filtering: {adata_filtered.n_obs:,}")

        print(f"\n📈 Top {n} cells by {metric}:")
        for i, idx in enumerate(top_cells_idx):
            value = adata.obs.loc[idx, metric]
            culture_medium = (
                adata.obs.loc[idx, "CultureMedium"]
                if "CultureMedium" in adata.obs.columns
                else "N/A"
            )
            print(
                f"   {i+1}. Cell {idx}: {metric} = {value:.0f}, Culture: {culture_medium}"
            )

        return adata_filtered
    else:
        # Modify in place
        adata._inplace_subset_obs(top_cells_idx)
        print(f"🔝 Filtered to top {n} cells by {metric}")
        print(f"📊 Cells after filtering: {adata.n_obs:,}")

        return None


def plot_violin_stripplot_by_group(
    adata,
    y_column: str,
    y_label: str,
    title_suffix: str = "",
    figsize_per_plot: int = 6,
    kde_bandwidth: float = 0.3,
    alpha: float = 0.3,
    stripplot_size: int = 4,
    stripplot_alpha: float = 0.9,
    stripplot_jitter: float = 0.25,
) -> None:
    """
    Create violin + stripplot visualization grouped by ODt/group showing RepBio distribution.

    Parameters:
    -----------
    adata : AnnData
        AnnData object with obs containing the required columns
    y_column : str
        Column name to plot on y-axis (e.g., 'n_counts', 'n_genes')
    y_label : str
        Label for y-axis (e.g., 'Number of mRNA UMIs per Cell Barcode')
    title_suffix : str, optional
        Additional suffix for the title (default: "")
    figsize_per_plot : int, optional
        Width of each subplot (default: 6)
    kde_bandwidth : float, optional
        Bandwidth for KDE calculation (default: 0.3)
    alpha : float, optional
        Transparency for violin plots (default: 0.3)
    stripplot_size : int, optional
        Size of points in stripplot (default: 4)
    stripplot_alpha : float, optional
        Transparency for stripplot points (default: 0.9)
    stripplot_jitter : float, optional
        Jitter amount for stripplot (default: 0.25)
    """
    import seaborn as sns
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    from scipy.stats import gaussian_kde

    # Ensure RepTech_suffix exists
    if "RepTech_suffix" not in adata.obs.columns:
        adata.obs["RepTech_suffix"] = adata.obs["RepTech"].str.split("_").str[-1]

    # Création de la colonne de regroupement 'group' selon la logique demandée
    def assign_group(row):
        prefix = row["CultureMedium"]  # M9 ou M9F
        odt = row["ODt"]
        if odt == "OD1":
            suffix = "sampling_t1"
        elif odt == "OD2":
            suffix = "sampling_t2"
        elif odt == "OD3":
            suffix = "sampling_t3"
        else:
            suffix = "sampling_unknown"
        return f"{prefix}_{suffix}"

    # Create temporary dataframe for processing
    df = adata.obs.copy()
    df["group"] = df.apply(assign_group, axis=1)

    # Ensure y_column exists
    if y_column not in df.columns:
        raise ValueError(f"Column '{y_column}' not found in adata.obs")

    # Convert columns to proper types
    df["RepTech_suffix"] = df["RepTech"].astype(str).str.split("_").str[-1]
    df["ODt"] = df["ODt"].astype(str)
    df["RepBio"] = df["RepBio"].astype(str)
    df["RepTech_suffix"] = df["RepTech_suffix"].astype(str)

    # Paramètres
    group_labels = sorted(df["group"].unique())
    n = len(group_labels)

    repbios = sorted(df["RepBio"].unique())

    # Palette tab20 personnalisée dans l'ordre numérique
    reptech_suffixes = sorted(df["RepTech_suffix"].unique(), key=lambda x: int(x))
    tab20_colors = sns.color_palette("tab20", n_colors=len(reptech_suffixes))
    palette = dict(zip(reptech_suffixes, tab20_colors))

    # Groupes à colorer
    group_vert = ["M9F_A", "M9F_B", "M9F_C"]
    group_rouge = ["M9_A", "M9_B", "M9_C"]
    repbio_colors = {
        repbio: (
            "green"
            if repbio in group_vert
            else "red" if repbio in group_rouge else "gray"
        )
        for repbio in repbios
    }

    # Setup grid - une ligne avec toutes les facettes
    fig, axes = plt.subplots(1, n, figsize=(figsize_per_plot * n, 6), sharey=True)
    if n == 1:
        axes = [axes]

    handles, labels = None, None

    for i, group in enumerate(group_labels):
        ax = axes[i]
        data_group = df[df["group"] == group]

        # Extraire culture_medium (M9 ou M9F) pour définir les RepBio attendus
        culture_medium = group.split("_")[0]  # M9 ou M9F

        # Définir les RepBio attendus pour ce groupe
        if culture_medium == "M9":
            expected_repbios = ["M9_A", "M9_B", "M9_C"]
        elif culture_medium == "M9F":
            expected_repbios = ["M9F_A", "M9F_B", "M9F_C"]
        else:
            expected_repbios = []

        # Filtrer pour garder seulement les RepBio attendus
        data_group = data_group[data_group["RepBio"].isin(expected_repbios)]

        # Create violin plots using KDE
        for j, repbio in enumerate(expected_repbios):
            data_subset = data_group[data_group["RepBio"] == repbio]
            values = data_subset[y_column].dropna()

            if len(values) < 2:
                continue

            # KDE
            kde = gaussian_kde(values, bw_method=kde_bandwidth)
            x_vals = np.linspace(values.min(), values.max(), 100)
            density = kde(x_vals)
            width = 0.4
            density = density / density.max() * width

            violin_color = repbio_colors.get(repbio, "gray")

            # Tracé du violon
            ax.fill_betweenx(
                x_vals,
                j - density,
                j + density,
                color=violin_color,
                alpha=alpha,
                linewidth=1,
            )

            # Affiche n
            ax.text(
                j,
                data_group[y_column].max() * 0.95,
                f"(n = {len(values)})",
                ha="center",
                va="bottom",
                fontsize=8,
                fontweight="bold",
                color="black",
            )

        # Stripplot avec hue_order pour contrôler l'ordre de la légende
        sns.stripplot(
            data=data_group,
            x="RepBio",
            y=y_column,
            hue="RepTech_suffix",
            dodge=True,
            jitter=stripplot_jitter,
            size=stripplot_size,
            ax=ax,
            alpha=stripplot_alpha,
            edgecolor="white",
            linewidth=0.4,
            palette=palette,
            order=expected_repbios,
            hue_order=reptech_suffixes,  # Ordre numérique 1 à 5
        )

        if handles is None and ax.get_legend() is not None:
            handles, labels = ax.get_legend_handles_labels()
        if ax.get_legend():
            ax.legend_.remove()

        # Couleur du titre selon le medium
        title_color = "green" if "M9F" in group else "red"
        full_title = f"{group}{title_suffix}" if title_suffix else group
        ax.set_title(
            full_title,
            fontsize=14,
            fontweight="bold",
            color=title_color,
            pad=15,
        )
        ax.set_xticks(range(len(expected_repbios)))
        ax.set_xticklabels(expected_repbios, rotation=0, fontsize=10, fontweight="bold")
        ax.set_ylabel(y_label, fontsize=12, fontweight="bold")

        # Colorer étiquettes x
        for tick_label in ax.get_xticklabels():
            label_text = tick_label.get_text()
            tick_label.set_color(repbio_colors.get(label_text, "gray"))

    # Légende commune dans l'ordre voulu
    if handles is not None:
        fig.legend(
            handles,
            labels,
            title="RepTech_suffix",
            loc="center left",
            bbox_to_anchor=(0.95, 0.5),
            fontsize=12,
            title_fontsize=14,
        )

    plt.tight_layout(rect=[0, 0, 0.92, 1])
    plt.show()


def plot_scatter_comparison_m9f_m9(
    adata,
    x_column: str = "total_counts",
    y_column: str = "n_genes_by_counts",
    color_column: str = "OD",
    x_label: str = "Total of mRNA UMIs per Cell Barcode",
    y_label: str = "Total of mRNA genes per Cell Barcode",
    point_size: int = 20,
    figsize: tuple = (12, 5),
    m9f_palette: str = "tab20",
    m9_palette: str = "Set1",
    title_suffix: str = "",
) -> None:
    """
    Create scatter plots comparing M9F vs M9 culture mediums.

    Parameters:
    -----------
    adata : AnnData
        AnnData object with obs containing the required columns
    x_column : str, optional
        Column name for x-axis (default: "total_counts")
    y_column : str, optional
        Column name for y-axis (default: "n_genes_by_counts")
    color_column : str, optional
        Column name for coloring points (default: "OD")
    x_label : str, optional
        Label for x-axis (default: "Total of mRNA UMIs per Cell Barcode")
    y_label : str, optional
        Label for y-axis (default: "Total of mRNA genes per Cell Barcode")
    point_size : int, optional
        Size of scatter points (default: 20)
    figsize : tuple, optional
        Figure size (default: (12, 5))
    m9f_palette : str, optional
        Color palette for M9F medium (default: "tab20")
    m9_palette : str, optional
        Color palette for M9 medium (default: "Set1")
    title_suffix : str, optional
        Additional suffix for titles (default: "")
    """
    import matplotlib.pyplot as plt
    import scanpy as sc

    # Validate columns exist
    required_columns = [x_column, y_column, color_column, "CultureMedium"]
    for col in required_columns:
        if col not in adata.obs.columns:
            raise ValueError(f"Column '{col}' not found in adata.obs")

    # Créer les figures
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    # Valeurs min/max globales pour garder les mêmes échelles
    x_max = adata.obs[x_column].max()
    y_max = adata.obs[y_column].max()

    # Données M9F
    m9f_data = adata[adata.obs["CultureMedium"] == "M9F"]
    if m9f_data.n_obs > 0:
        sc.pl.scatter(
            m9f_data,
            x_column,
            y_column,
            color=color_column,
            ax=ax1,
            show=False,
            size=point_size,
            palette=m9f_palette,
        )
        m9f_title = f"M9F medium{title_suffix}" if title_suffix else "M9F medium"
        ax1.set_title(m9f_title, color="green", fontweight="bold")
        ax1.set_xlabel(x_label)
        ax1.set_ylabel(y_label)
        ax1.set_xlim(0, x_max)
        ax1.set_ylim(0, y_max)
    else:
        ax1.set_title("M9F medium - No data", color="green", fontweight="bold")
        ax1.set_xlabel(x_label)
        ax1.set_ylabel(y_label)

    # Données M9
    m9_data = adata[adata.obs["CultureMedium"] == "M9"]
    if m9_data.n_obs > 0:
        sc.pl.scatter(
            m9_data,
            x_column,
            y_column,
            color=color_column,
            ax=ax2,
            show=False,
            size=point_size,
            palette=m9_palette,
        )
        m9_title = f"M9 medium{title_suffix}" if title_suffix else "M9 medium"
        ax2.set_title(m9_title, color="red", fontweight="bold")
        ax2.set_xlabel(x_label)
        ax2.set_ylabel(y_label)
        ax2.set_xlim(0, x_max)
        ax2.set_ylim(0, y_max)
    else:
        ax2.set_title("M9 medium - No data", color="red", fontweight="bold")
        ax2.set_xlabel(x_label)
        ax2.set_ylabel(y_label)

    plt.tight_layout()
    plt.show()
