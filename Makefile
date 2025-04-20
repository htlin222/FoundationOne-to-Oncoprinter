# Makefile for genetic workshop

# Variables
PYTHON = python
SRC_DIR = src
DATA_DIR = data
XML_DIR = $(DATA_DIR)/xml
OUTPUT_JSON = $(DATA_DIR)/combined_reports.json
OUTPUT_VARIANTS_CSV = $(DATA_DIR)/short_variants.csv
OUTPUT_CNA_CSV = $(DATA_DIR)/copy_number_alterations.csv
OUTPUT_REARR_CSV = $(DATA_DIR)/rearrangements.csv
OUTPUT_MSI_CSV = $(DATA_DIR)/microsatellite_instability.csv
OUTPUT_TMB_CSV = $(DATA_DIR)/tumor_mutation_burden.csv
OUTPUT_PMI_CSV = $(DATA_DIR)/patient_medical_info.csv
OUTPUT_EXCEL = $(DATA_DIR)/combined_reports.xlsx
OUTPUT_GENE_COUNTS = $(DATA_DIR)/gene_counts.csv
ONCOPRINTER_DIR = $(DATA_DIR)/oncoprinter
ONCOPRINTER_ALL = $(ONCOPRINTER_DIR)/all.txt
ONCOPRINTER_CLINICAL = $(ONCOPRINTER_DIR)/clinical_data.txt
OUTPUT_CHORD_DIAGRAM = $(DATA_DIR)/gene_comutation_chord.png

# Default target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  all                    - Run the complete pipeline: extract all data and combine to Excel"
	@echo "  xml2json               - Convert XML files to a combined JSON file"
	@echo "  extract-variants       - Extract short variants from JSON to CSV"
	@echo "  extract-cna            - Extract copy number alterations from JSON to CSV"
	@echo "  extract-rearrangements - Extract rearrangements from JSON to CSV"
	@echo "  extract-msi            - Extract microsatellite instability from JSON to CSV"
	@echo "  extract-tmb            - Extract tumor mutation burden from JSON to CSV"
	@echo "  extract-pmi            - Extract patient medical information from JSON to CSV"
	@echo "  extract-biomarkers     - Extract both biomarker types (MSI and TMB)"
	@echo "  extract-all            - Extract all genomic alterations and biomarkers"
	@echo "  combine-to-excel       - Combine all CSV files into a single Excel file"
	@echo "  extract-gene-counts    - Extract gene names and counts from oncoprinter/all.txt"
	@echo "  to-oncoprinter         - Convert data to OncoprinterValidated format"
	@echo "  to-oncoprinter-dx      - Convert data to OncoprinterValidated format filtered by diagnosis"
	@echo "  to-oncoprinter-gene    - Convert data for a specific gene to OncoprinterValidated format"
	@echo "  to-oncoprinter-clinical - Convert patient data to oncoprinter clinical data format"
	@echo "  gene-comutation-chord  - Generate chord diagram of gene co-mutations"
	@echo "  env                    - Create a Python virtual environment using uv"
	@echo "  clean                  - Remove generated files"

# Complete pipeline target
.PHONY: all
all: combine-to-excel
	@echo "Complete pipeline executed successfully."

# Convert XML files to JSON
.PHONY: xml2json
xml2json:
	@echo "Converting XML files to JSON..."
	$(PYTHON) $(SRC_DIR)/xml_to_json.py --input $(XML_DIR) --output $(OUTPUT_JSON)
	@echo "Conversion complete. Output saved to $(OUTPUT_JSON)"

# Extract short variants to CSV
.PHONY: extract-variants
extract-variants: xml2json
	@echo "Extracting short variants to CSV..."
	$(PYTHON) $(SRC_DIR)/extract_short_variants.py --input $(OUTPUT_JSON) --output $(OUTPUT_VARIANTS_CSV)
	@echo "Extraction complete. Output saved to $(OUTPUT_VARIANTS_CSV)"

# Extract copy number alterations to CSV
.PHONY: extract-cna
extract-cna: xml2json
	@echo "Extracting copy number alterations to CSV..."
	$(PYTHON) $(SRC_DIR)/extract_copy_number_alterations.py --input $(OUTPUT_JSON) --output $(OUTPUT_CNA_CSV)
	@echo "Extraction complete. Output saved to $(OUTPUT_CNA_CSV)"

# Extract rearrangements to CSV
.PHONY: extract-rearrangements
extract-rearrangements: xml2json
	@echo "Extracting rearrangements to CSV..."
	$(PYTHON) $(SRC_DIR)/extract_rearrangements.py --input $(OUTPUT_JSON) --output $(OUTPUT_REARR_CSV)
	@echo "Extraction complete. Output saved to $(OUTPUT_REARR_CSV)"

# Extract microsatellite instability to CSV
.PHONY: extract-msi
extract-msi: xml2json
	@echo "Extracting microsatellite instability to CSV..."
	$(PYTHON) $(SRC_DIR)/extract_microsatellite_instability.py --input $(OUTPUT_JSON) --output $(OUTPUT_MSI_CSV)
	@echo "Extraction complete. Output saved to $(OUTPUT_MSI_CSV)"

# Extract tumor mutation burden to CSV
.PHONY: extract-tmb
extract-tmb: xml2json
	@echo "Extracting tumor mutation burden to CSV..."
	$(PYTHON) $(SRC_DIR)/extract_tumor_mutation_burden.py --input $(OUTPUT_JSON) --output $(OUTPUT_TMB_CSV)
	@echo "Extraction complete. Output saved to $(OUTPUT_TMB_CSV)"

# Extract patient medical information to CSV
.PHONY: extract-pmi
extract-pmi: xml2json
	@echo "Extracting patient medical information to CSV..."
	$(PYTHON) $(SRC_DIR)/extract_patient_medical_info.py --input $(OUTPUT_JSON) --output $(OUTPUT_PMI_CSV)
	@echo "Extraction complete. Output saved to $(OUTPUT_PMI_CSV)"

# Extract gene names and counts from oncoprinter/all.txt
.PHONY: extract-gene-counts
extract-gene-counts:
	@echo "Extracting gene names and counts..."
	$(PYTHON) $(SRC_DIR)/all_genes.py --output $(OUTPUT_GENE_COUNTS)
	@echo "Extraction complete. Output saved to $(OUTPUT_GENE_COUNTS)"

# Convert data to OncoprinterValidated format
.PHONY: to-oncoprinter
to-oncoprinter: extract-all
	@echo "Converting data to OncoprinterValidated format..."
	mkdir -p $(ONCOPRINTER_DIR)
	$(PYTHON) $(SRC_DIR)/to_oncoprinter_validated_dataset.py --data_dir $(DATA_DIR) --output $(ONCOPRINTER_ALL)
	@echo "Conversion complete. Output saved to $(ONCOPRINTER_ALL)"

# Convert patient data to oncoprinter clinical data format
.PHONY: to-oncoprinter-clinical
to-oncoprinter-clinical: extract-variants extract-pmi
	@echo "Converting patient data to oncoprinter clinical data format..."
	mkdir -p $(ONCOPRINTER_DIR)
	$(PYTHON) $(SRC_DIR)/to_oncoprinter_clinical_data.py --data-dir $(DATA_DIR) --output-file $(ONCOPRINTER_CLINICAL)
	@echo "Conversion complete. Output saved to $(ONCOPRINTER_CLINICAL)"

# Convert data to OncoprinterValidated format filtered by diagnosis
.PHONY: to-oncoprinter-dx
to-oncoprinter-dx: extract-all
	@echo "Usage: make to-oncoprinter-dx DX=diagnosis [OUTPUT=output_filename]"
	@if [ -z "$(DX)" ]; then \
		echo "Error: DX parameter is required. Example: make to-oncoprinter-dx DX=lung"; \
		exit 1; \
	fi
	@echo "Converting data to OncoprinterValidated format filtered by diagnosis '$(DX)'..."
	mkdir -p $(ONCOPRINTER_DIR)
	$(PYTHON) $(SRC_DIR)/to_oncoprinter_filtered_by_dx.py --dx "$(DX)" --data-dir $(DATA_DIR) $(if $(OUTPUT),--output-file "$(OUTPUT)")
	@echo "Conversion complete."

# Convert data for a specific gene to OncoprinterValidated format
.PHONY: to-oncoprinter-gene
to-oncoprinter-gene: extract-variants
	@echo "Usage: make to-oncoprinter-gene GENE=gene_name [ONEFILE=1]"
	@echo "       For multiple genes: make to-oncoprinter-gene GENE=gene1,gene2,gene3 [ONEFILE=1]"
	@if [ -z "$(GENE)" ]; then \
		echo "Error: GENE parameter is required. Examples:"; \
		echo "  make to-oncoprinter-gene GENE=TP53"; \
		echo "  make to-oncoprinter-gene GENE=TP53,EGFR,KRAS"; \
		echo "  make to-oncoprinter-gene GENE=TP53,EGFR,KRAS ONEFILE=1"; \
		exit 1; \
	fi
	@echo "Converting data for gene(s) '$(GENE)' to OncoprinterValidated format..."
	mkdir -p $(ONCOPRINTER_DIR)
	$(PYTHON) $(SRC_DIR)/to_oncoprinter_mutation_map_validated_dataset.py --gene "$(GENE)" --data_dir $(DATA_DIR) $(if $(ONEFILE),--onefile)
	@if [ -n "$(ONEFILE)" ]; then \
		echo "Conversion complete. Output saved to a single combined file in $(ONCOPRINTER_DIR)/"; \
	else \
		echo "Conversion complete. Output saved to $(ONCOPRINTER_DIR)/<gene>.txt for each gene."; \
	fi

# Extract all biomarker data
.PHONY: extract-biomarkers
extract-biomarkers: extract-msi extract-tmb
	@echo "All biomarker extractions complete."

# Extract all data types
.PHONY: extract-all
extract-all: extract-variants extract-cna extract-rearrangements extract-biomarkers extract-pmi extract-gene-counts
	@echo "All extractions complete."

# Combine all CSV files into a single Excel file
.PHONY: combine-to-excel
combine-to-excel: extract-all
	@echo "Combining all CSV files into a single Excel file..."
	$(PYTHON) $(SRC_DIR)/combine_csv_to_excel.py --input $(DATA_DIR) --output $(OUTPUT_EXCEL)
	@echo "Combination complete. Output saved to $(OUTPUT_EXCEL)"

# Generate chord diagram of gene co-mutations
.PHONY: gene-comutation-chord
gene-comutation-chord:
	@echo "Generating gene co-mutation chord diagram..."
	mkdir -p $(dir $(OUTPUT_CHORD_DIAGRAM))
	$(PYTHON) $(SRC_DIR)/gene_comutation_chord.py --input $(ONCOPRINTER_ALL) --output $(OUTPUT_CHORD_DIAGRAM) --min-count 3 --top-genes 20
	@echo "Chord diagram generated. Output saved to $(OUTPUT_CHORD_DIAGRAM)"

# Create a Python virtual environment using uv
.PHONY: env
env:
	@echo "Creating Python virtual environment using uv..."
	uv venv
	@echo "Virtual environment created at .venv"
	@echo ""
	@echo "Installing dependencies..."
	uv pip install --python .venv/bin/python -r requirements.txt
	@echo ""
	@echo "Dependencies installed successfully!"
	@echo ""
	@echo "====================================================================="
	@echo "IMPORTANT: The virtual environment has been created, but NOT activated"
	@echo "To activate it, run this command:"
	@echo ""
	@echo "  source .venv/bin/activate"
	@echo ""
	@echo "Alternatively, you can use this one-liner to create and activate:"
	@echo ""
	@echo "  make env && source .venv/bin/activate"
	@echo "====================================================================="

# Clean generated files
.PHONY: clean
clean:
	@echo "Removing generated files..."
	rm -f $(OUTPUT_JSON) $(OUTPUT_VARIANTS_CSV) $(OUTPUT_CNA_CSV) $(OUTPUT_REARR_CSV) $(OUTPUT_MSI_CSV) $(OUTPUT_TMB_CSV) $(OUTPUT_PMI_CSV) $(OUTPUT_EXCEL) $(OUTPUT_GENE_COUNTS) $(OUTPUT_CHORD_DIAGRAM)
	rm -rf $(ONCOPRINTER_DIR)
	@echo "Clean complete."
