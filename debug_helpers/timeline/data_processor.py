"""Timeline Data Processor - Process timeline events into visualization data."""

from typing import List, Dict, Any
from collections import defaultdict

try:
    from ..timeline_event import TimelineEvent
    from .statistics import count_event_types, count_severities
except ImportError:
    from timeline_event import TimelineEvent
    from statistics import count_event_types, count_severities


def prepare_timeline_data(events: List[TimelineEvent]) -> Dict[str, Any]:
    """Prepare timeline data structure for visualization."""
    if not events:
        return {}
        
    # Calculate timeline bounds
    start_time = min(e.timestamp for e in events)
    end_time = max(e.timestamp for e in events)
    duration = end_time - start_time
    
    # Group events by module (swimlanes)
    modules = defaultdict(list)
    for event in events:
        modules[event.module].append(event)
        
    # Calculate event positions
    positions = {}
    for event in events:
        # Normalize timestamp to 0-100% range
        relative_time = (event.timestamp - start_time) / duration if duration > 0 else 0
        positions[event.event_id] = {
            'x_percent': relative_time * 100,
            'timestamp': event.timestamp,
            'duration_ms': event.duration_ms
        }
        
    # Build module lanes
    module_lanes = []
    for i, (module, module_events) in enumerate(sorted(modules.items())):
        module_lanes.append({
            'module': module,
            'lane_index': i,
            'event_count': len(module_events),
            'events': [e.event_id for e in module_events]
        })
        
    return {
        'start_time': start_time,
        'end_time': end_time,
        'duration': duration,
        'positions': positions,
        'modules': module_lanes,
        'total_events': len(events),
        'event_types': count_event_types(events),
        'severities': count_severities(events)
    }