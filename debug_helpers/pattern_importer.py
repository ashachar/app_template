#!/usr/bin/env python3
"""
Import patterns from various sources into the Failure Pattern Database.

Sources include:
- Existing error_patterns.json
- Historical debugging sessions
- Test failure logs
- Manual pattern definitions
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import glob

from failure_pattern_db import FailurePatternDB, Solution, CodeChange


class PatternImporter:
    """Import patterns from various sources."""
    
    def __init__(self, pattern_db: Optional[FailurePatternDB] = None):
        self.base_path = Path(__file__).parent
        self.pattern_db = pattern_db or FailurePatternDB()
        self.import_stats = {
            'patterns_imported': 0,
            'sessions_processed': 0,
            'solutions_created': 0,
            'errors': []
        }
    
    def import_from_error_patterns(self, patterns_file: Optional[str] = None):
        """Import from existing error_patterns.json file."""
        patterns_file = patterns_file or self.base_path / 'patterns' / 'error_patterns.json'
        
        try:
            with open(patterns_file, 'r') as f:
                error_patterns = json.load(f)
            
            for category_key, category_data in error_patterns.items():
                if not isinstance(category_data, dict):
                    continue
                
                # Create pattern signature
                pattern_signature = {
                    'error_type': category_data.get('category', 'Unknown'),
                    'error_message': f"{category_data.get('category')} Error",
                    'context_keywords': self._extract_keywords_from_patterns(
                        category_data.get('patterns', [])
                    ),
                    'module_hints': self._infer_modules_from_category(category_key)
                }
                
                # Create a generic solution from suggestions
                suggestions = category_data.get('suggestions', [])
                if suggestions:
                    solution = {
                        'description': suggestions[0] if suggestions else "Check error details",
                        'code_changes': [],
                        'test_cases': []
                    }
                    
                    # Try to extract code changes from suggestions
                    for suggestion in suggestions:
                        if 'cd' in suggestion or '.sh' in suggestion:
                            # Command suggestion
                            solution['code_changes'].append({
                                'file_path': 'terminal',
                                'description': suggestion,
                                'diff_snippet': suggestion
                            })
                    
                    pattern_id = self.pattern_db.record_pattern(
                        pattern_signature,
                        solution,
                        session_id='import_error_patterns'
                    )
                    
                    # Add all regex patterns
                    pattern = self.pattern_db.patterns[pattern_id]
                    pattern.error_patterns = category_data.get('patterns', [])
                    
                    self.import_stats['patterns_imported'] += 1
                
        except Exception as e:
            self.import_stats['errors'].append(f"Error importing error patterns: {str(e)}")
    
    def import_from_sessions(self, sessions_dir: Optional[str] = None):
        """Import patterns from historical debugging sessions."""
        sessions_dir = sessions_dir or self.base_path / 'sessions'
        
        # Find all session JSON files
        session_files = glob.glob(str(sessions_dir / '*.json'))
        session_files.extend(glob.glob(str(sessions_dir / '*' / 'state.json')))
        
        for session_file in session_files:
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                session_id = session_data.get('session_id', Path(session_file).stem)
                
                # Process findings
                for finding in session_data.get('findings', []):
                    if finding['type'] in ['root_cause', 'error', 'bug']:
                        # Extract pattern information
                        pattern_signature = self._extract_pattern_from_finding(finding)
                        
                        # Extract solution if available
                        solution = None
                        if finding.get('fix_suggestion'):
                            solution = {
                                'description': finding['fix_suggestion'],
                                'code_changes': self._extract_code_changes_from_finding(finding),
                                'test_cases': self._extract_test_cases_from_session(session_data)
                            }
                        
                        # Record pattern
                        self.pattern_db.record_pattern(pattern_signature, solution, session_id)
                        
                        if solution:
                            self.import_stats['solutions_created'] += 1
                
                # Also check for common errors in test results
                if 'test_data' in session_data:
                    self._import_from_test_data(session_data['test_data'], session_id)
                
                self.import_stats['sessions_processed'] += 1
                
            except Exception as e:
                self.import_stats['errors'].append(
                    f"Error importing session {session_file}: {str(e)}"
                )
    
    def import_manual_patterns(self, patterns: List[Dict[str, Any]]):
        """Import manually defined patterns."""
        for pattern_def in patterns:
            try:
                pattern_signature = {
                    'error_type': pattern_def.get('error_type', 'Unknown'),
                    'error_message': pattern_def.get('error_message', ''),
                    'context_keywords': pattern_def.get('context_keywords', []),
                    'module_hints': pattern_def.get('module_hints', [])
                }
                
                # Process solutions
                for solution_def in pattern_def.get('solutions', []):
                    solution = {
                        'description': solution_def['description'],
                        'code_changes': [
                            {
                                'file_path': change.get('file_path', ''),
                                'description': change.get('description', ''),
                                'diff_snippet': change.get('diff_snippet', '')
                            }
                            for change in solution_def.get('code_changes', [])
                        ],
                        'test_cases': solution_def.get('test_cases', [])
                    }
                    
                    self.pattern_db.record_pattern(
                        pattern_signature,
                        solution,
                        session_id=solution_def.get('session_id', 'manual_import')
                    )
                    
                    self.import_stats['solutions_created'] += 1
                
                self.import_stats['patterns_imported'] += 1
                
            except Exception as e:
                self.import_stats['errors'].append(
                    f"Error importing manual pattern: {str(e)}"
                )
    
    def _extract_keywords_from_patterns(self, patterns: List[str]) -> List[str]:
        """Extract meaningful keywords from regex patterns."""
        keywords = set()
        
        for pattern in patterns:
            # Extract literal words from regex
            words = re.findall(r'[a-zA-Z_]{3,}', pattern)
            keywords.update(word.lower() for word in words if len(word) > 3)
        
        # Remove common words
        stop_words = {'does', 'not', 'exist', 'error', 'failed', 'cannot', 'invalid'}
        keywords = keywords - stop_words
        
        return list(keywords)[:10]  # Limit to 10 keywords
    
    def _infer_modules_from_category(self, category_key: str) -> List[str]:
        """Infer module hints from category name."""
        modules = []
        
        category_lower = category_key.lower()
        
        if 'database' in category_lower or 'sql' in category_lower:
            modules.extend(['database', 'migration', 'schema'])
        elif 'api' in category_lower:
            modules.extend(['api', 'routes', 'middleware'])
        elif 'auth' in category_lower:
            modules.extend(['auth', 'login', 'session'])
        elif 'react' in category_lower:
            modules.extend(['ui', 'component', 'react'])
        elif 'lambda' in category_lower:
            modules.extend(['lambda', 'serverless', 'aws'])
        elif 'file' in category_lower:
            modules.extend(['filesystem', 'io'])
        
        return modules
    
    def _extract_pattern_from_finding(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """Extract pattern signature from a session finding."""
        # Determine error type
        error_type = finding.get('category', 'Unknown')
        if not error_type or error_type == 'Unknown':
            # Try to infer from description
            description = finding.get('description', '').lower()
            if 'database' in description or 'sql' in description:
                error_type = 'Database'
            elif 'api' in description or 'request' in description:
                error_type = 'API'
            elif 'null' in description or 'undefined' in description:
                error_type = 'Null Reference'
            elif 'auth' in description or 'token' in description:
                error_type = 'Authentication'
        
        # Extract keywords from evidence
        evidence = finding.get('evidence', '')
        keywords = re.findall(r'\b[a-zA-Z_]{4,}\b', evidence.lower())
        keywords = [kw for kw in keywords if len(kw) < 20][:10]
        
        # Infer modules
        modules = []
        related_files = finding.get('related_files', [])
        for file_path in related_files:
            if 'api' in file_path:
                modules.append('api')
            elif 'component' in file_path or 'pages' in file_path:
                modules.append('ui')
            elif 'lambda' in file_path:
                modules.append('lambda')
        
        return {
            'error_type': error_type,
            'error_message': finding.get('description', ''),
            'context_keywords': keywords,
            'module_hints': modules
        }
    
    def _extract_code_changes_from_finding(self, finding: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract code changes from finding data."""
        changes = []
        
        # Look for file references in fix suggestion
        fix_suggestion = finding.get('fix_suggestion', '')
        file_refs = re.findall(r'[a-zA-Z0-9_/]+\.[a-zA-Z]{2,4}', fix_suggestion)
        
        for file_ref in file_refs:
            changes.append({
                'file_path': file_ref,
                'description': fix_suggestion,
                'diff_snippet': None
            })
        
        # Also check related files
        for file_path in finding.get('related_files', []):
            if not any(c['file_path'] == file_path for c in changes):
                changes.append({
                    'file_path': file_path,
                    'description': 'Related file in fix',
                    'diff_snippet': None
                })
        
        return changes
    
    def _extract_test_cases_from_session(self, session_data: Dict[str, Any]) -> List[str]:
        """Extract test cases mentioned in session."""
        test_cases = []
        
        # Check test data
        test_data = session_data.get('test_data', {})
        for category_data in test_data.values():
            for test_name, test_info in category_data.items():
                if 'test' in test_name:
                    test_cases.append(test_name)
        
        # Check checkpoints for test references
        for checkpoint in session_data.get('checkpoints', []):
            desc = checkpoint.get('description', '')
            test_refs = re.findall(r'test_[a-zA-Z0-9_]+', desc)
            test_cases.extend(test_refs)
        
        return list(set(test_cases))[:5]  # Limit to 5 test cases
    
    def _import_from_test_data(self, test_data: Dict[str, Any], session_id: str):
        """Import patterns from test execution data."""
        for category, tests in test_data.items():
            if not isinstance(tests, dict):
                continue
            
            for test_name, test_info in tests.items():
                if isinstance(test_info, dict) and 'value' in test_info:
                    value = test_info['value']
                    
                    # Look for error information
                    if isinstance(value, dict):
                        if 'common_errors' in value:
                            for error, count in value.get('common_errors', []):
                                pattern_signature = {
                                    'error_type': 'Test Failure',
                                    'error_message': error,
                                    'context_keywords': [test_name, category],
                                    'module_hints': [category]
                                }
                                
                                self.pattern_db.record_pattern(
                                    pattern_signature,
                                    None,
                                    session_id
                                )
    
    def generate_import_report(self) -> str:
        """Generate a report of the import process."""
        report = []
        report.append("=" * 60)
        report.append("PATTERN IMPORT REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        report.append("SUMMARY")
        report.append("-" * 30)
        report.append(f"Patterns imported: {self.import_stats['patterns_imported']}")
        report.append(f"Sessions processed: {self.import_stats['sessions_processed']}")
        report.append(f"Solutions created: {self.import_stats['solutions_created']}")
        report.append(f"Errors encountered: {len(self.import_stats['errors'])}")
        report.append("")
        
        # Database stats
        db_stats = self.pattern_db.get_pattern_stats()
        report.append("DATABASE STATUS")
        report.append("-" * 30)
        report.append(f"Total patterns: {db_stats['total_patterns']}")
        report.append(f"Total solutions: {db_stats['total_solutions']}")
        report.append(f"Success rate: {db_stats['average_success_rate']:.1%}")
        report.append("")
        
        # Pattern breakdown
        report.append("PATTERNS BY TYPE")
        report.append("-" * 30)
        for error_type, pattern_ids in db_stats['patterns_by_type'].items():
            report.append(f"{error_type}: {len(pattern_ids)} patterns")
        report.append("")
        
        # Errors
        if self.import_stats['errors']:
            report.append("ERRORS")
            report.append("-" * 30)
            for error in self.import_stats['errors'][:10]:
                report.append(f"- {error}")
            if len(self.import_stats['errors']) > 10:
                report.append(f"... and {len(self.import_stats['errors']) - 10} more errors")
        
        report.append("=" * 60)
        
        return "\n".join(report)


def run_full_import():
    """Run a full import from all available sources."""
    print("Starting full pattern import...")
    
    importer = PatternImporter()
    
    # Import from error patterns
    print("Importing from error_patterns.json...")
    importer.import_from_error_patterns()
    
    # Import from sessions
    print("Importing from debugging sessions...")
    importer.import_from_sessions()
    
    # Save the database
    importer.pattern_db._save_database()
    
    # Generate report
    report = importer.generate_import_report()
    print("\n" + report)
    
    # Save report
    report_path = Path(__file__).parent / 'import_report.txt'
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    run_full_import()