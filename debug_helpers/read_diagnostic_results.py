#!/usr/bin/env python3
"""
Read and display diagnostic results saved by globalDiagnostics.ts
This script can be used by the explore.md command to automatically include diagnostic results.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

def find_latest_diagnostic_file(diagnostic_type='infinite-loop'):
    """Find the most recent diagnostic results file."""
    # Look in Downloads folder (where browser saves files)
    downloads_path = Path.home() / 'Downloads'
    
    # Pattern to match diagnostic files
    pattern = f'diagnostic_results_{diagnostic_type}_*.json'
    
    # Find all matching files
    matching_files = list(downloads_path.glob(pattern))
    
    if not matching_files:
        return None
    
    # Sort by modification time and get the latest
    latest_file = max(matching_files, key=lambda f: f.stat().st_mtime)
    return latest_file

def format_diagnostic_results(data):
    """Format diagnostic results for display."""
    output = []
    
    output.append(f"Diagnostic Type: {data.get('type', 'Unknown')}")
    output.append(f"Timestamp: {data.get('timestamp', 'Unknown')}")
    output.append(f"URL: {data.get('url', 'Unknown')}")
    output.append("")
    
    summary = data.get('summary', {})
    output.append("Summary:")
    output.append(f"  Total Tests: {summary.get('totalTests', 0)}")
    output.append(f"  Passed: {summary.get('passed', 0)}")
    output.append(f"  Failed: {summary.get('failed', 0)}")
    output.append(f"  All Passed: {summary.get('allPassed', False)}")
    output.append("")
    
    output.append("Test Results:")
    for result in data.get('results', []):
        status = "✅ PASS" if result.get('passed') else "❌ FAIL"
        output.append(f"  {result.get('test')}: {status}")
        if isinstance(result.get('details'), dict):
            for key, value in result['details'].items():
                output.append(f"    - {key}: {value}")
        else:
            output.append(f"    - {result.get('details')}")
        output.append("")
    
    # Include sample of debug logs
    logs = data.get('logs', [])
    if logs:
        output.append(f"Debug Logs (showing last 10 of {len(logs)}):")
        for log in logs[-10:]:
            output.append(f"  {log}")
    
    return "\n".join(output)

def save_to_bug_report_section(diagnostic_results):
    """Create a CDATA section for bug_report.xml"""
    return f"""<![CDATA[
{diagnostic_results}
]]>"""

def main():
    diagnostic_type = sys.argv[1] if len(sys.argv) > 1 else 'infinite-loop'
    
    # Find the latest diagnostic file
    diagnostic_file = find_latest_diagnostic_file(diagnostic_type)
    
    if not diagnostic_file:
        print(f"No diagnostic results found for type: {diagnostic_type}")
        print("Looking in: ~/Downloads/diagnostic_results_*.json")
        return 1
    
    print(f"Found diagnostic file: {diagnostic_file}")
    
    # Read and parse the file
    try:
        with open(diagnostic_file, 'r') as f:
            data = json.load(f)
        
        # Format the results
        formatted_results = format_diagnostic_results(data)
        print("\n" + "="*50)
        print(formatted_results)
        print("="*50 + "\n")
        
        # Save formatted results for easy inclusion in bug report
        output_file = Path('debug_artifacts') / f'formatted_{diagnostic_type}_results.txt'
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(formatted_results)
        
        print(f"Formatted results saved to: {output_file}")
        
        # Also create CDATA version
        cdata_file = Path('debug_artifacts') / f'{diagnostic_type}_results_cdata.txt'
        with open(cdata_file, 'w') as f:
            f.write(save_to_bug_report_section(formatted_results))
        
        print(f"CDATA version saved to: {cdata_file}")
        
    except Exception as e:
        print(f"Error reading diagnostic file: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())