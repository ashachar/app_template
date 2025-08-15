"""Timeline Demo Generator - Generate demo timeline for testing."""

import time
from pathlib import Path

try:
    from ..timeline_event import TimelineEventCollector, EventType, EventSeverity
    from ..timeline_generator import TimelineHTMLGenerator
except ImportError:
    from timeline_event import TimelineEventCollector, EventType, EventSeverity
    from timeline_generator import TimelineHTMLGenerator


def generate_demo_timeline():
    """Generate a demo timeline for testing."""
    # Create collector
    collector = TimelineEventCollector('DEMO-TIMELINE')
    
    # Simulate a debugging session
    start_time = time.time()
    
    # Session start
    collector.create_event(
        EventType.SESSION_START,
        "Debug Session Started",
        "Starting investigation of API authentication issue",
        module="main"
    )
    
    # API call with error
    time.sleep(0.1)
    api_event_id = collector.start_timed_event(
        EventType.API_CALL,
        "POST /api/jobs",
        "Creating new job listing",
        module="api"
    )
    
    time.sleep(0.2)
    collector.end_timed_event(api_event_id, success=False, error_message="401 Unauthorized")
    
    # Error event
    collector.add_error_event(
        "Authentication failed: Invalid token",
        module="auth",
        stack_trace="at checkAuth (auth.js:45)\\nat middleware (server.js:123)",
        file_path="src/middleware/auth.js",
        line_number=45
    )
    
    # Finding
    time.sleep(0.1)
    collector.add_finding_event(
        "root_cause",
        "Token expiration not handled properly",
        evidence="Token expired 2 hours ago but no refresh attempted",
        fix_suggestion="Implement token refresh logic",
        module="auth"
    )
    
    # Test runs
    time.sleep(0.1)
    collector.add_test_event("test_token_refresh", passed=False, duration_ms=1523,
                           error_message="RefreshToken is not defined")
    
    time.sleep(0.2)
    collector.add_test_event("test_token_refresh", passed=True, duration_ms=892)
    
    # Success
    time.sleep(0.1)
    collector.create_event(
        EventType.SOLUTION_ATTEMPT,
        "Fix Applied",
        "Added token refresh logic to auth middleware",
        module="auth",
        severity=EventSeverity.SUCCESS
    )
    
    # Pattern match
    collector.create_event(
        EventType.PATTERN_MATCH,
        "Known Issue Identified",
        "Matched pattern: auth_token_expired (85% confidence)",
        module="pattern_db",
        details={
            "pattern_id": "auth_token_expired_a1b2c3",
            "confidence": 0.85,
            "previous_occurrences": 15
        }
    )
    
    # Session end
    time.sleep(0.1)
    collector.create_event(
        EventType.SESSION_END,
        "Debug Session Completed",
        "Issue resolved: Authentication now handles token refresh",
        module="main",
        severity=EventSeverity.SUCCESS
    )
    
    # Generate HTML
    generator = TimelineHTMLGenerator("Authentication Debug Timeline")
    
    metadata = {
        "session_id": "DEMO-TIMELINE",
        "issue_type": "Authentication Token Expiry",
        "start_time": start_time,
        "end_time": time.time()
    }
    
    output_file = Path(__file__).parent.parent / 'demo_timeline.html'
    html_content = generator.generate_timeline(
        collector.events,
        output_file=output_file,
        metadata=metadata
    )
    
    print(f"Demo timeline generated: {output_file}")
    print(f"  Total events: {len(collector.events)}")
    print(f"  Duration: {metadata['end_time'] - metadata['start_time']:.2f} seconds")
    
    return output_file


if __name__ == "__main__":
    # Generate demo timeline
    demo_file = generate_demo_timeline()
    print(f"\nOpen the timeline in your browser:")
    print(f"  file://{demo_file.absolute()}")