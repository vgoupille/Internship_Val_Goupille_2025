#! /bin/bash

#SBATCH --job-name=subsampling_random_reads
#SBATCH --mail-type=ALL
#SBATCH --mail-user=valentin.goupille@univ-rennes.fr
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=10:00:00
#SBATCH --output=logs/subsampling_random_reads_%j.log
#SBATCH --error=logs/subsampling_random_reads_%j.err

# Default parameters
SAMPLES_YAML="data/info/samples/samples_all.yaml"
OUTPUT_DIR="data/raw_data/subsampled_data/random_reads"
INPUT_TYPE="unzipped"  # Can be: unzipped, trimmed_simple, trimmed_complex
SEEDS=(200)           # Default single seed
NUM_READS=(5000 10000 1000000)  # Array of read numbers to subsample
SELECTED_SAMPLES=()    # Empty array means process all samples

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --samples-yaml)
            SAMPLES_YAML="$2"
            shift 2
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --input-type)
            INPUT_TYPE="$2"
            shift 2
            ;;
        --seeds)
            IFS=',' read -ra SEEDS <<< "$2"
            shift 2
            ;;
        --num-reads)
            IFS=',' read -ra NUM_READS <<< "$2"
            shift 2
            ;;
        --samples)
            IFS=',' read -ra SELECTED_SAMPLES <<< "$2"
            shift 2
            ;;
        *)
            echo "Unknown parameter: $1"
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --samples-yaml PATH    Path to samples YAML file (default: $SAMPLES_YAML)"
            echo "  --output-dir PATH      Output directory (default: $OUTPUT_DIR)"
            echo "  --input-type TYPE      Input type: unzipped, trimmed_simple, trimmed_complex (default: $INPUT_TYPE)"
            echo "  --seeds SEEDS          Comma-separated list of seeds (default: ${SEEDS[*]})"
            echo "  --num-reads READS      Comma-separated list of read numbers (default: ${NUM_READS[*]})"
            echo "  --samples SAMPLES      Comma-separated list of sample names to process (default: all samples)"
            exit 1
            ;;
    esac
done

# Load conda module
. /local/env/envconda.sh

# Create or update conda environment
ENV_PATH="env/envSubsampling"
YAML_FILE="scripts/0_useful_scripts/create_subsamples_fastq_reads/environment_subsampling.yml"

if [ -d "$ENV_PATH" ]; then
    echo "Updating conda environment..."
    conda env update -p "$ENV_PATH" -f "$YAML_FILE" --prune
else
    echo "Creating conda environment..."
    conda env create -p "$ENV_PATH" -f "$YAML_FILE" -y
fi

# Activate environment
conda activate "$ENV_PATH"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Function to extract FASTQ paths from samples.yaml
extract_fastq_paths() {
    local sample_name="$1"
    local yaml_file="$2"
    local input_type="$3"
    
    # Extract R1 path
    local r1_path
    r1_path=$(yq -r ".samples[\"${sample_name}\"].R1.${input_type}" "${yaml_file}")
    if [ -z "$r1_path" ] || [ "$r1_path" = "null" ]; then
        echo "Error: Could not find R1 path for sample ${sample_name} with type ${input_type} in ${yaml_file}"
        return 1
    fi
    
    # Extract R2 path
    local r2_path
    r2_path=$(yq -r ".samples[\"${sample_name}\"].R2.${input_type}" "${yaml_file}")
    if [ -z "$r2_path" ] || [ "$r2_path" = "null" ]; then
        echo "Error: Could not find R2 path for sample ${sample_name} with type ${input_type} in ${yaml_file}"
        return 1
    fi
    
    # Verify files exist
    if [ ! -f "${r1_path}" ]; then
        echo "Error: R1 file not found: ${r1_path}"
        return 1
    fi
    
    if [ ! -f "${r2_path}" ]; then
        echo "Error: R2 file not found: ${r2_path}"
        return 1
    fi
    
    echo "Found FASTQ files for ${sample_name}:"
    echo "R1: ${r1_path}"
    echo "R2: ${r2_path}"
    
    # Return paths through global variables
    R1_PATH="${r1_path}"
    R2_PATH="${r2_path}"
    return 0
}

# Function to process a single sample
process_sample() {
    local sample=$1
    local r1_path=$2
    local r2_path=$3
    
    echo "Processing sample: $sample"
    
    for seed in "${SEEDS[@]}"; do
        for num_reads in "${NUM_READS[@]}"; do
            local output_subdir="${OUTPUT_DIR}/${sample}_seed${seed}_reads${num_reads}"
            mkdir -p "$output_subdir"
            
            echo "Subsampling R1 with seed $seed and $num_reads reads..."
            seqtk sample -s"$seed" "$r1_path" "$num_reads" > "${output_subdir}/${sample}_R1_subsampled.fastq"
            
            echo "Subsampling R2 with seed $seed and $num_reads reads..."
            seqtk sample -s"$seed" "$r2_path" "$num_reads" > "${output_subdir}/${sample}_R2_subsampled.fastq"
            
            echo "Completed subsampling for $sample (seed=$seed, reads=$num_reads)"
        done
    done
}

# Get list of samples to process
if [ ${#SELECTED_SAMPLES[@]} -eq 0 ]; then
    echo "No samples specified, processing all samples from YAML..."
    # Get list of samples using yq
    mapfile -t SAMPLES_TO_PROCESS < <(yq -r '.samples | keys | .[]' "$SAMPLES_YAML")
else
    echo "Processing selected samples: ${SELECTED_SAMPLES[*]}"
    SAMPLES_TO_PROCESS=("${SELECTED_SAMPLES[@]}")
fi

# Process each sample
for sample in "${SAMPLES_TO_PROCESS[@]}"; do
    echo "Processing sample: $sample"
    
    # Extract and verify FASTQ paths
    if ! extract_fastq_paths "$sample" "$SAMPLES_YAML" "$INPUT_TYPE"; then
        echo "Error: Failed to extract FASTQ paths for sample $sample"
        continue
    fi
    
    # Process the sample with verified paths
    process_sample "$sample" "$R1_PATH" "$R2_PATH"
done

echo "Subsampling completed for all processed samples!"