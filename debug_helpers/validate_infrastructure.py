#!/usr/bin/env python3
"""
Quick validation script to ensure debug infrastructure is operational.
Run this before any debugging session to verify everything works.
"""

import os
import sys
import json
from pathlib import Path

def check_component(name, check_func):
    """Check a component and report status."""
    try:
        check_func()
        print(f" {name}")
        return True
    except Exception as e:
        print(f" {name}: {str(e)}")
        return False

def check_python_analyzer():
    """Verify Python analyzer can be imported and initialized."""
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from debug_helpers.analyze_logs import LogAnalyzer
    analyzer = LogAnalyzer()
    assert analyzer.patterns is not None
    assert len(analyzer.patterns) > 0

def check_js_analyzer():
    """Verify JavaScript analyzer exists."""
    js_path = Path(__file__).parent / 'log_analyzer.cjs'
    assert js_path.exists(), f"JS analyzer not found at {js_path}"
    
    # Check it's not empty
    assert js_path.stat().st_size > 1000, "JS analyzer file too small"

def check_patterns():
    """Verify error patterns are valid."""
    patterns_path = Path(__file__).parent / 'patterns' / 'error_patterns.json'
    assert patterns_path.exists(), f"Patterns file not found at {patterns_path}"
    
    with open(patterns_path, 'r') as f:
        patterns = json.load(f)
    
    assert len(patterns) >= 10, f"Too few patterns: {len(patterns)}"
    
    # Check each pattern has required fields
    for name, pattern in patterns.items():
        assert "patterns" in pattern, f"Missing 'patterns' in {name}"
        assert "category" in pattern, f"Missing 'category' in {name}"
        assert "severity" in pattern, f"Missing 'severity' in {name}"
        assert "suggestions" in pattern, f"Missing 'suggestions' in {name}"

def check_shell_script():
    """Verify shell script exists and is executable."""
    script_path = Path(__file__).parent / 'debug_with_analysis.sh'
    assert script_path.exists(), f"Shell script not found at {script_path}"
    assert os.access(str(script_path), os.X_OK), "Shell script not executable"

def check_test_infrastructure():
    """Verify test files exist."""
    test_dir = Path(__file__).parent.parent / 'tests' / 'debug_infrastructure'
    assert test_dir.exists(), f"Test directory not found at {test_dir}"
    
    required_tests = [
        'test_debug_infrastructure.py',
        'test_real_world_scenarios.py',
        'run_all_tests.sh'
    ]
    
    for test_file in required_tests:
        test_path = test_dir / test_file
        assert test_path.exists(), f"Test file not found: {test_file}"

def main():
    """Run all validation checks."""
    print(" Validating Debug Infrastructure...")
    print("=" * 50)
    
    checks = [
        ("Python Analyzer", check_python_analyzer),
        ("JavaScript Analyzer", check_js_analyzer),
        ("Error Patterns", check_patterns),
        ("Shell Script", check_shell_script),
        ("Test Infrastructure", check_test_infrastructure)
    ]
    
    passed = 0
    for name, check_func in checks:
        if check_component(name, check_func):
            passed += 1
    
    print("=" * 50)
    
    if passed == len(checks):
        print(f" All {len(checks)} components validated successfully!")
        print("\n Debug infrastructure is ready to use:")
        print("   - Run: python debug_helpers/analyze_logs.py")
        print("   - Or: ./debug_helpers/debug_with_analysis.sh")
        return 0
    else:
        print(f" {len(checks) - passed} components failed validation")
        print("\n  Fix the issues before using debug infrastructure")
        print("   Run full tests: ./tests/debug_infrastructure/run_all_tests.sh")
        return 1

if __name__ == "__main__":
    sys.exit(main())