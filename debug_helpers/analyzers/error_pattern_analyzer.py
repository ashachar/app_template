#!/usr/bin/env python3
"""
Error Pattern Analyzer - Analyzes errors across workers to identify patterns.
"""

import re
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple


class ErrorPatternAnalyzer:
    """Analyzes errors across all workers to find patterns."""
    
    def __init__(self):
        # Pattern matchers for common issues
        self.error_patterns = {
            'null_reference': re.compile(r"(null|undefined|None).*?(reference|property|attribute)", re.I),
            'timeout': re.compile(r"(timeout|timed out|exceeded.*?timeout)", re.I),
            'connection': re.compile(r"(connection.*?(refused|failed|error)|ECONNREFUSED)", re.I),
            'authentication': re.compile(r"(401|403|unauthorized|forbidden|auth.*?fail)", re.I),
            'validation': re.compile(r"(validation.*?(error|fail)|invalid.*?data)", re.I),
            'database': re.compile(r"(database|sql|query).*?(error|fail|exception)", re.I),
            'api_error': re.compile(r"(4\d{2}|5\d{2}).*?(error|fail)|api.*?error", re.I)
        }
    
    def analyze_errors(self, worker_results: List[Dict[str, Any]]) -> Tuple[List[Tuple[str, int]], Dict[str, List]]:
        """
        Analyze errors across all workers to find patterns.
        
        Returns:
            Tuple of (common_errors, error_patterns)
        """
        error_messages = []
        error_categories = defaultdict(list)
        
        for worker_result in worker_results:
            if not worker_result['success'] and worker_result.get('error'):
                error = worker_result['error']
                error_messages.append(error)
                
                # Categorize error
                for category, pattern in self.error_patterns.items():
                    if pattern.search(error):
                        error_categories[category].append({
                            'scenario': worker_result['scenario_name'],
                            'error': error
                        })
                
                # Also check logs for error patterns
                for log_line in worker_result.get('logs', []):
                    if 'error' in log_line.lower() or 'fail' in log_line.lower():
                        for category, pattern in self.error_patterns.items():
                            if pattern.search(log_line):
                                error_categories[category].append({
                                    'scenario': worker_result['scenario_name'],
                                    'log': log_line
                                })
        
        # Find most common errors
        common_errors = []
        if error_messages:
            error_counter = Counter(error_messages)
            common_errors = error_counter.most_common(5)
        
        return common_errors, dict(error_categories)