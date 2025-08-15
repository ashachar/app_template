#!/usr/bin/env python3
"""
Debug Session Management - Creates unique session IDs and provides
standardized logging helpers for systematic debugging.
"""

import os
import json
import random
import string
from datetime import datetime
from pathlib import Path

class DebugSession:
    """Manages debug sessions with unique IDs and standardized logging."""
    
    def __init__(self, issue_type=None):
        """Initialize a new debug session."""
        self.session_id = self._generate_session_id(issue_type)
        self.start_time = datetime.now()
        self.issue_type = issue_type
        self.modules = ['UI', 'API', 'DB', 'LAMBDA', 'AUTH']
        self.categories = ['STATE', 'FLOW', 'ERROR', 'TIMING', 'DATA', 'VALIDATE']
        self.session_file = self._create_session_file()
        
    def _generate_session_id(self, issue_type):
        """Generate a readable session ID."""
        # Use issue type prefix if provided
        prefix = issue_type[:4].upper() if issue_type else 'DBG'
        
        # Add random suffix for uniqueness
        suffix = ''.join(random.choices(string.digits, k=3))
        
        return f"{prefix}{suffix}"
    
    def _create_session_file(self):
        """Create a session metadata file."""
        session_dir = Path(__file__).parent / 'sessions'
        session_dir.mkdir(exist_ok=True)
        
        session_file = session_dir / f"{self.session_id}.json"
        
        metadata = {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "issue_type": self.issue_type,
            "log_prefixes": [],
            "files_modified": [],
            "status": "active"
        }
        
        with open(session_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return session_file
    
    def get_prefix(self, module, category='FLOW'):
        """Get a standardized log prefix."""
        module = module.upper()
        category = category.upper()
        
        # Validate inputs
        if module not in self.modules:
            module = 'MISC'
        if category not in self.categories:
            category = 'FLOW'
        
        prefix = f"[DEBUG-{self.session_id}-{module}-{category}]"
        
        # Track this prefix
        self._add_prefix_to_metadata(prefix)
        
        return prefix
    
    def _add_prefix_to_metadata(self, prefix):
        """Add a prefix to session metadata."""
        with open(self.session_file, 'r') as f:
            metadata = json.load(f)
        
        if prefix not in metadata["log_prefixes"]:
            metadata["log_prefixes"].append(prefix)
        
        with open(self.session_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def generate_log_statements(self, language='javascript'):
        """Generate example log statements for different languages."""
        examples = []
        
        if language == 'javascript':
            examples = [
                f"console.log('{self.get_prefix('UI', 'FLOW')} Starting requisition submission');",
                f"console.log('{self.get_prefix('UI', 'DATA')} Form data:', formData);",
                f"console.log('{self.get_prefix('UI', 'VALIDATE')} Validation result:', isValid);",
                f"console.log('{self.get_prefix('API', 'FLOW')} Received request for', req.url);",
                f"console.log('{self.get_prefix('API', 'TIMING')} Query execution time:', endTime - startTime);",
                f"console.log('{self.get_prefix('API', 'ERROR')} Database error:', error.message);",
            ]
        elif language == 'python':
            examples = [
                f"print('{self.get_prefix('LAMBDA', 'FLOW')} Processing event')",
                f"print('{self.get_prefix('LAMBDA', 'DATA')} Event payload:', json.dumps(event))",
                f"print('{self.get_prefix('LAMBDA', 'ERROR')} Failed to process:', str(e))",
                f"logger.info('{self.get_prefix('DB', 'FLOW')} Executing query')",
                f"logger.debug('{self.get_prefix('DB', 'DATA')} Query params:', params)",
            ]
        
        return examples
    
    def get_cleanup_command(self):
        """Get command to clean up this session's logs."""
        return f"python debug_helpers/find_log_prints.py --clean --prefix 'DEBUG-{self.session_id}'"
    
    def close_session(self):
        """Mark session as completed."""
        with open(self.session_file, 'r') as f:
            metadata = json.load(f)
        
        metadata["end_time"] = datetime.now().isoformat()
        metadata["status"] = "completed"
        metadata["duration"] = str(datetime.now() - self.start_time)
        
        with open(self.session_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def print_session_info(self):
        """Print session information."""
        print(f"""
 DEBUG SESSION INITIALIZED
{'=' * 50}
Session ID: {self.session_id}
Issue Type: {self.issue_type or 'General'}
Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}

 LOG PREFIX FORMAT:
[DEBUG-{self.session_id}-MODULE-CATEGORY]

 AVAILABLE MODULES:
{', '.join(self.modules)}

 AVAILABLE CATEGORIES:
{', '.join(self.categories)}

 EXAMPLE USAGE:
""")
        
        # Show JavaScript examples
        print("JavaScript:")
        for example in self.generate_log_statements('javascript')[:3]:
            print(f"  {example}")
        
        print("\nPython:")
        for example in self.generate_log_statements('python')[:2]:
            print(f"  {example}")
        
        print(f"""
 CLEANUP COMMAND:
{self.get_cleanup_command()}

 ANALYZE LOGS:
python debug_helpers/analyze_logs.py --session {self.session_id}
{'=' * 50}
""")


def main():
    """Example usage."""
    import sys
    
    # Get issue type from command line
    issue_type = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Create new session
    session = DebugSession(issue_type)
    session.print_session_info()
    
    # Save session ID to file for easy access
    session_id_file = Path(__file__).parent / '.current_session'
    with open(session_id_file, 'w') as f:
        f.write(session.session_id)


if __name__ == "__main__":
    main()