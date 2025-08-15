"""Timeline Details Panel Module - Generate event details panel."""

import html
from datetime import datetime
from typing import Optional, Dict, Any, List

try:
    from ..timeline_event import TimelineEvent
    from .formatters import format_duration
except ImportError:
    from timeline_event import TimelineEvent
    from formatters import format_duration


def generate_details_panel() -> str:
    """Generate event details panel template."""
    return """
    <div class="details-header">
        <h3>Event Details</h3>
        <button id="close-details" class="btn-close">×</button>
    </div>
    <div class="details-content" id="details-content">
        <p class="details-placeholder">Click on an event to view details</p>
    </div>
    """


def generate_summary_stats(events: List[TimelineEvent], 
                          metadata: Optional[Dict[str, Any]]) -> str:
    """Generate summary statistics section."""
    if not events:
        return '<div class="summary-stats">No events recorded</div>'
        
    stats = _calculate_display_stats(events)
    session_info = metadata or {}
    
    return f"""
    <div class="summary-stats">
        <div class="stat-item">
            <span class="stat-label">Session ID:</span>
            <span class="stat-value">{html.escape(session_info.get('session_id', 'Unknown'))}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Duration:</span>
            <span class="stat-value">{format_duration(stats['duration'])}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Total Events:</span>
            <span class="stat-value">{stats['total_events']}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Errors:</span>
            <span class="stat-value error-count">{stats['error_count']}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Warnings:</span>
            <span class="stat-value warning-count">{stats['warning_count']}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Success:</span>
            <span class="stat-value success-count">{stats['success_count']}</span>
        </div>
    </div>
    """


def generate_footer(metadata: Optional[Dict[str, Any]]) -> str:
    """Generate footer with metadata."""
    meta = metadata or {}
    generated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return f"""
    <div class="footer-info">
        <span>Generated: {generated_at}</span>
        {f'<span>Issue: {html.escape(meta.get("issue_type", ""))}</span>' if meta.get("issue_type") else ''}
        <span>Timeline v1.0</span>
    </div>
    """


def _calculate_display_stats(events: List[TimelineEvent]) -> Dict[str, Any]:
    """Calculate display statistics (internal helper)."""
    from collections import defaultdict
    
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
        severity_counts[event.severity.value] += 1
        
    return {
        'duration': end_time - start_time,
        'total_events': len(events),
        'error_count': severity_counts.get('error', 0) + severity_counts.get('critical', 0),
        'warning_count': severity_counts.get('warning', 0),
        'success_count': severity_counts.get('success', 0)
    }