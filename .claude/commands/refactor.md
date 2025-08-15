---
description: Refactor code to improve quality and maintainability
argument-hint: <file_path>
---

# Refactor Command

When invoked with `/refactor`, this command performs code refactoring to improve quality and maintainability.

## Usage

### Without arguments:
```
/refactor
```
I'll use the dedicated script `../scripts/find-refactoring-candidates.sh` to scan the codebase and identify the top refactoring candidates.

### With a file path:
```
/refactor src/components/UserProfile.tsx
```
I'll analyze the specific file and create a detailed refactoring plan. IMPORTANT: I'll first show a plan WITH EXPLICIT TODO LIST, before executing any chage. The plan will outline what will be in each file, and as a derivative of that, how many lines will be in each file, after the change. Throughout the inference I will keep track of this TODO list and tick the actions I already took.

## What happens

I will:
1. Use `../scripts/find-refactoring-candidates.sh` to identify candidates (NEVER run custom Bash find commands)
2. Analyze the code for refactoring opportunities
3. Create a prioritized plan
4. Automatically execute refactorings without asking for permission
5. Ensure all files stay under 200 lines
6. Return results to you

The refactoring focuses on:
- Safe, incremental refactoring
- File splitting for size compliance
- Code smell detection
- Duplicate code extraction
- Component and function extraction
- Dead code removal
- **NO BACKWARD COMPATIBILITY**: Updates all imports and usages throughout the codebase

## Important Note

When searching for refactoring candidates, I ALWAYS use the dedicated `../scripts/find-refactoring-candidates.sh` script. I NEVER run custom Bash find commands or other ad-hoc searches.

## Critical: No Backward Compatibility

When refactoring files, I MUST:
1. **Remove all re-exports** from the original file (no backward compatibility layer)
2. **Find all usages** of the refactored code throughout the codebase
3. **Update all imports** to point to the new modular files
4. **Verify no broken imports** remain after the refactoring
5. **Delete the original file** if it becomes empty after extraction

Example:
- Original: `import { useTooltipState } from './hooks'`
- Updated: `import { useTooltipState } from './RequisitionDetailsPanel.tooltip'`

The refactoring is NOT complete until ALL imports are updated.