#!/usr/bin/env python3
"""
Performance Analyzer - Analyzes performance metrics across workers.
"""

from collections import defaultdict
from typing import Dict, List, Any, Tuple


class PerformanceAnalyzer:
    """Analyzes performance metrics across workers."""
    
    def analyze_performance(self, worker_results: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], Dict[str, int]]:
        """
        Analyze performance metrics across workers.
        
        Returns:
            Tuple of (performance_metrics, test_data_usage)
        """
        perf_data = defaultdict(list)
        test_data_usage = {}
        
        for worker_result in worker_results:
            metrics = worker_result.get('metrics', {})
            
            # Collect performance metrics
            if 'performance' in metrics:
                for key, value in metrics['performance'].items():
                    if isinstance(value, (int, float)):
                        perf_data[key].append(value)
            
            # Test data usage
            if 'test_data' in metrics:
                for category, items in metrics['test_data'].items():
                    test_data_usage[category] = (
                        test_data_usage.get(category, 0) + len(items)
                    )
            
            # Cache hit rates
            if 'cache_hit_rate' in metrics:
                perf_data['cache_hit_rates'].append(metrics['cache_hit_rate'])
        
        # Calculate performance statistics
        performance_metrics = {}
        for metric, values in perf_data.items():
            if values:
                performance_metrics[metric] = {
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'values': values
                }
        
        return performance_metrics, test_data_usage