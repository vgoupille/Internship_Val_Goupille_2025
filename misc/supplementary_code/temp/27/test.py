# %%
import os
import scanpy as sc
import scvi  # scvi-tools
from scvi.model import SCVI
import matplotlib.pyplot as plt

# %%
# Définir le dossier de travail
os.chdir("/workspaces/microsplit_DOL")

# %%
# Charger les données brutes
adata = sc.read_h5ad("code/27/final_adata_filtered.h5ad")

# Appliquer les mêmes filtres que précédemment
adata = adata[adata.obs["CultureMedium"] == "M9F"].copy()
print(f"Forme des données brutes (non normalisées) : {adata.shape}")

# %%
# Ajouter une colonne "batch" (nécessaire pour scVI)
adata.obs["batch"] = adata.obs["RepTech"].astype(str)

# %%
# Préparer l'objet AnnData pour scVI (⚠️ utiliser les données brutes non transformées)
SCVI.setup_anndata(
    adata,
    batch_key="batch",  # correction des effets de lot
)

# %%
# Créer et entraîner le modèle scVI
model = SCVI(adata)
model.train()


# %%
adata


# %%

# Extraire les représentations latentes apprises par scVI
latent = model.get_latent_representation()  # (n_cells, n_latent)

# Ajouter à AnnData
adata.obsm["X_scVI"] = latent

# %%
# Construire le graphe de voisinage à partir de l’espace scVI
sc.pp.neighbors(adata, use_rep="X_scVI")

# %%
# Calculer l'UMAP
sc.tl.umap(adata)

# %%
# Clustering Leiden
sc.tl.leiden(adata, resolution=0.5, random_state=42)

# %%
# Visualisation finale
sc.pl.umap(adata, color=["leiden", "CultureMedium", "RepBio", "OD", "total_counts"])

# %%
