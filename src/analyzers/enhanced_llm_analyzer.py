"""
Enhanced LLM Accessibility Analyzer

Based on comprehensive 2025 research on how LLMs read web content,
this analyzer provides detailed insights into LLM-specific accessibility
issues and recommendations.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import re

from ..models.analysis_result import AnalysisResult, ContentAnalysis, StructureAnalysis, MetaAnalysis, JavaScriptAnalysis, HiddenContent
from ..models.scoring_models import Priority

logger = logging.getLogger(__name__)


@dataclass
class LLMCrawlerCapability:
    """Defines specific LLM crawler capabilities and limitations"""
    name: str
    executes_javascript: bool
    uses_headless_browser: bool
    chunking_strategy: str
    vectorization_quality: str
    schema_preference: str
    real_time_access: bool
    limitations: List[str]


@dataclass
class LLMChunkingAnalysis:
    """Analysis of how content will be chunked for LLM processing"""
    semantic_boundaries: int
    heading_hierarchy_quality: float
    paragraph_structure: int
    list_structure: int
    table_structure: int
    chunking_score: float
    issues: List[str]
    recommendations: List[str]


@dataclass
class LLMSchemaAnalysis:
    """Analysis of structured data for LLM understanding"""
    json_ld_items: int
    microdata_items: int
    rdfa_items: int
    entity_types: List[str]
    schema_quality_score: float
    llm_benefits: List[str]
    missing_opportunities: List[str]


@dataclass
class LLMRenderingAnalysis:
    """Analysis of SSR vs CSR impact on LLM accessibility"""
    rendering_type: str
    initial_content_size: int
    javascript_dependency_score: float
    ssr_benefits: List[str]
    csr_limitations: List[str]
    framework_impact: str
    visibility_score: float


@dataclass
class EnhancedLLMReport:
    """Comprehensive LLM accessibility report with detailed insights"""
    overall_score: float
    grade: str
    
    # Core analysis components
    crawler_analysis: Dict[str, LLMCrawlerCapability]
    chunking_analysis: LLMChunkingAnalysis
    schema_analysis: LLMSchemaAnalysis
    rendering_analysis: LLMRenderingAnalysis
    
    # Detailed insights
    semantic_html_score: float
    content_structure_score: float
    javascript_impact_score: float
    css_visibility_analysis: Dict[str, Any]
    
    # Recommendations
    critical_recommendations: List[str]
    high_priority_recommendations: List[str]
    medium_priority_recommendations: List[str]
    
    # Technical details
    llms_txt_present: bool
    llms_txt_content: Optional[str]
    framework_detection: Dict[str, Any]
    
    # Citations and evidence
    evidence_sources: List[str]
    technical_explanations: Dict[str, str]


class EnhancedLLMAccessibilityAnalyzer:
    """
    Enhanced LLM accessibility analyzer based on 2025 research.
    
    Provides detailed analysis of how different LLMs will access and
    process website content, with specific focus on:
    - Crawler-specific capabilities and limitations
    - Content chunking and vectorization quality
    - SSR vs CSR impact on LLM visibility
    - Semantic HTML structure analysis
    - Schema.org markup effectiveness
    - JavaScript framework impact
    - CSS visibility issues
    """
    
    def __init__(self):
        """Initialize the enhanced LLM accessibility analyzer."""
        self.logger = logging.getLogger(__name__)
        
        # Define LLM crawler capabilities based on 2025 research
        self.llm_crawlers = {
            'gptbot': LLMCrawlerCapability(
                name='GPTBot (OpenAI)',
                executes_javascript=False,
                uses_headless_browser=False,
                chunking_strategy='Semantic HTML boundaries',
                vectorization_quality='High for static content',
                schema_preference='JSON-LD',
                real_time_access=True,
                limitations=[
                    'Cannot execute JavaScript',
                    'Limited to raw HTML content',
                    'Requires SSR for dynamic content',
                    '34% of requests result in 404 errors'
                ]
            ),
            'claudebot': LLMCrawlerCapability(
                name='ClaudeBot (Anthropic)',
                executes_javascript=False,
                uses_headless_browser=False,
                chunking_strategy='Semantic HTML boundaries',
                vectorization_quality='High for static content',
                schema_preference='JSON-LD',
                real_time_access=True,
                limitations=[
                    'Limited JavaScript execution',
                    'Prefers static HTML content',
                    'Web search feature launched March 2025',
                    'Conversational delivery of results'
                ]
            ),
            'googlebot': LLMCrawlerCapability(
                name='Googlebot (Gemini)',
                executes_javascript=True,
                uses_headless_browser=True,
                chunking_strategy='Advanced semantic analysis',
                vectorization_quality='Excellent with JS execution',
                schema_preference='JSON-LD + Microdata',
                real_time_access=True,
                limitations=[
                    'Higher resource requirements',
                    'May not execute all JS frameworks',
                    'Backed by Google Search index'
                ]
            ),
            'perplexity': LLMCrawlerCapability(
                name='Perplexity AI',
                executes_javascript=True,
                uses_headless_browser=True,
                chunking_strategy='Aggressive crawling',
                vectorization_quality='High with real-time access',
                schema_preference='JSON-LD',
                real_time_access=True,
                limitations=[
                    'Known for aggressive crawling',
                    'May use undeclared crawlers',
                    'Adapts to dynamic pages'
                ]
            )
        }
    
    def analyze(self, analysis_result: AnalysisResult) -> EnhancedLLMReport:
        """
        Perform comprehensive LLM accessibility analysis.
        
        Args:
            analysis_result: Complete analysis result from static/dynamic analysis
            
        Returns:
            Enhanced LLM accessibility report with detailed insights
        """
        self.logger.info("Starting enhanced LLM accessibility analysis...")
        
        # Extract components
        content = analysis_result.content_analysis
        structure = analysis_result.structure_analysis
        meta = analysis_result.meta_analysis
        js = analysis_result.javascript_analysis
        hidden_content = analysis_result.hidden_content
        
        # Perform detailed analysis
        crawler_analysis = self._analyze_crawler_capabilities(content, structure, js)
        chunking_analysis = self._analyze_content_chunking(content, structure)
        schema_analysis = self._analyze_schema_markup(meta)
        rendering_analysis = self._analyze_rendering_impact(content, js)
        
        # Calculate detailed scores
        semantic_html_score = self._calculate_semantic_html_score(structure)
        content_structure_score = self._calculate_content_structure_score(content, structure)
        javascript_impact_score = self._calculate_javascript_impact_score(js)
        css_visibility_analysis = self._analyze_css_visibility(hidden_content)
        
        # Check for llms.txt
        llms_txt_present, llms_txt_content = self._check_llms_txt(analysis_result.url)
        
        # Framework detection with LLM impact
        framework_detection = self._analyze_framework_llm_impact(js)
        
        # Generate comprehensive recommendations
        critical_recs, high_recs, medium_recs = self._generate_enhanced_recommendations(
            crawler_analysis, chunking_analysis, schema_analysis, rendering_analysis,
            semantic_html_score, javascript_impact_score, llms_txt_present
        )
        
        # Calculate overall score
        overall_score = self._calculate_enhanced_llm_score(
            semantic_html_score, content_structure_score, javascript_impact_score,
            chunking_analysis.chunking_score, schema_analysis.schema_quality_score,
            rendering_analysis.visibility_score
        )
        
        grade = self._calculate_grade(overall_score)
        
        # Technical explanations and evidence
        evidence_sources = self._get_evidence_sources()
        technical_explanations = self._get_technical_explanations()
        
        self.logger.info(f"Enhanced LLM accessibility analysis complete. Score: {overall_score:.1f} ({grade})")
        
        return EnhancedLLMReport(
            overall_score=overall_score,
            grade=grade,
            crawler_analysis=crawler_analysis,
            chunking_analysis=chunking_analysis,
            schema_analysis=schema_analysis,
            rendering_analysis=rendering_analysis,
            semantic_html_score=semantic_html_score,
            content_structure_score=content_structure_score,
            javascript_impact_score=javascript_impact_score,
            css_visibility_analysis=css_visibility_analysis,
            critical_recommendations=critical_recs,
            high_priority_recommendations=high_recs,
            medium_priority_recommendations=medium_recs,
            llms_txt_present=llms_txt_present,
            llms_txt_content=llms_txt_content,
            framework_detection=framework_detection,
            evidence_sources=evidence_sources,
            technical_explanations=technical_explanations
        )
    
    def _analyze_crawler_capabilities(self, content: ContentAnalysis, 
                                    structure: StructureAnalysis, 
                                    js: JavaScriptAnalysis) -> Dict[str, LLMCrawlerCapability]:
        """Analyze how different LLM crawlers will access the content."""
        crawler_analysis = {}
        
        for crawler_name, capability in self.llm_crawlers.items():
            # Calculate accessibility score for this crawler
            score = 100.0
            
            # JavaScript dependency penalty
            if not capability.executes_javascript and js and js.dynamic_content_detected:
                score -= 40  # Major penalty for JS-dependent content
            
            # Content structure bonus
            if structure and structure.semantic_elements:
                score += min(20, len(structure.semantic_elements) * 2)
            
            # Content quality bonus
            if content and content.word_count > 500:
                score += 10
            
            # Create analysis for this crawler
            crawler_analysis[crawler_name] = capability
        
        return crawler_analysis
    
    def _analyze_content_chunking(self, content: ContentAnalysis, 
                                structure: StructureAnalysis) -> LLMChunkingAnalysis:
        """Analyze how content will be chunked for LLM processing."""
        semantic_boundaries = 0
        heading_hierarchy_quality = 0.0
        paragraph_structure = 0
        list_structure = 0
        table_structure = 0
        issues = []
        recommendations = []
        
        if structure:
            # Count semantic boundaries
            semantic_boundaries = len(structure.semantic_elements)
            
            # Analyze heading hierarchy
            if structure.heading_hierarchy:
                h1_count = len(structure.heading_hierarchy.h1)
                h2_count = len(structure.heading_hierarchy.h2)
                h3_count = len(structure.heading_hierarchy.h3)
                
                # Good hierarchy: 1 H1, multiple H2s, some H3s
                if h1_count == 1 and h2_count > 0:
                    heading_hierarchy_quality = 0.9
                elif h1_count == 1:
                    heading_hierarchy_quality = 0.7
                elif h1_count > 1:
                    heading_hierarchy_quality = 0.3
                    issues.append("Multiple H1 tags confuse LLM chunking")
                    recommendations.append("Use only one H1 tag per page")
                else:
                    heading_hierarchy_quality = 0.1
                    issues.append("No H1 tag found")
                    recommendations.append("Add a descriptive H1 tag")
            
            # Count structural elements
            paragraph_structure = content.paragraphs if content else 0
            list_structure = content.lists if content else 0
            table_structure = content.tables if content else 0
        
        # Calculate chunking score
        chunking_score = (
            semantic_boundaries * 10 +
            heading_hierarchy_quality * 30 +
            min(paragraph_structure * 2, 20) +
            min(list_structure * 3, 15) +
            min(table_structure * 5, 15)
        )
        
        return LLMChunkingAnalysis(
            semantic_boundaries=semantic_boundaries,
            heading_hierarchy_quality=heading_hierarchy_quality,
            paragraph_structure=paragraph_structure,
            list_structure=list_structure,
            table_structure=table_structure,
            chunking_score=min(chunking_score, 100),
            issues=issues,
            recommendations=recommendations
        )
    
    def _analyze_schema_markup(self, meta: MetaAnalysis) -> LLMSchemaAnalysis:
        """Analyze Schema.org markup effectiveness for LLMs."""
        json_ld_items = 0
        microdata_items = 0
        rdfa_items = 0
        entity_types = []
        llm_benefits = []
        missing_opportunities = []
        
        if meta and meta.structured_data:
            for item in meta.structured_data:
                if item.type == 'json-ld':
                    json_ld_items += 1
                elif item.type == 'microdata':
                    microdata_items += 1
                elif item.type == 'rdfa':
                    rdfa_items += 1
                
                # Extract entity types
                if hasattr(item, 'data') and isinstance(item.data, dict):
                    entity_type = item.data.get('@type', '')
                    if entity_type:
                        entity_types.append(entity_type)
        
        # Calculate schema quality score
        schema_quality_score = (
            json_ld_items * 15 +  # JSON-LD is most widely supported
            microdata_items * 10 +
            rdfa_items * 8 +
            len(set(entity_types)) * 5  # Bonus for variety
        )
        
        # Generate benefits and opportunities
        if json_ld_items > 0:
            llm_benefits.append("JSON-LD markup improves LLM entity recognition")
        if 'Product' in entity_types:
            llm_benefits.append("Product schema helps LLMs understand commerce context")
        if 'Organization' in entity_types:
            llm_benefits.append("Organization schema improves brand recognition")
        
        if json_ld_items == 0:
            missing_opportunities.append("Add JSON-LD structured data for better LLM understanding")
        if 'Article' not in entity_types and 'BlogPosting' not in entity_types:
            missing_opportunities.append("Consider adding Article schema for content pages")
        
        return LLMSchemaAnalysis(
            json_ld_items=json_ld_items,
            microdata_items=microdata_items,
            rdfa_items=rdfa_items,
            entity_types=entity_types,
            schema_quality_score=min(schema_quality_score, 100),
            llm_benefits=llm_benefits,
            missing_opportunities=missing_opportunities
        )
    
    def _analyze_rendering_impact(self, content: ContentAnalysis, 
                                js: JavaScriptAnalysis) -> LLMRenderingAnalysis:
        """Analyze SSR vs CSR impact on LLM accessibility."""
        rendering_type = "Unknown"
        initial_content_size = content.character_count if content else 0
        javascript_dependency_score = 0.0
        ssr_benefits = []
        csr_limitations = []
        framework_impact = "None detected"
        visibility_score = 100.0
        
        if js:
            # Determine rendering type based on JavaScript analysis
            if js.is_spa:
                rendering_type = "CSR (Client-Side Rendering)"
                javascript_dependency_score = 0.2  # Very low
                csr_limitations = [
                    "Content requires JavaScript execution",
                    "Most AI crawlers cannot access dynamic content",
                    "Poor chunking due to minimal initial HTML",
                    "Delayed content availability"
                ]
                visibility_score = 20.0
            elif js.dynamic_content_detected:
                rendering_type = "Hybrid (SSR + Dynamic)"
                javascript_dependency_score = 0.6
                ssr_benefits = ["Core content available in initial HTML"]
                csr_limitations = ["Some content requires JavaScript"]
                visibility_score = 70.0
            else:
                rendering_type = "SSR (Server-Side Rendering)"
                javascript_dependency_score = 0.9
                ssr_benefits = [
                    "Complete HTML in initial response",
                    "Excellent LLM crawler visibility",
                    "Optimal chunking and vectorization",
                    "Fast content availability"
                ]
                visibility_score = 95.0
            
            # Framework impact analysis
            if js.frameworks:
                framework_names = [fw.name for fw in js.frameworks]
                if 'React' in framework_names and js.is_spa:
                    framework_impact = "React SPA - Poor LLM accessibility"
                elif 'Next.js' in framework_names:
                    framework_impact = "Next.js - Good SSR support"
                elif 'Vue' in framework_names and js.is_spa:
                    framework_impact = "Vue SPA - Poor LLM accessibility"
                elif 'Nuxt' in framework_names:
                    framework_impact = "Nuxt - Good SSR support"
        
        return LLMRenderingAnalysis(
            rendering_type=rendering_type,
            initial_content_size=initial_content_size,
            javascript_dependency_score=javascript_dependency_score,
            ssr_benefits=ssr_benefits,
            csr_limitations=csr_limitations,
            framework_impact=framework_impact,
            visibility_score=visibility_score
        )
    
    def _calculate_semantic_html_score(self, structure: StructureAnalysis) -> float:
        """Calculate semantic HTML score for LLM accessibility."""
        if not structure:
            return 0.0
        
        score = 0.0
        
        # Semantic elements bonus
        if structure.semantic_elements:
            score += min(30, len(structure.semantic_elements) * 3)
        
        # Heading hierarchy bonus
        if structure.heading_hierarchy:
            total_headings = len(structure.heading_hierarchy.h1 + 
                               structure.heading_hierarchy.h2 + 
                               structure.heading_hierarchy.h3)
            score += min(25, total_headings * 2)
        
        # Proper nesting bonus
        if structure.nested_depth <= 10:
            score += 20
        elif structure.nested_depth <= 20:
            score += 10
        
        return min(score, 100.0)
    
    def _calculate_content_structure_score(self, content: ContentAnalysis, 
                                        structure: StructureAnalysis) -> float:
        """Calculate content structure score for LLM processing."""
        score = 0.0
        
        if content:
            # Word count bonus
            if content.word_count > 1000:
                score += 25
            elif content.word_count > 500:
                score += 15
            elif content.word_count > 200:
                score += 10
            
            # Paragraph structure bonus
            if content.paragraphs > 5:
                score += 20
            elif content.paragraphs > 2:
                score += 10
            
            # List structure bonus
            if content.lists > 0:
                score += 15
            
            # Table structure bonus
            if content.tables > 0:
                score += 10
        
        return min(score, 100.0)
    
    def _calculate_javascript_impact_score(self, js: JavaScriptAnalysis) -> float:
        """Calculate JavaScript impact score (higher = better for LLMs)."""
        if not js:
            return 100.0  # No JS = perfect for LLMs
        
        score = 100.0
        
        # Penalty for dynamic content
        if js.dynamic_content_detected:
            score -= 30
        
        # Penalty for SPA
        if js.is_spa:
            score -= 40
        
        # Penalty for AJAX
        if js.has_ajax:
            score -= 20
        
        # Penalty for high script count
        if js.total_scripts > 10:
            score -= 15
        elif js.total_scripts > 5:
            score -= 10
        
        return max(score, 0.0)
    
    def _analyze_css_visibility(self, hidden_content: Optional[HiddenContent]) -> Dict[str, Any]:
        """Analyze CSS visibility issues for LLM accessibility."""
        analysis = {
            'display_none_elements': 0,
            'visibility_hidden_elements': 0,
            'total_hidden_elements': 0,
            'llm_impact': 'None',
            'explanation': 'CSS hiding does not affect LLM accessibility',
            'recommendations': []
        }
        
        if hidden_content:
            analysis['display_none_elements'] = hidden_content.display_none_count
            analysis['visibility_hidden_elements'] = hidden_content.visibility_hidden_count
            analysis['total_hidden_elements'] = len(hidden_content.hidden_elements)
            
            if hidden_content.hidden_elements:
                analysis['llm_impact'] = 'None - LLMs can still access hidden content'
                analysis['explanation'] = 'CSS hiding (display:none, visibility:hidden) does not affect scraper accessibility. LLMs can still read hidden content.'
                analysis['recommendations'] = [
                    'CSS hiding only affects human visibility',
                    'Use server-side logic to hide sensitive content from LLMs',
                    'Consider using robots.txt or llms.txt for content control'
                ]
        
        return analysis
    
    def _check_llms_txt(self, url: str) -> Tuple[bool, Optional[str]]:
        """Check for llms.txt file presence."""
        # This would typically make an HTTP request to check for llms.txt
        # For now, return False as we don't have HTTP client in this analyzer
        return False, None
    
    def _analyze_framework_llm_impact(self, js: JavaScriptAnalysis) -> Dict[str, Any]:
        """Analyze JavaScript framework impact on LLM accessibility."""
        analysis = {
            'frameworks_detected': [],
            'llm_accessibility': 'Good',
            'recommendations': [],
            'ssr_support': []
        }
        
        if js and js.frameworks:
            framework_names = [fw.name for fw in js.frameworks]
            analysis['frameworks_detected'] = framework_names
            
            # Analyze each framework's LLM impact
            for framework in framework_names:
                if framework in ['Next.js', 'Nuxt', 'SvelteKit']:
                    analysis['ssr_support'].append(f"{framework} - Good SSR support")
                    analysis['recommendations'].append(f"Ensure {framework} SSR is properly configured")
                elif framework in ['React', 'Vue', 'Angular'] and js.is_spa:
                    analysis['llm_accessibility'] = 'Poor'
                    analysis['recommendations'].append(f"Consider SSR implementation for {framework}")
                elif framework == 'Gatsby':
                    analysis['ssr_support'].append("Gatsby - Static generation")
                    analysis['recommendations'].append("Ensure Gatsby generates static HTML")
        
        return analysis
    
    def _generate_enhanced_recommendations(self, crawler_analysis: Dict[str, LLMCrawlerCapability],
                                         chunking_analysis: LLMChunkingAnalysis,
                                         schema_analysis: LLMSchemaAnalysis,
                                         rendering_analysis: LLMRenderingAnalysis,
                                         semantic_html_score: float,
                                         javascript_impact_score: float,
                                         llms_txt_present: bool) -> Tuple[List[str], List[str], List[str]]:
        """Generate comprehensive recommendations based on 2025 LLM research."""
        critical_recs = []
        high_recs = []
        medium_recs = []
        
        # Critical recommendations
        if rendering_analysis.rendering_type == "CSR (Client-Side Rendering)":
            critical_recs.append("CRITICAL: Implement SSR - Most AI crawlers cannot execute JavaScript")
            critical_recs.append("CRITICAL: Add server-side rendering for core content pages")
        
        if javascript_impact_score < 30:
            critical_recs.append("CRITICAL: Reduce JavaScript dependency - LLMs cannot execute JS")
        
        if chunking_analysis.heading_hierarchy_quality < 0.5:
            critical_recs.append("CRITICAL: Fix heading hierarchy - Essential for LLM chunking")
        
        # High priority recommendations
        if semantic_html_score < 70:
            high_recs.append("HIGH: Use semantic HTML elements (article, section, nav) for better chunking")
        
        if schema_analysis.schema_quality_score < 50:
            high_recs.append("HIGH: Add JSON-LD structured data - Significantly improves LLM understanding")
        
        if not llms_txt_present:
            high_recs.append("HIGH: Create llms.txt file to guide AI crawlers to important content")
        
        if chunking_analysis.issues:
            for issue in chunking_analysis.issues:
                high_recs.append(f"HIGH: {issue}")
        
        # Medium priority recommendations
        if chunking_analysis.chunking_score < 80:
            medium_recs.append("MEDIUM: Improve content structure for better LLM chunking")
        
        if schema_analysis.missing_opportunities:
            medium_recs.extend(schema_analysis.missing_opportunities)
        
        if rendering_analysis.ssr_benefits:
            medium_recs.append("MEDIUM: Consider implementing SSR for better LLM visibility")
        
        return critical_recs, high_recs, medium_recs
    
    def _calculate_enhanced_llm_score(self, semantic_html_score: float,
                                    content_structure_score: float,
                                    javascript_impact_score: float,
                                    chunking_score: float,
                                    schema_score: float,
                                    visibility_score: float) -> float:
        """Calculate comprehensive LLM accessibility score."""
        # Weighted average based on 2025 research importance
        weights = {
            'semantic_html': 0.25,
            'content_structure': 0.20,
            'javascript_impact': 0.25,
            'chunking': 0.15,
            'schema': 0.10,
            'visibility': 0.05
        }
        
        overall_score = (
            semantic_html_score * weights['semantic_html'] +
            content_structure_score * weights['content_structure'] +
            javascript_impact_score * weights['javascript_impact'] +
            chunking_score * weights['chunking'] +
            schema_score * weights['schema'] +
            visibility_score * weights['visibility']
        )
        
        return min(overall_score, 100.0)
    
    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from score."""
        if score >= 97:
            return "A+"
        elif score >= 93:
            return "A"
        elif score >= 90:
            return "A-"
        elif score >= 87:
            return "B+"
        elif score >= 83:
            return "B"
        elif score >= 80:
            return "B-"
        elif score >= 77:
            return "C+"
        elif score >= 73:
            return "C"
        elif score >= 70:
            return "C-"
        elif score >= 67:
            return "D+"
        elif score >= 63:
            return "D"
        elif score >= 60:
            return "D-"
        else:
            return "F"
    
    def _get_evidence_sources(self) -> List[str]:
        """Get evidence sources for LLM analysis."""
        return [
            "OpenAI GPTBot documentation - JavaScript execution limitations",
            "Anthropic ClaudeBot research - Static HTML preference",
            "Google Gemini integration - Enhanced JavaScript support",
            "Perplexity AI analysis - Aggressive crawling patterns",
            "2025 LLM accessibility research - SSR vs CSR impact",
            "Schema.org markup effectiveness studies",
            "Semantic HTML chunking research",
            "CSS visibility impact on scrapers"
        ]
    
    def _get_technical_explanations(self) -> Dict[str, str]:
        """Get technical explanations for LLM analysis."""
        return {
            "javascript_execution": "Most AI crawlers (GPTBot, ClaudeBot) do not execute JavaScript, making SSR critical for content visibility",
            "chunking_process": "LLMs chunk content based on semantic HTML boundaries. Poor structure creates poor chunks, degrading understanding",
            "vectorization": "Content is converted to numeric vectors for similarity search. Clear, structured content creates better vectors",
            "schema_markup": "JSON-LD structured data significantly improves LLM entity recognition and citation accuracy",
            "css_visibility": "CSS hiding (display:none, visibility:hidden) does not affect scraper accessibility - only human visibility",
            "ssr_benefits": "SSR delivers complete HTML in initial response, enabling proper crawling, chunking, and vectorization",
            "framework_impact": "JavaScript frameworks like React/Vue SPAs are invisible to most AI crawlers without SSR implementation"
        }
