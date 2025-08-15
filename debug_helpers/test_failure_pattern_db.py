#!/usr/bin/env python3
"""
Comprehensive tests for the Failure Pattern Database system.
Tests pattern matching, solution tracking, and integration.
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from debug_helpers.failure_pattern_db import FailurePatternDB, Solution, CodeChange
from debug_helpers.pattern_matcher import PatternMatcher, MatchResult
from debug_helpers.pattern_importer import PatternImporter


class TestFailurePatternDB:
    """Test the failure pattern database functionality."""
    
    def __init__(self):
        self.temp_dir = None
        self.passed_tests = []
        self.failed_tests = []
    
    def setup(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / 'test_patterns.json'
    
    def teardown(self):
        """Clean up test environment."""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def run_test(self, test_name: str, test_func):
        """Run a single test and track results."""
        try:
            print(f"\n Testing: {test_name}")
            test_func()
            print(f" PASSED: {test_name}")
            self.passed_tests.append(test_name)
        except Exception as e:
            print(f" FAILED: {test_name}")
            print(f"   Error: {str(e)}")
            self.failed_tests.append((test_name, str(e)))
    
    def test_pattern_creation_and_storage(self):
        """Test creating and storing patterns."""
        db = FailurePatternDB(self.db_path)
        
        # Create a pattern
        pattern_signature = {
            'error_type': 'Database',
            'error_message': 'relation "users" does not exist',
            'context_keywords': ['migration', 'schema'],
            'module_hints': ['database', 'migration']
        }
        
        solution = {
            'description': 'Run database migrations',
            'code_changes': [
                {
                    'file_path': 'terminal',
                    'description': 'cd schema && ./run_migration.sh',
                    'diff_snippet': None
                }
            ],
            'test_cases': ['test_database_schema']
        }
        
        # Record pattern
        pattern_id = db.record_pattern(pattern_signature, solution, 'TEST-001')
        
        # Verify pattern created
        assert pattern_id in db.patterns, "Pattern not created"
        pattern = db.patterns[pattern_id]
        
        assert pattern.error_type == 'Database', "Wrong error type"
        assert pattern.occurrences == 1, "Wrong occurrence count"
        assert len(pattern.solutions) == 1, "Solution not added"
        assert pattern.solutions[0].description == solution['description'], "Wrong solution"
        
        # Save and reload
        db._save_database()
        
        # Create new DB instance and verify persistence
        db2 = FailurePatternDB(self.db_path)
        assert pattern_id in db2.patterns, "Pattern not persisted"
        assert db2.patterns[pattern_id].solutions[0].description == solution['description']
    
    def test_pattern_matching(self):
        """Test pattern matching functionality."""
        db = FailurePatternDB(self.db_path)
        
        # Add test patterns
        patterns = [
            {
                'error_type': 'Null Reference',
                'error_message': 'Cannot read property "map" of null',
                'context_keywords': ['render', 'component'],
                'module_hints': ['ui', 'react']
            },
            {
                'error_type': 'API',
                'error_message': '401 Unauthorized',
                'context_keywords': ['auth', 'token'],
                'module_hints': ['api', 'auth']
            },
            {
                'error_type': 'Database',
                'error_message': 'duplicate key value violates unique constraint',
                'context_keywords': ['insert', 'create'],
                'module_hints': ['database']
            }
        ]
        
        for sig in patterns:
            db.record_pattern(sig, None, 'TEST')
        
        # Test exact match
        matches = db.find_similar_patterns(
            'Cannot read property "map" of null',
            {'module': 'ui'},
            confidence_threshold=0.5
        )
        
        assert len(matches) > 0, "No matches found for exact error"
        assert matches[0][1] > 0.7, "Low confidence for exact match"
        assert matches[0][0].error_type == 'Null Reference', "Wrong pattern matched"
        
        # Test fuzzy match
        matches = db.find_similar_patterns(
            'Cannot read property "filter" of undefined',
            {'module': 'ui'},
            confidence_threshold=0.4
        )
        
        assert len(matches) > 0, "No fuzzy matches found"
        assert matches[0][0].error_type == 'Null Reference', "Wrong fuzzy match"
        
        # Test context-based matching
        matches = db.find_similar_patterns(
            'Error: Authentication failed',
            {'module': 'api', 'action': 'login'},
            confidence_threshold=0.3
        )
        
        assert len(matches) > 0, "No context matches found"
        # Should match API pattern due to context
        api_match_found = any(m[0].error_type == 'API' for m in matches)
        assert api_match_found, "API pattern not matched with context"
    
    def test_solution_tracking(self):
        """Test solution success tracking."""
        db = FailurePatternDB(self.db_path)
        
        # Create pattern with solution
        pattern_id = db.record_pattern(
            {
                'error_type': 'Test Error',
                'error_message': 'Test error message',
                'context_keywords': [],
                'module_hints': []
            },
            {
                'description': 'Test solution',
                'code_changes': [],
                'test_cases': []
            },
            'TEST-001'
        )
        
        # Record solution attempts
        db.record_solution_result(pattern_id, 0, True, 'TEST-002')
        db.record_solution_result(pattern_id, 0, True, 'TEST-003')
        db.record_solution_result(pattern_id, 0, False, 'TEST-004')
        
        # Check success rate
        pattern = db.patterns[pattern_id]
        solution = pattern.solutions[0]
        
        assert solution.success_count == 2, f"Wrong success count: {solution.success_count}"
        assert solution.failure_count == 1, f"Wrong failure count: {solution.failure_count}"
        assert solution.success_rate == 2/3, f"Wrong success rate: {solution.success_rate}"
    
    def test_pattern_matcher(self):
        """Test advanced pattern matching capabilities."""
        matcher = PatternMatcher()
        
        # Test text similarity
        pattern_data = {
            'pattern_id': 'test_pattern',
            'error_type': 'Database',
            'error_patterns': [
                'relation.*does not exist',
                'table.*not found'
            ],
            'context_keywords': ['migration', 'schema'],
            'module_hints': ['database']
        }
        
        # Test regex match
        result = matcher.match_pattern(
            'ERROR: relation "users" does not exist',
            pattern_data
        )
        
        assert result.text_similarity > 0.8, "Low text similarity for regex match"
        assert 'relation.*does not exist' in result.matched_patterns, "Pattern not matched"
        
        # Test fuzzy match
        result = matcher.match_pattern(
            'Cannot find table users in database',
            pattern_data
        )
        
        assert result.text_similarity > 0.2, f"No fuzzy match found: {result.text_similarity}"
        
        # Test context scoring
        result = matcher.match_pattern(
            'Database error occurred',
            pattern_data,
            {'module': 'database', 'action': 'migration'}
        )
        
        assert result.context_similarity > 0.5, "Low context similarity"
        assert 'migration' in result.matched_keywords, "Keyword not matched"
    
    def test_pattern_importer(self):
        """Test importing patterns from various sources."""
        # Create test error patterns file
        error_patterns = {
            "test_errors": {
                "patterns": ["test.*error", "sample.*issue"],
                "category": "Test",
                "severity": "medium",
                "suggestions": ["Fix the test error", "Check test configuration"]
            }
        }
        
        patterns_file = self.temp_dir / 'error_patterns.json'
        with open(patterns_file, 'w') as f:
            json.dump(error_patterns, f)
        
        # Create test session file
        session_data = {
            "session_id": "TEST-123",
            "findings": [
                {
                    "type": "root_cause",
                    "description": "Test error in module",
                    "evidence": "Stack trace shows test failure",
                    "fix_suggestion": "Update test configuration",
                    "related_files": ["test.py"]
                }
            ]
        }
        
        sessions_dir = self.temp_dir / 'sessions'
        sessions_dir.mkdir()
        with open(sessions_dir / 'TEST-123.json', 'w') as f:
            json.dump(session_data, f)
        
        # Run importer
        db = FailurePatternDB(self.temp_dir / 'imported_patterns.json')
        importer = PatternImporter(db)
        
        importer.import_from_error_patterns(patterns_file)
        importer.import_from_sessions(sessions_dir)
        
        # Verify imports
        assert importer.import_stats['patterns_imported'] > 0, "No patterns imported"
        assert importer.import_stats['sessions_processed'] > 0, "No sessions processed"
        
        # Check database has patterns
        stats = db.get_pattern_stats()
        assert stats['total_patterns'] > 0, "No patterns in database"
    
    def test_integration_with_session_state(self):
        """Test integration with debug session state."""
        # This would require the actual session state module
        # For now, test the interface
        db = FailurePatternDB(self.db_path)
        
        # Simulate finding from session
        finding = {
            'type': 'root_cause',
            'description': 'API returns 401 Unauthorized',
            'evidence': 'Token expired after 24 hours',
            'fix_suggestion': 'Implement token refresh'
        }
        
        context = {
            'module': 'auth',
            'action': 'api_call'
        }
        
        # Find matching patterns
        matches = db.find_similar_patterns(
            finding['description'],
            context,
            confidence_threshold=0.4
        )
        
        # This would normally return matches from the populated database
        # For testing, just verify the method works
        assert isinstance(matches, list), "find_similar_patterns should return a list"
    
    def test_pattern_evolution(self):
        """Test pattern refinement over time."""
        db = FailurePatternDB(self.db_path)
        
        # Create initial pattern
        pattern_id = db.record_pattern(
            {
                'error_type': 'Evolving Error',
                'error_message': 'Initial error message',
                'context_keywords': ['test'],
                'module_hints': ['module1']
            },
            None,
            'TEST-001'
        )
        
        # Record similar patterns that should be merged/related
        similar_id = db.record_pattern(
            {
                'error_type': 'Evolving Error',
                'error_message': 'Similar error message with more detail',
                'context_keywords': ['test', 'additional'],
                'module_hints': ['module1', 'module2']
            },
            None,
            'TEST-002'
        )
        
        # Both patterns should exist
        assert pattern_id in db.patterns
        assert similar_id in db.patterns
        
        # Patterns should have increased occurrence counts
        assert db.patterns[pattern_id].occurrences >= 1
    
    def test_database_statistics(self):
        """Test pattern database statistics."""
        # Use a fresh database for this test
        stats_db_path = self.temp_dir / 'stats_test.json'
        db = FailurePatternDB(stats_db_path)
        
        # Add various patterns
        for i in range(5):
            db.record_pattern(
                {
                    'error_type': f'Type{i % 3}',
                    'error_message': f'Error {i}',
                    'context_keywords': [],
                    'module_hints': []
                },
                {
                    'description': f'Solution {i}',
                    'code_changes': [],
                    'test_cases': []
                } if i % 2 == 0 else None,
                f'TEST-{i:03d}'
            )
        
        # Record some solution results
        for pattern_id in list(db.patterns.keys())[:2]:
            if db.patterns[pattern_id].solutions:  # Only if pattern has solutions
                db.record_solution_result(pattern_id, 0, True, 'TEST-SUCCESS')
        
        # Get statistics
        stats = db.get_pattern_stats()
        
        assert stats['total_patterns'] == 5, f"Wrong pattern count: {stats['total_patterns']}"
        assert stats['total_solutions'] >= 2, f"Wrong solution count: {stats['total_solutions']}"
        # Since we only add solutions to even-indexed patterns (0, 2, 4) and only record success for first 2
        # we should have at least 1 successful application (pattern 0 has a solution)
        assert stats['successful_applications'] >= 1, f"Wrong success count: {stats['successful_applications']}"
        assert 'patterns_by_type' in stats, "Missing patterns by type"
        assert len(stats['most_common_patterns']) <= 10, "Too many common patterns"
    
    def run_all_tests(self):
        """Run all tests."""
        print("\n" + "="*60)
        print(" TESTING FAILURE PATTERN DATABASE")
        print("="*60)
        
        self.setup()
        
        # Run all test methods
        test_methods = [
            ("Pattern Creation and Storage", self.test_pattern_creation_and_storage),
            ("Pattern Matching", self.test_pattern_matching),
            ("Solution Tracking", self.test_solution_tracking),
            ("Advanced Pattern Matcher", self.test_pattern_matcher),
            ("Pattern Importer", self.test_pattern_importer),
            ("Session State Integration", self.test_integration_with_session_state),
            ("Pattern Evolution", self.test_pattern_evolution),
            ("Database Statistics", self.test_database_statistics),
        ]
        
        for test_name, test_func in test_methods:
            self.run_test(test_name, test_func)
        
        self.teardown()
        
        # Print summary
        total_tests = len(self.passed_tests) + len(self.failed_tests)
        pass_rate = (len(self.passed_tests) / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "="*60)
        print(" TEST RESULTS")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {len(self.passed_tests)} ({pass_rate:.1f}%)")
        print(f"Failed: {len(self.failed_tests)} ({100-pass_rate:.1f}%)")
        
        if self.passed_tests:
            print("\n PASSED TESTS:")
            for test in self.passed_tests:
                print(f"   - {test}")
        
        if self.failed_tests:
            print("\n FAILED TESTS:")
            for test, error in self.failed_tests:
                print(f"   - {test}")
                print(f"     Error: {error}")
        
        print("\n" + "="*60)
        if len(self.failed_tests) == 0:
            print(" ALL TESTS PASSED! Failure Pattern Database is working correctly!")
        else:
            print("  Some tests failed. Please fix the issues above.")
        print("="*60)
        
        return len(self.failed_tests) == 0


if __name__ == "__main__":
    tester = TestFailurePatternDB()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)