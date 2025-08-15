#!/usr/bin/env python3
"""
Mock candidate-requisition matches creator following schema constraints.
Creates matches for Hunt page testing.
"""

import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime
import random
import uuid

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from debug_helpers.mock.base_mock import BaseMockCreator


class MockMatchesCreator(BaseMockCreator):
    """Creates mock candidate-requisition matches for Hunt page testing."""
    
    def analyze_schema_requirements(self) -> Dict[str, Any]:
        """
        Analyze schema files to understand requirements.
        
        From candidate_requisition_matches.sql:
        - requisition_id uuid NOT NULL (FK to requisitions)
        - candidate_id text NOT NULL (FK to candidates.id)
        - candidate_source text NOT NULL ('internal', 'external', 'candidates')
        - total_score numeric(4,3) NOT NULL (0-1)
        - skills_score numeric(4,3) NOT NULL (0-1)
        - experience_score numeric(4,3) NOT NULL (0-1)
        - title_score numeric(4,3) NOT NULL (0-1)
        - location_score numeric(4,3) NOT NULL (0-1)
        - matching_skills text[]
        - missing_required_skills text[]
        - best_matching_title text
        - match_details jsonb
        """
        print(f"[SCHEMA] Analyzing candidate_requisition_matches table requirements...")
        
        requirements = {
            'candidate_requisition_matches': {
                'required_fields': [
                    'requisition_id', 'candidate_id', 'candidate_source',
                    'total_score', 'skills_score', 'experience_score',
                    'title_score', 'location_score'
                ],
                'optional_fields': [
                    'matching_skills', 'missing_required_skills',
                    'best_matching_title', 'match_details'
                ],
                'foreign_keys': {
                    'requisition_id': 'requisitions.id',
                    'candidate_id': 'candidates.id'
                },
                'constraints': {
                    'candidate_source': ['internal', 'external', 'candidates'],
                    'scores': 'All scores must be between 0 and 1',
                    'prerequisite': 'Must have existing requisitions and candidates'
                }
            }
        }
        
        return requirements
    
    def generate_match_scores(self, index: int) -> Dict[str, float]:
        """Generate realistic match scores for a candidate."""
        # Create varied but realistic scores
        base_score = 0.7 + (index % 3) * 0.1  # 0.7, 0.8, or 0.9
        
        scores = {
            'skills_score': round(base_score + random.uniform(-0.1, 0.1), 3),
            'experience_score': round(base_score + random.uniform(-0.15, 0.05), 3),
            'title_score': round(base_score + random.uniform(-0.05, 0.15), 3),
            'location_score': round(0.8 + random.uniform(0, 0.2), 3),  # Usually high
        }
        
        # Ensure all scores are within bounds
        for key in scores:
            scores[key] = max(0.0, min(1.0, scores[key]))
        
        # Calculate total score as weighted average
        scores['total_score'] = round(
            scores['skills_score'] * 0.4 +
            scores['experience_score'] * 0.3 +
            scores['title_score'] * 0.2 +
            scores['location_score'] * 0.1,
            3
        )
        
        return scores
    
    def generate_skills_match(self, index: int) -> Dict[str, List[str]]:
        """Generate matching and missing skills for a candidate."""
        all_skills = [
            'Python', 'JavaScript', 'React', 'Node.js', 'TypeScript',
            'AWS', 'Docker', 'Kubernetes', 'PostgreSQL', 'MongoDB',
            'Git', 'CI/CD', 'Agile', 'REST APIs', 'GraphQL',
            'Redis', 'RabbitMQ', 'Elasticsearch', 'Jenkins', 'Terraform'
        ]
        
        # Number of matching skills varies by candidate
        num_matching = 5 + (index % 5)
        num_missing = max(0, 3 - (index % 4))
        
        matching_skills = random.sample(all_skills[:15], num_matching)
        missing_skills = random.sample(all_skills[15:], num_missing)
        
        return {
            'matching_skills': matching_skills,
            'missing_required_skills': missing_skills
        }
    
    def generate_match_details(self, scores: Dict[str, float], skills: Dict[str, List[str]]) -> Dict[str, Any]:
        """Generate detailed match information."""
        return {
            'score_breakdown': {
                'skills': {
                    'score': scores['skills_score'],
                    'matched': len(skills['matching_skills']),
                    'required': len(skills['matching_skills']) + len(skills['missing_required_skills'])
                },
                'experience': {
                    'score': scores['experience_score'],
                    'years_matched': True,
                    'industry_match': 'partial'
                },
                'title': {
                    'score': scores['title_score'],
                    'exact_match': scores['title_score'] > 0.9
                },
                'location': {
                    'score': scores['location_score'],
                    'same_city': scores['location_score'] > 0.9
                }
            },
            'generated_at': datetime.now().isoformat(),
            'algorithm_version': '1.2.0'
        }
    
    def create_matches_for_requisitions(self, requisition_ids: List[str], 
                                      candidates_per_req: int = 5,
                                      **kwargs) -> Dict[str, Any]:
        """
        Create candidate matches for specified requisitions.
        This is the main method for Hunt page testing.
        
        Args:
            requisition_ids: List of requisition IDs to create matches for
            candidates_per_req: Number of candidates to match per requisition
        """
        print(f"[MOCK] Creating {candidates_per_req} candidate matches for {len(requisition_ids)} requisitions...")
        
        # First, create EXTERNAL candidates (not users!)
        from debug_helpers.mock.mock_candidates import MockCandidatesCreator
        candidate_creator = MockCandidatesCreator(self.test_id, self.supabase)
        
        total_candidates = len(requisition_ids) * candidates_per_req
        candidate_ids = candidate_creator.create_mock_records(count=total_candidates)
        
        if not candidate_ids:
            print("[MOCK] Failed to create candidates")
            return {'created_ids': [], 'verification': {}}
        
        created_match_ids = []
        candidate_index = 0
        
        for req_id in requisition_ids:
            print(f"\n[MOCK] Creating matches for requisition: {req_id}")
            
            for i in range(candidates_per_req):
                if candidate_index >= len(candidate_ids):
                    break
                    
                candidate_id = candidate_ids[candidate_index]
                candidate_index += 1
                
                # Generate match data
                scores = self.generate_match_scores(i)
                skills = self.generate_skills_match(i)
                
                # Determine best matching title based on score
                titles = [
                    'Senior Full Stack Developer',
                    'Full Stack Developer', 
                    'Software Engineer',
                    'Backend Developer',
                    'Frontend Developer'
                ]
                best_title = titles[min(i, len(titles) - 1)]
                
                match_data = {
                    'requisition_id': req_id,
                    'candidate_id': candidate_id,
                    'candidate_source': 'internal',  # Matches from our platform
                    'total_score': scores['total_score'],
                    'skills_score': scores['skills_score'],
                    'experience_score': scores['experience_score'],
                    'title_score': scores['title_score'],
                    'location_score': scores['location_score'],
                    'matching_skills': skills['matching_skills'],
                    'missing_required_skills': skills['missing_required_skills'],
                    'best_matching_title': best_title,
                    'match_details': self.generate_match_details(scores, skills),
                    'created_at': datetime.now().isoformat()
                }
                
                try:
                    result = self.supabase.table('candidate_requisition_matches').insert(match_data).execute()
                    if result.data:
                        match_id = result.data[0]['id']
                        created_match_ids.append(match_id)
                        self.track_created_record('candidate_requisition_matches', match_id)
                        print(f"   Match {i+1}: Score {scores['total_score']}, {len(skills['matching_skills'])} matching skills")
                except Exception as e:
                    print(f"   Error creating match {i+1}: {str(e)}")
        
        # Return comprehensive result
        result = {
            'created_ids': {
                'matches': created_match_ids,
                'candidates': candidate_ids,
                'requisitions': requisition_ids
            },
            'verification': self.verify_created_records()
        }
        
        print(f"\n[MOCK] Created {len(created_match_ids)} matches total")
        return result
    
    def create_mock_records(self, count: int = 1, **kwargs) -> List[str]:
        """
        Create mock matches. This method requires requisition_ids.
        
        Args:
            count: Number of matches to create per requisition
            requisition_ids: List of requisition IDs (required in kwargs)
        """
        requisition_ids = kwargs.get('requisition_ids', [])
        if not requisition_ids:
            print("[MOCK] Error: requisition_ids required for creating matches")
            return []
        
        result = self.create_matches_for_requisitions(requisition_ids, candidates_per_req=count)
        return result['created_ids']['matches']
    
    def get_cleanup_queries(self) -> List[str]:
        """Generate SQL queries to clean up all created mock data."""
        queries = []
        
        # Delete matches first
        if 'candidate_requisition_matches' in self.created_records and self.created_records['candidate_requisition_matches']:
            match_ids = "', '".join(self.created_records['candidate_requisition_matches'])
            queries.append(f"DELETE FROM candidate_requisition_matches WHERE id IN ('{match_ids}');")
        
        # Note: Candidates are managed by MockCandidatesCreator, not here
        
        # Also clean by prefix as backup
        queries.append(f"DELETE FROM candidate_requisition_matches WHERE best_matching_title LIKE '{self.mock_prefix}%';")
        
        return queries
    
    def verify_created_records(self) -> Dict[str, Any]:
        """Verify that all created records exist in the database."""
        verification_results = {
            'verified_count': 0,
            'missing_records': [],
            'details': {}
        }
        
        if 'candidate_requisition_matches' in self.created_records and self.created_records['candidate_requisition_matches']:
            print(f"\n[VERIFY] Checking {len(self.created_records['candidate_requisition_matches'])} matches...")
            
            for match_id in self.created_records['candidate_requisition_matches']:
                try:
                    # Query match with related data
                    result = self.supabase.table('candidate_requisition_matches')\
                        .select('*, requisitions!requisition_id(id), candidates!candidate_id(name)')\
                        .eq('id', match_id)\
                        .single()\
                        .execute()
                    
                    if result.data:
                        verification_results['verified_count'] += 1
                        
                        verification_results['details'][match_id] = {
                            'exists': True,
                            'total_score': result.data.get('total_score'),
                            'candidate_id': result.data.get('candidate_id'),
                            'requisition_id': result.data.get('requisition_id'),
                            'matching_skills_count': len(result.data.get('matching_skills', []))
                        }
                        
                        print(f"   Match {match_id[:8]}... verified (score: {result.data.get('total_score')})")
                    else:
                        verification_results['missing_records'].append(match_id)
                        print(f"   Match {match_id[:8]}... NOT FOUND")
                except Exception as e:
                    print(f"    Error verifying {match_id[:8]}...: {str(e)}")
                    verification_results['missing_records'].append(match_id)
        
        return verification_results
    
    def create_matches_with_existing_candidates(self, requisition_ids: List[str], 
                                               candidate_ids: List[str]) -> Dict[str, Any]:
        """
        Create matches between existing requisitions and existing candidates.
        
        This is useful when you already have candidates created and just need to match them.
        
        Args:
            requisition_ids: List of existing requisition IDs
            candidate_ids: List of existing candidate IDs
            
        Returns:
            Dict with created match IDs and verification results
        """
        print(f"\n[MOCK] Creating matches between {len(requisition_ids)} requisitions and {len(candidate_ids)} candidates")
        
        created_match_ids = []
        
        for req_id in requisition_ids:
            print(f"\n[MOCK] Creating matches for requisition: {req_id}")
            
            for i, candidate_id in enumerate(candidate_ids):
                # Generate match data
                scores = self.generate_match_scores(i)
                skills_match = self.generate_skills_match(i)
                
                match_data = {
                    'id': str(uuid.uuid4()),
                    'requisition_id': req_id,
                    'candidate_id': candidate_id,
                    'candidate_source': 'external',  # External candidates from hunting
                    'total_score': scores['total_score'],
                    'skills_score': scores['skills_score'],
                    'experience_score': scores['experience_score'],
                    'title_score': scores['title_score'],
                    'location_score': scores['location_score'],
                    'matching_skills': skills_match['matching_skills'],
                    'missing_required_skills': skills_match['missing_required_skills'],
                    'best_matching_title': f"{self.mock_prefix}Senior Developer",
                    'match_details': {
                        'algorithm_version': '1.0',
                        'matched_at': datetime.now().isoformat()
                    }
                }
                
                try:
                    result = self.supabase.table('candidate_requisition_matches').insert(match_data).execute()
                    if result.data:
                        created_match_ids.append(match_data['id'])
                        self.track_created_record('candidate_requisition_matches', match_data['id'])
                        print(f"   Match {i+1}: Score {scores['total_score']}, {len(skills_match['matching_skills'])} matching skills")
                except Exception as e:
                    print(f"   Error creating match {i+1}: {str(e)}")
        
        # Return comprehensive result
        result = {
            'match_ids': created_match_ids,
            'candidate_ids': candidate_ids,
            'requisition_ids': requisition_ids,
            'verification': self.verify_created_records()
        }
        
        print(f"\n[MOCK] Created {len(created_match_ids)} matches total")
        return result


def main():
    """Example usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Create mock candidate-requisition matches')
    parser.add_argument('--test-id', required=True, help='Test ID for tracking')
    parser.add_argument('--requisitions', nargs='+', help='Requisition IDs to create matches for')
    parser.add_argument('--candidates-per-req', type=int, default=5, help='Number of candidates per requisition')
    parser.add_argument('--existing-candidates', nargs='+', help='Use existing candidate IDs instead of creating new ones')
    parser.add_argument('--cleanup-only', action='store_true', help='Only show cleanup queries')
    
    args = parser.parse_args()
    
    creator = MockMatchesCreator(args.test_id)
    
    if args.cleanup_only:
        queries = creator.get_cleanup_queries()
        print("Cleanup queries:")
        for q in queries:
            print(f"  {q}")
    else:
        if not args.requisitions:
            parser.error("--requisitions is required when not using --cleanup-only")
        
        if args.existing_candidates:
            # Use existing candidates
            result = creator.create_matches_with_existing_candidates(
                args.requisitions,
                args.existing_candidates
            )
            print(f"\n Mock matching process completed")
            print(f" Created {len(result['match_ids'])} matches")
        else:
            # Create new candidates and matches
            result = creator.create_matches_for_requisitions(
                args.requisitions,
                candidates_per_req=args.candidates_per_req
            )
            print(f"\n Mock matching process completed")
            print(f" Created {len(result['created_ids']['matches'])} matches")
        
        print(f" To clean up later, run: python {__file__} --test-id {args.test_id} --cleanup-only")


if __name__ == "__main__":
    main()