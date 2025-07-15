#!/bin/bash
#SBATCH --job-name=multiQC_%A
#SBATCH --output=logs/multiQC_%A_%j.out
#SBATCH --error=logs/multiQC_%A_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=valentin.goupille@univ-rennes.fr
#SBATCH --partition=bigmem
#SBATCH --cpus-per-task=32
#SBATCH --mem=64G
#SBATCH --time=04:00:00

# Remove redundant path definitions since they are passed via --export
# PROJECT_DIR, SCRIPT_DIR, LOGS_DIR, ENV_DIR, SAMPLES_YAML, and ENV_YAML
# are now passed from launch_multiQC_jobs.sh

# Ensure we're in the project directory
cd "$PROJECT_DIR" || { echo "Error: Cannot change to project directory"; exit 1; }

# Create logs directory if it doesn't exist
mkdir -p "$LOGS_DIR" || { echo "Error: Cannot create logs directory"; exit 1; }

# Parse command line arguments
READ_TYPE=""
DATA_TYPE=""
OUTPUT_DIR=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --read_type)
            READ_TYPE="$2"
            shift 2
            ;;
        --data_type)
            DATA_TYPE="$2"
            shift 2
            ;;
        --output_dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        *)
            echo "Unknown parameter: $1"
            echo "Usage: $0 --read_type [R1|R2] [--data_type TYPE] [--output_dir DIR]"
            exit 1
            ;;
    esac
done

# Validate read type
if [[ "$READ_TYPE" != "R1" && "$READ_TYPE" != "R2" ]]; then
    echo "Error: --read_type must be either R1 or R2"
    exit 1
fi

# Load conda environment
source /local/env/envconda.sh || { echo "Error: Cannot load conda environment"; exit 1; }

# Create or update conda environment
if [ ! -d "$ENV_DIR" ]; then
    echo "Creating conda environment..."
    conda env create -p "$ENV_DIR" -f "$ENV_YAML" || { echo "Error: Cannot create conda environment"; exit 1; }
else
    echo "Updating conda environment..."
    conda env update -p "$ENV_DIR" -f "$ENV_YAML" || { echo "Error: Cannot update conda environment"; exit 1; }
fi

# Activate environment
conda activate "$ENV_DIR" || { echo "Error: Cannot activate conda environment"; exit 1; }

# Run MultiQC analysis
if [ -z "$DATA_TYPE" ]; then
    if [ -z "$OUTPUT_DIR" ]; then
        python "${SCRIPT_DIR}/run_multiQC.py" --read_type "$READ_TYPE" --yaml_file "$SAMPLES_YAML" || { echo "Error: MultiQC analysis failed"; exit 1; }
    else
        python "${SCRIPT_DIR}/run_multiQC.py" --read_type "$READ_TYPE" --yaml_file "$SAMPLES_YAML" --output_dir "$OUTPUT_DIR" || { echo "Error: MultiQC analysis failed"; exit 1; }
    fi
else
    if [ -z "$OUTPUT_DIR" ]; then
        python "${SCRIPT_DIR}/run_multiQC.py" --read_type "$READ_TYPE" --data_type "$DATA_TYPE" --yaml_file "$SAMPLES_YAML" || { echo "Error: MultiQC analysis failed"; exit 1; }
    else
        python "${SCRIPT_DIR}/run_multiQC.py" --read_type "$READ_TYPE" --data_type "$DATA_TYPE" --yaml_file "$SAMPLES_YAML" --output_dir "$OUTPUT_DIR" || { echo "Error: MultiQC analysis failed"; exit 1; }
    fi
fi 