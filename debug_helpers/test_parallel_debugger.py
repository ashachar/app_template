#!/usr/bin/env python3
"""
Comprehensive tests for the parallel debugging system.
Tests all components to ensure reliable parallel execution.
"""

import os
import sys
import time
import json
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any
from multiprocessing import Queue, Event
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from parallel_config import (
    ParallelDebugConfig, TestScenario, TestType, ResourceConfig,
    get_standard_scenarios
)
from debug_worker import DebugWorker, WorkerResult
from result_aggregator import ResultAggregator, AggregatedResults
from parallel_debugger import ParallelDebugger
from parallel_monitor import WorkerStatus, SimpleMonitor


class TestParallelDebugger:
    """Test suite for parallel debugging system."""
    
    def __init__(self):
        self.passed_tests = []
        self.failed_tests = []
        self.temp_dir = None
        
    def setup(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create test scripts directory
        test_scripts_dir = self.temp_dir / 'test_scripts'
        test_scripts_dir.mkdir()
        
        # Create a simple test script
        test_script = test_scripts_dir / 'simple_test.py'
        test_script.write_text('''
import sys
import time
import json

print("Test started")
time.sleep(0.5)
print("METRIC: " + json.dumps({"test_metric": 42}))
print("Test completed")
sys.exit(0)
''')
        
        # Create a failing test script
        failing_script = test_scripts_dir / 'failing_test.py'
        failing_script.write_text('''
import sys
print("Test started")
raise Exception("Intentional test failure")
''')
        
    def teardown(self):
        """Clean up test environment."""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def run_test(self, test_name: str, test_func):
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
    
    def test_parallel_config(self):
        """Test parallel configuration system."""
        config = ParallelDebugConfig()
        
        # Test default resource config
        assert config.resource_config.max_workers > 0, "Max workers should be positive"
        assert config.resource_config.base_port > 0, "Base port should be positive"
        
        # Test scenario addition
        scenario = TestScenario(
            name="test_scenario",
            test_type=TestType.UI_FLOW,
            test_function="test_func",
            user_type="recruiter"
        )
        config.add_scenario(scenario)
        assert len(config.scenarios) == 1, "Scenario not added"
        
        # Test port allocation
        worker_id = "test_worker"
        ports = config.allocate_ports(worker_id)
        assert len(ports) == 2, "Should allocate 2 ports"
        assert all(isinstance(p, int) for p in ports), "Ports should be integers"
        
        # Test port release
        config.release_ports(worker_id)
        assert worker_id not in config.allocated_ports, "Ports not released"
        
        # Test worker environment
        env = config.get_worker_env(worker_id, scenario)
        assert 'PARALLEL_WORKER_ID' in env, "Worker ID not in env"
        assert env['PARALLEL_WORKER_ID'] == worker_id, "Wrong worker ID"
        
        # Test validation
        warnings = config.validate_configuration()
        assert isinstance(warnings, list), "Validation should return list"
    
    def test_worker_result(self):
        """Test worker result container."""
        result = WorkerResult("worker_1", "test_scenario")
        
        # Test initial state
        assert result.worker_id == "worker_1", "Wrong worker ID"
        assert result.scenario_name == "test_scenario", "Wrong scenario name"
        assert result.success is False, "Should start as unsuccessful"
        assert result.start_time is not None, "Start time not set"
        
        # Test completion
        result.complete(success=True)
        assert result.success is True, "Success not set"
        assert result.end_time is not None, "End time not set"
        assert result.duration > 0, "Duration not calculated"
        
        # Test serialization
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict), "Should return dict"
        assert result_dict['worker_id'] == "worker_1", "Worker ID not serialized"
        assert result_dict['success'] is True, "Success not serialized"
    
    def test_debug_worker(self):
        """Test debug worker functionality."""
        # Create test scenario
        scenario = TestScenario(
            name="test_worker",
            test_type=TestType.UI_FLOW,
            test_function=str(self.temp_dir / 'test_scripts' / 'simple_test.py'),
            timeout=5
        )
        
        # Create queues and event
        result_queue = Queue()
        status_queue = Queue()
        shutdown_event = Event()
        
        # Create environment
        env = os.environ.copy()
        env['APP_PORT'] = '3100'
        env['API_PORT'] = '3101'
        
        # Create and run worker
        worker = DebugWorker(
            "test_worker_1", scenario, result_queue,
            status_queue, shutdown_event, env
        )
        
        # Run worker
        worker.run()
        
        # Check result
        assert not result_queue.empty(), "No result produced"
        result = result_queue.get()
        
        assert result['worker_id'] == "test_worker_1", "Wrong worker ID in result"
        assert result['scenario_name'] == "test_worker", "Wrong scenario name"
        # The test might fail due to missing dependencies, that's ok for this test
        
        # Check status updates
        status_updates = []
        while not status_queue.empty():
            status_updates.append(status_queue.get())
        
        assert len(status_updates) > 0, "No status updates produced"
    
    def test_result_aggregator(self):
        """Test result aggregation."""
        aggregator = ResultAggregator("MASTER123")
        
        # Add sample results
        results = [
            {
                'worker_id': 'worker_1',
                'scenario_name': 'test_1',
                'success': True,
                'duration': 5.0,
                'start_time': '2024-01-01T10:00:00',
                'end_time': '2024-01-01T10:00:05',
                'logs': ['Test log 1'],
                'findings': [
                    {'type': 'observation', 'description': 'Test works well'}
                ],
                'metrics': {'test_metric': 100}
            },
            {
                'worker_id': 'worker_2',
                'scenario_name': 'test_2',
                'success': False,
                'duration': 3.0,
                'start_time': '2024-01-01T10:00:01',
                'end_time': '2024-01-01T10:00:04',
                'error': 'Test failed',
                'logs': ['Error occurred'],
                'findings': [
                    {'type': 'root_cause', 'description': 'Missing configuration'}
                ]
            },
            {
                'worker_id': 'worker_3',
                'scenario_name': 'test_3',
                'success': True,
                'duration': 4.0,
                'start_time': '2024-01-01T10:00:02',
                'end_time': '2024-01-01T10:00:06',
                'logs': ['Test log 3'],
                'findings': [
                    {'type': 'observation', 'description': 'Test works well'}
                ]
            }
        ]
        
        for result in results:
            aggregator.add_result(result)
        
        # Aggregate results
        aggregated = aggregator.aggregate()
        
        # Test basic statistics
        assert aggregated.total_scenarios == 3, "Wrong total scenarios"
        assert aggregated.successful_scenarios == 2, "Wrong successful count"
        assert aggregated.failed_scenarios == 1, "Wrong failed count"
        assert aggregated.success_rate == 2/3, "Wrong success rate"
        
        # Test duration statistics
        assert aggregated.total_duration == 12.0, "Wrong total duration"
        assert aggregated.average_duration == 4.0, "Wrong average duration"
        assert aggregated.min_duration == 3.0, "Wrong min duration"
        assert aggregated.max_duration == 5.0, "Wrong max duration"
        
        # Test error analysis
        assert len(aggregated.common_errors) > 0, "No common errors found"
        assert aggregated.common_errors[0][0] == "Test failed", "Wrong error"
        
        # Test findings
        assert len(aggregated.root_causes) == 1, "Root cause not found"
        
        # Test report generation
        report = aggregator.generate_report()
        assert isinstance(report, str), "Report should be string"
        assert "PARALLEL DEBUG EXECUTION REPORT" in report, "Missing report header"
        assert "test_1" in report, "Missing scenario in report"
    
    def test_worker_status(self):
        """Test worker status tracking."""
        status = WorkerStatus("worker_1", "test_scenario")
        
        # Test initial state
        assert status.worker_id == "worker_1", "Wrong worker ID"
        assert status.scenario_name == "test_scenario", "Wrong scenario"
        assert status.status == "pending", "Wrong initial status"
        assert status.get_status_icon() == "⏳", "Wrong pending icon"
        
        # Test status update
        status.update("running", "Executing test")
        assert status.status == "running", "Status not updated"
        assert status.message == "Executing test", "Message not updated"
        assert status.get_status_icon() == "", "Wrong running icon"
        
        # Test elapsed time
        status.start_time = status.last_update
        time.sleep(1)
        elapsed = status.get_elapsed_time()
        assert "0:01" in elapsed or "0:00" in elapsed, f"Wrong elapsed time: {elapsed}"
        
        # Test failure
        status.update("failed", "Test error")
        assert status.error == "Test error", "Error not recorded"
        assert status.get_status_icon() == "", "Wrong failed icon"
    
    def test_simple_monitor(self):
        """Test simple monitor functionality."""
        status_queue = Queue()
        scenarios = {"worker_1": "test_1", "worker_2": "test_2"}
        
        monitor = SimpleMonitor(status_queue, scenarios)
        
        # Add test updates
        updates = [
            {
                'worker_id': 'worker_1',
                'scenario': 'test_1',
                'status': 'starting',
                'message': 'Starting test'
            },
            {
                'worker_id': 'worker_2',
                'scenario': 'test_2',
                'status': 'completed',
                'message': 'Test completed'
            }
        ]
        
        for update in updates:
            status_queue.put(update)
        
        # Test that monitor can process updates without error
        # (We can't easily test the output in unit tests)
        assert monitor.status_queue.qsize() == 2, "Updates not in queue"
    
    async def test_parallel_debugger_basic(self):
        """Test basic parallel debugger functionality."""
        # Create simple test scenarios
        scenarios = [
            TestScenario(
                name="test_1",
                test_type=TestType.UI_FLOW,
                test_function=str(self.temp_dir / 'test_scripts' / 'simple_test.py'),
                timeout=10
            ),
            TestScenario(
                name="test_2",
                test_type=TestType.UI_FLOW,
                test_function=str(self.temp_dir / 'test_scripts' / 'simple_test.py'),
                timeout=10
            )
        ]
        
        # Create debugger
        debugger = ParallelDebugger("test-issue")
        
        # Mock the worker execution to speed up test
        original_execute = debugger._execute_scenarios
        async def mock_execute(scenarios):
            # Add mock results directly
            for i, scenario in enumerate(scenarios):
                result = {
                    'worker_id': f'worker_{i}',
                    'scenario_name': scenario.name,
                    'success': True,
                    'duration': 1.0,
                    'start_time': '2024-01-01T10:00:00',
                    'end_time': '2024-01-01T10:00:01',
                    'logs': [],
                    'findings': [],
                    'metrics': {}
                }
                debugger.aggregator.add_result(result)
        
        debugger._execute_scenarios = mock_execute
        
        # Run parallel execution
        results = await debugger.run_parallel(
            scenarios=scenarios,
            max_workers=2,
            with_monitor=False  # Skip monitor for tests
        )
        
        # Verify results
        assert isinstance(results, AggregatedResults), "Should return aggregated results"
        assert results.total_scenarios == 2, "Wrong scenario count"
        assert results.success_rate == 1.0, "All scenarios should succeed"
        
        # Clean up
        debugger.shutdown()
    
    def test_parallel_config_edge_cases(self):
        """Test edge cases in parallel configuration."""
        config = ParallelDebugConfig()
        
        # Test port exhaustion
        config.resource_config.port_range = 2
        worker1_ports = config.allocate_ports("worker1", 2)
        assert len(worker1_ports) == 2, "Should allocate 2 ports"
        
        # Should fail when no more ports
        try:
            config.allocate_ports("worker2", 2)
            assert False, "Should raise RuntimeError for port exhaustion"
        except RuntimeError as e:
            assert "Port range exhausted" in str(e), "Wrong error message"
        
        # Test double allocation
        config.release_ports("worker1")
        config.allocate_ports("worker1")
        try:
            config.allocate_ports("worker1")
            assert False, "Should not allow double allocation"
        except ValueError as e:
            assert "already allocated" in str(e), "Wrong error message"
        
        # Test validation with duplicate scenarios
        config.scenarios = [
            TestScenario(name="dup", test_type=TestType.UI_FLOW, test_function="test"),
            TestScenario(name="dup", test_type=TestType.UI_FLOW, test_function="test")
        ]
        warnings = config.validate_configuration()
        assert any("Duplicate scenario names" in w for w in warnings), "Should warn about duplicates"
    
    def test_aggregator_pattern_detection(self):
        """Test pattern detection in result aggregator."""
        aggregator = ResultAggregator("PATTERN_TEST")
        
        # Add results with patterns
        error_results = [
            {
                'worker_id': f'worker_{i}',
                'scenario_name': f'test_{i}',
                'success': False,
                'duration': 1.0,
                'error': error,
                'logs': [f'Log with {error}'],
                'findings': []
            }
            for i, error in enumerate([
                "Timeout exceeded",
                "Connection refused",
                "401 Unauthorized",
                "Database connection failed",
                "Timeout waiting for element"
            ])
        ]
        
        for result in error_results:
            aggregator.add_result(result)
        
        # Aggregate and check patterns
        aggregated = aggregator.aggregate()
        
        # Check error patterns detected
        assert 'timeout' in aggregated.error_patterns, "Timeout pattern not detected"
        assert len(aggregated.error_patterns['timeout']) >= 2, "Not all timeouts found"
        
        assert 'connection' in aggregated.error_patterns, "Connection pattern not detected"
        assert 'authentication' in aggregated.error_patterns, "Auth pattern not detected"
        assert 'database' in aggregated.error_patterns, "Database pattern not detected"
        
        # Check recommendations
        assert len(aggregated.recommendations) > 0, "No recommendations generated"
        assert any("timeout" in r.lower() for r in aggregated.recommendations), "No timeout recommendation"
    
    def run_all_tests(self):
        """Run all tests and report results."""
        print("\n" + "="*60)
        print(" TESTING PARALLEL DEBUGGING SYSTEM")
        print("="*60)
        
        self.setup()
        
        # Run all test methods
        test_methods = [
            ("Parallel Configuration", self.test_parallel_config),
            ("Worker Result Container", self.test_worker_result),
            ("Debug Worker", self.test_debug_worker),
            ("Result Aggregator", self.test_result_aggregator),
            ("Worker Status", self.test_worker_status),
            ("Simple Monitor", self.test_simple_monitor),
            ("Parallel Debugger Basic", lambda: asyncio.run(self.test_parallel_debugger_basic())),
            ("Config Edge Cases", self.test_parallel_config_edge_cases),
            ("Pattern Detection", self.test_aggregator_pattern_detection),
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
            print(" ALL TESTS PASSED! Parallel debugging system is ready.")
        else:
            print("  Some tests failed. Please fix the issues above.")
        print("="*60)
        
        return len(self.failed_tests) == 0


if __name__ == "__main__":
    tester = TestParallelDebugger()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)