# Containerized Development Environment for Bioinformatics Analysis

This folder contains the configuration for a containerized development environment optimized for bioinformatics analysis, particularly tailored for single-cell data analysis.

## 🚀 Usage

### Prerequisites
- Docker installed on your system
- Visual Studio Code with the "Dev Containers" extension

### Getting Started
1. Open the project in VSCode
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
3. Type "Dev Containers: Reopen in Container"
4. Select the option and wait for the container to build

## 📁 Contents

### `devcontainer.json`
Main container configuration including:
- **Base image**: Ubuntu 22.04
- **R 4.5.0** with bioinformatics packages:
  - `Seurat` (v5.3.0) - Single-cell analysis
  - `anndata` (v0.8.0) - Annotated data structures
  - `tidyverse` (v2.0.0) - R ecosystem for data science
  - `reticulate` (v1.42.0) - R-Python interface
  - `scCustomize` (v3.0.1) - Single-cell analysis customization
  - `vegan` (v2.7-1) - Ecological analyses
  - `BiocManager` - Bioconductor package manager
  - `glmGamPoi` - Generalized linear models for single-cell data
- **Quarto CLI** - Reproducible documentation
- **Miniforge** - Conda package manager
- **VSCode extensions** optimized for R, Python, and Jupyter

### `environment.yml`
Conda environment `bioinfo_env` with:
- **Python 3.11** and data science ecosystem
- **Bioinformatics packages**:
  - `scanpy` (v1.11.2) - Single-cell analysis in Python
  - `biopython` (v1.85) - Bioinformatics tools
  - `pandas`, `matplotlib`, `seaborn` - Data manipulation and visualization
  - `statsmodels`, `numpy`, `scipy` - Statistical analysis
  - `anndata` (v0.11.4) - Data structures
- **Specialized packages**:
  - `pydeseq2` - Differential expression analysis
  - `goatools` - Functional enrichment
  - `rpy2` - Python-R interface

### `.Rprofile`
R configuration for:
- **VSCode integration** - R interface optimization in VSCode
- **httpgd graphics** - Display graphics in browser
- **reticulate configuration** - Using conda environment from R

## 🔧 Features

### Supported languages and tools
- **R** - Statistical analysis and visualization
- **Python** - Bioinformatics analysis and machine learning
- **Jupyter** - Interactive notebooks
- **Quarto** - Documentation and reproducible reports

### R-Python Integration
The environment enables seamless integration between R and Python via:
- `reticulate` (R to Python)
- `rpy2` (Python to R)
- Shared conda environment

### Jupyter Integration
Environments are **directly available** in Jupyter:
- **Conda environment** (`bioinfo_env`): Accessible as Python kernel in Jupyter
- **R environment**: Available via R kernel in Jupyter
- **Easy switching** between Python and R in the same notebook
- **Variable sharing** between environments via `reticulate` and `rpy2`

### Supported analyses
- **Single-cell RNA-seq** - Scanpy, Seurat, anndata
- **Differential expression analysis** - pydeseq2, glmGamPoi
- **Functional enrichment** - goatools
- **Ecological analyses** - vegan
- **Visualizations** - ggplot2, matplotlib, seaborn

## ⚠️ Important Note

This container is configured in a **simplified** manner for basic bioinformatics analyses. It is fully **customizable** according to your specific needs. Feel free to modify it to add additional packages, change versions, or adapt the configuration to your project.

## 🛠️ Customization

### Adding R packages
Modify the `r-packages` section in `devcontainer.json`:
```json
"packages": "languageserver@0.3.16, my_new_package"
```

### Adding Python packages
Add packages in `environment.yml`:
```yaml
dependencies:
  - new_package=version
```

### Modifying VSCode extensions
Add or remove extensions in the `extensions` section of `devcontainer.json`.

## 📊 Typical Use Cases

This environment is particularly suitable for:
- Single-cell RNA-seq data analysis
- Multi-omics data integration
- Differential expression analyses
- Scientific visualizations
- Reproducible reports with Quarto

## 🔍 Troubleshooting

### Container won't start
- Check that Docker is running
- Ensure you have sufficient disk space
- Review container build logs

### Issues with reticulate
- Restart R session
- Check that conda environment is activated
- Use `reticulate::py_config()` for diagnostics

### R graphics not displaying
- Check that httpgd is installed and loaded
- Restart R session
- Ensure port is not blocked

## 📝 Notes
- The container automatically installs the conda environment at startup
- R configuration is copied to the user's home directory
- Packages are installed from specific mirrors to ensure reproducibility 