#!/usr/bin/env python3
"""
Comprehensive tests for debug session state management.
Tests all functionality to ensure rock-solid debugging infrastructure.
"""

import os
import sys
import json
import time
import shutil
import tempfile
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from debug_session_state import DebugSessionState, load_session, list_sessions, cleanup_old_sessions


class TestDebugSessionState:
    """Test suite for debug session state management."""
    
    def __init__(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.passed_tests = []
        self.failed_tests = []
        
    def setup(self):
        """Set up test environment."""
        # Create a temporary directory for test sessions
        self.sessions_dir = self.test_dir / 'test_sessions'
        self.sessions_dir.mkdir(exist_ok=True)
        
    def teardown(self):
        """Clean up test environment."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def run_test(self, test_name, test_func):
        """Run a single test and track results."""
        try:
            print(f"\n Running: {test_name}")
            test_func()
            print(f" PASSED: {test_name}")
            self.passed_tests.append(test_name)
        except Exception as e:
            print(f" FAILED: {test_name}")
            print(f"   Error: {str(e)}")
            self.failed_tests.append((test_name, str(e)))
    
    def test_session_initialization(self):
        """Test creating and loading a session."""
        session = DebugSessionState("TEST001", base_dir=self.sessions_dir / "TEST001")
        
        # Check directories created
        assert session.base_dir.exists(), "Base directory not created"
        assert session.checkpoints_dir.exists(), "Checkpoints directory not created"
        assert session.cache_dir.exists(), "Cache directory not created"
        assert session.artifacts_dir.exists(), "Artifacts directory not created"
        
        # Check state file created
        state_file = session._get_state_file()
        assert state_file.exists(), "State file not created"
        
        # Verify session ID
        assert session.session_id == "TEST001", f"Wrong session ID: {session.session_id}"
        
        # Test loading existing session
        session2 = DebugSessionState("TEST001", base_dir=self.sessions_dir / "TEST001")
        assert session2.metadata.get('last_accessed') is not None, "Last accessed not updated"
    
    def test_checkpoint_management(self):
        """Test checkpoint creation and restoration."""
        session = DebugSessionState("TEST002", base_dir=self.sessions_dir / "TEST002")
        
        # Add some test data
        session.save_test_data("job_id", "12345", "ids")
        session.save_test_data("user_token", "abc123", "auth")
        session.current_step = {"name": "login", "started_at": datetime.now().isoformat()}
        
        # Create checkpoint
        checkpoint_file = session.create_checkpoint("after_login", "Successfully logged in", {"custom": "data"})
        assert checkpoint_file is not None, "Checkpoint file not returned"
        assert len(session.checkpoints) == 1, "Checkpoint not added to list"
        assert session.last_successful_step == "after_login", "Last successful step not updated"
        
        # Modify data
        session.save_test_data("job_id", "67890", "ids")
        session.current_step = {"name": "create_job", "started_at": datetime.now().isoformat()}
        
        # Create another checkpoint
        session.create_checkpoint("after_job_create", "Job created successfully")
        assert len(session.checkpoints) == 2, "Second checkpoint not added"
        
        # Restore first checkpoint
        success = session.restore_checkpoint("after_login")
        assert success, "Failed to restore checkpoint"
        assert session.get_test_data("job_id", "ids") == "12345", "Test data not restored"
        assert session.current_step["name"] == "login", "Current step not restored"
        
        # Try to restore non-existent checkpoint
        success = session.restore_checkpoint("non_existent")
        assert not success, "Should fail for non-existent checkpoint"
        
        # List checkpoints
        checkpoints = session.list_checkpoints()
        assert len(checkpoints) == 2, "Wrong number of checkpoints"
        assert checkpoints[0]["name"] == "after_login", "Wrong checkpoint name"
    
    def test_test_data_management(self):
        """Test saving and retrieving test data."""
        session = DebugSessionState("TEST003", base_dir=self.sessions_dir / "TEST003")
        
        # Save test data in different categories
        session.save_test_data("job_id", "job123", "ids")
        session.save_test_data("candidate_id", "cand456", "ids")
        session.save_test_data("auth_token", "token789", "auth")
        session.save_test_data("test_email", "test@example.com", "credentials")
        
        # Retrieve test data
        job_id = session.get_test_data("job_id", "ids")
        assert job_id == "job123", f"Wrong job ID: {job_id}"
        
        # Check usage tracking
        test_data = session.test_data["ids"]["job_id"]
        assert test_data["used_count"] == 1, "Usage count not incremented"
        assert "last_used" in test_data, "Last used not set"
        
        # Get non-existent data
        result = session.get_test_data("non_existent", "ids")
        assert result is None, "Should return None for non-existent data"
        
        # Get all data in category
        ids_data = session.get_all_test_data("ids")
        assert len(ids_data) == 2, "Wrong number of items in category"
        assert "job_id" in ids_data and "candidate_id" in ids_data, "Missing items"
        
        # Get all data
        all_data = session.get_all_test_data()
        assert len(all_data) == 3, "Wrong number of categories"
        assert "ids" in all_data and "auth" in all_data and "credentials" in all_data, "Missing categories"
    
    def test_api_cache_management(self):
        """Test API response caching."""
        session = DebugSessionState("TEST004", base_dir=self.sessions_dir / "TEST004")
        
        # Cache a small response
        small_response = {"status": "success", "data": {"id": 123}}
        session.cache_api_response("GET", "/api/test", small_response, 200, {"content-type": "application/json"})
        
        # Retrieve cached response
        cached = session.get_cached_response("GET", "/api/test")
        assert cached is not None, "Failed to retrieve cached response"
        assert cached["response"] == small_response, "Wrong response data"
        assert cached["status_code"] == 200, "Wrong status code"
        assert cached["hit_count"] == 1, "Hit count not incremented"
        
        # Cache a large response (should save to file)
        large_response = {"data": "x" * 2000}  # > 1KB
        session.cache_api_response("POST", "/api/large", large_response, 201)
        
        # Check file was created
        cache_files = list(session.cache_dir.glob("*.json"))
        assert len(cache_files) == 1, f"Cache file not created: {cache_files}"
        
        # Retrieve large cached response
        cached_large = session.get_cached_response("POST", "/api/large")
        assert cached_large is not None, "Failed to retrieve large cached response"
        assert cached_large["response"] == large_response, "Wrong large response data"
        
        # Test cache miss
        miss = session.get_cached_response("DELETE", "/api/missing")
        assert miss is None, "Should return None for cache miss"
    
    def test_failed_attempts_tracking(self):
        """Test recording failed debugging attempts."""
        session = DebugSessionState("TEST005", base_dir=self.sessions_dir / "TEST005")
        
        # Set current step
        session.set_current_step("test_api_call", "Testing API endpoint")
        
        # Record failed attempts
        session.record_failed_attempt(
            "API call failed", 
            "404 Not Found",
            {"url": "/api/test", "method": "GET"},
            "Need to check if endpoint exists"
        )
        
        session.record_failed_attempt(
            "Database query failed",
            "relation does not exist",
            {"query": "SELECT * FROM missing_table"},
            "Table might not be created yet"
        )
        
        # Check attempts recorded
        assert len(session.failed_attempts) == 2, "Failed attempts not recorded"
        assert session.failed_attempts[0]["description"] == "API call failed", "Wrong description"
        assert session.failed_attempts[1]["error"] == "relation does not exist", "Wrong error"
        assert session.failed_attempts[0]["step"]["name"] == "test_api_call", "Step not recorded"
    
    def test_findings_documentation(self):
        """Test documenting debugging findings."""
        session = DebugSessionState("TEST006", base_dir=self.sessions_dir / "TEST006")
        
        # Add various findings
        session.add_finding(
            "observation",
            "API returns empty array for new users",
            evidence="GET /api/user/123/jobs returns []",
            fix_suggestion="Check if this is expected behavior",
            related_files=["api/routes/user.js"]
        )
        
        session.add_finding(
            "root_cause",
            "Missing database index causes slow queries",
            evidence="EXPLAIN shows sequential scan",
            fix_suggestion="Add index on user_id column",
            related_files=["schema/migrations/add_indexes.sql"]
        )
        
        session.add_finding(
            "hypothesis",
            "Race condition in concurrent requests",
            evidence="Intermittent failures under load"
        )
        
        # Check findings recorded
        assert len(session.findings) == 3, "Findings not recorded"
        
        # Get findings by type
        observations = session.get_findings_by_type("observation")
        assert len(observations) == 1, "Wrong number of observations"
        assert observations[0]["description"] == "API returns empty array for new users", "Wrong observation"
        
        root_causes = session.get_findings_by_type("root_cause")
        assert len(root_causes) == 1, "Wrong number of root causes"
        assert "Missing database index" in root_causes[0]["description"], "Wrong root cause"
    
    def test_step_management(self):
        """Test debugging step tracking."""
        session = DebugSessionState("TEST007", base_dir=self.sessions_dir / "TEST007")
        
        # Set current step
        session.set_current_step("login", "Testing user login flow")
        assert session.current_step is not None, "Current step not set"
        assert session.current_step["name"] == "login", "Wrong step name"
        assert "started_at" in session.current_step, "Started time not set"
        
        # Complete step
        session.complete_current_step("Login successful, token received")
        assert "completed_at" in session.current_step, "Completed time not set"
        assert session.current_step["notes"] == "Login successful, token received", "Notes not saved"
        assert session.last_successful_step == "login", "Last successful step not updated"
        
        # Set new step
        session.set_current_step("create_job", "Testing job creation")
        assert session.current_step["name"] == "create_job", "New step not set"
    
    def test_artifact_management(self):
        """Test saving debugging artifacts."""
        session = DebugSessionState("TEST008", base_dir=self.sessions_dir / "TEST008")
        
        # Save artifact from content
        content = b"Test screenshot data"
        artifact_path = session.save_artifact("test_screenshot.png", content=content, artifact_type="screenshots")
        assert artifact_path.exists(), "Artifact not saved"
        assert artifact_path.read_bytes() == content, "Wrong artifact content"
        
        # Save artifact from file
        source_file = self.test_dir / "source.txt"
        source_file.write_text("Source file content")
        
        artifact_path2 = session.save_artifact("copied.txt", source_path=str(source_file), artifact_type="logs")
        assert artifact_path2.exists(), "Artifact not copied"
        assert artifact_path2.read_text() == "Source file content", "Wrong copied content"
        
        # Check subdirectories created
        assert (session.artifacts_dir / "screenshots").exists(), "Screenshots dir not created"
        assert (session.artifacts_dir / "logs").exists(), "Logs dir not created"
    
    def test_session_summary(self):
        """Test session summary generation."""
        session = DebugSessionState("TEST009", base_dir=self.sessions_dir / "TEST009")
        
        # Add various data
        session.create_checkpoint("cp1", "First checkpoint")
        session.save_test_data("id1", "value1", "cat1")
        session.save_test_data("id2", "value2", "cat2")
        session.cache_api_response("GET", "/test", {"data": "test"})
        session.record_failed_attempt("Test failed", "Error message")
        session.add_finding("observation", "Test finding")
        session.set_current_step("current", "Current step")
        
        # Get summary
        summary = session.get_summary()
        assert summary["session_id"] == "TEST009", "Wrong session ID"
        assert summary["checkpoints_count"] == 1, "Wrong checkpoint count"
        assert summary["test_data_items"] == 2, "Wrong test data count"
        assert summary["cached_api_calls"] == 1, "Wrong cache count"
        assert summary["failed_attempts"] == 1, "Wrong failed attempts count"
        assert summary["findings"] == 1, "Wrong findings count"
        assert summary["current_step"]["name"] == "current", "Wrong current step"
        
        # Test print summary (should not error)
        session.print_summary()
    
    def test_resume_helpers(self):
        """Test session resume functionality."""
        session = DebugSessionState("TEST010", base_dir=self.sessions_dir / "TEST010")
        
        # Test suggestions with login step
        session.last_successful_step = "login"
        suggestions = session.suggest_next_steps()
        assert any("authenticated API" in s for s in suggestions), "No API suggestion after login"
        
        # Test suggestions with create step
        session.last_successful_step = "create_job"
        suggestions = session.suggest_next_steps()
        assert any("verify" in s.lower() and "displayed" in s.lower() for s in suggestions), "No verify suggestion"
        
        # Test suggestions with root cause finding
        session.add_finding("root_cause", "Missing validation on form submit")
        suggestions = session.suggest_next_steps()
        assert any("implement fix" in s.lower() for s in suggestions), "No fix suggestion"
        
        # Test suggestions with failed attempt
        session.record_failed_attempt("API call failed", "500 error")
        suggestions = session.suggest_next_steps()
        assert any("retry" in s.lower() for s in suggestions), "No retry suggestion"
    
    def test_session_management_functions(self):
        """Test session management helper functions."""
        # Create multiple test sessions
        for i in range(3):
            session = DebugSessionState(f"MGMT{i:03d}", base_dir=self.sessions_dir / f"MGMT{i:03d}")
            session.create_checkpoint(f"checkpoint_{i}", f"Test checkpoint {i}")
            session.add_finding("observation", f"Finding {i}")
            time.sleep(0.1)  # Ensure different timestamps
        
        # List sessions
        sessions = list_sessions(self.sessions_dir)
        assert len(sessions) >= 3, f"Not all sessions listed: {len(sessions)}"
        assert sessions[0]["session_id"].startswith("MGMT"), "Wrong session ID format"
        
        # Load existing session
        loaded = load_session("MGMT001")
        loaded.base_dir = self.sessions_dir / "MGMT001"  # Fix base dir for test
        assert loaded.session_id == "MGMT001", "Wrong loaded session ID"
        
        # Test cleanup (create old session)
        old_session_dir = self.sessions_dir / "OLD001"
        old_session_dir.mkdir()
        state_file = old_session_dir / "state.json"
        state_file.write_text(json.dumps({"session_id": "OLD001"}))
        
        # Make it old by modifying mtime
        old_time = time.time() - (35 * 24 * 60 * 60)  # 35 days ago
        os.utime(state_file, (old_time, old_time))
        
        # Run cleanup
        cleaned = cleanup_old_sessions(days=30, base_dir=self.sessions_dir)
        assert cleaned >= 1, "Old session not cleaned"
        assert not old_session_dir.exists(), "Old session directory still exists"
    
    def test_state_persistence(self):
        """Test that state persists across session loads."""
        session_id = "PERSIST001"
        base_dir = self.sessions_dir / session_id
        
        # Create session and add data
        session1 = DebugSessionState(session_id, base_dir=base_dir)
        session1.save_test_data("test_key", "test_value", "test_cat")
        session1.create_checkpoint("test_checkpoint", "Test checkpoint")
        session1.add_finding("observation", "Test observation")
        session1.cache_api_response("GET", "/test", {"test": "data"})
        session1.record_failed_attempt("Test failure", "Test error")
        
        # Load session in new instance
        session2 = DebugSessionState(session_id, base_dir=base_dir)
        
        # Verify all data persisted
        assert session2.get_test_data("test_key", "test_cat") == "test_value", "Test data not persisted"
        assert len(session2.checkpoints) == 1, "Checkpoints not persisted"
        assert len(session2.findings) == 1, "Findings not persisted"
        assert len(session2.api_cache) == 1, "API cache not persisted"
        assert len(session2.failed_attempts) == 1, "Failed attempts not persisted"
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        session = DebugSessionState("EDGE001", base_dir=self.sessions_dir / "EDGE001")
        
        # Test empty checkpoint restoration
        success = session.restore_checkpoint("")
        assert not success, "Should fail for empty checkpoint name"
        
        # Test saving None values
        session.save_test_data("null_test", None, "edge")
        retrieved = session.get_test_data("null_test", "edge")
        assert retrieved is None, "None value not handled correctly"
        
        # Test large data in checkpoint
        large_data = {"key": "x" * 10000}
        checkpoint = session.create_checkpoint("large", "Large data test", large_data)
        assert checkpoint is not None, "Failed to create checkpoint with large data"
        
        # Test special characters in session ID
        special_session = DebugSessionState("TEST-123_ABC", base_dir=self.sessions_dir / "special")
        assert special_session.session_id == "TEST-123_ABC", "Special characters not preserved"
        
        # Test concurrent access (simplified)
        session.save_test_data("concurrent", "value1", "test")
        session._save_state()
        
        # Simulate concurrent modification
        state_file = session._get_state_file()
        with open(state_file, 'r') as f:
            state = json.load(f)
        state['test_data']['test']['concurrent']['value'] = "value2"
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        # Reload and check (should have the modified value)
        session._load_state()
        concurrent_value = session.get_test_data("concurrent", "test")
        assert concurrent_value == "value2", "Concurrent modification not detected"
    
    def run_all_tests(self):
        """Run all tests and report results."""
        print("\n" + "="*60)
        print(" TESTING DEBUG SESSION STATE MANAGEMENT")
        print("="*60)
        
        self.setup()
        
        # Run all test methods
        test_methods = [
            ("Session Initialization", self.test_session_initialization),
            ("Checkpoint Management", self.test_checkpoint_management),
            ("Test Data Management", self.test_test_data_management),
            ("API Cache Management", self.test_api_cache_management),
            ("Failed Attempts Tracking", self.test_failed_attempts_tracking),
            ("Findings Documentation", self.test_findings_documentation),
            ("Step Management", self.test_step_management),
            ("Artifact Management", self.test_artifact_management),
            ("Session Summary", self.test_session_summary),
            ("Resume Helpers", self.test_resume_helpers),
            ("Session Management Functions", self.test_session_management_functions),
            ("State Persistence", self.test_state_persistence),
            ("Edge Cases", self.test_edge_cases),
        ]
        
        for test_name, test_func in test_methods:
            self.run_test(test_name, test_func)
        
        self.teardown()
        
        # Print summary
        total_tests = len(self.passed_tests) + len(self.failed_tests)
        pass_rate = (len(self.passed_tests) / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "="*60)
        print(" TEST RESULTS SUMMARY")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {len(self.passed_tests)} ({pass_rate:.1f}%)")
        print(f"Failed: {len(self.failed_tests)} ({100-pass_rate:.1f}%)")
        
        if self.passed_tests:
            print("\n PASSED TESTS:")
            for test in self.passed_tests:
                print(f"   - {test}")
        
        if self.failed_tests:
            print("\n FAILED TESTS:")
            for test, error in self.failed_tests:
                print(f"   - {test}")
                print(f"     Error: {error}")
        
        print("\n" + "="*60)
        if len(self.failed_tests) == 0:
            print(" ALL TESTS PASSED! Debug session state management is ready.")
        else:
            print("  Some tests failed. Please fix the issues above.")
        print("="*60)
        
        return len(self.failed_tests) == 0


if __name__ == "__main__":
    tester = TestDebugSessionState()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)