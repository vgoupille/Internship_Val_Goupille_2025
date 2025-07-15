#!/bin/bash

# Define path to ZIP file
ZIP_FILE="/scratch/$USER/NTS-412_fastq.zip"

# Check if ZIP file exists
if [ ! -f "$ZIP_FILE" ]; then
    echo "Error: ZIP file not found at $ZIP_FILE"
    exit 1
fi

# Get ZIP file size
echo "ZIP file size:"
du -h "$ZIP_FILE"

# List contents with sizes
echo -e "\nContents of the ZIP file:"
unzip -l "$ZIP_FILE" | head -n 1  # Show header
unzip -l "$ZIP_FILE" | tail -n +4 | sort -k 4  # Sort by filename

# Count number of files
echo -e "\nNumber of files:"
unzip -l "$ZIP_FILE" | tail -n +4 | wc -l

# Show total size of contents
echo -e "\nTotal size of contents:"
unzip -l "$ZIP_FILE" | tail -n +4 | awk '{sum += $1} END {print sum/1024/1024/1024 " GB"}' 