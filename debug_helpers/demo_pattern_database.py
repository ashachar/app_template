#!/usr/bin/env python3
"""
Demo script showing the Failure Pattern Database in action.
Run this to see how the pattern database helps with debugging.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from debug_helpers.failure_pattern_db import FailurePatternDB
from debug_helpers.debug_session_state import DebugSessionState


def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)


def demo_finding_solutions():
    """Demo: Finding solutions for common errors."""
    print_header("DEMO 1: Finding Solutions for Errors")
    
    pattern_db = FailurePatternDB()
    
    # Example 1: Null reference error
    print("\n1⃣ Searching for null reference error solutions...")
    
    error_msg = "Cannot read property 'map' of null"
    context = {'module': 'ui', 'component': 'JobList'}
    
    matches = pattern_db.find_similar_patterns(error_msg, context, 0.5)
    
    if matches:
        print(f"   Found {len(matches)} potential solutions!\n")
        
        for i, (pattern, confidence, solutions) in enumerate(matches[:2], 1):
            print(f"   Match {i}: {pattern.error_type} (confidence: {confidence:.0%})")
            print(f"   Pattern seen {pattern.occurrences} times before")
            
            for j, solution in enumerate(solutions[:2], 1):
                print(f"\n    Solution {i}.{j}: {solution.description}")
                print(f"      Success rate: {solution.success_rate:.0%} ({solution.success_count}/{solution.success_count + solution.failure_count} attempts)")
                
                if solution.code_changes:
                    print("      Code changes:")
                    for change in solution.code_changes[:2]:
                        print(f"      - {change.file_path}: {change.description}")
                
                if solution.test_cases:
                    print(f"      Verify with: {', '.join(solution.test_cases[:2])}")
    else:
        print("   No matches found - this might be a new type of error")
    
    # Example 2: API authentication error
    print("\n\n2⃣ Searching for authentication error solutions...")
    
    error_msg = "401 Unauthorized: Invalid token"
    context = {'module': 'api', 'endpoint': '/api/jobs', 'action': 'create'}
    
    matches = pattern_db.find_similar_patterns(error_msg, context, 0.4)
    
    if matches:
        pattern, confidence, solutions = matches[0]
        print(f"   Best match: {pattern.error_type} error ({confidence:.0%} confidence)")
        
        if solutions:
            best_solution = solutions[0]
            print(f"   Recommended: {best_solution.description}")
            print(f"   This solution has worked {best_solution.success_count} times!")


def demo_recording_solutions():
    """Demo: Recording a new solution after fixing an issue."""
    print_header("DEMO 2: Recording New Solutions")
    
    pattern_db = FailurePatternDB()
    
    print("\n Recording a solution for a database migration issue...")
    
    # Record the pattern and solution
    pattern_id = pattern_db.record_pattern(
        pattern_signature={
            'error_type': 'Database',
            'error_message': 'relation "job_applications" does not exist',
            'context_keywords': ['migration', 'table', 'postgres'],
            'module_hints': ['database', 'schema']
        },
        solution={
            'description': 'Run pending database migrations to create missing table',
            'code_changes': [
                {
                    'file_path': 'terminal',
                    'description': 'Execute migration script',
                    'diff_snippet': 'cd schema && ./run_migration.sh'
                },
                {
                    'file_path': 'schema/migrations/add_job_applications.sql',
                    'description': 'Ensure migration file exists',
                    'diff_snippet': 'CREATE TABLE job_applications (...);'
                }
            ],
            'test_cases': ['test_job_applications_table_exists']
        },
        session_id='DEMO-001'
    )
    
    print(f"    Pattern recorded with ID: {pattern_id}")
    
    # Simulate trying the solution and it working
    print("\n Testing the solution...")
    print("   Running migrations...")
    print("    Table created successfully!")
    
    # Record that it worked
    pattern_db.record_solution_result(pattern_id, 0, True, 'DEMO-002')
    print("    Success recorded - solution rating improved!")
    
    # Show the pattern statistics
    pattern = pattern_db.patterns[pattern_id]
    solution = pattern.solutions[0]
    print(f"\n   Solution statistics:")
    print(f"   - Success rate: {solution.success_rate:.0%}")
    print(f"   - Times used: {solution.success_count + solution.failure_count}")


def demo_session_integration():
    """Demo: Integration with debug session state."""
    print_header("DEMO 3: Session Integration")
    
    # Create a debug session
    state = DebugSessionState('DEMO-SESSION')
    state.metadata['module'] = 'api'
    
    print("\n Adding a finding to the session...")
    
    # This automatically checks the pattern database!
    state.add_finding(
        'root_cause',
        'API returns "department must be integer" error',
        evidence='POST /api/jobs with department: "Engineering"',
        fix_suggestion='Convert department name to ID before sending'
    )
    
    print("    Finding added and pattern database checked")
    
    # Check if patterns were found
    if state.pattern_matches:
        print(f"\n    Found {len(state.pattern_matches)} matching patterns!")
        
        match = state.pattern_matches[0]
        print(f"   Pattern: {match['pattern_type']} ({match['confidence']:.0%} match)")
        
        if match['solutions']:
            print(f"   Best solution: {match['solutions'][0]['description']}")
            print(f"   Success rate: {match['solutions'][0]['success_rate']:.0%}")
    
    # Check suggestions
    suggestions = state.suggest_next_steps()
    print("\n    Suggested next steps:")
    for suggestion in suggestions:
        print(f"   - {suggestion}")


def demo_pattern_statistics():
    """Demo: View pattern database statistics."""
    print_header("DEMO 4: Pattern Database Statistics")
    
    pattern_db = FailurePatternDB()
    stats = pattern_db.get_pattern_stats()
    
    print(f"\n Database Overview:")
    print(f"   Total patterns: {stats['total_patterns']}")
    print(f"   Total solutions: {stats['total_solutions']}")
    print(f"   Solutions tried: {stats['total_attempts']}")
    print(f"   Average success rate: {stats['average_success_rate']:.1%}")
    
    print(f"\n Patterns by Category:")
    for error_type, pattern_ids in stats['patterns_by_type'].items():
        if pattern_ids:  # Only show categories with patterns
            print(f"   {error_type}: {len(pattern_ids)} patterns")
    
    print(f"\n Most Common Issues:")
    for i, pattern in enumerate(stats['most_common_patterns'][:5], 1):
        print(f"   {i}. {pattern.error_type}: {pattern.error_patterns[0][:50]}...")
        print(f"      Seen {pattern.occurrences} times")
        if pattern.solutions:
            print(f"      Solutions available: {len(pattern.solutions)}")


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print(" FAILURE PATTERN DATABASE DEMO")
    print("="*60)
    print("\nThis demo shows how the pattern database helps with debugging.")
    
    # Run demos
    demo_finding_solutions()
    demo_recording_solutions()
    demo_session_integration()
    demo_pattern_statistics()
    
    print("\n" + "="*60)
    print(" DEMO COMPLETE")
    print("="*60)
    print("\nThe pattern database is a powerful tool that:")
    print("•  Finds proven solutions for errors")
    print("•  Tracks solution success rates")
    print("•  Learns from every debugging session")
    print("•  Makes debugging faster over time")
    print("\nStart using it in your debugging workflow today!")
    print("="*60)


if __name__ == "__main__":
    main()