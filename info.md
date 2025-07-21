# Organisation des données du projet

## Structure des dossiers de données

### `Anndata/`
Contient les fichiers AnnData formatés pour l'analyse avec Scanpy, organisés selon les différentes étapes de traitement.

### `barcodes_result/`
Regroupe les barcodes nécessaires pour l'analyse STARsolo ainsi que les métadonnées complètes du projet.

### `genome_annotation/`
Contient le fichier d'annotation génomique de la souche de Cologne utilisée comme référence.

### `genome_ref/`
Stocke la séquence de référence du génome de la souche de Cologne.

### `info/`
Comprend les informations sur la structure des données de séquençage :
- `experiment/` : résume les informations sur l'expérience
- `samples/` : contient les liens absolus vers les fichiers FASTQ

### `meta/`
Contient les fichiers Excel originaux avec les métadonnées :
- Utiles pour construire les barcodes STARsolo et assigner les métadonnées
- `plan_exp.xlsx` est particulièrement utile pour ajouter les timepoints

### `multiqc/`
Résultats des analyses MultiQC à différentes étapes :
- Avant trimming
- Après trimming  
- Données fusionnées après trimming
- Inclut également les résultats FastQC

### `RDS/`
Contient les fichiers au format RDS pour les analyses dans R.

### `STARsolo_result/`
Contient les outputs de STARsolo (sans les fichiers BAM de ~250 Go qui restent disponibles sur le cluster).