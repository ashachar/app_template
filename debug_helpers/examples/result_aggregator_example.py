#!/usr/bin/env python3
"""
Example usage of the Result Aggregator.
"""

from debug_helpers.result_aggregator import ResultAggregator


def main():
    """Example usage of ResultAggregator."""
    # Create aggregator
    aggregator = ResultAggregator("MASTER123")
    
    # Add sample results
    sample_results = [
        {
            'worker_id': 'worker_1',
            'scenario_name': 'test_login',
            'success': True,
            'duration': 5.2,
            'findings': [
                {'type': 'observation', 'description': 'Login flow works correctly'}
            ]
        },
        {
            'worker_id': 'worker_2',
            'scenario_name': 'test_job_creation',
            'success': False,
            'duration': 8.5,
            'error': 'Timeout waiting for element',
            'findings': [
                {'type': 'root_cause', 'description': 'Missing required field validation'}
            ]
        }
    ]
    
    for result in sample_results:
        aggregator.add_result(result)
    
    # Aggregate and print report
    aggregator.aggregate()
    print(aggregator.generate_report())


if __name__ == "__main__":
    main()