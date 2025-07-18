import anndata as ad
import os

folder = "anndata_objects"
files = sorted([f for f in os.listdir(folder) if f.endswith(".h5ad")])

for f in files:
    print(f"\n--- {f} ---")
    adata = ad.read_h5ad(os.path.join(folder, f))
    print(f"Shape: {adata.shape}")
    print(f"obs (barcodes): {adata.obs.shape}")
    print(f"var (features): {adata.var.shape}")
    print(f"obs_names[:3]: {list(adata.obs_names[:3])}")
    print(f"var_names[:3]: {list(adata.var_names[:3])}")
    print(f"obs columns: {list(adata.obs.columns)}")
    print(f"var columns: {list(adata.var.columns)}")
    print(f"uns: {adata.uns}")
