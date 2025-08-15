#!/usr/bin/env python3
"""
Timeline HTML Generator - Creates interactive HTML visualizations from timeline events.

This module orchestrates the generation of rich, interactive HTML timeline visualizations
by coordinating various specialized modules for styles, scripts, data processing, and rendering.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from .timeline_event import TimelineEvent
    from .timeline import (
        generate_css,
        generate_javascript,
        generate_main_template,
        generate_empty_timeline,
        prepare_timeline_data,
        generate_summary_stats,
        generate_filters,
        generate_timeline_controls,
        generate_swimlanes,
        generate_timeline_events,
        generate_details_panel,
        generate_footer
    )
except ImportError:
    from timeline_event import TimelineEvent
    from timeline import (
        generate_css,
        generate_javascript,
        generate_main_template,
        generate_empty_timeline,
        prepare_timeline_data,
        generate_summary_stats,
        generate_filters,
        generate_timeline_controls,
        generate_swimlanes,
        generate_timeline_events,
        generate_details_panel,
        generate_footer
    )


class TimelineHTMLGenerator:
    """Generates interactive HTML timeline visualizations from debugging events."""
    
    def __init__(self, title: str = "Debug Timeline Visualization"):
        self.title = title
        self.css_styles = generate_css()
        self.js_scripts = generate_javascript()
        
    def generate_timeline(self, events: List[TimelineEvent], 
                         output_file: Optional[Path] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> str:
        """Generate complete HTML timeline visualization."""
        if not events:
            return generate_empty_timeline()
            
        # Prepare timeline data
        timeline_data = prepare_timeline_data(events)
        
        # Generate HTML components
        html_content = generate_main_template(
            title=self.title,
            css_styles=self.css_styles,
            js_scripts=self.js_scripts,
            summary_stats=generate_summary_stats(events, metadata),
            filters=generate_filters(timeline_data),
            controls=generate_timeline_controls(),
            swimlanes=generate_swimlanes(timeline_data),
            events=generate_timeline_events(events, timeline_data),
            details_panel=generate_details_panel(),
            footer=generate_footer(metadata),
            timeline_data=timeline_data,
            events_data=[e.to_dict() for e in events]
        )
        
        # Save to file if specified
        if output_file:
            output_file = Path(output_file)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
        return html_content


# For backward compatibility and direct script execution
if __name__ == "__main__":
    from timeline.demo import generate_demo_timeline
    
    # Generate demo timeline
    demo_file = generate_demo_timeline()
    print(f"\nOpen the timeline in your browser:")
    print(f"  file://{demo_file.absolute()}")