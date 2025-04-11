# XML to JSON Converter

This script processes all XML files in the specified directory and combines them into a single JSON file. Each XML file is converted to a JSON object with the filename as the key.

## Requirements

- Python 3.6+
- xmltodict package

## Installation

The required package can be installed using `uv`:

```bash
uv pip install xmltodict
```

## Usage

```bash
python src/xml_to_json.py [--input INPUT_DIR] [--output OUTPUT_FILE]
```

### Arguments

- `--input`, `-i`: Directory containing XML files (default: `data/xml`)
- `--output`, `-o`: Output JSON file path (default: `data/combined_reports.json`)

### Example

```bash
# Use default paths
python src/xml_to_json.py

# Specify custom paths
python src/xml_to_json.py --input /path/to/xml/files --output /path/to/output.json
```

## Output

The script will create a single JSON file with the following structure:

```json
{
  "filename1.xml": {
    // XML content converted to JSON
  },
  "filename2.xml": {
    // XML content converted to JSON
  },
  // ...
}
```

Each XML file is represented as a key-value pair in the JSON, where the key is the filename and the value is the XML content converted to JSON format.
