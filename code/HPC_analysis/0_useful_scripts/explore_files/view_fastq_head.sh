#!/bin/bash

# Script to view the first lines of a gzipped FASTQ file
# Usage: ./view_fastq_head.sh <fastq.gz_file> [number_of_lines]

# Check if a file is provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <fastq.gz_file> [number_of_lines]"
    echo "Default number of lines: 4 (one complete FASTQ record)"
    exit 1
fi

# Set the input file
input_file=$1

# Set number of lines (default: 4 for one complete FASTQ record)
num_lines=${2:-4}

# Check if file exists
if [ ! -f "$input_file" ]; then
    echo "Error: File '$input_file' not found"
    exit 1
fi

# Check if file is gzipped
if [[ ! "$input_file" =~ \.gz$ ]]; then
    echo "Error: File must be gzipped (.gz)"
    exit 1
fi

# Display the first n lines
echo "Showing first $num_lines lines of $input_file:"
echo "----------------------------------------"
zcat "$input_file" | head -n "$num_lines" 