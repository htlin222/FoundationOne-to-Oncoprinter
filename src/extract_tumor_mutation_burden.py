#!/usr/bin/env python3
"""
Extract Tumor Mutation Burden from Foundation Medicine Reports

This script extracts tumor mutation burden information from the combined JSON file
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
        The report ID (e.g., 'ORD-1668218-01')
    """
    # Remove file extension
    return os.path.splitext(filename)[0]


def extract_tumor_mutation_burden(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract tumor mutation burden information from all reports in the combined JSON data.
    
    Args:
        data: The combined JSON data containing all reports
        
    Returns:
        A list of dictionaries, each containing report_id and TMB data
    """
    all_tmb_data = []
    
    for filename, report_data in data.items():
        report_id = extract_report_id(filename)
        
        # Navigate to the biomarkers section
        try:
            variant_report = report_data.get('rr:ResultsReport', {}).get('rr:ResultsPayload', {}).get('variant-report', {})
            
            # Check if biomarkers exists
            biomarkers = variant_report.get('biomarkers', {})
            
            # Extract tumor mutation burden data
            tmb_data = biomarkers.get('tumor-mutation-burden', {})
            
            # If TMB data exists, create a record
            if tmb_data:
                # Create a dictionary for this record
                tmb_record = {
                    'report_id': report_id
                }
                
                # Add all attributes from the TMB data
                if isinstance(tmb_data, dict):
                    for key, value in tmb_data.items():
                        # Remove @ from attribute names
                        if key.startswith('@'):
                            tmb_record[key[1:]] = value
                        else:
                            tmb_record[key] = value
                
                all_tmb_data.append(tmb_record)
            
        except (KeyError, AttributeError) as e:
            print(f"Error processing {filename}: {str(e)}")
            continue
    
    return all_tmb_data


def get_all_fields(tmb_data: List[Dict[str, Any]]) -> List[str]:
    """
    Get all unique fields from the TMB data.
    
    Args:
        tmb_data: List of TMB dictionaries
        
    Returns:
        List of all unique field names
    """
    all_fields = set()
    
    for record in tmb_data:
        all_fields.update(record.keys())
    
    # Ensure report_id is the first field
    fields = list(all_fields)
    if 'report_id' in fields:
        fields.remove('report_id')
    
    return ['report_id'] + sorted(fields)


def save_to_csv(tmb_data: List[Dict[str, Any]], output_path: str) -> None:
    """
    Save the TMB data to a CSV file.
    
    Args:
        tmb_data: List of TMB dictionaries
        output_path: Path to save the CSV file
    """
    if not tmb_data:
        print("No tumor mutation burden data found to save.")
        return
    
    # Get all unique fields
    fieldnames = get_all_fields(tmb_data)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for record in tmb_data:
            writer.writerow(record)
    
    print(f"Successfully saved {len(tmb_data)} tumor mutation burden records to {output_path}")


def main():
    """Main function to parse arguments and run the extraction process."""
    parser = argparse.ArgumentParser(description='Extract tumor mutation burden data from Foundation Medicine reports')
    parser.add_argument('--input', '-i', default='data/combined_reports.json',
                       help='Input JSON file path (default: data/combined_reports.json)')
    parser.add_argument('--output', '-o', default='data/tumor_mutation_burden.csv',
                       help='Output CSV file path (default: data/tumor_mutation_burden.csv)')
    
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
    
    # Extract tumor mutation burden data
    print("Extracting tumor mutation burden data...")
    tmb_data = extract_tumor_mutation_burden(data)
    
    # Save to CSV
    print(f"Saving {len(tmb_data)} tumor mutation burden records to {args.output}...")
    save_to_csv(tmb_data, args.output)


if __name__ == "__main__":
    main()
