#!/bin/bash
#SBATCH --job-name=starsolo_wrapper
#SBATCH --output=/projects/microsplit/logs/starsolo_wrapper_%j.out
#SBATCH --error=/projects/microsplit/logs/starsolo_wrapper_%j.err
#SBATCH --time=10:00:00
#SBATCH --mem=2G
#SBATCH --cpus-per-task=2

# === Script to run STARsolo pipeline for all samples ===
# This script reads samples_all.yaml and runs the pipeline for each sample

# Define paths
SCRIPT_DIR="/projects/microsplit/scripts/4_barcodes_and_alignment/STARsolo/STARsolo_microSPLIT_DOL/script/pipeline"  # Chemin absolu complet
BASE_PATH="/projects/microsplit"  # Use absolute path
SAMPLES_YAML="${BASE_PATH}/data/info/samples/samples_trimming.yaml"
INPUT_TYPE="merged_trimmed"  # Type of input data to use
CONDA_ENV_PATH="${BASE_PATH}/env/STARsolo_microSPLIT_DOL"  # Chemin complet de l'environnement
CONFIG_SH="${SCRIPT_DIR}/config.sh"  # Chemin absolu vers config.sh
OUTPUT_BASE_DIR="${BASE_PATH}/data/processed_data/STARsolo_result"  # Nouveau chemin de base pour les résultats
SLURM_PARTITION="bigmem"  # Partition SLURM par défaut

# Initialiser conda
. /local/env/envconda.sh

# Activer l'environnement conda avec le chemin complet
conda activate "$CONDA_ENV_PATH"

# === Main script ===
# Parse command line arguments
TARGET_SAMPLE=""
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--sample)
            TARGET_SAMPLE="$2"
            shift 2
            ;;
        -t|--type)
            INPUT_TYPE="$2"
            shift 2
            ;;
        -p|--partition)
            SLURM_PARTITION="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  -s, --sample SAMPLE    Run pipeline for specific sample (e.g., BC_0076)"
            echo "  -t, --type TYPE        Input type to use (default: merged_trimmed)"
            echo "  -p, --partition PART   SLURM partition to use (default: bigmem)"
            echo "  -h, --help             Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Validate YAML file before processing
echo "Validating YAML file: ${SAMPLES_YAML}"

# Check if YAML file exists
if [ ! -f "${SAMPLES_YAML}" ]; then
    echo "ERROR: YAML file not found: ${SAMPLES_YAML}"
    echo "Please check the SAMPLES_YAML variable or create the file"
    exit 1
fi

# Check if YAML file is readable
if [ ! -r "${SAMPLES_YAML}" ]; then
    echo "ERROR: YAML file is not readable: ${SAMPLES_YAML}"
    echo "Please check file permissions"
    exit 1
fi

# Check if YAML file is valid
if ! yq -e '.' "${SAMPLES_YAML}" > /dev/null 2>&1; then
    echo "ERROR: YAML file is not valid or malformed: ${SAMPLES_YAML}"
    echo "Please check the YAML syntax"
    exit 1
fi

# Check if samples section exists
if ! yq -e '.samples' "${SAMPLES_YAML}" > /dev/null 2>&1; then
    echo "ERROR: No 'samples' section found in YAML file: ${SAMPLES_YAML}"
    echo "Please check the YAML structure"
    exit 1
fi

echo "YAML file validation completed."

# Get sample names from the YAML file
if [ -n "$TARGET_SAMPLE" ]; then
    # Check if the specified sample exists and has the required input type
    if yq -e ".samples.${TARGET_SAMPLE}.R1.${INPUT_TYPE}" "${SAMPLES_YAML}" > /dev/null 2>&1; then
        SAMPLES=("$TARGET_SAMPLE")
        echo "Processing single sample: ${TARGET_SAMPLE}"
        echo "Using input files:"
        R1_FILE=$(yq -r ".samples.${TARGET_SAMPLE}.R1.${INPUT_TYPE}" "${SAMPLES_YAML}")
        R2_FILE=$(yq -r ".samples.${TARGET_SAMPLE}.R2.${INPUT_TYPE}" "${SAMPLES_YAML}")
        echo "R1: $R1_FILE"
        echo "R2: $R2_FILE"
        
        # Validate that the files exist
        if [ ! -f "$R1_FILE" ]; then
            echo "ERROR: R1 file not found: $R1_FILE"
            exit 1
        fi
        if [ ! -f "$R2_FILE" ]; then
            echo "ERROR: R2 file not found: $R2_FILE"
            exit 1
        fi
    else
        echo "ERROR: Sample ${TARGET_SAMPLE} not found or does not have input type ${INPUT_TYPE}"
        echo "Available samples and types:"
        if yq -e '.samples' "${SAMPLES_YAML}" > /dev/null 2>&1; then
            yq -r '.samples | to_entries | .[] | .key + ": " + (.value.R1 | keys | join(", "))' "${SAMPLES_YAML}" 2>/dev/null || echo "Unable to parse sample information"
        else
            echo "Unable to parse sample information from YAML file"
        fi
        exit 1
    fi
else
    # Get all samples that have the specified input type
    echo "Reading samples from ${SAMPLES_YAML} for input type: ${INPUT_TYPE}..."
    SAMPLES=($(yq -r ".samples | to_entries | .[] | select(.value.R1.${INPUT_TYPE} != null) | .key" "${SAMPLES_YAML}" 2>/dev/null))
    
    # Check if any samples were found
    if [ ${#SAMPLES[@]} -eq 0 ]; then
        echo "ERROR: No samples found with input type '${INPUT_TYPE}'"
        echo "Available input types:"
        yq -r '.samples | to_entries | .[0].value.R1 | keys | join(", ")' "${SAMPLES_YAML}" 2>/dev/null || echo "Unable to parse available types"
        exit 1
    fi
fi



echo "Found ${#SAMPLES[@]} samples to process"
echo "Options:"
echo "- Input type: ${INPUT_TYPE}"
if [ -n "$TARGET_SAMPLE" ]; then
    echo "- Target sample: ${TARGET_SAMPLE}"
fi

# Vérifier que config.sh existe
if [ ! -f "$CONFIG_SH" ]; then
    echo "Erreur: Le fichier de configuration $CONFIG_SH n'existe pas"
    exit 1
fi

# Process each sample with error handling
for SAMPLE in "${SAMPLES[@]}"; do
    echo "Traitement de l'échantillon: ${SAMPLE}"
    
    # Get input file paths from YAML
    R1_PATH=$(yq -r ".samples.${SAMPLE}.R1.${INPUT_TYPE}" "${SAMPLES_YAML}")
    R2_PATH=$(yq -r ".samples.${SAMPLE}.R2.${INPUT_TYPE}" "${SAMPLES_YAML}")
    
    if [ "$R1_PATH" = "null" ] || [ "$R2_PATH" = "null" ]; then
        echo "Attention: Fichiers ${INPUT_TYPE} manquants pour l'échantillon ${SAMPLE}, passage au suivant"
        continue
    fi
    
    # Create output directory with input type subdirectory
    output_dir="${OUTPUT_BASE_DIR}/${INPUT_TYPE}/${SAMPLE}"
    if [ -d "$output_dir" ]; then
        echo "Attention: Le répertoire de sortie existe déjà: $output_dir"
        if [ ! -w "$output_dir" ]; then
            echo "Erreur: Le répertoire de sortie n'est pas accessible en écriture: $output_dir"
            continue
        fi
    else
        mkdir -p "$output_dir" || {
            echo "Erreur: Impossible de créer le répertoire de sortie: $output_dir"
            continue
        }
    fi
    
    # Create and verify temporary config in the output directory
    temp_config="${output_dir}/config_${SAMPLE}.sh"
    temp_config_abs=$(realpath "$temp_config")
    
    # Fonction pour nettoyer en cas d'erreur de création/modification
    cleanup_config() {
        echo "Erreur lors de la préparation du fichier de configuration, nettoyage..."
        rm -f "$temp_config"
        return 1
    }
    
    # Créer le fichier temporaire
    if ! cp "$CONFIG_SH" "$temp_config"; then
        echo "Erreur: Impossible de créer le fichier de configuration temporaire"
        cleanup_config
        continue
    fi
    
    # Update config with verification
    sed_commands=(
        "s/ANALYSIS_NAME=\".*\"/ANALYSIS_NAME=\"STARsolo_microSPLIT_${SAMPLE}\"/"
        "s|BASE_DIR=\".*\"|BASE_DIR=\"${output_dir}\"|"
        "s|SOURCE_FASTQ_R1=\".*\"|SOURCE_FASTQ_R1=\"$(basename "$R1_PATH")\"|"
        "s|SOURCE_FASTQ_R2=\".*\"|SOURCE_FASTQ_R2=\"$(basename "$R2_PATH")\"|"
        "s|SOURCE_FASTQ=\".*\"|SOURCE_FASTQ=\"$(dirname "$R1_PATH")\"|"
        "s|TARGET_FASTQ_R1=\".*\"|TARGET_FASTQ_R1=\"$(basename "$R1_PATH")\"|"
        "s|TARGET_FASTQ_R2=\".*\"|TARGET_FASTQ_R2=\"$(basename "$R2_PATH")\"|"
        "s|SOURCE_BARCODES=\".*\"|SOURCE_BARCODES=\"\${BASE_PATH}/data/processed_data/metadata_DOL_Exp1/barcodeSTARsolo/filtered\"|"
        "s|SOURCE_GENOME_REF=\".*\"|SOURCE_GENOME_REF=\"\${BASE_PATH}/data/raw_data/genome_ref\"|"
        "s|SOURCE_GENOME_ANNOTATION=\".*\"|SOURCE_GENOME_ANNOTATION=\"\${BASE_PATH}/data/raw_data/genome_annotation\"|"
    )
    
    for cmd in "${sed_commands[@]}"; do
        if ! sed -i "$cmd" "$temp_config"; then
            echo "Erreur: Échec de la modification du fichier de configuration"
            cleanup_config
            continue
        fi
    done
    
    # Verify the modified config file
    if [ ! -s "$temp_config" ]; then
        echo "Erreur: Le fichier de configuration est vide après modification"
        cleanup_config
        continue
    fi
    
    # Submit job with error handling
    echo "Soumission du job pour l'échantillon $SAMPLE..."
    if ! CONFIG_FILE="$temp_config_abs" "${SCRIPT_DIR}/submit_pipeline.sh" \
        --threads 64 \
        --memory 500G \
        --runtime 10-00:00:00 \
        --name "STARsolo_microSPLIT_${SAMPLE}"; then
        echo "Erreur: Échec de la soumission du job pour $SAMPLE"
        cleanup_config
        continue
    fi
    
    echo "Job soumis avec succès pour l'échantillon $SAMPLE"
    echo "Le fichier de configuration temporaire sera supprimé automatiquement à la fin du job"
done

echo "Tous les jobs ont été soumis. Utilisez 'squeue -u $USER' pour vérifier leur statut." 