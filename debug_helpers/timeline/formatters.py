"""Timeline Formatting Utilities - Date/time and duration formatting functions."""

from datetime import datetime


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m {int(seconds % 60)}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def format_timestamp(timestamp: float) -> str:
    """Format timestamp for display."""
    return datetime.fromtimestamp(timestamp).strftime('%H:%M:%S.%f')[:-3]


def format_duration_ms(ms: int) -> str:
    """Format milliseconds duration."""
    if ms < 1000:
        return f"{ms}ms"
    return format_duration(ms / 1000)