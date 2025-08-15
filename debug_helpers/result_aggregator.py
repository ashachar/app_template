#!/usr/bin/env python3
"""
Result Aggregator - Collects and synthesizes results from parallel debug workers.
Identifies patterns, common errors, and generates comprehensive reports.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from debug_session_state import DebugSessionState
from debug_helpers.models.aggregated_results import AggregatedResults
from debug_helpers.analyzers.error_pattern_analyzer import ErrorPatternAnalyzer
from debug_helpers.analyzers.findings_analyzer import FindingsAnalyzer
from debug_helpers.analyzers.performance_analyzer import PerformanceAnalyzer
from debug_helpers.builders.timeline_builder import TimelineBuilder
from debug_helpers.generators.recommendation_generator import RecommendationGenerator
from debug_helpers.generators.report_generator import ReportGenerator


class ResultAggregator:
    """Aggregates and analyzes results from parallel debug workers."""
    
    def __init__(self, master_session_id: str):
        self.master_session_id = master_session_id
        self.worker_results = []
        self.aggregated_results = AggregatedResults()
        
        # Initialize analyzers and generators
        self.error_analyzer = ErrorPatternAnalyzer()
        self.findings_analyzer = FindingsAnalyzer()
        self.performance_analyzer = PerformanceAnalyzer()
        self.timeline_builder = TimelineBuilder()
        self.recommendation_generator = RecommendationGenerator()
        self.report_generator = ReportGenerator()
        
    def add_result(self, worker_result: Dict[str, Any]):
        """Add a worker result to the aggregator."""
        self.worker_results.append(worker_result)
        
    def aggregate(self) -> AggregatedResults:
        """Aggregate all worker results and identify patterns."""
        if not self.worker_results:
            return self.aggregated_results
        
        # Basic statistics
        self._calculate_basic_stats()
        
        # Analyze errors and patterns
        self._analyze_errors()
        
        # Analyze findings
        self._analyze_findings()
        
        # Analyze performance metrics
        self._analyze_performance()
        
        # Build timeline
        self._build_timeline()
        
        # Generate recommendations
        self._generate_recommendations()
        
        # Create master session state with aggregated data
        self._save_to_master_session()
        
        return self.aggregated_results
    
    def _calculate_basic_stats(self):
        """Calculate basic statistics from results."""
        results = self.aggregated_results
        results.total_scenarios = len(self.worker_results)
        
        for worker_result in self.worker_results:
            scenario_name = worker_result['scenario_name']
            
            # Success/failure counts
            if worker_result['success']:
                results.successful_scenarios += 1
            else:
                results.failed_scenarios += 1
            
            # Duration statistics
            duration = worker_result.get('duration', 0)
            if duration:
                results.total_duration += duration
                results.min_duration = min(results.min_duration, duration)
                results.max_duration = max(results.max_duration, duration)
            
            # Store individual results
            results.scenario_results[scenario_name] = {
                'success': worker_result['success'],
                'duration': duration,
                'error': worker_result.get('error'),
                'worker_id': worker_result['worker_id'],
                'session_id': worker_result.get('session_id'),
                'checkpoints': worker_result.get('checkpoints', []),
                'artifacts': worker_result.get('artifacts', [])
            }
        
        # Calculate rates and averages
        if results.total_scenarios > 0:
            results.success_rate = results.successful_scenarios / results.total_scenarios
            results.average_duration = results.total_duration / results.total_scenarios
    
    def _analyze_errors(self):
        """Analyze errors across all workers to find patterns."""
        common_errors, error_patterns = self.error_analyzer.analyze_errors(self.worker_results)
        self.aggregated_results.common_errors = common_errors
        self.aggregated_results.error_patterns = error_patterns
    
    def _analyze_findings(self):
        """Analyze findings across all workers."""
        common_findings, root_causes = self.findings_analyzer.analyze_findings(self.worker_results)
        self.aggregated_results.common_findings = common_findings
        self.aggregated_results.root_causes = root_causes
    
    def _analyze_performance(self):
        """Analyze performance metrics across workers."""
        performance_metrics, test_data_usage = self.performance_analyzer.analyze_performance(self.worker_results)
        self.aggregated_results.performance_metrics = performance_metrics
        self.aggregated_results.test_data_usage = test_data_usage
    
    def _build_timeline(self):
        """Build a timeline of events across all workers."""
        self.aggregated_results.timeline = self.timeline_builder.build_timeline(self.worker_results)
    
    def _generate_recommendations(self):
        """Generate recommendations based on analysis."""
        self.aggregated_results.recommendations = self.recommendation_generator.generate_recommendations(self.aggregated_results)
    
    def _save_to_master_session(self):
        """Save aggregated results to master session state."""
        try:
            # Create master session state
            master_state = DebugSessionState(self.master_session_id)
            
            # Save aggregated results
            master_state.metadata['parallel_execution'] = {
                'aggregated_at': datetime.now().isoformat(),
                'total_workers': len(self.worker_results),
                'summary': self.aggregated_results.to_dict()
            }
            
            # Create checkpoint
            master_state.create_checkpoint(
                "parallel_execution_complete",
                f"Completed parallel execution of {self.aggregated_results.total_scenarios} scenarios"
            )
            
            # Add key findings
            for root_cause in self.aggregated_results.root_causes:
                master_state.add_finding(
                    "root_cause",
                    f"[Aggregated] {root_cause.get('description', 'Unknown')}",
                    evidence=root_cause.get('evidence', ''),
                    fix_suggestion=root_cause.get('fix_suggestion', '')
                )
            
            # Save state
            master_state._save_state()
            
        except Exception as e:
            print(f"Warning: Could not save to master session: {e}")
    
    def generate_report(self, output_path: Optional[Path] = None) -> str:
        """Generate a comprehensive report of the parallel execution."""
        return self.report_generator.generate_report(self.master_session_id, self.aggregated_results, output_path)

