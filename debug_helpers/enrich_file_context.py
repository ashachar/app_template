#!/usr/bin/env python3
"""
Enriches bug_report.md by adding file contents to each <file> element.
Reads the file paths from the XML structure and adds the actual file content.
"""

import os
import re
from pathlib import Path


def read_file_content(file_path):
    """Read and return the content of a file."""
    try:
        # Convert relative path to absolute path from app directory
        app_dir = Path(__file__).parent.parent  # debug_helpers -> app
        full_path = app_dir / file_path
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Escape XML special characters
        content = content.replace('&', '&amp;')
        content = content.replace('<', '&lt;')
        content = content.replace('>', '&gt;')
        content = content.replace('"', '&quot;')
        content = content.replace("'", '&apos;')
        
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"


def enrich_bug_report(report_path='bug_report.md'):
    """Read bug_report.md and enrich each <file> element with content."""
    
    # Read the bug report
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {report_path} not found in current directory")
        return
    
    # Find the <files> section
    files_match = re.search(r'<files>(.*?)</files>', content, re.DOTALL)
    if not files_match:
        print("Error: No <files> section found in bug_report.md")
        return
    
    files_section = files_match.group(1)
    
    # Find all <file> elements
    file_pattern = re.compile(r'<file>\s*<path>(.*?)</path>\s*<context>(.*?)</context>\s*</file>', re.DOTALL)
    
    enriched_files = []
    
    for match in file_pattern.finditer(files_section):
        file_path = match.group(1).strip()
        context = match.group(2).strip()
        
        print(f"Reading: {file_path}")
        file_content = read_file_content(file_path)
        
        # Create enriched file element
        enriched_file = f"""    <file>
        <path>{file_path}</path>
        <context>{context}</context>
        <content><![CDATA[
{file_content}
]]></content>
    </file>"""
        
        enriched_files.append(enriched_file)
    
    # Replace the files section with enriched version
    new_files_section = f"<files>\n{chr(10).join(enriched_files)}\n</files>"
    
    # Replace in the original content
    new_content = content.replace(files_match.group(0), new_files_section)
    
    # Write to a new file
    output_path = 'bug_report_enriched.md'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"\nEnriched bug report saved to: {output_path}")
    print(f"Total files enriched: {len(enriched_files)}")


def main():
    """Main function."""
    print("Enriching bug_report.md with file contents...")
    print("-" * 50)
    
    # Check if bug_report.md exists
    if not os.path.exists('bug_report.md'):
        print("Error: bug_report.md not found in current directory")
        print("Please run this script from the app directory where bug_report.md is located")
        return
    
    enrich_bug_report()


if __name__ == "__main__":
    main()