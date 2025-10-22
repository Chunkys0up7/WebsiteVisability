"""
LLM vs Scraper Comparison Analyzer

Compares what LLMs can see versus what web scrapers can see from the same website.
This shows the fundamental differences in how these two systems access web content.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import time
from urllib.parse import urlparse

from .llm_content_viewer import LLMContentViewer
from .static_analyzer import StaticAnalyzer
from .dynamic_analyzer import DynamicAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class ContentAccessComparison:
    """Comparison of content access between LLMs and scrapers"""
    
    # Basic info
    url: str
    analysis_timestamp: str
    
    # LLM perspective
    llm_content: str
    llm_character_count: int
    llm_word_count: int
    llm_visibility_score: float
    llm_limitations: List[str]
    
    # Scraper perspective  
    scraper_content: str
    scraper_character_count: int
    scraper_word_count: int
    scraper_accessibility_score: float
    scraper_capabilities: List[str]
    
    # Comparison metrics
    content_difference_percentage: float
    access_gap_score: float
    key_differences: List[str]
    recommendations: List[str]


class LLMScraperComparisonAnalyzer:
    """
    Analyzes the difference between LLM and scraper content access.
    
    Shows exactly what each system can see from the same website,
    highlighting the fundamental differences in their capabilities.
    """
    
    def __init__(self, timeout: int = 30):
        """Initialize the comparison analyzer."""
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
    
    def compare_content_access(self, url: str) -> ContentAccessComparison:
        """
        Compare what LLMs see vs what scrapers see from the same URL.
        
        Args:
            url: URL to analyze
            
        Returns:
            Detailed comparison of LLM vs scraper content access
        """
        self.logger.info(f"Starting LLM vs Scraper comparison for {url}")
        
        # Analyze LLM perspective
        llm_content, llm_metrics = self._analyze_llm_perspective(url)
        
        # Analyze scraper perspective
        scraper_content, scraper_metrics = self._analyze_scraper_perspective(url)
        
        # Compare the results
        comparison_metrics = self._compare_perspectives(llm_content, scraper_content, llm_metrics, scraper_metrics)
        
        # Generate insights and recommendations
        key_differences = self._identify_key_differences(llm_content, scraper_content, llm_metrics, scraper_metrics)
        recommendations = self._generate_recommendations(key_differences, llm_metrics, scraper_metrics)
        
        self.logger.info(f"LLM vs Scraper comparison complete for {url}")
        
        return ContentAccessComparison(
            url=url,
            analysis_timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
            llm_content=llm_content,
            llm_character_count=llm_metrics['character_count'],
            llm_word_count=llm_metrics['word_count'],
            llm_visibility_score=llm_metrics['visibility_score'],
            llm_limitations=llm_metrics['limitations'],
            scraper_content=scraper_content,
            scraper_character_count=scraper_metrics['character_count'],
            scraper_word_count=scraper_metrics['word_count'],
            scraper_accessibility_score=scraper_metrics['accessibility_score'],
            scraper_capabilities=scraper_metrics['capabilities'],
            content_difference_percentage=comparison_metrics['content_difference_percentage'],
            access_gap_score=comparison_metrics['access_gap_score'],
            key_differences=key_differences,
            recommendations=recommendations
        )
    
    def _analyze_llm_perspective(self, url: str) -> Tuple[str, Dict[str, Any]]:
        """Analyze what LLMs can see from the URL."""
        self.logger.info("Analyzing LLM perspective...")
        
        with LLMContentViewer(timeout=self.timeout) as viewer:
            # Get raw LLM content
            content_result = viewer.get_raw_llm_content(url)
            
            # Get visibility analysis
            visibility_analysis = viewer.analyze_llm_visibility(url)
            
            return content_result.raw_content, {
                'character_count': content_result.character_count,
                'word_count': content_result.word_count,
                'visibility_score': visibility_analysis.visibility_score,
                'limitations': self._extract_llm_limitations(visibility_analysis),
                'content_type': 'llm_processed'
            }
    
    def _analyze_scraper_perspective(self, url: str) -> Tuple[str, Dict[str, Any]]:
        """Analyze what web scrapers can see from the URL."""
        self.logger.info("Analyzing scraper perspective...")
        
        # Use static analyzer to get scraper-accessible content
        static_analyzer = StaticAnalyzer(timeout=self.timeout)
        static_result = static_analyzer.analyze(url)
        
        # Extract content that scrapers can access
        scraper_content = ""
        if static_result and static_result.content_analysis:
            scraper_content = static_result.content_analysis.text_content or ""
        
        # Calculate scraper accessibility score
        accessibility_score = self._calculate_scraper_accessibility_score(static_result)
        
        return scraper_content, {
            'character_count': len(scraper_content),
            'word_count': len(scraper_content.split()) if scraper_content else 0,
            'accessibility_score': accessibility_score,
            'capabilities': self._extract_scraper_capabilities(static_result),
            'content_type': 'scraper_accessible'
        }
    
    def _compare_perspectives(self, llm_content: str, scraper_content: str, 
                           llm_metrics: Dict[str, Any], scraper_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Compare LLM and scraper perspectives."""
        
        # Calculate content difference
        llm_chars = llm_metrics['character_count']
        scraper_chars = scraper_metrics['character_count']
        
        if scraper_chars > 0:
            content_difference_percentage = abs(llm_chars - scraper_chars) / scraper_chars * 100
        else:
            content_difference_percentage = 100 if llm_chars > 0 else 0
        
        # Calculate access gap score (higher = bigger gap)
        llm_score = llm_metrics['visibility_score']
        scraper_score = scraper_metrics['accessibility_score']
        access_gap_score = abs(llm_score - scraper_score)
        
        return {
            'content_difference_percentage': content_difference_percentage,
            'access_gap_score': access_gap_score,
            'llm_advantage': llm_chars > scraper_chars,
            'scraper_advantage': scraper_chars > llm_chars
        }
    
    def _identify_key_differences(self, llm_content: str, scraper_content: str,
                                llm_metrics: Dict[str, Any], scraper_metrics: Dict[str, Any]) -> List[str]:
        """Identify key differences between LLM and scraper access."""
        differences = []
        
        # Content volume differences
        llm_chars = llm_metrics['character_count']
        scraper_chars = scraper_metrics['character_count']
        
        if llm_chars > scraper_chars * 1.2:
            differences.append(f"LLMs see {llm_chars:,} characters vs scrapers' {scraper_chars:,} - LLMs have better access")
        elif scraper_chars > llm_chars * 1.2:
            differences.append(f"Scrapers see {scraper_chars:,} characters vs LLMs' {llm_chars:,} - Scrapers have better access")
        
        # Score differences
        llm_score = llm_metrics['visibility_score']
        scraper_score = scraper_metrics['accessibility_score']
        
        if llm_score > scraper_score + 20:
            differences.append(f"LLM visibility score ({llm_score:.1f}) significantly higher than scraper score ({scraper_score:.1f})")
        elif scraper_score > llm_score + 20:
            differences.append(f"Scraper accessibility score ({scraper_score:.1f}) significantly higher than LLM score ({llm_score:.1f})")
        
        # Content quality differences
        if "javascript" in llm_content.lower() and "javascript" in scraper_content.lower():
            if "please turn on javascript" in llm_content.lower():
                differences.append("LLMs see JavaScript requirement message - content is hidden")
        
        # Add specific limitations
        for limitation in llm_metrics['limitations']:
            if "javascript" in limitation.lower():
                differences.append("LLMs cannot execute JavaScript - dynamic content inaccessible")
            elif "meta" in limitation.lower():
                differences.append("Missing meta tags affect LLM understanding")
        
        return differences
    
    def _generate_recommendations(self, key_differences: List[str], 
                                llm_metrics: Dict[str, Any], scraper_metrics: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on the comparison."""
        recommendations = []
        
        # Analyze the differences
        for difference in key_differences:
            if "javascript" in difference.lower():
                recommendations.append("CRITICAL: Implement server-side rendering for JavaScript-dependent content")
                recommendations.append("HIGH: Add static HTML fallbacks for dynamic features")
            elif "meta" in difference.lower():
                recommendations.append("HIGH: Add comprehensive meta tags for better LLM understanding")
            elif "LLMs have better access" in difference:
                recommendations.append("MEDIUM: Optimize content structure for both LLMs and scrapers")
            elif "Scrapers have better access" in difference:
                recommendations.append("HIGH: Improve LLM accessibility while maintaining scraper compatibility")
        
        # General recommendations
        if llm_metrics['visibility_score'] < 70:
            recommendations.append("HIGH: Focus on LLM accessibility improvements")
        
        if scraper_metrics['accessibility_score'] < 70:
            recommendations.append("HIGH: Focus on scraper accessibility improvements")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _extract_llm_limitations(self, visibility_analysis) -> List[str]:
        """Extract LLM limitations from visibility analysis."""
        limitations = []
        
        hidden = visibility_analysis.hidden_content_summary
        for issue, status in hidden.items():
            if status:
                limitations.append(f"{issue.replace('_', ' ').title()}: Content is hidden from LLMs")
        
        return limitations
    
    def _extract_scraper_capabilities(self, static_result) -> List[str]:
        """Extract scraper capabilities from static analysis."""
        capabilities = []
        
        if static_result and static_result.content_analysis:
            capabilities.append("Can access static HTML content")
            
            if static_result.content_analysis.images > 0:
                capabilities.append("Can access image metadata and alt text")
            
            if static_result.content_analysis.links > 0:
                capabilities.append("Can follow and analyze links")
        
        if static_result and static_result.meta_analysis:
            capabilities.append("Can read meta tags and structured data")
        
        return capabilities
    
    def _calculate_scraper_accessibility_score(self, static_result) -> float:
        """Calculate scraper accessibility score."""
        if not static_result:
            return 0.0
        
        score = 100.0
        
        # Check content availability
        if static_result.content_analysis:
            if static_result.content_analysis.character_count < 100:
                score -= 30
            elif static_result.content_analysis.character_count < 500:
                score -= 15
        
        # Check meta tags
        if static_result.meta_analysis:
            if not static_result.meta_analysis.title:
                score -= 20
            if not static_result.meta_analysis.description:
                score -= 15
        
        # Check structure
        if static_result.structure_analysis:
            if not static_result.structure_analysis.heading_hierarchy:
                score -= 10
        
        return max(0, score)
    
    def close(self):
        """Close the analyzer."""
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
