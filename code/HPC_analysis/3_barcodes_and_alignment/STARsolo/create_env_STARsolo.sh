#!/bin/bash
#SBATCH --job-name=conda_STARsolo
#SBATCH --mail-type=ALL
#SBATCH --mail-user=valentin.goupille@univ-rennes.fr
#SBATCH --output=/projects/microsplit/logs/create_env_STARsolo_%j.out
#SBATCH --error=/projects/microsplit/logs/create_env_STARsolo_%j.err
#SBATCH --time=02:00:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=4

# Load conda
. /local/env/envconda.sh

# Define paths
BASE_PATH="/projects/microsplit/Internship_Val_Goupille_2025"
ENV_PATH="${BASE_PATH}/env/STARsolo_microSPLIT_DOL"
YAML_FILE="${BASE_PATH}/code/HPC_analysis/3_barcodes_and_alignment/STARsolo/environment_STARsolo.yml"

echo "Creating/updating STARsolo environment..."
echo "Environment path: $ENV_PATH"
echo "YAML file: $YAML_FILE"

# Check if environment exists
if [ -d "$ENV_PATH" ]; then
    echo "Environment exists, updating..."
    conda env update -p "$ENV_PATH" -f "$YAML_FILE" --prune
else
    echo "Creating new environment..."
    conda env create -p "$ENV_PATH" -f "$YAML_FILE" -y
fi

# Verify installation
echo "Verifying installation..."
conda activate "$ENV_PATH"

# Check if tools are available
for tool in STAR cufflinks gffread yq; do
    if command -v $tool &> /dev/null; then
        echo "✓ $tool is installed"
        if [ "$tool" = "STAR" ]; then
            STAR --version
        fi
    else
        echo "✗ $tool is NOT installed"
    fi
done

echo "Environment setup completed!" 