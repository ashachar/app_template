#!/usr/bin/env python3
"""
Parallel Debugger - Main orchestrator for parallel debugging execution.
Manages worker processes, resource allocation, and result aggregation.
"""

import os
import sys
import time
import signal
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from multiprocessing import Process, Queue, Event, Manager
from concurrent.futures import ProcessPoolExecutor, as_completed
import threading

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from debug_session import DebugSession
from debug_session_state import DebugSessionState
from parallel_config import ParallelDebugConfig, TestScenario, ResourceConfig
from debug_worker import run_worker
from result_aggregator import ResultAggregator, AggregatedResults
from parallel_monitor import ParallelMonitor


class ParallelDebugger:
    """Main orchestrator for parallel debugging execution."""
    
    def __init__(self, issue_type: str, config: Optional[ParallelDebugConfig] = None):
        """Initialize the parallel debugger."""
        self.issue_type = issue_type
        self.config = config or ParallelDebugConfig()
        
        # Create master debug session
        self.master_session = DebugSession(f"parallel-{issue_type}")
        self.master_state = DebugSessionState(self.master_session.session_id)
        
        # Multiprocessing components
        self.manager = Manager()
        self.result_queue = self.manager.Queue()
        self.status_queue = self.manager.Queue()
        self.shutdown_event = self.manager.Event()
        
        # Worker tracking
        self.workers: Dict[str, Process] = {}
        self.worker_scenarios: Dict[str, TestScenario] = {}
        
        # Results and monitoring
        self.aggregator = ResultAggregator(self.master_session.session_id)
        self.monitor = None
        self.monitor_thread = None
        
        # Signal handling
        self._setup_signal_handlers()
        
        print(f" Parallel Debugger initialized")
        print(f"   Master Session: {self.master_session.session_id}")
        print(f"   Max Workers: {self.config.resource_config.max_workers}")
        print(f"   Issue Type: {issue_type}")
        print()
    
    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        def signal_handler(sig, frame):
            print("\n  Interrupt received, shutting down gracefully...")
            self.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def run_parallel(self, scenarios: Optional[List[TestScenario]] = None,
                          max_workers: Optional[int] = None,
                          with_monitor: bool = True) -> AggregatedResults:
        """Run scenarios in parallel and return aggregated results."""
        # Use provided scenarios or config scenarios
        scenarios = scenarios or self.config.scenarios
        if not scenarios:
            raise ValueError("No scenarios provided for parallel execution")
        
        # Update max workers if specified
        if max_workers:
            self.config.resource_config.max_workers = max_workers
        
        # Validate configuration
        warnings = self.config.validate_configuration()
        if warnings:
            print("  Configuration warnings:")
            for warning in warnings:
                print(f"   {warning}")
            print()
        
        # Save initial state
        self.master_state.set_current_step("initialization", "Preparing parallel execution")
        self.master_state.metadata['scenarios'] = [s.name for s in scenarios]
        self.master_state.metadata['max_workers'] = self.config.resource_config.max_workers
        self.master_state._save_state()
        
        # Start monitoring if requested
        if with_monitor:
            self._start_monitoring()
        
        print(f" Executing {len(scenarios)} scenarios with up to {self.config.resource_config.max_workers} workers")
        print()
        
        try:
            # Execute scenarios
            await self._execute_scenarios(scenarios)
            
            # Wait for all results
            results = self._collect_results()
            
            # Aggregate results
            self.master_state.set_current_step("aggregation", "Aggregating results from all workers")
            aggregated = self.aggregator.aggregate()
            
            # Save final state
            self.master_state.create_checkpoint(
                "parallel_execution_complete",
                f"Completed {aggregated.total_scenarios} scenarios"
            )
            
            # Generate and display report
            print("\n" + "="*80)
            print(self.aggregator.generate_report())
            
            return aggregated
            
        except Exception as e:
            print(f" Parallel execution failed: {str(e)}")
            self.master_state.record_failed_attempt(
                "Parallel execution",
                str(e),
                {"scenarios": len(scenarios)},
                "Master orchestrator failure"
            )
            raise
        
        finally:
            self.shutdown()
    
    async def _execute_scenarios(self, scenarios: List[TestScenario]):
        """Execute scenarios in parallel batches."""
        self.master_state.set_current_step("execution", "Running scenarios in parallel")
        
        # Process scenarios in batches based on max workers
        scenario_queue = list(scenarios)
        active_workers = {}
        completed = 0
        
        while scenario_queue or active_workers:
            # Start new workers up to the limit
            while scenario_queue and len(active_workers) < self.config.resource_config.max_workers:
                scenario = scenario_queue.pop(0)
                worker_id = self._start_worker(scenario)
                if worker_id:
                    active_workers[worker_id] = scenario
            
            # Check for completed workers
            completed_workers = []
            for worker_id, process in self.workers.items():
                if worker_id in active_workers and not process.is_alive():
                    completed_workers.append(worker_id)
            
            # Clean up completed workers
            for worker_id in completed_workers:
                scenario = active_workers.pop(worker_id)
                del self.workers[worker_id]
                self.config.release_ports(worker_id)
                completed += 1
                
                print(f" Completed {scenario.name} ({completed}/{len(scenarios)})")
            
            # Brief sleep to prevent busy waiting
            await asyncio.sleep(0.1)
    
    def _start_worker(self, scenario: TestScenario) -> Optional[str]:
        """Start a worker process for a scenario."""
        worker_id = f"worker_{len(self.workers)}"
        
        try:
            # Allocate ports
            ports = self.config.allocate_ports(worker_id)
            
            # Get worker environment
            env = self.config.get_worker_env(worker_id, scenario)
            
            # Create worker process
            process = Process(
                target=run_worker,
                args=(worker_id, scenario, self.result_queue, 
                      self.status_queue, self.shutdown_event, env),
                name=f"DebugWorker-{worker_id}"
            )
            
            # Start process
            process.start()
            
            # Track worker
            self.workers[worker_id] = process
            self.worker_scenarios[worker_id] = scenario
            
            print(f" Started {worker_id} for scenario '{scenario.name}' (ports: {ports})")
            
            return worker_id
            
        except Exception as e:
            print(f" Failed to start worker for {scenario.name}: {str(e)}")
            self.config.release_ports(worker_id)
            return None
    
    def _collect_results(self) -> List[Dict]:
        """Collect all results from the result queue."""
        print("\n Collecting results from workers...")
        
        results = []
        timeout_count = 0
        max_timeouts = 10
        
        while len(results) < len(self.worker_scenarios):
            try:
                # Get result with timeout
                result = self.result_queue.get(timeout=5)
                results.append(result)
                self.aggregator.add_result(result)
                
                # Reset timeout count on successful get
                timeout_count = 0
                
            except:
                timeout_count += 1
                if timeout_count >= max_timeouts:
                    print(f"  Timeout waiting for results. Got {len(results)}/{len(self.worker_scenarios)}")
                    break
        
        return results
    
    def _start_monitoring(self):
        """Start the monitoring dashboard in a separate thread."""
        try:
            self.monitor = ParallelMonitor(self.status_queue, self.worker_scenarios)
            self.monitor_thread = threading.Thread(
                target=self.monitor.run,
                daemon=True
            )
            self.monitor_thread.start()
        except Exception as e:
            print(f"  Could not start monitor: {e}")
    
    def shutdown(self):
        """Gracefully shut down all workers and clean up resources."""
        print("\n Shutting down parallel debugger...")
        
        # Signal all workers to shutdown
        self.shutdown_event.set()
        
        # Wait for workers to finish (with timeout)
        for worker_id, process in self.workers.items():
            process.join(timeout=5)
            if process.is_alive():
                print(f"  Force terminating {worker_id}")
                process.terminate()
                process.join(timeout=2)
        
        # Stop monitoring
        if self.monitor:
            self.monitor.stop()
        
        # Clean up resources
        for worker_id in list(self.workers.keys()):
            self.config.release_ports(worker_id)
        
        # Save final state
        self.master_state.complete_current_step("Parallel execution shutdown")
        
        print(" Shutdown complete")
    
    def run_scenario_batch(self, scenario_names: List[str],
                          test_type: str = "ui_flow",
                          user_type: Optional[str] = None) -> AggregatedResults:
        """Convenience method to run a batch of similar scenarios."""
        scenarios = []
        
        for name in scenario_names:
            scenario = TestScenario(
                name=name,
                test_type=test_type,
                test_function=name,
                user_type=user_type
            )
            scenarios.append(scenario)
        
        # Run synchronously for convenience
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.run_parallel(scenarios))
        finally:
            loop.close()


# Convenience functions
async def debug_parallel(issue_type: str, scenarios: List[TestScenario],
                        max_workers: int = 4) -> AggregatedResults:
    """Run parallel debugging with default configuration."""
    debugger = ParallelDebugger(issue_type)
    return await debugger.run_parallel(scenarios, max_workers=max_workers)


def debug_auth_issues() -> AggregatedResults:
    """Debug authentication issues in parallel."""
    from parallel_config import get_auth_scenarios
    
    debugger = ParallelDebugger("auth-issues")
    debugger.config.add_scenarios(get_auth_scenarios())
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(debugger.run_parallel())
    finally:
        loop.close()


def debug_performance_issues() -> AggregatedResults:
    """Debug performance issues in parallel."""
    from parallel_config import get_performance_scenarios
    
    debugger = ParallelDebugger("performance-issues")
    debugger.config.add_scenarios(get_performance_scenarios())
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(debugger.run_parallel())
    finally:
        loop.close()


# Example usage
if __name__ == "__main__":
    from parallel_config import get_standard_scenarios
    
    # Create debugger
    debugger = ParallelDebugger("demo-issue")
    
    # Add scenarios
    debugger.config.add_scenarios(get_standard_scenarios()[:2])  # Just first 2 for demo
    
    # Run
    async def main():
        results = await debugger.run_parallel(max_workers=2)
        print(f"\n Execution complete!")
        print(f"   Success rate: {results.success_rate:.1%}")
        print(f"   Total duration: {results.total_duration:.2f}s")
    
    asyncio.run(main())