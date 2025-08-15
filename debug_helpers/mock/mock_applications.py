#!/usr/bin/env python3
"""
Mock applications creator following schema constraints.
"""

import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from debug_helpers.mock.base_mock import BaseMockCreator


class MockApplicationsCreator(BaseMockCreator):
    """Creates mock applications between candidates and requisitions."""
    
    def analyze_schema_requirements(self) -> Dict[str, Any]:
        """
        Analyze schema files to understand requirements.
        
        From applications table:
        - id uuid PRIMARY KEY
        - candidate_id uuid (FK to candidates)
        - requisition_id uuid (FK to requisitions)
        - status text
        - applied_at timestamp
        - cover_letter text
        - source text
        - etc.
        """
        print(f"[SCHEMA] Analyzing applications table requirements...")
        
        requirements = {
            'applications': {
                'required_fields': ['candidate_id', 'requisition_id'],
                'optional_fields': [
                    'status', 'applied_at', 'cover_letter', 
                    'source', 'notes', 'rating'
                ],
                'foreign_keys': {
                    'candidate_id': 'candidates.user_id',
                    'requisition_id': 'requisitions.id'
                },
                'statuses': [
                    'new', 'screening', 'interview', 
                    'offer', 'hired', 'rejected'
                ],
                'sources': [
                    'direct', 'referral', 'linkedin', 
                    'indeed', 'website'
                ]
            }
        }
        
        return requirements
    
    def create_mock_records(self, count: int = 1, 
                          candidate_ids: Optional[List[str]] = None,
                          requisition_ids: Optional[List[str]] = None,
                          **kwargs) -> List[str]:
        """
        Create mock applications.
        
        Args:
            count: Number of applications to create
            candidate_ids: List of candidate IDs to use
            requisition_ids: List of requisition IDs to apply to
        """
        print(f"[MOCK] Creating {count} mock applications...")
        
        # Get candidates if not provided
        if not candidate_ids:
            print("[MOCK] No candidate IDs provided, creating candidates first...")
            from debug_helpers.mock.mock_candidates import MockCandidatesCreator
            candidate_creator = MockCandidatesCreator(self.test_id, self.supabase)
            candidate_ids = candidate_creator.create_mock_records(count=min(count, 3))
            
            if not candidate_ids:
                print("[MOCK] Failed to create candidates")
                return []
        
        # Get requisitions if not provided
        if not requisition_ids:
            print("[MOCK] No requisition IDs provided, creating requisitions first...")
            from debug_helpers.mock.mock_requisitions import MockRequisitionsCreator
            req_creator = MockRequisitionsCreator(self.test_id, self.supabase)
            requisition_ids = req_creator.create_mock_records(count=min(count, 3))
            
            if not requisition_ids:
                print("[MOCK] Failed to create requisitions")
                return []
        
        created_ids = []
        statuses = ['new', 'screening', 'interview', 'offer', 'hired', 'rejected']
        sources = ['direct', 'referral', 'linkedin', 'indeed', 'website']
        
        # Create applications by pairing candidates with requisitions
        for i in range(count):
            # Cycle through candidates and requisitions
            candidate_id = candidate_ids[i % len(candidate_ids)]
            requisition_id = requisition_ids[i % len(requisition_ids)]
            
            # Determine status with realistic distribution
            status_weights = [30, 25, 20, 10, 5, 10]  # More new/screening, fewer hired
            status = random.choices(statuses, weights=status_weights)[0]
            
            # Create application data
            application_data = {
                'candidate_id': candidate_id,
                'requisition_id': requisition_id,
                'status': status,
                'applied_at': (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
                'source': random.choice(sources),
                'cover_letter': f"{self.mock_prefix}I am very interested in this position. My experience aligns well with the requirements...",
                'rating': random.randint(1, 5) if status != 'new' else None
            }
            
            # Add status-specific fields
            if status in ['interview', 'offer', 'hired']:
                application_data['interview_date'] = (datetime.now() + timedelta(days=random.randint(1, 14))).isoformat()
            
            if status == 'rejected':
                application_data['rejection_reason'] = random.choice([
                    'Not enough experience',
                    'Salary expectations too high',
                    'Not a cultural fit',
                    'Position filled'
                ])
            
            try:
                result = self.supabase.table('applications').insert(application_data).execute()
                if result.data:
                    app_id = result.data[0]['id']
                    created_ids.append(app_id)
                    self.track_created_record('applications', app_id)
                    print(f"[MOCK] Created application {i+1}: {app_id}")
                    print(f"[MOCK]   Candidate: {candidate_id[:8]}...")
                    print(f"[MOCK]   Requisition: {requisition_id[:8]}...")
                    print(f"[MOCK]   Status: {status}")
            except Exception as e:
                print(f"[MOCK] Error creating application {i+1}: {str(e)}")
                # Check if it's a duplicate application
                if "duplicate key" in str(e).lower():
                    print(f"[MOCK] Candidate already applied to this requisition")
        
        return created_ids
    
    def create_application_pipeline(self, requisition_id: str, num_candidates: int = 10) -> Dict[str, Any]:
        """
        Create a complete application pipeline for a requisition.
        Useful for testing recruiter dashboards and pipelines.
        """
        print(f"[MOCK] Creating application pipeline for requisition {requisition_id}...")
        
        # Create candidates
        from debug_helpers.mock.mock_candidates import MockCandidatesCreator
        candidate_creator = MockCandidatesCreator(self.test_id, self.supabase)
        candidate_ids = candidate_creator.create_mock_records(count=num_candidates)
        
        if not candidate_ids:
            print("[MOCK] Failed to create candidates for pipeline")
            return {}
        
        # Create applications with realistic status distribution
        pipeline_distribution = {
            'new': int(num_candidates * 0.3),
            'screening': int(num_candidates * 0.25),
            'interview': int(num_candidates * 0.2),
            'offer': int(num_candidates * 0.1),
            'hired': int(num_candidates * 0.05),
            'rejected': int(num_candidates * 0.1)
        }
        
        created_apps = []
        status_index = 0
        
        for status, count in pipeline_distribution.items():
            for _ in range(count):
                if status_index < len(candidate_ids):
                    app_ids = self.create_mock_records(
                        count=1,
                        candidate_ids=[candidate_ids[status_index]],
                        requisition_ids=[requisition_id]
                    )
                    if app_ids:
                        created_apps.extend(app_ids)
                        # Update the application status
                        self.supabase.table('applications')\
                            .update({'status': status})\
                            .eq('id', app_ids[0])\
                            .execute()
                    status_index += 1
        
        result = {
            'requisition_id': requisition_id,
            'total_applications': len(created_apps),
            'distribution': pipeline_distribution,
            'application_ids': created_apps
        }
        
        print(f"[MOCK] Created pipeline with {len(created_apps)} applications")
        return result
    
    def get_cleanup_queries(self) -> List[str]:
        """Generate SQL queries to clean up all created mock data."""
        queries = []
        
        if 'applications' in self.created_records and self.created_records['applications']:
            app_ids = "', '".join(self.created_records['applications'])
            queries.append(f"DELETE FROM applications WHERE id IN ('{app_ids}');")
        
        # Also clean by cover letter prefix as backup
        queries.append(f"DELETE FROM applications WHERE cover_letter LIKE '{self.mock_prefix}%';")
        
        return queries
    
    def verify_created_records(self) -> Dict[str, Any]:
        """Verify that all created records exist in the database."""
        verification_results = {
            'verified_count': 0,
            'missing_records': [],
            'details': {},
            'status_distribution': {}
        }
        
        if 'applications' in self.created_records and self.created_records['applications']:
            print(f"\n[VERIFY] Checking {len(self.created_records['applications'])} applications...")
            
            for app_id in self.created_records['applications']:
                try:
                    # Query application with related data
                    result = self.supabase.table('applications')\
                        .select('''
                            *,
                            candidates!candidate_id(
                                user_details!user_id(name, email)
                            ),
                            requisitions!requisition_id(
                                requisition_titles!title_id(english)
                            )
                        ''')\
                        .eq('id', app_id)\
                        .single()\
                        .execute()
                    
                    if result.data:
                        verification_results['verified_count'] += 1
                        
                        # Track status distribution
                        status = result.data.get('status', 'unknown')
                        verification_results['status_distribution'][status] = \
                            verification_results['status_distribution'].get(status, 0) + 1
                        
                        # Extract nested data safely
                        candidate_name = 'N/A'
                        requisition_title = 'N/A'
                        
                        try:
                            candidate_data = result.data.get('candidates', {})
                            if candidate_data and 'user_details' in candidate_data:
                                candidate_name = candidate_data['user_details'].get('name', 'N/A')
                            
                            requisition_data = result.data.get('requisitions', {})
                            if requisition_data and 'requisition_titles' in requisition_data:
                                requisition_title = requisition_data['requisition_titles'].get('english', 'N/A')
                        except:
                            pass
                        
                        verification_results['details'][app_id] = {
                            'exists': True,
                            'status': status,
                            'candidate_name': candidate_name,
                            'requisition_title': requisition_title,
                            'source': result.data.get('source'),
                            'applied_at': result.data.get('applied_at')
                        }
                        
                        print(f"   Application {app_id[:8]}... verified")
                        print(f"     Status: {status}")
                        print(f"     Candidate: {candidate_name}")
                        print(f"     Position: {requisition_title}")
                        print(f"     Source: {result.data.get('source')}")
                    else:
                        verification_results['missing_records'].append(app_id)
                        print(f"   Application {app_id[:8]}... NOT FOUND")
                except Exception as e:
                    print(f"    Error verifying {app_id[:8]}...: {str(e)}")
                    verification_results['missing_records'].append(app_id)
            
            # Print status distribution summary
            if verification_results['status_distribution']:
                print(f"\n[VERIFY] Application status distribution:")
                for status, count in verification_results['status_distribution'].items():
                    print(f"  - {status}: {count}")
        
        return verification_results


def main():
    """Example usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Create mock applications')
    parser.add_argument('--test-id', required=True, help='Test ID for tracking')
    parser.add_argument('--count', type=int, default=5, help='Number of applications to create')
    parser.add_argument('--pipeline', help='Create full pipeline for this requisition ID')
    parser.add_argument('--candidates', nargs='+', help='Specific candidate IDs')
    parser.add_argument('--requisitions', nargs='+', help='Specific requisition IDs')
    parser.add_argument('--cleanup-only', action='store_true', help='Only show cleanup queries')
    
    args = parser.parse_args()
    
    creator = MockApplicationsCreator(args.test_id)
    
    if args.cleanup_only:
        queries = creator.get_cleanup_queries()
        print("Cleanup queries:")
        for q in queries:
            print(f"  {q}")
    else:
        if args.pipeline:
            # Create full pipeline
            result = creator.create_application_pipeline(args.pipeline)
            print(f"\n Created application pipeline:")
            print(f"   Total applications: {result.get('total_applications', 0)}")
        else:
            # Create regular applications
            result = creator.create_all_mock_data(
                count=args.count,
                candidate_ids=args.candidates,
                requisition_ids=args.requisitions
            )
            print(f"\n Mock applications process completed")
        
        print(f" To clean up later, run: python {__file__} --test-id {args.test_id} --cleanup-only")


if __name__ == "__main__":
    main()