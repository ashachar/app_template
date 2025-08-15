#!/usr/bin/env python3
"""
Extract analysis script from bug report XML and copy to clipboard
Usage: python debug_helpers/extract_analysis_script.py debug_artifacts/bug_report_ISSUE-123.xml
"""

import xml.etree.ElementTree as ET
import sys
import subprocess
import os

def extract_and_copy_script(xml_file):
    """Extract analysis script from XML and copy to clipboard."""
    try:
        # Parse XML file
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Find analysis script code
        analysis_script = root.find('analysis_script')
        if analysis_script is None:
            print("❌ No analysis_script element found in XML")
            return False
        
        code_elem = analysis_script.find('code')
        if code_elem is None or not code_elem.text:
            print("❌ No code found in analysis_script element")
            return False
        
        # Get the script code
        script_code = code_elem.text.strip()
        
        # Copy to clipboard using pbcopy (macOS)
        try:
            process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            process.communicate(script_code.encode('utf-8'))
            
            if process.returncode == 0:
                print("✅ Analysis script copied to clipboard")
                print(f"📄 Script length: {len(script_code)} characters")
                print("📋 Ready to paste in browser console")
                return True
            else:
                print("❌ Failed to copy to clipboard")
                return False
        except FileNotFoundError:
            print("❌ pbcopy not found (macOS only)")
            print("📄 Script code:")
            print(script_code)
            return False
            
    except ET.ParseError as e:
        print(f"❌ XML parsing error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python debug_helpers/extract_analysis_script.py <xml_file>")
        print("Example: python debug_helpers/extract_analysis_script.py debug_artifacts/bug_report_COMP-FILTER-001.xml")
        sys.exit(1)
    
    xml_file = sys.argv[1]
    
    if not os.path.exists(xml_file):
        print(f"❌ File not found: {xml_file}")
        sys.exit(1)
    
    success = extract_and_copy_script(xml_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()