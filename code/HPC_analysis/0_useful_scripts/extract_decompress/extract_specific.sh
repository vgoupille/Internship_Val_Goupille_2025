#!/bin/bash
#SBATCH --job-name=extract_specific
#SBATCH --output=extract_specific_%j.log
#SBATCH --error=extract_specific_%j.err
#SBATCH --constraint avx2
#SBATCH --time=24:00:00
#SBATCH --mem=4G

# Define paths
ZIP_FILE="data/raw_data/NTS-412_fastq.zip"
EXTRACT_DIR="data/processed_data/unzipped_data_specific/NTS-412_fastq"


# Check if ZIP file exists
if [ ! -f "$ZIP_FILE" ]; then
    echo "Error: ZIP file not found at $ZIP_FILE"
    exit 1
fi

# Check if argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: sbatch $0 <choice>"
    echo "Choices:"
    echo "1) BC_0076 (R1: 42.8GB, R2: 18.6GB)"
    echo "2) BC_0077 (R1: 21.3GB, R2: 9.6GB)"
    echo "3) BC_0079 (R1: 25.2GB, R2: 11.3GB)"
    echo "4) BC_0080 (R1: 26.6GB, R2: 11.6GB)"
    exit 1
fi

# Process the choice
case $1 in
    1)
        echo "Extraction des fichiers BC_0076..."
        FILES_TO_EXTRACT=("fastq/BC_0076_R1.fastq.gz" "fastq/BC_0076_R2.fastq.gz")
        ;;
    2)
        echo "Extraction des fichiers BC_0077..."
        FILES_TO_EXTRACT=("fastq/BC_0077_R1.fastq.gz" "fastq/BC_0077_R2.fastq.gz")
        ;;
    3)
        echo "Extraction des fichiers BC_0079..."
        FILES_TO_EXTRACT=("fastq/BC_0079_R1.fastq.gz" "fastq/BC_0079_R2.fastq.gz")
        ;;
    4)
        echo "Extraction des fichiers BC_0080..."
        FILES_TO_EXTRACT=("fastq/BC_0080_R1.fastq.gz" "fastq/BC_0080_R2.fastq.gz")
        ;;
    *)
        echo "Choix invalide. Veuillez choisir entre 1 et 4."
        exit 1
        ;;
esac

# Create extraction directory
echo "Creating extraction directory..."
mkdir -p $EXTRACT_DIR

# Extract selected files
echo "Extracting selected files..."
unzip -q "$ZIP_FILE" "${FILES_TO_EXTRACT[@]}" -d $EXTRACT_DIR

if [ $? -eq 0 ]; then
    echo "Extraction completed successfully"
    echo "Files are available in: $EXTRACT_DIR/fastq/"
    
    # Show extracted files and their sizes
    echo -e "\nExtracted files:"
    for file in "${FILES_TO_EXTRACT[@]}"; do
        ls -lh "$EXTRACT_DIR/$file"
    done
    
    # Show space usage
    echo -e "\nSpace usage:"
    du -sh $EXTRACT_DIR
else
    echo "Extraction failed"
    exit 1
fi 