#!/usr/bin/env python3
"""
XML to JSON Converter for Foundation Medicine XML Reports

This script processes all XML files in the specified directory and combines them
into a single JSON file. Each XML file is converted to a JSON object with the
filename as the key.
"""

import os
import json
import xmltodict
from pathlib import Path
import argparse
from typing import Dict, Any


def convert_xml_to_dict(xml_path: str) -> Dict[str, Any]:
    """
    Convert an XML file to a Python dictionary.
    
    Args:
        xml_path: Path to the XML file
        
    Returns:
        Dictionary representation of the XML
    """
    try:
        with open(xml_path, 'r', encoding='utf-8') as file:
            xml_content = file.read()
        return xmltodict.parse(xml_content)
    except Exception as e:
        print(f"Error processing {xml_path}: {str(e)}")
        return {"error": str(e)}


def process_directory(directory_path: str, output_path: str) -> None:
    """
    Process all XML files in the specified directory and save as a single JSON file.
    
    Args:
        directory_path: Path to directory containing XML files
        output_path: Path where the output JSON file should be saved
    """
    directory = Path(directory_path)
    result = {}
    
    # Get all XML files in the directory
    xml_files = list(directory.glob("*.xml"))
    total_files = len(xml_files)
    
    print(f"Found {total_files} XML files to process")
    
    # Process each XML file
    for i, xml_file in enumerate(xml_files, 1):
        file_name = xml_file.name
        print(f"Processing file {i}/{total_files}: {file_name}")
        
        # Convert XML to dictionary and add to result with filename as key
        result[file_name] = convert_xml_to_dict(str(xml_file))
    
    # Save the combined result as JSON
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(result, json_file, indent=2)
    
    print(f"Successfully processed {total_files} files")
    print(f"Combined JSON saved to: {output_path}")


def main():
    """Main function to parse arguments and run the conversion process."""
    parser = argparse.ArgumentParser(description='Convert XML files to a combined JSON file')
    parser.add_argument('--input', '-i', default='data/xml',
                       help='Directory containing XML files (default: data/xml)')
    parser.add_argument('--output', '-o', default='data/combined_reports.json',
                       help='Output JSON file path (default: data/combined_reports.json)')
    
    args = parser.parse_args()
    
    # Ensure input directory exists
    if not os.path.isdir(args.input):
        print(f"Error: Input directory '{args.input}' does not exist")
        return
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Process the files
    process_directory(args.input, args.output)


if __name__ == "__main__":
    main()
