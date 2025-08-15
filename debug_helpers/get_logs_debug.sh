#!/bin/bash

# Debug version to diagnose keyboard shortcut issues
# This writes debug info to a log file

DEBUG_LOG="/tmp/get_logs_debug.log"
echo "=== Debug log started at $(date) ===" > "$DEBUG_LOG"

# Log environment
echo "Current user: $(whoami)" >> "$DEBUG_LOG"
echo "Current directory: $(pwd)" >> "$DEBUG_LOG"
echo "Script called with args: $@" >> "$DEBUG_LOG"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "Script dir: $SCRIPT_DIR" >> "$DEBUG_LOG"
echo "App dir: $APP_DIR" >> "$DEBUG_LOG"

# Change to app directory
cd "$APP_DIR"
echo "Changed to directory: $(pwd)" >> "$DEBUG_LOG"

# Check if consolidated_logs exists
if [ -d "consolidated_logs" ]; then
    echo "consolidated_logs directory exists" >> "$DEBUG_LOG"
    ls -la consolidated_logs/ >> "$DEBUG_LOG" 2>&1
else
    echo "ERROR: consolidated_logs directory NOT found" >> "$DEBUG_LOG"
fi

# Check if get_prefixed_logs.sh exists
if [ -f "./get_prefixed_logs.sh" ]; then
    echo "get_prefixed_logs.sh exists" >> "$DEBUG_LOG"
else
    echo "ERROR: get_prefixed_logs.sh NOT found" >> "$DEBUG_LOG"
fi

# Use AppleScript to get user input
echo "Showing dialog..." >> "$DEBUG_LOG"
PREFIX=$(osascript <<EOD 2>&1
set dialogResult to display dialog "Enter log prefix to search for:" default answer "[DEBUG-" buttons {"Cancel", "Search"} default button "Search" with icon note
if button returned of dialogResult is "Search" then
    return text returned of dialogResult
else
    error number -128
end if
EOD
)

DIALOG_EXIT_CODE=$?
echo "Dialog exit code: $DIALOG_EXIT_CODE" >> "$DEBUG_LOG"
echo "Dialog result: $PREFIX" >> "$DEBUG_LOG"

# Check if user cancelled
if [ $DIALOG_EXIT_CODE -ne 0 ]; then
    echo "User cancelled dialog" >> "$DEBUG_LOG"
    osascript -e 'display notification "Search cancelled" with title "Log Search"'
    exit 0
fi

# Check if log file exists
if [ ! -f "consolidated_logs/latest.log" ]; then
    echo "ERROR: Log file not found at consolidated_logs/latest.log" >> "$DEBUG_LOG"
    osascript -e 'display alert "Error" message "Log file not found at consolidated_logs/latest.log" as critical'
    exit 1
fi

echo "Running get_prefixed_logs.sh with prefix: $PREFIX" >> "$DEBUG_LOG"

# Run the get_prefixed_logs script and capture output
OUTPUT=$(./get_prefixed_logs.sh "$PREFIX" 2>&1)
EXIT_CODE=$?

echo "get_prefixed_logs.sh exit code: $EXIT_CODE" >> "$DEBUG_LOG"
echo "Output length: ${#OUTPUT}" >> "$DEBUG_LOG"
echo "First 500 chars of output:" >> "$DEBUG_LOG"
echo "${OUTPUT:0:500}" >> "$DEBUG_LOG"

# Check clipboard before
CLIPBOARD_BEFORE=$(pbpaste | wc -c)
echo "Clipboard size before: $CLIPBOARD_BEFORE bytes" >> "$DEBUG_LOG"

# Check if any logs were found
if echo "$OUTPUT" | grep -q "Total matches: 0"; then
    echo "No matches found" >> "$DEBUG_LOG"
    osascript -e "display notification \"No logs found for prefix: $PREFIX\" with title \"Log Search\" sound name \"Basso\""
else
    # Extract match count if possible
    MATCHES=$(echo "$OUTPUT" | grep "Total matches:" | awk '{print $3}')
    echo "Matches found: $MATCHES" >> "$DEBUG_LOG"
    
    # Check clipboard after (give it a moment)
    sleep 1
    CLIPBOARD_AFTER=$(pbpaste | wc -c)
    echo "Clipboard size after: $CLIPBOARD_AFTER bytes" >> "$DEBUG_LOG"
    
    if [ -n "$MATCHES" ]; then
        osascript -e "display notification \"Found $MATCHES log entries - Check /tmp/get_logs_debug.log\" with title \"Log Search Debug\" sound name \"Glass\""
    else
        osascript -e 'display notification "Logs processed - Check /tmp/get_logs_debug.log" with title "Log Search Debug" sound name "Glass"'
    fi
fi

echo "=== Debug log ended at $(date) ===" >> "$DEBUG_LOG"

# Also show alert with log location
osascript -e 'display alert "Debug Complete" message "Debug log saved to /tmp/get_logs_debug.log\n\nYou can view it with:\ncat /tmp/get_logs_debug.log" buttons {"OK"} default button "OK"'