#!/bin/bash

# This script is called by the macOS keyboard shortcut
# It prompts for a prefix and runs get_prefixed_logs.sh

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# Change to app directory
cd "$APP_DIR"

# Use AppleScript to get user input
PREFIX=$(osascript -e 'text returned of (display dialog "Enter log prefix to search for:" default answer "[DEBUG-" buttons {"Cancel", "Search"} default button "Search")')

# Check if user cancelled
if [ $? -ne 0 ]; then
    exit 0
fi

# Run the get_prefixed_logs script
./get_prefixed_logs.sh "$PREFIX"

# Show notification
osascript -e 'display notification "Logs copied to clipboard" with title "Log Search Complete" sound name "Glass"'