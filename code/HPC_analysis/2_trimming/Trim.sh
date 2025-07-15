#!/bin/bash
#SBATCH --job-name=microsplit_trim_submit
#SBATCH --output=/projects/microsplit/scripts/2_trimming/logs/slurm/microsplit_trim_submit_%j.out
#SBATCH --error=/projects/microsplit/scripts/2_trimming/logs/slurm/microsplit_trim_submit_%j.err
#SBATCH --time=1:00:00
#SBATCH --mem=2G
#SBATCH --cpus-per-task=1
#SBATCH --partition=genouest

# Define paths
SCRIPT_DIR="/projects/microsplit/scripts/2_trimming"
LOGS_DIR="/projects/microsplit/scripts/2_trimming/logs"
SLURM_LOGS_DIR="/projects/microsplit/scripts/2_trimming/logs/slurm"
RESULTS_DIR="/projects/microsplit/scripts/2_trimming/results"
INFO_DIR="/projects/microsplit/data/info"
SAMPLES_YAML="/projects/microsplit/data/info/samples/samples_trimming.yaml"
ENV_DIR="/projects/microsplit/env/envSimpleTrimming"

# Load and activate conda environment
source /local/env/envconda.sh
source activate "${ENV_DIR}"

# Default values
OUTPUT_DIR=""
SAMPLE=""
INPUT_TYPE="unzipped"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
RUN_ID="run_${TIMESTAMP}"

# Default SLURM resources for sub-jobs
SLURM_CPUS=32
SLURM_MEM="200G"
SLURM_TIME="10-00:00:00"
SLURM_PARTITION="bigmem"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --sample)
            SAMPLE="$2"
            shift 2
            ;;
        --input-type)
            INPUT_TYPE="$2"
            shift 2
            ;;
        --run-id)
            RUN_ID="$2"
            shift 2
            ;;
        --cpus)
            SLURM_CPUS="$2"
            shift 2
            ;;
        --mem)
            SLURM_MEM="$2"
            shift 2
            ;;
        --time)
            SLURM_TIME="$2"
            shift 2
            ;;
        --partition)
            SLURM_PARTITION="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --output-dir DIR    Output directory"
            echo "  --sample SAMPLE     Process single sample"
            echo "  --input-type TYPE   Input type (unzipped/subsampled)"
            echo "  --run-id ID         Run ID (default: run_TIMESTAMP)"
            echo "  --cpus N            Number of CPUs (default: 4)"
            echo "  --mem MEM           Memory per node (default: 16G)"
            echo "  --time TIME         Time limit (default: 4:00:00)"
            echo "  --partition PART    SLURM partition (default: genouest, options: genouest, bigmem)"
            exit 1
            ;;
    esac
done

# Function to log messages
log() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [${level}] ${message}" | tee -a "${LOGS_DIR}/${RUN_ID}.log"
}

# Function to check if required tools are available
check_requirements() {
    local tools=("cutadapt" "fastp" "python3")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log "ERROR" "Required tool '$tool' is not installed"
            exit 1
        fi
    done
}

# Function to read samples from YAML
read_samples_yaml() {
    local python_script=$(cat << 'EOF'
import yaml
import sys
import json

def read_samples(yaml_file, sample=None, input_type="unzipped"):
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)
    
    samples = {}
    sample_list = sample.split() if sample else None
    
    for sample_name, sample_data in data['samples'].items():
        if sample_list and sample_name not in sample_list:
            continue
            
        if 'R1' in sample_data and 'R2' in sample_data:
            if input_type in sample_data['R1'] and input_type in sample_data['R2']:
                samples[sample_name] = {
                    'R1': sample_data['R1'][input_type],
                    'R2': sample_data['R2'][input_type]
                }
    
    print(json.dumps(samples))

if __name__ == "__main__":
    yaml_file = sys.argv[1]
    sample = sys.argv[2] if len(sys.argv) > 2 else None
    input_type = sys.argv[3] if len(sys.argv) > 3 else "unzipped"
    read_samples(yaml_file, sample, input_type)
EOF
)
    
    python3 -c "${python_script}" "$SAMPLES_YAML" "$SAMPLE" "$INPUT_TYPE"
}

# Function to validate SLURM parameters
validate_slurm_params() {
    # Validate CPUs
    if ! [[ "$SLURM_CPUS" =~ ^[0-9]+$ ]] || [ "$SLURM_CPUS" -lt 1 ]; then
        log "ERROR" "Invalid CPU count: ${SLURM_CPUS}"
        exit 1
    fi

    # Validate memory format (e.g., 16G, 32G, 64G, 128G)
    if ! [[ "$SLURM_MEM" =~ ^[0-9]+[MG]$ ]]; then
        log "ERROR" "Invalid memory format: ${SLURM_MEM}. Use format like 16G, 32G, etc."
        exit 1
    fi

    # Validate time format (DD-HH:MM:SS)
    if ! [[ "$SLURM_TIME" =~ ^[0-9]+-[0-9]{2}:[0-9]{2}:[0-9]{2}$ ]]; then
        log "ERROR" "Invalid time format: ${SLURM_TIME}. Use format DD-HH:MM:SS"
        exit 1
    fi

    # Validate partition
    if [[ ! "$SLURM_PARTITION" =~ ^(genouest|bigmem)$ ]]; then
        log "ERROR" "Invalid partition: ${SLURM_PARTITION}. Use 'genouest' or 'bigmem'"
        exit 1
    fi
}

# Function to submit SLURM job for a sample
submit_slurm_job() {
    local sample_name="$1"
    local r1_input="$2"
    local r2_input="$3"
    local output_dir="${OUTPUT_DIR:-${RESULTS_DIR}/${RUN_ID}/${INPUT_TYPE}/${sample_name}}"
    
    # Create job script
    local job_script="${SLURM_LOGS_DIR}/${RUN_ID}_${sample_name}_job.sh"
    cat > "${job_script}" << EOF
#!/bin/bash
#SBATCH --job-name=microsplit_trim_${sample_name}
#SBATCH --output=/projects/microsplit/scripts/2_trimming/logs/slurm/${RUN_ID}_${sample_name}_%j.out
#SBATCH --error=/projects/microsplit/scripts/2_trimming/logs/slurm/${RUN_ID}_${sample_name}_%j.err
#SBATCH --time=${SLURM_TIME}
#SBATCH --mem=${SLURM_MEM}
#SBATCH --cpus-per-task=${SLURM_CPUS}
#SBATCH --partition=${SLURM_PARTITION}

# Load and activate conda environment
source /local/env/envconda.sh
source activate "${ENV_DIR}"

# Verify conda environment
echo "Checking conda environment..."
which cutadapt
which fastp
which python3

# Run trimming process
"${SCRIPT_DIR}/process_sample.sh" "${sample_name}" "${r1_input}" "${r2_input}" "${output_dir}" "${RUN_ID}"
EOF
    
    # Make the job script executable
    chmod +x "${job_script}"
    
    # Submit job with the same partition as the main job
    sbatch --partition="${SLURM_PARTITION}" "${job_script}"
    log "INFO" "Submitted job for sample ${sample_name} (Job script: ${job_script})"
    log "INFO" "Resources: CPUs=${SLURM_CPUS}, MEM=${SLURM_MEM}, TIME=${SLURM_TIME}, PARTITION=${SLURM_PARTITION}"
}

# Main execution
main() {
    # Create necessary directories
    mkdir -p "${LOGS_DIR}"
    mkdir -p "${SLURM_LOGS_DIR}"
    mkdir -p "${RESULTS_DIR}/${RUN_ID}/${INPUT_TYPE}"
    
    # Initialize logging
    log "INFO" "Starting trimming pipeline (Run ID: ${RUN_ID})"
    log "INFO" "Input type: ${INPUT_TYPE}"
    if [ -n "${SAMPLE}" ]; then
        log "INFO" "Processing single sample: ${SAMPLE}"
    else
        log "INFO" "Processing all samples"
    fi
    
    # Validate SLURM parameters
    validate_slurm_params
    
    # Check requirements
    check_requirements
    
    # Read samples from YAML
    local samples_json
    samples_json=$(read_samples_yaml)
    
    if [ -z "$samples_json" ]; then
        log "ERROR" "No samples found in YAML file"
        exit 1
    fi
    
    # Process each sample
    echo "$samples_json" | python3 -c '
import json
import sys
samples = json.load(sys.stdin)
for sample_name, paths in samples.items():
    print(f"{sample_name}\t{paths["R1"]}\t{paths["R2"]}")
' | while IFS=$'\t' read -r sample_name r1_path r2_path; do
        submit_slurm_job "$sample_name" "$r1_path" "$r2_path"
    done
    
    log "INFO" "All jobs submitted successfully"
    log "INFO" "Results will be in: ${RESULTS_DIR}/${RUN_ID}"
    log "INFO" "Logs will be in: ${LOGS_DIR}"
    log "INFO" "SLURM logs will be in: ${SLURM_LOGS_DIR}"
}

# Run main function
main "$@"