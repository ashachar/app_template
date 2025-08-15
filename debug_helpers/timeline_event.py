#!/usr/bin/env python3
"""
Timeline Event System - Captures and stores debugging events for visualization.

This module provides the foundation for creating visual debug timelines by
capturing events during debugging sessions with timestamps, categories, and metadata.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import hashlib


class EventType(Enum):
    """Types of debugging events."""
    # Session events
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    CHECKPOINT = "checkpoint"
    
    # Error events
    ERROR = "error"
    WARNING = "warning"
    CRITICAL_ERROR = "critical_error"
    
    # Action events
    TEST_RUN = "test_run"
    API_CALL = "api_call"
    DB_QUERY = "db_query"
    FILE_CHANGE = "file_change"
    SERVER_RESTART = "server_restart"
    
    # Discovery events
    FINDING = "finding"
    PATTERN_MATCH = "pattern_match"
    SOLUTION_ATTEMPT = "solution_attempt"
    
    # Flow events
    MODULE_TRANSITION = "module_transition"
    STATE_CHANGE = "state_change"
    USER_ACTION = "user_action"


class EventSeverity(Enum):
    """Severity levels for events."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class TimelineEvent:
    """Represents a single event in the debugging timeline."""
    event_id: str
    timestamp: float  # Unix timestamp for precise ordering
    event_type: EventType
    severity: EventSeverity
    module: str  # Which module/component (ui, api, db, etc.)
    title: str
    description: str
    
    # Optional detailed data
    details: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    
    # Relationships
    parent_event_id: Optional[str] = None
    related_event_ids: List[str] = field(default_factory=list)
    
    # Visual hints
    icon: Optional[str] = None
    color: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    # Duration for events that span time
    duration_ms: Optional[int] = None
    end_timestamp: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['event_type'] = self.event_type.value
        data['severity'] = self.severity.value
        data['formatted_time'] = datetime.fromtimestamp(self.timestamp).isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimelineEvent':
        """Create from dictionary."""
        data = data.copy()
        data['event_type'] = EventType(data['event_type'])
        data['severity'] = EventSeverity(data['severity'])
        data.pop('formatted_time', None)  # Remove formatted time if present
        return cls(**data)


class TimelineEventCollector:
    """Collects and manages timeline events during a debugging session."""
    
    def __init__(self, session_id: str, base_dir: Optional[Path] = None):
        self.session_id = session_id
        self.base_dir = base_dir or Path(__file__).parent / 'sessions' / session_id
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.events: List[TimelineEvent] = []
        self.event_index: Dict[str, TimelineEvent] = {}
        self.module_stacks: Dict[str, List[str]] = {}  # Track module transitions
        
        # Load existing events if resuming session
        self._load_events()
        
        # Auto-save configuration
        self.auto_save = True
        self.save_interval = 10  # Save every 10 events
        self.unsaved_count = 0
    
    def create_event(self, event_type: EventType, title: str, description: str,
                    module: str = "unknown", severity: Optional[EventSeverity] = None,
                    **kwargs) -> TimelineEvent:
        """Create and record a new timeline event."""
        # Auto-determine severity if not provided
        if severity is None:
            severity = self._determine_severity(event_type)
        
        # Generate event ID
        event_id = self._generate_event_id(event_type, title)
        
        # Create event
        event = TimelineEvent(
            event_id=event_id,
            timestamp=time.time(),
            event_type=event_type,
            severity=severity,
            module=module,
            title=title,
            description=description,
            **kwargs
        )
        
        # Set visual properties
        event.icon = self._get_event_icon(event_type)
        event.color = self._get_severity_color(severity)
        
        # Track module transitions
        if event_type == EventType.MODULE_TRANSITION:
            self._track_module_transition(module, event_id)
        
        # Add to collections
        self.events.append(event)
        self.event_index[event_id] = event
        
        # Auto-save if enabled
        self.unsaved_count += 1
        if self.auto_save and self.unsaved_count >= self.save_interval:
            self.save_events()
        
        return event
    
    def start_timed_event(self, event_type: EventType, title: str, 
                         description: str, **kwargs) -> str:
        """Start a timed event that will be completed later."""
        event = self.create_event(event_type, title, description, **kwargs)
        return event.event_id
    
    def end_timed_event(self, event_id: str, success: bool = True, 
                       error_message: Optional[str] = None):
        """End a timed event and calculate duration."""
        if event_id not in self.event_index:
            return
        
        event = self.event_index[event_id]
        event.end_timestamp = time.time()
        event.duration_ms = int((event.end_timestamp - event.timestamp) * 1000)
        
        # Update severity based on outcome
        if not success:
            event.severity = EventSeverity.ERROR
            if error_message:
                event.details['error'] = error_message
        
        self.save_events()
    
    def add_error_event(self, error_message: str, module: str = "unknown",
                       stack_trace: Optional[str] = None, 
                       file_path: Optional[str] = None,
                       line_number: Optional[int] = None,
                       critical: bool = False):
        """Add an error event with full context."""
        event_type = EventType.CRITICAL_ERROR if critical else EventType.ERROR
        severity = EventSeverity.CRITICAL if critical else EventSeverity.ERROR
        
        return self.create_event(
            event_type=event_type,
            title=f"Error in {module}",
            description=error_message,
            module=module,
            severity=severity,
            stack_trace=stack_trace,
            file_path=file_path,
            line_number=line_number,
            tags=['error', module]
        )
    
    def add_finding_event(self, finding_type: str, description: str,
                         evidence: Optional[str] = None,
                         fix_suggestion: Optional[str] = None,
                         module: str = "unknown"):
        """Add a debugging finding event."""
        details = {
            'finding_type': finding_type,
            'evidence': evidence,
            'fix_suggestion': fix_suggestion
        }
        
        severity = EventSeverity.WARNING
        if finding_type == 'root_cause':
            severity = EventSeverity.ERROR
        elif finding_type == 'solution':
            severity = EventSeverity.SUCCESS
        
        return self.create_event(
            event_type=EventType.FINDING,
            title=f"{finding_type.title()} Found",
            description=description,
            module=module,
            severity=severity,
            details=details,
            tags=['finding', finding_type]
        )
    
    def add_test_event(self, test_name: str, passed: bool, 
                      duration_ms: Optional[int] = None,
                      error_message: Optional[str] = None):
        """Add a test execution event."""
        severity = EventSeverity.SUCCESS if passed else EventSeverity.ERROR
        title = f"Test {test_name}"
        description = f"Test {'passed' if passed else 'failed'}"
        
        details = {
            'test_name': test_name,
            'passed': passed
        }
        
        if error_message:
            details['error'] = error_message
            description += f": {error_message}"
        
        return self.create_event(
            event_type=EventType.TEST_RUN,
            title=title,
            description=description,
            module='test',
            severity=severity,
            duration_ms=duration_ms,
            details=details,
            tags=['test', 'passed' if passed else 'failed']
        )
    
    def link_events(self, event_id1: str, event_id2: str):
        """Create a relationship between two events."""
        if event_id1 in self.event_index and event_id2 in self.event_index:
            event1 = self.event_index[event_id1]
            event2 = self.event_index[event_id2]
            
            if event_id2 not in event1.related_event_ids:
                event1.related_event_ids.append(event_id2)
            if event_id1 not in event2.related_event_ids:
                event2.related_event_ids.append(event_id1)
    
    def get_events_by_module(self, module: str) -> List[TimelineEvent]:
        """Get all events for a specific module."""
        return [e for e in self.events if e.module == module]
    
    def get_events_by_type(self, event_type: EventType) -> List[TimelineEvent]:
        """Get all events of a specific type."""
        return [e for e in self.events if e.event_type == event_type]
    
    def get_events_by_severity(self, severity: EventSeverity) -> List[TimelineEvent]:
        """Get all events of a specific severity."""
        return [e for e in self.events if e.severity == severity]
    
    def get_events_in_range(self, start_time: float, end_time: float) -> List[TimelineEvent]:
        """Get events within a time range."""
        return [e for e in self.events 
                if start_time <= e.timestamp <= end_time]
    
    def get_module_flow(self) -> List[Tuple[str, str, float]]:
        """Get the flow of execution between modules."""
        flow = []
        module_events = [e for e in self.events 
                        if e.event_type == EventType.MODULE_TRANSITION]
        
        for i in range(len(module_events) - 1):
            current = module_events[i]
            next_event = module_events[i + 1]
            flow.append((current.module, next_event.module, next_event.timestamp))
        
        return flow
    
    def save_events(self):
        """Save events to disk."""
        events_file = self.base_dir / 'timeline_events.json'
        
        data = {
            'session_id': self.session_id,
            'events': [e.to_dict() for e in self.events],
            'last_saved': datetime.now().isoformat()
        }
        
        with open(events_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.unsaved_count = 0
    
    def _load_events(self):
        """Load events from disk if they exist."""
        events_file = self.base_dir / 'timeline_events.json'
        
        if events_file.exists():
            try:
                with open(events_file, 'r') as f:
                    data = json.load(f)
                
                for event_data in data.get('events', []):
                    event = TimelineEvent.from_dict(event_data)
                    self.events.append(event)
                    self.event_index[event.event_id] = event
            except Exception as e:
                print(f"Warning: Could not load timeline events: {e}")
    
    def _generate_event_id(self, event_type: EventType, title: str) -> str:
        """Generate a unique event ID."""
        timestamp = str(time.time())
        content = f"{event_type.value}:{title}:{timestamp}"
        hash_suffix = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"{event_type.value}_{hash_suffix}"
    
    def _determine_severity(self, event_type: EventType) -> EventSeverity:
        """Auto-determine severity based on event type."""
        severity_map = {
            EventType.ERROR: EventSeverity.ERROR,
            EventType.CRITICAL_ERROR: EventSeverity.CRITICAL,
            EventType.WARNING: EventSeverity.WARNING,
            EventType.SESSION_START: EventSeverity.INFO,
            EventType.SESSION_END: EventSeverity.INFO,
            EventType.CHECKPOINT: EventSeverity.SUCCESS,
            EventType.SOLUTION_ATTEMPT: EventSeverity.INFO,
            EventType.PATTERN_MATCH: EventSeverity.SUCCESS,
        }
        return severity_map.get(event_type, EventSeverity.INFO)
    
    def _get_event_icon(self, event_type: EventType) -> str:
        """Get icon for event type."""
        icon_map = {
            EventType.SESSION_START: "",
            EventType.SESSION_END: "⏹",
            EventType.CHECKPOINT: "",
            EventType.ERROR: "",
            EventType.CRITICAL_ERROR: "",
            EventType.WARNING: "",
            EventType.TEST_RUN: "",
            EventType.API_CALL: "",
            EventType.DB_QUERY: "",
            EventType.FILE_CHANGE: "",
            EventType.SERVER_RESTART: "",
            EventType.FINDING: "",
            EventType.PATTERN_MATCH: "",
            EventType.SOLUTION_ATTEMPT: "",
            EventType.MODULE_TRANSITION: "",
            EventType.STATE_CHANGE: "",
            EventType.USER_ACTION: ""
        }
        return icon_map.get(event_type, "•")
    
    def _get_severity_color(self, severity: EventSeverity) -> str:
        """Get color for severity level."""
        color_map = {
            EventSeverity.INFO: "#6c757d",      # Gray
            EventSeverity.SUCCESS: "#28a745",    # Green
            EventSeverity.WARNING: "#ffc107",    # Yellow
            EventSeverity.ERROR: "#dc3545",      # Red
            EventSeverity.CRITICAL: "#721c24"    # Dark Red
        }
        return color_map.get(severity, "#6c757d")
    
    def _track_module_transition(self, module: str, event_id: str):
        """Track module transitions for flow analysis."""
        if module not in self.module_stacks:
            self.module_stacks[module] = []
        self.module_stacks[module].append(event_id)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the timeline."""
        if not self.events:
            return {
                'total_events': 0,
                'duration_seconds': 0,
                'modules_involved': [],
                'error_count': 0,
                'success_count': 0
            }
        
        start_time = min(e.timestamp for e in self.events)
        end_time = max(e.timestamp for e in self.events)
        
        return {
            'total_events': len(self.events),
            'duration_seconds': end_time - start_time,
            'modules_involved': list(set(e.module for e in self.events)),
            'error_count': len([e for e in self.events 
                               if e.severity in [EventSeverity.ERROR, EventSeverity.CRITICAL]]),
            'success_count': len([e for e in self.events 
                                 if e.severity == EventSeverity.SUCCESS]),
            'event_types': dict(self._count_by_type()),
            'severities': dict(self._count_by_severity())
        }
    
    def _count_by_type(self) -> List[Tuple[str, int]]:
        """Count events by type."""
        from collections import Counter
        type_counts = Counter(e.event_type.value for e in self.events)
        return type_counts.most_common()
    
    def _count_by_severity(self) -> List[Tuple[str, int]]:
        """Count events by severity."""
        from collections import Counter
        severity_counts = Counter(e.severity.value for e in self.events)
        return severity_counts.most_common()