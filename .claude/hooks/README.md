# Claude Post-Execution Hooks

This directory contains the post-execution hook system that automatically checks and refactors files exceeding 200 lines.

## Overview

The hook system automatically:
1. Detects modified files after any code changes
2. Checks if any file exceeds 200 lines
3. Automatically refactors large files into smaller, logical modules
4. Updates imports throughout the project

## Components

### 1. `post-execution-file-size-check.py`
The main hook that runs after file modifications. It:
- Identifies modified files using git
- Checks line counts
- Creates refactoring plans
- Triggers automatic refactoring

### 2. `auto_refactor.py`
The refactoring utility that:
- Analyzes file structure (Python, TypeScript, JavaScript)
- Splits files into logical modules:
  - Constants files (`*_constants.py`, `*.constants.ts`)
  - Type definitions (`*_types.py`, `*.types.ts`)
  - Utility functions (`*_utils.py`, `*.utils.ts`)
  - Models/Classes (`*_models.py`)
  - React hooks (`*.hooks.ts`)
- Preserves all original logic
- Updates imports

### 3. `run_hooks.py`
The hook runner that:
- Loads hook configuration
- Executes hooks based on events
- Logs results
- Handles errors gracefully

### 4. `hooks.json`
Configuration file that defines:
- Which hooks to run
- Hook settings and parameters
- File patterns to include/exclude

## Usage

### Manual Execution

Run all post-execution hooks:
```bash
python .claude/hooks/run_hooks.py
```

Run a specific hook:
```bash
python .claude/hooks/run_hooks.py --hook "File Size Check and Auto-Refactor"
```

List all configured hooks:
```bash
python .claude/hooks/run_hooks.py --list
```

### Automatic Integration

The hooks are designed to be integrated into Claude's workflow. After any file modification:

1. Claude checks for modified files
2. Runs the post-execution hooks
3. Automatically refactors files over 200 lines
4. Reports results

### Direct Refactoring

To refactor a specific file:
```bash
python .claude/hooks/auto_refactor.py path/to/large_file.py
```

## Configuration

Edit `hooks.json` to customize:

```json
{
  "config": {
    "max_lines": 200,              // Maximum lines per file
    "auto_refactor": true,         // Enable automatic refactoring
    "file_extensions": [".py", ".js", ".ts", ".tsx", ".jsx"],
    "exclude_patterns": ["*test*", "*spec*", "*.min.js"]
  }
}
```

## How It Works

### Python Files
- Separates imports, constants, types, utilities, classes, and main code
- Creates modules: `*_constants.py`, `*_types.py`, `*_utils.py`, `*_models.py`
- Updates the main file to import from new modules

### TypeScript/JavaScript Files
- Separates imports, types, interfaces, constants, utilities, hooks, and components
- Creates modules: `*.types.ts`, `*.constants.ts`, `*.utils.ts`, `*.hooks.ts`
- Maintains proper export/import structure

## Example

Before (large_component.tsx - 350 lines):
```typescript
// All code in one file
import React from 'react';
// ... 350 lines of mixed code
```

After automatic refactoring:
```
large_component.tsx (50 lines) - Main component
large_component.types.ts (40 lines) - Type definitions
large_component.constants.ts (30 lines) - Constants
large_component.utils.ts (80 lines) - Utility functions
large_component.hooks.ts (60 lines) - React hooks
```

## Logs

Check `.claude/hooks/hooks.log` for execution history and any errors.

## Disabling Hooks

To temporarily disable:
1. Edit `hooks.json` and set `"enabled": false` for specific hooks
2. Or set `"hooks_enabled": false` in settings to disable all hooks

## Contributing

When adding new hooks:
1. Create the hook script in this directory
2. Add configuration to `hooks.json`
3. Test with `run_hooks.py`
4. Document the hook's purpose and behavior