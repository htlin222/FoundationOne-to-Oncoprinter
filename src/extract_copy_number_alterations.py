#!/usr/bin/env python3
"""
Extract Copy Number Alterations from Foundation Medicine Reports

This script extracts copy number alteration information from the combined JSON file
of Foundation Medicine reports and saves it as a CSV file.
"""

import json
import csv
import os
import argparse
from typing import Dict, List, Any, Optional
from pathlib import Path


def extract_report_id(filename: str) -> str:
    """
    Extract the report ID from the filename.
    
    Args:
        filename: The XML filename
        
    Returns:
        The report ID (e.g., 'ORD-0893926-02')
    """
    # Remove file extension
    return os.path.splitext(filename)[0]


def extract_copy_number_alterations(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract all copy number alterations from all reports in the combined JSON data.
    
    Args:
        data: The combined JSON data containing all reports
        
    Returns:
        A list of dictionaries, each containing report_id and copy number alteration attributes
    """
    all_alterations = []
    
    for filename, report_data in data.items():
        report_id = extract_report_id(filename)
        
        # Navigate to the variant-report section
        try:
            variant_report = report_data.get('rr:ResultsReport', {}).get('rr:ResultsPayload', {}).get('variant-report', {})
            
            # Check if copy-number-alterations exists and is not empty
            copy_number_alterations = variant_report.get('copy-number-alterations', {}).get('copy-number-alteration', [])
            
            # If copy-number-alteration is a dictionary (single alteration), convert to list
            if isinstance(copy_number_alterations, dict):
                copy_number_alterations = [copy_number_alterations]
            
            # Process each copy number alteration
            for alteration in copy_number_alterations:
                # Create a copy of the alteration data
                alteration_data = alteration.copy()
                
                # Add report_id to the alteration data
                alteration_data['report_id'] = report_id
                
                # Add dna-evidence information if it exists
                if 'dna-evidence' in alteration:
                    dna_evidence = alteration['dna-evidence']
                    # If it's a dictionary, extract sample attribute
                    if isinstance(dna_evidence, dict) and '@sample' in dna_evidence:
                        alteration_data['dna_evidence_sample'] = dna_evidence['@sample']
                    # If it's a list, extract sample attributes from each item
                    elif isinstance(dna_evidence, list):
                        samples = [item.get('@sample', '') for item in dna_evidence if '@sample' in item]
                        alteration_data['dna_evidence_sample'] = ';'.join(samples)
                
                # Remove nested structures to flatten the data
                if 'dna-evidence' in alteration_data:
                    del alteration_data['dna-evidence']
                
                all_alterations.append(alteration_data)
        except (KeyError, AttributeError) as e:
            print(f"Error processing {filename}: {str(e)}")
            continue
    
    return all_alterations


def get_all_fields(alterations: List[Dict[str, Any]]) -> List[str]:
    """
    Get all unique fields from the alterations.
    
    Args:
        alterations: List of alteration dictionaries
        
    Returns:
        List of all unique field names
    """
    all_fields = set()
    
    for alteration in alterations:
        all_fields.update(alteration.keys())
    
    # Ensure report_id is the first field
    fields = list(all_fields)
    if 'report_id' in fields:
        fields.remove('report_id')
    
    return ['report_id'] + sorted(fields)


def save_to_csv(alterations: List[Dict[str, Any]], output_path: str) -> None:
    """
    Save the alterations data to a CSV file.
    
    Args:
        alterations: List of alteration dictionaries
        output_path: Path to save the CSV file
    """
    if not alterations:
        print("No copy number alterations found to save.")
        return
    
    # Get all unique fields
    fieldnames = get_all_fields(alterations)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for alteration in alterations:
            writer.writerow(alteration)
    
    print(f"Successfully saved {len(alterations)} copy number alterations to {output_path}")


def main():
    """Main function to parse arguments and run the extraction process."""
    parser = argparse.ArgumentParser(description='Extract copy number alterations from Foundation Medicine reports')
    parser.add_argument('--input', '-i', default='data/combined_reports.json',
                       help='Input JSON file path (default: data/combined_reports.json)')
    parser.add_argument('--output', '-o', default='data/copy_number_alterations.csv',
                       help='Output CSV file path (default: data/copy_number_alterations.csv)')
    
    args = parser.parse_args()
    
    # Ensure input file exists
    if not os.path.isfile(args.input):
        print(f"Error: Input file '{args.input}' does not exist")
        return
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Load the combined JSON data
    print(f"Loading data from {args.input}...")
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract copy number alterations
    print("Extracting copy number alterations...")
    alterations = extract_copy_number_alterations(data)
    
    # Save to CSV
    print(f"Saving {len(alterations)} alterations to {args.output}...")
    save_to_csv(alterations, args.output)


if __name__ == "__main__":
    main()
