#!/bin/bash

# Simple test to verify clipboard functionality

echo "Testing clipboard functionality..."

# Test 1: Direct pbcopy
echo "Test 1: Direct clipboard test"
echo "Hello from test 1" | pbcopy
sleep 1
RESULT1=$(pbpaste)
echo "Result 1: $RESULT1"

# Test 2: Variable to clipboard
echo "Test 2: Variable to clipboard"
TEST_VAR="Hello from test 2"
echo "$TEST_VAR" | pbcopy
sleep 1
RESULT2=$(pbpaste)
echo "Result 2: $RESULT2"

# Test 3: Command output to clipboard
echo "Test 3: Command output to clipboard"
OUTPUT=$(echo "Hello from test 3")
echo "$OUTPUT" | pbcopy
sleep 1
RESULT3=$(pbpaste)
echo "Result 3: $RESULT3"

# Test 4: Multiline to clipboard
echo "Test 4: Multiline to clipboard"
MULTILINE="Line 1
Line 2
Line 3"
echo "$MULTILINE" | pbcopy
sleep 1
RESULT4=$(pbpaste)
echo "Result 4:"
echo "$RESULT4"

echo "All tests complete!"