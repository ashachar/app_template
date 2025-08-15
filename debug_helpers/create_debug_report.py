#!/usr/bin/env python3
"""
Creates an enhanced debug report by reading bug_report.xml and adding:
1. LLM instructions at the beginning
2. Tree visualization of selected files
3. File contents to each file entry
"""

import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List
import xml.dom.minidom
from repo_tree import RepositoryTree
import pyperclip
import json
import glob


def read_file_content(file_path: str) -> str:
    """Read and return the content of a file."""
    try:
        # Convert relative path to absolute path from app directory
        app_dir = Path(__file__).parent.parent  # debug_helpers -> app
        full_path = app_dir / file_path
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"


def extract_file_paths_from_xml(root: ET.Element) -> List[str]:
    """Extract all file paths from the XML."""
    paths = []
    for file_elem in root.findall('.//file/path'):
        if file_elem.text:
            path = file_elem.text.strip()
            paths.append(path)
    return paths


def build_tree_structure(paths: List[str]) -> str:
    """Build a tree visualization of the file paths using repo-tree."""
    # Create a temporary directory structure for repo-tree
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create the directory structure in temp directory
        for path in paths:
            file_path = Path(temp_dir) / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch()
        
        # Use repo-tree to generate the tree
        tree_output = RepositoryTree.display_tree(
            dir_path=temp_dir,
            print_tree=False,  # We want to return the string, not print it
            show_hidden=True,
            exclusion_patterns=[]
        )
        
        # Replace the temp directory path with the actual app path
        app_base = "/Users/amirshachar/Desktop/Amir/Projects/Personal/swifit/app"
        temp_base = os.path.basename(temp_dir)
        tree_output = tree_output.replace(temp_base, app_base)
        
        return tree_output


def create_llm_instructions() -> str:
    """Create the LLM instructions for the beginning of the report."""
    return """<instructions>
You're a first-class super intelligent engineer who is highly motivated to fix bugs in the most elegant way. I will describe to you below the project structure, the involved classes/methods/properties etc., and elaborate on how the project's elements intertwine with each other. Then I will describe you my goal or the problem I'm facing. Your answer will be a detailed and well-orchestrated reasoned explanation including the code that needs to change in order to achieve the goal. For example you can provide snippets of "Before" and "After" and explain how each of them contributes to achieving the goal.
</instructions>"""


def enrich_xml_report(input_path: str, output_path: str, copy_analysis_script: bool = False, analysis_results_path: str = None):
    """Read the XML report and enrich it with additional information."""
    # Parse the XML
    try:
        tree = ET.parse(input_path)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing XML: {e}")
        return
    
    # Extract file paths
    paths = extract_file_paths_from_xml(root)
    print(f"Found {len(paths)} files to process")
    
    # Add LLM instructions at the beginning
    instructions = ET.fromstring(create_llm_instructions())
    root.insert(0, instructions)
    
    # Add tree visualization
    tree_structure = build_tree_structure(paths)
    treemap_elem = ET.SubElement(root, 'treemap')
    treemap_elem.text = '\n' + tree_structure + '\n'
    
    # Find the overall_context to insert treemap after it
    overall_context = root.find('overall_context')
    if overall_context is not None:
        overall_index = list(root).index(overall_context)
        root.remove(treemap_elem)
        root.insert(overall_index + 1, treemap_elem)
    
    # Import analysis results if path provided or try to find them automatically
    if analysis_results_path:
        analysis_file = analysis_results_path
    else:
        # Try to find the most recent analysis file in Downloads
        downloads_path = Path.home() / 'Downloads'
        analysis_files = list(downloads_path.glob('job-id-refresh-analysis-*.json'))
        if analysis_files:
            # Get the most recent file
            analysis_file = max(analysis_files, key=lambda p: p.stat().st_mtime)
            print(f"Found analysis results: {analysis_file.name}")
        else:
            analysis_file = None
            print("No analysis results file found in Downloads folder")
    
    # Load and add analysis results if found
    if analysis_file and Path(analysis_file).exists():
        try:
            with open(analysis_file, 'r') as f:
                analysis_data = json.load(f)
            
            # Find the analysis_script/results element
            analysis_script_elem = root.find('.//analysis_script')
            if analysis_script_elem is not None:
                results_elem = analysis_script_elem.find('results')
                if results_elem is None:
                    results_elem = ET.SubElement(analysis_script_elem, 'results')
                
                # Format the JSON nicely
                results_elem.text = '\n' + json.dumps(analysis_data, indent=2) + '\n'
                print("Added analysis results to report")
        except Exception as e:
            print(f"Error loading analysis results: {e}")
    
    # Process each file
    for file_elem in root.findall('.//file'):
        path_elem = file_elem.find('path')
        if path_elem is not None and path_elem.text:
            file_path = path_elem.text.strip()
            
            # Read file content
            content = read_file_content(file_path)
            
            # Add file content
            content_elem = ET.SubElement(file_elem, 'content')
            # Use CDATA for content to preserve formatting
            content_elem.text = content
    
    # Write the enriched XML
    # Pretty print the XML
    xml_str = ET.tostring(root, encoding='unicode')
    dom = xml.dom.minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent='    ')
    
    # Remove empty lines
    lines = [line for line in pretty_xml.split('\n') if line.strip()]
    pretty_xml = '\n'.join(lines[1:])  # Skip XML declaration added by toprettyxml
    
    # Add original XML declaration
    final_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + pretty_xml
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_xml)
    
    # Check if we should copy analysis script instead
    if copy_analysis_script:
        # Look for analysis script in the XML
        analysis_script_elem = root.find('.//analysis_script/code')
        if analysis_script_elem is not None and analysis_script_elem.text:
            script_content = analysis_script_elem.text.strip()
            try:
                pyperclip.copy(script_content)
                clipboard_msg = "✓ Analysis script copied to clipboard"
            except Exception as e:
                clipboard_msg = f"✗ Could not copy analysis script to clipboard: {e}"
        else:
            # If no script in XML, try to read from file
            analysis_script_path = Path(__file__).parent.parent / 'debug_artifacts' / 'analysis_script.js'
            if analysis_script_path.exists():
                try:
                    script_content = analysis_script_path.read_text()
                    pyperclip.copy(script_content)
                    clipboard_msg = "✓ Analysis script copied to clipboard (from file)"
                except Exception as e:
                    clipboard_msg = f"✗ Could not copy analysis script to clipboard: {e}"
            else:
                clipboard_msg = "✗ No analysis script found to copy"
    else:
        # Copy the full XML report
        try:
            pyperclip.copy(final_xml)
            clipboard_msg = "✓ Full report copied to clipboard"
        except Exception as e:
            clipboard_msg = f"✗ Could not copy to clipboard: {e}"
    
    print(f"\nSuccessfully created {output_path}")
    print("Added:")
    print("  - LLM instructions")
    print(f"  - Tree visualization of {len(paths)} files")
    print("  - File contents for all files")
    print(f"\n{clipboard_msg}")


def main():
    """Main function to create enhanced debug report."""
    import sys
    
    input_path = 'debug_artifacts/bug_report.xml'
    output_path = 'debug_artifacts/enriched_bug_report.xml'
    
    # Check for command line argument to copy analysis script
    copy_analysis_script = '--copy-analysis-script' in sys.argv
    
    # Check for analysis results path argument
    analysis_results_path = None
    for i, arg in enumerate(sys.argv):
        if arg == '--analysis-results' and i + 1 < len(sys.argv):
            analysis_results_path = sys.argv[i + 1]
            break
    
    # Check if input file exists
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found in current directory")
        return
    
    print("Creating enhanced debug report...")
    print("-" * 50)
    
    enrich_xml_report(input_path, output_path, copy_analysis_script, analysis_results_path)


if __name__ == "__main__":
    main()