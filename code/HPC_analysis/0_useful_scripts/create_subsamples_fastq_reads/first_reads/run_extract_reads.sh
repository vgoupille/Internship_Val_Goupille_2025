#! /bin/bash

# Default values
NUM_READS=(5000 10000 1000000)  # Array of read numbers to subsample
SELECTED_SAMPLES=()    # Empty array means process all samples
YAML="data/info/samples/samples_all.yaml"
ENV_PATH="env/envSubsampling"
ENV_YAML="scripts/0_useful_scripts/create_subsamples_fastq_reads/environment_subsampling.yml"
OUTPUT_DIR="data/raw_data/subsampled_data/first_reads"  # Default output directory
SCRIPT_PATH="scripts/0_useful_scripts/create_subsamples_fastq_reads/first_reads/extract_first_reads.py"  # Chemin correct du script Python

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --reads)
            # Convert single value to array
            NUM_READS=("$2")
            shift 2
            ;;
        --samples)
            # Convert space-separated list to array
            IFS=' ' read -ra SELECTED_SAMPLES <<< "$2"
            shift 2
            ;;
        --yaml)
            YAML="$2"
            shift 2
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        *)
            echo "Unknown parameter: $1"
            echo "Usage: sbatch $0 [--reads N] [--samples 'SAMPLE1 SAMPLE2 ...'] [--yaml YAML_FILE] [--output OUTPUT_DIR]"
            exit 1
            ;;
    esac
done

# Function to process a single sample with a given number of reads
process_sample() {
    local sample=$1
    local reads=$2
    
    # Calculate memory based on number of reads (rough estimate: 1GB per 1000 reads)
    local mem=$((reads / 1000 + 8))
    mem=$((mem > 32 ? 32 : mem))  # Cap at 32GB

    # Calculate time based on number of reads (rough estimate: 1 hour per 5000 reads)
    local time=$((reads / 5000 + 2))
    time=$((time > 24 ? 24 : time))  # Cap at 24 hours

    # Create job script
    cat << EOF > "extract_${reads}_reads_${sample}.sh"
#! /bin/bash
#SBATCH --job-name=extract_${reads}_reads_${sample}
#SBATCH --mail-type=ALL
#SBATCH --mail-user=valentin.goupille@univ-rennes.fr
#SBATCH --cpus-per-task=4
#SBATCH --mem=${mem}G
#SBATCH --time=${time}:00:00
#SBATCH --output=logs/extract_reads/extract_${reads}_reads_${sample}_%j.log
#SBATCH --error=logs/extract_reads/extract_${reads}_reads_${sample}_%j.err

# Load conda environment
. /local/env/envconda.sh

# Activate environment (no need to create/update, it's done in the main script)
conda activate "$ENV_PATH"

# Run the Python script with specified parameters
echo "Starting extraction of first ${reads} reads for sample ${sample}..."
python "${SCRIPT_PATH}" --reads ${reads} --sample ${sample} --yaml ${YAML} --output "${OUTPUT_DIR}/${reads}_reads"

echo "Job completed!"
EOF

    # Submit the job
    sbatch "extract_${reads}_reads_${sample}.sh"
    rm "extract_${reads}_reads_${sample}.sh"
}

# Load conda and create/update environment only once at the start
echo "Setting up conda environment..."
. /local/env/envconda.sh

# Create or update conda environment
if [ -d "$ENV_PATH" ]; then
    echo "Updating conda environment..."
    conda env update -p "$ENV_PATH" -f "$ENV_YAML" --prune
else
    echo "Creating conda environment..."
    conda env create -p "$ENV_PATH" -f "$ENV_YAML" -y
fi

# Create log directory if it doesn't exist
mkdir -p logs/extract_reads

# Create output directories if they don't exist
for reads in "${NUM_READS[@]}"; do
    mkdir -p "${OUTPUT_DIR}/${reads}_reads"
done

# Get list of samples from YAML if no samples specified
if [ ${#SELECTED_SAMPLES[@]} -eq 0 ]; then
    echo "No samples specified, processing all samples from ${YAML}..."
    # Use Python to extract sample names from YAML
    SELECTED_SAMPLES=($(python -c "
import yaml
with open('${YAML}', 'r') as f:
    data = yaml.safe_load(f)
    if 'samples' in data:
        print(' '.join(data['samples'].keys()))
    else:
        print('Error: No "samples" key found in YAML file')
        exit(1)
"))
fi

# Process each sample with each number of reads
for sample in "${SELECTED_SAMPLES[@]}"; do
    for reads in "${NUM_READS[@]}"; do
        echo "Submitting job for sample ${sample} with ${reads} reads..."
        process_sample "${sample}" "${reads}"
    done
done

echo "All jobs submitted!" 