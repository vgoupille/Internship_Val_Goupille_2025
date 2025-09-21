import marimo

__generated_with = "0.15.3"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""https://scanpy.readthedocs.io/en/stable/tutorials/basics/clustering.html""")
    return


@app.cell
def _():
    import scanpy as sc
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    import anndata as ad
    import os
    import sys
    return pd, plt, sc


@app.cell
def _(sc):
    data_path = "data/Anndata/filtered/GeneFull_raw_unique_mult_with_metadata_grouped_filtered_100UMI_3c.h5ad"

    data = sc.read_h5ad(data_path)

    print(data)
    return (data,)


@app.cell
def _(data, sc):
    sc.pp.calculate_qc_metrics(
        data, inplace=True, log1p=True
    )
    return


@app.cell
def _(data):
    data.obs
    return


@app.cell
def _(data):
    data.var
    return


@app.cell
def _(data):
    data.obs.sample(10, random_state=42)   # aleatoire
    return


@app.cell
def _():
    #help(sc)
    return


@app.cell
def _(data):
    data.obs.columns.to_list()
    return


@app.cell
def _(data):
    data.obs.nunique()  # unique value counts for each column
    return


@app.cell
def _(data, sc):
    sc.pl.violin(data, keys='n_genes_by_counts', groupby='CultureMedium' )
    return


@app.cell
def _(data, pd):
    # nombre de RepTech for each OD (contigency table)

    pd.crosstab(data.obs['OD'], data.obs['RepTech'])
    return


@app.cell
def _(data):
    data.obs['RepTech'].value_counts() # count of cells for each RepTech
    return


@app.cell
def _(data):
    grouped = data.obs.groupby("CultureMedium")["n_genes_by_counts"].mean()
    grouped
    return


@app.cell
def _(data, plt):
    # nombre de genes detected in each CultureMedium
    data.obs.groupby("CultureMedium", observed=True)["n_genes_by_counts"].mean().plot(kind="bar")
    plt.ylabel("Mean number of genes detected")
    plt.title("Mean number of genes detected in each CultureMedium")
    plt.show()
    return


@app.cell
def _(data):
    # nombre de cell dans chaque RepTech-sample pour chaque OD
    data.obs.groupby("OD", observed=True)["RepTech_suffix"].value_counts()
    return


@app.cell
def _(data):
    # nombre de cell dans chaque RepTech-sample pour chaque OD
    #data.obs.groupby("OD", observed=True)["RepTech_suffix"].unique().apply(len)
    data.obs.groupby("OD", observed=True)["RepTech_suffix"].nunique()
    return


@app.cell
def _(data):
    # nombre moyen de genes detected for each sample (OD)

    data.obs.groupby('OD')['n_genes_by_counts'].mean().plot(kind='bar')
    return


@app.cell
def _(data):

    data.obs.groupby('OD')['total_counts'].mean().plot(kind='bar')
    return


@app.cell
def _(data, sc):
    sc.pl.violin(
        data,
        ["n_genes_by_counts", "total_counts"], groupby="OD",
        jitter=0.4,
        multi_panel=True,
        rotation=45,
    )
    return


@app.cell
def _(data):
    # Saving count data
    data.layers["counts"] = data.X.copy()
    return


@app.cell
def _(data):
    data.layers
    return


@app.cell
def _(mo):
    mo.md(r"""On va devoir regarder chaque sous groupe de maniere indepednante""")
    return


@app.cell
def _(data):
    data_nm = data.copy()
    return (data_nm,)


@app.cell
def _(data_nm, sc):
    # Normalize to median total counts and save in 'normalized' layer
    data_nm.layers["normalized"] = data_nm.layers["counts"].copy()
    sc.pp.normalize_total(data_nm, layer="normalized", copy=False)  # target_sum=1000

    # Log transform normalized data_nm and save in 'log1p' layer
    data_nm.layers["log1p"] = data_nm.layers["normalized"].copy()
    sc.pp.log1p(data_nm, layer="log1p", copy=False)

    # Keep normalized and log-transformed data_nm in main matrix
    data_nm.X = data_nm.layers["log1p"].copy()
    return


@app.cell
def _(data_nm):
    data_nm.layers
    return


@app.cell
def _(data_nm):
    data_nm.var
    return


@app.cell
def _(data_nm):
    data_hvg = data_nm.copy()
    return (data_hvg,)


@app.cell
def _(data_hvg, sc):

    #Identify highly variable genes using log1p normalized data
    #This helps focus on genes with high cell-to-cell variation
    sc.pp.highly_variable_genes(
        data_hvg,
        n_top_genes=2000,  # batch_key="sample"
    )
    data_hvg.var["highly_variable"]
    return


@app.cell
def _(data_hvg, sc):
    sc.pl.highly_variable_genes(data_hvg) # visualize highly variable genes
    return


@app.cell
def _(data_hvg):
    data_hvg_f = data_hvg[:, data_hvg.var.highly_variable]
    data_hvg_f.var
    return (data_hvg_f,)


@app.cell
def _(data_hvg_f):
    data_hvg_f
    return


@app.cell
def _(data_hvg_f):
    # create a new Anndata for the scalling 
    data_hvg_f_sc = data_hvg_f.copy()
    data_hvg_f_sc.layers["scaled"] = data_hvg_f_sc.layers["log1p"].copy()
    return (data_hvg_f_sc,)


@app.cell
def _(data_hvg_f_sc, sc):
    # Scale data and save in 'scaled' layer

    sc.pp.scale(data_hvg_f_sc, max_value=10, zero_center=True, layer="scaled", copy=False)
    # save it in the main matrix
    data_hvg_f_sc.X = data_hvg_f_sc.layers["scaled"].copy()
    return


@app.cell
def _(data_hvg_f_sc, sc):
    sc.tl.pca(data_hvg_f_sc)
    return


@app.cell
def _(data_hvg_f_sc, sc):
    sc.pl.pca_variance_ratio(data_hvg_f_sc, n_pcs=50, log=True)
    sc.pl.pca_variance_ratio(data_hvg_f_sc, n_pcs=50, log=False)
    return


@app.cell
def _(data_hvg_f_sc, sc):
    sc.pl.pca(
        data_hvg_f_sc,
        ncols=2,
        color=["CultureMedium", "group", "OD", "total_counts"],
        alpha=1,
        cmap="viridis",
        title=[
            "Culture Medium",
            " Sampling Time",
            "Individual Samples at sampling Time",
            "Total mRNA UMIs per Cell Barcode",
        ],
        wspace=0.5,  # Increase horizontal spacing between plots
        hspace=0.4,  # Increase vertical spacing between plots
    )
    return


if __name__ == "__main__":
    app.run()
