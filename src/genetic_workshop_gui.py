#!/usr/bin/env python3
"""
Genetic Workshop GUI

A graphical user interface for the Genetic Workshop project using NiceGUI.
This application provides:
1. A UI for all Makefile functionality
2. A search feature for combined_reports.json
3. A report viewer for individual reports
"""

import os
import json
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from functools import partial

from nicegui import ui, app
import pandas as pd
from fuzzywuzzy import process, fuzz

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SRC_DIR = PROJECT_ROOT / "src"
JSON_DB_PATH = DATA_DIR / "combined_reports.json"

# Cache for loaded data
loaded_data = {
    "reports": None,
    "patient_info": None,
    "variants": None,
    "cna": None,
    "rearrangements": None,
    "msi": None,
    "tmb": None
}

# Function to load JSON data
def load_json_data():
    """Load the combined reports JSON data"""
    if not JSON_DB_PATH.exists():
        return None
    
    try:
        with open(JSON_DB_PATH, 'r') as f:
            data = json.load(f)
        loaded_data["reports"] = data
        return data
    except Exception as e:
        ui.notify(f"Error loading JSON data: {str(e)}", type="negative")
        return None

# Function to load CSV data
def load_csv_data(file_name):
    """Load CSV data from the data directory"""
    file_path = DATA_DIR / file_name
    if not file_path.exists():
        return None
    
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        ui.notify(f"Error loading {file_name}: {str(e)}", type="negative")
        return None

# Function to run make commands
async def run_make_command(target, params=None):
    """Run a make command with optional parameters"""
    cmd = ["make", target]
    if params:
        cmd.extend([f"{k}={v}" for k, v in params.items()])
    
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=PROJECT_ROOT
    )
    
    stdout, stderr = await process.communicate()
    
    if process.returncode == 0:
        ui.notify(f"Successfully ran: {' '.join(cmd)}", type="positive")
        return stdout.decode()
    else:
        error_msg = stderr.decode()
        ui.notify(f"Error running command: {error_msg}", type="negative")
        return error_msg

# Function to search reports
def search_reports(query, reports_data):
    """Search reports using fuzzy matching"""
    if not reports_data:
        ui.notify("No reports data loaded. Please run 'XML to JSON' first.", type="warning")
        return []
    
    results = []
    
    # Search in each report
    for report in reports_data:
        report_id = report.get("report_id", "Unknown")
        patient_name = report.get("patient", {}).get("name", "Unknown")
        diagnosis = report.get("patient", {}).get("diagnosis", "Unknown")
        
        # Create a searchable text from the report
        searchable_text = f"{report_id} {patient_name} {diagnosis}"
        
        # Add variants if they exist
        variants = report.get("variants", [])
        for variant in variants:
            gene = variant.get("@gene", "")
            protein_effect = variant.get("@protein-effect", "")
            searchable_text += f" {gene} {protein_effect}"
        
        # Score the match
        score = fuzz.partial_ratio(query.lower(), searchable_text.lower())
        
        if score > 60:  # Threshold for matches
            results.append({
                "report_id": report_id,
                "patient_name": patient_name,
                "diagnosis": diagnosis,
                "score": score,
                "full_report": report
            })
    
    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:20]  # Limit to top 20 results

# Create the main application
@ui.page('/')
def home():
    with ui.header().classes('bg-primary text-white'):
        ui.label('Genetic Workshop GUI').classes('text-h4 q-ml-md')
    
    with ui.tabs().classes('w-full') as tabs:
        pipeline_tab = ui.tab('Pipeline')
        search_tab = ui.tab('Search Reports')
        viewer_tab = ui.tab('Report Viewer')
    
    with ui.tab_panels(tabs, value=pipeline_tab).classes('w-full'):
        with ui.tab_panel(pipeline_tab):
            create_pipeline_tab()
        
        with ui.tab_panel(search_tab):
            create_search_tab()
        
        with ui.tab_panel(viewer_tab):
            create_viewer_tab()

def create_pipeline_tab():
    """Create the pipeline tab with Makefile functionality"""
    with ui.card().classes('w-full'):
        ui.label('Pipeline Operations').classes('text-h5')
        
        with ui.row():
            ui.button('Run Complete Pipeline', on_click=lambda: run_make_command('all'))
            ui.button('Clean Generated Files', on_click=lambda: run_make_command('clean'))
        
        ui.separator()
        
        with ui.expansion('Data Extraction', icon='mdi-database-export').classes('w-full'):
            with ui.column().classes('w-full gap-2'):
                ui.button('XML to JSON', on_click=lambda: run_make_command('xml2json'))
                ui.button('Extract Short Variants', on_click=lambda: run_make_command('extract-variants'))
                ui.button('Extract Copy Number Alterations', on_click=lambda: run_make_command('extract-cna'))
                ui.button('Extract Rearrangements', on_click=lambda: run_make_command('extract-rearrangements'))
                ui.button('Extract Microsatellite Instability', on_click=lambda: run_make_command('extract-msi'))
                ui.button('Extract Tumor Mutation Burden', on_click=lambda: run_make_command('extract-tmb'))
                ui.button('Extract Patient Medical Info', on_click=lambda: run_make_command('extract-pmi'))
                ui.button('Extract All Data', on_click=lambda: run_make_command('extract-all'))
                ui.button('Combine to Excel', on_click=lambda: run_make_command('combine-to-excel'))
        
        with ui.expansion('Oncoprinter Conversion', icon='mdi-file-export').classes('w-full'):
            with ui.column().classes('w-full gap-2'):
                ui.button('Convert to Oncoprinter Format', on_click=lambda: run_make_command('to-oncoprinter'))
                ui.button('Convert to Oncoprinter Clinical Format', on_click=lambda: run_make_command('to-oncoprinter-clinical'))
                
                with ui.row():
                    dx_input = ui.input(label='Diagnosis (e.g., lung)')
                    ui.button('Convert by Diagnosis', on_click=lambda: run_make_command('to-oncoprinter-dx', {'DX': dx_input.value}))
                
                with ui.row():
                    gene_input = ui.input(label='Gene (e.g., TP53)')
                    ui.button('Convert by Gene', on_click=lambda: run_make_command('to-oncoprinter-gene', {'GENE': gene_input.value}))
        
        with ui.expansion('Analysis Tools', icon='mdi-chart-bar').classes('w-full'):
            ui.button('Extract Gene Counts', on_click=lambda: run_make_command('extract-gene-counts'))

def create_search_tab():
    """Create the search tab for searching reports"""
    with ui.card().classes('w-full'):
        ui.label('Search Reports').classes('text-h5')
        
        search_input = ui.input(label='Search Query', placeholder='Enter patient ID, gene, mutation, diagnosis, etc.')
        search_results_container = ui.column().classes('w-full mt-4')
        
        async def perform_search():
            search_results_container.clear()
            
            if not search_input.value:
                ui.notify('Please enter a search query', type='warning')
                return
            
            # Load data if not already loaded
            reports_data = loaded_data["reports"]
            if not reports_data:
                with ui.spinner('Loading data...'):
                    reports_data = load_json_data()
            
            if not reports_data:
                ui.notify('No data available. Please run XML to JSON conversion first.', type='negative')
                return
            
            # Perform search
            with ui.spinner('Searching...'):
                results = search_reports(search_input.value, reports_data)
            
            # Display results
            if not results:
                with search_results_container:
                    ui.label('No results found').classes('text-subtitle1')
            else:
                with search_results_container:
                    ui.label(f'Found {len(results)} results').classes('text-subtitle1')
                    
                    for result in results:
                        with ui.card().classes('w-full q-mb-sm'):
                            with ui.row().classes('items-center justify-between'):
                                with ui.column().classes('q-pa-sm'):
                                    ui.label(f"Report ID: {result['report_id']}").classes('text-weight-bold')
                                    ui.label(f"Patient: {result['patient_name']}")
                                    ui.label(f"Diagnosis: {result['diagnosis']}")
                                    ui.label(f"Match Score: {result['score']}%")
                                
                                ui.button('View Report', on_click=partial(view_report, result['full_report']))
        
        ui.button('Search', on_click=perform_search).classes('mt-4')

def create_viewer_tab():
    """Create the report viewer tab"""
    with ui.card().classes('w-full'):
        ui.label('Report Viewer').classes('text-h5')
        ui.label('Select a report from the Search tab to view details').classes('text-subtitle1')
        
        global report_viewer_container
        report_viewer_container = ui.column().classes('w-full mt-4')

def view_report(report_data):
    """Display a single report in the viewer tab"""
    report_viewer_container.clear()
    
    if not report_data:
        with report_viewer_container:
            ui.label('No report data available').classes('text-subtitle1')
        return
    
    with report_viewer_container:
        # Report header
        with ui.card().classes('w-full q-mb-md'):
            report_id = report_data.get('report_id', 'Unknown')
            ui.label(f'Report ID: {report_id}').classes('text-h6')
            
            # Patient information
            patient = report_data.get('patient', {})
            with ui.row().classes('w-full'):
                with ui.column().classes('w-1/2'):
                    ui.label('Patient Information').classes('text-subtitle1 text-weight-bold')
                    ui.label(f"Name: {patient.get('name', 'N/A')}")
                    ui.label(f"Gender: {patient.get('gender', 'N/A')}")
                    ui.label(f"DOB: {patient.get('dob', 'N/A')}")
                
                with ui.column().classes('w-1/2'):
                    ui.label('Clinical Information').classes('text-subtitle1 text-weight-bold')
                    ui.label(f"Diagnosis: {patient.get('diagnosis', 'N/A')}")
                    ui.label(f"Specimen Site: {patient.get('specimen-site', 'N/A')}")
                    ui.label(f"Collection Date: {patient.get('collection-date', 'N/A')}")
        
        # Variants
        variants = report_data.get('variants', [])
        if variants:
            with ui.expansion('Short Variants', icon='mdi-dna').classes('w-full q-mb-md'):
                with ui.table().classes('w-full').style('max-height: 400px; overflow-y: auto;'):
                    ui.table.column('Gene', 'gene')
                    ui.table.column('Protein Effect', 'protein_effect')
                    ui.table.column('Functional Effect', 'functional_effect')
                    ui.table.column('Status', 'status')
                    ui.table.column('Position', 'position')
                    ui.table.column('CDS Effect', 'cds_effect')
                    
                    table_rows = [
                        {
                            'gene': v.get('@gene', 'N/A'),
                            'protein_effect': v.get('@protein-effect', 'N/A'),
                            'functional_effect': v.get('@functional-effect', 'N/A'),
                            'status': v.get('@status', 'N/A'),
                            'position': v.get('@position', 'N/A'),
                            'cds_effect': v.get('@cds-effect', 'N/A')
                        }
                        for v in variants
                    ]
                    ui.table.rows(table_rows)
        
        # Copy Number Alterations
        cnas = report_data.get('copy-number-alterations', [])
        if cnas:
            with ui.expansion('Copy Number Alterations', icon='mdi-dna').classes('w-full q-mb-md'):
                with ui.table().classes('w-full').style('max-height: 400px; overflow-y: auto;'):
                    ui.table.column('Gene', 'gene')
                    ui.table.column('Type', 'type')
                    ui.table.column('Copy Number', 'copy_number')
                    ui.table.column('Status', 'status')
                    
                    table_rows = [
                        {
                            'gene': c.get('@gene', 'N/A'),
                            'type': c.get('@type', 'N/A'),
                            'copy_number': c.get('@copy-number', 'N/A'),
                            'status': c.get('@status', 'N/A')
                        }
                        for c in cnas
                    ]
                    ui.table.rows(table_rows)
        
        # Rearrangements
        rearrangements = report_data.get('rearrangements', [])
        if rearrangements:
            with ui.expansion('Rearrangements', icon='mdi-dna').classes('w-full q-mb-md'):
                with ui.table().classes('w-full').style('max-height: 400px; overflow-y: auto;'):
                    ui.table.column('Targeted Gene', 'targeted_gene')
                    ui.table.column('Other Gene', 'other_gene')
                    ui.table.column('Type', 'type')
                    ui.table.column('Description', 'description')
                    ui.table.column('Status', 'status')
                    
                    table_rows = [
                        {
                            'targeted_gene': r.get('@targeted-gene', 'N/A'),
                            'other_gene': r.get('@other-gene', 'N/A'),
                            'type': r.get('@type', 'N/A'),
                            'description': r.get('@description', 'N/A'),
                            'status': r.get('@status', 'N/A')
                        }
                        for r in rearrangements
                    ]
                    ui.table.rows(table_rows)
        
        # Biomarkers
        biomarkers = report_data.get('biomarkers', {})
        if biomarkers:
            with ui.expansion('Biomarkers', icon='mdi-test-tube').classes('w-full q-mb-md'):
                with ui.column().classes('w-full'):
                    # MSI
                    msi = biomarkers.get('microsatellite-instability', {})
                    if msi:
                        ui.label('Microsatellite Instability').classes('text-subtitle1 text-weight-bold')
                        ui.label(f"Status: {msi.get('@status', 'N/A')}")
                        ui.label(f"Score: {msi.get('@score', 'N/A')}")
                    
                    # TMB
                    tmb = biomarkers.get('tumor-mutation-burden', {})
                    if tmb:
                        ui.separator()
                        ui.label('Tumor Mutation Burden').classes('text-subtitle1 text-weight-bold')
                        ui.label(f"Status: {tmb.get('@status', 'N/A')}")
                        ui.label(f"Score: {tmb.get('@score', 'N/A')} mutations/Mb")

# Main entry point
def main():
    ui.run(title="Genetic Workshop GUI", port=8080)

if __name__ == "__main__":
    main()
