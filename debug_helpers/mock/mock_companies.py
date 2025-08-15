#!/usr/bin/env python3
"""
Mock companies creator following schema constraints.
"""

import os
import sys
from typing import Dict, List, Any
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from debug_helpers.mock.base_mock import BaseMockCreator


class MockCompaniesCreator(BaseMockCreator):
    """Creates mock companies following schema constraints."""
    
    def analyze_schema_requirements(self) -> Dict[str, Any]:
        """
        Analyze schema files to understand requirements.
        
        From companies.sql:
        - id uuid PRIMARY KEY
        - company_name text NOT NULL
        - company_email text
        - company_website text
        - industry text
        - company_size text
        - logo_url text
        - description text
        - etc.
        """
        print(f"[SCHEMA] Analyzing companies table requirements...")
        
        requirements = {
            'companies': {
                'required_fields': ['company_name'],
                'optional_fields': [
                    'company_email', 'company_website', 'industry',
                    'company_size', 'logo_url', 'description'
                ],
                'constraints': {
                    'RLS': 'Only service role can insert companies directly'
                }
            }
        }
        
        return requirements
    
    def create_mock_records(self, count: int = 1, **kwargs) -> List[str]:
        """
        Create mock companies.
        
        Note: Due to RLS policies, creating companies requires special permissions.
        This is typically done through the API or with service role.
        """
        print(f"[MOCK] Attempting to create {count} mock companies...")
        
        created_ids = []
        
        # Check if we have service key
        has_service_key = os.getenv('SUPABASE_SERVICE_KEY') is not None
        
        if not has_service_key:
            print("[MOCK]   No service key found - will use existing company")
            # Get test recruiter's company
            return self.get_test_recruiter_company()
        
        print("[MOCK]  Service key found - creating companies with elevated permissions")
        
        for i in range(count):
            company_data = {
                'company_name': f"{self.mock_prefix}Test Company {i+1}",
                'company_description': f"Mock company created for testing purposes - {self.test_id}",
                'company_homepage': self.generate_mock_url(f"company{i+1}"),
                'logo_url': f"https://placeholder.com/logo_{i+1}.png"
            }
            
            try:
                # Attempt to insert with service key
                result = self.supabase.table('companies').insert(company_data).execute()
                if result.data:
                    company_id = result.data[0]['id']
                    created_ids.append(company_id)
                    self.track_created_record('companies', company_id)
                    print(f"[MOCK]  Created company {i+1}: {company_id}")
            except Exception as e:
                print(f"[MOCK]  Failed to create company {i+1}: {str(e)}")
                # If we can't create companies, use existing one
                if not created_ids:
                    return self.get_test_recruiter_company()
        
        return created_ids
    
    def get_test_recruiter_company(self) -> List[str]:
        """Get the test recruiter's existing company ID."""
        try:
            # Get test recruiter email from env
            test_email = os.getenv('TEST_RECRUITER_EMAIL')
            if not test_email:
                print("[MOCK] No TEST_RECRUITER_EMAIL found in env")
                return []
            
            # Query user details to get company
            result = self.supabase.table('user_details')\
                .select('company_id')\
                .eq('email', test_email)\
                .single()\
                .execute()
            
            if result.data and result.data.get('company_id'):
                company_id = result.data['company_id']
                print(f"[MOCK] Using test recruiter's company: {company_id}")
                return [company_id]
            else:
                print("[MOCK] Could not find test recruiter's company")
                return []
                
        except Exception as e:
            print(f"[MOCK] Error getting test recruiter company: {str(e)}")
            return []
    
    def get_cleanup_queries(self) -> List[str]:
        """Generate SQL queries to clean up all created mock data."""
        queries = []
        
        if 'companies' in self.created_records and self.created_records['companies']:
            comp_ids = "', '".join(self.created_records['companies'])
            queries.append(f"DELETE FROM companies WHERE id IN ('{comp_ids}');")
        
        # Also clean by prefix as backup
        queries.append(f"DELETE FROM companies WHERE company_name LIKE '{self.mock_prefix}%';")
        
        return queries
    
    def verify_created_records(self) -> Dict[str, Any]:
        """Verify that all created records exist in the database."""
        verification_results = {
            'verified_count': 0,
            'missing_records': [],
            'details': {}
        }
        
        if 'companies' in self.created_records and self.created_records['companies']:
            print(f"\n[VERIFY] Checking {len(self.created_records['companies'])} companies...")
            
            for company_id in self.created_records['companies']:
                try:
                    result = self.supabase.table('companies')\
                        .select('*')\
                        .eq('id', company_id)\
                        .single()\
                        .execute()
                    
                    if result.data:
                        verification_results['verified_count'] += 1
                        verification_results['details'][company_id] = {
                            'exists': True,
                            'name': result.data.get('company_name'),
                            'homepage': result.data.get('company_homepage')
                        }
                        print(f"   Company {company_id[:8]}... verified")
                        print(f"     Name: {result.data.get('company_name')}")
                    else:
                        verification_results['missing_records'].append(company_id)
                        print(f"   Company {company_id[:8]}... NOT FOUND")
                except Exception as e:
                    print(f"    Error verifying {company_id[:8]}...: {str(e)}")
                    verification_results['missing_records'].append(company_id)
        else:
            # If no companies were created, check if we used an existing one
            print("[VERIFY] No companies created (expected due to RLS)")
        
        return verification_results


def main():
    """Example usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Create mock companies')
    parser.add_argument('--test-id', required=True, help='Test ID for tracking')
    parser.add_argument('--count', type=int, default=1, help='Number of companies to create')
    parser.add_argument('--cleanup-only', action='store_true', help='Only show cleanup queries')
    
    args = parser.parse_args()
    
    creator = MockCompaniesCreator(args.test_id)
    
    if args.cleanup_only:
        queries = creator.get_cleanup_queries()
        print("Cleanup queries:")
        for q in queries:
            print(f"  {q}")
    else:
        result = creator.create_all_mock_data(count=args.count)
        
        print(f"\n Mock companies process completed")
        print(f" To clean up later, run: python {__file__} --test-id {args.test_id} --cleanup-only")


if __name__ == "__main__":
    main()