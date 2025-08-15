#!/usr/bin/env python3
"""
Report Generator - Generates comprehensive reports from aggregated results.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional
from debug_helpers.models.aggregated_results import AggregatedResults


class ReportGenerator:
    """Generates comprehensive reports of the parallel execution."""
    
    def generate_report(self, master_session_id: str, results: AggregatedResults, 
                       output_path: Optional[Path] = None) -> str:
        """Generate a comprehensive report of the parallel execution."""
        report_lines = []
        
        # Header
        report_lines.append("=" * 80)
        report_lines.append("PARALLEL DEBUG EXECUTION REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Master Session: {master_session_id}")
        report_lines.append("")
        
        # Summary
        report_lines.append("EXECUTION SUMMARY")
        report_lines.append("-" * 40)
        report_lines.append(f"Total Scenarios: {results.total_scenarios}")
        report_lines.append(f"Successful: {results.successful_scenarios}")
        report_lines.append(f"Failed: {results.failed_scenarios}")
        report_lines.append(f"Success Rate: {results.success_rate:.1%}")
        report_lines.append(f"Total Duration: {results.total_duration:.2f}s")
        report_lines.append(f"Average Duration: {results.average_duration:.2f}s")
        report_lines.append("")
        
        # Scenario Results
        report_lines.append("SCENARIO RESULTS")
        report_lines.append("-" * 40)
        for scenario, result in results.scenario_results.items():
            status = " PASSED" if result['success'] else " FAILED"
            report_lines.append(f"{scenario}: {status} ({result['duration']:.2f}s)")
            if result.get('error'):
                report_lines.append(f"  Error: {result['error']}")
        report_lines.append("")
        
        # Common Errors
        if results.common_errors:
            report_lines.append("COMMON ERRORS")
            report_lines.append("-" * 40)
            for error, count in results.common_errors:
                report_lines.append(f"({count}x) {error}")
            report_lines.append("")
        
        # Error Patterns
        if results.error_patterns:
            report_lines.append("ERROR PATTERNS")
            report_lines.append("-" * 40)
            for category, errors in results.error_patterns.items():
                report_lines.append(f"{category.upper()}: {len(errors)} occurrences")
        report_lines.append("")
        
        # Root Causes
        if results.root_causes:
            report_lines.append("ROOT CAUSES IDENTIFIED")
            report_lines.append("-" * 40)
            for i, cause in enumerate(results.root_causes, 1):
                report_lines.append(f"{i}. {cause.get('description', 'Unknown')}")
                if cause.get('fix_suggestion'):
                    report_lines.append(f"   Fix: {cause['fix_suggestion']}")
        report_lines.append("")
        
        # Recommendations
        if results.recommendations:
            report_lines.append("RECOMMENDATIONS")
            report_lines.append("-" * 40)
            for rec in results.recommendations:
                report_lines.append(f"• {rec}")
        report_lines.append("")
        
        # Footer
        report_lines.append("=" * 80)
        report_lines.append("END OF REPORT")
        report_lines.append("=" * 80)
        
        report_text = "\n".join(report_lines)
        
        # Save to file if requested
        if output_path:
            output_path.write_text(report_text)
            print(f"Report saved to: {output_path}")
        
        return report_text