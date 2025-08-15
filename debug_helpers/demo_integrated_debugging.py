#!/usr/bin/env python3
"""
Demonstration of integrated debugging workflow with:
- Debug session management (prefixes)
- Session state persistence
- Log analysis
- Checkpoint/resume functionality
"""

import os
import sys
import json
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from debug_session import DebugSession
from debug_session_state import DebugSessionState
from analyze_logs import LogAnalyzer


def demonstrate_integrated_debugging():
    """Demonstrate how all debugging tools work together."""
    
    print(" INTEGRATED DEBUGGING WORKFLOW DEMONSTRATION")
    print("=" * 60)
    
    # 1. Initialize debug session with prefix management
    issue_type = "job-creation-missing-fields"
    debug_session = DebugSession(issue_type)
    session_id = debug_session.session_id
    
    print("\n1⃣  Debug Session Initialized:")
    print(f"   Session ID: {session_id}")
    print(f"   Issue Type: {issue_type}")
    
    # 2. Initialize session state management
    state = DebugSessionState(session_id)
    
    print("\n2⃣  Session State Management Active:")
    print(f"   State directory: {state.base_dir}")
    
    # 3. Demonstrate checkpoint creation after successful steps
    print("\n3⃣  Simulating Debugging Steps:")
    
    # Step 1: Login
    state.set_current_step("login", "Testing user authentication")
    print(f"\n    Step: Login")
    print(f"      Prefix: {debug_session.get_prefix('UI', 'FLOW')}")
    
    # Simulate saving test data
    state.save_test_data("auth_token", "eyJ0eXAiOiJKV1Q...", "auth")
    state.save_test_data("user_email", "test@example.com", "auth")
    print("       Saved authentication data")
    
    # Create checkpoint
    checkpoint1 = state.create_checkpoint("login_complete", "Successfully authenticated user")
    state.complete_current_step("Login successful")
    print(f"       Checkpoint created: login_complete")
    
    # Step 2: Navigate to job creation
    state.set_current_step("navigate_job_form", "Navigating to job creation form")
    print(f"\n    Step: Navigate to Job Form")
    print(f"      Prefix: {debug_session.get_prefix('UI', 'FLOW')}")
    
    # Cache an API response
    state.cache_api_response(
        "GET", 
        "/api/lookup/departments",
        {"data": [{"id": 1, "name": "Engineering"}, {"id": 2, "name": "Sales"}]},
        200
    )
    print("       Cached department lookup data")
    
    checkpoint2 = state.create_checkpoint("form_loaded", "Job creation form loaded with lookups")
    state.complete_current_step("Navigation successful")
    print(f"       Checkpoint created: form_loaded")
    
    # Step 3: Submit job (simulate failure)
    state.set_current_step("submit_job", "Submitting job creation form")
    print(f"\n    Step: Submit Job")
    print(f"      Prefix: {debug_session.get_prefix('API', 'ERROR')}")
    
    # Record a failed attempt
    state.record_failed_attempt(
        "Job submission failed",
        "400 Bad Request - Missing required fields",
        {"fields": ["salary_range", "experience_level"]},
        "API validation error - frontend should have caught this"
    )
    print("       Failed attempt recorded")
    
    # Add finding
    state.add_finding(
        "root_cause",
        "Frontend validation missing for salary_range and experience_level",
        evidence="API returns 400 with missing fields that should be validated client-side",
        fix_suggestion="Add required field validation in JobCreationForm component",
        related_files=["src/components/JobCreationForm.tsx", "src/validators/job.ts"]
    )
    print("       Root cause finding documented")
    
    # 4. Demonstrate session summary and resume
    print("\n4⃣  Session Summary:")
    state.print_summary()
    
    # Show how to get specific data
    print("\n5⃣  Retrieving Session Data:")
    
    # Get test data
    auth_token = state.get_test_data("auth_token", "auth")
    print(f"   Auth token retrieved: {auth_token[:20]}... (used {state.test_data['auth']['auth_token']['used_count']} times)")
    
    # Get cached response
    cached = state.get_cached_response("GET", "/api/lookup/departments")
    if cached:
        print(f"   Cached departments: {len(cached['response']['data'])} items (hit {cached['hit_count']} times)")
    
    # Get findings
    root_causes = state.get_findings_by_type("root_cause")
    if root_causes:
        print(f"   Root cause found: {root_causes[0]['description']}")
    
    # 6. Demonstrate resume functionality
    print("\n6⃣  Resume Suggestions:")
    suggestions = state.suggest_next_steps()
    for i, suggestion in enumerate(suggestions, 1):
        print(f"   {i}. {suggestion}")
    
    # 7. Show log analysis integration
    print("\n7⃣  Log Analysis Integration:")
    print(f"   Analyze logs for session: python analyze_logs.py --session {session_id}")
    print(f"   Clean up session logs: {debug_session.get_cleanup_command()}")
    
    # 8. Demonstrate checkpoint restoration
    print("\n8⃣  Checkpoint Restoration Demo:")
    
    # Modify some data
    state.save_test_data("job_id", "new-job-123", "ids")
    print("   Modified data: job_id = 'new-job-123'")
    
    # Restore earlier checkpoint
    success = state.restore_checkpoint("form_loaded")
    if success:
        job_id = state.get_test_data("job_id", "ids")
        print(f"   After restoration: job_id = {job_id if job_id else 'None'}")
    
    # 9. Close session
    debug_session.close_session()
    print("\n Debug session closed")
    
    # Show example integration code
    print("\n" + "="*60)
    print(" EXAMPLE INTEGRATION IN PLAYWRIGHT TEST:")
    print("="*60)
    print("""
# At the start of your debug script:
from debug_helpers.debug_session import DebugSession
from debug_helpers.debug_session_state import DebugSessionState

# Initialize both systems
debug_session = DebugSession("job-creation-issue")
state = DebugSessionState(debug_session.session_id)

# In your test code:
async def test_job_creation():
    # Set current step
    state.set_current_step("login", "Authenticating user")
    
    # Add debug logs with session prefix
        # After successful login
    auth_token = await page.evaluate("localStorage.getItem('authToken')")
    state.save_test_data("auth_token", auth_token, "auth")
    state.create_checkpoint("after_login", "User authenticated")
    
    # If something fails
    try:
        await page.click('button[type="submit"]')
    except Exception as e:
        state.record_failed_attempt(
            "Submit button click failed",
            str(e),
            {"selector": 'button[type="submit"]', "page_url": page.url()}
        )
    
    # When you find the issue
    state.add_finding(
        "root_cause",
        "Submit button disabled due to validation",
        evidence="Button has disabled attribute when required fields empty"
    )
""")
    
    print("\n" + "="*60)
    print(" KEY BENEFITS:")
    print("="*60)
    print("""
1. PERSISTENCE: Test data, API responses, and progress saved across runs
2. RESUMABILITY: Skip already-completed steps using checkpoints
3. TRACEABILITY: All logs tagged with session ID for easy filtering
4. DOCUMENTATION: Failed attempts and findings tracked automatically
5. EFFICIENCY: Cached API responses speed up repeated test runs
6. ANALYSIS: Integrated with log analyzer for pattern detection
""")


if __name__ == "__main__":
    demonstrate_integrated_debugging()