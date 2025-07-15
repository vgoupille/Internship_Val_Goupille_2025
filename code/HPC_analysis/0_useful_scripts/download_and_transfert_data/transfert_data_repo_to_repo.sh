#!/bin/bash
#SBATCH --job-name=transfert_data_repo_to_repo
#SBATCH --output=transfert_data_repo_to_repo_%j.log
#SBATCH --error=transfert_data_repo_to_repo_%j.err
#SBATCH --time=24:00:00
#SBATCH --mem=4G


#scp -r /projects/ecogeno/DEV/2025_GoupilleValentin/data/processed_data/unzipped_data/* /projects/microsplit/data/raw_data/unzipped_data/



#scp -r /projects/ecogeno/DEV/2025_GoupilleValentin/data/processed_data/merged_fastq/* /projects/microsplit/data/raw_data/merged_fastq/

#scp -r /projects/ecogeno/DEV/2025_GoupilleValentin/data/processed_data/subsampled_data/* /projects/microsplit/data/raw_data/subsampled_data/


#Importation des fichiers de trim_final dans le repo de microsplit qui correspond des fichiers trimmés 
scp -r /projects/ecogeno/DEV/2025_GoupilleValentin/data/processed_data/Trim_final/6_fastp_final/* /projects/microsplit/data/processed_data/Trim_result_29_05_25


scp -r /projects/ecogeno/DEV/2025_GoupilleValentin/data/processed_data/Trim_final2/6_fastp_final/* /projects/microsplit/data/processed_data/Trim_result_29_05_25


scp -r /projects/ecogeno/DEV/2025_GoupilleValentin/data/processed_data/Trim_final3/6_fastp_final/* /projects/microsplit/data/processed_data/Trim_result_29_05_25


scp -r /projects/ecogeno/DEV/2025_GoupilleValentin/data/processed_data/Trim_final4/6_fastp_final/* /projects/microsplit/data/processed_data/Trim_result_29_05_25