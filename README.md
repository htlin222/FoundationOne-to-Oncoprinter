# FoundationOne NGS to Oncoprinter Converter

A comprehensive toolkit for converting FoundationOne Next Generation Sequencing (NGS) data into formats compatible with the cBioPortal Oncoprinter visualization tool.

## Overview

This project provides a pipeline to process FoundationOne genomic reports in XML format and convert them into the Oncoprinter validated data format. The toolkit extracts various types of genomic alterations (short variants, copy number alterations, rearrangements) and biomarkers (microsatellite instability, tumor mutation burden), along with patient clinical information, and transforms them into formats suitable for visualization with the cBioPortal Oncoprinter tool.

## Features

- **XML to JSON Conversion**: Converts FoundationOne XML reports to a structured JSON format
- **Data Extraction**: Extracts multiple types of genomic data:
  - Short variants (mutations)
  - Copy number alterations
  - Gene rearrangements
  - Microsatellite instability (MSI)
  - Tumor mutation burden (TMB)
  - Patient medical information
- **Oncoprinter Format Conversion**:
  - Converts genomic data to Oncoprinter validated format
  - Generates clinical data in Oncoprinter format
  - Supports filtering by diagnosis
  - Provides gene-specific mutation mapping
- **Analysis Tools**:
  - Extracts and counts gene frequencies
  - Consolidates data into Excel format for easy viewing
  - Calculates mutation spectrum profiles

## Prerequisites

- Python 3.6+
- Required Python packages (can be installed via `pip`):
  - pandas
  - numpy
  - argparse
  - pathlib

## Directory Structure

```
genetic_workshop/
├── data/                      # Data directory
│   ├── xml/                   # Input XML files from FoundationOne
│   ├── oncoprinter/           # Output files for Oncoprinter
│   └── *.csv                  # Extracted data in CSV format
├── src/                       # Source code
│   ├── xml_to_json.py         # Converts XML to JSON
│   ├── extract_*.py           # Data extraction scripts
│   ├── to_oncoprinter_*.py    # Oncoprinter format conversion scripts
│   ├── all_genes.py           # Gene frequency analysis
│   └── combine_csv_to_excel.py # Combines CSVs to Excel
└── Makefile                   # Build automation
```

## Usage

The project uses a Makefile to automate the workflow. Here are the main commands:

### Basic Pipeline

```bash
# Run the complete pipeline
make all

# Convert XML files to JSON
make xml2json

# Extract all genomic data
make extract-all

# Combine all CSV files into Excel
make combine-to-excel
```

### Oncoprinter Conversion

```bash
# Convert all data to Oncoprinter format
make to-oncoprinter

# Convert patient data to Oncoprinter clinical data format
make to-oncoprinter-clinical

# Convert data filtered by diagnosis
make to-oncoprinter-dx DX=lung

# Convert data for a specific gene
make to-oncoprinter-gene GENE=TP53
```

### Gene Analysis

```bash
# Extract gene names and count frequencies
make extract-gene-counts
```

### Cleanup

```bash
# Remove generated files
make clean
```

## Data Conversion Process

1. **XML to JSON**: The pipeline starts by converting FoundationOne XML reports to a structured JSON format.
2. **Data Extraction**: Various scripts extract specific genomic alterations and patient information from the JSON.
3. **Oncoprinter Format Conversion**: The extracted data is then converted to formats compatible with Oncoprinter:
   - Genomic alterations are formatted according to Oncoprinter validated format
   - Clinical data is formatted with appropriate track types (number, string, lognumber)
   - Mutation data includes genomic coordinates for mutation mapping

## Oncoprinter Data Format

### Genomic Data Format
```
Sample Gene Alteration Type
```

Example:
```
SAMPLE1 TP53 R273H MISSENSE
SAMPLE2 EGFR T790M MISSENSE_DRIVER
```

### Clinical Data Format
```
Sample Age(number) Cancer_Type(string) Mutation_Count(lognumber) Mutation_Spectrum(C>A/C>G/C>T/T>A/T>C/T>G)
```

## Gene Frequency Analysis

The `all_genes.py` script extracts gene names from the Oncoprinter data and counts their frequencies. The most common genes in the dataset include:

- TP53 (127 occurrences)
- APC (59 occurrences)
- MLL2 (58 occurrences)
- EGFR (48 occurrences)
- ARID1A/PIK3CA (39 occurrences each)

In total, the analysis found 370 unique genes with 2,999 total occurrences across all samples.

## Visualization with Oncoprinter

After converting the data, you can visualize it using the cBioPortal Oncoprinter tool:

1. Go to [cBioPortal Oncoprinter](https://www.cbioportal.org/oncoprinter)
2. Upload the generated files from the `data/oncoprinter/` directory
3. Configure visualization settings as needed
4. Generate and explore the visualization

## Contributing

Contributions to improve the toolkit are welcome. Please feel free to submit pull requests or open issues to suggest improvements or report bugs.

## License

This project is available for use under the MIT license.
