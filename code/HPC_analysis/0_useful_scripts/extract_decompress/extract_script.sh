#!/bin/bash
#SBATCH --job-name=extract_nts412
#SBATCH --output=extract_nts412_%j.log
#SBATCH --error=extract_nts412_%j.err
#SBATCH --constraint avx2
#SBATCH --time=24:00:00
#SBATCH --mem=4G

# Define paths
ZIP_FILE="data/raw_data/NTS-412_fastq.zip"
EXTRACT_DIR="data/processed_data/unzipped_data/NTS-412_fastq"

# Check if ZIP file exists
if [ ! -f "$ZIP_FILE" ]; then
    echo "Error: ZIP file not found at $ZIP_FILE"
    exit 1
fi


# Create extraction directory
echo "Creating extraction directory..."
mkdir -p $EXTRACT_DIR

# Extract the ZIP file
echo "Extracting NTS-412_fastq.zip..."
unzip -q $ZIP_FILE -d $EXTRACT_DIR

if [ $? -eq 0 ]; then
    echo "Extraction completed successfully"
    echo "Files are available in: $EXTRACT_DIR"
    
    # Show final space usage
    echo "Final space usage:"
    du -sh $EXTRACT_DIR
    
    # Optional: remove the ZIP file after successful extraction
    # echo "Removing ZIP file..."
    # rm $ZIP_FILE
else
    echo "Extraction failed"
    exit 1
fi 