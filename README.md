# FoundationOne Genomic Report Processing

A comprehensive toolkit for processing, analyzing, and visualizing genetic data from genomic reports.

## Overview

This project provides a pipeline for extracting, processing, and analyzing genetic data from genomic reports. It converts XML-based genomic reports into structured formats (JSON, CSV, Excel) and provides tools for data visualization using Oncoprinter.

## Features

- **Data Extraction**: Convert XML genomic reports to JSON and extract various genetic alterations
- **Data Processing**: Process and analyze genetic data including:
  - Short variants (mutations)
  - Copy number alterations (CNAs)
  - Rearrangements (fusions)
  - Biomarkers (MSI, TMB)
  - Patient medical information
- **Data Visualization**: Generate Oncoprinter-compatible files for visualization
  - Complete dataset visualization
  - Diagnosis-specific filtering
  - Gene-specific mutation mapping
  - Clinical data integration
- **Gene Analysis**: Extract and count gene occurrences across the dataset

## Installation

### Prerequisites

- Python 3.6+
- [uv](https://github.com/astral-sh/uv) - Modern Python package manager
- Make (for using the Makefile)

### Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd genetic_workshop
   ```

2. Create and activate a virtual environment with uv:
   ```
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies using uv:
   ```
   uv sync
   ```

   If you don't have a pyproject.toml file yet, create one:
   ```
   # Create a basic pyproject.toml
   cat > pyproject.toml << EOL
   [project]
   name = "genetic-workshop"
   version = "0.1.0"
   description = "A toolkit for processing, analyzing, and visualizing genetic data"
   readme = "README.md"
   requires-python = ">=3.6"
   dependencies = [
       "pandas",
       "numpy",
       "openpyxl",
       "lxml"
   ]

   [build-system]
   requires = ["hatchling"]
   build-backend = "hatchling.build"
   EOL

   # Install dependencies
   uv sync
   ```

4. Run a command in the project environment:
   ```
   uv run -- python src/all_genes.py
   ```

## Usage

The project uses a Makefile to orchestrate the data processing pipeline. Here are the main commands:

### Basic Pipeline

```bash
# Run the complete pipeline
make all

# Convert XML files to JSON
make xml2json

# Extract all genomic alterations and biomarkers
make extract-all

# Combine all CSV files into a single Excel file
make combine-to-excel

# Clean generated files
make clean
```

### Data Extraction

```bash
# Extract short variants
make extract-variants

# Extract copy number alterations
make extract-cna

# Extract rearrangements
make extract-rearrangements

# Extract biomarkers (MSI and TMB)
make extract-biomarkers

# Extract patient medical information
make extract-pmi

# Extract gene names and counts
make extract-gene-counts
```

### Oncoprinter Integration

```bash
# Convert data to Oncoprinter format
make to-oncoprinter

# Convert data to Oncoprinter format filtered by diagnosis
make to-oncoprinter-dx DX=lung

# Convert data for a specific gene to Oncoprinter format
make to-oncoprinter-gene GENE=TP53

# Convert patient data to Oncoprinter clinical data format
make to-oncoprinter-clinical
```

## File Structure

- `src/`: Source code for data processing
  - `xml_to_json.py`: Converts XML reports to JSON
  - `extract_*.py`: Extracts specific data types from JSON
  - `to_oncoprinter_*.py`: Converts data to Oncoprinter format
  - `all_genes.py`: Extracts and counts gene occurrences
  - `combine_csv_to_excel.py`: Combines CSV files into Excel
- `data/`: Data directory
  - `xml/`: Input XML files
  - `*.csv`: Extracted data in CSV format
  - `*.json`: Processed data in JSON format
  - `*.xlsx`: Combined data in Excel format
  - `oncoprinter/`: Oncoprinter-compatible output files

## Gene Analysis

The project includes a tool for analyzing gene frequencies in the dataset. The most common genes found include:
- TP53 (127 occurrences)
- APC (59 occurrences)
- MLL2 (58 occurrences)
- EGFR (48 occurrences)
- ARID1A/PIK3CA (39 occurrences each)

In total, 370 unique genes with 2999 total occurrences were identified in the dataset.

## Oncoprinter Integration

The project generates files compatible with [Oncoprinter](https://www.cbioportal.org/oncoprinter), a tool for visualizing genomic alterations across samples. The generated files can be directly uploaded to Oncoprinter for visualization.

### Supported Oncoprinter Features

- **Complete Dataset**: Visualize all genomic alterations
- **Diagnosis Filtering**: Filter data by diagnosis (e.g., lung, breast)
- **Gene-Specific Analysis**: Analyze mutations for specific genes
- **Clinical Data Integration**: Include clinical data in visualizations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.