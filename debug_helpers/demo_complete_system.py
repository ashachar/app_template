#!/usr/bin/env python3
"""
Demonstration of the complete debugging ecosystem:
- Test discovery and enrichment
- Session state management  
- Parallel execution
- Result aggregation
"""

import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from debug_helpers.debug_session import DebugSession
from debug_helpers.debug_session_state import DebugSessionState
from debug_helpers.parallel_debugger import ParallelDebugger
from debug_helpers.parallel_config import TestScenario, TestType
from tests.test_manager import TestManager


async def demonstrate_complete_debugging_workflow():
    """
    Demonstrate how all debugging systems work together for maximum efficiency.
    """
    print(" COMPLETE DEBUGGING ECOSYSTEM DEMONSTRATION")
    print("=" * 60)
    
    # 1. Initialize debugging session
    issue_description = "Job creation form not saving department and employment type correctly"
    debug_session = DebugSession("job-field-issue")
    state = DebugSessionState(debug_session.session_id)
    
    print(f"\n1⃣  Debug Session Started: {debug_session.session_id}")
    state.set_current_step("initialization", "Starting debugging workflow")
    
    # 2. Test Discovery
    print("\n2⃣  Discovering Relevant Tests...")
    test_manager = TestManager()
    
    # Search for relevant tests
    relevant_tests = test_manager.suggest_tests_for_issue(
        issue_description,
        error_logs=["department must be integer", "400 Bad Request"]
    )
    
    print(f"   Found {len(relevant_tests)} relevant tests:")
    for test in relevant_tests[:5]:
        print(f"   - {test.name}: {test.purpose}")
        print(f"     Success rate: {test.success_rate:.1%}, Used {test.usage_count} times")
    
    # Save discovered tests to session state
    state.save_test_data("discovered_tests", [t.name for t in relevant_tests], "discovery")
    state.create_checkpoint("test_discovery_complete", f"Found {len(relevant_tests)} relevant tests")
    
    # 3. Test Enrichment
    print("\n3⃣  Enriching Tests with Scenario-Specific Additions...")
    
    if relevant_tests:
        test_to_enrich = relevant_tests[0]
        
        # Define enrichments based on the issue
        enrichments = {
            'assertions': {
                'validate_job_request': 'assert isinstance(request_data.get("department"), int), "Department must be integer"',
                'format_job_response': 'assert response["department"] != "Engineering", "Department should be ID not name"'
            },
            'new_tests': {
                'field_type_validation': '''
    # Verify all lookup fields are integers
    lookup_fields = ['department', 'employment_type', 'experience_level']
    for field in lookup_fields:
        if field in job_data:
            assert isinstance(job_data[field], int), f"{field} must be integer, got {type(job_data[field])}"
'''
            }
        }
        
        # Enrich the test
        enriched_path = test_manager.enrich_test(
            f"{test_to_enrich.file_path}::{test_to_enrich.name}",
            {'issue_type': 'job-field-types'},
            enrichments
        )
        
        if enriched_path:
            print(f"    Enriched test saved to: {enriched_path}")
            state.save_test_data("enriched_test_path", enriched_path, "enrichment")
    
    # 4. Parallel Test Execution
    print("\n4⃣  Preparing Parallel Test Execution...")
    
    # Create test scenarios from discovered tests
    scenarios = []
    for i, test in enumerate(relevant_tests[:3]):  # Run top 3 in parallel
        scenario = TestScenario(
            name=f"{test.name}_parallel",
            test_type=TestType.UNIT if test.test_type == 'unit' else TestType.INTEGRATION,
            test_function=test.file_path,
            timeout=60,
            tags=['discovered', 'parallel']
        )
        scenarios.append(scenario)
    
    # Add the enriched test if available
    if 'enriched_path' in locals() and enriched_path:
        scenarios.append(TestScenario(
            name="enriched_test",
            test_type=TestType.UNIT,
            test_function=enriched_path,
            timeout=60,
            tags=['enriched', 'scenario-specific']
        ))
    
    print(f"   Prepared {len(scenarios)} test scenarios for parallel execution")
    
    # Initialize parallel debugger
    parallel_debugger = ParallelDebugger(f"parallel-{issue_description[:20]}")
    
    # Mock execution for demo (in real use, this would run actual tests)
    print("\n5⃣  Executing Tests in Parallel...")
    print("   [In production, this would run actual tests]")
    
    # Simulate results
    mock_results = {
        'total_scenarios': len(scenarios),
        'successful_scenarios': len(scenarios) - 1,
        'failed_scenarios': 1,
        'common_errors': [("Department validation failed", 2)],
        'root_causes': [{
            'description': "API expects integer for department but receives string",
            'fix_suggestion': "Update form to send department ID instead of name"
        }]
    }
    
    # Save results to state
    state.save_test_data("parallel_results", mock_results, "execution")
    state.add_finding(
        "root_cause",
        mock_results['root_causes'][0]['description'],
        evidence="Multiple tests show department field type mismatch",
        fix_suggestion=mock_results['root_causes'][0]['fix_suggestion']
    )
    
    # 6. Learning and Contribution
    print("\n6⃣  Contributing Back to Test Repository...")
    
    # Record test usage
    for test in relevant_tests[:3]:
        test_manager.record_test_usage(
            f"{test.file_path}::{test.name}",
            success=True,
            scenario="job-field-type-debugging",
            notes="Helped identify integer type requirement for lookup fields"
        )
    
    # Create new test from discoveries
    new_test_code = '''
def test_job_api_lookup_field_types():
    """
    Ensure all lookup fields in job API use integer IDs not strings.
    
    @scenarios: api-field-validation, lookup-fields
    @tags: api, validation, lookup-fields
    """
    job_data = {
        "title": "Test Job",
        "department": 2,  # Must be integer
        "employment_type": 1,  # Must be integer
        "location": "Tel Aviv"
    }
    
    # Validate request
    errors = validate_job_request(job_data)
    assert len(errors) == 0, f"Valid request failed: {errors}"
    
    # Test invalid string values
    invalid_data = job_data.copy()
    invalid_data["department"] = "Engineering"
    errors = validate_job_request(invalid_data)
    assert "department must be integer" in str(errors).lower()
'''
    
    new_test_path = test_manager.create_test_from_debugging(
        test_name="job_api_lookup_field_types",
        test_type="unit",
        category="api",
        test_code=new_test_code,
        scenario="job-field-type-validation",
        purpose="Ensure lookup fields use integer IDs per API agreement"
    )
    
    print(f"    Created new test: {new_test_path}")
    
    # 7. Generate Updated Documentation
    print("\n7⃣  Updating Test Documentation...")
    docs = test_manager.generate_documentation()
    
    for filename, content in docs.items():
        doc_path = Path(__file__).parent.parent / 'tests' / filename
        # In demo, just show what would be written
        print(f"   Would update: {filename} ({len(content)} chars)")
    
    # 8. Session Summary
    print("\n8⃣  Debug Session Summary:")
    state.create_checkpoint("debugging_complete", "All debugging steps completed")
    state.print_summary()
    
    # Show next steps
    suggestions = state.suggest_next_steps()
    if suggestions:
        print("\n Suggested Next Steps:")
        for suggestion in suggestions:
            print(f"   - {suggestion}")
    
    print("\n" + "="*60)
    print(" DEMONSTRATION COMPLETE")
    print("="*60)
    print("\nKey Benefits Demonstrated:")
    print("1.  Test Discovery - Found existing relevant tests")
    print("2.  Test Enrichment - Enhanced tests for specific scenario")
    print("3.  Parallel Execution - Run multiple tests simultaneously")
    print("4.  Result Aggregation - Identified common patterns")
    print("5.  Knowledge Accumulation - Created new tests from discoveries")
    print("6.  Continuous Improvement - Each session makes future debugging faster")
    
    return state.session_id


def main():
    """Run the demonstration."""
    session_id = asyncio.run(demonstrate_complete_debugging_workflow())
    
    print(f"\n Session data saved. To resume:")
    print(f"   python debug_helpers/debug_session_state.py --resume {session_id}")


if __name__ == "__main__":
    main()