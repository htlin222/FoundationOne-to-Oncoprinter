#!/usr/bin/env python3
"""
to_oncoprinter_mutation_map_validated_dataset.py

This script extracts mutation data for specific genes from the short_variants.csv file
and converts it to the OncoprinterValidated format. The output is saved as tab-delimited
text files in the data/oncoprinter directory with the gene names as the filenames.

The script follows the format rules for genomic location data as specified in the
OncoprinterValidated documentation, ensuring all variants include:
- Chromosome
- Start_Position
- End_Position
- Reference_Allele
- Variant_Allele

Usage:
    python to_oncoprinter_mutation_map_validated_dataset.py --gene GENE_NAME
    python to_oncoprinter_mutation_map_validated_dataset.py --gene GENE1,GENE2,GENE3
    python to_oncoprinter_mutation_map_validated_dataset.py --gene GENE1,GENE2,GENE3 --onefile

For more details on the format, see the OncoprinterValidated documentation.
"""

import os
import csv
import pandas as pd
import argparse
from pathlib import Path


def load_short_variants(data_dir):
    """Load short variant data from CSV file"""
    variants_file = os.path.join(data_dir, "short_variants.csv")
    if not os.path.exists(variants_file):
        print(f"Short variants file not found: {variants_file}")
        return None
    
    return pd.read_csv(variants_file)


def parse_genomic_position(position_str):
    """
    Parse the genomic position string (e.g., 'chr16:23647362') into chromosome and position
    
    Args:
        position_str: String in format 'chrX:POSITION'
        
    Returns:
        Tuple of (chromosome, position)
    """
    if pd.isna(position_str) or not position_str:
        return None, None
    
    # Remove 'chr' prefix and split by colon
    parts = position_str.replace('chr', '').split(':')
    if len(parts) != 2:
        return None, None
    
    chromosome, position = parts
    try:
        position = int(position)
        return chromosome, position
    except ValueError:
        return None, None


def parse_cds_effect(cds_effect):
    """
    Parse the CDS effect string to extract reference and variant alleles
    
    Args:
        cds_effect: String like '505C>T' or '638_639insTGGCGGGGG' or '340_344CCGGC>G'
        
    Returns:
        Tuple of (reference_allele, variant_allele)
    """
    if pd.isna(cds_effect) or not cds_effect:
        return None, None
    
    # Handle insertions (format: POS_POSinsBASES)
    if 'ins' in cds_effect:
        parts = cds_effect.split('ins')
        if len(parts) == 2:
            return '-', parts[1]
    
    # Handle deletions (format: POS_POSdelBASES)
    elif 'del' in cds_effect:
        parts = cds_effect.split('del')
        if len(parts) == 2:
            return parts[1], '-'
    
    # Handle substitutions (format: POSR>V)
    elif '>' in cds_effect:
        # Extract the part after any numbers and underscores
        effect_part = ''.join(c for c in cds_effect if c.isalpha() or c == '>')
        parts = effect_part.split('>')
        if len(parts) == 2:
            return parts[0], parts[1]
    
    # Default case - can't parse
    return None, None


def determine_mutation_type(variant):
    """
    Determine the mutation type based on the functional effect
    Returns a string representing the mutation type
    """
    functional_effect = variant['@functional-effect']
    
    # Map functional effects to mutation types
    if functional_effect == 'missense':
        return 'Missense_Mutation'
    elif functional_effect == 'nonsense':
        return 'Nonsense_Mutation'
    elif functional_effect in ['nonframeshift', 'inframe']:
        return 'In_Frame_Indel'
    elif functional_effect == 'frameshift':
        return 'Frame_Shift_Indel'
    elif functional_effect == 'splice':
        return 'Splice_Site'
    elif functional_effect == 'promoter':
        return 'Promoter'
    else:
        return 'Missense_Mutation'  # Default


def convert_to_oncoprinter_format(variants, gene, output_file):
    """
    Convert the data for a specific gene to OncoprinterValidated format and write to output file
    
    Args:
        variants: DataFrame containing variant data
        gene: Gene name to filter for
        output_file: Path to output file
    """
    # Filter variants for the specified gene
    gene_variants = variants[variants['@gene'] == gene]
    
    if len(gene_variants) == 0:
        print(f"No variants found for gene {gene}")
        return 0
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Define the headers required for OncoprinterValidated format
    headers = [
        'Hugo_Symbol',
        'Sample_ID',
        'Protein_Change',
        'Mutation_Type',
        'Chromosome',
        'Start_Position',
        'End_Position',
        'Reference_Allele',
        'Variant_Allele',
        'Validation_Status',
        'Mutation_Status'
    ]
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(headers)
        
        for _, variant in gene_variants.iterrows():
            # Parse genomic position
            chromosome, position = parse_genomic_position(variant['@position'])
            if chromosome is None or position is None:
                continue
            
            # For point mutations, start and end positions are the same
            start_position = position
            end_position = position
            
            # Parse reference and variant alleles
            reference_allele, variant_allele = parse_cds_effect(variant['@cds-effect'])
            if reference_allele is None or variant_allele is None:
                # Skip variants where we can't determine the alleles
                continue
            
            # Determine mutation type
            mutation_type = determine_mutation_type(variant)
            
            # Map validation status
            status = variant['@status']
            validation_status = 'Valid' if status in ['known', 'likely'] else 'Unknown'
            
            # Determine mutation status (always Somatic for this dataset)
            mutation_status = 'Somatic'
            
            # Write the row
            writer.writerow([
                gene,                      # Hugo_Symbol
                variant['report_id'],      # Sample_ID
                variant['@protein-effect'],# Protein_Change
                mutation_type,             # Mutation_Type
                chromosome,                # Chromosome
                start_position,            # Start_Position
                end_position,              # End_Position
                reference_allele,          # Reference_Allele
                variant_allele,            # Variant_Allele
                validation_status,         # Validation_Status
                mutation_status            # Mutation_Status
            ])
    
    print(f"Successfully wrote {len(gene_variants)} variants for gene {gene} to {output_file}")
    return len(gene_variants)


def process_genes_to_separate_files(variants, genes, output_dir):
    """
    Process each gene and create separate output files
    
    Args:
        variants: DataFrame containing variant data
        genes: List of gene names to process
        output_dir: Directory to save output files
        
    Returns:
        Dictionary mapping gene names to variant counts
    """
    results = {}
    
    for gene in genes:
        if not gene:  # Skip empty gene names
            continue
            
        output_file = os.path.join(output_dir, f"{gene}.txt")
        variant_count = convert_to_oncoprinter_format(variants, gene, output_file)
        results[gene] = variant_count
        
    return results


def process_genes_to_single_file(variants, genes, output_dir):
    """
    Process multiple genes and combine results into a single output file
    
    Args:
        variants: DataFrame containing variant data
        genes: List of gene names to process
        output_dir: Directory to save output file
        
    Returns:
        Tuple of (output_file_path, total_variant_count)
    """
    # Create a combined filename with up to 3 gene names
    if len(genes) <= 3:
        filename = f"{'_'.join(genes)}.txt"
    else:
        filename = f"{'_'.join(genes[:3])}_plus_{len(genes)-3}_more.txt"
    
    output_file = os.path.join(output_dir, filename)
    
    # Define the headers required for OncoprinterValidated format
    headers = [
        'Hugo_Symbol',
        'Sample_ID',
        'Protein_Change',
        'Mutation_Type',
        'Chromosome',
        'Start_Position',
        'End_Position',
        'Reference_Allele',
        'Variant_Allele',
        'Validation_Status',
        'Mutation_Status'
    ]
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    total_variants = 0
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(headers)
        
        for gene in genes:
            if not gene:  # Skip empty gene names
                continue
                
            # Filter variants for this gene
            gene_variants = variants[variants['@gene'] == gene]
            
            if len(gene_variants) == 0:
                print(f"No variants found for gene {gene}")
                continue
            
            gene_count = 0
            
            for _, variant in gene_variants.iterrows():
                # Parse genomic position
                chromosome, position = parse_genomic_position(variant['@position'])
                if chromosome is None or position is None:
                    continue
                
                # For point mutations, start and end positions are the same
                start_position = position
                end_position = position
                
                # Parse reference and variant alleles
                reference_allele, variant_allele = parse_cds_effect(variant['@cds-effect'])
                if reference_allele is None or variant_allele is None:
                    # Skip variants where we can't determine the alleles
                    continue
                
                # Determine mutation type
                mutation_type = determine_mutation_type(variant)
                
                # Map validation status
                status = variant['@status']
                validation_status = 'Valid' if status in ['known', 'likely'] else 'Unknown'
                
                # Determine mutation status (always Somatic for this dataset)
                mutation_status = 'Somatic'
                
                # Write the row
                writer.writerow([
                    gene,                      # Hugo_Symbol
                    variant['report_id'],      # Sample_ID
                    variant['@protein-effect'],# Protein_Change
                    mutation_type,             # Mutation_Type
                    chromosome,                # Chromosome
                    start_position,            # Start_Position
                    end_position,              # End_Position
                    reference_allele,          # Reference_Allele
                    variant_allele,            # Variant_Allele
                    validation_status,         # Validation_Status
                    mutation_status            # Mutation_Status
                ])
                
                gene_count += 1
            
            print(f"Added {gene_count} variants for gene {gene}")
            total_variants += gene_count
    
    print(f"Successfully wrote a total of {total_variants} variants to {output_file}")
    return output_file, total_variants


def main():
    parser = argparse.ArgumentParser(description='Convert genetic data for specific genes to OncoprinterValidated format')
    parser.add_argument('--gene', type=str, required=True,
                        help='Gene name(s) to extract data for. For multiple genes, provide a comma-separated list (e.g., TP53,EGFR,KRAS)')
    parser.add_argument('--data_dir', type=str, 
                        default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data'),
                        help='Directory containing the CSV data files')
    parser.add_argument('--onefile', action='store_true',
                        help='Combine all genes into a single output file instead of creating separate files for each gene')
    
    args = parser.parse_args()
    
    # Ensure data directory exists
    data_dir = args.data_dir
    if not os.path.exists(data_dir):
        print(f"Data directory not found: {data_dir}")
        return
    
    # Load variant data
    variants = load_short_variants(data_dir)
    if variants is None:
        print("Failed to load variant data. Exiting.")
        return
    
    # Process each gene in the comma-separated list
    genes = [gene.strip() for gene in args.gene.split(',')]
    
    if not genes:
        print("No valid genes specified. Exiting.")
        return
    
    print(f"Processing {len(genes)} gene(s): {', '.join(genes)}")
    
    # Create output directory
    output_dir = os.path.join(data_dir, "oncoprinter")
    os.makedirs(output_dir, exist_ok=True)
    
    # Process genes based on the onefile flag
    if args.onefile:
        process_genes_to_single_file(variants, genes, output_dir)
    else:
        process_genes_to_separate_files(variants, genes, output_dir)

if __name__ == "__main__":
    main()
