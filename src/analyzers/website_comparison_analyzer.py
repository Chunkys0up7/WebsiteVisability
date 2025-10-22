"""
Website Comparison Analyzer

Compares two websites across various dimensions including content,
structure, accessibility, and bot directives.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from ..models.analysis_result import AnalysisResult
from .bot_directives_analyzer import BotDirectivesAnalysis

logger = logging.getLogger(__name__)


@dataclass
class ContentComparison:
    """Comparison of content between two websites"""
    word_count_diff: int
    semantic_elements_diff: int
    links_diff: int
    images_diff: int
    tables_diff: int
    lists_diff: int
    text_similarity_score: float
    structure_similarity_score: float
    key_differences: List[str]


@dataclass
class AccessibilityComparison:
    """Comparison of accessibility features"""
    llm_score_diff: float
    scraper_score_diff: float
    ssr_comparison: str
    bot_directives_comparison: Dict[str, Any]
    key_differences: List[str]


@dataclass
class TechnicalComparison:
    """Comparison of technical aspects"""
    js_usage_diff: Dict[str, Any]
    meta_tags_diff: Dict[str, Any]
    structured_data_diff: Dict[str, Any]
    key_differences: List[str]


@dataclass
class WebsiteComparisonResult:
    """Complete comparison results between two websites"""
    timestamp: str
    url1: str
    url2: str
    content_comparison: ContentComparison
    accessibility_comparison: AccessibilityComparison
    technical_comparison: TechnicalComparison
    overall_similarity_score: float
    key_insights: List[str]
    recommendations: List[str]


class WebsiteComparisonAnalyzer:
    """
    Analyzes and compares two websites across multiple dimensions.
    
    Provides detailed insights into differences in content, structure,
    accessibility, and technical implementation.
    """
    
    def __init__(self):
        """Initialize the website comparison analyzer."""
        self.logger = logging.getLogger(__name__)
    
    def compare(
        self,
        url1: str,
        url2: str,
        analysis1: AnalysisResult,
        analysis2: AnalysisResult,
        bot_directives1: Optional[BotDirectivesAnalysis] = None,
        bot_directives2: Optional[BotDirectivesAnalysis] = None,
        llm_score1: Optional[float] = None,
        llm_score2: Optional[float] = None,
        scraper_score1: Optional[float] = None,
        scraper_score2: Optional[float] = None
    ) -> WebsiteComparisonResult:
        """
        Compare two websites based on their analysis results.
        
        Args:
            url1: URL of first website
            url2: URL of second website
            analysis1: Analysis results for first website
            analysis2: Analysis results for second website
            bot_directives1: Bot directives analysis for first website
            bot_directives2: Bot directives analysis for second website
            llm_score1: LLM accessibility score for first website
            llm_score2: LLM accessibility score for second website
            scraper_score1: Scraper friendliness score for first website
            scraper_score2: Scraper friendliness score for second website
            
        Returns:
            Detailed comparison results
        """
        self.logger.info(f"Starting comparison between {url1} and {url2}")
        
        # Validate inputs
        if not analysis1 or not analysis2:
            raise ValueError("Both analysis results must be provided")
        
        # Compare content
        content_comparison = self._compare_content(analysis1, analysis2)
        
        # Compare accessibility
        accessibility_comparison = self._compare_accessibility(
            bot_directives1,
            bot_directives2,
            llm_score1,
            llm_score2,
            scraper_score1,
            scraper_score2,
            analysis1,
            analysis2
        )
        
        # Compare technical aspects
        technical_comparison = self._compare_technical(analysis1, analysis2)
        
        # Calculate overall similarity
        similarity_score = self._calculate_similarity(
            content_comparison,
            accessibility_comparison,
            technical_comparison
        )
        
        # Generate insights and recommendations
        key_insights = self._generate_insights(
            content_comparison,
            accessibility_comparison,
            technical_comparison,
            similarity_score
        )
        
        recommendations = self._generate_recommendations(
            content_comparison,
            accessibility_comparison,
            technical_comparison
        )
        
        return WebsiteComparisonResult(
            timestamp=datetime.now().isoformat(),
            url1=url1,
            url2=url2,
            content_comparison=content_comparison,
            accessibility_comparison=accessibility_comparison,
            technical_comparison=technical_comparison,
            overall_similarity_score=similarity_score,
            key_insights=key_insights,
            recommendations=recommendations
        )
    
    def _safe_get_content_analysis(self, analysis: AnalysisResult) -> Dict[str, Any]:
        """Safely get content analysis data with defaults."""
        if not hasattr(analysis, 'content_analysis'):
            return {
                'word_count': 0,
                'links': 0,
                'images': 0,
                'tables': 0,
                'lists': 0,
                'text_content': ''
            }
        return {
            'word_count': getattr(analysis.content_analysis, 'word_count', 0),
            'links': getattr(analysis.content_analysis, 'links', 0),
            'images': getattr(analysis.content_analysis, 'images', 0),
            'tables': getattr(analysis.content_analysis, 'tables', 0),
            'lists': getattr(analysis.content_analysis, 'lists', 0),
            'text_content': getattr(analysis.content_analysis, 'text_content', '')
        }
    
    def _safe_get_structure_analysis(self, analysis: AnalysisResult) -> Dict[str, Any]:
        """Safely get structure analysis data with defaults."""
        if not hasattr(analysis, 'structure_analysis'):
            return {'semantic_elements': []}
        return {
            'semantic_elements': getattr(analysis.structure_analysis, 'semantic_elements', [])
        }
    
    def _safe_get_ssr_detection(self, analysis: AnalysisResult) -> Dict[str, Any]:
        """Safely get SSR detection data with defaults."""
        if not hasattr(analysis, 'ssr_detection'):
            return {'is_ssr': None, 'confidence': 0.0}
        return {
            'is_ssr': getattr(analysis.ssr_detection, 'is_ssr', None),
            'confidence': getattr(analysis.ssr_detection, 'confidence', 0.0)
        }
    
    def _compare_content(
        self, analysis1: AnalysisResult, analysis2: AnalysisResult
    ) -> ContentComparison:
        """Compare content between two websites."""
        content1 = self._safe_get_content_analysis(analysis1)
        content2 = self._safe_get_content_analysis(analysis2)
        structure1 = self._safe_get_structure_analysis(analysis1)
        structure2 = self._safe_get_structure_analysis(analysis2)
        
        # Calculate differences
        word_count_diff = content2['word_count'] - content1['word_count']
        semantic_elements_diff = len(structure2['semantic_elements']) - len(structure1['semantic_elements'])
        links_diff = content2['links'] - content1['links']
        images_diff = content2['images'] - content1['images']
        tables_diff = content2['tables'] - content1['tables']
        lists_diff = content2['lists'] - content1['lists']
        
        # Calculate similarity scores
        text_similarity = self._calculate_text_similarity(
            content1['text_content'],
            content2['text_content']
        )
        
        structure_similarity = self._calculate_structure_similarity(
            structure1['semantic_elements'],
            structure2['semantic_elements']
        )
        
        # Identify key differences
        key_differences = []
        
        if abs(word_count_diff) > content1['word_count'] * 0.2:  # 20% difference
            key_differences.append(
                f"Significant word count difference: {'more' if word_count_diff > 0 else 'fewer'} "
                f"words in second site ({abs(word_count_diff)} difference)"
            )
        
        if abs(semantic_elements_diff) > 2:
            key_differences.append(
                f"Different semantic structure: {'more' if semantic_elements_diff > 0 else 'fewer'} "
                f"semantic elements in second site ({abs(semantic_elements_diff)} difference)"
            )
        
        if abs(links_diff) > content1['links'] * 0.2:
            key_differences.append(
                f"Different link density: {'more' if links_diff > 0 else 'fewer'} "
                f"links in second site ({abs(links_diff)} difference)"
            )
        
        return ContentComparison(
            word_count_diff=word_count_diff,
            semantic_elements_diff=semantic_elements_diff,
            links_diff=links_diff,
            images_diff=images_diff,
            tables_diff=tables_diff,
            lists_diff=lists_diff,
            text_similarity_score=text_similarity,
            structure_similarity_score=structure_similarity,
            key_differences=key_differences
        )
    
    def _compare_accessibility(
        self,
        bot_directives1: Optional[BotDirectivesAnalysis],
        bot_directives2: Optional[BotDirectivesAnalysis],
        llm_score1: Optional[float],
        llm_score2: Optional[float],
        scraper_score1: Optional[float],
        scraper_score2: Optional[float],
        analysis1: AnalysisResult,
        analysis2: AnalysisResult
    ) -> AccessibilityComparison:
        """Compare accessibility features between two websites."""
        # Calculate score differences
        llm_score_diff = (llm_score2 - llm_score1) if (llm_score1 and llm_score2) else 0
        scraper_score_diff = (scraper_score2 - scraper_score1) if (scraper_score1 and scraper_score2) else 0
        
        # Compare SSR detection
        ssr_comparison = "Both sites use similar rendering methods"
        ssr1 = self._safe_get_ssr_detection(analysis1)
        ssr2 = self._safe_get_ssr_detection(analysis2)
        
        # Compare SSR status if we have valid data
        if ssr1['is_ssr'] is not None and ssr2['is_ssr'] is not None:
            if ssr1['confidence'] > 0.5 and ssr2['confidence'] > 0.5 and ssr1['is_ssr'] != ssr2['is_ssr']:
                ssr_comparison = (
                    f"Different rendering methods: {'SSR' if ssr1['is_ssr'] else 'CSR'} "
                    f"vs {'SSR' if ssr2['is_ssr'] else 'CSR'} "
                    f"(confidence: {ssr1['confidence']:.1%} vs {ssr2['confidence']:.1%})"
                )
            elif ssr1['confidence'] <= 0.5 or ssr2['confidence'] <= 0.5:
                ssr_comparison = "Rendering methods unclear due to low confidence in detection"
        else:
            ssr_comparison = "SSR detection data not available for comparison"
        
        # Compare bot directives
        bot_directives_comparison = {}
        if bot_directives1 and bot_directives2:
            bot_directives_comparison = {
                "robots_txt_present": [
                    bot_directives1.robots_txt.is_present,
                    bot_directives2.robots_txt.is_present
                ],
                "llms_txt_present": [
                    bot_directives1.llms_txt.is_present,
                    bot_directives2.llms_txt.is_present
                ],
                "compatibility_score_diff": (
                    bot_directives2.compatibility_score -
                    bot_directives1.compatibility_score
                )
            }
        
        # Identify key differences
        key_differences = []
        
        if abs(llm_score_diff) > 10:
            key_differences.append(
                f"Significant LLM accessibility difference: {'better' if llm_score_diff > 0 else 'worse'} "
                f"in second site ({abs(llm_score_diff):.1f} points)"
            )
        
        if abs(scraper_score_diff) > 10:
            key_differences.append(
                f"Significant scraper friendliness difference: {'better' if scraper_score_diff > 0 else 'worse'} "
                f"in second site ({abs(scraper_score_diff):.1f} points)"
            )
        
        # Add SSR comparison to key differences if we have valid data
        if ssr1['is_ssr'] is not None and ssr2['is_ssr'] is not None:
            if ssr1['confidence'] > 0.5 and ssr2['confidence'] > 0.5 and ssr1['is_ssr'] != ssr2['is_ssr']:
                key_differences.append(
                    f"Different rendering methods detected with high confidence: "
                    f"{'SSR' if ssr1['is_ssr'] else 'CSR'} vs {'SSR' if ssr2['is_ssr'] else 'CSR'}"
                )
        
        if bot_directives1 and bot_directives2:
            if bot_directives1.robots_txt.is_present != bot_directives2.robots_txt.is_present:
                key_differences.append(
                    f"robots.txt {'missing in first' if bot_directives2.robots_txt.is_present else 'missing in second'} site"
                )
            
            if bot_directives1.llms_txt.is_present != bot_directives2.llms_txt.is_present:
                key_differences.append(
                    f"llms.txt {'missing in first' if bot_directives2.llms_txt.is_present else 'missing in second'} site"
                )
        
        return AccessibilityComparison(
            llm_score_diff=llm_score_diff,
            scraper_score_diff=scraper_score_diff,
            ssr_comparison=ssr_comparison,
            bot_directives_comparison=bot_directives_comparison,
            key_differences=key_differences
        )
    
    def _compare_technical(
        self, analysis1: AnalysisResult, analysis2: AnalysisResult
    ) -> TechnicalComparison:
        """Compare technical aspects between two websites."""
        js1 = getattr(analysis1, 'javascript_analysis', None)
        js2 = getattr(analysis2, 'javascript_analysis', None)
        meta1 = getattr(analysis1, 'meta_analysis', None)
        meta2 = getattr(analysis2, 'meta_analysis', None)
        
        # Compare JavaScript usage
        js_usage_diff = {
            "total_scripts_diff": getattr(js2, 'total_scripts', 0) - getattr(js1, 'total_scripts', 0),
            "frameworks": [],  # Initialize empty list
            "spa_difference": getattr(js2, 'is_spa', False) != getattr(js1, 'is_spa', False),
            "dynamic_content_difference": getattr(js2, 'dynamic_content_detected', False) != getattr(js1, 'dynamic_content_detected', False)
        }
        
        # Safely handle framework comparison
        frameworks1 = getattr(js1, 'frameworks', []) or []
        frameworks2 = getattr(js2, 'frameworks', []) or []
        framework_names1 = {f.name for f in frameworks1}
        framework_names2 = {f.name for f in frameworks2}
        js_usage_diff["frameworks"] = [name for name in framework_names2 if name not in framework_names1]
        
        # Compare meta tags
        meta_tags_diff = {
            "title_present": [bool(getattr(meta1, 'title', None)), bool(getattr(meta2, 'title', None))],
            "description_present": [bool(getattr(meta1, 'description', None)), bool(getattr(meta2, 'description', None))],
            "og_tags_diff": len(getattr(meta2, 'open_graph_tags', [])) - len(getattr(meta1, 'open_graph_tags', [])),
            "twitter_tags_diff": len(getattr(meta2, 'twitter_card_tags', [])) - len(getattr(meta1, 'twitter_card_tags', []))
        }
        
        # Compare structured data
        structured_data_diff = {
            "json_ld_diff": len(getattr(meta2, 'json_ld', [])) - len(getattr(meta1, 'json_ld', [])),
            "microdata_diff": len(getattr(meta2, 'microdata', [])) - len(getattr(meta1, 'microdata', [])),
            "rdfa_diff": len(getattr(meta2, 'rdfa', [])) - len(getattr(meta1, 'rdfa', []))
        }
        
        # Identify key differences
        key_differences = []
        
        if abs(js_usage_diff["total_scripts_diff"]) > 5:
            key_differences.append(
                f"Significant difference in JavaScript usage: {'more' if js_usage_diff['total_scripts_diff'] > 0 else 'fewer'} "
                f"scripts in second site ({abs(js_usage_diff['total_scripts_diff'])} difference)"
            )
        
        if js_usage_diff["frameworks"]:
            key_differences.append(
                f"Different JavaScript frameworks: {', '.join(js_usage_diff['frameworks'])} "
                "present in second site but not in first"
            )
        
        if js_usage_diff["spa_difference"]:
            key_differences.append(
                "Different application architecture: "
                f"{'SPA' if getattr(js2, 'is_spa', False) else 'Traditional'} vs {'SPA' if getattr(js1, 'is_spa', False) else 'Traditional'}"
            )
        
        if not meta_tags_diff["title_present"][0] and meta_tags_diff["title_present"][1]:
            key_differences.append("Second site has title meta tag while first does not")
        elif meta_tags_diff["title_present"][0] and not meta_tags_diff["title_present"][1]:
            key_differences.append("First site has title meta tag while second does not")
        
        if abs(meta_tags_diff["og_tags_diff"]) > 2:
            key_differences.append(
                f"Different Open Graph tag usage: {'more' if meta_tags_diff['og_tags_diff'] > 0 else 'fewer'} "
                f"tags in second site ({abs(meta_tags_diff['og_tags_diff'])} difference)"
            )
        
        total_structured_data_diff = (
            structured_data_diff["json_ld_diff"] +
            structured_data_diff["microdata_diff"] +
            structured_data_diff["rdfa_diff"]
        )
        if abs(total_structured_data_diff) > 2:
            key_differences.append(
                f"Different structured data usage: {'more' if total_structured_data_diff > 0 else 'fewer'} "
                f"items in second site ({abs(total_structured_data_diff)} difference)"
            )
        
        return TechnicalComparison(
            js_usage_diff=js_usage_diff,
            meta_tags_diff=meta_tags_diff,
            structured_data_diff=structured_data_diff,
            key_differences=key_differences
        )
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity score between two text contents."""
        # Simple implementation using word overlap
        # For production, consider using more sophisticated methods
        if not text1 or not text2:
            return 0.0
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) * 100
    
    def _calculate_structure_similarity(
        self,
        elements1: List[str],
        elements2: List[str]
    ) -> float:
        """Calculate similarity score between two HTML structures."""
        # Compare semantic elements
        if not elements1 or not elements2:
            return 0.0
        
        intersection = set(elements1).intersection(set(elements2))
        union = set(elements1).union(set(elements2))
        
        return len(intersection) / len(union) * 100
    
    def _calculate_similarity(
        self,
        content_comparison: ContentComparison,
        accessibility_comparison: AccessibilityComparison,
        technical_comparison: TechnicalComparison
    ) -> float:
        """Calculate overall similarity score between two websites."""
        scores = []
        
        # Content similarity (40% weight)
        content_score = (
            content_comparison.text_similarity_score * 0.6 +
            content_comparison.structure_similarity_score * 0.4
        )
        scores.append(content_score * 0.4)
        
        # Accessibility similarity (30% weight)
        accessibility_score = 100.0
        if accessibility_comparison.llm_score_diff:
            accessibility_score -= abs(accessibility_comparison.llm_score_diff)
        if accessibility_comparison.scraper_score_diff:
            accessibility_score -= abs(accessibility_comparison.scraper_score_diff)
        accessibility_score = max(0.0, accessibility_score)
        scores.append(accessibility_score * 0.3)
        
        # Technical similarity (30% weight)
        technical_score = 100.0
        technical_score -= len(technical_comparison.key_differences) * 10
        technical_score = max(0.0, technical_score)
        scores.append(technical_score * 0.3)
        
        return sum(scores)
    
    def _generate_insights(
        self,
        content_comparison: ContentComparison,
        accessibility_comparison: AccessibilityComparison,
        technical_comparison: TechnicalComparison,
        similarity_score: float
    ) -> List[str]:
        """Generate key insights from the comparison."""
        insights = []
        
        # Overall similarity
        insights.append(
            f"Overall similarity: {similarity_score:.1f}% - "
            f"{'Very similar' if similarity_score > 80 else 'Somewhat similar' if similarity_score > 50 else 'Quite different'} websites"
        )
        
        # Content insights
        if content_comparison.key_differences:
            insights.append("Content differences:")
            insights.extend([f"• {diff}" for diff in content_comparison.key_differences])
        
        # Accessibility insights
        if accessibility_comparison.key_differences:
            insights.append("Accessibility differences:")
            insights.extend([f"• {diff}" for diff in accessibility_comparison.key_differences])
        
        # Technical insights
        if technical_comparison.key_differences:
            insights.append("Technical differences:")
            insights.extend([f"• {diff}" for diff in technical_comparison.key_differences])
        
        return insights
    
    def _generate_recommendations(
        self,
        content_comparison: ContentComparison,
        accessibility_comparison: AccessibilityComparison,
        technical_comparison: TechnicalComparison
    ) -> List[str]:
        """Generate recommendations based on the comparison."""
        recommendations = []
        
        # Content recommendations
        if content_comparison.word_count_diff < 0:
            recommendations.append(
                "Consider adding more content to match the depth of the second website"
            )
        if content_comparison.semantic_elements_diff < 0:
            recommendations.append(
                "Improve semantic structure by adding more semantic HTML elements"
            )
        
        # Accessibility recommendations
        if accessibility_comparison.llm_score_diff < 0:
            recommendations.append(
                "Improve LLM accessibility to match or exceed the second website"
            )
        if accessibility_comparison.scraper_score_diff < 0:
            recommendations.append(
                "Enhance scraper friendliness to match or exceed the second website"
            )
        
        # Technical recommendations
        js_diff = technical_comparison.js_usage_diff["total_scripts_diff"]
        if abs(js_diff) > 5:
            if js_diff > 0:
                recommendations.append(
                    "Consider optimizing JavaScript usage to reduce script count"
                )
            else:
                recommendations.append(
                    "Consider if additional JavaScript functionality would improve user experience"
                )
        
        # Meta tags
        meta_diff = technical_comparison.meta_tags_diff
        if not meta_diff["title_present"][0] and meta_diff["title_present"][1]:
            recommendations.append("Add a title meta tag to improve SEO")
        if not meta_diff["description_present"][0] and meta_diff["description_present"][1]:
            recommendations.append("Add a meta description to improve SEO")
        
        return recommendations