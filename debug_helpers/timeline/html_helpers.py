"""Timeline HTML Helpers - Helper functions for generating HTML elements."""

import html
from typing import List, Dict, Any


def generate_options(items: List[Dict], key: str) -> str:
    """Generate HTML options from items."""
    options = []
    for item in items:
        value = html.escape(str(item.get(key, '')))
        options.append(f'<option value="{value}">{value}</option>')
    return '\n'.join(options)


def generate_type_options(type_counts: Dict[str, int]) -> str:
    """Generate event type options."""
    options = []
    for event_type, count in sorted(type_counts.items()):
        options.append(f'<option value="{event_type}">{event_type} ({count})</option>')
    return '\n'.join(options)


def generate_severity_options(severity_counts: Dict[str, int]) -> str:
    """Generate severity options."""
    options = []
    severity_order = ['critical', 'error', 'warning', 'success', 'info']
    for severity in severity_order:
        if severity in severity_counts:
            count = severity_counts[severity]
            options.append(f'<option value="{severity}">{severity.title()} ({count})</option>')
    return '\n'.join(options)