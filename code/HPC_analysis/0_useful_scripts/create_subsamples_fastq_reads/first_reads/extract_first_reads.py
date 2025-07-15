#!/usr/bin/env python3
"""
Script to extract N reads from paired-end FASTQ files.
Maintains the pairing between R1 and R2 reads.
"""

import yaml
from Bio import SeqIO
import gzip
from pathlib import Path
import sys
import argparse

def extract_first_reads(yaml_file: str, sample_name: str, max_reads: int, output_dir: str) -> None:
    """
    Extract first N reads from both R1 and R2 files while maintaining pairing.
    
    Args:
        yaml_file (str): Path to the samples YAML file
        sample_name (str): Name of the sample to process
        max_reads (int): Number of reads to extract
        output_dir (str): Directory where to save the output files
    """
    # Load sample information
    with open(yaml_file, 'r') as file:
        samples = yaml.safe_load(file)
    
    # Get paths for R1 and R2 (using unzipped files)
    try:
        r1_path = samples['samples'][sample_name]['R1']['unzipped']
        r2_path = samples['samples'][sample_name]['R2']['unzipped']
    except KeyError as e:
        print(f"Error: Could not find paths for sample {sample_name} in YAML file")
        print(f"Missing key: {e}")
        return
    
    # Create output paths
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    r1_output = output_dir / f"{sample_name}_R1_first{max_reads}.fastq.gz"
    r2_output = output_dir / f"{sample_name}_R2_first{max_reads}.fastq.gz"
    
    # Check if input files exist
    if not Path(r1_path).exists() or not Path(r2_path).exists():
        print(f"Error: Input files not found:")
        print(f"R1: {r1_path} - {'exists' if Path(r1_path).exists() else 'missing'}")
        print(f"R2: {r2_path} - {'exists' if Path(r2_path).exists() else 'missing'}")
        return
    
    print(f"\nProcessing sample {sample_name}")
    print(f"Extracting first {max_reads} reads from both R1 and R2")
    print(f"Input files:")
    print(f"R1: {r1_path}")
    print(f"R2: {r2_path}")
    print("-" * 50)
    
    # Process R1
    print(f"\nProcessing R1 file...")
    with gzip.open(r1_path, "rt") as handle_in, gzip.open(r1_output, "wt") as handle_out:
        for i, record in enumerate(SeqIO.parse(handle_in, "fastq")):
            if i >= max_reads:
                break
            SeqIO.write(record, handle_out, "fastq")
            if (i + 1) % 1000 == 0:  # Show progress every 1000 reads
                print(f"Processed {i + 1} R1 reads...")
    
    # Process R2
    print(f"\nProcessing R2 file...")
    with gzip.open(r2_path, "rt") as handle_in, gzip.open(r2_output, "wt") as handle_out:
        for i, record in enumerate(SeqIO.parse(handle_in, "fastq")):
            if i >= max_reads:
                break
            SeqIO.write(record, handle_out, "fastq")
            if (i + 1) % 1000 == 0:  # Show progress every 1000 reads
                print(f"Processed {i + 1} R2 reads...")
    
    print("\nExtraction complete!")
    print(f"Output files:")
    print(f"R1: {r1_output}")
    print(f"R2: {r2_output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract N reads from paired-end FASTQ files')
    parser.add_argument('--reads', type=int, required=True,
                      help='Number of reads to extract')
    parser.add_argument('--sample', type=str, required=True,
                      help='Sample name to process')
    parser.add_argument('--yaml', type=str, required=True,
                      help='Path to samples YAML file')
    parser.add_argument('--output', type=str, required=True,
                      help='Output directory for the extracted reads')
    
    args = parser.parse_args()
    extract_first_reads(args.yaml, args.sample, args.reads, args.output) 