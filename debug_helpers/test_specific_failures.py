#!/usr/bin/env python3
"""Debug specific test failures."""

import sys
import time
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from debug_helpers.timeline_event import TimelineEventCollector, EventType
from debug_helpers.timeline_integration import TimelineDebugger

def test_event_persistence_debug():
    """Debug event persistence test."""
    print("\n=== Testing Event Persistence ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Temp dir: {temp_dir}")
        
        # Create collector
        collector = TimelineEventCollector(
            session_id="TEST-SESSION",
            base_dir=Path(temp_dir)
        )
        
        # Create events
        collector.create_event(EventType.SESSION_START, "Start", "Test")
        collector.create_event(EventType.ERROR, "Error", "Test error")
        print(f"Created {len(collector.events)} events")
        
        # Save events
        collector.save_events()
        
        # Check saved file
        events_file = Path(temp_dir) / 'sessions' / 'TEST-SESSION' / 'timeline_events.json'
        print(f"Events file exists: {events_file.exists()}")
        print(f"Events file path: {events_file}")
        
        # Create new collector
        new_collector = TimelineEventCollector(
            session_id="TEST-SESSION",
            base_dir=Path(temp_dir)
        )
        
        print(f"Loaded {len(new_collector.events)} events")
        if new_collector.events:
            print(f"First event: {new_collector.events[0].title}")
            print(f"Second event: {new_collector.events[1].title if len(new_collector.events) > 1 else 'N/A'}")
        
        # Test assertions
        try:
            assert len(new_collector.events) == 2
            assert new_collector.events[0].title == "Start"
            assert new_collector.events[1].title == "Error"
            print(" Event persistence test PASSED")
            return True
        except AssertionError as e:
            print(f" Event persistence test FAILED: {e}")
            return False

def test_test_execution_tracking_debug():
    """Debug test execution tracking."""
    print("\n=== Testing Test Execution Tracking ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        debugger = TimelineDebugger(
            session_id="TEST-EXEC",
            issue_type="Test Tracking"
        )
        debugger.base_dir = Path(temp_dir)
        debugger.timeline.base_dir = Path(temp_dir)
        
        print(f"Initial events: {len(debugger.timeline.events)}")
        
        # Run successful test
        result1 = debugger.run_test(
            "test_success",
            test_function=lambda: True
        )
        print(f"Test 1 result: {result1}")
        
        # Run failed test
        result2 = debugger.run_test(
            "test_failure",
            test_function=lambda: False
        )
        print(f"Test 2 result: {result2}")
        
        # Check timeline events
        all_events = debugger.timeline.events
        print(f"Total events: {len(all_events)}")
        
        test_events = [e for e in all_events if e.event_type == EventType.TEST_RUN]
        print(f"Test events: {len(test_events)}")
        
        for i, event in enumerate(test_events):
            print(f"  Event {i+1}: {event.title}, passed={event.details.get('passed')}")
        
        # Check success/failure
        success_events = [e for e in test_events if e.details.get('passed')]
        failed_events = [e for e in test_events if not e.details.get('passed')]
        
        print(f"Success events: {len(success_events)}")
        print(f"Failed events: {len(failed_events)}")
        
        # Test assertions
        try:
            assert result1 is True
            assert result2 is False
            assert len(test_events) == 2
            assert len(success_events) == 1
            assert len(failed_events) == 1
            print(" Test execution tracking PASSED")
            return True
        except AssertionError as e:
            print(f" Test execution tracking FAILED: {e}")
            return False

def test_performance_debug():
    """Debug performance test."""
    print("\n=== Testing Performance ===")
    
    collector = TimelineEventCollector("PERF-TEST")
    
    # Create events
    start_time = time.time()
    for i in range(1000):
        collector.create_event(
            EventType.USER_ACTION,
            f"Event {i}",
            f"Description {i}",
            module=f"module{i % 10}"
        )
    creation_time = time.time() - start_time
    print(f"Created 1000 events in {creation_time:.3f}s")
    
    # Test filtering
    start_time = time.time()
    filtered = collector.get_events_by_module("module5")
    filter_time = time.time() - start_time
    print(f"Filtered {len(filtered)} events in {filter_time:.3f}s")
    
    # Test HTML generation
    from debug_helpers.timeline_generator import TimelineHTMLGenerator
    generator = TimelineHTMLGenerator()
    start_time = time.time()
    html = generator.generate_timeline(collector.events)
    generation_time = time.time() - start_time
    print(f"Generated HTML ({len(html)} chars) in {generation_time:.3f}s")
    
    # More lenient performance thresholds
    try:
        assert creation_time < 10.0  # 10 seconds for 1000 events
        assert filter_time < 1.0     # 1 second for filtering
        assert generation_time < 10.0 # 10 seconds for HTML
        print(" Performance test PASSED")
        return True
    except AssertionError as e:
        print(f" Performance test FAILED: {e}")
        return False

if __name__ == "__main__":
    results = []
    
    results.append(test_event_persistence_debug())
    results.append(test_test_execution_tracking_debug())
    results.append(test_performance_debug())
    
    print("\n=== SUMMARY ===")
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print(" All tests PASSED!")
    else:
        print(" Some tests FAILED")