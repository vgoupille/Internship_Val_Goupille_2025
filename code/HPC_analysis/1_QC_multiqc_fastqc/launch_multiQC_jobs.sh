#!/bin/bash

# Define paths using relative paths from script location
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/../.." && pwd )"
LOGS_DIR="${SCRIPT_DIR}/logs"
ENV_DIR="${PROJECT_DIR}/env/envMultiQC"
DEFAULT_OUTPUT_DIR="${PROJECT_DIR}/data/processed_data/multiqc_results"
SAMPLES_YAML="${PROJECT_DIR}/data/info/samples/samples_trimming.yaml"
ENV_YAML="${SCRIPT_DIR}/environment_multiQC.yml"

# Create logs directory if it doesn't exist
mkdir -p "$LOGS_DIR"

# Parse command line arguments
DATA_TYPE=""
OUTPUT_DIR=""
READ_TYPE=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --data_type)
            DATA_TYPE="$2"
            shift 2
            ;;
        --output_dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --read_type)
            READ_TYPE="$2"
            shift 2
            ;;
        *)
            echo "Unknown parameter: $1"
            echo "Usage: $0 --data_type TYPE [--output_dir DIR] [--read_type TYPE]"
            echo "data_type must be a type present in the YAML file (e.g. unzipped, trimmed_simple, trimmed_complex, subsampled, test100000_rmTSO_74nt, etc.)"
            echo "read_type can be: R1, R2, or both (default)"
            exit 1
            ;;
    esac
done

# Check if data type is provided
if [ -z "$DATA_TYPE" ]; then
    echo "Error: --data_type is required"
    echo "Usage: $0 --data_type TYPE [--output_dir DIR] [--read_type TYPE]"
    echo "data_type must be a type present in the YAML file (e.g. unzipped, trimmed_simple, trimmed_complex, subsampled, test100000_rmTSO_74nt, etc.)"
    exit 1
fi

# Set default output directory if not provided
if [ -z "$OUTPUT_DIR" ]; then
    OUTPUT_DIR="${DEFAULT_OUTPUT_DIR}_${DATA_TYPE}"
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

echo "Launching MultiQC jobs for ${DATA_TYPE} data..."
echo "Results will be stored in: ${OUTPUT_DIR}"
echo "Logs will be stored in: ${LOGS_DIR}"

# Function to launch a MultiQC job
launch_multiqc_job() {
    local read_type=$1
    local job_name="multiqc_${read_type}_${DATA_TYPE}"
    local output_log="${LOGS_DIR}/${job_name}_%j.out"
    local error_log="${LOGS_DIR}/${job_name}_%j.err"
    
    sbatch --parsable \
        --job-name="$job_name" \
        --output="$output_log" \
        --error="$error_log" \
        --chdir="$PROJECT_DIR" \
        --export="PROJECT_DIR=$PROJECT_DIR,SCRIPT_DIR=$SCRIPT_DIR,LOGS_DIR=$LOGS_DIR,ENV_DIR=$ENV_DIR,SAMPLES_YAML=$SAMPLES_YAML,ENV_YAML=$ENV_YAML" \
        "$SCRIPT_DIR/run_multiQC.sh" \
        --read_type "$read_type" \
        --data_type "$DATA_TYPE" \
        --output_dir "${OUTPUT_DIR}/${read_type}"
}

# Launch jobs based on read_type parameter
if [ -z "$READ_TYPE" ] || [ "$READ_TYPE" = "both" ]; then
    # Launch both R1 and R2 jobs
    R1_JOB_ID=$(launch_multiqc_job "R1")
    R2_JOB_ID=$(launch_multiqc_job "R2")
    echo "Jobs have been submitted:"
    echo "- R1 job ID: $R1_JOB_ID"
    echo "- R2 job ID: $R2_JOB_ID"
elif [ "$READ_TYPE" = "R1" ] || [ "$READ_TYPE" = "R2" ]; then
    # Launch single job
    JOB_ID=$(launch_multiqc_job "$READ_TYPE")
    echo "Job has been submitted:"
    echo "- ${READ_TYPE} job ID: $JOB_ID"
else
    echo "Error: Invalid read_type. Must be R1, R2, or both"
    exit 1
fi

echo "You can monitor their status using: squeue -u $USER"
echo "Logs will be available in: ${LOGS_DIR}" 