#!/usr/bin/env python3
"""
Extract Microsatellite Instability from Foundation Medicine Reports

This script extracts microsatellite instability information from the combined JSON file
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


def extract_microsatellite_instability(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract microsatellite instability information from all reports in the combined JSON data.
    
    Args:
        data: The combined JSON data containing all reports
        
    Returns:
        A list of dictionaries, each containing report_id and MSI status
    """
    all_msi_data = []
    
    for filename, report_data in data.items():
        report_id = extract_report_id(filename)
        
        # Navigate to the biomarkers section
        try:
            variant_report = report_data.get('rr:ResultsReport', {}).get('rr:ResultsPayload', {}).get('variant-report', {})
            
            # Check if biomarkers exists
            biomarkers = variant_report.get('biomarkers', {})
            
            # Extract microsatellite instability data
            msi_data = biomarkers.get('microsatellite-instability', {})
            
            # If MSI data exists, create a record
            if msi_data:
                # Create a dictionary for this record
                msi_record = {
                    'report_id': report_id
                }
                
                # Add all attributes from the MSI data
                if isinstance(msi_data, dict):
                    for key, value in msi_data.items():
                        # Remove @ from attribute names
                        if key.startswith('@'):
                            msi_record[key[1:]] = value
                        else:
                            msi_record[key] = value
                
                all_msi_data.append(msi_record)
            
        except (KeyError, AttributeError) as e:
            print(f"Error processing {filename}: {str(e)}")
            continue
    
    return all_msi_data


def get_all_fields(msi_data: List[Dict[str, Any]]) -> List[str]:
    """
    Get all unique fields from the MSI data.
    
    Args:
        msi_data: List of MSI dictionaries
        
    Returns:
        List of all unique field names
    """
    all_fields = set()
    
    for record in msi_data:
        all_fields.update(record.keys())
    
    # Ensure report_id is the first field
    fields = list(all_fields)
    if 'report_id' in fields:
        fields.remove('report_id')
    
    return ['report_id'] + sorted(fields)


def save_to_csv(msi_data: List[Dict[str, Any]], output_path: str) -> None:
    """
    Save the MSI data to a CSV file.
    
    Args:
        msi_data: List of MSI dictionaries
        output_path: Path to save the CSV file
    """
    if not msi_data:
        print("No microsatellite instability data found to save.")
        return
    
    # Get all unique fields
    fieldnames = get_all_fields(msi_data)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for record in msi_data:
            writer.writerow(record)
    
    print(f"Successfully saved {len(msi_data)} microsatellite instability records to {output_path}")


def main():
    """Main function to parse arguments and run the extraction process."""
    parser = argparse.ArgumentParser(description='Extract microsatellite instability data from Foundation Medicine reports')
    parser.add_argument('--input', '-i', default='data/combined_reports.json',
                       help='Input JSON file path (default: data/combined_reports.json)')
    parser.add_argument('--output', '-o', default='data/microsatellite_instability.csv',
                       help='Output CSV file path (default: data/microsatellite_instability.csv)')
    
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
    
    # Extract microsatellite instability data
    print("Extracting microsatellite instability data...")
    msi_data = extract_microsatellite_instability(data)
    
    # Save to CSV
    print(f"Saving {len(msi_data)} microsatellite instability records to {args.output}...")
    save_to_csv(msi_data, args.output)


if __name__ == "__main__":
    main()
