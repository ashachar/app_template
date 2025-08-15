#!/usr/bin/env python3
"""
Mock candidates creator following schema constraints.

CRITICAL: The candidates table stores EXTERNAL candidates found through hunting/scraping,
NOT users who signed up for the app! These are completely separate entities.

NEVER create users when creating candidates - they are unrelated!
"""

import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import random
import uuid

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from debug_helpers.mock.base_mock import BaseMockCreator


class MockCandidatesCreator(BaseMockCreator):
    """Creates mock EXTERNAL candidates (NOT app users!) following schema constraints."""
    
    def analyze_schema_requirements(self) -> Dict[str, Any]:
        """
        Analyze schema files to understand requirements.
        
        From candidates.sql:
        - id uuid PRIMARY KEY (auto-generated)
        - email varchar(255)
        - name varchar(255)
        - linkedin_url text
        - experience jsonb (array of experience objects)
        - education jsonb (array of education objects)
        - skills text[]
        - location varchar(255)
        - source integer (1=platform, 2=recruiter, 3=candidate)
        - NO user_id - these are NOT app users!
        """
        print(f"[SCHEMA] Analyzing candidates table requirements...")
        
        requirements = {
            'candidates': {
                'required_fields': ['id'],
                'optional_fields': [
                    'email', 'name', 'linkedin_url', 'experience',
                    'education', 'skills', 'location', 'source'
                ],
                'foreign_keys': {},  # NO foreign keys to users!
                'constraints': {
                    'note': 'These are EXTERNAL candidates, not app users!'
                }
            }
        }
        
        return requirements
    
    def generate_experience_data(self, index: int) -> List[Dict[str, Any]]:
        """Generate realistic work experience data."""
        companies = [
            'Tech Solutions Ltd', 'StartupXYZ', 'WebDev Inc', 
            'Digital Innovations', 'CloudTech Systems', 'DataCorp',
            'AI Labs', 'Mobile First', 'Enterprise Solutions'
        ]
        
        titles = [
            'Senior Full Stack Developer',
            'Full Stack Developer',
            'Software Engineer', 
            'Backend Developer',
            'Frontend Developer',
            'DevOps Engineer',
            'Tech Lead',
            'Senior Software Engineer'
        ]
        
        # Generate 2-4 experiences
        num_experiences = random.randint(2, 4)
        experiences = []
        current_year = datetime.now().year
        
        for i in range(num_experiences):
            start_year = current_year - (num_experiences - i) * 2 - random.randint(0, 1)
            end_year = start_year + random.randint(1, 3)
            if i == 0:  # Current job
                end_date = 'current'
            else:
                end_date = f"{end_year}-{random.randint(1, 12):02d}-01"
            
            exp = {
                'title': random.choice(titles),
                'company': f"{self.mock_prefix}{random.choice(companies)}",
                'location': random.choice(['Tel Aviv', 'Haifa', 'Jerusalem', 'Herzliya']),
                'start_date': f"{start_year}-{random.randint(1, 12):02d}-01",
                'end_date': end_date,
                'description': f'Developed and maintained web applications using modern technologies. {self.mock_prefix}',
                'achievements': [
                    'Reduced API response time by 40%',
                    'Led team of 3 developers',
                    'Implemented CI/CD pipeline'
                ]
            }
            experiences.append(exp)
        
        return experiences
    
    def generate_education_data(self, index: int) -> List[Dict[str, Any]]:
        """Generate realistic education data."""
        institutions = [
            'Tel Aviv University',
            'Technion - Israel Institute of Technology',
            'Hebrew University of Jerusalem',
            'Ben-Gurion University',
            'Bar-Ilan University'
        ]
        
        degrees = ['B.Sc.', 'M.Sc.', 'B.A.']
        fields = ['Computer Science', 'Software Engineering', 'Information Systems', 'Mathematics']
        
        education = [{
            'degree': random.choice(degrees),
            'field': random.choice(fields),
            'institution': random.choice(institutions),
            'graduation_date': f"{datetime.now().year - random.randint(3, 10)}-06-01",
            'gpa': f"{random.randint(80, 95)}/100"
        }]
        
        # Sometimes add a bootcamp
        if random.random() > 0.5:
            education.append({
                'degree': 'Full Stack Bootcamp',
                'field': 'Web Development',
                'institution': random.choice(['Coding Academy', 'Tech Career', 'ITC']),
                'graduation_date': f"{datetime.now().year - random.randint(1, 5)}-12-01"
            })
        
        return education
    
    def create_mock_records(self, count: int = 1, **kwargs) -> List[str]:
        """
        Create mock EXTERNAL candidates.
        
        Args:
            count: Number of candidates to create
            
        IMPORTANT: These are NOT app users - they are external candidates!
        """
        print(f"[MOCK] Creating {count} mock EXTERNAL candidates (not app users!)...")
        
        created_ids = []
        
        skills_pool = [
            'Python', 'JavaScript', 'React', 'Node.js', 'TypeScript',
            'AWS', 'Docker', 'Kubernetes', 'PostgreSQL', 'MongoDB',
            'Git', 'CI/CD', 'Agile', 'REST APIs', 'GraphQL',
            'Redis', 'RabbitMQ', 'Elasticsearch', 'Jenkins', 'Terraform',
            'Vue.js', 'Angular', 'Django', 'FastAPI', 'Express.js'
        ]
        
        for i in range(count):
            candidate_id = str(uuid.uuid4())
            
            # Generate candidate data - these are EXTERNAL people, not users!
            # Always use developer's email for all mock candidates
            email = 'amir.shachar.se@gmail.com'
            
            candidate_data = {
                'id': candidate_id,
                'name': f"{self.mock_prefix}Candidate {i + 1}",
                'email': email,
                'linkedin_url': f"https://linkedin.com/in/{self.mock_prefix.lower()}candidate{i + 1}",
                'experience': json.dumps(self.generate_experience_data(i)),
                'education': json.dumps(self.generate_education_data(i)),
                'skills': random.sample(skills_pool, k=random.randint(5, 12)),
                'location': f"{random.choice(['Tel Aviv', 'Haifa', 'Jerusalem', 'Herzliya'])}, Israel",
                'source': 1,  # platform source
                'processed': True,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            try:
                result = self.supabase.table('candidates').insert(candidate_data).execute()
                if result.data:
                    created_ids.append(candidate_id)
                    self.track_created_record('candidates', candidate_id)
                    print(f"[MOCK] Created external candidate {i+1}: {candidate_id}")
                    print(f"[MOCK]   Name: {candidate_data['name']}")
                    print(f"[MOCK]   Email: {candidate_data['email']}")
                    print(f"[MOCK]   Skills: {', '.join(candidate_data['skills'][:5])}...")
                    print(f"[MOCK]   Location: {candidate_data['location']}")
            except Exception as e:
                print(f"[MOCK] Error creating candidate {i+1}: {str(e)}")
        
        return created_ids
    
    def get_cleanup_queries(self) -> List[str]:
        """Generate SQL queries to clean up all created mock data."""
        queries = []
        
        # Delete candidates
        if 'candidates' in self.created_records and self.created_records['candidates']:
            candidate_ids = "', '".join(self.created_records['candidates'])
            queries.append(f"DELETE FROM candidates WHERE id IN ('{candidate_ids}');")
        
        # Also clean by name prefix as backup
        queries.append(f"DELETE FROM candidates WHERE name LIKE '{self.mock_prefix}%';")
        
        return queries
    
    def verify_created_records(self) -> Dict[str, Any]:
        """Verify that all created records exist in the database."""
        verification_results = {
            'verified_count': 0,
            'missing_records': [],
            'details': {}
        }
        
        if 'candidates' in self.created_records and self.created_records['candidates']:
            print(f"\n[VERIFY] Checking {len(self.created_records['candidates'])} candidates...")
            
            for candidate_id in self.created_records['candidates']:
                try:
                    result = self.supabase.table('candidates')\
                        .select('*')\
                        .eq('id', candidate_id)\
                        .single()\
                        .execute()
                    
                    if result.data:
                        verification_results['verified_count'] += 1
                        
                        # Extract key information
                        skills = result.data.get('skills', [])
                        experience = result.data.get('experience', [])
                        education = result.data.get('education', [])
                        
                        verification_results['details'][candidate_id] = {
                            'exists': True,
                            'name': result.data.get('name', 'N/A'),
                            'email': result.data.get('email', 'N/A'),
                            'skills_count': len(skills),
                            'experience_count': len(experience) if isinstance(experience, list) else 0,
                            'education_count': len(education) if isinstance(education, list) else 0,
                            'location': result.data.get('location', 'N/A')
                        }
                        
                        print(f"   Candidate {candidate_id[:8]}... verified")
                        print(f"     Name: {result.data.get('name', 'N/A')}")
                        print(f"     Skills: {len(skills)} skills")
                        print(f"     Location: {result.data.get('location', 'N/A')}")
                    else:
                        verification_results['missing_records'].append(candidate_id)
                        print(f"   Candidate {candidate_id[:8]}... NOT FOUND")
                except Exception as e:
                    print(f"    Error verifying {candidate_id[:8]}...: {str(e)}")
                    verification_results['missing_records'].append(candidate_id)
        
        return verification_results


def main():
    """Example usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Create mock EXTERNAL candidates (not app users!)')
    parser.add_argument('--test-id', required=True, help='Test ID for tracking')
    parser.add_argument('--count', type=int, default=1, help='Number of candidates to create')
    parser.add_argument('--cleanup-only', action='store_true', help='Only show cleanup queries')
    
    args = parser.parse_args()
    
    creator = MockCandidatesCreator(args.test_id)
    
    if args.cleanup_only:
        queries = creator.get_cleanup_queries()
        print("Cleanup queries:")
        for q in queries:
            print(f"  {q}")
    else:
        # Create external candidates
        candidate_ids = creator.create_mock_records(count=args.count)
        if candidate_ids:
            print(f"\n Created {len(candidate_ids)} external candidates")
            creator.verify_created_records()
        
        print(f" To clean up later, run: python {__file__} --test-id {args.test_id} --cleanup-only")


if __name__ == "__main__":
    main()