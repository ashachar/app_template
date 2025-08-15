#!/usr/bin/env python3
"""
Recommendation Generator - Generates recommendations based on analysis results.
"""

from typing import List
from debug_helpers.models.aggregated_results import AggregatedResults


class RecommendationGenerator:
    """Generates recommendations based on analysis results."""
    
    def generate_recommendations(self, results: AggregatedResults) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Success rate recommendations
        if results.success_rate < 0.5:
            recommendations.append(
                " Low success rate indicates systemic issues. "
                "Review common errors and root causes."
            )
        
        # Error pattern recommendations
        if 'timeout' in results.error_patterns:
            recommendations.append(
                " Multiple timeout errors detected. Consider increasing timeouts "
                "or optimizing slow operations."
            )
        
        if 'authentication' in results.error_patterns:
            recommendations.append(
                " Authentication errors across scenarios. Check credentials and "
                "session management."
            )
        
        if 'database' in results.error_patterns:
            recommendations.append(
                " Database errors detected. Verify migrations are up-to-date and "
                "connections are properly configured."
            )
        
        # Performance recommendations
        if results.max_duration > results.average_duration * 3:
            recommendations.append(
                " Large variance in execution times. Some scenarios are significantly "
                "slower than others."
            )
        
        # Finding recommendations
        if results.root_causes:
            recommendations.append(
                f" {len(results.root_causes)} root causes identified. "
                "Prioritize fixing these issues."
            )
        
        if results.common_findings:
            recommendations.append(
                " Common findings across scenarios suggest shared underlying issues."
            )
        
        return recommendations