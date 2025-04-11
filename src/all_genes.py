#!/usr/bin/env python3
"""
Extract all gene names and their counts from Oncoprinter data

This script extracts gene names from the all.txt file in the oncoprinter directory,
counts their occurrences, and saves the results as a CSV file.
"""

import argparse
import csv
import os
import sys
from collections import Counter
from typing import Dict, List, Optional
from pathlib import Path


def find_all_txt() -> Optional[str]:
    """
    Try to find the all.txt file in common locations.
    
    Returns:
        Path to the all.txt file if found, None otherwise
    """
    possible_locations = [
        'data/oncoprinter/all.txt',
        'data/all.txt',
        'oncoprinter/all.txt',
        'all.txt'
    ]
    
    for location in possible_locations:
        if os.path.isfile(location):
            print(f"Found all.txt at: {location}")
            return location
    
    return None


def extract_gene_names(input_file: str) -> List[str]:
    """
    Extract all gene names from the all.txt file.
    
    Args:
        input_file: Path to the all.txt file
        
    Returns:
        A list of all gene names found in the file
    """
    all_genes = []
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    # Each line has the format: ORD-ID GENE_NAME MUTATION_INFO TYPE
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        gene_name = parts[1]
                        all_genes.append(gene_name)
                    else:
                        print(f"Warning: Line {line_num} does not have enough columns: {line.strip()}")
                except Exception as e:
                    print(f"Error processing line {line_num}: {str(e)}")
                    continue
    except Exception as e:
        print(f"Error reading file {input_file}: {str(e)}")
        return []
    
    return all_genes


def count_genes(gene_list: List[str]) -> Dict[str, int]:
    """
    Count the occurrences of each gene in the list.
    
    Args:
        gene_list: List of gene names
        
    Returns:
        Dictionary mapping gene names to their counts
    """
    return dict(Counter(gene_list))


def save_gene_counts_to_csv(gene_counts: Dict[str, int], output_path: str) -> bool:
    """
    Save gene counts to a CSV file.
    
    Args:
        gene_counts: Dictionary mapping gene names to their counts
        output_path: Path to save the CSV file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Sort genes by count (descending) and then by name (ascending)
        sorted_genes = sorted(gene_counts.items(), key=lambda x: (-x[1], x[0]))
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['gene_name', 'counts'])
            
            for gene_name, count in sorted_genes:
                writer.writerow([gene_name, count])
        
        print(f"Successfully saved {len(gene_counts)} gene counts to {output_path}")
        return True
    except Exception as e:
        print(f"Error saving to {output_path}: {str(e)}")
        return False


def main():
    """Main function to parse arguments and run the extraction process."""
    parser = argparse.ArgumentParser(description='Extract all gene names and their counts from Oncoprinter data')
    parser.add_argument('--input', '-i', default=None,
                       help='Input text file path (default: auto-detect)')
    parser.add_argument('--output', '-o', default='data/gene_counts.csv',
                       help='Output CSV file path (default: data/gene_counts.csv)')
    
    args = parser.parse_args()
    
    # Determine input file path
    input_file = args.input
    if not input_file:
        # Try to auto-detect the all.txt file
        input_file = find_all_txt()
        if not input_file:
            print("Error: Could not find all.txt file. Please specify the path using --input")
            print("Example: python src/all_genes.py --input path/to/all.txt")
            return 1
    
    # Ensure input file exists
    if not os.path.isfile(input_file):
        print(f"Error: Input file '{input_file}' does not exist")
        print("Please specify the correct path using --input")
        print("Example: python src/all_genes.py --input path/to/all.txt")
        return 1
    
    # Extract gene names
    print(f"Extracting gene names from {input_file}...")
    genes = extract_gene_names(input_file)
    
    if not genes:
        print("No genes found in the file. Please check if the data structure is as expected.")
        return 1
    
    # Count gene occurrences
    print("Counting gene occurrences...")
    gene_counts = count_genes(genes)
    
    # Save to CSV
    print(f"Saving gene counts to {args.output}...")
    if not save_gene_counts_to_csv(gene_counts, args.output):
        return 1
    
    print(f"Total unique genes found: {len(gene_counts)}")
    print(f"Total gene occurrences: {sum(gene_counts.values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
