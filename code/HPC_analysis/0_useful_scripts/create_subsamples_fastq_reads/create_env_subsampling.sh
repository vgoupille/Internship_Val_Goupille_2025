#! /bin/bash
#SBATCH --job-name=conda_subsampling_random
#SBATCH --mail-type=ALL
#SBATCH --mail-user=valentin.goupille@univ-rennes.fr
#SBATCH --output=logs/create_env_subsampling_%j.out
#SBATCH --error=logs/create_env_subsampling_%j.err
#SBATCH --time=02:00:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=4

# Load conda
. /local/env/envconda.sh


ENV_PATH="env/envSubsampling"
YAML_FILE="scripts/0_useful_scripts/create_subsamples_fastq_reads/environment_subsampling.yml"

# Check if environment exists
if [ -d "$ENV_PATH" ]; then
    echo "Environment exists, updating..."
    conda env update -p "$ENV_PATH" -f "$YAML_FILE" --prune
else
    echo "Creating new environment..."
    conda env create -p "$ENV_PATH" -f "$YAML_FILE" -y
fi



