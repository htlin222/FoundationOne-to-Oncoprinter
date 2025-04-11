#!/usr/bin/env python3
"""
Extract Rearrangements from Foundation Medicine Reports

This script extracts rearrangement information from the combined JSON file
of Foundation Medicine reports and saves it as a CSV file.
"""

import argparse
from typing import Dict, List, Any
from common import extract_report_id, save_to_csv, setup_extraction, process_dna_evidence, handle_missing_data


def extract_rearrangements(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract all rearrangements from all reports in the combined JSON data.
    
    Args:
        data: The combined JSON data containing all reports
        
    Returns:
        A list of dictionaries, each containing report_id and rearrangement attributes
    """
    all_rearrangements = []
    
    for filename, report_data in data.items():
        report_id = extract_report_id(filename)
        
        # Navigate to the variant-report section
        try:
            variant_report = report_data.get('rr:ResultsReport', {}).get('rr:ResultsPayload', {}).get('variant-report', {})
            
            # Check if rearrangements exists and is not empty
            rearrangements = variant_report.get('rearrangements', {}).get('rearrangement', [])
            
            # If rearrangement is a dictionary (single rearrangement), convert to list
            if isinstance(rearrangements, dict):
                rearrangements = [rearrangements]
            
            # Process each rearrangement
            for rearrangement in rearrangements:
                # Create a copy of the rearrangement data
                rearrangement_data = rearrangement.copy()
                
                # Add report_id to the rearrangement data
                rearrangement_data['report_id'] = report_id
                
                # Process DNA evidence
                process_dna_evidence(rearrangement, rearrangement_data)
                
                all_rearrangements.append(rearrangement_data)
        except (KeyError, AttributeError) as e:
            handle_missing_data(filename, "rearrangements", e)
            continue
    
    return all_rearrangements


def main():
    """Main function to parse arguments and run the extraction process."""
    parser = argparse.ArgumentParser(description='Extract rearrangements from Foundation Medicine reports')
    parser.add_argument('--input', '-i', default='data/combined_reports.json',
                       help='Input JSON file path (default: data/combined_reports.json)')
    parser.add_argument('--output', '-o', default='data/rearrangements.csv',
                       help='Output CSV file path (default: data/rearrangements.csv)')
    
    args = parser.parse_args()
    
    # Setup and load data
    data = setup_extraction(args.input, args.output)
    if not data:
        return
    
    # Extract rearrangements
    print("Extracting rearrangements...")
    rearrangements = extract_rearrangements(data)
    
    # Save to CSV
    print(f"Saving rearrangements to {args.output}...")
    save_to_csv(rearrangements, args.output, "rearrangements")


if __name__ == "__main__":
    main()
