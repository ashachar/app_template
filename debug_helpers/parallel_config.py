#!/usr/bin/env python3
"""
Parallel Debugging Configuration System
Defines test scenarios, resource allocation, and parallelism settings.
"""

import os
import multiprocessing
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class TestType(Enum):
    """Types of tests that can be run in parallel."""
    UI_FLOW = "ui_flow"
    API_TEST = "api_test"
    DATABASE = "database"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    SECURITY = "security"

@dataclass
class TestScenario:
    """Defines a single test scenario for parallel execution."""
    name: str
    test_type: TestType
    test_function: str  # Function name or path to test script
    user_type: Optional[str] = None  # recruiter, candidate, admin
    locale: str = "he"
    data_set: str = "standard"  # standard, edge_cases, minimal, large
    timeout: int = 120  # seconds
    retry_on_failure: bool = True
    max_retries: int = 2
    required_resources: Dict[str, Any] = None
    environment_vars: Dict[str, str] = None
    
    def __post_init__(self):
        if self.required_resources is None:
            self.required_resources = {}
        if self.environment_vars is None:
            self.environment_vars = {}

@dataclass
class ResourceConfig:
    """Configuration for system resources during parallel execution."""
    max_workers: int = None  # Auto-detect if None
    max_browsers_per_worker: int = 1
    base_port: int = 3100  # Start allocating ports from here
    port_range: int = 100  # Allocate ports in range [base_port, base_port + port_range]
    database_pool_size: int = 10
    memory_limit_per_worker_mb: int = 1024
    cpu_cores_per_worker: float = 1.0
    
    def __post_init__(self):
        if self.max_workers is None:
            # Use 75% of available CPU cores by default
            self.max_workers = max(1, int(multiprocessing.cpu_count() * 0.75))

class ParallelDebugConfig:
    """Main configuration class for parallel debugging."""
    
    def __init__(self):
        self.resource_config = ResourceConfig()
        self.scenarios: List[TestScenario] = []
        self.allocated_ports: Dict[str, int] = {}
        self.next_port = self.resource_config.base_port
        
    def add_scenario(self, scenario: TestScenario) -> None:
        """Add a test scenario to the configuration."""
        self.scenarios.append(scenario)
        
    def add_scenarios(self, scenarios: List[TestScenario]) -> None:
        """Add multiple test scenarios."""
        self.scenarios.extend(scenarios)
        
    def allocate_ports(self, worker_id: str, count: int = 2) -> List[int]:
        """Allocate unique ports for a worker (UI and API)."""
        if worker_id in self.allocated_ports:
            raise ValueError(f"Ports already allocated for worker {worker_id}")
        
        ports = []
        for _ in range(count):
            if self.next_port >= self.resource_config.base_port + self.resource_config.port_range:
                raise RuntimeError("Port range exhausted")
            
            ports.append(self.next_port)
            self.next_port += 1
        
        self.allocated_ports[worker_id] = ports
        return ports
    
    def release_ports(self, worker_id: str) -> None:
        """Release ports allocated to a worker."""
        if worker_id in self.allocated_ports:
            del self.allocated_ports[worker_id]
    
    def get_worker_env(self, worker_id: str, scenario: TestScenario) -> Dict[str, str]:
        """Get environment variables for a worker."""
        env = os.environ.copy()
        
        # Add worker-specific ports
        if worker_id in self.allocated_ports:
            ports = self.allocated_ports[worker_id]
            env['APP_PORT'] = str(ports[0])
            env['API_PORT'] = str(ports[1]) if len(ports) > 1 else str(ports[0] + 1)
        
        # Add scenario-specific environment variables
        env.update(scenario.environment_vars)
        
        # Add debugging-specific variables
        env['PARALLEL_WORKER_ID'] = worker_id
        env['PARALLEL_SCENARIO'] = scenario.name
        env['DEBUG_MODE'] = 'parallel'
        
        return env
    
    def validate_configuration(self) -> List[str]:
        """Validate the configuration and return any warnings."""
        warnings = []
        
        # Check if we have enough ports
        total_ports_needed = len(self.scenarios) * 2
        if total_ports_needed > self.resource_config.port_range:
            warnings.append(
                f"Port range ({self.resource_config.port_range}) may be insufficient "
                f"for {len(self.scenarios)} scenarios"
            )
        
        # Check memory requirements
        total_memory_needed = (
            self.resource_config.max_workers * 
            self.resource_config.memory_limit_per_worker_mb
        )
        available_memory = self._get_available_memory_mb()
        if available_memory and total_memory_needed > available_memory * 0.8:
            warnings.append(
                f"Memory requirements ({total_memory_needed}MB) exceed 80% of "
                f"available memory ({available_memory}MB)"
            )
        
        # Check for duplicate scenario names
        names = [s.name for s in self.scenarios]
        duplicates = [name for name in names if names.count(name) > 1]
        if duplicates:
            warnings.append(f"Duplicate scenario names found: {set(duplicates)}")
        
        return warnings
    
    def _get_available_memory_mb(self) -> Optional[int]:
        """Get available system memory in MB."""
        try:
            import psutil
            return psutil.virtual_memory().available // (1024 * 1024)
        except ImportError:
            return None

# Predefined scenario templates
def get_standard_scenarios() -> List[TestScenario]:
    """Get a standard set of test scenarios for debugging."""
    return [
        TestScenario(
            name="recruiter_job_creation",
            test_type=TestType.UI_FLOW,
            test_function="test_job_creation_flow",
            user_type="recruiter",
            locale="he",
            data_set="standard"
        ),
        TestScenario(
            name="candidate_job_search",
            test_type=TestType.UI_FLOW,
            test_function="test_job_search_flow",
            user_type="candidate",
            locale="he",
            data_set="standard"
        ),
        TestScenario(
            name="api_endpoints_validation",
            test_type=TestType.API_TEST,
            test_function="test_api_endpoints",
            data_set="edge_cases",
            timeout=60
        ),
        TestScenario(
            name="database_queries",
            test_type=TestType.DATABASE,
            test_function="test_database_operations",
            data_set="large",
            required_resources={"database_connections": 5}
        )
    ]

def get_auth_scenarios() -> List[TestScenario]:
    """Get authentication-specific test scenarios."""
    return [
        TestScenario(
            name="auth_login_recruiter",
            test_type=TestType.UI_FLOW,
            test_function="test_login_flow",
            user_type="recruiter",
            data_set="standard"
        ),
        TestScenario(
            name="auth_login_candidate",
            test_type=TestType.UI_FLOW,
            test_function="test_login_flow",
            user_type="candidate",
            data_set="standard"
        ),
        TestScenario(
            name="auth_token_validation",
            test_type=TestType.API_TEST,
            test_function="test_token_validation",
            timeout=30
        ),
        TestScenario(
            name="auth_session_timeout",
            test_type=TestType.INTEGRATION,
            test_function="test_session_timeout",
            timeout=180,
            environment_vars={"SESSION_TIMEOUT": "60"}
        )
    ]

def get_performance_scenarios() -> List[TestScenario]:
    """Get performance testing scenarios."""
    return [
        TestScenario(
            name="perf_job_list_loading",
            test_type=TestType.PERFORMANCE,
            test_function="test_job_list_performance",
            data_set="large",
            timeout=300,
            required_resources={"concurrent_users": 10}
        ),
        TestScenario(
            name="perf_search_response",
            test_type=TestType.PERFORMANCE,
            test_function="test_search_performance",
            data_set="large",
            timeout=180
        ),
        TestScenario(
            name="perf_api_throughput",
            test_type=TestType.PERFORMANCE,
            test_function="test_api_throughput",
            timeout=300,
            required_resources={"requests_per_second": 100}
        )
    ]

# Example usage
if __name__ == "__main__":
    # Create configuration
    config = ParallelDebugConfig()
    
    # Add standard scenarios
    config.add_scenarios(get_standard_scenarios())
    
    # Configure resources
    config.resource_config.max_workers = 4
    config.resource_config.memory_limit_per_worker_mb = 512
    
    # Validate
    warnings = config.validate_configuration()
    if warnings:
        print("Configuration warnings:")
        for warning in warnings:
            print(f"    {warning}")
    
    # Allocate ports for workers
    for i, scenario in enumerate(config.scenarios[:config.resource_config.max_workers]):
        worker_id = f"worker_{i}"
        ports = config.allocate_ports(worker_id)
        print(f"Allocated ports {ports} to {worker_id} for scenario '{scenario.name}'")