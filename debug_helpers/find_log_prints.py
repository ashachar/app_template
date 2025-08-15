#!/usr/bin/env python3
"""
Simplified log finder/cleaner using a unique marker approach.

Example:

"""

import argparse
from pathlib import Path

# Define the unique marker that identifies removable logs
LOG_MARKER = '@LOGMARK'

# Define the root directory to search
ROOT_DIR = Path(__file__).parent.parent

# File extensions to search
SEARCHABLE_EXTENSIONS = {
    '.js', '.jsx', '.ts', '.tsx',  # JavaScript/TypeScript
    '.py',                          # Python
    '.java',                        # Java
    '.go',                          # Go
    '.rb',                          # Ruby
    '.php',                         # PHP
    '.cs',                          # C#
    '.swift',                       # Swift
    '.kt', '.kts',                  # Kotlin
    '.rs',                          # Rust
    '.cpp', '.cc', '.cxx', '.c',   # C/C++
    '.sql',                         # SQL (for debug statements in procedures)
}

# Directories to skip
SKIP_DIRS = {
    'node_modules', '.git', '.next', 'dist', 'build', '.cache',
    '__pycache__', '.pytest_cache', 'venv', '.env', 'env',
    'coverage', '.nyc_output', 'out', 'tmp', 'temp',
    '.vscode', '.idea', 'vendor', 'target', 'debug_artifacts'
}


def get_searchable_files(root_dir):
    """Get all searchable files in the directory tree."""
    # Get the path of this script to exclude it
    script_path = Path(__file__).resolve()
    
    for path in root_dir.rglob('*'):
        # Skip directories
        if path.is_dir():
            continue
            
        # Skip this script itself
        if path.resolve() == script_path:
            continue
            
        # Skip if in a skipped directory
        if any(skip_dir in path.parts for skip_dir in SKIP_DIRS):
            continue
            
        # Skip non-code files
        if path.suffix not in SEARCHABLE_EXTENSIONS:
            continue
            
        yield path


def find_marked_logs(file_path):
    """Find all lines containing the log marker in a file."""
    marked_lines = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if LOG_MARKER in line:
                    marked_lines.append((line_num, line.strip()))
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return marked_lines


def remove_marked_logs(file_path):
    """Remove all lines containing the log marker from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        original_count = len(lines)
        
        # Filter out lines with the marker
        filtered_lines = [line for line in lines if LOG_MARKER not in line]
        
        removed_count = original_count - len(filtered_lines)
        
        if removed_count > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(filtered_lines)
        
        return removed_count
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0


def main():
    """Main function to find or clean marked log statements."""
    parser = argparse.ArgumentParser(
        description=f'Find and optionally clean log statements marked with {LOG_MARKER}'
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help=f'Remove all lines containing {LOG_MARKER}'
    )
    
    args = parser.parse_args()
    
    if args.clean:
        # Cleaning mode
        print(f"Removing all lines containing '{LOG_MARKER}'...")
        print(f"Root directory: {ROOT_DIR}\n")
        
        total_removed = 0
        files_cleaned = 0
        
        for file_path in get_searchable_files(ROOT_DIR):
            removed = remove_marked_logs(file_path)
            if removed > 0:
                relative_path = file_path.relative_to(ROOT_DIR)
                print(f"  Removed {removed} line(s) from {relative_path}")
                total_removed += removed
                files_cleaned += 1
        
        print(f"\n=== Cleaning Complete ===")
        print(f"Total lines removed: {total_removed}")
        print(f"Files cleaned: {files_cleaned}")
    else:
        # Search mode
        print(f"Searching for lines containing '{LOG_MARKER}'...")
        print(f"Root directory: {ROOT_DIR}\n")
        
        total_found = 0
        files_with_logs = 0
        
        for file_path in get_searchable_files(ROOT_DIR):
            marked_lines = find_marked_logs(file_path)
            if marked_lines:
                relative_path = file_path.relative_to(ROOT_DIR)
                print(f"\n{relative_path}:")
                files_with_logs += 1
                
                # Show first 5 lines as examples
                for line_num, content in marked_lines[:5]:
                    # Truncate long lines
                    if len(content) > 100:
                        content = content[:97] + "..."
                    print(f"  Line {line_num}: {content}")
                
                if len(marked_lines) > 5:
                    print(f"  ... and {len(marked_lines) - 5} more")
                
                total_found += len(marked_lines)
        
        print(f"\n=== Summary ===")
        print(f"Found {total_found} marked log line(s) in {files_with_logs} file(s)")
        if total_found > 0:
            print(f"\nUse --clean flag to remove these lines")


if __name__ == "__main__":
    main()