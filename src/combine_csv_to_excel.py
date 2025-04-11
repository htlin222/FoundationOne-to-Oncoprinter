#!/usr/bin/env python3
"""
Combine CSV Files to Excel

This script combines all CSV files in the specified directory into a single Excel file,
with each CSV file as a separate worksheet.
"""

import os
import glob
import pandas as pd
import argparse
from pathlib import Path


def combine_csv_to_excel(input_dir: str, output_file: str) -> None:
    """
    Combine all CSV files in the input directory into a single Excel file.
    
    Args:
        input_dir: Directory containing CSV files
        output_file: Path to save the Excel file
    """
    # Get all CSV files in the directory
    csv_files = glob.glob(os.path.join(input_dir, "*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {input_dir}")
        return
    
    print(f"Found {len(csv_files)} CSV files to combine")
    
    # Create a Pandas Excel writer using XlsxWriter as the engine
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        for csv_file in csv_files:
            # Get the base filename without extension to use as sheet name
            sheet_name = os.path.splitext(os.path.basename(csv_file))[0]
            
            # Truncate sheet name if needed (Excel has a 31 character limit for sheet names)
            if len(sheet_name) > 31:
                sheet_name = sheet_name[:31]
            
            print(f"Processing {csv_file} -> Sheet: {sheet_name}")
            
            # Read the CSV file
            try:
                df = pd.read_csv(csv_file)
                
                # Write the dataframe to the Excel file
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Get the xlsxwriter workbook and worksheet objects
                workbook = writer.book
                worksheet = writer.sheets[sheet_name]
                
                # Set the column width based on the maximum length of data in each column
                for i, col in enumerate(df.columns):
                    # Find the maximum length of the column name and the data in the column
                    max_len = max(
                        df[col].astype(str).map(len).max(),  # max length of data
                        len(str(col))  # length of column name
                    )
                    
                    # Add a little extra space
                    max_len += 2
                    
                    # Set the column width (max 100 to avoid excessive width)
                    worksheet.set_column(i, i, min(max_len, 100))
            
            except Exception as e:
                print(f"Error processing {csv_file}: {str(e)}")
    
    print(f"Successfully combined {len(csv_files)} CSV files into {output_file}")


def main():
    """Main function to parse arguments and run the conversion process."""
    parser = argparse.ArgumentParser(description='Combine CSV files into a single Excel file')
    parser.add_argument('--input', '-i', default='data',
                       help='Input directory containing CSV files (default: data)')
    parser.add_argument('--output', '-o', default='data/combined_reports.xlsx',
                       help='Output Excel file path (default: data/combined_reports.xlsx)')
    
    args = parser.parse_args()
    
    # Ensure input directory exists
    if not os.path.isdir(args.input):
        print(f"Error: Input directory '{args.input}' does not exist")
        return
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Combine CSV files to Excel
    combine_csv_to_excel(args.input, args.output)


if __name__ == "__main__":
    main()
