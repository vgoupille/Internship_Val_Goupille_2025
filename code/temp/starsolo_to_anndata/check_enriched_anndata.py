import anndata as ad
import os

folder = "metadata"
files = sorted([f for f in os.listdir(folder) if f.endswith(".h5ad")])

for f in files:
    print(f"\n--- {f} ---")
    adata = ad.read_h5ad(os.path.join(folder, f))
    print(f"Shape: {adata.shape}")
    print(f"var columns (features): {list(adata.var.columns)}")
    print(f"uns metadata: {adata.uns}")

    # Show some examples of the new metadata
    print(
        f"Gene Type examples: {list(adata.var['Gene Type'].value_counts().head(3).index)}"
    )
    print(f"Symbol examples: {list(adata.var['Symbol'].dropna().head(3))}")
    print(f"Name examples: {list(adata.var['Name'].head(3))}")
