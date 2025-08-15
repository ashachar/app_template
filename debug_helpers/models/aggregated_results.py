#!/usr/bin/env python3
"""
Aggregated Results Model - Container for aggregated results from parallel execution.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Tuple


@dataclass
class AggregatedResults:
    """Container for aggregated results from parallel execution."""
    
    total_scenarios: int = 0
    successful_scenarios: int = 0
    failed_scenarios: int = 0
    success_rate: float = 0.0
    
    total_duration: float = 0.0
    average_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    
    common_errors: List[Tuple[str, int]] = field(default_factory=list)
    error_patterns: Dict[str, List[str]] = field(default_factory=dict)
    
    common_findings: Dict[str, List[Dict]] = field(default_factory=dict)
    root_causes: List[Dict] = field(default_factory=list)
    
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    test_data_usage: Dict[str, int] = field(default_factory=dict)
    
    scenario_results: Dict[str, Dict] = field(default_factory=dict)
    timeline: List[Dict] = field(default_factory=list)
    
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'summary': {
                'total_scenarios': self.total_scenarios,
                'successful_scenarios': self.successful_scenarios,
                'failed_scenarios': self.failed_scenarios,
                'success_rate': self.success_rate,
                'total_duration': self.total_duration,
                'average_duration': self.average_duration,
                'min_duration': self.min_duration,
                'max_duration': self.max_duration
            },
            'errors': {
                'common_errors': self.common_errors,
                'error_patterns': self.error_patterns
            },
            'findings': {
                'common_findings': self.common_findings,
                'root_causes': self.root_causes
            },
            'metrics': {
                'performance': self.performance_metrics,
                'test_data_usage': self.test_data_usage
            },
            'scenario_results': self.scenario_results,
            'timeline': self.timeline,
            'recommendations': self.recommendations
        }