#!/usr/bin/env python3
"""
Timeline Builder - Builds a timeline of events across all workers.
"""

from typing import Dict, List, Any


class TimelineBuilder:
    """Builds a timeline of events across all workers."""
    
    def build_timeline(self, worker_results: List[Dict[str, Any]]) -> List[Dict]:
        """
        Build a timeline of events across all workers.
        
        Returns:
            List of timeline events sorted by timestamp
        """
        events = []
        
        for worker_result in worker_results:
            # Add start event
            if worker_result.get('start_time'):
                events.append({
                    'timestamp': worker_result['start_time'],
                    'event': 'start',
                    'scenario': worker_result['scenario_name'],
                    'worker_id': worker_result['worker_id']
                })
            
            # Add end event
            if worker_result.get('end_time'):
                events.append({
                    'timestamp': worker_result['end_time'],
                    'event': 'end',
                    'scenario': worker_result['scenario_name'],
                    'worker_id': worker_result['worker_id'],
                    'success': worker_result['success']
                })
            
            # Add checkpoint events
            for checkpoint in worker_result.get('checkpoints', []):
                events.append({
                    'timestamp': worker_result['start_time'],  # Approximate
                    'event': 'checkpoint',
                    'checkpoint': checkpoint,
                    'scenario': worker_result['scenario_name'],
                    'worker_id': worker_result['worker_id']
                })
        
        # Sort by timestamp
        events.sort(key=lambda x: x['timestamp'])
        return events