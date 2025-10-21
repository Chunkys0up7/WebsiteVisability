"""
Separate Analysis Module

Provides independent scraper and LLM analysis functions that can be called separately.
"""

import logging
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

from .static_analyzer import StaticAnalyzer
from .dynamic_analyzer import DynamicAnalyzer
from .content_comparator import ContentComparator
from .scoring_engine import ScoringEngine
from .crawler_analyzer import CrawlerAnalyzer
from .llm_accessibility_analyzer import LLMAccessibilityAnalyzer
from ..models.analysis_result import AnalysisResult
from ..models.scoring_models import Score

logger = logging.getLogger(__name__)


@dataclass
class ScraperAnalysisResult:
    """Results from scraper-focused analysis"""
    analysis_result: AnalysisResult
    score: Score
    scraper_friendliness: float
    grade: str
    recommendations: list


@dataclass
class LLMAnalysisResult:
    """Results from LLM-focused analysis"""
    analysis_result: AnalysisResult
    llm_report: Any  # LLMAccessibilityReport
    llm_accessibility: float
    grade: str
    recommendations: list


class SeparateAnalyzer:
    """
    Provides separate scraper and LLM analysis functions.
    
    This allows users to run only scraper analysis, only LLM analysis,
    or both analyses independently.
    """
    
    def __init__(self, timeout: int = 30):
        """Initialize the separate analyzer."""
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
    
    def analyze_scraper_only(self, url: str, include_dynamic: bool = False) -> ScraperAnalysisResult:
        """
        Perform scraper-focused analysis only.
        
        Args:
            url: URL to analyze
            include_dynamic: Whether to include dynamic analysis (if supported)
            
        Returns:
            ScraperAnalysisResult with scraper-specific insights
        """
        self.logger.info(f"Starting scraper-only analysis for {url}")
        
        try:
            # Static Analysis
            static_analyzer = StaticAnalyzer(timeout=self.timeout)
            static_result = static_analyzer.analyze(url)
            
            if static_result.status != "success":
                error_msg = static_result.error_message or "Unknown error"
                raise Exception(f"Static analysis failed: {error_msg}")
            
            # Dynamic Analysis (optional)
            dynamic_result = None
            comparison = None
            
            if include_dynamic:
                try:
                    dynamic_analyzer = DynamicAnalyzer(timeout=self.timeout, headless=True)
                    dynamic_result = dynamic_analyzer.analyze(url)
                    
                    if dynamic_result.status == "success":
                        comparator = ContentComparator()
                        comparison = comparator.compare(static_result, dynamic_result)
                except Exception as e:
                    self.logger.warning(f"Dynamic analysis failed: {e}")
                    dynamic_result = None
            
            # Crawler Analysis
            crawler_analyzer = CrawlerAnalyzer()
            crawler_result = crawler_analyzer.analyze(url)
            static_result.crawler_analysis = crawler_result
            
            # Scoring (scraper-focused)
            scoring_engine = ScoringEngine()
            score = scoring_engine.calculate_score(static_result, comparison)
            
            # Extract scraper-specific recommendations
            scraper_recommendations = []
            for rec in score.recommendations:
                if rec.category in ["static_content", "semantic_html", "structured_data", "meta_tags", "crawler_accessibility"]:
                    scraper_recommendations.append(f"{rec.priority.value.upper()}: {rec.description}")
            
            return ScraperAnalysisResult(
                analysis_result=static_result,
                score=score,
                scraper_friendliness=score.scraper_friendliness.total_score,
                grade=score.scraper_friendliness.grade,
                recommendations=scraper_recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Scraper analysis failed: {e}")
            raise
    
    def analyze_llm_only(self, url: str) -> LLMAnalysisResult:
        """
        Perform LLM-focused analysis only.
        
        Args:
            url: URL to analyze
            
        Returns:
            LLMAnalysisResult with LLM-specific insights
        """
        self.logger.info(f"Starting LLM-only analysis for {url}")
        
        try:
            # Static Analysis (required for LLM analysis)
            static_analyzer = StaticAnalyzer(timeout=self.timeout)
            static_result = static_analyzer.analyze(url)
            
            if static_result.status != "success":
                error_msg = static_result.error_message or "Unknown error"
                raise Exception(f"Static analysis failed: {error_msg}")
            
            # LLM Accessibility Analysis
            llm_analyzer = LLMAccessibilityAnalyzer()
            llm_report = llm_analyzer.analyze(static_result)
            
            # Extract LLM-specific recommendations
            llm_recommendations = []
            for rec in llm_report.recommendations:
                llm_recommendations.append(rec)
            
            return LLMAnalysisResult(
                analysis_result=static_result,
                llm_report=llm_report,
                llm_accessibility=llm_report.overall_score,
                grade=llm_report.grade,
                recommendations=llm_recommendations
            )
            
        except Exception as e:
            self.logger.error(f"LLM analysis failed: {e}")
            raise
    
    def analyze_both(self, url: str, include_dynamic: bool = False) -> Tuple[ScraperAnalysisResult, LLMAnalysisResult]:
        """
        Perform both scraper and LLM analysis.
        
        Args:
            url: URL to analyze
            include_dynamic: Whether to include dynamic analysis (if supported)
            
        Returns:
            Tuple of (ScraperAnalysisResult, LLMAnalysisResult)
        """
        self.logger.info(f"Starting combined analysis for {url}")
        
        scraper_result = self.analyze_scraper_only(url, include_dynamic)
        llm_result = self.analyze_llm_only(url)
        
        return scraper_result, llm_result
    
    def get_analysis_summary(self, scraper_result: Optional[ScraperAnalysisResult] = None, 
                           llm_result: Optional[LLMAnalysisResult] = None) -> Dict[str, Any]:
        """
        Get a summary of analysis results.
        
        Args:
            scraper_result: Optional scraper analysis result
            llm_result: Optional LLM analysis result
            
        Returns:
            Summary dictionary
        """
        summary = {
            "scraper_analysis": {
                "performed": scraper_result is not None,
                "score": scraper_result.scraper_friendliness if scraper_result else None,
                "grade": scraper_result.grade if scraper_result else None,
                "recommendations_count": len(scraper_result.recommendations) if scraper_result else 0
            },
            "llm_analysis": {
                "performed": llm_result is not None,
                "score": llm_result.llm_accessibility if llm_result else None,
                "grade": llm_result.grade if llm_result else None,
                "recommendations_count": len(llm_result.recommendations) if llm_result else 0
            }
        }
        
        return summary
