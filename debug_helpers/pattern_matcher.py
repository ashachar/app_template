#!/usr/bin/env python3
"""
Intelligent Pattern Matcher for Failure Pattern Database.

Provides advanced matching capabilities:
- Multi-dimensional pattern matching
- Fuzzy string matching with NLP techniques
- Context-aware scoring
- Pattern clustering and relationships
"""

import re
import difflib
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
import numpy as np
from collections import Counter
import json


@dataclass
class MatchResult:
    """Result of pattern matching with detailed scoring breakdown."""
    pattern_id: str
    overall_confidence: float
    text_similarity: float
    context_similarity: float
    structural_similarity: float
    matched_keywords: List[str]
    matched_patterns: List[str]
    explanation: str


class PatternMatcher:
    """Advanced pattern matching engine."""
    
    def __init__(self):
        # Common programming terms for better matching
        self.stop_words = {
            'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but',
            'in', 'with', 'to', 'for', 'of', 'as', 'by', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'shall', 'can', 'cannot'
        }
        
        # Technical synonyms for better matching
        self.synonyms = {
            'error': ['exception', 'fault', 'failure', 'issue', 'problem'],
            'null': ['undefined', 'none', 'nil', 'empty', 'missing'],
            'invalid': ['incorrect', 'wrong', 'bad', 'illegal', 'malformed'],
            'timeout': ['timed out', 'exceeded', 'deadline', 'expired'],
            'permission': ['access', 'authorization', 'privilege', 'rights'],
            'connection': ['connect', 'network', 'socket', 'communication'],
            'database': ['db', 'sql', 'query', 'table', 'schema'],
            'api': ['endpoint', 'route', 'service', 'rest', 'http'],
            'authentication': ['auth', 'login', 'credential', 'token', 'session']
        }
        
        # Error category weights for scoring
        self.category_weights = {
            'Database': 1.2,      # Database errors often have clear patterns
            'API': 1.1,          # API errors are well-structured
            'Authentication': 1.1,
            'Null Reference': 1.0,
            'Timeout': 0.9,      # Timeouts can be generic
            'File System': 1.0,
            'Lambda': 1.1,
            'React': 1.0,
            'Build/Compilation': 1.2,  # Build errors are very specific
            'Performance': 0.8   # Performance issues are often vague
        }
    
    def match_pattern(self, error_message: str, pattern_data: Dict[str, Any],
                     context: Optional[Dict[str, Any]] = None) -> MatchResult:
        """
        Match an error message against a pattern with detailed scoring.
        
        Args:
            error_message: The error message to match
            pattern_data: Pattern data including regex patterns, keywords, etc.
            context: Optional context information (module, action, etc.)
        
        Returns:
            MatchResult with detailed scoring breakdown
        """
        pattern_id = pattern_data.get('pattern_id', 'unknown')
        
        # Text similarity scoring
        text_score, matched_patterns = self._calculate_text_similarity(
            error_message, pattern_data.get('error_patterns', [])
        )
        
        # Context similarity scoring
        context_score, matched_keywords = self._calculate_context_similarity(
            error_message, pattern_data, context
        )
        
        # Structural similarity (error type, category matching)
        structural_score = self._calculate_structural_similarity(
            error_message, pattern_data, context
        )
        
        # Calculate weighted overall confidence
        error_type = pattern_data.get('error_type', 'Unknown')
        category_weight = self.category_weights.get(error_type, 1.0)
        
        # Weighted combination of scores
        overall_confidence = (
            text_score * 0.5 +          # Text matching is most important
            context_score * 0.3 +       # Context provides good signal
            structural_score * 0.2      # Structure confirms the match
        ) * category_weight
        
        # Generate explanation
        explanation = self._generate_match_explanation(
            text_score, context_score, structural_score,
            matched_patterns, matched_keywords
        )
        
        return MatchResult(
            pattern_id=pattern_id,
            overall_confidence=min(1.0, overall_confidence),
            text_similarity=text_score,
            context_similarity=context_score,
            structural_similarity=structural_score,
            matched_keywords=matched_keywords,
            matched_patterns=matched_patterns,
            explanation=explanation
        )
    
    def _calculate_text_similarity(self, error_message: str, 
                                 patterns: List[str]) -> Tuple[float, List[str]]:
        """Calculate text similarity score using multiple techniques."""
        error_lower = error_message.lower()
        matched_patterns = []
        scores = []
        
        for pattern in patterns:
            # Try regex match first (highest confidence)
            try:
                if re.search(pattern, error_message, re.IGNORECASE):
                    matched_patterns.append(pattern)
                    scores.append(0.9)  # High score for regex match
                    continue
            except:
                pass
            
            # Fuzzy string matching
            # Extract key parts from regex pattern
            pattern_words = re.findall(r'[a-zA-Z_]+', pattern)
            if pattern_words:
                pattern_text = ' '.join(pattern_words).lower()
                
                # Use difflib for sequence matching
                seq_ratio = difflib.SequenceMatcher(None, pattern_text, error_lower).ratio()
                scores.append(seq_ratio * 0.7)  # Slightly lower weight for fuzzy match
                
                if seq_ratio > 0.6:
                    matched_patterns.append(f"fuzzy:{pattern}")
        
        # Also try token-based matching
        error_tokens = self._tokenize(error_message)
        pattern_all_tokens = []
        for pattern in patterns:
            pattern_all_tokens.extend(self._tokenize(' '.join(re.findall(r'[a-zA-Z_]+', pattern))))
        
        if error_tokens and pattern_all_tokens:
            token_overlap = len(set(error_tokens) & set(pattern_all_tokens))
            token_score = token_overlap / max(len(error_tokens), len(pattern_all_tokens))
            scores.append(token_score * 0.5)  # Lower weight for token matching
        
        # Return best score
        return max(scores) if scores else 0.0, matched_patterns
    
    def _calculate_context_similarity(self, error_message: str,
                                    pattern_data: Dict[str, Any],
                                    context: Optional[Dict[str, Any]]) -> Tuple[float, List[str]]:
        """Calculate context-based similarity score."""
        matched_keywords = []
        scores = []
        
        # Extract all text for matching
        all_text = error_message.lower()
        if context:
            all_text += ' ' + ' '.join(str(v).lower() for v in context.values())
        
        # Check context keywords
        context_keywords = pattern_data.get('context_keywords', [])
        if context_keywords:
            keyword_matches = 0
            for keyword in context_keywords:
                if keyword.lower() in all_text:
                    matched_keywords.append(keyword)
                    keyword_matches += 1
                # Check synonyms
                elif any(syn in all_text for syn in self.synonyms.get(keyword.lower(), [])):
                    matched_keywords.append(f"syn:{keyword}")
                    keyword_matches += 0.8  # Slightly lower score for synonym
            
            if context_keywords:
                scores.append(keyword_matches / len(context_keywords))
        
        # Check module hints
        if context and 'module' in context:
            module_hints = pattern_data.get('module_hints', [])
            if module_hints:
                module_lower = context['module'].lower()
                module_matches = sum(1 for hint in module_hints if hint.lower() in module_lower)
                scores.append(module_matches / len(module_hints))
        
        # Check for specific context patterns
        if context:
            # Action-based matching
            if 'action' in context:
                action = context['action'].lower()
                if any(act in action for act in ['create', 'add', 'insert']):
                    if 'validation' in all_text or 'invalid' in all_text:
                        scores.append(0.7)
                elif any(act in action for act in ['update', 'edit', 'modify']):
                    if 'permission' in all_text or 'forbidden' in all_text:
                        scores.append(0.6)
        
        return max(scores) if scores else 0.0, matched_keywords
    
    def _calculate_structural_similarity(self, error_message: str,
                                       pattern_data: Dict[str, Any],
                                       context: Optional[Dict[str, Any]]) -> float:
        """Calculate structural similarity based on error characteristics."""
        scores = []
        
        # Check error type indicators in message
        error_type = pattern_data.get('error_type', '').lower()
        error_lower = error_message.lower()
        
        # Look for type-specific indicators
        type_indicators = {
            'database': ['sql', 'table', 'column', 'relation', 'query', 'database'],
            'api': ['request', 'response', 'endpoint', 'http', '404', '401', '500'],
            'null reference': ['null', 'undefined', 'cannot read', 'property'],
            'authentication': ['auth', 'token', 'login', 'credential', 'unauthorized'],
            'timeout': ['timeout', 'exceeded', 'timed out', 'deadline'],
            'lambda': ['lambda', 'function', 'aws', 'invoke', 'serverless'],
            'react': ['react', 'component', 'render', 'hook', 'state'],
            'file system': ['file', 'directory', 'path', 'permission', 'enoent']
        }
        
        if error_type in type_indicators:
            indicators = type_indicators[error_type]
            indicator_count = sum(1 for ind in indicators if ind in error_lower)
            if indicators:
                scores.append(indicator_count / len(indicators))
        
        # Check for common error formats
        # Stack trace format
        if re.search(r'at\s+\w+\s*\(.*:\d+:\d+\)', error_message):
            scores.append(0.3)  # Has stack trace structure
        
        # Error code format
        if re.search(r'\b[A-Z]+[_-]?[A-Z0-9]+\b', error_message):
            scores.append(0.2)  # Has error code format
        
        # HTTP status codes
        if re.search(r'\b[4-5]\d{2}\b', error_message):
            if error_type == 'api':
                scores.append(0.5)
        
        return max(scores) if scores else 0.0
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into meaningful words."""
        # Extract words, excluding stop words
        words = re.findall(r'\b[a-zA-Z_]+\b', text.lower())
        return [w for w in words if w not in self.stop_words and len(w) > 2]
    
    def _generate_match_explanation(self, text_score: float, context_score: float,
                                   structural_score: float, matched_patterns: List[str],
                                   matched_keywords: List[str]) -> str:
        """Generate human-readable explanation of the match."""
        explanations = []
        
        if text_score > 0.7:
            if any(not p.startswith('fuzzy:') for p in matched_patterns):
                explanations.append("Strong pattern match found")
            else:
                explanations.append("Good fuzzy match with error pattern")
        elif text_score > 0.4:
            explanations.append("Moderate text similarity")
        
        if context_score > 0.7:
            explanations.append(f"Context matches well ({len(matched_keywords)} keywords)")
        elif context_score > 0.4:
            explanations.append("Some context overlap")
        
        if structural_score > 0.5:
            explanations.append("Error structure matches expected type")
        
        if not explanations:
            explanations.append("Weak match - consider as fallback")
        
        return "; ".join(explanations)
    
    def find_related_patterns(self, patterns: List[Dict[str, Any]], 
                            similarity_threshold: float = 0.6) -> Dict[str, List[str]]:
        """Find related patterns based on similarity."""
        related = {}
        
        for i, pattern1 in enumerate(patterns):
            pattern1_id = pattern1.get('pattern_id', f'pattern_{i}')
            related[pattern1_id] = []
            
            for j, pattern2 in enumerate(patterns):
                if i == j:
                    continue
                
                pattern2_id = pattern2.get('pattern_id', f'pattern_{j}')
                
                # Compare patterns
                similarity = self._calculate_pattern_similarity(pattern1, pattern2)
                
                if similarity >= similarity_threshold:
                    related[pattern1_id].append(pattern2_id)
        
        return related
    
    def _calculate_pattern_similarity(self, pattern1: Dict[str, Any], 
                                    pattern2: Dict[str, Any]) -> float:
        """Calculate similarity between two patterns."""
        scores = []
        
        # Same error type gives high similarity
        if pattern1.get('error_type') == pattern2.get('error_type'):
            scores.append(0.4)
        
        # Compare error patterns
        patterns1 = set(' '.join(pattern1.get('error_patterns', [])).lower().split())
        patterns2 = set(' '.join(pattern2.get('error_patterns', [])).lower().split())
        if patterns1 and patterns2:
            pattern_overlap = len(patterns1 & patterns2) / len(patterns1 | patterns2)
            scores.append(pattern_overlap * 0.3)
        
        # Compare keywords
        keywords1 = set(pattern1.get('context_keywords', []))
        keywords2 = set(pattern2.get('context_keywords', []))
        if keywords1 and keywords2:
            keyword_overlap = len(keywords1 & keywords2) / len(keywords1 | keywords2)
            scores.append(keyword_overlap * 0.2)
        
        # Compare modules
        modules1 = set(pattern1.get('module_hints', []))
        modules2 = set(pattern2.get('module_hints', []))
        if modules1 and modules2:
            module_overlap = len(modules1 & modules2) / len(modules1 | modules2)
            scores.append(module_overlap * 0.1)
        
        return sum(scores)