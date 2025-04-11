#!/usr/bin/env python3
"""
to_oncoprinter_filtered_by_dx.py

This script converts genetic data from CSV files in the data directory to the OncoprinterValidated format,
filtering patients based on a case-insensitive match in the SubmittedDiagnosis field.

Usage:
    to_oncoprinter_filtered_by_dx.py --dx 'lung'

Format:
1. Sample only (e.g. so that percent altered in your data can be properly calculated by including unaltered samples).
2. Sample GeneAlterationTypeTrack Name (optional)

For more details on the format, see the script documentation.
"""

import os
import csv
import pandas as pd
import argparse
from pathlib import Path

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

def load_rearrangements(data_dir):
    """Load rearrangement data from CSV file"""
    rearrangements_file = os.path.join(data_dir, "rearrangements.csv")
    if not os.path.exists(rearrangements_file):
        print(f"Rearrangements file not found: {rearrangements_file}")
        return None
    
    return pd.read_csv(rearrangements_file)

def load_copy_number_alterations(data_dir):
    """Load copy number alteration data from CSV file"""
    cna_file = os.path.join(data_dir, "copy_number_alterations.csv")
    if not os.path.exists(cna_file):
        print(f"Copy number alterations file not found: {cna_file}")
        return None
    
    return pd.read_csv(cna_file)

def determine_mutation_type(variant):
    """
    Determine the mutation type based on the functional effect
    Returns a tuple of (alteration, type)
    """
    functional_effect = variant['@functional-effect']
    
    # Map functional effects to mutation types - strictly use only the allowed types
    if functional_effect == 'missense':
        mutation_type = 'MISSENSE'
    elif functional_effect == 'nonsense':
        mutation_type = 'TRUNC'
    elif functional_effect in ['nonframeshift', 'inframe']:
        mutation_type = 'INFRAME'
    elif functional_effect == 'frameshift':
        mutation_type = 'TRUNC'
    elif functional_effect == 'splice':
        mutation_type = 'SPLICE'
    elif functional_effect == 'promoter':
        mutation_type = 'PROMOTER'
    else:
        mutation_type = 'OTHER'
    
    # Create the alteration description
    protein_effect = variant['@protein-effect']
    
    # Clean up the alteration description
    if protein_effect.startswith('splice site '):
        protein_effect = protein_effect.replace('splice site ', '')
    
    # Replace spaces with underscores to avoid parsing issues
    alteration = protein_effect.replace(' ', '_')
    
    # Remove any potentially problematic characters
    alteration = ''.join(c for c in alteration if c.isalnum() or c in '_-*:+.()/')
    
    # Check if it's a known or likely mutation to mark as DRIVER
    status = variant['@status']
    if status in ['known', 'likely']:
        mutation_type += '_DRIVER'
    
    return alteration, mutation_type

def determine_rearrangement_type(rearrangement):
    """
    Determine the rearrangement type based on the description and type
    Returns a tuple of (alteration, type)
    """
    rearrangement_type = rearrangement['@type']
    description = rearrangement['@description']
    other_gene = rearrangement['@other-gene']
    targeted_gene = rearrangement['@targeted-gene']
    
    # Create a clean alteration description
    if pd.isna(other_gene) or other_gene == 'N/A':
        # Internal rearrangement
        clean_desc = description.replace(' ', '_')
        # Remove any potentially problematic characters
        clean_desc = ''.join(c for c in clean_desc if c.isalnum() or c in '_-*:+.()/')
        alteration = clean_desc
    else:
        # Fusion event - keep it simple
        alteration = f"{other_gene}-{targeted_gene}_fusion"
    
    # Always use FUSION for rearrangements
    # NOTE: We're not adding the _DRIVER suffix as it might not be supported
    # for fusion events in the OncoprinterValidated format
    type_code = 'FUSION'
    
    return alteration, type_code

def determine_cna_type(cna):
    """
    Determine the CNA type based on the copy number and type
    Returns a tuple of (alteration, type)
    """
    copy_number = cna['@copy-number']
    cna_type = cna['@type']
    
    # Strictly use only the allowed CNA types
    if cna_type == 'amplification':
        if copy_number >= 8:  # High level amplification
            return 'AMP', 'CNA'
        else:  # Low level gain
            return 'GAIN', 'CNA'
    elif cna_type == 'loss':
        if copy_number == 0:  # Deep deletion
            return 'HOMDEL', 'CNA'
        else:  # Shallow deletion
            return 'HETLOSS', 'CNA'
    
    # Default case - use GAIN as a safe default
    return 'GAIN', 'CNA'

def filter_patients_by_diagnosis(patients, diagnosis):
    """
    Filter patients based on a case-insensitive match in the SubmittedDiagnosis field
    """
    if patients is None:
        return None
    
    # Convert diagnosis to lowercase for case-insensitive matching
    diagnosis = diagnosis.lower()
    
    # Filter patients where SubmittedDiagnosis contains the specified diagnosis (case-insensitive)
    filtered_patients = patients[patients['SubmittedDiagnosis'].str.lower().str.contains(diagnosis, na=False)]
    
    if filtered_patients.empty:
        print(f"No patients found with diagnosis containing '{diagnosis}'")
        return None
    
    print(f"Found {len(filtered_patients)} patients with diagnosis containing '{diagnosis}'")
    return filtered_patients

def convert_to_oncoprinter_format(patients, variants, cnas, rearrangements, output_file):
    """
    Convert the data to OncoprinterValidated format and write to output file
    """
    # Create a set of all patient IDs
    all_patient_ids = set(patients['report_id'])
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        
        # Process short variants
        if variants is not None:
            for _, variant in variants.iterrows():
                patient_id = variant['report_id']
                
                # Skip if patient is not in the filtered list
                if patient_id not in all_patient_ids:
                    continue
                
                gene = variant['@gene']
                
                # Skip if gene is empty
                if not gene or pd.isna(gene):
                    continue
                
                alteration, mutation_type = determine_mutation_type(variant)
                
                # Skip if alteration is empty
                if not alteration or pd.isna(alteration):
                    continue
                
                # Write the row: Sample Gene Alteration Type
                writer.writerow([patient_id, gene, alteration, mutation_type])
                
                # Remove from the set of unaltered patients
                if patient_id in all_patient_ids:
                    all_patient_ids.remove(patient_id)
        
        # Process rearrangements
        if rearrangements is not None:
            for _, rearrangement in rearrangements.iterrows():
                patient_id = rearrangement['report_id']
                
                # Skip if patient is not in the filtered list
                if patient_id not in all_patient_ids:
                    continue
                
                gene = rearrangement['@targeted-gene']
                
                # Skip if gene is empty
                if not gene or pd.isna(gene):
                    continue
                
                alteration, rearrangement_type = determine_rearrangement_type(rearrangement)
                
                # Skip if alteration is empty
                if not alteration or pd.isna(alteration):
                    continue
                
                # Write the row: Sample Gene Alteration Type
                writer.writerow([patient_id, gene, alteration, rearrangement_type])
                
                # Remove from the set of unaltered patients
                if patient_id in all_patient_ids:
                    all_patient_ids.remove(patient_id)
        
        # Process copy number alterations
        if cnas is not None:
            for _, cna in cnas.iterrows():
                patient_id = cna['report_id']
                
                # Skip if patient is not in the filtered list
                if patient_id not in all_patient_ids:
                    continue
                
                gene = cna['@gene']
                
                # Skip if gene is empty
                if not gene or pd.isna(gene):
                    continue
                
                alteration, cna_type = determine_cna_type(cna)
                
                # Write the row: Sample Gene Alteration Type
                writer.writerow([patient_id, gene, alteration, cna_type])
                
                # Remove from the set of unaltered patients
                if patient_id in all_patient_ids:
                    all_patient_ids.remove(patient_id)
        
        # Add unaltered patients (only the sample ID)
        for patient_id in all_patient_ids:
            writer.writerow([patient_id])

def main():
    parser = argparse.ArgumentParser(description='Convert genetic data to OncoprinterValidated format, filtered by diagnosis.')
    parser.add_argument('--dx', required=True, help='Diagnosis to filter by (case-insensitive match)')
    parser.add_argument('--data-dir', default='data', help='Directory containing the data files')
    parser.add_argument('--output-file', help='Output file name (default: <diagnosis>.txt)')
    
    args = parser.parse_args()
    
    # Set default output file name if not provided
    if args.output_file is None:
        args.output_file = f"{args.dx.lower()}.txt"
    
    # Get the absolute path to the data directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(project_dir, args.data_dir)
    
    # Create the oncoprinter directory if it doesn't exist
    oncoprinter_dir = os.path.join(data_dir, "oncoprinter")
    os.makedirs(oncoprinter_dir, exist_ok=True)
    
    # Load data
    patients = load_patient_data(data_dir)
    if patients is None:
        return
    
    # Filter patients by diagnosis
    filtered_patients = filter_patients_by_diagnosis(patients, args.dx)
    if filtered_patients is None or filtered_patients.empty:
        return
    
    variants = load_short_variants(data_dir)
    rearrangements = load_rearrangements(data_dir)
    cnas = load_copy_number_alterations(data_dir)
    
    # Convert to OncoprinterValidated format
    output_path = os.path.join(oncoprinter_dir, args.output_file)
    convert_to_oncoprinter_format(filtered_patients, variants, cnas, rearrangements, output_path)
    
    print(f"Conversion complete. Output written to {output_path}")

if __name__ == "__main__":
    main()
