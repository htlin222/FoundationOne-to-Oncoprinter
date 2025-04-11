#!/usr/bin/env python3
"""
Extract Patient Medical Information (PMI) from Foundation Medicine Reports

This script extracts PMI information from the combined JSON file
of Foundation Medicine reports and saves it as a CSV file.
"""

import json
import argparse
from typing import Dict, List, Any
from common import extract_report_id, save_to_csv, setup_extraction, handle_missing_data


def extract_patient_medical_info(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract Patient Medical Information (PMI) from all reports in the combined JSON data.
    
    Args:
        data: The combined JSON data containing all reports
        
    Returns:
        A list of dictionaries, each containing report_id and PMI data
    """
    all_pmi_data = []
    
    for filename, report_data in data.items():
        report_id = extract_report_id(filename)
        
        # Navigate to the PMI section - it's in the FinalReport section
        try:
            pmi_data = report_data.get('rr:ResultsReport', {}).get('rr:ResultsPayload', {}).get('FinalReport', {}).get('PMI', {})
            
            # If PMI data exists, create a record
            if pmi_data:
                # Create a dictionary for this record with report_id
                pmi_record = {
                    'report_id': report_id
                }
                
                # Add all fields from the PMI data
                for key, value in pmi_data.items():
                    # Skip empty values
                    if value is not None and value != '':
                        # Convert nested dictionaries to string if needed
                        if isinstance(value, dict):
                            pmi_record[key] = json.dumps(value)
                        else:
                            pmi_record[key] = value
                
                all_pmi_data.append(pmi_record)
            else:
                print(f"Note: No PMI data found in report {report_id}")
            
        except (KeyError, AttributeError) as e:
            handle_missing_data(filename, "patient medical information", e)
            continue
    
    return all_pmi_data


def main():
    """Main function to parse arguments and run the extraction process."""
    parser = argparse.ArgumentParser(description='Extract patient medical information from Foundation Medicine reports')
    parser.add_argument('--input', '-i', default='data/combined_reports.json',
                       help='Input JSON file path (default: data/combined_reports.json)')
    parser.add_argument('--output', '-o', default='data/patient_medical_info.csv',
                       help='Output CSV file path (default: data/patient_medical_info.csv)')
    
    args = parser.parse_args()
    
    # Setup and load data
    data = setup_extraction(args.input, args.output)
    if not data:
        return
    
    # Extract patient medical information
    print("Extracting patient medical information...")
    pmi_data = extract_patient_medical_info(data)
    
    # Save to CSV
    print(f"Saving patient medical information to {args.output}...")
    save_to_csv(pmi_data, args.output, "patient medical information records")


if __name__ == "__main__":
    main()
