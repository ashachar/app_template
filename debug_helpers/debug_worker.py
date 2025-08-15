#!/usr/bin/env python3
"""
Debug Worker - Executes individual test scenarios in parallel.
Each worker runs in isolation with its own resources and session state.
"""

import os
import sys
import json
import time
import traceback
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from multiprocessing import Process, Queue, Event

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from debug_session import DebugSession
from debug_session_state import DebugSessionState
from analyze_logs import LogAnalyzer
from parallel_config import TestScenario, TestType


class WorkerResult:
    """Container for worker execution results."""
    
    def __init__(self, worker_id: str, scenario_name: str):
        self.worker_id = worker_id
        self.scenario_name = scenario_name
        self.success = False
        self.start_time = datetime.now()
        self.end_time = None
        self.duration = None
        self.error = None
        self.traceback = None
        self.logs = []
        self.findings = []
        self.metrics = {}
        self.artifacts = []
        self.session_id = None
        self.checkpoints = []
        
    def complete(self, success: bool, error: Optional[str] = None):
        """Mark the worker result as complete."""
        self.success = success
        self.error = error
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            'worker_id': self.worker_id,
            'scenario_name': self.scenario_name,
            'success': self.success,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'error': self.error,
            'traceback': self.traceback,
            'logs': self.logs,
            'findings': self.findings,
            'metrics': self.metrics,
            'artifacts': self.artifacts,
            'session_id': self.session_id,
            'checkpoints': self.checkpoints
        }


class DebugWorker:
    """Worker process for executing debug scenarios."""
    
    def __init__(self, worker_id: str, scenario: TestScenario, 
                 result_queue: Queue, status_queue: Queue,
                 shutdown_event: Event, env: Dict[str, str]):
        self.worker_id = worker_id
        self.scenario = scenario
        self.result_queue = result_queue
        self.status_queue = status_queue
        self.shutdown_event = shutdown_event
        self.env = env
        
        # Initialize debug session and state
        self.debug_session = None
        self.state = None
        self.result = WorkerResult(worker_id, scenario.name)
        
    def run(self):
        """Main worker execution method."""
        try:
            self._initialize_session()
            self._send_status("starting", f"Initializing {self.scenario.name}")
            
            # Execute based on test type
            if self.scenario.test_type == TestType.UI_FLOW:
                self._run_ui_test()
            elif self.scenario.test_type == TestType.API_TEST:
                self._run_api_test()
            elif self.scenario.test_type == TestType.DATABASE:
                self._run_database_test()
            elif self.scenario.test_type == TestType.INTEGRATION:
                self._run_integration_test()
            elif self.scenario.test_type == TestType.PERFORMANCE:
                self._run_performance_test()
            else:
                raise ValueError(f"Unknown test type: {self.scenario.test_type}")
            
            # Mark as successful if no exception
            self.result.complete(success=True)
            self._send_status("completed", f"Successfully completed {self.scenario.name}")
            
        except Exception as e:
            self.result.complete(success=False, error=str(e))
            self.result.traceback = traceback.format_exc()
            self._send_status("failed", f"Failed: {str(e)}")
            
            # Record failure in state
            if self.state:
                self.state.record_failed_attempt(
                    f"Worker {self.worker_id} test execution",
                    str(e),
                    {"scenario": self.scenario.name, "test_type": self.scenario.test_type.value},
                    "Worker process failed during test execution"
                )
        
        finally:
            self._cleanup()
            self._send_final_result()
    
    def _initialize_session(self):
        """Initialize debug session and state."""
        # Create unique session for this worker
        session_type = f"{self.scenario.name}-{self.worker_id}"
        self.debug_session = DebugSession(session_type)
        self.result.session_id = self.debug_session.session_id
        
        # Initialize state with worker-specific directory
        worker_state_dir = Path(__file__).parent / 'sessions' / 'parallel' / self.worker_id
        self.state = DebugSessionState(self.debug_session.session_id, base_dir=worker_state_dir)
        
        # Save scenario information
        self.state.metadata['worker_id'] = self.worker_id
        self.state.metadata['scenario'] = self.scenario.name
        self.state.metadata['test_type'] = self.scenario.test_type.value
        self.state._save_state()
        
        # Set initial step
        self.state.set_current_step("initialization", f"Starting {self.scenario.name}")
    
    def _send_status(self, status: str, message: str):
        """Send status update to the orchestrator."""
        try:
            self.status_queue.put({
                'worker_id': self.worker_id,
                'scenario': self.scenario.name,
                'status': status,
                'message': message,
                'timestamp': datetime.now().isoformat()
            })
        except:
            pass  # Don't fail if status queue is full
    
    def _send_final_result(self):
        """Send final result to the orchestrator."""
        # Collect session state data
        if self.state:
            summary = self.state.get_summary()
            self.result.checkpoints = [cp['name'] for cp in self.state.checkpoints]
            self.result.findings = self.state.findings
            
            # Get test data summary
            test_data_summary = {}
            for category, items in self.state.test_data.items():
                test_data_summary[category] = list(items.keys())
            self.result.metrics['test_data'] = test_data_summary
            
            # Get cache hit rate
            cache_hits = sum(1 for item in self.state.api_cache.values() 
                           if item.get('hit_count', 0) > 0)
            self.result.metrics['cache_hit_rate'] = (
                cache_hits / len(self.state.api_cache) 
                if self.state.api_cache else 0
            )
        
        # Send result
        self.result_queue.put(self.result.to_dict())
    
    def _run_ui_test(self):
        """Run UI flow test using Playwright."""
        self._send_status("running", "Starting UI test")
        self.state.set_current_step("ui_test", "Running UI flow test")
        
        # Build test script path
        test_function = self.scenario.test_function
        if not test_function.endswith(('.py', '.js')):
            # Assume it's a function name in standard test files
            test_script = self._find_test_script(test_function)
        else:
            test_script = test_function
        
        if not test_script:
            raise FileNotFoundError(f"Test script not found: {test_function}")
        
        # Prepare environment with ports and session info
        test_env = self.env.copy()
        test_env['DEBUG_SESSION_ID'] = self.debug_session.session_id
        test_env['DEBUG_WORKER_ID'] = self.worker_id
        test_env['BASE_URL'] = f"http://localhost:{test_env.get('APP_PORT', '3000')}"
        
        # Add user type specific credentials
        if self.scenario.user_type == 'recruiter':
            test_env['TEST_EMAIL'] = test_env.get('TEST_RECRUITER_EMAIL', '')
            test_env['TEST_PASSWORD'] = test_env.get('TEST_RECRUITER_PASSWORD', '')
        elif self.scenario.user_type == 'candidate':
            test_env['TEST_EMAIL'] = test_env.get('TEST_CANDIDATE_EMAIL', '')
            test_env['TEST_PASSWORD'] = test_env.get('TEST_CANDIDATE_PASSWORD', '')
        
        # Run the test
        self._execute_test_script(test_script, test_env)
        
        # Create checkpoint
        self.state.create_checkpoint("ui_test_complete", "UI test execution finished")
    
    def _run_api_test(self):
        """Run API endpoint tests."""
        self._send_status("running", "Starting API tests")
        self.state.set_current_step("api_test", "Running API endpoint tests")
        
        # For API tests, we might use a different approach
        # This is a placeholder - implement based on your API test structure
        test_script = self._find_test_script(self.scenario.test_function)
        if test_script:
            test_env = self.env.copy()
            test_env['API_BASE_URL'] = f"http://localhost:{test_env.get('API_PORT', '3001')}"
            self._execute_test_script(test_script, test_env)
        
        self.state.create_checkpoint("api_test_complete", "API tests finished")
    
    def _run_database_test(self):
        """Run database-specific tests."""
        self._send_status("running", "Starting database tests")
        self.state.set_current_step("database_test", "Running database tests")
        
        # Implement database test execution
        # This might involve running SQL queries, checking data integrity, etc.
        self.state.add_finding(
            "observation",
            "Database test execution placeholder",
            evidence="Would run database-specific tests here"
        )
        
        self.state.create_checkpoint("database_test_complete", "Database tests finished")
    
    def _run_integration_test(self):
        """Run integration tests spanning multiple components."""
        self._send_status("running", "Starting integration tests")
        self.state.set_current_step("integration_test", "Running integration tests")
        
        test_script = self._find_test_script(self.scenario.test_function)
        if test_script:
            self._execute_test_script(test_script, self.env)
        
        self.state.create_checkpoint("integration_test_complete", "Integration tests finished")
    
    def _run_performance_test(self):
        """Run performance tests."""
        self._send_status("running", "Starting performance tests")
        self.state.set_current_step("performance_test", "Running performance tests")
        
        # Performance tests might need special handling
        self.result.metrics['performance'] = {
            'response_times': [],
            'throughput': 0,
            'error_rate': 0
        }
        
        test_script = self._find_test_script(self.scenario.test_function)
        if test_script:
            self._execute_test_script(test_script, self.env)
        
        self.state.create_checkpoint("performance_test_complete", "Performance tests finished")
    
    def _execute_test_script(self, script_path: str, env: Dict[str, str]):
        """Execute a test script and capture output."""
        self._send_status("executing", f"Running {script_path}")
        
        # Determine script type and command
        if script_path.endswith('.py'):
            cmd = [sys.executable, script_path]
        elif script_path.endswith('.js'):
            cmd = ['node', script_path]
        else:
            raise ValueError(f"Unsupported script type: {script_path}")
        
        # Run with timeout
        try:
            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Monitor process with timeout
            stdout, stderr = process.communicate(timeout=self.scenario.timeout)
            
            # Capture output
            if stdout:
                self.result.logs.extend(stdout.splitlines())
            if stderr:
                self.result.logs.extend([f"STDERR: {line}" for line in stderr.splitlines()])
            
            # Check return code
            if process.returncode != 0:
                raise RuntimeError(f"Test script failed with code {process.returncode}")
            
            # Parse output for specific patterns
            self._parse_test_output(stdout + stderr)
            
        except subprocess.TimeoutExpired:
            process.kill()
            raise TimeoutError(f"Test exceeded timeout of {self.scenario.timeout}s")
        except Exception as e:
            raise RuntimeError(f"Failed to execute test script: {str(e)}")
    
    def _parse_test_output(self, output: str):
        """Parse test output for metrics and findings."""
        # Look for specific patterns in output
        lines = output.splitlines()
        
        for line in lines:
            # Extract metrics (example patterns)
            if "METRIC:" in line:
                try:
                    _, metric_data = line.split("METRIC:", 1)
                    metric = json.loads(metric_data.strip())
                    self.result.metrics.update(metric)
                except:
                    pass
            
            # Extract findings
            elif "FINDING:" in line:
                try:
                    _, finding_data = line.split("FINDING:", 1)
                    finding = json.loads(finding_data.strip())
                    self.state.add_finding(**finding)
                except:
                    pass
            
            # Extract artifacts
            elif "ARTIFACT:" in line:
                try:
                    _, artifact_path = line.split("ARTIFACT:", 1)
                    self.result.artifacts.append(artifact_path.strip())
                except:
                    pass
    
    def _find_test_script(self, test_function: str) -> Optional[str]:
        """Find test script by function name."""
        # Search in common test directories
        search_paths = [
            Path(__file__).parent.parent / 'tests' / 'integration',
            Path(__file__).parent.parent / 'tests' / 'unit',
            Path(__file__).parent.parent / 'tests' / 'parallel',
            Path(__file__).parent / 'test_scripts'
        ]
        
        # Look for exact file match
        for base_path in search_paths:
            if base_path.exists():
                # Check for .py and .js files
                for ext in ['.py', '.js']:
                    test_file = base_path / f"{test_function}{ext}"
                    if test_file.exists():
                        return str(test_file)
                
                # Search in subdirectories
                for test_file in base_path.rglob(f"{test_function}.*"):
                    if test_file.suffix in ['.py', '.js']:
                        return str(test_file)
        
        return None
    
    def _cleanup(self):
        """Clean up worker resources."""
        try:
            # Close debug session
            if self.debug_session:
                self.debug_session.close_session()
            
            # Save final state
            if self.state:
                self.state.complete_current_step("Worker execution complete")
                self.state._save_state()
            
            self._send_status("cleanup", "Cleaning up resources")
        except:
            pass  # Don't fail cleanup


def run_worker(worker_id: str, scenario: TestScenario,
               result_queue: Queue, status_queue: Queue,
               shutdown_event: Event, env: Dict[str, str]):
    """Entry point for worker process."""
    worker = DebugWorker(worker_id, scenario, result_queue, 
                        status_queue, shutdown_event, env)
    worker.run()


# Test worker functionality
if __name__ == "__main__":
    from multiprocessing import Queue, Event
    from parallel_config import TestScenario, TestType
    
    # Create test scenario
    scenario = TestScenario(
        name="test_worker_demo",
        test_type=TestType.UI_FLOW,
        test_function="demo_test",
        user_type="recruiter"
    )
    
    # Create queues and event
    result_queue = Queue()
    status_queue = Queue()
    shutdown_event = Event()
    
    # Run worker
    env = os.environ.copy()
    env['APP_PORT'] = '3100'
    env['API_PORT'] = '3101'
    
    worker = DebugWorker("demo_worker", scenario, result_queue, 
                        status_queue, shutdown_event, env)
    worker.run()
    
    # Get result
    result = result_queue.get()
    print(f"Worker result: {json.dumps(result, indent=2)}")