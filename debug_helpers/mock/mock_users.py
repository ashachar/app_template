#!/usr/bin/env python3
"""
Mock users creator following schema constraints.
"""

import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from debug_helpers.mock.base_mock import BaseMockCreator


class MockUsersCreator(BaseMockCreator):
    """Creates mock users following schema constraints."""
    
    def analyze_schema_requirements(self) -> Dict[str, Any]:
        """
        Analyze schema files to understand requirements.
        
        From user_details.sql:
        - user_id uuid (FK to auth.users)
        - name text
        - email text
        - phone_number text
        - role varchar(10) DEFAULT 'seeker' (seeker or hunter)
        - company_id uuid (FK to companies)
        - linkedin text
        - etc.
        
        Note: Creating auth.users requires Supabase Auth API
        """
        print(f"[SCHEMA] Analyzing user_details table requirements...")
        
        requirements = {
            'user_details': {
                'required_fields': ['user_id'],
                'optional_fields': [
                    'name', 'email', 'phone_number',
                    'role', 'company_id', 'linkedin', 'location'
                ],
                'foreign_keys': {
                    'user_id': 'auth.users.id',
                    'company_id': 'companies.id'
                },
                'constraints': {
                    'auth': 'Must create auth.users entry first via Supabase Auth',
                    'roles': ['seeker', 'hunter']  # seeker = job seeker, hunter = recruiter
                }
            }
        }
        
        return requirements
    
    def create_mock_records(self, count: int = 1, role: str = 'seeker', company_id: Optional[str] = None, **kwargs) -> List[str]:
        """
        Create mock users.
        
        Args:
            count: Number of users to create
            role: User role (seeker, hunter)
            company_id: Company ID for hunters/recruiters (optional)
        """
        print(f"[MOCK] Creating {count} mock {role} users...")
        
        created_ids = []
        
        for i in range(count):
            # Step 1: Create auth user via Supabase Auth
            email = self.generate_mock_email(f"{role}{i+1}")
            password = f"Test@{self.test_id}123!"  # Strong password for testing
            
            try:
                # Create auth user
                print(f"[MOCK] Creating auth user: {email}")
                auth_result = self.supabase.auth.sign_up({
                    "email": email,
                    "password": password
                })
                
                if auth_result.user:
                    user_id = auth_result.user.id
                    
                    # Step 2: Create user_details entry
                    user_details_data = {
                        'user_id': user_id,
                        'name': f"{self.mock_prefix}User {i+1}",
                        'email': email,
                        'phone_number': self.generate_mock_phone(),
                        'role': role,
                        'linkedin': f"https://linkedin.com/in/{self.mock_prefix.lower()}user{i+1}",
                        'location': 'Tel Aviv, Israel'
                    }
                    
                    # Add company_id for hunters (recruiters)
                    if role == 'hunter' and company_id:
                        user_details_data['company_id'] = company_id
                    elif role == 'hunter' and not company_id:
                        # Try to get existing company
                        current_user = self.get_current_user()
                        if current_user:
                            current_details = self.get_user_details(current_user['id'])
                            if current_details and current_details.get('company_id'):
                                user_details_data['company_id'] = current_details['company_id']
                    
                    details_result = self.supabase.table('user_details').insert(user_details_data).execute()
                    
                    if details_result.data:
                        created_ids.append(user_id)
                        self.track_created_record('user_details', user_id)
                        self.track_created_record('auth_users', user_id)  # Track for cleanup
                        print(f"[MOCK] Created {role} user {i+1}: {user_id}")
                        print(f"[MOCK]   Email: {email}")
                        print(f"[MOCK]   Password: {password}")
                    else:
                        print(f"[MOCK] Failed to create user_details for {email}")
                else:
                    print(f"[MOCK] Failed to create auth user: {email}")
                    
            except Exception as e:
                print(f"[MOCK] Error creating user {i+1}: {str(e)}")
                # Check if it's a duplicate email error
                if "already been registered" in str(e):
                    print(f"[MOCK] Email {email} already exists - skipping")
        
        return created_ids
    
    def get_cleanup_queries(self) -> List[str]:
        """Generate SQL queries to clean up all created mock data."""
        queries = []
        
        # Delete user_details first (respects FK constraint)
        if 'user_details' in self.created_records and self.created_records['user_details']:
            user_ids = "', '".join(self.created_records['user_details'])
            queries.append(f"DELETE FROM user_details WHERE user_id IN ('{user_ids}');")
        
        # Note: Deleting from auth.users requires service role or Auth Admin API
        if 'auth_users' in self.created_records and self.created_records['auth_users']:
            user_ids = "', '".join(self.created_records['auth_users'])
            queries.append(f"-- NOTE: Deleting auth users requires service role or Auth Admin API")
            queries.append(f"-- DELETE FROM auth.users WHERE id IN ('{user_ids}');")
        
        # Also clean by prefix as backup
        queries.append(f"DELETE FROM user_details WHERE email LIKE '{self.mock_prefix}%@mock-test.example.com';")
        
        return queries
    
    def verify_created_records(self) -> Dict[str, Any]:
        """Verify that all created records exist in the database."""
        verification_results = {
            'verified_count': 0,
            'missing_records': [],
            'details': {}
        }
        
        if 'user_details' in self.created_records and self.created_records['user_details']:
            print(f"\n[VERIFY] Checking {len(self.created_records['user_details'])} users...")
            
            for user_id in self.created_records['user_details']:
                try:
                    # Verify user_details entry
                    result = self.supabase.table('user_details')\
                        .select('*, companies!company_id(company_name)')\
                        .eq('user_id', user_id)\
                        .single()\
                        .execute()
                    
                    if result.data:
                        verification_results['verified_count'] += 1
                        verification_results['details'][user_id] = {
                            'exists': True,
                            'name': result.data.get('name'),
                            'email': result.data.get('email'),
                            'role': result.data.get('role'),
                            'company': result.data.get('companies', {}).get('company_name', 'N/A')
                        }
                        print(f"   User {user_id[:8]}... verified")
                        print(f"     Name: {result.data.get('name')}")
                        print(f"     Role: {result.data.get('role')}")
                        if result.data.get('company_id'):
                            print(f"     Company: {result.data.get('companies', {}).get('company_name', 'N/A')}")
                    else:
                        verification_results['missing_records'].append(user_id)
                        print(f"   User {user_id[:8]}... NOT FOUND in user_details")
                    
                    # Also check auth.users (requires admin access, so we'll check if we can authenticate)
                    if 'auth_users' in self.created_records and user_id in self.created_records['auth_users']:
                        print(f"     Auth user created but verification requires admin access")
                        
                except Exception as e:
                    print(f"    Error verifying {user_id[:8]}...: {str(e)}")
                    verification_results['missing_records'].append(user_id)
        
        return verification_results
    
    def create_seeker_with_resume(self, **kwargs) -> Optional[str]:
        """
        Create a seeker (job candidate) user with a complete resume.
        This is a specialized method for testing seeker features.
        """
        print(f"[MOCK] Creating seeker with resume...")
        
        # Create the seeker user
        user_ids = self.create_mock_records(count=1, role='seeker')
        
        if not user_ids:
            print("[MOCK] Failed to create seeker user")
            return None
        
        user_id = user_ids[0]
        
        # Create resume data (would be in candidates table)
        resume_data = {
            'user_id': user_id,
            'resume_json': {
                'personal': {
                    'name': f"{self.mock_prefix}Test Seeker",
                    'email': self.generate_mock_email('seeker'),
                    'phone': self.generate_mock_phone()
                },
                'experience': [
                    {
                        'title': 'Senior Developer',
                        'company': 'Mock Tech Corp',
                        'duration': '2020-2023',
                        'description': 'Led development team'
                    }
                ],
                'education': [
                    {
                        'degree': 'B.Sc Computer Science',
                        'institution': 'Mock University',
                        'year': '2019'
                    }
                ],
                'skills': ['Python', 'JavaScript', 'React', 'Node.js']
            },
            'created_at': datetime.now().isoformat()
        }
        
        try:
            result = self.supabase.table('candidates').insert(resume_data).execute()
            if result.data:
                self.track_created_record('candidates', user_id)
                print(f"[MOCK] Created seeker with resume: {user_id}")
                return user_id
        except Exception as e:
            print(f"[MOCK] Error creating seeker resume: {str(e)}")
        
        return user_id


def main():
    """Example usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Create mock users')
    parser.add_argument('--test-id', required=True, help='Test ID for tracking')
    parser.add_argument('--count', type=int, default=1, help='Number of users to create')
    parser.add_argument('--role', choices=['seeker', 'hunter'], 
                       default='seeker', help='User role (seeker=job seeker, hunter=recruiter)')
    parser.add_argument('--company-id', help='Company ID for hunters/recruiters')
    parser.add_argument('--with-resume', action='store_true', 
                       help='Create seeker with complete resume')
    parser.add_argument('--cleanup-only', action='store_true', help='Only show cleanup queries')
    
    args = parser.parse_args()
    
    creator = MockUsersCreator(args.test_id)
    
    if args.cleanup_only:
        queries = creator.get_cleanup_queries()
        print("Cleanup queries:")
        for q in queries:
            print(f"  {q}")
    else:
        if args.with_resume and args.role == 'seeker':
            # Create seeker with resume
            user_id = creator.create_seeker_with_resume()
            if user_id:
                print(f"\n Created seeker with resume: {user_id}")
        else:
            # Create regular users
            result = creator.create_all_mock_data(
                count=args.count, 
                role=args.role,
                company_id=args.company_id
            )
            print(f"\n Mock users process completed")
        
        print(f" To clean up later, run: python {__file__} --test-id {args.test_id} --cleanup-only")


if __name__ == "__main__":
    main()