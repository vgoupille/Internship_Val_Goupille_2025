#!/bin/bash

# Script to decompress R1 and R2 fastq.gz files
# Usage: 
#   ./decompress_fastq.sh [-f] <directory_path>     # Décompresse tous les fichiers R1 et R2 du répertoire
#   ./decompress_fastq.sh [-f] <fichier1.fastq.gz> [fichier2.fastq.gz] ...  # Décompresse les fichiers spécifiés
#
# Options:
#   -f: Remove original compressed files after decompression

# Initialize variables
REMOVE_ORIGINAL=false
FILES=()
IS_DIRECTORY=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -f) REMOVE_ORIGINAL=true; shift ;;
        *) FILES+=("$1"); shift ;;
    esac
done

# Check if files are provided
if [ ${#FILES[@]} -eq 0 ]; then
    echo "Veuillez fournir le chemin du répertoire ou des fichiers fastq.gz"
    echo "Usage: "
    echo "  ./decompress_fastq.sh [-f] <directory_path>     # Décompresse tous les fichiers R1 et R2 du répertoire"
    echo "  ./decompress_fastq.sh [-f] <fichier1.fastq.gz> [fichier2.fastq.gz] ...  # Décompresse les fichiers spécifiés"
    echo "Options:"
    echo "  -f: Supprimer les fichiers compressés originaux après décompression"
    exit 1
fi

# Initialize counter
COUNT=0

# Check if the first argument is a directory
if [ -d "${FILES[0]}" ]; then
    IS_DIRECTORY=true
    DIR_PATH=${FILES[0]}
    
    # Check if directory exists (redundant but kept for clarity)
    if [ ! -d "$DIR_PATH" ]; then
        echo "Le répertoire $DIR_PATH n'existe pas"
        exit 1
    fi
    
    # Find and decompress all R1 and R2 fastq.gz files
    echo "Recherche des fichiers R1 et R2 dans $DIR_PATH"
    
    for file in $(find "$DIR_PATH" -name "*R1*.fastq.gz" -o -name "*R2*.fastq.gz"); do
        echo "Décompression de $file"
        if [ "$REMOVE_ORIGINAL" = true ]; then
            gunzip "$file"  # Remove original
            echo "  Fichier original supprimé"
        else
            gunzip -k "$file"  # Keep original
        fi
        ((COUNT++))
    done
else
    # Process individual files
    for file in "${FILES[@]}"; do
        if [ ! -f "$file" ]; then
            echo "Le fichier $file n'existe pas ou n'est pas un fichier régulier"
            continue
        fi
        
        if [[ "$file" != *.fastq.gz ]]; then
            echo "Le fichier $file n'est pas un fichier fastq.gz"
            continue
        fi
        
        echo "Décompression de $file"
        if [ "$REMOVE_ORIGINAL" = true ]; then
            gunzip "$file"  # Remove original
            echo "  Fichier original supprimé"
        else
            gunzip -k "$file"  # Keep original
        fi
        ((COUNT++))
    done
fi

echo "Terminé! $COUNT fichiers ont été décompressés."
if [ "$REMOVE_ORIGINAL" = false ]; then
    echo "Les fichiers originaux .gz ont été conservés."
    echo "Pour les supprimer, relancez le script avec l'option -f."
fi 