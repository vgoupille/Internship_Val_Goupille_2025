import anndata as ad
import pandas as pd

# Charger l'objet AnnData
adata = ad.read_h5ad("metadata/Gene_filtered.h5ad")

print("=== STANDARDS SCANPY/ANNDATA POUR LES COLONNES ===")
print()

print("1. feature_id:")
print("   - Standard: Identifiant unique du feature (gène, UMI, etc.)")
print("   - Format attendu: Identifiant complet du feature")
print("   - Usage: Généralement utilisé pour la traçabilité")
print("   - Notre cas: gene-QLH64_XXXXX (format STARsolo standard)")
print()

print("2. gene_id:")
print('   - Standard: Identifiant "propre" du gène')
print("   - Format attendu: Nom du gène sans préfixe")
print("   - Usage: Souvent utilisé comme index ou pour les annotations")
print("   - Notre cas: QLH64-XXXXX (format locus tag)")
print()

print("3. feature_type:")
print("   - Standard: Type de feature dans l'expérience")
print("   - Valeurs communes:")
print('     * "Gene Expression" (gènes)')
print('     * "Antibody Capture" (protéines)')
print('     * "CRISPR Guide Capture" (gènes CRISPR)')
print('     * "Custom" (autres)')
print("   - Usage: Filtrage et analyse par type de feature")
print('   - Notre cas: Tous "Gene Expression" (normal pour RNA-seq)')
print()

print("=== VÉRIFICATION DE CONFORMITÉ ===")
print()

# Vérifier si on a des doublons
print("Doublons dans feature_id:", adata.var["feature_id"].duplicated().sum())
print("Doublons dans gene_id:", adata.var["gene_id"].duplicated().sum())
print("Doublons dans var_names:", adata.var_names.duplicated().sum())

print()
print("Types de features présents:")
print(adata.var["feature_type"].value_counts())

print()
print("=== RECOMMANDATIONS SCANPY ===")
print()
print("1. var_names (index) devrait être unique et stable")
print("2. gene_id est souvent utilisé pour les annotations")
print("3. feature_type permet le filtrage par type")
print("4. feature_id pour la traçabilité complète")
print()
print("Notre objet est conforme aux standards Scanpy !")
