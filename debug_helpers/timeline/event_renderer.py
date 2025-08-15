"""Timeline Event Renderer - Render timeline events as HTML."""

import html
from typing import List, Dict, Any

try:
    from ..timeline_event import TimelineEvent
    from .formatters import format_timestamp
except ImportError:
    from timeline_event import TimelineEvent
    from formatters import format_timestamp


def generate_timeline_events(events: List[TimelineEvent], 
                           timeline_data: Dict[str, Any]) -> str:
    """Generate timeline event markers."""
    positions = timeline_data.get('positions', {})
    modules = {m['module']: m['lane_index'] for m in timeline_data.get('modules', [])}
    
    events_html = []
    for event in events:
        pos = positions.get(event.event_id, {})
        lane_index = modules.get(event.module, 0)
        
        # Calculate visual properties
        x_pos = pos.get('x_percent', 0)
        y_pos = 50 + (lane_index * 80)  # 80px per lane
        
        # Event classes based on type and severity
        event_classes = [
            'timeline-event',
            f'event-type-{event.event_type.value}',
            f'severity-{event.severity.value}'
        ]
        
        # Add duration indicator if event has duration
        width = 4  # Default point width
        if event.duration_ms and event.duration_ms > 0:
            # Calculate width based on duration (max 20% of timeline)
            duration_percent = (event.duration_ms / 1000) / timeline_data['duration'] * 100
            width = min(duration_percent, 20)
            event_classes.append('has-duration')
            
        events_html.append(f"""
        <div class="{' '.join(event_classes)}" 
             id="event-{event.event_id}"
             data-event-id="{event.event_id}"
             data-module="{html.escape(event.module)}"
             data-type="{event.event_type.value}"
             data-severity="{event.severity.value}"
             style="left: {x_pos}%; top: {y_pos}px; width: {width}%;"
             title="{html.escape(event.title)}">
            <span class="event-icon">{event.icon or '•'}</span>
            <div class="event-tooltip">
                <div class="tooltip-header">{html.escape(event.title)}</div>
                <div class="tooltip-time">{format_timestamp(event.timestamp)}</div>
                <div class="tooltip-description">{html.escape(event.description[:100])}...</div>
            </div>
        </div>
        """)
        
    return '\n'.join(events_html)