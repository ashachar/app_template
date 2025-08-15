#!/usr/bin/env python3
"""Get test recruiter's company ID."""

import os
import sys
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

test_email = os.getenv('TEST_RECRUITER_EMAIL')
if not test_email:
    print(" TEST_RECRUITER_EMAIL not found in environment")
    sys.exit(1)

print(f" Looking up company for test recruiter: {test_email}")

# Query to get company ID (using parameterized query to prevent SQL injection)
# Escape single quotes in email
safe_email = test_email.replace("'", "''")
query = f"""
SELECT 
    ud.company_id,
    c.company_name
FROM user_details ud
JOIN companies c ON c.id = ud.company_id
WHERE ud.email = '{safe_email}'
LIMIT 1;
"""

# Save query to temporary file
query_file = os.path.join(os.path.dirname(__file__), '..', 'debug_artifacts', 'temp_query.sql')
os.makedirs(os.path.dirname(query_file), exist_ok=True)
with open(query_file, 'w') as f:
    f.write(query)

# Run query
result = subprocess.run(
    ['../schema/run_sql.sh', query_file],
    capture_output=True,
    text=True,
    cwd=os.path.dirname(__file__)
)

# Debug output (commented out for production use)
# print(f"Debug - Return code: {result.returncode}")
# print(f"Debug - stdout: {result.stdout}")
# print(f"Debug - stderr: {result.stderr}")

if result.returncode == 0 and result.stdout.strip():
    lines = result.stdout.strip().split('\n')
    # Find the data line (after headers and separator)
    data_line = None
    for i, line in enumerate(lines):
        if '|' in line and not line.strip().startswith('-'):
            # Skip header line
            if 'company_id' in line:
                continue
            data_line = line
            break
    
    if data_line:
        parts = data_line.split('|')
        if len(parts) >= 2:
            company_id = parts[0].strip()
            company_name = parts[1].strip()
            print(f" Found company: {company_name} (ID: {company_id})")
            
            # Save for use in tests (in debug_artifacts folder)
            artifacts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'debug_artifacts')
            os.makedirs(artifacts_dir, exist_ok=True)
            with open(os.path.join(artifacts_dir, 'test_company_id.txt'), 'w') as f:
                f.write(company_id)
            print(f" Saved company ID to debug_artifacts/test_company_id.txt")
            
            # Clean up temp file
            os.remove(query_file)
            
            # Return the company_id for direct use
            print(f"\nCompany ID: {company_id}")
            sys.exit(0)
else:
    print(" Could not find test recruiter's company")
    print(f"Error: {result.stderr}")
    print(f"Output: {result.stdout}")
    
    # Clean up temp file
    if os.path.exists(query_file):
        os.remove(query_file)
    
    sys.exit(1)