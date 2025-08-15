#!/usr/bin/env python3
"""
Failure Pattern Database - Learns from debugging sessions to suggest proven solutions.

This system:
1. Stores failure patterns with their successful solutions
2. Matches new errors against known patterns  
3. Suggests solutions ranked by confidence
4. Learns and improves from each debugging session
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
from pathlib import Path
import difflib
from collections import defaultdict
import hashlib


@dataclass
class CodeChange:
    """Represents a code change that fixed an issue."""
    file_path: str
    description: str
    diff_snippet: Optional[str] = None
    line_numbers: Optional[Tuple[int, int]] = None


@dataclass
class Solution:
    """A solution that fixed a failure pattern."""
    description: str
    code_changes: List[CodeChange]
    test_cases: List[str] = field(default_factory=list)
    session_ids: List[str] = field(default_factory=list)
    success_count: int = 0
    failure_count: int = 0
    last_used: Optional[str] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate of this solution."""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0


@dataclass
class FailurePattern:
    """Represents a failure pattern with associated solutions."""
    pattern_id: str
    error_type: str
    error_patterns: List[str]  # Regex patterns that match this error
    context_keywords: List[str]  # Keywords that help identify context
    module_hints: List[str]  # Modules where this error commonly occurs
    solutions: List[Solution] = field(default_factory=list)
    occurrences: int = 0
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    related_patterns: List[str] = field(default_factory=list)  # IDs of similar patterns
    
    def add_solution(self, solution: Solution):
        """Add a solution if it doesn't already exist."""
        # Check if solution already exists
        for existing in self.solutions:
            if existing.description == solution.description:
                # Merge session IDs
                existing.session_ids.extend(solution.session_ids)
                existing.session_ids = list(set(existing.session_ids))
                return
        self.solutions.append(solution)
        # Sort by success rate
        self.solutions.sort(key=lambda s: s.success_rate, reverse=True)


class FailurePatternDB:
    """Database for managing failure patterns and their solutions."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.base_path = Path(__file__).parent
        self.db_path = db_path or self.base_path / 'patterns' / 'failure_patterns.json'
        self.patterns: Dict[str, FailurePattern] = {}
        self.pattern_index: Dict[str, List[str]] = defaultdict(list)  # Error type to pattern IDs
        self.session_solutions: Dict[str, List[str]] = defaultdict(list)  # Session ID to pattern IDs
        self._load_database()
    
    def _load_database(self):
        """Load patterns from JSON file."""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                
                # Convert JSON to FailurePattern objects
                for pattern_id, pattern_data in data.get('patterns', {}).items():
                    solutions = []
                    for sol_data in pattern_data.get('solutions', []):
                        code_changes = [
                            CodeChange(**change) for change in sol_data.get('code_changes', [])
                        ]
                        sol_data['code_changes'] = code_changes
                        solutions.append(Solution(**sol_data))
                    
                    pattern_data['solutions'] = solutions
                    pattern = FailurePattern(**pattern_data)
                    self.patterns[pattern_id] = pattern
                    
                    # Build index
                    self.pattern_index[pattern.error_type].append(pattern_id)
                
                # Load session solutions mapping
                self.session_solutions = defaultdict(list, data.get('session_solutions', {}))
                
            except Exception as e:
                print(f"Warning: Could not load failure pattern database: {e}")
    
    def _save_database(self):
        """Save patterns to JSON file."""
        # Convert to JSON-serializable format
        data = {
            'patterns': {},
            'session_solutions': dict(self.session_solutions),
            'metadata': {
                'last_updated': datetime.now().isoformat(),
                'total_patterns': len(self.patterns),
                'total_solutions': sum(len(p.solutions) for p in self.patterns.values())
            }
        }
        
        for pattern_id, pattern in self.patterns.items():
            pattern_dict = asdict(pattern)
            # Convert Solution objects
            pattern_dict['solutions'] = [
                {
                    **asdict(sol),
                    'code_changes': [asdict(change) for change in sol.code_changes]
                }
                for sol in pattern.solutions
            ]
            data['patterns'][pattern_id] = pattern_dict
        
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to file
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def generate_pattern_id(self, error_type: str, error_message: str) -> str:
        """Generate a unique pattern ID."""
        # Create hash from error type and key parts of message
        key_parts = re.findall(r'\w+', error_message.lower())[:5]  # First 5 words
        id_string = f"{error_type}:{'_'.join(key_parts)}"
        hash_suffix = hashlib.md5(id_string.encode()).hexdigest()[:6]
        return f"{error_type.lower().replace(' ', '_')}_{hash_suffix}"
    
    def find_similar_patterns(self, error_message: str, context: Optional[Dict[str, Any]] = None,
                            confidence_threshold: float = 0.5) -> List[Tuple[FailurePattern, float, List[Solution]]]:
        """
        Find patterns similar to the given error with confidence scores.
        
        Returns list of (pattern, confidence, relevant_solutions) tuples.
        """
        matches = []
        
        for pattern in self.patterns.values():
            confidence = 0.0
            
            # Check regex patterns
            pattern_match_score = 0.0
            for regex_pattern in pattern.error_patterns:
                try:
                    if re.search(regex_pattern, error_message, re.IGNORECASE):
                        pattern_match_score = 0.6  # High score for regex match
                        break
                except:
                    pass
            
            # Fuzzy string matching if no regex match
            if pattern_match_score == 0:
                for regex_pattern in pattern.error_patterns:
                    # Extract literal parts from regex for fuzzy matching
                    literal_parts = re.findall(r'[a-zA-Z_]+', regex_pattern)
                    if literal_parts:
                        literal_string = ' '.join(literal_parts)
                        similarity = difflib.SequenceMatcher(None, 
                                                           literal_string.lower(), 
                                                           error_message.lower()).ratio()
                        pattern_match_score = max(pattern_match_score, similarity * 0.4)
            
            confidence += pattern_match_score
            
            # Context matching
            if context:
                context_score = 0.0
                context_str = str(context).lower()
                
                # Check module hints
                if 'module' in context:
                    for module in pattern.module_hints:
                        if module.lower() in context['module'].lower():
                            context_score += 0.2
                            break
                
                # Check context keywords
                keyword_matches = sum(1 for kw in pattern.context_keywords 
                                    if kw.lower() in context_str)
                context_score += min(0.2, keyword_matches * 0.05)
                
                confidence += context_score
            
            # Consider pattern usage (popular patterns get small boost)
            if pattern.occurrences > 10:
                confidence += 0.1
            
            # Filter by threshold and add to matches
            if confidence >= confidence_threshold:
                # Get solutions sorted by success rate
                relevant_solutions = sorted(pattern.solutions, 
                                          key=lambda s: s.success_rate, 
                                          reverse=True)
                matches.append((pattern, confidence, relevant_solutions))
        
        # Sort by confidence
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches
    
    def record_pattern(self, pattern_signature: Dict[str, Any], 
                      solution: Optional[Dict[str, Any]] = None,
                      session_id: Optional[str] = None) -> str:
        """
        Record a new pattern or update existing one.
        
        Returns the pattern ID.
        """
        error_type = pattern_signature.get('error_type', 'Unknown')
        error_message = pattern_signature.get('error_message', '')
        
        # Find existing pattern or create new one
        pattern_id = None
        
        # Check if pattern already exists
        matches = self.find_similar_patterns(error_message, 
                                           pattern_signature.get('context'),
                                           confidence_threshold=0.8)
        
        if matches:
            # Use the best matching pattern
            pattern = matches[0][0]
            pattern_id = pattern.pattern_id
        else:
            # Create new pattern
            pattern_id = self.generate_pattern_id(error_type, error_message)
            
            # Extract patterns from error message
            error_patterns = self._extract_error_patterns(error_message)
            
            pattern = FailurePattern(
                pattern_id=pattern_id,
                error_type=error_type,
                error_patterns=error_patterns,
                context_keywords=pattern_signature.get('context_keywords', []),
                module_hints=pattern_signature.get('module_hints', []),
                first_seen=datetime.now().isoformat(),
                occurrences=0
            )
            self.patterns[pattern_id] = pattern
            self.pattern_index[error_type].append(pattern_id)
        
        # Update pattern
        pattern = self.patterns[pattern_id]
        pattern.occurrences += 1
        pattern.last_seen = datetime.now().isoformat()
        
        # Add solution if provided
        if solution and session_id:
            code_changes = [
                CodeChange(**change) for change in solution.get('code_changes', [])
            ]
            
            new_solution = Solution(
                description=solution['description'],
                code_changes=code_changes,
                test_cases=solution.get('test_cases', []),
                session_ids=[session_id],
                last_used=datetime.now().isoformat()
            )
            
            pattern.add_solution(new_solution)
            self.session_solutions[session_id].append(pattern_id)
        
        self._save_database()
        return pattern_id
    
    def record_solution_result(self, pattern_id: str, solution_index: int, 
                             success: bool, session_id: str):
        """Record whether a solution worked or not."""
        if pattern_id not in self.patterns:
            return
        
        pattern = self.patterns[pattern_id]
        if solution_index < len(pattern.solutions):
            solution = pattern.solutions[solution_index]
            
            if success:
                solution.success_count += 1
            else:
                solution.failure_count += 1
            
            solution.last_used = datetime.now().isoformat()
            if session_id not in solution.session_ids:
                solution.session_ids.append(session_id)
            
            # Re-sort solutions by success rate
            pattern.solutions.sort(key=lambda s: s.success_rate, reverse=True)
            
            self._save_database()
    
    def _extract_error_patterns(self, error_message: str) -> List[str]:
        """Extract regex patterns from error message."""
        patterns = []
        
        # Escape special regex characters but preserve some flexibility
        escaped = re.escape(error_message)
        
        # Replace common variable parts with regex patterns
        # Numbers
        pattern = re.sub(r'\\\d+', r'\\d+', escaped)
        # Quoted strings
        pattern = re.sub(r'\\"[^"]*\\"', r'\\"[^"]*\\"', pattern)
        pattern = re.sub(r"\\'[^']*\\'", r"\\'[^']*\\'", pattern)
        # File paths
        pattern = re.sub(r'[\\/][^\s\\/]+[\\/]', r'[\\\\/][^\\s\\\\/]+[\\\\/]', pattern)
        
        patterns.append(pattern)
        
        # Also store simplified version
        key_words = re.findall(r'\b\w{4,}\b', error_message)[:5]
        if key_words:
            simple_pattern = '.*'.join(re.escape(word) for word in key_words)
            patterns.append(simple_pattern)
        
        return patterns
    
    def get_pattern_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        total_solutions = sum(len(p.solutions) for p in self.patterns.values())
        successful_solutions = sum(
            s.success_count 
            for p in self.patterns.values() 
            for s in p.solutions
        )
        total_attempts = sum(
            s.success_count + s.failure_count
            for p in self.patterns.values() 
            for s in p.solutions
        )
        
        return {
            'total_patterns': len(self.patterns),
            'total_solutions': total_solutions,
            'successful_applications': successful_solutions,
            'total_attempts': total_attempts,
            'average_success_rate': successful_solutions / total_attempts if total_attempts > 0 else 0,
            'patterns_by_type': dict(self.pattern_index),
            'most_common_patterns': sorted(
                self.patterns.values(),
                key=lambda p: p.occurrences,
                reverse=True
            )[:10]
        }
    
    def import_from_session(self, session_data: Dict[str, Any], session_id: str):
        """Import patterns and solutions from a debugging session."""
        # Extract findings
        for finding in session_data.get('findings', []):
            if finding['type'] == 'root_cause':
                # Create pattern signature
                pattern_signature = {
                    'error_type': finding.get('category', 'Unknown'),
                    'error_message': finding['description'],
                    'context_keywords': [],
                    'module_hints': []
                }
                
                # Extract module from evidence
                evidence = finding.get('evidence', '')
                if 'api' in evidence.lower():
                    pattern_signature['module_hints'].append('api')
                if 'ui' in evidence.lower() or 'component' in evidence.lower():
                    pattern_signature['module_hints'].append('ui')
                if 'database' in evidence.lower() or 'db' in evidence.lower():
                    pattern_signature['module_hints'].append('database')
                
                # Create solution if fix suggestion exists
                solution = None
                if finding.get('fix_suggestion'):
                    solution = {
                        'description': finding['fix_suggestion'],
                        'code_changes': [],  # Would need to extract from session
                        'test_cases': []  # Would need to extract from test data
                    }
                
                self.record_pattern(pattern_signature, solution, session_id)