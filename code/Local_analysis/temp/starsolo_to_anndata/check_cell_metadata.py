import anndata as ad
import pandas as pd

# Charger l'objet AnnData
adata = ad.read_h5ad("metadata/Gene_filtered.h5ad")

print("=== MÉTADONNÉES DES CELLULES (obs) ===")
print()

print("Shape de l'objet:")
print(f"  Cellules: {adata.n_obs}")
print(f"  Gènes: {adata.n_vars}")
print()

print("Colonnes disponibles dans obs:")
for col in adata.obs.columns:
    print(f"  - {col}")
print()

print("Head des métadonnées des cellules:")
print(adata.obs.head())
print()

print("Types de données des colonnes obs:")
print(adata.obs.dtypes)
print()

print("=== MÉTHODES D'ANALYSE POSSIBLES ===")
print()

print("1. QUALITY CONTROL:")
print("   - sc.pp.calculate_qc_metrics() - Calculer métriques QC")
print("   - sc.pl.violin() - Visualiser distributions QC")
print("   - sc.pp.highly_variable_genes() - Identifier gènes variables")
print()

print("2. NORMALISATION:")
print("   - sc.pp.normalize_total() - Normalisation par cellule")
print("   - sc.pp.log1p() - Transformation log")
print("   - sc.pp.scale() - Standardisation")
print()

print("3. DIMENSIONNALITÉ:")
print("   - sc.pp.pca() - Analyse en composantes principales")
print("   - sc.pp.neighbors() - Calcul des voisins")
print("   - sc.tl.umap() - Réduction dimensionnelle UMAP")
print()

print("4. CLUSTERING:")
print("   - sc.tl.leiden() - Clustering Leiden")
print("   - sc.tl.louvain() - Clustering Louvain")
print("   - sc.pl.umap() - Visualisation clusters")
print()

print("5. MARKERS:")
print("   - sc.tl.rank_genes_groups() - Gènes marqueurs")
print("   - sc.pl.rank_genes_groups() - Visualisation marqueurs")
print()

print("6. TRAJECTORIES:")
print("   - sc.tl.dpt() - Diffusion pseudotime")
print("   - sc.tl.paga() - Analyse de graphe partitionné")
print()

print("=== EXEMPLE DE PIPELINE COMPLET ===")
print()
print("sc.pp.calculate_qc_metrics(adata)")
print("sc.pp.normalize_total(adata)")
print("sc.pp.log1p(adata)")
print("sc.pp.highly_variable_genes(adata)")
print("sc.pp.pca(adata)")
print("sc.pp.neighbors(adata)")
print("sc.tl.umap(adata)")
print("sc.tl.leiden(adata)")
print("sc.tl.rank_genes_groups(adata)")
