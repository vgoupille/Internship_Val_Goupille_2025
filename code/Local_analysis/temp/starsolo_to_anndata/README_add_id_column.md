# Script add_id_column.py

## Description
Ce script Python traite le fichier `ncbi_dataset.tsv` en :
1. **Gérant les doublons** dans la colonne Symbol (ajout de suffixes _1, _2, etc.)
2. **Modifiant les locus_tags** (remplacement des underscores par des tirets)
3. **Créant une colonne final_gene_name** qui utilise Symbol si disponible, sinon Locus tag

## Fonctionnalités principales

### Gestion des doublons
- Détecte automatiquement les symboles en double
- Renomme les doublons avec des suffixes (_1, _2, _3, etc.)
- Exemple : `rrf` devient `rrf_1`, `rrf_2`, etc.

### Modification des locus_tags
- Remplace tous les underscores (_) par des tirets (-)
- Exemple : `QLH64_00005` devient `QLH64-00005`

### Colonnes créées (optimisées)
- **final_gene_name** : Utilise Symbol si disponible, sinon Locus tag (identifiant unique)
- **symbol_old** : Copie des symboles originaux
- **locus_tag_old** : Copie des locus_tags originaux
- **symbol_renamed** : Indique si le symbole a été renommé

## Utilisation

### Exécution simple
```bash
python add_id_column.py
```

### Fonctionnement détaillé
1. Le script lit le fichier `data/ncbi_dataset.tsv`
2. Il vérifie la présence des colonnes requises
3. Il traite les doublons dans la colonne Symbol
4. Il modifie les locus_tags (remplace _ par -)
5. Il crée les nouvelles colonnes optimisées
6. Il sauvegarde le résultat dans `data/ncbi_dataset_with_id.tsv`
7. Il affiche des statistiques détaillées

### Sortie
- **Fichier de sortie** : `data/ncbi_dataset_with_id.tsv`
- **Format** : TSV (Tab-Separated Values)
- **Colonnes** : Toutes les colonnes originales + colonnes optimisées

### Statistiques affichées
Le script affiche :
- Nombre total d'entrées
- Nombre de symboles en double trouvés
- Nombre de symboles renommés
- Vérification des doublons dans final_gene_name
- Liste des colonnes conservées

## Exemple de sortie
```
Reading input file: data/ncbi_dataset.tsv
Processing duplicate symbols and creating optimized columns...
Modified locus_tag: replaced underscores with hyphens
Found 101 duplicate symbols
Renamed 6 instances of 'rrf'
Renamed 6 instances of 'ltrA'
...

Statistics:
  - Total entries: 6249
  - Total symbols renamed: 5165
  - Duplicates in final_gene_name: 0

Colonnes conservées (19):
  - Accession
  - Begin
  - End
  - Chromosome
  - Orientation
  - Name
  - Symbol
  - Gene ID
  - Gene Type
  - Transcripts accession
  - Transcript name
  - Protein accession
  - Protein name
  - Protein length
  - Locus tag
  - symbol_old
  - locus_tag_old
  - symbol_renamed
  - final_gene_name

Saving optimized output file: data/ncbi_dataset_with_id.tsv
Done!
```

## Résultats de l'analyse
- **6249 entrées** traitées avec succès
- **101 symboles en double** détectés et renommés
- **5165 symboles renommés** au total
- **0 doublon** dans final_gene_name (garantie d'unicité)
- **19 colonnes** optimisées (sans redondance)

## Dépendances
- Python 3.x
- pandas

## Structure des fichiers
```
code/starsolo_to_anndata/
├── add_id_column.py                    # Script principal (version optimisée)
├── README_add_id_column.md            # Cette documentation
└── data/
    ├── ncbi_dataset.tsv               # Fichier d'entrée
    └── ncbi_dataset_with_id.tsv       # Fichier de sortie optimisé
```

## Notes importantes
- Le script préserve toutes les colonnes originales
- Les doublons sont automatiquement gérés pour garantir l'unicité
- La colonne `final_gene_name` peut être utilisée comme identifiant unique
- Les locus_tags sont modifiés pour remplacer _ par -
- Toutes les modifications sont tracées dans les colonnes *_old 