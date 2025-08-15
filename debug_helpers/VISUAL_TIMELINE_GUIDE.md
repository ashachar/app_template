# 🎯 Visual Debug Timeline Guide

The Visual Debug Timeline provides an interactive, real-time visualization of your debugging sessions, making it easier to understand complex issues by seeing the flow of events, errors, and solutions over time.

## 📚 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Core Components](#core-components)
4. [Using the Timeline](#using-the-timeline)
5. [Integration with Debug Workflow](#integration-with-debug-workflow)
6. [Interactive Features](#interactive-features)
7. [Best Practices](#best-practices)
8. [Examples](#examples)

## Overview

The Visual Debug Timeline transforms debugging from a text-based log analysis to an interactive visual experience:

- 📊 **Timeline Visualization**: See all debugging events on a chronological timeline
- 🏊 **Swimlanes**: Events organized by module (UI, API, Database, etc.)
- 🔍 **Interactive Exploration**: Zoom, filter, and click for details
- 🎯 **Pattern Recognition**: Visual indicators for known patterns and solutions
- 📈 **Performance Insights**: See timing and duration of operations
- 🔗 **Event Relationships**: Understand cause-and-effect relationships

## Quick Start

### 1. Basic Timeline Usage

```python
from debug_helpers.timeline_integration import TimelineDebugger

# Start a debugging session
debugger = TimelineDebugger('DEBUG-123', 'API Authentication Issue')

# Your debugging activities are automatically tracked
results = debugger.analyze_logs()

# Add findings
debugger.add_finding(
    'root_cause',
    'JWT token expiration not handled',
    evidence='Token expired 2 hours ago',
    fix_suggestion='Implement token refresh'
)

# Run tests
debugger.run_test('test_auth_refresh', test_function)

# Generate timeline
timeline_file = debugger.end_session(
    resolution="Added token refresh logic",
    success=True
)

print(f"Timeline available at: {timeline_file}")
```

### 2. Manual Event Tracking

```python
from debug_helpers.timeline_event import TimelineEventCollector

# Create collector
timeline = TimelineEventCollector('MANUAL-DEBUG')

# Track an operation
event_id = timeline.start_timed_event(
    EventType.API_CALL,
    "POST /api/login",
    "Testing authentication"
)

# ... do work ...

timeline.end_timed_event(event_id, success=True)

# Add error
timeline.add_error_event(
    "Authentication failed",
    module="auth",
    stack_trace="...",
    critical=False
)
```

## Core Components

### TimelineEvent
The basic unit of the timeline - represents a single debugging event.

```python
@dataclass
class TimelineEvent:
    event_id: str              # Unique identifier
    timestamp: float           # When it occurred
    event_type: EventType      # Category of event
    severity: EventSeverity    # Impact level
    module: str               # Which system component
    title: str                # Short description
    description: str          # Detailed information
    duration_ms: Optional[int] # For timed operations
    # ... additional fields
```

### Event Types

- **Session Events**: `SESSION_START`, `SESSION_END`, `CHECKPOINT`
- **Error Events**: `ERROR`, `WARNING`, `CRITICAL_ERROR`
- **Action Events**: `TEST_RUN`, `API_CALL`, `DB_QUERY`, `FILE_CHANGE`
- **Discovery Events**: `FINDING`, `PATTERN_MATCH`, `SOLUTION_ATTEMPT`
- **Flow Events**: `MODULE_TRANSITION`, `STATE_CHANGE`, `USER_ACTION`

### Severity Levels

- 🔵 **INFO**: Normal operations
- ✅ **SUCCESS**: Successful operations
- ⚠️ **WARNING**: Potential issues
- ❌ **ERROR**: Failures
- 🚨 **CRITICAL**: Severe failures

## Using the Timeline

### Starting a Session

```python
# Integrated approach (recommended)
debugger = TimelineDebugger(
    session_id='ISSUE-789',
    issue_type='Performance Degradation'
)

# Manual approach
timeline = TimelineEventCollector('DEBUG-SESSION')
timeline.create_event(
    EventType.SESSION_START,
    "Investigation Started",
    "Looking into slow API responses"
)
```

### Tracking Operations

```python
# Track any debugging operation
op_id = debugger.start_operation(
    "Database Query Analysis",
    "Checking slow queries",
    module="database"
)

# ... perform analysis ...

debugger.end_operation(
    "Database Query Analysis",
    success=True
)
```

### Recording Findings

```python
# Add findings with automatic timeline tracking
debugger.add_finding(
    'observation',
    'N+1 query pattern detected',
    evidence='100+ queries for single request',
    fix_suggestion='Use eager loading',
    module='database'
)
```

### API and Test Tracking

```python
# Track API calls
debugger.api_call(
    'GET', '/api/users',
    success=False,
    response_time_ms=5234,
    error='Timeout after 5s'
)

# Track test execution
debugger.run_test('test_query_optimization')
```

## Integration with Debug Workflow

### With Log Analysis

```python
# Logs are automatically added to timeline
results = debugger.analyze_logs()

# Critical findings become error events
# Pattern matches become pattern events
# Timeline shows when logs were analyzed
```

### With Pattern Database

```python
# Pattern matches appear on timeline
debugger.add_finding(
    'error',
    'Database connection timeout'
)

# If patterns match, timeline shows:
# - Pattern match event
# - Confidence level
# - Available solutions
```

### With Session State

```python
# Checkpoints appear on timeline
debugger.checkpoint(
    "Pre-optimization",
    "Before applying query fixes"
)

# State changes are tracked
# Module transitions visible
```

## Interactive Features

### Timeline Navigation

- **🔍+ Zoom In**: See more detail
- **🔍- Zoom Out**: See broader context
- **⛶ Fit to View**: Reset zoom
- **📋 Toggle Details**: Show/hide details panel
- **💾 Export**: Save timeline data
- **🔗 Share**: Generate shareable link

### Filtering

- **Module Filter**: Show only specific modules
- **Event Type Filter**: Focus on errors, tests, etc.
- **Severity Filter**: Show only critical events
- **Search**: Find events by text

### Event Details

Click any event to see:
- Full description
- Stack traces
- File locations
- Related events
- Timing information
- Additional metadata

### Visual Indicators

- **Duration bars**: Show how long operations took
- **Color coding**: Severity indicated by color
- **Icons**: Quick visual event type recognition
- **Swimlanes**: Module organization
- **Tooltips**: Hover for quick info

## Best Practices

### 1. Use Descriptive Titles

```python
# ❌ Poor
timeline.create_event(EventType.ERROR, "Error", "Failed")

# ✅ Good
timeline.create_event(
    EventType.ERROR,
    "Auth Middleware Timeout",
    "JWT validation took 5.2s, exceeded 5s limit"
)
```

### 2. Track Key Operations

```python
# Always track operations that might fail
op_id = debugger.start_operation("Complex Analysis")
try:
    # ... do work ...
    debugger.end_operation("Complex Analysis", success=True)
except Exception as e:
    debugger.end_operation("Complex Analysis", 
                          success=False, 
                          error_message=str(e))
```

### 3. Link Related Events

```python
# Create relationships between events
error_event = timeline.add_error_event("API failed")
fix_event = timeline.create_event(
    EventType.SOLUTION_ATTEMPT,
    "Retry with backoff"
)
timeline.link_events(error_event.event_id, fix_event.event_id)
```

### 4. Use Checkpoints

```python
# Mark important milestones
debugger.checkpoint("Root Cause Identified")
debugger.checkpoint("Fix Applied")
debugger.checkpoint("Tests Passing")
```

### 5. Provide Context

```python
# Add relevant context to events
timeline.create_event(
    EventType.ERROR,
    "Query Timeout",
    "User listing query exceeded 30s limit",
    module="database",
    details={
        'query': 'SELECT * FROM users WHERE...',
        'table_size': '2.5M rows',
        'missing_index': 'user_status'
    }
)
```

## Examples

### Example 1: API Debugging Session

```python
# Start session
debugger = TimelineDebugger('API-DEBUG-001', 'Login Endpoint 500 Error')

# Analyze logs
log_results = debugger.analyze_logs()
# Timeline shows: Log analysis event with findings

# Test the endpoint
debugger.api_call('POST', '/api/login', 
                 success=False, 
                 error='500 Internal Server Error')

# Check database
debugger.module_transition('api', 'database', 
                          'Checking user table access')

db_op = debugger.start_operation("Query User Table")
# ... check database ...
debugger.end_operation("Query User Table", success=True)

# Found issue
debugger.add_finding(
    'root_cause',
    'Database connection pool exhausted',
    evidence='0 available connections',
    fix_suggestion='Increase pool size or fix connection leak'
)

# Apply fix
debugger.file_change(
    'config/database.yml',
    'Modified',
    'Increased connection pool from 5 to 20'
)

# Verify fix
debugger.api_call('POST', '/api/login', success=True)

# Complete
timeline_file = debugger.end_session(
    "Fixed connection pool exhaustion",
    success=True
)
```

### Example 2: Performance Investigation

```python
debugger = TimelineDebugger('PERF-001', 'Slow Page Load')

# Track page load
load_event = debugger.start_operation(
    "Page Load", 
    "Loading /dashboard",
    module="ui"
)
time.sleep(3.5)  # Simulate slow load
debugger.end_operation("Page Load", success=True)

# Break down components
debugger.add_finding(
    'observation',
    'API calls taking 2.5s of 3.5s total',
    evidence='Network tab shows multiple sequential calls'
)

# Test parallel loading
test_event = debugger.start_operation("Parallel API Test")
# ... test implementation ...
debugger.end_operation("Parallel API Test", success=True)

debugger.add_finding(
    'solution',
    'Parallelize API calls',
    evidence='Reduces load time from 3.5s to 1.2s'
)
```

## HTML Timeline Features

The generated HTML timeline includes:

### Header Section
- Session ID and issue type
- Total duration
- Event counts by severity
- Summary statistics

### Timeline View
- Horizontal timeline with events
- Module swimlanes
- Zoom and pan controls
- Event markers with severity colors

### Filters Panel
- Module selector
- Event type filter
- Severity filter
- Text search

### Details Panel
- Click event for full details
- Stack traces
- Related events
- Timestamps and durations

### Export Options
- JSON export of all data
- Shareable links
- PNG screenshot (browser feature)

## Troubleshooting

### Timeline Not Showing Events

1. Check events are being created:
   ```python
   print(f"Event count: {len(debugger.timeline.events)}")
   ```

2. Ensure session is ended:
   ```python
   timeline_file = debugger.end_session()
   ```

3. Verify file path:
   ```python
   print(f"Timeline at: {timeline_file.absolute()}")
   ```

### Performance Issues

For sessions with many events:
- Use filtering to focus on relevant events
- Zoom in to specific time ranges
- Export and analyze data programmatically

### Missing Relationships

Ensure events are properly linked:
```python
# Link cause and effect
timeline.link_events(error_id, solution_id)
```

## Advanced Usage

### Custom Event Types

```python
# Add domain-specific details
timeline.create_event(
    EventType.USER_ACTION,
    "Custom Analysis",
    "Running specialized checks",
    details={
        'custom_metric': 42,
        'special_flag': True,
        'related_ids': [1, 2, 3]
    }
)
```

### Batch Operations

```python
# Track multiple related operations
with debugger.batch_operation("Bulk Update"):
    for item in items:
        debugger.process_item(item)
```

### Timeline Merging

```python
# Combine multiple debugging sessions
timeline1 = TimelineEventCollector('SESSION-1')
timeline2 = TimelineEventCollector('SESSION-2')

# Merge events
all_events = timeline1.events + timeline2.events
all_events.sort(key=lambda e: e.timestamp)

# Generate combined timeline
generator = TimelineHTMLGenerator("Combined Debug Sessions")
generator.generate_timeline(all_events)
```

## Summary

The Visual Debug Timeline transforms debugging by:
- **Visualizing** the debugging process
- **Tracking** all operations and findings
- **Connecting** related events
- **Identifying** patterns visually
- **Sharing** debugging insights

Use it to make your debugging sessions more efficient, understandable, and shareable!