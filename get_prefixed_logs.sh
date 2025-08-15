#!/bin/bash

# Script to extract logs with a given prefix from consolidated logs
# Usage: ./get_prefixed_logs.sh <prefix> [options]
# Options:
#   -f <file>  : Specific log file to search (default: latest.log)
#   -n <lines> : Number of context lines after match (default: 0)
#   -c         : Count matches only
#   -i         : Case insensitive search
#   -r         : Use prefix as regex pattern instead of literal string
#   -o         : Output only (don't copy to clipboard)
#   -h         : Show this help

# Default values
LOG_FILE="consolidated_logs/latest.log"
CONTEXT_LINES=0
COUNT_ONLY=false
CASE_INSENSITIVE=""
USE_REGEX=false
NO_CLIPBOARD=false

# Show help
show_help() {
    echo "Usage: $0 <prefix> [options]"
    echo ""
    echo "Extract logs containing a specific prefix from consolidated logs"
    echo ""
    echo "Options:"
    echo "  -f <file>  : Specific log file to search (default: latest.log)"
    echo "  -n <lines> : Number of context lines after match (default: 0)"
    echo "  -c         : Count matches only"
    echo "  -i         : Case insensitive search"
    echo "  -r         : Use prefix as regex pattern instead of literal string"
    echo "  -o         : Output only (don't copy to clipboard)"
    echo "  -h         : Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 '[MAGIC-LINK-DEBUG]'              # Find all magic link debug logs"
    echo "  $0 'ERROR' -i                        # Find all errors (case insensitive)"
    echo "  $0 '\\[DEBUG-.*\\]' -r                # Find all debug session logs using regex"
    echo "  $0 'API' -n 2                        # Show API logs with 2 lines of context"
    echo "  $0 'ERROR' -f consolidated_logs/consolidated_2025-07-26.log"
    exit 0
}

# Parse command line arguments
if [ $# -eq 0 ]; then
    show_help
fi

PREFIX="$1"
shift

while getopts "f:n:ciroh" opt; do
    case $opt in
        f)
            LOG_FILE="$OPTARG"
            ;;
        n)
            CONTEXT_LINES="$OPTARG"
            ;;
        c)
            COUNT_ONLY=true
            ;;
        i)
            CASE_INSENSITIVE="-i"
            ;;
        r)
            USE_REGEX=true
            ;;
        o)
            NO_CLIPBOARD=true
            ;;
        h)
            show_help
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            show_help
            ;;
    esac
done

# Check if log file exists
if [ ! -f "$LOG_FILE" ]; then
    echo "Error: Log file '$LOG_FILE' not found!" >&2
    echo "Available log files:"
    ls -la consolidated_logs/*.log 2>/dev/null | awk '{print "  " $9}'
    exit 1
fi

# Prepare the pattern
if [ "$USE_REGEX" = true ]; then
    PATTERN="$PREFIX"
else
    # Escape special regex characters for literal search
    PATTERN=$(echo "$PREFIX" | sed 's/[[\.*^$()+?{|]/\\&/g')
fi

# Extract matching logs
echo "==================================================================="
echo "Searching for: $PREFIX (+ all ERROR entries)"
echo "Log file: $LOG_FILE"
echo "Options: $([ -n "$CASE_INSENSITIVE" ] && echo "case-insensitive" || echo "case-sensitive")"
echo "==================================================================="
echo ""

if [ "$COUNT_ONLY" = true ]; then
    # Count matches for pattern and errors
    PATTERN_COUNT=$(grep $CASE_INSENSITIVE -c "$PATTERN" "$LOG_FILE")
    ERROR_COUNT=$(grep -c "\[ERROR\]" "$LOG_FILE")
    # Remove duplicates (entries that match both pattern and error)
    TOTAL_COUNT=$(grep $CASE_INSENSITIVE -E "($PATTERN|\[ERROR\])" "$LOG_FILE" | sort -u | wc -l)
    echo "Found $TOTAL_COUNT matching log entries ($PATTERN_COUNT for pattern, $ERROR_COUNT errors)"
else
    # Use awk to capture full log entries (including multi-line content)
    # A new log entry starts with a timestamp pattern: [YYYY-MM-DDTHH:MM:SS.sssZ]
    OUTPUT=$(awk -v pattern="$PATTERN" -v case_insensitive="$CASE_INSENSITIVE" '
    BEGIN {
        # Set up case sensitivity
        if (case_insensitive == "-i") {
            IGNORECASE = 1
        }
        in_matching_entry = 0
        current_entry = ""
        match_count = 0
    }
    
    # Detect start of a new log entry
    /^\[[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}Z\]/ {
        # If we were capturing a matching entry, print it
        if (in_matching_entry && current_entry != "") {
            print current_entry
            print ""  # Add blank line between entries
        }
        
        # Check if this new entry contains our pattern OR is an error
        if ($0 ~ pattern || $0 ~ /\[ERROR\]/) {
            in_matching_entry = 1
            match_count++
            current_entry = $0
        } else {
            in_matching_entry = 0
            current_entry = ""
        }
        next
    }
    
    # For continuation lines (not starting with timestamp)
    {
        if (in_matching_entry) {
            current_entry = current_entry "\n" $0
        }
    }
    
    END {
        # Print the last entry if it was matching
        if (in_matching_entry && current_entry != "") {
            print current_entry
        }
        
        # Print summary to stderr so it doesnt interfere with piping
        print "" > "/dev/stderr"
        print "===================================================================" > "/dev/stderr"
        print "Total matches: " match_count > "/dev/stderr"
    }
    ' "$LOG_FILE")
    
    # Print the output
    echo "$OUTPUT"
    
    # Copy to clipboard if not disabled and output is not empty
    if [ "$NO_CLIPBOARD" = false ] && [ -n "$OUTPUT" ]; then
        # Detect the OS and use appropriate clipboard command
        if command -v pbcopy >/dev/null 2>&1; then
            # macOS
            echo "$OUTPUT" | pbcopy
            echo "" >&2
            echo "✓ Logs copied to clipboard" >&2
        elif command -v xclip >/dev/null 2>&1; then
            # Linux with xclip
            echo "$OUTPUT" | xclip -selection clipboard
            echo "" >&2
            echo "✓ Logs copied to clipboard" >&2
        elif command -v wl-copy >/dev/null 2>&1; then
            # Wayland
            echo "$OUTPUT" | wl-copy
            echo "" >&2
            echo "✓ Logs copied to clipboard" >&2
        else
            echo "" >&2
            echo "Note: Clipboard command not found. Install pbcopy (macOS), xclip (Linux), or wl-copy (Wayland) to enable clipboard support." >&2
        fi
    fi
fi

# Show tip for viewing in less with highlighting
if [ "$COUNT_ONLY" = false ]; then
    echo "" >&2
    echo "Tip: For better viewing with highlighting, use:" >&2
    echo "  $0 '$PREFIX' | less -R" >&2
    echo "" >&2
    echo "Note: Use -o flag to disable automatic clipboard copy" >&2
fi