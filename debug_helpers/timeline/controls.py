"""Timeline Controls Module - Generate filter and navigation controls."""

import html
from typing import Dict, Any

try:
    from .html_helpers import generate_options, generate_type_options, generate_severity_options
except ImportError:
    from html_helpers import generate_options, generate_type_options, generate_severity_options


def generate_filters(timeline_data: Dict[str, Any]) -> str:
    """Generate filter controls."""
    modules = timeline_data.get('modules', [])
    event_types = timeline_data.get('event_types', {})
    severities = timeline_data.get('severities', {})
    
    return f"""
    <div class="filter-controls">
        <div class="filter-group">
            <label>Module:</label>
            <select id="module-filter" class="filter-select">
                <option value="">All Modules</option>
                {generate_options(modules, 'module')}
            </select>
        </div>
        
        <div class="filter-group">
            <label>Event Type:</label>
            <select id="type-filter" class="filter-select">
                <option value="">All Types</option>
                {generate_type_options(event_types)}
            </select>
        </div>
        
        <div class="filter-group">
            <label>Severity:</label>
            <select id="severity-filter" class="filter-select">
                <option value="">All Severities</option>
                {generate_severity_options(severities)}
            </select>
        </div>
        
        <div class="filter-group">
            <label>Search:</label>
            <input type="text" id="search-filter" class="filter-input" 
                   placeholder="Search events...">
        </div>
        
        <button id="clear-filters" class="btn btn-secondary">Clear Filters</button>
    </div>
    """


def generate_timeline_controls() -> str:
    """Generate timeline navigation controls."""
    return """
    <div class="navigation-controls">
        <button id="zoom-in" class="btn btn-icon" title="Zoom In">+</button>
        <button id="zoom-out" class="btn btn-icon" title="Zoom Out">-</button>
        <button id="zoom-fit" class="btn btn-icon" title="Fit to View">⊡</button>
        <button id="toggle-details" class="btn btn-icon" title="Toggle Details">☰</button>
        <button id="export-timeline" class="btn btn-icon" title="Export">⬇</button>
        <button id="share-timeline" class="btn btn-icon" title="Share">⤴</button>
    </div>
    """