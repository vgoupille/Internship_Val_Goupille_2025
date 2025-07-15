#!/bin/bash

# Wrapper script to launch separate SLURM jobs for merging R1 and R2 fastq files
# This script creates and submits two separate jobs, one for each read type

# Usage function
usage() {
    echo "Usage: $0 -i <input_dir> -o <output_name>"
    echo "Options:"
    echo "  -i    Input directory containing fastq files (required)"
    echo "  -o    Output name for merged files (required)"
    echo "Example: $0 -i data/raw_data/unzipped_data/fastq -o sample1"
    exit 1
}

# Parse command line arguments
while getopts "i:o:" opt; do
    case $opt in
        i) input_dir="$OPTARG";;
        o) output_name="$OPTARG";;
        ?) usage;;
    esac
done

# Check if required arguments are provided
if [ -z "$input_dir" ] || [ -z "$output_name" ]; then
    echo "Error: Both input directory (-i) and output name (-o) are required"
    usage
fi

# Check if input directory exists
if [ ! -d "$input_dir" ]; then
    echo "Error: Input directory '$input_dir' does not exist"
    exit 1
fi

# Define paths
output_dir="data/processed_data/merged_data"
mkdir -p "$output_dir"
output_prefix="${output_dir}/${output_name}"
script_dir="$(dirname "$0")"
log_dir="logs"

# Create output and log directories if they don't exist
mkdir -p $(dirname $output_prefix)
mkdir -p $log_dir

# Function to create and submit a SLURM job for a specific read type
submit_merge_job() {
    local read_type=$1
    local read_number=${read_type#R}  # Extract the number after R
    local job_name="merge_fastq_${read_type}"
    local slurm_script="${script_dir}/merge_fastq_${read_type}.sh"
    
    # Create the SLURM script for this read type
    cat > "$slurm_script" << EOF
#!/bin/bash
#SBATCH --job-name=${job_name}
#SBATCH --partition=bigmem
#SBATCH --output=${log_dir}/${job_name}_%j.log
#SBATCH --error=${log_dir}/${job_name}_%j.err
#SBATCH --time=12:00:00
#SBATCH --mem=64G
#SBATCH --cpus-per-task=8

# Script to merge ${read_type} fastq.gz files recursively from subdirectories
# Input files are in ${input_dir} and its subdirectories
# Output will be in ${output_prefix}-${read_type}.fastq.gz

# Find all input files
echo "Searching for ${read_type} files..."
find ${input_dir} -type f -name "BC_*_${read_type}*.fastq.gz" > input_files.txt

# Check if we found any files
if [ ! -s "input_files.txt" ]; then
    echo "Error: No ${read_type} fastq.gz files found in ${input_dir} or its subdirectories"
    exit 1
fi

# Print the number of files found
num_files=\$(wc -l < input_files.txt)
echo "Found \$num_files ${read_type} files to merge"

# Start time
start_time=\$(date +%s)

# Merge files directly to final location
echo "Starting merge of ${read_type} files..."
while IFS= read -r file; do
    if [ -f "\$file" ]; then
        echo "Processing: \$(basename "\$file")"
        cat "\$file" >> "${output_prefix}-${read_type}.fastq.gz"
    else
        echo "Warning: File not found: \$file"
    fi
done < input_files.txt

# Clean up
rm input_files.txt

# Check if merge was successful
if [ \$? -eq 0 ] && [ -s "${output_prefix}-${read_type}.fastq.gz" ]; then
    end_time=\$(date +%s)
    duration=\$((end_time - start_time))
    final_size=\$(ls -lh "${output_prefix}-${read_type}.fastq.gz" | awk '{print \$5}')
    echo "Successfully merged ${read_type} files to ${output_prefix}-${read_type}.fastq.gz"
    echo "Final file size: \$final_size"
    echo "Execution time: \${duration} seconds"
    exit 0
else
    echo "Error: Merge failed or output file is empty"
    exit 1
fi
EOF

    # Make the script executable
    chmod +x "$slurm_script"
    
    # Submit the job and capture the job ID
    local job_output=$(sbatch "$slurm_script" 2>&1)
    local job_id=$(echo "$job_output" | grep -o '[0-9]\+')
    
    if [ -n "$job_id" ]; then
        echo "$job_id"
        return 0
    else
        echo "Failed to submit job for ${read_type} files: $job_output" >&2
        return 1
    fi
}

# Submit jobs for both R1 and R2
echo "Launching merge jobs for R1 and R2 files..."

echo -n "Submitting R1 job... "
r1_job_id=$(submit_merge_job "R1")
r1_status=$?
rm -f "${script_dir}/merge_fastq_R1.sh"  # Delete temporary R1 script

echo -n "Submitting R2 job... "
r2_job_id=$(submit_merge_job "R2")
r2_status=$?
rm -f "${script_dir}/merge_fastq_R2.sh"  # Delete temporary R2 script

echo

# Check if both jobs were submitted successfully
if [ $r1_status -eq 0 ] && [ $r2_status -eq 0 ]; then
    echo "Jobs submitted successfully:"
    echo "  R1 merge job ID: ${r1_job_id}"
    echo "  R2 merge job ID: ${r2_job_id}"
    echo
    echo "Monitor jobs with: squeue -j ${r1_job_id},${r2_job_id}"
    exit 0
else
    echo "Error: Failed to submit one or both jobs"
    exit 1
fi 