#!/usr/bin/env python3
"""
Mock requisitions creator following schema constraints.
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from debug_helpers.mock.base_mock import BaseMockCreator


class MockRequisitionsCreator(BaseMockCreator):
    """Creates mock requisitions following schema constraints."""
    
    def __init__(self, test_id: str, supabase_client=None):
        super().__init__(test_id, supabase_client)
        # Additional initialization specific to requisitions if needed
    
    def analyze_schema_requirements(self):
        """
        STEP 1: Analyze schema files to understand requirements.
        
        Example analysis for requisitions:
        - requisitions.sql shows:
          - company_id uuid NOT NULL (FK to companies)
          - title_id uuid (FK to requisition_titles)
          - department text (but also department_id uuid)
          - employment_type integer
          - work_arrangement_type integer
          - is_deleted boolean DEFAULT false
          - is_public boolean DEFAULT false
          - source integer DEFAULT 2 NOT NULL
          
        - requisition_titles.sql shows:
          - requisition_id uuid (FK to requisitions)
          - english text
          - hebrew text
          
        - Foreign key order: companies -> requisitions -> requisition_titles
        """
        print(f"[SCHEMA] Analyzing schema requirements for requisitions...")
        
        # Document the schema requirements
        requirements = {
            'requisitions': {
                'required_fields': ['company_id', 'source'],
                'defaults': {'is_deleted': False, 'is_public': False, 'source': 1},  # source MUST be 1 for recruiter inserts
                'foreign_keys': {'company_id': 'companies.id'},
                'lookups': {
                    'employment_type': 'Integer index (1=Full-time, 2=Part-time, etc)',
                    'work_arrangement_type': 'Integer index (1=Office, 2=Remote, 3=Hybrid)'
                }
            },
            'requisition_titles': {
                'required_fields': ['requisition_id', 'english', 'hebrew'],
                'foreign_keys': {'requisition_id': 'requisitions.id'}
            }
        }
        
        return requirements
    
    def get_or_create_company(self) -> str:
        """Get existing company or create a mock one if allowed."""
        print(f"[MOCK] Checking for existing company...")
        
        # First, try to use the get_test_recruiter_company.py script
        import subprocess
        
        script_path = os.path.join(os.path.dirname(__file__), '..', 'get_test_recruiter_company.py')
        
        try:
            # Run the script to get company ID
            result = subprocess.run(
                ['python', script_path],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(script_path)
            )
            
            if result.returncode == 0:
                # Extract company ID from output
                output_lines = result.stdout.strip().split('\n')
                for line in output_lines:
                    if line.startswith('Company ID:'):
                        company_id = line.replace('Company ID:', '').strip()
                        print(f"[MOCK] Found test recruiter's company: {company_id}")
                        return company_id
                
                # Also check if it was saved to file
                artifacts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'debug_artifacts')
                company_file = os.path.join(artifacts_dir, 'test_company_id.txt')
                if os.path.exists(company_file):
                    with open(company_file, 'r') as f:
                        company_id = f.read().strip()
                        print(f"[MOCK] Using saved company ID: {company_id}")
                        return company_id
            else:
                print(f"[MOCK] Failed to get company from script: {result.stderr}")
                
        except Exception as e:
            print(f"[MOCK] Error running get_test_recruiter_company.py: {str(e)}")
        
        # Fallback: Check if user already has a company
        user = self.supabase.auth.get_user()
        if user and user.user:
            user_details = self.supabase.table('user_details')\
                .select('company_id, role')\
                .eq('user_id', user.user.id)\
                .single()\
                .execute()
            
            if user_details.data and user_details.data.get('company_id'):
                print(f"[MOCK] Using existing company: {user_details.data['company_id']}")
                print(f"[MOCK] User role: {user_details.data.get('role', 'unknown')}")
                return user_details.data['company_id']
        
        # If no existing company, we can't create one due to RLS
        # This would need to be done through proper API or with service role
        print("[MOCK] No existing company found. Users cannot create companies due to RLS.")
        print("[MOCK] Please ensure TEST_RECRUITER_EMAIL is set in .env and the user has a company.")
        
        # For testing purposes, we'll need to use an existing company
        # In a real scenario, company creation would be done through the proper API
        raise Exception("Cannot create companies due to RLS. Please ensure TEST_RECRUITER_EMAIL is set in .env and the test user has a company.")
    
    def create_mock_records(self, count: int = 3, company_id: Optional[str] = None, **kwargs) -> List[str]:
        """Create mock requisitions following schema constraints."""
        print(f"[MOCK] Creating {count} mock requisitions...")
        
        # Use provided company_id or get existing one
        if company_id:
            print(f"[MOCK] Using provided company ID: {company_id}")
        else:
            # Get or create company
            company_id = self.get_or_create_company()
        
        created_ids = []
        
        for i in range(count):
            # Create requisition with required fields
            requisition_data = {
                'company_id': company_id,
                'source': 1,  # MUST BE 1 for recruiters to insert (RLS policy)
                'is_deleted': False,
                'is_public': True,  # Make visible for testing
                'is_published': True,  # Also make published
                'employment_type': 1,  # Full-time
                'work_arrangement_type': 3,  # Hybrid
                'min_years_of_experience': 2,
                'max_years_of_experience': 5,
                'posting_date': datetime.now().isoformat(),
                'min_salary': 100000,
                'max_salary': 150000
            }
            
            try:
                result = self.supabase.table('requisitions').insert(requisition_data).execute()
                if result.data:
                    req_id = result.data[0]['id']
                    
                    # First create the title record
                    title_data = {
                        'english': f"{self.mock_prefix}Developer Position {i+1}",
                        'hebrew': f"{self.mock_prefix}משרת מפתח {i+1}"
                    }
                    
                    title_result = self.supabase.table('requisition_titles').insert(title_data).execute()
                    if title_result.data:
                        title_id = title_result.data[0]['id']
                        
                        # Update requisition with title_id
                        update_result = self.supabase.table('requisitions')\
                            .update({'title_id': title_id})\
                            .eq('id', req_id)\
                            .execute()
                        
                        if update_result.data:
                            created_ids.append(req_id)
                            self.track_created_record('requisitions', req_id)
                            self.track_created_record('requisition_titles', title_id)
                            print(f"[MOCK] Created requisition {i+1}: {req_id} with title: {title_id}")
                        else:
                            print(f"[MOCK] Failed to update requisition with title_id")
                    
            except Exception as e:
                print(f"[MOCK] Error creating requisition {i+1}: {str(e)}")
        
        return created_ids
    
    def get_cleanup_queries(self) -> List[str]:
        """Generate SQL queries to clean up all created mock data."""
        queries = []
        
        # Delete in reverse order of creation (respect FK constraints)
        if 'requisitions' in self.created_records and self.created_records['requisitions']:
            req_ids = "', '".join(self.created_records['requisitions'])
            # First delete requisitions (they reference titles)
            queries.append(f"DELETE FROM requisitions WHERE id IN ('{req_ids}');")
        
        if 'requisition_titles' in self.created_records and self.created_records['requisition_titles']:
            title_ids = "', '".join(self.created_records['requisition_titles'])
            queries.append(f"DELETE FROM requisition_titles WHERE id IN ('{title_ids}');")
        
        # Also clean by prefix as backup
        queries.append(f"DELETE FROM requisition_titles WHERE english LIKE '{self.mock_prefix}%';")
        
        return queries
    
    def verify_created_records(self) -> Dict[str, Any]:
        """Verify that all created records exist in the database."""
        verification_results = {
            'verified_count': 0,
            'missing_records': [],
            'details': {}
        }
        
        # Verify requisitions
        if 'requisitions' in self.created_records and self.created_records['requisitions']:
            print(f"\n[VERIFY] Checking {len(self.created_records['requisitions'])} requisitions...")
            
            for req_id in self.created_records['requisitions']:
                try:
                    # Query requisition with joins to get complete data
                    result = self.supabase.table('requisitions')\
                        .select('*, requisition_titles!title_id(english, hebrew), companies!company_id(company_name)')\
                        .eq('id', req_id)\
                        .single()\
                        .execute()
                    
                    if result.data:
                        verification_results['verified_count'] += 1
                        verification_results['details'][req_id] = {
                            'exists': True,
                            'title': result.data.get('requisition_titles', {}).get('english', 'N/A'),
                            'company': result.data.get('companies', {}).get('company_name', 'N/A'),
                            'is_public': result.data.get('is_public'),
                            'is_deleted': result.data.get('is_deleted')
                        }
                        print(f"   Requisition {req_id[:8]}... verified")
                        print(f"     Title: {result.data.get('requisition_titles', {}).get('english', 'N/A')}")
                    else:
                        verification_results['missing_records'].append(req_id)
                        print(f"   Requisition {req_id[:8]}... NOT FOUND")
                except Exception as e:
                    print(f"    Error verifying {req_id[:8]}...: {str(e)}")
                    verification_results['missing_records'].append(req_id)
        
        # Verify requisition titles
        if 'requisition_titles' in self.created_records and self.created_records['requisition_titles']:
            print(f"\n[VERIFY] Checking {len(self.created_records['requisition_titles'])} titles...")
            
            for title_id in self.created_records['requisition_titles']:
                try:
                    result = self.supabase.table('requisition_titles')\
                        .select('*')\
                        .eq('id', title_id)\
                        .single()\
                        .execute()
                    
                    if result.data:
                        print(f"   Title {title_id[:8]}... verified: {result.data.get('english', 'N/A')}")
                except Exception as e:
                    print(f"    Error verifying title {title_id[:8]}...: {str(e)}")
        
        return verification_results
    


def main():
    """Example usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Create mock requisitions')
    parser.add_argument('--test-id', required=True, help='Test ID for tracking')
    parser.add_argument('--count', type=int, default=3, help='Number of requisitions to create')
    parser.add_argument('--cleanup-only', action='store_true', help='Only show cleanup queries')
    
    args = parser.parse_args()
    
    creator = MockRequisitionsCreator(args.test_id)
    
    if args.cleanup_only:
        # Just show cleanup queries
        queries = creator.get_cleanup_queries()
        print("Cleanup queries:")
        for q in queries:
            print(f"  {q}")
    else:
        # Create mock data
        result = creator.create_all_mock_data(count=args.count)
        
        print(f"\n Mock requisitions created")
        print(f" To clean up later, run: python {__file__} --test-id {args.test_id} --cleanup-only")


if __name__ == "__main__":
    main()