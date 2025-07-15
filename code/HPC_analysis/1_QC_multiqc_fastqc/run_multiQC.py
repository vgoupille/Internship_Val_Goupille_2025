import os
import subprocess
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
import argparse
import yaml
import sys



# FastQC and MultiQC are command-line tools, not Python modules
# We use subprocess to run them as if we were typing in the terminal

def load_samples(yaml_file, data_type=None):
    """
    Load sample information from YAML file
    Args:
        yaml_file (str): Path to YAML file
        data_type (str): Type of data to process (unzipped, trimmed_simple, trimmed_complex, subsampled)
    Returns:
        dict: Dictionary of samples with their file paths
    """
    if not os.path.exists(yaml_file):
        raise FileNotFoundError(f"YAML file not found: {yaml_file}")
        
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)
    
    if 'samples' not in data:
        raise ValueError("YAML file must contain a 'samples' key")
    
    samples = {}
    for sample_name, reads in data['samples'].items():
        if data_type:
            # Filter by data type if specified
            if all(data_type in reads[read_type] for read_type in ['R1', 'R2']):
                samples[sample_name] = {
                    'R1': reads['R1'][data_type],
                    'R2': reads['R2'][data_type]
                }
        else:
            # Use all data types
            samples[sample_name] = {
                'R1': reads['R1'],
                'R2': reads['R2']
            }
    
    if not samples:
        raise ValueError(f"No samples found for data_type: {data_type}")
        
    return samples

def run_fastqc(args_tuple):
    """
    Run FastQC on a single file
    Args:
        args_tuple (tuple): (fastq_file, output_dir)
    Returns:
        str: Basename of processed file
    """
    fastq_file, output_dir = args_tuple
    if not os.path.exists(fastq_file):
        raise FileNotFoundError(f"FastQ file not found: {fastq_file}")
        
    print(f"\nProcessing {fastq_file}...")
    subprocess.run(
        [
            "fastqc",
            fastq_file,
            "-o",
            output_dir,
            "-t",
            str(multiprocessing.cpu_count() // 2),
        ],
        check=True  # Raise exception if command fails
    )
    return os.path.basename(fastq_file)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run FastQC and MultiQC analysis on FASTQ files')
    parser.add_argument('--read_type', choices=['R1', 'R2'], required=True,
                      help='Specify whether to process R1 or R2 files')
    parser.add_argument('--data_type', required=True,
                      help='Specify the type of data to process (must exist in YAML file)')
    parser.add_argument('--yaml_file', required=True,
                      help='Path to YAML file containing sample information')
    parser.add_argument('--output_dir', required=True,
                      help='Output directory for results')
    args = parser.parse_args()

    try:
        # Load sample information
        samples = load_samples(args.yaml_file, args.data_type)
        
        # Create output directory
        os.makedirs(args.output_dir, exist_ok=True)

        # Prepare files to process
        files_to_process = []
        for sample_info in samples.values():
            if args.data_type:
                # Single path per read type
                files_to_process.append(sample_info[args.read_type])
            else:
                # Multiple paths per read type (all data types)
                for data_type, path in sample_info[args.read_type].items():
                    files_to_process.append(path)

        if not files_to_process:
            raise ValueError(f"No files found to process for read_type={args.read_type} and data_type={args.data_type}")

        # Prepare arguments for parallel processing
        process_args = [(f, args.output_dir) for f in files_to_process]

        # Get number of available CPUs
        num_cpus = multiprocessing.cpu_count()
        print(f"Using {num_cpus} CPUs for parallel processing")

        # Process files
        print(f"\nProcessing {args.read_type} files...")
        with ProcessPoolExecutor(max_workers=num_cpus) as executor:
            list(tqdm(
                executor.map(run_fastqc, process_args),
                total=len(files_to_process),
                desc=f"Running FastQC on {args.read_type} files",
                unit="file"
            ))

        print(f"\nFastQC analysis completed. Running MultiQC on {args.read_type} results...")
        subprocess.run(
            [
                "multiqc",
                args.output_dir,
                "-o",
                args.output_dir,
            ],
            check=True  # Raise exception if command fails
        )

        print(f"Analysis complete! Results are in {args.output_dir} directory.")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
