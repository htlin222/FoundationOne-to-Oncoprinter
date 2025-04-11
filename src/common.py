#!/usr/bin/env python3
"""
Common utilities for Foundation Medicine report extraction

This module provides shared functionality for extracting data from
Foundation Medicine reports and saving it to CSV files.
"""

import json
import csv
import os
from typing import Dict, List, Any, Optional
from pathlib import Path


def extract_report_id(filename: str) -> str:
    """
    Extract the report ID from the filename.
    
    Args:
        filename: The XML filename
        
    Returns:
        The report ID (e.g., 'ORD-0906514-01')
    """
    # Remove file extension
    return os.path.splitext(filename)[0]


def get_all_fields(data_list: List[Dict[str, Any]]) -> List[str]:
    """
    Get all unique fields from a list of dictionaries.
    
    Args:
        data_list: List of dictionaries
        
    Returns:
        List of all unique field names
    """
    all_fields = set()
    
    for record in data_list:
        all_fields.update(record.keys())
    
    # Ensure report_id is the first field
    fields = list(all_fields)
    if 'report_id' in fields:
        fields.remove('report_id')
    
    return ['report_id'] + sorted(fields)


def save_to_csv(data_list: List[Dict[str, Any]], output_path: str, data_type: str = "records") -> None:
    """
    Save a list of dictionaries to a CSV file.
    
    Args:
        data_list: List of dictionaries to save
        output_path: Path to save the CSV file
        data_type: Description of the data type (for logging)
    """
    if not data_list:
        print(f"No {data_type} found to save.")
        return
    
    # Get all unique fields
    fieldnames = get_all_fields(data_list)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for record in data_list:
            writer.writerow(record)
    
    print(f"Successfully saved {len(data_list)} {data_type} to {output_path}")


def setup_extraction(input_path: str, output_path: str) -> Optional[Dict[str, Any]]:
    """
    Common setup for extraction scripts.
    
    Args:
        input_path: Path to the input JSON file
        output_path: Path to the output CSV file
        
    Returns:
        The loaded JSON data if successful, None otherwise
    """
    # Ensure input file exists
    if not os.path.isfile(input_path):
        print(f"Error: Input file '{input_path}' does not exist")
        return None
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Load the combined JSON data
    print(f"Loading data from {input_path}...")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data


def process_dna_evidence(item: Dict[str, Any], data_dict: Dict[str, Any]) -> None:
    """
    Process DNA evidence data and add it to the data dictionary.
    
    Args:
        item: The item containing dna-evidence
        data_dict: The dictionary to add the processed data to
    """
    if 'dna-evidence' in item:
        dna_evidence = item['dna-evidence']
        # If it's a dictionary, extract sample attribute
        if isinstance(dna_evidence, dict) and '@sample' in dna_evidence:
            data_dict['dna_evidence_sample'] = dna_evidence['@sample']
        # If it's a list, extract sample attributes from each item
        elif isinstance(dna_evidence, list):
            samples = [i.get('@sample', '') for i in dna_evidence if '@sample' in i]
            data_dict['dna_evidence_sample'] = ';'.join(samples)
    
    # Remove nested structures to flatten the data
    if 'dna-evidence' in data_dict:
        del data_dict['dna-evidence']


def handle_missing_data(filename: str, data_type: str, error: Exception) -> None:
    """
    Handle missing data errors with user-friendly messages.
    
    Args:
        filename: The filename being processed
        data_type: The type of data being extracted (e.g., 'rearrangements')
        error: The exception that was raised
    """
    report_id = extract_report_id(filename)
    
    if "'NoneType' object has no attribute 'get'" in str(error):
        print(f"Note: No {data_type} data found in report {report_id}")
    else:
        print(f"Error processing {filename}: {str(error)}")
