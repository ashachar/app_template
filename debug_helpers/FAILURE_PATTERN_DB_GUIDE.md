# 🎯 Failure Pattern Database Usage Guide

The Failure Pattern Database is a learning system that captures debugging knowledge and provides instant solutions for recurring issues. This guide shows how to use it effectively.

## 📚 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Finding Solutions](#finding-solutions)
4. [Recording New Patterns](#recording-new-patterns)
5. [Integration with Debugging Workflow](#integration-with-debugging-workflow)
6. [Pattern Categories](#pattern-categories)
7. [Best Practices](#best-practices)
8. [Examples](#examples)

## Overview

The Failure Pattern Database:
- 🔍 **Identifies** similar errors from past debugging sessions
- 💡 **Suggests** proven solutions with success rates
- 📈 **Learns** from each debugging session
- 🚀 **Accelerates** debugging by avoiding duplicate work

## Quick Start

### 1. Finding Solutions for an Error

```python
from debug_helpers.failure_pattern_db import FailurePatternDB

# Initialize the database
pattern_db = FailurePatternDB()

# Search for solutions
error_message = "Cannot read property 'map' of null"
context = {
    'module': 'ui',
    'action': 'render_job_list',
    'file': 'JobList.tsx'
}

matches = pattern_db.find_similar_patterns(
    error_message,
    context,
    confidence_threshold=0.6  # 60% confidence minimum
)

# Display solutions
for pattern, confidence, solutions in matches[:3]:
    print(f"\n🎯 Pattern: {pattern.error_type} ({confidence:.0%} match)")
    print(f"   Occurrences: {pattern.occurrences} times")
    
    for i, solution in enumerate(solutions[:2], 1):
        print(f"\n   Solution {i}: {solution.description}")
        print(f"   Success rate: {solution.success_rate:.0%}")
        print(f"   Used {solution.success_count} times successfully")
        
        if solution.code_changes:
            print("   Changes needed:")
            for change in solution.code_changes:
                print(f"   - {change.file_path}: {change.description}")
```

### 2. Recording a Successful Solution

```python
# After fixing an issue, record what worked
pattern_id = pattern_db.record_pattern(
    pattern_signature={
        'error_type': 'Null Reference',
        'error_message': error_message,
        'context_keywords': ['array', 'map', 'render'],
        'module_hints': ['ui', 'react']
    },
    solution={
        'description': 'Add default empty array to prevent null reference',
        'code_changes': [
            {
                'file_path': 'src/components/JobList.tsx',
                'description': 'Initialize with empty array',
                'diff_snippet': '- {jobs.map(job => (\n+ {(jobs || []).map(job => ('
            }
        ],
        'test_cases': ['test_job_list_null_handling']
    },
    session_id='JOB-123'
)
```

## Finding Solutions

### Basic Search

```python
# Simple error search
matches = pattern_db.find_similar_patterns("401 Unauthorized")

# With context for better matches
matches = pattern_db.find_similar_patterns(
    "401 Unauthorized",
    context={'module': 'api', 'endpoint': '/jobs'}
)
```

### Understanding Match Results

Each match returns:
- **Pattern**: The matched failure pattern
- **Confidence**: How well it matches (0.0 to 1.0)
- **Solutions**: List of solutions sorted by success rate

```python
pattern, confidence, solutions = matches[0]

print(f"Pattern ID: {pattern.pattern_id}")
print(f"Error Type: {pattern.error_type}")
print(f"Times Seen: {pattern.occurrences}")
print(f"First Seen: {pattern.first_seen}")
print(f"Related Patterns: {pattern.related_patterns}")
```

### Filtering by Confidence

```python
# High confidence matches only (80%+)
high_confidence = pattern_db.find_similar_patterns(
    error_message,
    confidence_threshold=0.8
)

# Include lower confidence matches for exploration
all_matches = pattern_db.find_similar_patterns(
    error_message,
    confidence_threshold=0.3
)
```

## Recording New Patterns

### When to Record a Pattern

Record a pattern when:
- ✅ You solve a new type of error
- ✅ You find a better solution for an existing error
- ✅ You discover an edge case variation

### Pattern Signature Components

```python
pattern_signature = {
    'error_type': 'Database',  # Category: Database, API, React, etc.
    'error_message': 'The actual error message from logs',
    'context_keywords': [
        'migration',    # Related concepts
        'schema',       # Technologies involved
        'postgres'      # Specific tools
    ],
    'module_hints': [
        'database',     # Code modules affected
        'migration',    # Functional areas
        'backend'       # System components
    ]
}
```

### Solution Components

```python
solution = {
    'description': 'Clear, actionable description of the fix',
    'code_changes': [
        {
            'file_path': 'schema/migration.sql',
            'description': 'Add missing table',
            'diff_snippet': '+ CREATE TABLE users (...);'  # Optional
        },
        {
            'file_path': 'terminal',
            'description': 'Run migrations',
            'diff_snippet': 'cd schema && ./run_migration.sh'
        }
    ],
    'test_cases': [
        'test_database_schema_validity',  # Tests that verify the fix
        'test_user_table_exists'
    ]
}
```

### Tracking Solution Success

```python
# After trying a solution
pattern_db.record_solution_result(
    pattern_id='database_5724e4',
    solution_index=0,  # First solution in the list
    success=True,      # Did it work?
    session_id='DB-456'
)
```

## Integration with Debugging Workflow

### 1. With Log Analysis

```python
# After running log analysis
from debug_helpers.analyze_logs import LogAnalyzer

analyzer = LogAnalyzer()
results = analyzer.analyze_all_logs()

# Check critical findings against pattern database
if results['pattern_matches']:
    for match in results['pattern_matches']:
        print(f"Known issue: {match['pattern_type']}")
        print(f"Confidence: {match['confidence']:.0%}")
        for solution in match['solutions']:
            print(f"Try: {solution['description']}")
```

### 2. With Session State

```python
from debug_helpers.debug_session_state import DebugSessionState

state = DebugSessionState('DEBUG-123')

# Add finding - automatically checks patterns
state.add_finding(
    'root_cause',
    'Database connection timeout',
    evidence='Timeout after 30s',
    fix_suggestion='Increase connection timeout'
)

# Check suggested solutions
suggestions = state.suggest_next_steps()
# Will include: "Try proven solution: Increase timeout in config (success rate: 85%)"

# Record solution attempt
if state.pattern_matches:
    match = state.pattern_matches[0]
    state.record_solution_attempt(
        match['pattern_id'],
        solution_index=0,
        success=True,
        notes="Timeout increase to 60s resolved issue"
    )
```

### 3. Automated Import from Sessions

```python
from debug_helpers.pattern_importer import PatternImporter

# Import patterns from all debugging sessions
importer = PatternImporter()
importer.import_from_sessions()
importer.import_from_error_patterns()

print(importer.generate_import_report())
```

## Pattern Categories

### 🗄️ Database
- Migration issues
- Constraint violations  
- Connection problems
- Query errors

### 🌐 API
- Authentication failures
- CORS issues
- Validation errors
- Timeout problems

### ⚛️ React/UI
- Null references
- Hook violations
- Render errors
- State management

### ⚡ Lambda
- Deployment failures
- Permission issues
- Timeout errors
- Cold start problems

### 🏗️ Build/Compilation
- TypeScript errors
- Module resolution
- Syntax issues
- Dependency conflicts

## Best Practices

### 1. Be Specific in Error Messages
```python
# ❌ Too vague
'error_message': 'Database error'

# ✅ Specific
'error_message': 'relation "users" does not exist at users.findAll()'
```

### 2. Include Relevant Context
```python
# ❌ Missing context
context = {}

# ✅ Rich context
context = {
    'module': 'api',
    'endpoint': '/api/users',
    'method': 'POST',
    'user_role': 'admin'
}
```

### 3. Document Code Changes Clearly
```python
# ❌ Unclear
'description': 'Fixed it'

# ✅ Clear and actionable
'description': 'Add null check before mapping array to prevent TypeError'
```

### 4. Link to Verification Tests
```python
# Always include tests that verify the fix
'test_cases': [
    'test_null_array_handling',
    'test_empty_array_rendering'
]
```

### 5. Update Success Rates
```python
# Always record whether solutions worked
pattern_db.record_solution_result(pattern_id, 0, success=True, session_id)
```

## Examples

### Example 1: Lookup Field Type Mismatch

```python
# Error encountered
error = "Expected integer for department, got string"

# Search for solutions
matches = pattern_db.find_similar_patterns(error, {'module': 'api'})

# Best match suggests
# Solution: "Convert string lookup values to integer IDs before sending to API"
# Success rate: 86% (12 successes, 2 failures)

# After implementing fix
pattern_db.record_solution_result(
    'lookup_field_type_mismatch_d3f8a2',
    solution_index=0,
    success=True,
    session_id='JOB-789'
)
```

### Example 2: Authentication Token Expiry

```python
# Pattern search
matches = pattern_db.find_similar_patterns(
    "JWT token expired",
    context={'module': 'auth', 'action': 'api_call'}
)

# Solution found: "Implement token refresh mechanism"
# Code changes show exactly where to add refresh logic

# Recording a variation
pattern_db.record_pattern(
    pattern_signature={
        'error_type': 'Authentication',
        'error_message': 'JWT token expired during long operation',
        'context_keywords': ['jwt', 'expiry', 'long-running'],
        'module_hints': ['auth', 'background']
    },
    solution={
        'description': 'Refresh token before long operations',
        'code_changes': [{
            'file_path': 'src/services/longOperations.ts',
            'description': 'Add preemptive token refresh'
        }],
        'test_cases': ['test_long_operation_token_refresh']
    },
    session_id='BATCH-123'
)
```

### Example 3: React Rendering Error

```python
# Complex UI error
error = "Maximum update depth exceeded in JobList component"

matches = pattern_db.find_similar_patterns(
    error,
    context={
        'module': 'ui',
        'component': 'JobList',
        'action': 'filter_update'
    }
)

# Multiple solutions with different success rates:
# 1. "Add useCallback to prevent recreation" (92% success)
# 2. "Move state update out of render" (87% success)  
# 3. "Use useEffect with proper dependencies" (78% success)
```

## Database Maintenance

### View Statistics

```python
stats = pattern_db.get_pattern_stats()

print(f"Total Patterns: {stats['total_patterns']}")
print(f"Total Solutions: {stats['total_solutions']}")
print(f"Average Success Rate: {stats['average_success_rate']:.1%}")
print("\nMost Common Issues:")
for pattern in stats['most_common_patterns'][:5]:
    print(f"- {pattern.error_type}: {pattern.occurrences} times")
```

### Export/Import Patterns

```python
# Export for backup or sharing
with open('patterns_backup.json', 'w') as f:
    json.dump(pattern_db.patterns, f)

# Import from another system
importer = PatternImporter()
importer.import_manual_patterns(external_patterns)
```

## Troubleshooting

### Pattern Not Found

If no patterns match:
1. Lower confidence threshold (try 0.3)
2. Use fewer context filters
3. Try partial error message
4. Check if it's truly a new pattern

### Low Confidence Matches

If all matches have low confidence:
1. The error might be unique
2. Add more specific context
3. Check error message formatting
4. Consider recording as new pattern

### Solution Didn't Work

If a suggested solution fails:
1. Record the failure: `record_solution_result(..., success=False)`
2. Try the next solution in the list
3. Document what was different
4. Add your working solution when found

## Summary

The Failure Pattern Database transforms debugging from a repetitive task to a learning system. Each debugging session contributes to a growing knowledge base that benefits all future sessions.

Key commands:
- **Find solutions**: `pattern_db.find_similar_patterns(error, context)`
- **Record pattern**: `pattern_db.record_pattern(signature, solution, session_id)`
- **Track success**: `pattern_db.record_solution_result(pattern_id, index, success, session_id)`

Remember: The more you use it, the smarter it gets! 🚀