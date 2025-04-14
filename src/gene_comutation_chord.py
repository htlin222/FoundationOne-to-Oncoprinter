#!/usr/bin/env python3
"""
Gene Co-mutation Chord Diagram Generator

This script analyzes gene mutation data from the oncoprinter/all.txt file,
identifies co-mutations (genes that appear in the same patient),
and visualizes these relationships using a chord diagram with pycirclize.
"""

import os
import sys
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
from pycirclize import Circos
import argparse
from pathlib import Path


def find_data_file(filename="all.txt", possible_dirs=None):
    """Find the data file in common locations."""
    if possible_dirs is None:
        possible_dirs = [
            "data/oncoprinter",
            "./data/oncoprinter",
            "../data/oncoprinter",
        ]
    
    for directory in possible_dirs:
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            return filepath
    
    return None


def read_mutation_data(filepath):
    """Read mutation data from the specified file."""
    try:
        # Read the file with tab delimiter
        df = pd.read_csv(filepath, sep='\t', header=None)
        
        # Assign column names based on the observed structure
        if df.shape[1] >= 4:
            df.columns = ['Patient_ID', 'Gene', 'Mutation', 'Type'] + [f'Col_{i+5}' for i in range(df.shape[1]-4)]
        else:
            # Handle case with fewer columns
            df.columns = ['Patient_ID', 'Gene'] + [f'Col_{i+3}' for i in range(df.shape[1]-2)]
        
        return df
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        sys.exit(1)


def identify_comutations(df, min_count=2, top_genes=30):
    """
    Identify and count gene co-mutations.
    
    Args:
        df: DataFrame with mutation data
        min_count: Minimum co-mutation count to include
        top_genes: Number of top genes to include in the visualization
    
    Returns:
        comutation_matrix: DataFrame of co-mutation counts
        gene_counts: Counter of gene frequencies
    """
    # Count gene occurrences
    gene_counts = Counter(df['Gene'])
    
    # Get the top genes by frequency
    top_genes_list = [gene for gene, count in gene_counts.most_common(top_genes)]
    
    # Group mutations by patient
    patient_genes = defaultdict(set)
    for _, row in df.iterrows():
        patient_genes[row['Patient_ID']].add(row['Gene'])
    
    # Count co-mutations
    comutation_counts = defaultdict(int)
    for patient, genes in patient_genes.items():
        # Only consider genes in our top list
        relevant_genes = [gene for gene in genes if gene in top_genes_list]
        
        # Count all pairs of genes
        for i, gene1 in enumerate(relevant_genes):
            for gene2 in relevant_genes[i+1:]:
                if gene1 != gene2:  # Avoid self-loops
                    # Sort genes alphabetically to ensure consistent counting
                    key = tuple(sorted([gene1, gene2]))
                    comutation_counts[key] += 1
    
    # Filter by minimum count
    filtered_comutations = {k: v for k, v in comutation_counts.items() if v >= min_count}
    
    # Create a matrix for the chord diagram
    comutation_matrix = np.zeros((len(top_genes_list), len(top_genes_list)))
    gene_to_idx = {gene: i for i, gene in enumerate(top_genes_list)}
    
    for (gene1, gene2), count in filtered_comutations.items():
        if gene1 in gene_to_idx and gene2 in gene_to_idx:
            i, j = gene_to_idx[gene1], gene_to_idx[gene2]
            comutation_matrix[i, j] = count
            comutation_matrix[j, i] = count  # Make it symmetric
    
    # Convert to DataFrame for pycirclize
    matrix_df = pd.DataFrame(comutation_matrix, index=top_genes_list, columns=top_genes_list)
    
    return matrix_df, gene_counts, top_genes_list


def create_chord_diagram(matrix_df, gene_counts, output_file="gene_comutation_chord.png"):
    """
    Create a chord diagram from the co-mutation matrix.
    
    Args:
        matrix_df: DataFrame with co-mutation counts
        gene_counts: Counter with gene frequencies
        output_file: Path to save the output image
    """
    # Add gene counts to index and column names
    matrix_df_with_counts = matrix_df.copy()
    new_labels = {gene: f"{gene}\n({gene_counts[gene]})" for gene in matrix_df.index}
    matrix_df_with_counts.rename(index=new_labels, columns=new_labels, inplace=True)
    
    # Create a directed matrix where links only go from higher count genes to lower count genes
    directed_matrix = matrix_df.copy() * 0  # Start with zeros
    
    # Fill the directed matrix based on gene counts
    for i, gene_i in enumerate(matrix_df.index):
        for j, gene_j in enumerate(matrix_df.columns):
            if i != j and matrix_df.iloc[i, j] > 0:
                # Determine which gene has higher count
                if gene_counts[gene_i] >= gene_counts[gene_j]:
                    # i has higher count, so link goes from i to j
                    directed_matrix.iloc[i, j] = matrix_df.iloc[i, j]
                else:
                    # j has higher count, so link goes from j to i
                    directed_matrix.iloc[j, i] = matrix_df.iloc[i, j]
    
    # Rename with counts for display
    directed_matrix_with_counts = directed_matrix.copy()
    directed_matrix_with_counts.rename(index=new_labels, columns=new_labels, inplace=True)
    
    # Initialize Circos instance for chord diagram plot
    circos = Circos.chord_diagram(
        directed_matrix_with_counts,
        space=2,
        r_lim=(90, 100),
        cmap="tab10",
        label_kws=dict(r=105, size=8),
        link_kws=dict(ec="grey", lw=0.1),
    )
    
    # Set figure size and save
    fig = circos.plotfig()
    fig.set_figwidth(10)
    fig.set_figheight(10)
    
    # Save figure
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Chord diagram saved to {output_file}")
    
    return fig


def main():
    parser = argparse.ArgumentParser(description="Generate a chord diagram of gene co-mutations")
    parser.add_argument("-i", "--input", help="Path to the mutation data file")
    parser.add_argument("-o", "--output", default="gene_comutation_chord.png", help="Output image file path")
    parser.add_argument("-m", "--min-count", type=int, default=3, help="Minimum co-mutation count to include")
    parser.add_argument("-t", "--top-genes", type=int, default=20, help="Number of top genes to include")
    args = parser.parse_args()
    
    # Find the data file
    if args.input:
        data_file = args.input
    else:
        data_file = find_data_file()
        if not data_file:
            print("Error: Could not find the mutation data file.")
            sys.exit(1)
    
    print(f"Reading mutation data from {data_file}")
    df = read_mutation_data(data_file)
    
    print(f"Analyzing co-mutations for top {args.top_genes} genes with minimum count of {args.min_count}")
    matrix_df, gene_counts, gene_list = identify_comutations(df, min_count=args.min_count, top_genes=args.top_genes)
    
    # Create output directory if it doesn't exist
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("Generating chord diagram...")
    fig = create_chord_diagram(matrix_df, gene_counts, output_file=args.output)
    
    # Display some statistics
    total_mutations = sum(gene_counts.values())
    unique_genes = len(gene_counts)
    print(f"\nStatistics:")
    print(f"Total mutations: {total_mutations}")
    print(f"Unique genes: {unique_genes}")
    print(f"Top 5 genes by frequency:")
    for gene, count in gene_counts.most_common(5):
        print(f"  {gene}: {count}")


if __name__ == "__main__":
    main()
