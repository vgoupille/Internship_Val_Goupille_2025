# Script starsolo_to_anndata.py

## Description
Ce script Python convertit les fichiers de sortie STARsolo en objets AnnData. Il crée **6 objets AnnData différents** basés sur les différents types de données disponibles.

## Objets AnnData créés

### Données Gene (niveau gène)
1. **Gene_raw_matrix.h5ad** : Matrice brute au niveau gène
2. **Gene_raw_unique_mult.h5ad** : Matrice UniqueAndMult-Uniform brute (avec conversion float→int)
3. **Gene_filtered.h5ad** : Matrice filtrée au niveau gène

### Données GeneFull (niveau transcrit complet)
4. **GeneFull_raw_matrix.h5ad** : Matrice brute au niveau transcrit complet
5. **GeneFull_raw_unique_mult.h5ad** : Matrice UniqueAndMult-Uniform brute (avec conversion float→int)
6. **GeneFull_filtered.h5ad** : Matrice filtrée au niveau transcrit complet

## Fonctionnalités

### Modification des features
- **Modification en mémoire** : Les fichiers features.tsv ne sont pas modifiés physiquement
- **Transformation de la colonne 2** : Suppression du préfixe `gene-` et remplacement des underscores par des tirets
- **Exemple** : `gene-QLH64_00005` → `QLH64-00005`

### Gestion des matrices UniqueAndMult-Uniform
- **Détection automatique** : Reconnaissance des matrices au format float
- **Conversion** : Arrondi des valeurs décimales vers des entiers
- **Exemple** : `0.8` → `1`, `1.4` → `1`

### Structure des objets AnnData
- **X** : Matrice de comptage (sparse)
- **obs** : Barcodes cellulaires
- **var** : Features/gènes avec colonnes modifiées
- **uns** : Métadonnées (type de matrice, source, nom)

## Utilisation

### Exécution simple
```bash
python starsolo_to_anndata.py
```

### Structure des fichiers d'entrée attendue
```
data/Solo.out/
├── Gene/
│   ├── raw/
│   │   ├── matrix.mtx
│   │   ├── UniqueAndMult-Uniform.mtx
│   │   ├── barcodes.tsv
│   │   └── features.tsv
│   └── filtered/
│       ├── matrix.mtx
│       ├── barcodes.tsv
│       └── features.tsv
└── GeneFull/
    ├── raw/
    │   ├── matrix.mtx
    │   ├── UniqueAndMult-Uniform.mtx
    │   ├── barcodes.tsv
    │   └── features.tsv
    └── filtered/
        ├── matrix.mtx
        ├── barcodes.tsv
        └── features.tsv
```

### Fichiers de sortie
```
anndata_objects/
├── Gene_raw_matrix.h5ad
├── Gene_raw_unique_mult.h5ad
├── Gene_filtered.h5ad
├── GeneFull_raw_matrix.h5ad
├── GeneFull_raw_unique_mult.h5ad
└── GeneFull_filtered.h5ad
```

## Dépendances
- Python 3.x
- pandas
- numpy
- scipy
- anndata

## Exemple de sortie
```
Creating Gene_raw_matrix...
  Shape: (6248, 820800)
  Non-zero entries: 22721911
  Saved to: anndata_objects/Gene_raw_matrix.h5ad

Creating Gene_raw_unique_mult...
  Converting float matrix to integers (rounding)...
  Shape: (6248, 820800)
  Non-zero entries: 30106129
  Saved to: anndata_objects/Gene_raw_unique_mult.h5ad

...

Conversion completed!
AnnData objects saved in: anndata_objects/
```

## Notes importantes
- Les fichiers originaux STARsolo ne sont **PAS modifiés**
- Les modifications des features sont faites **en mémoire uniquement**
- Les matrices UniqueAndMult-Uniform sont **automatiquement converties** en entiers
- Le script gère les **erreurs** et continue même si certains fichiers sont manquants
- Les objets AnnData sont **optimisés** avec des matrices sparse CSR 