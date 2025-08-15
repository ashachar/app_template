#!/usr/bin/env python3
"""
Findings Analyzer - Analyzes findings across workers to identify common issues.
"""

from collections import defaultdict
from typing import Dict, List, Any, Tuple


class FindingsAnalyzer:
    """Analyzes findings across all workers."""
    
    def analyze_findings(self, worker_results: List[Dict[str, Any]]) -> Tuple[Dict[str, List[Dict]], List[Dict]]:
        """
        Analyze findings across all workers.
        
        Returns:
            Tuple of (common_findings, all_root_causes)
        """
        findings_by_type = defaultdict(list)
        all_root_causes = []
        
        for worker_result in worker_results:
            for finding in worker_result.get('findings', []):
                finding_type = finding.get('type', 'observation')
                findings_by_type[finding_type].append({
                    'scenario': worker_result['scenario_name'],
                    'description': finding.get('description'),
                    'evidence': finding.get('evidence'),
                    'fix_suggestion': finding.get('fix_suggestion'),
                    'timestamp': finding.get('timestamp')
                })
                
                if finding_type == 'root_cause':
                    all_root_causes.append(finding)
        
        # Find common findings (similar descriptions)
        common_findings = {}
        for finding_type, findings in findings_by_type.items():
            if len(findings) > 1:
                # Group similar findings
                grouped = self._group_similar_findings(findings)
                if grouped:
                    common_findings[finding_type] = grouped
        
        return common_findings, all_root_causes
    
    def _group_similar_findings(self, findings: List[Dict]) -> List[Dict]:
        """Group findings with similar descriptions."""
        grouped = []
        seen = set()
        
        for i, finding in enumerate(findings):
            if i in seen:
                continue
            
            desc = finding.get('description', '')
            similar = [finding]
            
            # Find similar findings
            for j, other in enumerate(findings[i+1:], i+1):
                if j in seen:
                    continue
                
                other_desc = other.get('description', '')
                if self._are_similar(desc, other_desc):
                    similar.append(other)
                    seen.add(j)
            
            if len(similar) > 1:
                grouped.append({
                    'description': desc,
                    'count': len(similar),
                    'scenarios': [f['scenario'] for f in similar],
                    'evidence': [f.get('evidence') for f in similar if f.get('evidence')]
                })
        
        return grouped
    
    def _are_similar(self, text1: str, text2: str) -> bool:
        """Check if two texts are similar (simple implementation)."""
        # Normalize texts
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()
        
        # Exact match
        if text1 == text2:
            return True
        
        # Check if one contains the other
        if text1 in text2 or text2 in text1:
            return True
        
        # Check word overlap (simple similarity)
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return False
        
        overlap = len(words1.intersection(words2))
        similarity = overlap / min(len(words1), len(words2))
        
        return similarity > 0.7