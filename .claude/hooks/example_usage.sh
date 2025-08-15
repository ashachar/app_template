#!/bin/bash
# Example usage of the post-execution hook system

echo "Claude Post-Execution Hook System Usage Examples"
echo "==============================================="
echo ""

# Change to app directory
cd /Users/amirshachar/Desktop/Amir/Projects/Personal/swifit/app

echo "1. Running all post-execution hooks:"
echo "   python .claude/hooks/run_hooks.py"
echo ""

echo "2. Running a specific hook by name:"
echo "   python .claude/hooks/run_hooks.py --hook 'File Size Check and Auto-Refactor'"
echo ""

echo "3. Listing all configured hooks:"
echo "   python .claude/hooks/run_hooks.py --list"
echo ""

echo "4. Manually refactoring a large file:"
echo "   python .claude/hooks/auto_refactor.py path/to/large_file.py"
echo ""

echo "5. Checking modified files for size violations:"
echo "   python .claude/hooks/post-execution-file-size-check.py"
echo ""

echo "Configuration:"
echo "- Edit .claude/hooks/hooks.json to customize settings"
echo "- Max lines per file: 200 (configurable)"
echo "- Supported file types: .py, .js, .ts, .tsx, .jsx"
echo ""

echo "The hook system will:"
echo "1. Detect any modified files after code changes"
echo "2. Check if files exceed 200 lines"
echo "3. Automatically refactor large files into smaller modules"
echo "4. Preserve all logic - only rearranges code"
echo "5. Update imports throughout the project"