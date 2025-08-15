#!/bin/bash

# Simple test script for Automator service
osascript -e 'display notification "Service is working! Prefix file contains: '"$(cat /Users/amirshachar/Desktop/Amir/Projects/Personal/swifit/app/debug_prefix.txt)"'" with title "Service Test" sound name "Glass"'

# Also copy something simple to clipboard to test
echo "Service test successful at $(date)" | pbcopy