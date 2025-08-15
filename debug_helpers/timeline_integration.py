#!/usr/bin/env python3
"""
Timeline Integration - Integrates timeline events with existing debug systems.

This module provides seamless integration between the visual timeline system
and existing debugging tools like log analysis, session state, and pattern database.
"""

import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from .timeline_event import (
        TimelineEventCollector, TimelineEvent, EventType, EventSeverity
    )
    from .timeline_generator import TimelineHTMLGenerator
    from .debug_session_state import DebugSessionState
    from .analyze_logs import LogAnalyzer
except ImportError:
    from timeline_event import (
        TimelineEventCollector, TimelineEvent, EventType, EventSeverity
    )
    from timeline_generator import TimelineHTMLGenerator
    from debug_session_state import DebugSessionState
    from analyze_logs import LogAnalyzer


class TimelineDebugger:
    """Enhanced debugger with integrated timeline visualization."""
    
    def __init__(self, session_id: str, issue_type: str = ""):
        self.session_id = session_id
        self.issue_type = issue_type
        self.base_dir = Path(__file__).parent / 'sessions' / session_id
        
        # Initialize components
        self.timeline = TimelineEventCollector(session_id, self.base_dir)
        self.state = DebugSessionState(session_id, base_dir=self.base_dir)
        self.log_analyzer = LogAnalyzer(session_id=session_id)
        
        # Track active operations
        self.active_operations = {}
        
        # Start session
        self._start_session()
        
    def _start_session(self):
        """Initialize debugging session."""
        self.timeline.create_event(
            EventType.SESSION_START,
            f"Debug Session: {self.issue_type or 'Investigation'}",
            f"Session ID: {self.session_id}",
            module="debugger",
            details={
                "issue_type": self.issue_type,
                "start_time": datetime.now().isoformat()
            }
        )
        
    def analyze_logs(self, include_timeline: bool = True) -> Dict[str, Any]:
        """Analyze logs with timeline integration."""
        # Start timed event
        if include_timeline:
            event_id = self.timeline.start_timed_event(
                EventType.USER_ACTION,
                "Log Analysis",
                "Analyzing all available log sources",
                module="log_analyzer"
            )
        
        # Run analysis
        results = self.log_analyzer.analyze_all_logs()
        
        if include_timeline:
            # Record findings in timeline
            if results.get('critical_findings'):
                for finding in results['critical_findings']:
                    self.timeline.add_error_event(
                        finding['message'],
                        module=finding.get('source', 'unknown'),
                        file_path=finding.get('file'),
                        line_number=finding.get('line'),
                        critical=finding.get('severity') == 'CRITICAL'
                    )
            
            # Record pattern matches
            if results.get('pattern_matches'):
                for match in results['pattern_matches']:
                    self.timeline.create_event(
                        EventType.PATTERN_MATCH,
                        f"Pattern: {match['pattern_type']}",
                        f"Confidence: {match['confidence']:.0%}",
                        module="pattern_db",
                        severity=EventSeverity.SUCCESS,
                        details=match
                    )
            
            # End timed event
            self.timeline.end_timed_event(
                event_id,
                success=len(results.get('critical_findings', [])) > 0
            )
        
        return results
    
    def start_operation(self, operation_name: str, description: str = "",
                       module: str = "unknown") -> str:
        """Start tracking a debugging operation."""
        event_id = self.timeline.start_timed_event(
            EventType.USER_ACTION,
            operation_name,
            description or f"Starting {operation_name}",
            module=module
        )
        
        self.active_operations[operation_name] = {
            'event_id': event_id,
            'start_time': time.time()
        }
        
        return event_id
    
    def end_operation(self, operation_name: str, success: bool = True,
                     error_message: Optional[str] = None):
        """End tracking a debugging operation."""
        if operation_name not in self.active_operations:
            return
            
        op_data = self.active_operations.pop(operation_name)
        self.timeline.end_timed_event(
            op_data['event_id'],
            success=success,
            error_message=error_message
        )
    
    def add_finding(self, finding_type: str, description: str,
                   evidence: Optional[str] = None,
                   fix_suggestion: Optional[str] = None,
                   module: str = "unknown"):
        """Add a finding to both state and timeline."""
        # Add to state
        self.state.add_finding(
            finding_type,
            description,
            evidence=evidence,
            fix_suggestion=fix_suggestion
        )
        
        # Add to timeline
        self.timeline.add_finding_event(
            finding_type,
            description,
            evidence=evidence,
            fix_suggestion=fix_suggestion,
            module=module
        )
        
        # Check for pattern matches
        if self.state.pattern_matches:
            latest_match = self.state.pattern_matches[-1]
            self.timeline.create_event(
                EventType.PATTERN_MATCH,
                f"Matched: {latest_match['pattern_type']}",
                f"Solutions available: {len(latest_match.get('solutions', []))}",
                module="pattern_db",
                severity=EventSeverity.SUCCESS,
                details=latest_match
            )
    
    def run_test(self, test_name: str, test_function=None) -> bool:
        """Run a test with timeline tracking."""
        start_time = time.time()
        success = False
        error_message = None
        
        try:
            if test_function:
                result = test_function()
                success = bool(result)
            else:
                # Placeholder for actual test execution
                success = True
        except Exception as e:
            success = False
            error_message = str(e)
            
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Record in timeline
        self.timeline.add_test_event(
            test_name,
            passed=success,
            duration_ms=duration_ms,
            error_message=error_message
        )
        
        return success
    
    def checkpoint(self, name: str, description: str = ""):
        """Create a checkpoint in the debugging session."""
        self.timeline.create_event(
            EventType.CHECKPOINT,
            name,
            description or f"Checkpoint: {name}",
            module="debugger",
            severity=EventSeverity.INFO
        )
        
        # Also save state
        self.state.save_state()
    
    def module_transition(self, from_module: str, to_module: str, reason: str = ""):
        """Record module transition in timeline."""
        self.timeline.create_event(
            EventType.MODULE_TRANSITION,
            f"{from_module} → {to_module}",
            reason or "Investigating in different module",
            module=to_module
        )
    
    def api_call(self, method: str, endpoint: str, 
                 success: bool, response_time_ms: Optional[int] = None,
                 error: Optional[str] = None):
        """Record API call in timeline."""
        event = self.timeline.create_event(
            EventType.API_CALL,
            f"{method} {endpoint}",
            "Success" if success else f"Failed: {error or 'Unknown error'}",
            module="api",
            severity=EventSeverity.SUCCESS if success else EventSeverity.ERROR,
            duration_ms=response_time_ms
        )
        
        if not success:
            # Link to error event if created
            if error:
                error_event = self.timeline.add_error_event(
                    error,
                    module="api",
                    critical=False
                )
                self.timeline.link_events(event.event_id, error_event.event_id)
    
    def file_change(self, file_path: str, change_type: str, description: str = ""):
        """Record file change in timeline."""
        self.timeline.create_event(
            EventType.FILE_CHANGE,
            f"{change_type}: {Path(file_path).name}",
            description or f"{change_type} {file_path}",
            module="filesystem",
            severity=EventSeverity.INFO,
            file_path=file_path
        )
    
    def end_session(self, resolution: str = "Unknown", success: bool = False):
        """End the debugging session."""
        # Create final checkpoint
        self.checkpoint("Session End", f"Resolution: {resolution}")
        
        # End session event
        self.timeline.create_event(
            EventType.SESSION_END,
            "Debug Session Completed",
            f"Resolution: {resolution}",
            module="debugger",
            severity=EventSeverity.SUCCESS if success else EventSeverity.WARNING
        )
        
        # Save everything
        self.timeline.save_events()
        self.state.save_state()
        
        # Generate timeline
        return self.generate_timeline()
    
    def generate_timeline(self, output_name: Optional[str] = None) -> Path:
        """Generate HTML timeline visualization."""
        generator = TimelineHTMLGenerator(
            f"Debug Timeline: {self.issue_type or self.session_id}"
        )
        
        # Prepare metadata
        metadata = {
            "session_id": self.session_id,
            "issue_type": self.issue_type,
            "total_findings": len(self.state.findings),
            "pattern_matches": len(self.state.pattern_matches),
            "tests_run": sum(1 for e in self.timeline.events 
                           if e.event_type == EventType.TEST_RUN),
            "errors_found": sum(1 for e in self.timeline.events 
                              if e.severity in [EventSeverity.ERROR, EventSeverity.CRITICAL])
        }
        
        # Generate output filename
        if not output_name:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_name = f"timeline_{self.session_id}_{timestamp}.html"
            
        output_file = self.base_dir / output_name
        
        # Generate timeline
        generator.generate_timeline(
            self.timeline.events,
            output_file=output_file,
            metadata=metadata
        )
        
        return output_file
    
    def get_summary(self) -> Dict[str, Any]:
        """Get debugging session summary."""
        timeline_summary = self.timeline.get_summary()
        state_summary = {
            "findings": len(self.state.findings),
            "pattern_matches": len(self.state.pattern_matches),
            "checkpoints": len(self.state.checkpoints),
            "next_steps": self.state.suggest_next_steps()
        }
        
        return {
            "session_id": self.session_id,
            "issue_type": self.issue_type,
            "timeline": timeline_summary,
            "state": state_summary,
            "timeline_file": str(self.base_dir / f"timeline_{self.session_id}.html")
        }


class TimelineLogEnhancer:
    """Enhances log analysis with timeline events."""
    
    def __init__(self, timeline: TimelineEventCollector):
        self.timeline = timeline
        
    def process_log_entry(self, entry: Dict[str, Any]):
        """Convert log entry to timeline event."""
        # Determine event type and severity
        level = entry.get('level', 'INFO').upper()
        
        if 'error' in entry.get('message', '').lower() or level in ['ERROR', 'CRITICAL']:
            event_type = EventType.ERROR
            severity = EventSeverity.CRITICAL if level == 'CRITICAL' else EventSeverity.ERROR
        elif 'warning' in entry.get('message', '').lower() or level == 'WARNING':
            event_type = EventType.WARNING
            severity = EventSeverity.WARNING
        else:
            # Skip info/debug logs unless they're important
            return None
            
        # Create timeline event
        return self.timeline.create_event(
            event_type,
            f"Log: {entry.get('source', 'Unknown')}",
            entry.get('message', 'No message'),
            module=entry.get('module', 'logs'),
            severity=severity,
            file_path=entry.get('file'),
            line_number=entry.get('line'),
            details={
                'log_level': level,
                'source': entry.get('source'),
                'raw_entry': entry
            }
        )


def demo_integrated_debugging():
    """Demonstrate integrated timeline debugging."""
    print("\n" + "="*60)
    print(" INTEGRATED TIMELINE DEBUGGING DEMO")
    print("="*60)
    
    # Create integrated debugger
    debugger = TimelineDebugger('INTEGRATED-DEMO', 'API Authentication Failure')
    
    print("\n1⃣ Starting debugging session...")
    
    # Analyze logs
    print("\n2⃣ Analyzing logs...")
    log_results = debugger.analyze_logs()
    print(f"   Found {len(log_results.get('critical_findings', []))} critical issues")
    
    # Simulate investigation steps
    print("\n3⃣ Investigating authentication flow...")
    
    # Start operation
    op_id = debugger.start_operation(
        "Check Auth Middleware",
        "Examining authentication middleware configuration",
        module="auth"
    )
    
    time.sleep(0.5)  # Simulate work
    
    # Add finding
    debugger.add_finding(
        'configuration',
        'JWT secret not properly configured',
        evidence='JWT_SECRET env var is undefined',
        fix_suggestion='Set JWT_SECRET in environment variables',
        module='auth'
    )
    
    debugger.end_operation("Check Auth Middleware", success=True)
    
    # Module transition
    debugger.module_transition('auth', 'api', 'Checking API endpoint configuration')
    
    # Run tests
    print("\n4⃣ Running tests...")
    debugger.run_test('test_auth_middleware_config', lambda: False)
    time.sleep(0.2)
    debugger.run_test('test_auth_middleware_config', lambda: True)
    
    # API call tracking
    print("\n5⃣ Testing API endpoints...")
    debugger.api_call('POST', '/api/login', success=False, 
                     response_time_ms=235, error='401 Unauthorized')
    
    time.sleep(0.3)
    
    debugger.api_call('POST', '/api/login', success=True, response_time_ms=187)
    
    # File changes
    print("\n6⃣ Applying fixes...")
    debugger.file_change('src/middleware/auth.js', 'Modified', 
                        'Added JWT secret configuration')
    debugger.file_change('.env', 'Created', 'Added JWT_SECRET')
    
    # Create checkpoint
    debugger.checkpoint('Fix Applied', 'JWT configuration corrected')
    
    # End session
    print("\n7⃣ Completing session...")
    timeline_file = debugger.end_session(
        resolution="JWT secret configuration fixed",
        success=True
    )
    
    # Get summary
    summary = debugger.get_summary()
    
    print("\n" + "="*60)
    print(" SESSION SUMMARY")
    print("="*60)
    print(f"Session ID: {summary['session_id']}")
    print(f"Issue Type: {summary['issue_type']}")
    print(f"Total Events: {summary['timeline']['total_events']}")
    print(f"Duration: {summary['timeline']['duration_seconds']:.1f}s")
    print(f"Findings: {summary['state']['findings']}")
    print(f"Pattern Matches: {summary['state']['pattern_matches']}")
    print(f"Errors Found: {summary['timeline']['error_count']}")
    print(f"Tests Run: {summary['timeline']['event_types'].get('test_run', 0)}")
    
    print(f"\n Timeline generated: {timeline_file}")
    print(f"   Open in browser: file://{timeline_file.absolute()}")
    
    print("\n" + "="*60)
    print(" DEMO COMPLETE")
    print("="*60)
    
    return timeline_file


if __name__ == "__main__":
    # Run demo
    demo_integrated_debugging()