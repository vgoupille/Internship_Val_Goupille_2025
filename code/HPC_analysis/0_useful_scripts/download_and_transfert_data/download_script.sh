#!/bin/bash
#SBATCH --job-name=download_nts412
#SBATCH --output=download_nts412_%j.log
#SBATCH --error=download_nts412_%j.err
#SBATCH --constraint avx2
#SBATCH --time=24:00:00
#SBATCH --mem=4G

# Create a temporary directory for the download
TEMP_DIR="/projects/microsplit/data/temp_download"
mkdir -p $TEMP_DIR
cd $TEMP_DIR

# Download the file using wget with progress monitoring and retry mechanism
echo "Starting download of NTS-412_fastq.zip..."
MAX_RETRIES=3
RETRY_COUNT=0
SUCCESS=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ] && [ "$SUCCESS" = false ]; do
    wget --progress=bar:force:noscroll \
         --retry-connrefused \
         --tries=0 \
         --timeout=300 \
         --waitretry=5 \
         --no-check-certificate \
         https://partage.os-bird.glicid.fr/index.php/s/dQsQgDp2F67SPez/download/NTS-412_fastq.zip
    
    if [ $? -eq 0 ]; then
        SUCCESS=true
        echo "Download completed successfully"
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            echo "Download failed, retrying in 5 seconds... (Attempt $RETRY_COUNT of $MAX_RETRIES)"
            sleep 5
        else
            echo "Download failed after $MAX_RETRIES attempts"
            exit 1
        fi
    fi
done

if [ "$SUCCESS" = true ]; then
    # Move the file to the final destination
    mv NTS-412_fastq.zip /projects/microsplit/data/
    echo "File moved to /projects/microsplit/data/"
fi

# Clean up
rm -rf $TEMP_DIR