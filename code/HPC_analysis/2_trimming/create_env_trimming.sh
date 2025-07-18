#! /bin/bash
#SBATCH --job-name=conda_trimming
#SBATCH --mail-type=ALL
#SBATCH --mail-user=valentin.goupille@univ-rennes.fr
#SBATCH --output=logs/create_env_trimming_%j.out
#SBATCH --error=logs/create_env_trimming_%j.err
#SBATCH --time=02:00:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=4


# Load conda
. /local/env/envconda.sh


# Define paths relative to script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_PATH="${SCRIPT_DIR}/../../env/envTrimming"
YAML_FILE="${SCRIPT_DIR}/environment_trimming.yml"

# Check if environment exists
if [ -d "$ENV_PATH" ]; then
    echo "Environment exists, updating..."
    conda env update -p "$ENV_PATH" -f "$YAML_FILE" --prune
else
    echo "Creating new environment..."
    conda env create -p "$ENV_PATH" -f "$YAML_FILE" -y
fi

#old way to create the environment : 
# Create conda environment from YAML file
# conda env create -p env/envTrimming -f scripts/1_trimming/environment_trimming.yml -y





