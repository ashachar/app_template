"""
Mock data creation utilities for testing and debugging.

This package provides structured mock data creators for all major database elements.
Each creator follows schema constraints and handles foreign key relationships properly.

Usage:
    from debug_helpers.mock import MockRequisitionsCreator, MockUsersCreator
    
    # Create mock requisitions
    creator = MockRequisitionsCreator("TEST_123")
    result = creator.create_all_mock_data(count=3)
    
    # Clean up when done
    creator.cleanup()

Available Creators:
    - MockCompaniesCreator: Creates mock companies (requires special permissions)
    - MockUsersCreator: Creates mock users with auth entries
    - MockCandidatesCreator: Creates mock candidates with resumes
    - MockRequisitionsCreator: Creates mock job requisitions
    - MockApplicationsCreator: Creates mock job applications
    - MockMatchesCreator: Creates mock candidate-requisition matches

Always check this folder first when you need mock data for testing!
"""

from .base_mock import BaseMockCreator
from .mock_companies import MockCompaniesCreator
from .mock_users import MockUsersCreator
from .mock_candidates import MockCandidatesCreator
from .mock_requisitions import MockRequisitionsCreator
from .mock_applications import MockApplicationsCreator
from .mock_matches import MockMatchesCreator

__all__ = [
    'BaseMockCreator',
    'MockCompaniesCreator', 
    'MockUsersCreator',
    'MockCandidatesCreator',
    'MockRequisitionsCreator',
    'MockApplicationsCreator',
    'MockMatchesCreator'
]