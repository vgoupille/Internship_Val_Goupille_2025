import pandas as pd

# # Charger les fichiers
# df1 = pd.read_csv("genome_ref/other/annotation_2023.tsv", sep="\t")
# df2 = pd.read_csv("genome_ref/other/annotation_2024.tsv", sep="\t")

# # Comparer les fichiers en utilisant la colonne "Locus tag"
# locus_diff = pd.merge(df1[['Locus tag']], df2[['Locus tag']], on='Locus tag', how='outer', indicator=True)

# # Sauvegarde des différences
# locus_diff.to_csv("differences_locus_tag.tsv", sep="\t", index=False)
# print(locus_diff)



import pandas as pd
import pandas as pd

# Charger les fichiers
df1 = pd.read_csv("genome_ref/other/annotation_2023.tsv", sep="\t")
df2 = pd.read_csv("genome_ref/other/annotation_2024.tsv", sep="\t")

# Ajouter une colonne pour gérer les correspondances avec RS
df1['Normalized Locus tag'] = df1['Locus tag'].str.replace('_', '_RS', regex=False)
df2['Normalized Locus tag'] = df2['Locus tag']

# Extraire les colonnes "Normalized Locus tag"
locus_2023 = set(df1['Normalized Locus tag'])
locus_2024 = set(df2['Normalized Locus tag'])

# Identifier les identifiants uniques à chaque fichier
unique_to_2023 = locus_2023 - locus_2024
unique_to_2024 = locus_2024 - locus_2023

# Sauvegarder les résultats dans des fichiers
with open("unique_to_2023_normalized.txt", "w") as f:
    f.write("\n".join(unique_to_2023))

with open("unique_to_2024_normalized.txt", "w") as f:
    f.write("\n".join(unique_to_2024))

# Afficher les résultats
print(f"Identifiants uniques à 2023 après normalisation : {len(unique_to_2023)}")
print(f"Identifiants uniques à 2024 après normalisation : {len(unique_to_2024)}")

import pandas as pd
import json

# Charger les fichiers
df1 = pd.read_csv("genome_ref/other/annotation_2023.tsv", sep="\t")
df2 = pd.read_csv("genome_ref/other/annotation_2024.tsv", sep="\t")

# Ajouter une colonne pour gérer les correspondances avec RS
df1['Normalized Locus tag'] = df1['Locus tag'].str.replace('_', '_RS', regex=False)
df2['Normalized Locus tag'] = df2['Locus tag']

# Effectuer une jointure externe sur "Normalized Locus tag"
merged = pd.merge(
    df1,
    df2,
    on='Normalized Locus tag',
    how='outer',
    suffixes=('_2023', '_2024'),
    indicator=True
)

# Identifier les colonnes à comparer (ignorer "Locus tag" et "Normalized Locus tag")
columns_to_compare = [col for col in df1.columns if col not in ['Locus tag', 'Normalized Locus tag']]

# Créer une matrice pour stocker les différences
difference_matrix = []
column_diff_stats = {col: 0 for col in columns_to_compare}  # Initialiser les stats des colonnes

# Parcourir chaque ligne et comparer les colonnes
for index, row in merged.iterrows():
    row_differences = {}
    for col in columns_to_compare:
        col_2023 = f"{col}_2023"
        col_2024 = f"{col}_2024"
        if col_2023 in merged.columns and col_2024 in merged.columns:
            if row[col_2023] != row[col_2024]:
                row_differences[col] = True  # Différence détectée
                column_diff_stats[col] += 1  # Incrémenter le compteur pour cette colonne
            else:
                row_differences[col] = False  # Pas de différence
    difference_matrix.append({'Normalized Locus tag': row['Normalized Locus tag'], 'Differences': row_differences})

# Sauvegarder les différences dans un fichier JSON pour une analyse détaillée
with open("detailed_differences.json", "w") as f:
    json.dump(difference_matrix, f, indent=4)

# Sauvegarder les statistiques des colonnes dans un fichier
with open("column_diff_stats.json", "w") as f:
    json.dump(column_diff_stats, f, indent=4)

# Afficher un résumé des différences
print(f"Nombre de lignes uniquement dans 2023 : {len(merged[merged['_merge'] == 'left_only'])}")
print(f"Nombre de lignes uniquement dans 2024 : {len(merged[merged['_merge'] == 'right_only'])}")
print(f"Nombre de lignes avec des différences : {len([row for row in difference_matrix if any(row['Differences'].values())])}")

# Afficher les statistiques des colonnes
print("Statistiques des différences par colonne :")
for col, count in column_diff_stats.items():
    print(f"- {col} : {count} différences")