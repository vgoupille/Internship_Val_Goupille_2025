#!/bin/bash

# Setup script for conda environment in devcontainer
# This replaces the problematic conda env create command

set -e  # Exit on any error

echo "🚀 Starting conda environment setup..."

# Initialize conda
echo "📦 Initializing conda..."
conda init bash
source ~/.bashrc

# Create the environment with Python first
echo "🐍 Creating bioinfo_env environment with Python 3.11..."
conda create -n bioinfo_env python=3.11 -y

# Install core packages from conda-forge and bioconda
echo "📚 Installing core bioinformatics packages..."
conda install -n bioinfo_env -c conda-forge -c bioconda \
    pip=24.0 \
    ipykernel=6.29.5 \
    jupyterlab=4.4.1 \
    pandas=2.2.3 \
    matplotlib=3.10.1 \
    seaborn=0.13.2 \
    statsmodels=0.14.4 \
    numpy=2.2.5 \
    biopython=1.85 \
    scanpy=1.11.2 \
    scipy=1.15.3 \
    anndata=0.11.4 -y

# Install pip packages
echo "🔧 Installing pip packages..."
conda run -n bioinfo_env pip install \
    pydeseq2==0.5.1 \
    goatools==1.4.12 \
    rpy2==3.6.1

# Install Jupyter kernel
echo "🪐 Installing Jupyter kernel..."
conda run -n bioinfo_env python -m ipykernel install --user --name=bioinfo_env --display-name='Python (bioinfo_env)'

# Copy R profile
echo "📋 Copying R profile..."
if [ -f ".devcontainer/.Rprofile" ]; then
    cp .devcontainer/.Rprofile /home/vscode/.Rprofile
else
    echo "⚠️  Warning: .Rprofile not found, skipping..."
fi

echo "✅ Container setup completed successfully!"
echo "🎯 Environment 'bioinfo_env' is ready to use"