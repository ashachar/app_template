#!/usr/bin/env python3
"""
Generic Bug Report XML Updater

This script provides a reusable way to update bug report XML files with:
- New hypotheses (moving current to past if needed)
- Log file annotations
- Diagnostic script references
- Proper XML formatting

Usage:
    python debug_helpers/bug_report_xml_updater.py \
        --xml-file debug_artifacts/bug_report_ISSUE-123.xml \
        --hypothesis "New hypothesis text here" \
        --logged-files "file1.ts,file2.tsx,file3.py" \
        --analysis-script "$(cat diagnostic_script.js)" \
        --issue-id "ISSUE-123"
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import argparse
import os
import sys
from datetime import datetime


class BugReportXMLUpdater:
    def __init__(self, xml_file_path):
        self.xml_file_path = xml_file_path
        self.root = None
        
    def load_xml(self):
        """Load and parse the XML file."""
        try:
            if os.path.exists(self.xml_file_path):
                # Load existing XML file
                tree = ET.parse(self.xml_file_path)
                self.root = tree.getroot()
                print(f"✅ Loaded existing XML: {self.xml_file_path}")
            else:
                print(f"❌ XML file not found: {self.xml_file_path}")
                return False
        except ET.ParseError as e:
            print(f"❌ XML parsing error: {e}")
            return False
        except Exception as e:
            print(f"❌ Error loading XML: {e}")
            return False
            
        return True
    
    def move_current_to_past_hypothesis(self):
        """Move current hypothesis to past_hypotheses if it exists."""
        current_hyp = self.root.find('current_hypothesis')
        
        if current_hyp is not None and current_hyp.text and current_hyp.text.strip():
            # Find or create past_hypotheses element
            past_hyps = self.root.find('past_hypotheses')
            if past_hyps is None:
                past_hyps = ET.SubElement(self.root, 'past_hypotheses')
            
            # Create a new hypothesis entry with timestamp
            past_hyp = ET.SubElement(past_hyps, 'hypothesis')
            past_hyp.set('timestamp', datetime.now().isoformat())
            past_hyp.text = current_hyp.text
            
            print("📋 Moved current hypothesis to past_hypotheses")
            return True
        
        return False
            
    def update_hypothesis(self, new_hypothesis):
        """Update the current hypothesis."""
        if not new_hypothesis or not new_hypothesis.strip():
            print("⚠️  No hypothesis provided, skipping hypothesis update")
            return
            
        # Move existing hypothesis to past if it exists
        self.move_current_to_past_hypothesis()
        
        # Find or create current_hypothesis element
        current_hyp = self.root.find('current_hypothesis')
        if current_hyp is None:
            current_hyp = ET.SubElement(self.root, 'current_hypothesis')
        
        # Set the new hypothesis
        current_hyp.text = new_hypothesis.strip()
        print("✅ Updated current hypothesis")
    
    def add_logs_to_files(self, logged_files):
        """Add logs element to specified files."""
        if not logged_files:
            print("⚠️  No logged files specified, skipping logs update")
            return
            
        files_elem = self.root.find('files_relevant_to_issue')
        if files_elem is None:
            print("⚠️  No files_relevant_to_issue section found")
            return
        
        files_updated = 0
        for file_elem in files_elem.findall('file'):
            path_elem = file_elem.find('path')
            if path_elem is not None and path_elem.text in logged_files:
                logs_elem = file_elem.find('logs')
                if logs_elem is None:
                    logs_elem = ET.SubElement(file_elem, 'logs')
                    logs_elem.text = f'Strategic debug logs added - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
                    files_updated += 1
                    
        print(f"✅ Added log annotations to {files_updated} files")
    
    def add_analysis_script_code(self, js_script_code):
        """Add the diagnostic JS script code directly to XML."""
        if not js_script_code:
            print("⚠️  No JS script code specified, skipping script code")
            return
            
        # Find or create analysis_script element
        analysis_script_elem = self.root.find('analysis_script')
        if analysis_script_elem is None:
            analysis_script_elem = ET.SubElement(self.root, 'analysis_script')
        
        # Find or create code sub-element
        code_elem = analysis_script_elem.find('code')
        if code_elem is None:
            code_elem = ET.SubElement(analysis_script_elem, 'code')
        
        # Set the script code (wrapped in CDATA to preserve formatting)
        code_elem.text = js_script_code.strip()
        print("✅ Added analysis script code to XML")
    
    def remove_old_js_script_reference(self):
        """Remove obsolete js_script element if it exists."""
        js_script_elem = self.root.find('js_script')
        if js_script_elem is not None:
            self.root.remove(js_script_elem)
            print("🗑️  Removed obsolete js_script reference")
    
    def add_metadata_update(self):
        """Add or update last_updated metadata.""" 
        metadata_elem = self.root.find('metadata')
        if metadata_elem is None:
            metadata_elem = ET.SubElement(self.root, 'metadata')
            
        last_updated = metadata_elem.find('last_updated')
        if last_updated is None:
            last_updated = ET.SubElement(metadata_elem, 'last_updated')
            
        last_updated.text = datetime.now().isoformat()
        print("✅ Updated metadata timestamp")
    
    def save_xml(self, output_path=None):
        """Save the updated XML to file."""
        if output_path is None:
            output_path = self.xml_file_path
            
        try:
            # Convert to pretty XML string
            rough_string = ET.tostring(self.root, 'unicode')
            reparsed = minidom.parseString(rough_string)
            pretty_xml = reparsed.toprettyxml(indent="  ")
            
            # Remove extra blank lines
            lines = [line for line in pretty_xml.split('\n') if line.strip()]
            pretty_xml = '\n'.join(lines)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(pretty_xml)
            
            print(f"✅ Saved updated XML: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving XML: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description='Update bug report XML with hypothesis, logs, and diagnostic script info',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Update with new hypothesis only
    python debug_helpers/bug_report_xml_updater.py \\
        --xml-file debug_artifacts/bug_report_COMP-001.xml \\
        --hypothesis "Missing data propagation in props chain"
        
    # Full update with all options
    python debug_helpers/bug_report_xml_updater.py \\
        --xml-file debug_artifacts/bug_report_COMP-001.xml \\
        --hypothesis "Missing data propagation in props chain" \\
        --logged-files "useExploreProps.ts,filterBarProps.ts,useSearchOrchestrator.ts" \\
        --analysis-script "$(cat diagnostic_script.js)" \\
        --issue-id "COMP-001"
        """
    )
    
    parser.add_argument('--xml-file', required=True,
                      help='Path to the bug report XML file')
    parser.add_argument('--hypothesis', 
                      help='New hypothesis text to add')
    parser.add_argument('--logged-files',
                      help='Comma-separated list of files that had debug logs added')
    parser.add_argument('--analysis-script',
                      help='The diagnostic JavaScript script code content')  
    parser.add_argument('--issue-id',
                      help='Issue ID for validation and naming')
    parser.add_argument('--output',
                      help='Output file path (defaults to input file)')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.xml_file):
        print(f"❌ XML file not found: {args.xml_file}")
        sys.exit(1)
    
    # Parse logged files list
    logged_files = []
    if args.logged_files:
        logged_files = [f.strip() for f in args.logged_files.split(',') if f.strip()]
    
    # Initialize updater
    updater = BugReportXMLUpdater(args.xml_file)
    
    # Load XML
    if not updater.load_xml():
        sys.exit(1)
    
    # Perform updates
    print("\n🔄 Updating bug report XML...")
    
    if args.hypothesis:
        updater.update_hypothesis(args.hypothesis)
    
    if logged_files:
        updater.add_logs_to_files(logged_files)
    
    if args.analysis_script:
        updater.add_analysis_script_code(args.analysis_script)
    
    # Remove obsolete js_script references
    updater.remove_old_js_script_reference()
    
    # Always add metadata
    updater.add_metadata_update()
    
    # Save results
    output_path = args.output or args.xml_file
    if updater.save_xml(output_path):
        print(f"\n✅ Bug report XML updated successfully!")
        print(f"📁 Location: {output_path}")
    else:
        print("\n❌ Failed to save XML")
        sys.exit(1)


if __name__ == "__main__":
    main()