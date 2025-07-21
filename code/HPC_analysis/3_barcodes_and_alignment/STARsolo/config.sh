#!/bin/bash

# === Global Configuration for STARsolo Pipeline ===

# Here you can change the name of the analysis, the location of the folder for the Analysis, the number of threads, the memory, the maximum runtime, the location of the conda environment, the source data locations, the source file names, the target file names...

# Go to the folder where you want to run the analysis:
# For example: 
    # cd 1_data/test/starsolo_script_DOL_microSPLIT/
    # Then you can run the analysis with the following command:
    # sbatch run_pipeline.sh


# Email Configuration
EMAIL="valentin.goupille@univ-rennes.fr"

# Define the base path for all directories
BASE_PATH="/projects/microsplit"  # Base path for the project

# IMPORTANT: Make sure this path exists before running the pipeline
# You can check it using: [ -d "$BASE_PATH" ] && echo "Path exists" || echo "Path DOES NOT exist"
# If it doesn't exist, the pipeline will fail when trying to create the conda environment

# Analysis Name and Base Directory (Fixed for merged data analysis)
ANALYSIS_NAME="STARsolo_microSPLIT_merged" # Fixed name for merged analysis
BASE_DIR="${BASE_PATH}/data/STARsolo_result/merged_trimmed/merged" # Fixed directory for merged analysis

# Resource Configuration
THREADS=64 # For the number of threads (cpus-per-task): You can change it # VERY IMPORTANT: YOU NEED TO HAVE ENOUGH THREADS TO RUN THE ANALYSIS: 16 MAY NOT BE ENOUGH FOR THE ANALYSIS =======> test with 32 or 64 is probably better

MEMORY="600G" # Memory allocation for merged data analysis (increased for large datasets)

MAX_RUNTIME="10-00:00:00" # For the maximum runtime: You can change it

# Conda Configuration
CONDA_INIT_SCRIPT="/local/env/envconda.sh" # Path to the conda initialization script
CONDA_ENV_PATH="${BASE_PATH}/env/STARsolo_microSPLIT_DOL" # For the location of the conda environment

# Source Data Locations - Absolute paths to prevent errors
SOURCE_FASTQ="${BASE_PATH}/data/merged_data"  # Chemin vers les données trimmed

# for barcodes, genome_ref and genome_annotation here we use the file avaible in the repository (barcodes_result folder) :::::
SOURCE_BARCODES="${BASE_PATH}/data/barcodes_result/barcodeSTARsolo/filtered"  # Chemin vers les barcodes filtrés

# Source barcode file names
SOURCE_BARCODE_R1="barcode_rd1_filtered.txt"  # Nom du fichier de barcodes round 1
SOURCE_BARCODE_R2="barcode_rd2_filtered.txt"  # Nom du fichier de barcodes round 2
SOURCE_BARCODE_R3="barcode_rd3_filtered.txt"  # Nom du fichier de barcodes round 3

# Target barcode file names (noms attendus par STARsolo)
TARGET_BARCODE_R1="barcode_round1.txt"  # Nom cible pour STARsolo round 1
TARGET_BARCODE_R2="barcode_round2.txt"  # Nom cible pour STARsolo round 2
TARGET_BARCODE_R3="barcode_round3.txt"  # Nom cible pour STARsolo round 3

SOURCE_GENOME_REF="${BASE_PATH}/data/raw_data/genome_ref"
SOURCE_GENOME_ANNOTATION="${BASE_PATH}/data/raw_data/genome_annotation"





#---------------------------------------------------------------------------

# === FASTQ FILES (fixed names for merged data) ===
SOURCE_FASTQ_R1="merged_trimmed-R1.fastq.gz" # Merged trimmed R1 file
SOURCE_FASTQ_R2="merged_trimmed-R2.fastq.gz" # Merged trimmed R2 file

# === GENOME FILES (fixed names) ===
SOURCE_GENOME_FASTA="GCA_030064105.1_ASM3006410v1_genomic.fna"
SOURCE_GENOME_GFF="GCA_030064105.1_ASM3006410v1_genomic.gff"

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
GENERAL_OUTPUT_DIR="${BASE_DIR}/Output_DOL_microsplit_starsolo2"
GENOME_DIR="${GENERAL_OUTPUT_DIR}/genome_index"
OUTPUT_STARSOLO_DIR="${GENERAL_OUTPUT_DIR}/starsolo_output2" 