import pandas as pd

def extract_gene_features(file_path):
    """
    Extrait les lignes de features différentes de 'gene' 
    avec le seq_type 'chromosome' et les colonnes spécifiées.
    
    Parameters:
    file_path (str): Chemin vers le fichier texte

    Returns:
    pandas.DataFrame: DataFrame avec les colonnes demandées
    """
    # Lire manuellement l'en-tête
    with open(file_path, 'r') as file:
        # Trouver la première ligne qui ne commence pas par '#'
        header_line = ''
        for line in file:
            if line.startswith('#'):
                # Enlever le '#' et les espaces
                possible_header = line.lstrip('#').strip()
                if possible_header:  # S'assurer que la ligne n'est pas vide
                    header_line = possible_header
            else:
                break
    
    # Vérifier si un en-tête valide a été trouvé
    if not header_line:
        print("Erreur : Impossible de trouver l'en-tête du fichier")
        return None
    
    # Lire le fichier avec l'en-tête correct
    try:
        # Utiliser l'en-tête trouvé et ignorer les lignes de commentaire
        df = pd.read_csv(file_path, sep='\t', comment='#', 
                         names=header_line.split('\t'), 
                         dtype=str, 
                         header=None)
        
        # Filtrer les lignes selon les critères
        filtered_df = df[
            (df['feature'] != 'gene') #& 
         #   (df['seq_type'] == 'chromosome')
        ]
        
        # Sélectionner uniquement les colonnes demandées
        result_df = filtered_df[['seq_type','feature','class', 'product_accession', 'name', 'symbol', 'locus_tag']]
        
        return result_df
    
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier : {e}")
        return None

# Exemple d'utilisation
file_path = 'genome_ref/GCA_030064105.1_ASM3006410v1_feature_table.txt'
resultat = extract_gene_features(file_path)

if resultat is not None:
    # Sauvegarder le résultat dans un nouveau fichier
    output_file = 'genome_ref/extracted_features.tsv'
    resultat.to_csv(output_file, sep='\t', index=False)
    print(f"✅ Résultat sauvegardé dans : {output_file}")
    print(f"Nombre de lignes extraites : {len(resultat)}")
else:
    print("❌ Extraction échouée.")