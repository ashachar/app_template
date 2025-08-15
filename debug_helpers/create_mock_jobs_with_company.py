#!/usr/bin/env python3
"""
Unified script to create mock jobs for testing.
Automatically fetches test recruiter's company and creates mock data.

Usage:
    python debug_helpers/create_mock_jobs_with_company.py [session_id] [count]
    
Example:
    python debug_helpers/create_mock_jobs_with_company.py BULK123 5
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from debug_helpers.mock.mock_requisitions import MockRequisitionsCreator


def get_test_company_id():
    """Get test recruiter's company ID."""
    print(" Getting test recruiter's company...")
    
    # Run the helper script
    result = subprocess.run(
        ['python', 'debug_helpers/get_test_recruiter_company.py'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f" Failed to get company ID: {result.stderr}")
        sys.exit(1)
    
    # Read the saved company ID
    company_file = Path('debug_artifacts/test_company_id.txt')
    if not company_file.exists():
        print(" Company ID file not found")
        sys.exit(1)
        
    with open(company_file, 'r') as f:
        company_id = f.read().strip()
        
    return company_id


def create_mock_jobs(session_id, count=5, company_id=None):
    """Create mock jobs with the given parameters."""
    
    # Get company ID if not provided
    if not company_id:
        company_id = get_test_company_id()
    
    print(f"\n Using company ID: {company_id}")
    print(f" Creating {count} mock jobs...")
    print(f" Session: {session_id}")
    print(f"⏰ Time: {datetime.now().isoformat()}\n")
    
    # Initialize mock creator
    creator = MockRequisitionsCreator(session_id)
    
    # Create mock data with the company ID
    result = creator.create_all_mock_data(count=count, company_id=company_id)
    
    if not result or 'created_ids' not in result or len(result['created_ids']) == 0:
        print(" Failed to create mock jobs")
        return None
        
    print(f"\n Successfully created {len(result['created_ids'])} mock jobs")
    print("\n Created job IDs:")
    for job_id in result['created_ids']:
        print(f"  - {job_id}")
    
    # Save IDs and cleanup info
    output_data = {
        'session_id': session_id,
        'created_at': datetime.now().isoformat(),
        'company_id': company_id,
        'job_ids': result['created_ids'],
        'cleanup_queries': result.get('cleanup_queries', []),
        'mock_prefix': result.get('mock_prefix', f'MOCK_{session_id}_')
    }
    
    # Ensure debug_artifacts directory exists
    Path('debug_artifacts').mkdir(exist_ok=True)
    
    output_file = f'debug_artifacts/mock_job_ids_{session_id}.json'
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n Mock job IDs saved to: {output_file}")
    print(" These jobs are now visible in the UI for testing")
    print("\n Cleanup queries have been saved for later use")
    
    return output_data


def main():
    """Main entry point."""
    # Get arguments
    session_id = sys.argv[1] if len(sys.argv) > 1 else f"TEST{datetime.now().strftime('%H%M%S')}"
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    print("="*60)
    print("Mock Job Creation Utility")
    print("="*60)
    
    # Create mock jobs
    result = create_mock_jobs(session_id, count)
    
    if result:
        print("\n Mock data creation completed successfully!")
        print(f"Session ID: {session_id}")
        print(f"Total jobs created: {len(result['job_ids'])}")
    else:
        print("\n Mock data creation failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()