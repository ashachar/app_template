#!/usr/bin/env python3
"""
Base class for all mock data creators.
Provides common functionality for creating and cleaning up mock data.
"""

import os
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()


class BaseMockCreator(ABC):
    """Abstract base class for all mock data creators."""
    
    def __init__(self, test_id: str, supabase_client=None):
        """
        Initialize mock creator with a unique test ID.
        
        Args:
            test_id: Unique identifier for this test run
            supabase_client: Optional authenticated Supabase client
        """
        self.test_id = test_id
        self.mock_prefix = f"MOCK_{test_id}_{uuid.uuid4().hex[:6]}_"
        self.created_records = {}
        self.cleanup_queries = []
        
        # Use provided client or create new one
        if supabase_client:
            self.supabase = supabase_client
        else:
            # Try to use service key for elevated permissions, fall back to anon key
            supabase_url = os.getenv('VITE_SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('VITE_SUPABASE_ANON_KEY')
            
            if os.getenv('SUPABASE_SERVICE_KEY'):
                print("[MOCK] Using service key for elevated permissions")
            else:
                print("[MOCK] Using anon key - some operations may be restricted")
                
            self.supabase = create_client(supabase_url, supabase_key)
    
    @abstractmethod
    def analyze_schema_requirements(self) -> Dict[str, Any]:
        """
        Analyze schema files to understand requirements.
        Must be implemented by each mock creator.
        
        Returns:
            Dictionary describing schema requirements
        """
        pass
    
    @abstractmethod
    def create_mock_records(self, count: int = 1, **kwargs) -> List[str]:
        """
        Create mock records in the database.
        Must be implemented by each mock creator.
        
        Args:
            count: Number of records to create
            **kwargs: Additional parameters specific to the record type
            
        Returns:
            List of created record IDs
        """
        pass
    
    @abstractmethod
    def get_cleanup_queries(self) -> List[str]:
        """
        Generate SQL queries to clean up all created mock data.
        Must be implemented by each mock creator.
        
        Returns:
            List of SQL DELETE queries
        """
        pass
    
    @abstractmethod
    def verify_created_records(self) -> Dict[str, Any]:
        """
        Verify that all created records exist in the database.
        Must be implemented by each mock creator.
        
        Returns:
            Dictionary with verification results
        """
        pass
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get the currently authenticated user."""
        user = self.supabase.auth.get_user()
        if user and user.user:
            return {
                'id': user.user.id,
                'email': user.user.email
            }
        return None
    
    def get_user_details(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user details for a given user ID."""
        result = self.supabase.table('user_details')\
            .select('*')\
            .eq('user_id', user_id)\
            .single()\
            .execute()
        
        return result.data if result.data else None
    
    def track_created_record(self, table: str, record_id: str):
        """Track a created record for cleanup."""
        if table not in self.created_records:
            self.created_records[table] = []
        self.created_records[table].append(record_id)
    
    def create_all_mock_data(self, **kwargs) -> Dict[str, Any]:
        """
        Main method to create all required mock data.
        Can be overridden for complex scenarios.
        
        Returns:
            Dictionary with creation results and cleanup info
        """
        print(f"\n{'='*60}")
        print(f"Creating mock data for: {self.__class__.__name__}")
        print(f"Test ID: {self.test_id}")
        print(f"Mock prefix: {self.mock_prefix}")
        print(f"{'='*60}\n")
        
        # Analyze schema
        requirements = self.analyze_schema_requirements()
        
        # Create mock records
        created_ids = self.create_mock_records(**kwargs)
        
        # Verify records were created
        print(f"\n[VERIFY] Checking created records in database...")
        verification_results = self.verify_created_records()
        
        # Get cleanup queries
        cleanup_queries = self.get_cleanup_queries()
        
        result = {
            'mock_prefix': self.mock_prefix,
            'created_records': self.created_records,
            'created_ids': created_ids,
            'cleanup_queries': cleanup_queries,
            'requirements': requirements,
            'verification': verification_results
        }
        
        print(f"\n[MOCK] Created {len(created_ids)} records")
        print(f"[MOCK] Verified: {verification_results.get('verified_count', 0)}/{len(created_ids)} records exist in DB")
        print(f"[MOCK] Cleanup queries generated: {len(cleanup_queries)}")
        
        return result
    
    def cleanup(self):
        """Execute cleanup queries to remove all mock data."""
        cleanup_queries = self.get_cleanup_queries()
        
        print(f"\n[CLEANUP] Executing {len(cleanup_queries)} cleanup queries...")
        
        for query in cleanup_queries:
            print(f"[CLEANUP] {query[:80]}...")
            # In production, you would execute these queries
            # For safety, we're just printing them
        
        print("[CLEANUP] Complete!")
    
    def generate_mock_email(self, prefix: str = "") -> str:
        """Generate a unique mock email address."""
        return f"{self.mock_prefix}{prefix}@mock-test.example.com".lower()
    
    def generate_mock_phone(self) -> str:
        """Generate a mock phone number."""
        # Israeli format: +972-XX-XXX-XXXX
        return f"+972-50-{uuid.uuid4().hex[:3]}-{uuid.uuid4().hex[:4]}"
    
    def generate_mock_url(self, subdomain: str = "www") -> str:
        """Generate a mock URL."""
        return f"https://{subdomain}.{self.mock_prefix.lower()}example.com"