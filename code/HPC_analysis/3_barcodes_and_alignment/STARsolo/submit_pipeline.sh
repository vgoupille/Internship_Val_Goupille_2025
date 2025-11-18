#!/bin/bash

# === STARsolo Pipeline Submission Wrapper ===
# This script submits the STARsolo pipeline with customizable SLURM parameters

# Default values (will be overwritten by config.sh if exists)
THREADS=64
MEMORY="600G"
MAX_RUNTIME="10-00:00:00"
EMAIL="goupille.valentin@live.fr"
ANALYSIS_NAME="STARsolo_microSPLIT_Pipeline"
SLURM_PARTITION="bigmem"  # Partition SLURM par défaut

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Load configuration if available
if [ -f "$SCRIPT_DIR/config.sh" ]; then
    source "$SCRIPT_DIR/config.sh"
    echo "Configuration loaded from $SCRIPT_DIR/config.sh"
fi

# Help function
show_help() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -h, --help                Show this help message"
    echo "  -t, --threads N           Set number of CPU threads (default: $THREADS)"
    echo "  -m, --memory SIZE         Set memory allocation (default: $MEMORY)"
    echo "  -r, --runtime HH:MM:SS    Set maximum runtime (default: $MAX_RUNTIME)"
    echo "  -e, --email EMAIL         Set notification email (default: $EMAIL)"
    echo "  -n, --name NAME           Set job name (default: $ANALYSIS_NAME)"
    echo "  -p, --partition PART      Set SLURM partition (default: $SLURM_PARTITION)"
    echo ""
    echo "Example: $0 --threads 32 --memory 64G --runtime 12:00:00 --partition bigmem"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -h|--help)
            show_help
            exit 0
            ;;
        -t|--threads)
            THREADS="$2"
            shift 2
            ;;
        -m|--memory)
            MEMORY="$2"
            shift 2
            ;;
        -r|--runtime)
            MAX_RUNTIME="$2"
            shift 2
            ;;
        -e|--email)
            EMAIL="$2"
            shift 2
            ;;
        -n|--name)
            ANALYSIS_NAME="$2"
            shift 2
            ;;
        -p|--partition)
            SLURM_PARTITION="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Submit the job with updated parameters
echo "Submitting STARsolo pipeline with the following parameters:"
echo "  Job name:  $ANALYSIS_NAME"
echo "  Email:     $EMAIL"
echo "  Threads:   $THREADS"
echo "  Memory:    $MEMORY"
echo "  Runtime:   $MAX_RUNTIME"
echo "  Partition: $SLURM_PARTITION"
echo ""

# Vérifier que CONFIG_FILE est défini
if [ -z "$CONFIG_FILE" ]; then
    echo "ERROR: CONFIG_FILE is not set"
    exit 1
fi

# Vérifier que le fichier existe
if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: CONFIG_FILE does not exist: $CONFIG_FILE"
    exit 1
fi

# Obtenir le chemin absolu
CONFIG_FILE_ABS=$(realpath "$CONFIG_FILE")
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to get absolute path for CONFIG_FILE"
    exit 1
fi

# Submit the job with the config file path
if ! sbatch --job-name="$ANALYSIS_NAME" \
       --mail-user="$EMAIL" \
       --cpus-per-task="$THREADS" \
       --mem="$MEMORY" \
       --time="$MAX_RUNTIME" \
       --partition="$SLURM_PARTITION" \
       --export="CONFIG_FILE=$CONFIG_FILE_ABS" \
       "$SCRIPT_DIR/starsolo_microsplit_pipeline.sh"; then
    echo "ERROR: Failed to submit job"
    exit 1
fi

echo "Job submitted. Use 'squeue -u $USER' to check status."
exit 0 