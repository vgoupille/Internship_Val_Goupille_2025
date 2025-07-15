# Random FASTQ Reads Subsampling

This script allows creating random subsamples of reads from FASTQ files, using various configurable parameters.

## Description

The `run_subsampling_random.sh` script uses `seqtk` to create random subsamples of reads from FASTQ files. It can process multiple samples in parallel and generate different subsample sizes.

## Prerequisites

- SLURM environment
- Conda
- Samples YAML file (`data/info/samples/samples_all.yaml`)
- Input FASTQ files (defined in YAML)

## Default Parameters

- **Input type**: `unzipped` (untreated FASTQ files)
- **Seed**: 200
- **Number of reads**: 5000, 10000, 1000000
- **Samples**: all samples found in the YAML file

## Output File Structure

```
data/raw_data/subsampled_data/random_reads/
├── BC_XXXX_seed200_reads5000/
│   ├── BC_XXXX_R1_subsampled.fastq
│   └── BC_XXXX_R2_subsampled.fastq
├── BC_XXXX_seed200_reads10000/
│   ├── BC_XXXX_R1_subsampled.fastq
│   └── BC_XXXX_R2_subsampled.fastq
└── BC_XXXX_seed200_reads1000000/
    ├── BC_XXXX_R1_subsampled.fastq
    └── BC_XXXX_R2_subsampled.fastq
```

## Usage

### Basic Command

```bash
sbatch run_subsampling_random.sh
```

### Available Options

```bash
sbatch run_subsampling_random.sh [options]

Options:
  --samples-yaml PATH    Path to samples YAML file
                        (default: data/info/samples/samples_all.yaml)
  
  --output-dir PATH     Output directory
                        (default: data/raw_data/subsampled_data/random_reads)
  
  --input-type TYPE     Input type: unzipped, trimmed_simple, trimmed_complex
                        (default: unzipped)
  
  --seeds SEEDS         Comma-separated list of seeds
                        (default: 200)
  
  --num-reads READS     Comma-separated list of read numbers
                        (default: 5000,10000,1000000)
  
  --samples SAMPLES     Comma-separated list of samples to process
                        (default: all samples)
```

### Usage Examples

1. **Process all samples with default parameters**:
```bash
sbatch run_subsampling_random.sh
```

2. **Process specific samples**:
```bash
sbatch run_subsampling_random.sh --samples BC_0076,BC_0077
```

3. **Use custom parameters**:
```bash
sbatch run_subsampling_random.sh \
    --samples BC_0076 \
    --input-type trimmed_simple \
    --seeds 200,300 \
    --num-reads 1000,5000
```

4. **Change input type**:
```bash
sbatch run_subsampling_random.sh --input-type trimmed_complex
```

## Notes

- The script automatically creates the required conda environment
- Output files are in uncompressed FASTQ format
- Logs are saved in the `logs/` directory
- The script checks for input file existence before processing

## Dependencies

- seqtk (installed via conda environment)
- yq (for YAML parsing)

## Author

Valentin Goupille (valentin.goupille@univ-rennes.fr) 