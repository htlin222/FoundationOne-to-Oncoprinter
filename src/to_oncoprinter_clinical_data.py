#!/usr/bin/env python3
"""
to_oncoprinter_clinical_data.py

This script converts patient medical info and short variants data to the oncoprinter clinical data format.
It follows the format rules for clinical data as specified in the oncoprinter documentation.

Clinical data format:
All rows are tab- or space-delimited.
The first (header) row gives the names of the tracks, as well as their data type. 
The possible clinical data types are number, lognumber, or string. 
The default track type is string. You can also enter a /-delimited list of labels to create a stacked-bar-chart track.

Example first row:
SampleAge(number)Cancer_Type(string)Mutation_Count(lognumber)Mutation_Spectrum(C>A/C>G/C>T/T>A/T>C/T>G)

Each following row gives the sample id, then the value for each clinical attribute, 
or the special value N/A which indicates that there's no data.

For diagnosis grouping, the script groups diagnoses that have the same first 4 letters 
and uses the most common name within each group as the unified diagnosis name.
"""

import os
import csv
import pandas as pd
import argparse
from pathlib import Path
from collections import Counter, defaultdict
import re

def load_patient_data(data_dir):
    """Load patient information from CSV file"""
    patient_file = os.path.join(data_dir, "patient_medical_info.csv")
    if not os.path.exists(patient_file):
        print(f"Patient file not found: {patient_file}")
        return None
    
    return pd.read_csv(patient_file)

def load_short_variants(data_dir):
    """Load short variant data from CSV file"""
    variants_file = os.path.join(data_dir, "short_variants.csv")
    if not os.path.exists(variants_file):
        print(f"Short variants file not found: {variants_file}")
        return None
    
    return pd.read_csv(variants_file)

def calculate_age(patients):
    """Calculate patient age from DOB and CollDate"""
    # Convert date columns to datetime
    patients['DOB'] = pd.to_datetime(patients['DOB'], errors='coerce')
    patients['CollDate'] = pd.to_datetime(patients['CollDate'], errors='coerce')
    
    # Calculate age in years
    patients['Age'] = (patients['CollDate'] - patients['DOB']).dt.days / 365.25
    
    # Round to nearest integer
    patients['Age'] = patients['Age'].round().astype('Int64')
    
    return patients

def count_mutations_per_patient(variants):
    """Count the number of mutations for each patient"""
    if variants is None:
        return {}
    
    # Group by report_id and count
    mutation_counts = variants.groupby('report_id').size()
    
    return mutation_counts.to_dict()

def calculate_mutation_spectrum(variants):
    """
    Calculate mutation spectrum (C>A, C>G, C>T, T>A, T>C, T>G) for each patient
    Returns a dictionary with patient_id as key and a list of 6 counts as value
    """
    if variants is None:
        return {}
    
    # Initialize result dictionary
    spectrum = defaultdict(lambda: [0, 0, 0, 0, 0, 0])  # C>A, C>G, C>T, T>A, T>C, T>G
    
    # Define the mutation types to track
    mutation_types = ['C>A', 'C>G', 'C>T', 'T>A', 'T>C', 'T>G']
    
    # Process each variant
    for _, variant in variants.iterrows():
        patient_id = variant['report_id']
        cds_effect = variant['@cds-effect']
        
        # Skip if cds_effect is missing
        if pd.isna(cds_effect) or not cds_effect:
            continue
        
        # Extract the base change (e.g., C>T from 505C>T)
        match = re.search(r'([ACGT])>([ACGT])', cds_effect)
        if match:
            ref, alt = match.groups()
            
            # Normalize to C>X or T>X format
            if ref in ['C', 'T']:
                mutation = f"{ref}>{alt}"
            elif ref == 'G':
                # G>X is equivalent to C>Y on the opposite strand
                complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
                mutation = f"C>{complement[alt]}"
            elif ref == 'A':
                # A>X is equivalent to T>Y on the opposite strand
                complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
                mutation = f"T>{complement[alt]}"
            else:
                continue
            
            # Increment the appropriate counter
            if mutation in mutation_types:
                idx = mutation_types.index(mutation)
                spectrum[patient_id][idx] += 1
    
    return spectrum

def group_diagnoses(patients):
    """
    Group diagnoses that have the same first 4 letters
    and use the most common name within each group as the unified diagnosis name
    """
    if patients is None or 'SubmittedDiagnosis' not in patients.columns:
        return {}
    
    # Group diagnoses by first 4 letters
    diagnosis_groups = defaultdict(list)
    for dx in patients['SubmittedDiagnosis'].dropna().unique():
        if len(dx) >= 4:
            prefix = dx[:4].lower()
            diagnosis_groups[prefix].append(dx)
    
    # For each group, find the most common diagnosis
    unified_diagnoses = {}
    for prefix, diagnoses in diagnosis_groups.items():
        # Count occurrences of each diagnosis in the dataset
        dx_counts = Counter()
        for _, row in patients.iterrows():
            if pd.notna(row['SubmittedDiagnosis']) and row['SubmittedDiagnosis'] in diagnoses:
                dx_counts[row['SubmittedDiagnosis']] += 1
        
        # Use the most common diagnosis as the unified name
        if dx_counts:
            most_common = dx_counts.most_common(1)[0][0]
            for dx in diagnoses:
                unified_diagnoses[dx] = most_common
    
    return unified_diagnoses

def convert_to_clinical_data_format(patients, variants, output_file):
    """
    Convert patient data and variant data to oncoprinter clinical data format
    """
    if patients is None:
        print("No patient data available")
        return
    
    # Calculate age
    patients = calculate_age(patients)
    
    # Count mutations per patient
    mutation_counts = count_mutations_per_patient(variants)
    
    # Calculate mutation spectrum
    mutation_spectrum = calculate_mutation_spectrum(variants)
    
    # Group diagnoses
    unified_diagnoses = group_diagnoses(patients)
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', newline='') as f:
        # Write header row with track names and data types
        header = "Sample\tAge(number)\tCancer_Type(string)\tMutation_Count(lognumber)\tMutation_Spectrum(C>A/C>G/C>T/T>A/T>C/T>G)"
        f.write(header + '\n')
        
        # Write data rows
        for _, patient in patients.iterrows():
            patient_id = patient['report_id']
            
            # Age
            age = patient['Age'] if pd.notna(patient['Age']) else 'N/A'
            
            # Cancer type (use unified diagnosis if available)
            if pd.notna(patient['SubmittedDiagnosis']) and patient['SubmittedDiagnosis'] in unified_diagnoses:
                cancer_type = unified_diagnoses[patient['SubmittedDiagnosis']]
            elif pd.notna(patient['SubmittedDiagnosis']):
                cancer_type = patient['SubmittedDiagnosis']
            else:
                cancer_type = 'N/A'
            
            # Mutation count
            mutation_count = mutation_counts.get(patient_id, 0)
            
            # Mutation spectrum
            spectrum = mutation_spectrum.get(patient_id, [0, 0, 0, 0, 0, 0])
            spectrum_str = '/'.join(map(str, spectrum))
            
            # Write the row
            row = f"{patient_id}\t{age}\t{cancer_type}\t{mutation_count}\t{spectrum_str}"
            f.write(row + '\n')
    
    print(f"Clinical data written to {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Convert patient data to oncoprinter clinical data format')
    parser.add_argument('--data-dir', default='data', help='Directory containing the data files')
    parser.add_argument('--output-file', default=None, help='Output file name (default: clinical_data.txt)')
    
    args = parser.parse_args()
    
    # Set default output file name if not provided
    if args.output_file is None:
        args.output_file = "clinical_data.txt"
    
    # Get the absolute path to the data directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(project_dir, args.data_dir)
    
    # Create the oncoprinter directory if it doesn't exist
    oncoprinter_dir = os.path.join(data_dir, "oncoprinter")
    os.makedirs(oncoprinter_dir, exist_ok=True)
    
    # Load data
    patients = load_patient_data(data_dir)
    variants = load_short_variants(data_dir)
    
    # Convert to oncoprinter clinical data format
    output_path = os.path.join(oncoprinter_dir, args.output_file)
    convert_to_clinical_data_format(patients, variants, output_path)

if __name__ == "__main__":
    main()
