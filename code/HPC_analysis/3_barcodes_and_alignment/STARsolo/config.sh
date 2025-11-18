#!/bin/bash

# === Global Configuration for STARsolo Pipeline ===

# Here you can change the name of the analysis, the location of the folder for the Analysis, the number of threads, the memory, the maximum runtime, the location of the conda environment, the source data locations, the source file names, the target file names...



# Email Configuration
EMAIL="goupille.valentin@live.fr"

# Define the base path for all directories
BASE_PATH="/projects/microsplit/Internship_Val_Goupille_2025"  # Base path for the project
BASE_BIG_DATA="/projects/microsplit/big_data"

# Analysis Name and Base Directory (Fixed for merged data analysis)
ANALYSIS_NAME="STARsolo_microSPLIT_merged" # Fixed name for merged analysis
BASE_DIR="${BASE_PATH}/data/STARsolo_result/merged_trimmed/merged" # Fixed directory for merged analysis

# Resource Configuration
THREADS=64 # For the number of threads (cpus-per-task)
MEMORY="600G" # Memory allocation for merged data analysis (increased for large datasets)

MAX_RUNTIME="10-00:00:00" # For the maximum runtime: You can change it

# Conda Configuration
CONDA_INIT_SCRIPT="${BASE_PATH}/code/HPC_analysis/3_barcodes_and_alignment/STARsolo/create_env_STARsolo.sh" # Path to the conda initialization script
CONDA_ENV_PATH="${BASE_PATH}/env/STARsolo_microSPLIT_DOL" # For the location of the conda environment

# Source Data Locations - Absolute paths to prevent errors
SOURCE_FASTQ="${BASE_BIG_DATA}/merged_data"  # Chemin vers les données trimmed

# for barcodes, genome_ref and genome_annotation here we use the file avaible in the repository (barcodes_result folder) :::::
SOURCE_BARCODES="${BASE_PATH}/projects/microsplit/data/barcodes_result/barcodeSTARsolo/filtered"  # Chemin vers les barcodes filtrés

# Source barcode file names
SOURCE_BARCODE_R1="barcode_rd1_filtered.txt"  # Nom du fichier de barcodes round 1
SOURCE_BARCODE_R2="barcode_rd2_filtered.txt"  # Nom du fichier de barcodes round 2
SOURCE_BARCODE_R3="barcode_rd3_filtered.txt"  # Nom du fichier de barcodes round 3

# Target barcode file names (noms attendus par STARsolo)
TARGET_BARCODE_R1="barcode_round1.txt"  # Nom cible pour STARsolo round 1
TARGET_BARCODE_R2="barcode_round2.txt"  # Nom cible pour STARsolo round 2
TARGET_BARCODE_R3="barcode_round3.txt"  # Nom cible pour STARsolo round 3

SOURCE_GENOME_REF="${BASE_PATH}/data/genome_ref"
SOURCE_GENOME_ANNOTATION="${BASE_PATH}/data/genome_annotation"





#---------------------------------------------------------------------------

# === FASTQ FILES (fixed names for merged data) ===
SOURCE_FASTQ_R1="merged_trimmed-R1.fastq.gz" # Merged trimmed R1 file
SOURCE_FASTQ_R2="merged_trimmed-R2.fastq.gz" # Merged trimmed R2 file

# === GENOME FILES (fixed names) ===
SOURCE_GENOME_FASTA="GCA_030064105.1_ASM3006410v1_genomic.fna" # change it if you use another genome (new versions)
SOURCE_GENOME_GFF="GCA_030064105.1_ASM3006410v1_genomic.gff" # change it if you use another genome (new versions)

# === TARGET FILES (symbolic link names) ===
TARGET_FASTQ_R1="merged_trimmed-R1.fastq.gz" # Target name for merged R1
TARGET_FASTQ_R2="merged_trimmed-R2.fastq.gz" # Target name for merged R2
TARGET_GENOME_FASTA="genome_ref_PsR401.fna"
TARGET_GENOME_GFF="genome_annotation_PsR401.gff"

# Path Structure - Don't change these unless necessary
DATA_DIR="${BASE_DIR}/raw_data"
FASTQ_DIR="${DATA_DIR}/fastq"
BARCODE_DIR="${DATA_DIR}/barcodes"
GENOME_REF_DIR="${DATA_DIR}/genome_ref"
GENOME_ANNOTATION_DIR="${DATA_DIR}/genome_annotation"
GENERAL_OUTPUT_DIR="${BASE_DIR}/Output_DOL_microsplit_starsolo"
GENOME_DIR="${GENERAL_OUTPUT_DIR}/genome_index"
OUTPUT_STARSOLO_DIR="${GENERAL_OUTPUT_DIR}/starsolo_output" 