"""Timeline Statistics Module - Calculate timeline and event statistics."""

from typing import List, Dict, Any
from collections import defaultdict

try:
    from ..timeline_event import TimelineEvent, EventSeverity
except ImportError:
    from timeline_event import TimelineEvent, EventSeverity


def calculate_stats(events: List[TimelineEvent]) -> Dict[str, Any]:
    """Calculate timeline statistics."""
    if not events:
        return {
            'duration': 0,
            'total_events': 0,
            'error_count': 0,
            'warning_count': 0,
            'success_count': 0
        }
        
    start_time = min(e.timestamp for e in events)
    end_time = max(e.timestamp for e in events)
    
    severity_counts = defaultdict(int)
    for event in events:
        severity_counts[event.severity] += 1
        
    return {
        'duration': end_time - start_time,
        'total_events': len(events),
        'error_count': severity_counts.get(EventSeverity.ERROR, 0) + severity_counts.get(EventSeverity.CRITICAL, 0),
        'warning_count': severity_counts.get(EventSeverity.WARNING, 0),
        'success_count': severity_counts.get(EventSeverity.SUCCESS, 0)
    }


def count_event_types(events: List[TimelineEvent]) -> Dict[str, int]:
    """Count events by type."""
    type_counts = defaultdict(int)
    for event in events:
        type_counts[event.event_type.value] += 1
    return dict(type_counts)


def count_severities(events: List[TimelineEvent]) -> Dict[str, int]:
    """Count events by severity."""
    severity_counts = defaultdict(int)
    for event in events:
        severity_counts[event.severity.value] += 1
    return dict(severity_counts)