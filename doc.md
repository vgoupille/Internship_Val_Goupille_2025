
- compréhension du probleme : 
    - probleme de chemin d'acces sur le cluster 
    - j'ai mal expliqué la structure des données data
    - Solène souhaite relancer l'analyse sur sur le cluster (HPC) dont les codes sont dispo ici :
    /projects/microsplit/Internship_Val_Goupille_2025/code/HPC_analysis
    - focus sur l'analyse starsolo pour commencer 

- test de resolution : 
- j'ai clone sur le cluster mon repo git Internship_Val_Goupille_2025 : 
/projects/microsplit/Internship_Val_Goupille_2025

- j'ai renommer /projects/microsplit/data  en /projects/microsplit/Important_data
 - ce fichier contient les données lourdes (fastq et autres données issues de l'analyse sur HPC durant mon stage, ces données ne sont pas présentes sur mon repo git) 
 - ne pas le confondre avec /projects/microsplit/Internship_Val_Goupille_2025/data qui est le dossier qui contient les infos data utiles pour lancer les scripts


- ce deplacer ici : Internship_Val_Goupille_2025/code/HPC_analysis/3_barcodes_and_alignment/STARsolo/create_env_STARsolo.sh

avec la commande cd Internship_Val_Goupille_2025/code/HPC_analysis/3_barcodes_and_alignment/STARsolo/

puis 

```bash
sbatch create_env_STARsolo.sh
```

il y a avait effectivement une erreur de chemin pour le yml de l'env, le chemin correct est : /code/HPC_analysis/3_barcodes_and_alignment/STARsolo/environment_STARsolo.yml"
 j'ai corrigé l'erreur


cela me creer bien le script l'env conda : /projects/microsplit/Internship_Val_Goupille_2025/env/STARsolo_microSPLIT_DOL