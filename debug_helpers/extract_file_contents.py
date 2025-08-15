#!/usr/bin/env python3
"""
Extract File Contents Utility

This script reads a list of file paths and extracts their contents,
preparing them for injection into bug report XML files.

Usage:
    python debug_helpers/extract_file_contents.py \
        --file-paths "file1.ts,file2.tsx,file3.py" \
        --xml-file debug_artifacts/bug_report_ISSUE-123.xml
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path


def read_file_safely(file_path):
    """Read file content safely, handling encoding issues."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with latin-1 if utf-8 fails
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            return f"[Error reading file: {e}]"
    except Exception as e:
        return f"[Error reading file: {e}]"


def extract_file_contents(file_paths):
    """Extract contents from a list of file paths."""
    file_contents = {}
    
    for file_path in file_paths:
        file_path = file_path.strip()
        if not file_path:
            continue
            
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            file_contents[file_path] = "[File not found]"
            continue
        
        # Read file content
        content = read_file_safely(file_path)
        file_contents[file_path] = content
        print(f"✅ Read content from: {file_path} ({len(content)} chars)")
    
    return file_contents


def update_xml_with_contents(xml_file, file_contents):
    """Call the bug_report_xml_updater.py with file contents."""
    # Prepare the file contents as a formatted string for the updater
    # We'll pass it as part of the --file-contents parameter
    
    # First, let's modify the XML directly since the updater doesn't have this feature yet
    import xml.etree.ElementTree as ET
    from xml.dom import minidom
    
    try:
        # Load XML
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Find files_relevant_to_issue section
        files_elem = root.find('files_relevant_to_issue')
        if files_elem is None:
            print("⚠️  No files_relevant_to_issue section found in XML")
            return False
        
        # Update each file element with content
        files_updated = 0
        for file_elem in files_elem.findall('file'):
            path_elem = file_elem.find('path')
            if path_elem is not None and path_elem.text in file_contents:
                # Check if content element already exists
                content_elem = file_elem.find('content')
                if content_elem is None:
                    content_elem = ET.SubElement(file_elem, 'content')
                
                # Set the content (escape special XML characters)
                content_elem.text = file_contents[path_elem.text]
                files_updated += 1
        
        # Save the updated XML
        rough_string = ET.tostring(root, 'unicode')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        
        # Remove extra blank lines
        lines = [line for line in pretty_xml.split('\n') if line.strip()]
        pretty_xml = '\n'.join(lines)
        
        # Save to file
        with open(xml_file, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        
        print(f"✅ Updated {files_updated} files with content in XML")
        return True
        
    except Exception as e:
        print(f"❌ Error updating XML: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Extract file contents and update bug report XML',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Extract contents from files listed in XML
    python debug_helpers/extract_file_contents.py \\
        --file-paths "src/components/CompanyFilter.tsx,src/api/companyService.ts" \\
        --xml-file debug_artifacts/bug_report_COMP-001.xml
        """
    )
    
    parser.add_argument('--file-paths', required=True,
                      help='Comma-separated list of file paths to extract content from')
    parser.add_argument('--xml-file', required=True,
                      help='Path to the bug report XML file to update')
    
    args = parser.parse_args()
    
    # Validate XML file exists
    if not os.path.exists(args.xml_file):
        print(f"❌ XML file not found: {args.xml_file}")
        sys.exit(1)
    
    # Parse file paths
    file_paths = [f.strip() for f in args.file_paths.split(',') if f.strip()]
    
    if not file_paths:
        print("❌ No file paths provided")
        sys.exit(1)
    
    print(f"\n📁 Extracting contents from {len(file_paths)} files...")
    
    # Extract file contents
    file_contents = extract_file_contents(file_paths)
    
    # Update XML with contents
    print(f"\n📝 Updating XML with file contents...")
    if update_xml_with_contents(args.xml_file, file_contents):
        print(f"\n✅ Successfully updated XML with file contents!")
        print(f"📁 Location: {args.xml_file}")
    else:
        print("\n❌ Failed to update XML with contents")
        sys.exit(1)


if __name__ == "__main__":
    main()