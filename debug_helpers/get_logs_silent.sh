#!/bin/bash

# Silent version that runs without Terminal window
# This script is called by the macOS keyboard shortcut
# Updates XML bug report with logs and JS results

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# Change to app directory
cd "$APP_DIR"

# Find the most recent bug_report_*.xml file in debug_artifacts
DEBUG_DIR="$APP_DIR/debug_artifacts"
if [ ! -d "$DEBUG_DIR" ]; then
    osascript -e 'display alert "Error" message "debug_artifacts directory not found" as critical'
    exit 1
fi

# Get the most recent bug_report_*.xml file
LATEST_XML=$(ls -t "$DEBUG_DIR"/bug_report_*.xml 2>/dev/null | head -1)

if [ -z "$LATEST_XML" ]; then
    osascript -e 'display alert "Error" message "No bug report XML files found in debug_artifacts/" as critical'
    exit 1
fi

# Extract issue_id from the XML
ISSUE_ID=$(grep -oP '(?<=<issue_id>)[^<]+' "$LATEST_XML" 2>/dev/null || grep -o '<issue_id>[^<]*</issue_id>' "$LATEST_XML" | sed 's/<[^>]*>//g')

if [ -z "$ISSUE_ID" ]; then
    osascript -e 'display alert "Error" message "Could not extract issue_id from XML" as critical'
    exit 1
fi

# Use the issue_id as the prefix for log search
PREFIX="[DEBUG-$ISSUE_ID]"

# Check if log file exists
if [ ! -f "consolidated_logs/latest.log" ]; then
    osascript -e 'display alert "Error" message "Log file not found at consolidated_logs/latest.log" as critical'
    exit 1
fi

# Create a temporary file for the updated XML
TEMP_XML=$(mktemp)

# Run the get_prefixed_logs script to get logs
FULL_OUTPUT=$(./get_prefixed_logs.sh "$PREFIX" -o 2>&1)

# Extract just the log entries
LOG_OUTPUT=$(echo "$FULL_OUTPUT" | awk '
    # Pattern for log entry start
    /^\[[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}Z\]/ {
        # This is a log entry, print it
        if (NR > 1 && in_logs) print ""  # Add blank line between entries
        print
        in_logs = 1
        in_entry = 1
        next
    }
    # If we are in a log entry and this line is not empty and not a new log entry
    in_entry && /^[^\[]/ && NF > 0 {
        # This is a continuation of the current log entry
        print
        next
    }
    # Empty line or new section - end current entry
    {
        in_entry = 0
    }
')

# Check for JS script results in Downloads
JSON_RESULTS=""
DOWNLOADS_DIR="$HOME/Downloads"
if [ -d "$DOWNLOADS_DIR" ]; then
    # Look for analysis_report_<issue_id>.json files created in the last 3 minutes
    ANALYSIS_FILE=$(find "$DOWNLOADS_DIR" -name "analysis_report_${ISSUE_ID}.json" -type f -mmin -3 2>/dev/null | head -1)
    
    if [ -n "$ANALYSIS_FILE" ] && [ -f "$ANALYSIS_FILE" ]; then
        JSON_RESULTS=$(cat "$ANALYSIS_FILE" 2>/dev/null)
    else
        # Fallback: Find any recent JSON file if specific one not found
        RECENT_JSON_FILES=$(find "$DOWNLOADS_DIR" -name "*.json" -type f -mmin -3 2>/dev/null | sort -t/ -k9 | head -1)
        if [ -n "$RECENT_JSON_FILES" ] && [ -f "$RECENT_JSON_FILES" ]; then
            JSON_RESULTS=$(cat "$RECENT_JSON_FILES" 2>/dev/null)
        fi
    fi
fi

# Export the environment variables for Python
export LOG_OUTPUT="$LOG_OUTPUT"
export JSON_RESULTS="$JSON_RESULTS"

# Process the XML file
python3 - "$LATEST_XML" "$TEMP_XML" << 'PYTHON_SCRIPT'
import sys
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import re
import os
import html

xml_file = sys.argv[1]
output_file = sys.argv[2]

# Read the XML file content first to check for common issues
try:
    with open(xml_file, 'r', encoding='utf-8') as f:
        xml_content = f.read()
    
    # Common issue: backslash characters in JavaScript code within XML
    # These are not XML special characters but can cause issues in some contexts
    # We'll handle them by using proper XML escaping
    
    # Fix backslash-exclamation which appears to be a common pattern
    # This is likely from JavaScript negation operators
    xml_content = xml_content.replace('\\!', '!')
    
    # Parse the fixed XML
    try:
        root = ET.fromstring(xml_content)
        tree = ET.ElementTree(root)
    except ET.ParseError as e:
        # If still failing, try a more aggressive approach
        # Escape content within message tags
        def escape_message_content(match):
            tag_open = match.group(1)
            content = match.group(2)
            tag_close = match.group(3)
            # Use HTML escaping which handles most cases
            escaped = html.escape(content, quote=False)
            return tag_open + escaped + tag_close
        
        # Apply to message tags
        xml_content = re.sub(r'(<message>)(.*?)(</message>)', escape_message_content, xml_content, flags=re.DOTALL)
        
        try:
            root = ET.fromstring(xml_content)
            tree = ET.ElementTree(root)
        except Exception as e2:
            print(f"Error parsing XML after fixes: {e2}")
            print("First few lines of XML:")
            print('\n'.join(xml_content.split('\n')[:20]))
            sys.exit(1)

except Exception as e:
    print(f"Error reading XML file: {e}")
    sys.exit(1)

# Get the logs from environment
logs = os.environ.get('LOG_OUTPUT', '')
js_results = os.environ.get('JSON_RESULTS', '')

# Process logs - group by file
if logs:
    # Parse log entries to extract file information
    log_lines = logs.strip().split('\n')
    file_logs = {}
    
    for line in log_lines:
        # Look for [DEBUG-ISSUE_ID] patterns
        if '[DEBUG-' in line:
            # Try to extract file path from the log
            # Common patterns in logs might include file paths
            # This is a simplified approach - adjust based on actual log format
            
            # For now, we'll just collect all logs
            # In a real implementation, you'd parse the logs to determine which file they came from
            if 'all_logs' not in file_logs:
                file_logs['all_logs'] = []
            file_logs['all_logs'].append(line)

# Update the XML - add log results to files
files_element = root.find('.//files_relevant_to_issue')
if files_element is not None and logs:
    for file_elem in files_element.findall('file'):
        # Check if this file already has logs
        logs_elem = file_elem.find('logs')
        if logs_elem is not None:
            # Add a results element to each log
            for log_elem in logs_elem.findall('log'):
                # Create result element if it doesn't exist
                result_elem = log_elem.find('result')
                if result_elem is None:
                    result_elem = ET.SubElement(log_elem, 'result')
                    # Add relevant log lines here
                    # This is simplified - in practice you'd match logs to specific log statements
                    result_elem.text = "Log output collected - see consolidated results"

# Update analysis script results  
analysis_script_elem = root.find('.//analysis_script')
if analysis_script_elem is not None and js_results:
    result_elem = analysis_script_elem.find('results')
    if result_elem is None:
        result_elem = ET.SubElement(analysis_script_elem, 'results')
    result_elem.text = js_results

# Add a consolidated log section if it doesn't exist
if logs:
    log_results_elem = root.find('log_results')
    if log_results_elem is None:
        log_results_elem = ET.SubElement(root, 'log_results')
    
    # Clear any existing content
    log_results_elem.clear()
    
    # Truncate logs if they exceed 30K characters
    MAX_LOG_LENGTH = 30000
    if len(logs) > MAX_LOG_LENGTH:
        log_results_elem.text = logs[:MAX_LOG_LENGTH] + '\n\n[... truncated after 30K chars]'
    else:
        log_results_elem.text = logs

# Pretty print the XML
def prettify(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

# Write the pretty-printed XML
with open(output_file, 'w', encoding='utf-8') as f:
    pretty_xml = prettify(root)
    # Remove extra blank lines
    pretty_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])
    f.write(pretty_xml)

PYTHON_SCRIPT

# Check if Python script succeeded
if [ $? -ne 0 ]; then
    osascript -e 'display alert "Error" message "Failed to update XML with logs" as critical'
    rm -f "$TEMP_XML"
    exit 1
fi

# Copy the updated XML back to the original location
cp "$TEMP_XML" "$LATEST_XML"

# Copy the updated XML to clipboard
cat "$LATEST_XML" | pbcopy

# Clean up
rm -f "$TEMP_XML"

# Extract match count if possible
MATCHES=$(echo "$FULL_OUTPUT" | grep "Total matches:" | awk '{print $3}')

# Show notification
if [ -n "$JSON_RESULTS" ]; then
    if [ -n "$MATCHES" ]; then
        osascript -e "display notification \"Updated XML with $MATCHES log entries + JS results\" with title \"Bug Report Updated\" sound name \"Glass\""
    else
        osascript -e "display notification \"Updated XML with logs and JS results\" with title \"Bug Report Updated\" sound name \"Glass\""
    fi
else
    if [ -n "$MATCHES" ]; then
        osascript -e "display notification \"Updated XML with $MATCHES log entries\" with title \"Bug Report Updated\" sound name \"Glass\""
    else
        osascript -e "display notification \"Bug report XML updated and copied to clipboard\" with title \"Bug Report Updated\" sound name \"Glass\""
    fi
fi

# Wait a moment for clipboard to be ready
sleep 0.2

# Simulate Command+V to paste
osascript -e 'tell application "System Events" to keystroke "v" using command down'