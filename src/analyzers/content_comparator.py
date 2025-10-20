"""
Content Comparator Module

Compares static and dynamic content analysis to identify JavaScript-dependent content.
"""

import logging
from typing import List, Tuple
from difflib import SequenceMatcher

from ..models.analysis_result import AnalysisResult, ContentComparison
from ..utils.helpers import calculate_similarity, clean_text

logger = logging.getLogger(__name__)


class ContentComparator:
    """
    Compare static and dynamic analysis results to identify differences.
    
    This comparator identifies content that is only available with JavaScript
    execution and calculates similarity scores.
    """
    
    def __init__(self, similarity_threshold: float = 0.95):
        """
        Initialize content comparator.
        
        Args:
            similarity_threshold: Threshold for considering content similar (0.0-1.0)
        """
        self.similarity_threshold = similarity_threshold
    
    def compare(
        self,
        static_result: AnalysisResult,
        dynamic_result: AnalysisResult
    ) -> ContentComparison:
        """
        Compare static and dynamic analysis results.
        
        Args:
            static_result: Analysis result from static analyzer
            dynamic_result: Analysis result from dynamic analyzer
            
        Returns:
            ContentComparison with detailed comparison metrics
        """
        logger.info("Comparing static vs dynamic content...")
        
        # Extract text content
        static_text = static_result.content_analysis.text_content if static_result.content_analysis else ""
        dynamic_text = dynamic_result.content_analysis.text_content if dynamic_result.content_analysis else ""
        
        # Clean and normalize text
        static_clean = clean_text(static_text)
        dynamic_clean = clean_text(dynamic_text)
        
        # Calculate lengths
        static_length = len(static_clean)
        dynamic_length = len(dynamic_clean)
        content_difference = dynamic_length - static_length
        
        # Calculate similarity score
        similarity = calculate_similarity(static_clean, dynamic_clean)
        
        # Determine if content is JavaScript-dependent
        javascript_dependent = similarity < self.similarity_threshold
        
        # Find missing content in static
        missing_in_static = self._find_missing_content(static_clean, dynamic_clean)
        
        # Compare word counts
        static_words = static_result.content_analysis.word_count if static_result.content_analysis else 0
        dynamic_words = dynamic_result.content_analysis.word_count if dynamic_result.content_analysis else 0
        
        # Compare structural elements
        added_elements = self._compare_structure(static_result, dynamic_result)
        
        logger.info(
            f"Comparison complete: similarity={similarity:.2%}, "
            f"difference={content_difference} chars, "
            f"JS-dependent={javascript_dependent}"
        )
        
        return ContentComparison(
            static_content_length=static_length,
            dynamic_content_length=dynamic_length,
            content_difference=content_difference,
            similarity_score=similarity,
            javascript_dependent=javascript_dependent,
            missing_in_static=missing_in_static,
            added_elements=added_elements
        )
    
    def _find_missing_content(self, static_text: str, dynamic_text: str) -> List[str]:
        """
        Find content present in dynamic but missing in static.
        
        Args:
            static_text: Cleaned static text
            dynamic_text: Cleaned dynamic text
            
        Returns:
            List of text snippets missing in static analysis
        """
        missing = []
        
        # Split into sentences
        static_sentences = set(s.strip() for s in static_text.split('.') if s.strip())
        dynamic_sentences = set(s.strip() for s in dynamic_text.split('.') if s.strip())
        
        # Find sentences in dynamic but not in static
        new_sentences = dynamic_sentences - static_sentences
        
        # Filter out very short sentences and limit results
        significant_missing = [
            s for s in new_sentences 
            if len(s) > 20  # Minimum meaningful sentence length
        ]
        
        # Sort by length (longer = more significant) and limit to top 10
        significant_missing.sort(key=len, reverse=True)
        missing = significant_missing[:10]
        
        logger.debug(f"Found {len(missing)} significant missing content snippets")
        
        return missing
    
    def _compare_structure(
        self,
        static_result: AnalysisResult,
        dynamic_result: AnalysisResult
    ) -> List[str]:
        """
        Compare structural elements between static and dynamic.
        
        Args:
            static_result: Static analysis result
            dynamic_result: Dynamic analysis result
            
        Returns:
            List of structural elements added by JavaScript
        """
        added = []
        
        if not static_result.structure_analysis or not dynamic_result.structure_analysis:
            return added
        
        static_struct = static_result.structure_analysis
        dynamic_struct = dynamic_result.structure_analysis
        
        # Compare heading counts
        for level in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            static_headings = getattr(static_struct.heading_hierarchy, level, [])
            dynamic_headings = getattr(dynamic_struct.heading_hierarchy, level, [])
            
            if len(dynamic_headings) > len(static_headings):
                diff = len(dynamic_headings) - len(static_headings)
                added.append(f"{diff} additional {level.upper()} heading(s)")
        
        # Compare content analysis if available
        if static_result.content_analysis and dynamic_result.content_analysis:
            static_content = static_result.content_analysis
            dynamic_content = dynamic_result.content_analysis
            
            # Check paragraphs
            if dynamic_content.paragraphs > static_content.paragraphs:
                diff = dynamic_content.paragraphs - static_content.paragraphs
                added.append(f"{diff} additional paragraph(s)")
            
            # Check links
            if dynamic_content.links > static_content.links:
                diff = dynamic_content.links - static_content.links
                added.append(f"{diff} additional link(s)")
            
            # Check images
            if dynamic_content.images > static_content.images:
                diff = dynamic_content.images - static_content.images
                added.append(f"{diff} additional image(s)")
            
            # Check tables
            if dynamic_content.tables > static_content.tables:
                diff = dynamic_content.tables - static_content.tables
                added.append(f"{diff} additional table(s)")
            
            # Check lists
            if dynamic_content.lists > static_content.lists:
                diff = dynamic_content.lists - static_content.lists
                added.append(f"{diff} additional list(s)")
        
        logger.debug(f"Found {len(added)} structural additions")
        
        return added
    
    def calculate_javascript_dependency_score(self, comparison: ContentComparison) -> float:
        """
        Calculate a score indicating how dependent the page is on JavaScript.
        
        Args:
            comparison: ContentComparison result
            
        Returns:
            Score from 0.0 (no dependency) to 1.0 (fully dependent)
        """
        # Higher difference = more dependency
        if comparison.dynamic_content_length == 0:
            return 0.0
        
        # Calculate percentage of content that's JS-dependent
        if comparison.static_content_length == 0:
            # All content is dynamic
            return 1.0
        
        # Inverse of similarity (lower similarity = higher dependency)
        dependency_from_similarity = 1.0 - comparison.similarity_score
        
        # Weight by content difference
        content_ratio = comparison.content_difference / comparison.dynamic_content_length
        content_ratio = max(0.0, min(1.0, content_ratio))  # Clamp to 0-1
        
        # Combine metrics (weighted average)
        dependency_score = (dependency_from_similarity * 0.7) + (content_ratio * 0.3)
        
        return dependency_score
    
    def generate_comparison_summary(self, comparison: ContentComparison) -> dict:
        """
        Generate a human-readable summary of the comparison.
        
        Args:
            comparison: ContentComparison result
            
        Returns:
            Dictionary with summary information
        """
        dependency_score = self.calculate_javascript_dependency_score(comparison)
        
        # Determine dependency level
        if dependency_score < 0.1:
            dependency_level = "Minimal"
        elif dependency_score < 0.3:
            dependency_level = "Low"
        elif dependency_score < 0.6:
            dependency_level = "Moderate"
        elif dependency_score < 0.8:
            dependency_level = "High"
        else:
            dependency_level = "Critical"
        
        summary = {
            "similarity_percentage": f"{comparison.similarity_score * 100:.1f}%",
            "content_difference_chars": comparison.content_difference,
            "javascript_dependent": comparison.javascript_dependent,
            "dependency_level": dependency_level,
            "dependency_score": f"{dependency_score * 100:.1f}%",
            "missing_content_count": len(comparison.missing_in_static),
            "structural_additions": len(comparison.added_elements),
            "verdict": self._generate_verdict(comparison, dependency_score)
        }
        
        return summary
    
    def _generate_verdict(self, comparison: ContentComparison, dependency_score: float) -> str:
        """
        Generate a verdict about scraper accessibility.
        
        Args:
            comparison: ContentComparison result
            dependency_score: JavaScript dependency score
            
        Returns:
            Human-readable verdict string
        """
        if dependency_score < 0.1:
            return "Excellent for scrapers - minimal JavaScript dependency"
        elif dependency_score < 0.3:
            return "Good for scrapers - most content accessible without JavaScript"
        elif dependency_score < 0.6:
            return "Moderate scraper accessibility - some content requires JavaScript"
        elif dependency_score < 0.8:
            return "Poor scraper accessibility - significant JavaScript-dependent content"
        else:
            return "Critical issue - most content requires JavaScript execution"

