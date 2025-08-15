"""Timeline HTML Templates Module - Contains HTML template generation functions."""

import html
import json
from typing import Dict, Any, Optional


def generate_main_template(title: str, css_styles: str, js_scripts: str,
                          summary_stats: str, filters: str, controls: str,
                          swimlanes: str, events: str, details_panel: str,
                          footer: str, timeline_data: Dict[str, Any],
                          events_data: list) -> str:
    """Generate the main HTML template."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)}</title>
    {css_styles}
</head>
<body>
    <div id="timeline-app">
        <header class="timeline-header">
            <h1>{html.escape(title)}</h1>
            {summary_stats}
        </header>
        
        <div class="timeline-controls">
            {filters}
            {controls}
        </div>
        
        <div class="timeline-container">
            <div class="timeline-swimlanes">
                {swimlanes}
            </div>
            <div class="timeline-events" id="timeline-events">
                {events}
            </div>
        </div>
        
        <div class="event-details-panel" id="event-details-panel">
            {details_panel}
        </div>
        
        <footer class="timeline-footer">
            {footer}
        </footer>
    </div>
    
    <script>
        const timelineData = {json.dumps(timeline_data, indent=2)};
        const eventsData = {json.dumps(events_data, indent=2)};
    </script>
    {js_scripts}
</body>
</html>"""


def generate_empty_timeline() -> str:
    """Generate empty timeline placeholder."""
    return """<!DOCTYPE html>
<html>
<head>
    <title>Empty Timeline</title>
    <style>
        body { font-family: sans-serif; text-align: center; padding: 50px; }
        .empty-state { color: #666; }
    </style>
</head>
<body>
    <div class="empty-state">
        <h2>No Timeline Events</h2>
        <p>No events were recorded in this debugging session.</p>
    </div>
</body>
</html>"""