
- compréhension du probleme : 
    - erreurs dans les chemins d'acces sur le cluster 
    - j'ai mal expliqué la structure des données 
    - Solène souhaite relancer l'analyse sur sur le cluster (HPC)
    
- solution : 
    - j'ai cloné sur le cluster mon repo git Internship_Val_Goupille_2025 : 
/projects/microsplit/Internship_Val_Goupille_2025
    - j'ai renommer /projects/microsplit/data  en /projects/microsplit/big_data
        - ce dossier contient les données lourdes (fastq et autres données issues de l'analyse sur HPC durant mon stage, ces données ne sont pas présentes sur mon repo git) 
    - ne pas le confondre avec /projects/microsplit/Internship_Val_Goupille_2025/data qui est le dossier qui contient les autres data utiles pour lancer les scripts mais peu lourdes commes le genome, annotations, barcodes... (données au sein du repo : Internship_Val_Goupille_2025)

    - Si tu souhaites relancer les analyses HPC : 
        - les codes sont dispo ici :
    /projects/microsplit/Internship_Val_Goupille_2025/code/HPC_analysis
            - focus sur l'analyse STARsolo pour commencer :
                - se placer dans le répertoire :
```bash
cd Internship_Val_Goupille_2025/code/HPC_analysis/3_barcodes_and_alignment/STARsolo/ 
```
                - exécution :
            
```bash
sbatch create_env_STARsolo.sh
```

                - remarques :
                    - le script crée l'environnement conda : /projects/microsplit/Internship_Val_Goupille_2025/env/STARsolo_microSPLIT_DOL
                    - vérifier que le dépôt est cloné sur le cluster sous /projects/microsplit/Internship_Val_Goupille_2025 avant d'exécuter


J'ai ensuite corrigé le fichier de config et submit qui contenait des erreurs de lien ( cela va chercher les fichiers fastq trimmmé et mergé dans le dossier : "/projects/microsplit/big_data")

puis lancer l'analyse starsolo avec : 

```bash
sbatch submit_pipeline.sh
```


les logs vont dans : /projects/microsplit/logs
et les resultats dans : /projects/microsplit/Internship_Val_Goupille_2025/data/STARsolo_result/merged_trimmed/merged/Output_DOL_microsplit_starsolo