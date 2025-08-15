"""Timeline visualization package for debug sessions."""

from .styles import generate_css
from .javascript import generate_javascript
from .templates import generate_main_template, generate_empty_timeline
from .formatters import format_duration, format_timestamp, format_duration_ms
from .statistics import calculate_stats, count_event_types, count_severities
from .html_helpers import generate_options, generate_type_options, generate_severity_options
from .data_processor import prepare_timeline_data
from .event_renderer import generate_timeline_events
from .controls import generate_filters, generate_timeline_controls
from .swimlanes import generate_swimlanes
from .details_panel import generate_details_panel, generate_summary_stats, generate_footer
from .demo import generate_demo_timeline

__all__ = [
    'generate_css',
    'generate_javascript',
    'generate_main_template',
    'generate_empty_timeline',
    'format_duration',
    'format_timestamp',
    'format_duration_ms',
    'calculate_stats',
    'count_event_types',
    'count_severities',
    'generate_options',
    'generate_type_options',
    'generate_severity_options',
    'prepare_timeline_data',
    'generate_timeline_events',
    'generate_filters',
    'generate_timeline_controls',
    'generate_swimlanes',
    'generate_details_panel',
    'generate_summary_stats',
    'generate_footer',
    'generate_demo_timeline'
]