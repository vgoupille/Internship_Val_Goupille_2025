#!/bin/bash
#SBATCH --job-name=STARsolo_Pipeline
#SBATCH --mail-type=ALL
#SBATCH --mail-user=valentin.goupille@univ-rennes.fr
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=600G
#SBATCH --time=48:00:00
#SBATCH --output=/projects/microsplit/logs/starsolo_pipeline_%j.out
#SBATCH --error=/projects/microsplit/logs/starsolo_pipeline_%j.err

# === STARsolo Pipeline Master Script ===
# This script runs the complete STARsolo analysis pipeline for microSPLIT scRNA-seq data

# Create logs directory if it doesn't exist
LOGS_DIR="/projects/microsplit/logs"
mkdir -p "$LOGS_DIR" || {
    echo "ERROR: Failed to create logs directory: $LOGS_DIR"
    exit 1
}

# Load configuration
echo "$(date) - Loading configuration..."

# Use CONFIG_FILE from environment if available
if [ -n "$CONFIG_FILE" ] && [ -f "$CONFIG_FILE" ]; then
    echo "Using configuration file from environment: $CONFIG_FILE"
    source "$CONFIG_FILE"
else
    echo "ERROR: CONFIG_FILE environment variable not set or file not found!"
    echo "Please ensure the configuration file is properly passed to the script."
    exit 1
fi

# Verify BASE_PATH exists
if [ ! -d "$BASE_PATH" ]; then
    echo "ERROR: BASE_PATH directory does not exist: $BASE_PATH"
    echo "Please check the BASE_PATH variable in your config.sh file"
    exit 1
fi

# Create BASE_DIR early to avoid issues with conda environment
echo "$(date) - Creating base directory structure..."
mkdir -p "$BASE_DIR"
echo "Base directory created or already exists: $BASE_DIR"


echo "Using SLURM parameters provided at submission time."

# Function to check if a script completed successfully
check_script() {
    if [ $? -ne 0 ]; then
        echo "ERROR: $1 failed! Pipeline stopped."
        exit 1
    else
        echo "$1 completed successfully."
    fi
}

# Step 0: Source Conda environment script
echo "$(date) - Setting up Conda environment..."
if [ -f "$CONDA_INIT_SCRIPT" ]; then
    echo "Sourcing Conda initialization script from: $CONDA_INIT_SCRIPT"
    . "$CONDA_INIT_SCRIPT"
else
    echo "ERROR: Conda initialization script not found at $CONDA_INIT_SCRIPT"
    echo "Please check the CONDA_INIT_SCRIPT variable in your config.sh file"
    exit 1
fi

# Step 1: Activate STARsolo environment (should be created beforehand with create_env_STARsolo.sh)
echo "$(date) - Step 1: Activating STARsolo environment..."

# Check if the environment exists
if ! conda env list | grep -q "${CONDA_ENV_PATH##*/}"; then
    echo "ERROR: STARsolo environment does not exist at $CONDA_ENV_PATH"
    echo "Please run create_env_STARsolo.sh first to create the environment"
    echo "Command: sbatch create_env_STARsolo.sh"
    exit 1
fi

# Activate the environment
echo "Activating conda environment..."
conda activate "$CONDA_ENV_PATH" || { 
    echo "ERROR: Failed to activate conda environment at $CONDA_ENV_PATH"
    echo "The environment may be corrupted. Please recreate it with create_env_STARsolo.sh"
    exit 1
}

# Verify that required tools are available
echo "Verifying required tools availability..."
MISSING_TOOLS=0

# Check each required tool
for cmd in STAR gffread cufflinks; do
    if ! command -v $cmd &> /dev/null; then
        echo "ERROR: $cmd command not found in the activated environment"
        MISSING_TOOLS=$((MISSING_TOOLS+1))
    else
        echo "✓ $cmd is available"
    fi
done

if [ $MISSING_TOOLS -gt 0 ]; then
    echo "ERROR: $MISSING_TOOLS required tools are missing from the environment"
    echo "Please recreate the environment with create_env_STARsolo.sh"
    exit 1
fi

echo "Conda environment setup completed successfully."

# Step 1.5: Validate input files
echo "$(date) - Step 1.5: Validating input files..."

# Check FASTQ files
echo "Checking FASTQ files..."
for file_var in SOURCE_FASTQ_R1 SOURCE_FASTQ_R2; do
    file_path="${SOURCE_FASTQ}/${!file_var}"
    if [ ! -f "$file_path" ]; then
        echo "ERROR: FASTQ file not found: $file_path"
        echo "Please check the SOURCE_FASTQ and $file_var variables in config.sh"
        exit 1
    else
        echo "✓ Found: $file_path"
        # Check if file is readable and not empty
        if [ ! -r "$file_path" ] || [ ! -s "$file_path" ]; then
            echo "ERROR: FASTQ file is not readable or empty: $file_path"
            exit 1
        fi
    fi
done

# Check barcode files
echo "Checking barcode files..."
for file_var in SOURCE_BARCODE_R1 SOURCE_BARCODE_R2 SOURCE_BARCODE_R3; do
    file_path="${SOURCE_BARCODES}/${!file_var}"
    if [ ! -f "$file_path" ]; then
        echo "ERROR: Barcode file not found: $file_path"
        echo "Please check the SOURCE_BARCODES and $file_var variables in config.sh"
        exit 1
    else
        echo "✓ Found: $file_path"
        # Check if file is readable and not empty
        if [ ! -r "$file_path" ] || [ ! -s "$file_path" ]; then
            echo "ERROR: Barcode file is not readable or empty: $file_path"
            exit 1
        fi
    fi
done

# Check genome reference file
echo "Checking genome reference file..."
genome_ref_path="${SOURCE_GENOME_REF}/${SOURCE_GENOME_FASTA}"
if [ ! -f "$genome_ref_path" ]; then
    echo "ERROR: Genome reference file not found: $genome_ref_path"
    echo "Please check the SOURCE_GENOME_REF and SOURCE_GENOME_FASTA variables in config.sh"
    exit 1
else
    echo "✓ Found: $genome_ref_path"
    if [ ! -r "$genome_ref_path" ] || [ ! -s "$genome_ref_path" ]; then
        echo "ERROR: Genome reference file is not readable or empty: $genome_ref_path"
        exit 1
    fi
fi

# Check genome annotation file
echo "Checking genome annotation file..."
genome_annotation_path="${SOURCE_GENOME_ANNOTATION}/${SOURCE_GENOME_GFF}"
if [ ! -f "$genome_annotation_path" ]; then
    echo "ERROR: Genome annotation file not found: $genome_annotation_path"
    echo "Please check the SOURCE_GENOME_ANNOTATION and SOURCE_GENOME_GFF variables in config.sh"
    exit 1
else
    echo "✓ Found: $genome_annotation_path"
    if [ ! -r "$genome_annotation_path" ] || [ ! -s "$genome_annotation_path" ]; then
        echo "ERROR: Genome annotation file is not readable or empty: $genome_annotation_path"
        exit 1
    fi
fi

echo "All input files validated successfully."

# Step 2: Create directory structure and symbolic links
echo "$(date) - Step 2: Setting up directory structure and links..."

# Create directory structure
mkdir -p "$FASTQ_DIR" "$BARCODE_DIR" "$GENOME_REF_DIR" "$GENOME_ANNOTATION_DIR"

# Create symbolic links for FASTQ files
echo "Creating symbolic links for FASTQ files..."
ln -sf "$(realpath "$SOURCE_FASTQ/$SOURCE_FASTQ_R1")" "$FASTQ_DIR/$TARGET_FASTQ_R1"
ln -sf "$(realpath "$SOURCE_FASTQ/$SOURCE_FASTQ_R2")" "$FASTQ_DIR/$TARGET_FASTQ_R2"

# Create symbolic links for barcode files
echo "Creating symbolic links for barcode files..."
ln -sf "$(realpath "$SOURCE_BARCODES/$SOURCE_BARCODE_R1")" "$BARCODE_DIR/$TARGET_BARCODE_R1"
ln -sf "$(realpath "$SOURCE_BARCODES/$SOURCE_BARCODE_R2")" "$BARCODE_DIR/$TARGET_BARCODE_R2"
ln -sf "$(realpath "$SOURCE_BARCODES/$SOURCE_BARCODE_R3")" "$BARCODE_DIR/$TARGET_BARCODE_R3"

# Verify barcode links
echo "Verifying barcode links..."
for i in 1 2 3; do
    source_var="SOURCE_BARCODE_R$i"
    target_var="TARGET_BARCODE_R$i"
    source_file="${SOURCE_BARCODES}/${!source_var}"
    target_file="${BARCODE_DIR}/${!target_var}"
    if [ ! -L "$target_file" ] || [ ! -e "$target_file" ]; then
        echo "ERROR: Failed to create or verify barcode link: $target_file -> $source_file"
        echo "Source file exists: $([ -f "$source_file" ] && echo "Yes" || echo "No")"
        echo "Target directory exists: $([ -d "$BARCODE_DIR" ] && echo "Yes" || echo "No")"
        echo "Target directory permissions: $(ls -ld "$BARCODE_DIR")"
        echo "Source file permissions: $(ls -l "$source_file" 2>/dev/null || echo "File not found")"
        exit 1
    fi
    echo "Verified barcode link: $target_file -> $source_file"
done

# Create symbolic links for genome reference files
echo "Creating symbolic links for genome reference files..."
ln -sf "$(realpath "$SOURCE_GENOME_REF/$SOURCE_GENOME_FASTA")" "$GENOME_REF_DIR/$TARGET_GENOME_FASTA"

# Create symbolic links for genome annotation files
echo "Creating symbolic links for genome annotation files..."
ln -sf "$(realpath "$SOURCE_GENOME_ANNOTATION/$SOURCE_GENOME_GFF")" "$GENOME_ANNOTATION_DIR/$TARGET_GENOME_GFF"

check_script "Directory and link setup"

# Step 3: Run STARsolo analysis
echo "$(date) - Step 3: Running STARsolo analysis..."

# Create output directories
mkdir -p "$GENERAL_OUTPUT_DIR" "$GENOME_DIR" "$OUTPUT_STARSOLO_DIR"

# Activate STARsolo environment
conda activate "$CONDA_ENV_PATH"

# Function to check command success
check_success() {
    if [ $? -ne 0 ]; then
        echo "ERROR: Command failed - $1"
        exit 1
    fi
}

# Convert GFF3 to GTF Format
echo "$(date) - Converting GFF3 to GTF..."

# Ensure conda environment is still activated
if ! command -v gffread &> /dev/null; then
    echo "WARNING: gffread command not found. Trying to reactivate conda environment..."
    conda activate "$CONDA_ENV_PATH" || { 
        echo "ERROR: Failed to reactivate conda environment and gffread is not available."
        echo "Please ensure that gffread is installed in your conda environment."
        exit 1
    }
    
    # Check again after reactivation
    if ! command -v gffread &> /dev/null; then
        echo "ERROR: gffread command still not available after reactivating conda environment."
        echo "Please install gffread: conda install -c bioconda gffread"
        exit 1
    fi
fi

# Path for the output GTF file
GTF_FILE="${GENOME_ANNOTATION_DIR}/${TARGET_GENOME_GFF%.gff}.gtf"
echo "Converting GFF to GTF: ${GENOME_ANNOTATION_DIR}/${TARGET_GENOME_GFF} -> $GTF_FILE"

# Run conversion with -h option if -v doesn't work
gffread "${GENOME_ANNOTATION_DIR}/${TARGET_GENOME_GFF}" -T -o "$GTF_FILE"
if [ $? -ne 0 ]; then
    echo "ERROR: GFF3 to GTF conversion failed"
    exit 1
else
    echo "GFF3 to GTF conversion completed successfully"
fi

# Check that the GTF file was created
if [ ! -f "$GTF_FILE" ]; then
    echo "ERROR: GTF file was not created: $GTF_FILE"
    exit 1
fi

# GTF File Correction
echo "$(date) - Correcting GTF file..."
GTF_FIXED="${GTF_FILE%.gtf}_fixed.gtf"
awk 'BEGIN{OFS=FS="\t"} {if ($3 == "CDS" || $3 == "transcript") $3 = "exon"; print}' "$GTF_FILE" > "$GTF_FIXED"
check_success "GTF file correction"

# Genome Index Generation
echo "$(date) - Generating genome index..."
STAR --runMode genomeGenerate \
    --runThreadN "$THREADS" \
    --genomeDir "$GENOME_DIR" \
    --genomeSAindexNbases 10 \
    --genomeFastaFiles "${GENOME_REF_DIR}/${TARGET_GENOME_FASTA}" \
    --sjdbGTFfile "$GTF_FIXED"
check_success "Genome index generation"

# STARsolo Alignment and Quantification
echo "$(date) - Executing STARsolo alignment..."
STAR --genomeDir "$GENOME_DIR" \
    --runThreadN "$THREADS" \
    --readFilesIn "${FASTQ_DIR}/${TARGET_FASTQ_R1}" "${FASTQ_DIR}/${TARGET_FASTQ_R2}" \
    --readFilesCommand gunzip -c \
    --soloType CB_UMI_Complex \
    --soloCBposition 0_10_0_17 0_48_0_55 0_78_0_85 \
    --soloUMIposition 0_0_0_9 \
    --soloCBwhitelist "${BARCODE_DIR}/barcode_round3.txt" "${BARCODE_DIR}/barcode_round2.txt" "${BARCODE_DIR}/barcode_round1.txt" \
    --soloCBmatchWLtype 1MM \
    --soloUMIdedup 1MM_All \
    --soloFeatures Gene GeneFull \
    --soloMultiMappers Uniform \
    --outFilterScoreMinOverLread 0 \
    --outFilterMatchNminOverLread 0 \
    --outFilterMatchNmin 50 \
    --alignSJDBoverhangMin 1000 \
    --alignSJoverhangMin 1000 \
    --outSAMtype BAM Unsorted \
    --outFileNamePrefix "${OUTPUT_STARSOLO_DIR}/"
check_success "STARsolo alignment and quantification"

# Output Validation
echo "$(date) - Verifying output files..."

# Check for log file
if [ ! -f "${OUTPUT_STARSOLO_DIR}/Log.final.out" ]; then
    echo "ERROR: Log file not found!"
    exit 1
fi

# Check for matrix files in both Gene and GeneFull features
GENE_MTX="${OUTPUT_STARSOLO_DIR}/Solo.out/Gene/raw/UniqueAndMult-Uniform.mtx"
GENEFULL_MTX="${OUTPUT_STARSOLO_DIR}/Solo.out/GeneFull/raw/UniqueAndMult-Uniform.mtx"
BARCODE_FILE="${OUTPUT_STARSOLO_DIR}/Solo.out/GeneFull/raw/barcodes.tsv"
FEATURE_FILE="${OUTPUT_STARSOLO_DIR}/Solo.out/GeneFull/raw/features.tsv"

MISSING_FILES=0
for file in "$GENE_MTX" "$GENEFULL_MTX" "$BARCODE_FILE" "$FEATURE_FILE"; do
    if [ ! -f "$file" ]; then
        echo "WARNING: Missing output file: $file"
        MISSING_FILES=$((MISSING_FILES+1))
    fi
done

if [ $MISSING_FILES -gt 0 ]; then
    echo "WARNING: $MISSING_FILES output files are missing!"
else
    echo "Analysis completed successfully!"
    echo "Key files for downstream analysis:"
    echo "- $BARCODE_FILE"
    echo "- $FEATURE_FILE"
    echo "- $GENEFULL_MTX"
    echo "- $GENE_MTX"
    
    # Display detailed alignment statistics
    echo -e "\nAlignment statistics:"
    echo "-----------------------"
    echo "$(grep "Number of input reads" "${OUTPUT_STARSOLO_DIR}/Log.final.out")"
    echo "$(grep "Average input read length" "${OUTPUT_STARSOLO_DIR}/Log.final.out")"
    echo "$(grep "Uniquely mapped reads number" "${OUTPUT_STARSOLO_DIR}/Log.final.out")"
    echo "$(grep "Uniquely mapped reads %" "${OUTPUT_STARSOLO_DIR}/Log.final.out")"
    echo "$(grep "Number of reads mapped to multiple loci" "${OUTPUT_STARSOLO_DIR}/Log.final.out")"
    echo "$(grep "% of reads mapped to multiple loci" "${OUTPUT_STARSOLO_DIR}/Log.final.out")"
    echo "$(grep "Number of reads unmapped: other" "${OUTPUT_STARSOLO_DIR}/Log.final.out")"
    echo "$(grep "% of reads unmapped: other" "${OUTPUT_STARSOLO_DIR}/Log.final.out")"
    echo "$(grep "Mismatch rate per base, %" "${OUTPUT_STARSOLO_DIR}/Log.final.out")"
fi

echo "$(date) - Pipeline completed!"

# Suppression de la partie de nettoyage du fichier de configuration
# Le fichier de configuration sera conservé dans le répertoire de sortie

exit 0 