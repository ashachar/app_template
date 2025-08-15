#!/usr/bin/env python3
"""Simple test to debug persistence."""

import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from debug_helpers.timeline_event import TimelineEventCollector, EventType

def test_persistence():
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Temp dir: {temp_dir}")
        
        # Method 1: Let it create its own structure
        collector1 = TimelineEventCollector("TEST1", base_dir=Path(temp_dir))
        print(f"Collector1 base_dir: {collector1.base_dir}")
        
        collector1.create_event(EventType.SESSION_START, "Test", "Test")
        collector1.save_events()
        
        events_file = collector1.base_dir / 'timeline_events.json' 
        print(f"Events file exists: {events_file.exists()}")
        print(f"Events file: {events_file}")
        
        # Method 2: Specify exact directory
        session_dir = Path(temp_dir) / "sessions" / "TEST2"
        collector2 = TimelineEventCollector("TEST2", base_dir=session_dir)
        print(f"\nCollector2 base_dir: {collector2.base_dir}")
        
        collector2.create_event(EventType.SESSION_START, "Test2", "Test2")
        collector2.save_events()
        
        events_file2 = collector2.base_dir / 'timeline_events.json'
        print(f"Events file2 exists: {events_file2.exists()}")
        print(f"Events file2: {events_file2}")

if __name__ == "__main__":
    test_persistence()