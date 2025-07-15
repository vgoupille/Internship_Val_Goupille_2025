import anndata as ad

# Charger l'objet AnnData
adata = ad.read_h5ad("metadata/Gene_filtered.h5ad")

print("=== CONTENU DES COLONNES ORIGINALES ===")

print("\n=== feature_id (premiers 10) ===")
print(adata.var["feature_id"].head(10).tolist())

print("\n=== gene_id (premiers 10) ===")
print(adata.var["gene_id"].head(10).tolist())

print("\n=== feature_type (tous les types) ===")
print(adata.var["feature_type"].value_counts())

print("\n=== Comparaison feature_id vs gene_id (premiers 5) ===")
for i in range(5):
    print(f'{adata.var["feature_id"].iloc[i]} -> {adata.var["gene_id"].iloc[i]}')

print("\n=== Exemples détaillés (premiers 5 gènes) ===")
for i in range(5):
    print(f"Gène {i+1}:")
    print(f'  feature_id: {adata.var["feature_id"].iloc[i]}')
    print(f'  gene_id: {adata.var["gene_id"].iloc[i]}')
    print(f'  feature_type: {adata.var["feature_type"].iloc[i]}')
    print(f"  var_names (index): {adata.var_names[i]}")
    print()
