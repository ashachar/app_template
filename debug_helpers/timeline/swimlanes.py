"""Timeline Swimlanes Module - Generate module swimlanes for timeline."""

import html
from typing import Dict, Any


def generate_swimlanes(timeline_data: Dict[str, Any]) -> str:
    """Generate module swimlanes."""
    modules = timeline_data.get('modules', [])
    
    swimlanes_html = []
    for lane in modules:
        swimlanes_html.append(f"""
        <div class="swimlane" data-module="{html.escape(lane['module'])}">
            <div class="swimlane-header">
                <span class="module-name">{html.escape(lane['module'])}</span>
                <span class="event-count">{lane['event_count']} events</span>
            </div>
        </div>
        """)
        
    return '\n'.join(swimlanes_html)