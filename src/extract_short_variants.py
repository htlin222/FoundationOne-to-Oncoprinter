#!/usr/bin/env python3
"""
Extract Short Variants from Foundation Medicine Reports

This script extracts short variant information from the combined JSON file
of Foundation Medicine reports and saves it as a CSV file.
"""

import argparse
from typing import Dict, List, Any
from common import extract_report_id, save_to_csv, setup_extraction, process_dna_evidence, handle_missing_data


def extract_short_variants(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract all short variants from all reports in the combined JSON data.
    
    Args:
        data: The combined JSON data containing all reports
        
    Returns:
        A list of dictionaries, each containing report_id and short variant attributes
    """
    all_variants = []
    
    for filename, report_data in data.items():
        report_id = extract_report_id(filename)
        
        # Navigate to the variant-report section
        try:
            variant_report = report_data.get('rr:ResultsReport', {}).get('rr:ResultsPayload', {}).get('variant-report', {})
            
            # Check if short-variants exists and is not empty
            short_variants = variant_report.get('short-variants', {}).get('short-variant', [])
            
            # If short-variant is a dictionary (single variant), convert to list
            if isinstance(short_variants, dict):
                short_variants = [short_variants]
            
            # Process each short variant
            for variant in short_variants:
                # Create a copy of the variant data
                variant_data = variant.copy()
                
                # Add report_id to the variant data
                variant_data['report_id'] = report_id
                
                # Process DNA evidence
                process_dna_evidence(variant, variant_data)
                
                all_variants.append(variant_data)
        except (KeyError, AttributeError) as e:
            handle_missing_data(filename, "short variants", e)
            continue
    
    return all_variants


def main():
    """Main function to parse arguments and run the extraction process."""
    parser = argparse.ArgumentParser(description='Extract short variants from Foundation Medicine reports')
    parser.add_argument('--input', '-i', default='data/combined_reports.json',
                       help='Input JSON file path (default: data/combined_reports.json)')
    parser.add_argument('--output', '-o', default='data/short_variants.csv',
                       help='Output CSV file path (default: data/short_variants.csv)')
    
    args = parser.parse_args()
    
    # Setup and load data
    data = setup_extraction(args.input, args.output)
    if not data:
        return
    
    # Extract short variants
    print("Extracting short variants...")
    variants = extract_short_variants(data)
    
    # Save to CSV
    print(f"Saving short variants to {args.output}...")
    save_to_csv(variants, args.output, "variants")


if __name__ == "__main__":
    main()
