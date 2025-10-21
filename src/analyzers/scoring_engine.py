"""
Scoring Engine Module

Calculates scraper-friendliness and LLM accessibility scores.
Generates actionable recommendations for optimization.
"""

import logging
from typing import List, Optional

from ..models.analysis_result import AnalysisResult, ContentComparison
from ..models.scoring_models import (
    Score,
    ScoreBreakdown,
    ScoreComponent,
    Recommendation,
    Priority,
    Difficulty,
    ImpactLevel
)

logger = logging.getLogger(__name__)


class ScoringEngine:
    """
    Calculate comprehensive scores for scraper-friendliness and LLM accessibility.
    
    Scoring breakdown:
    - Static content quality: 25 points
    - Semantic HTML structure: 20 points
    - Structured data implementation: 20 points
    - Meta tag completeness: 15 points
    - JavaScript dependency: 10 points
    - Crawler accessibility: 10 points
    """
    
    def __init__(self):
        """Initialize scoring engine."""
        self.weights = {
            'static_content': 25.0,
            'semantic_html': 20.0,
            'structured_data': 20.0,
            'meta_tags': 15.0,
            'javascript': 10.0,
            'crawler': 10.0
        }
    
    def calculate_score(
        self,
        analysis_result: AnalysisResult,
        comparison: Optional[ContentComparison] = None
    ) -> Score:
        """
        Calculate complete scoring for an analysis result.
        
        Args:
            analysis_result: Complete analysis result
            comparison: Optional content comparison result
            
        Returns:
            Score with breakdown and recommendations
        """
        logger.info("Calculating scores...")
        
        # Debug: Log analysis result details for consistency checking
        logger.debug(f"Analysis result status: {analysis_result.status}")
        logger.debug(f"Content analysis word count: {analysis_result.content_analysis.word_count if analysis_result.content_analysis else 'None'}")
        logger.debug(f"Structure analysis semantic elements: {len(analysis_result.structure_analysis.semantic_elements) if analysis_result.structure_analysis else 'None'}")
        
        # Calculate component scores
        static_content = self._score_static_content(analysis_result)
        semantic_html = self._score_semantic_html(analysis_result)
        structured_data = self._score_structured_data(analysis_result)
        meta_tags = self._score_meta_tags(analysis_result)
        javascript = self._score_javascript(analysis_result, comparison)
        crawler = self._score_crawler(analysis_result)
        
        # Debug: Log score components for consistency checking
        logger.debug(f"Static content score: {static_content.score:.2f}")
        logger.debug(f"Semantic HTML score: {semantic_html.score:.2f}")
        logger.debug(f"Structured data score: {structured_data.score:.2f}")
        logger.debug(f"Meta tags score: {meta_tags.score:.2f}")
        logger.debug(f"JavaScript score: {javascript.score:.2f}")
        logger.debug(f"Crawler score: {crawler.score:.2f}")
        
        # Calculate total scraper-friendliness score
        scraper_total = (
            static_content.score +
            semantic_html.score +
            structured_data.score +
            meta_tags.score +
            javascript.score +
            crawler.score
        )
        
        logger.debug(f"Scraper total: {scraper_total:.2f}")
        
        scraper_breakdown = ScoreBreakdown(
            total_score=scraper_total,
            grade=Score.calculate_grade(scraper_total),
            static_content_quality=static_content,
            semantic_html_structure=semantic_html,
            structured_data_implementation=structured_data,
            meta_tag_completeness=meta_tags,
            javascript_dependency=javascript,
            crawler_accessibility=crawler
        )
        
        # Calculate LLM accessibility (emphasizes different aspects)
        llm_breakdown = self._calculate_llm_score(
            analysis_result,
            comparison,
            static_content,
            semantic_html,
            structured_data,
            meta_tags
        )
        
        logger.debug(f"LLM total: {llm_breakdown.total_score:.2f}")
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            analysis_result,
            comparison,
            scraper_breakdown,
            llm_breakdown
        )
        
        logger.info(
            f"Scoring complete: Scraper={scraper_total:.1f}/100 ({scraper_breakdown.grade}), "
            f"LLM={llm_breakdown.total_score:.1f}/100 ({llm_breakdown.grade})"
        )
        
        return Score(
            scraper_friendliness=scraper_breakdown,
            llm_accessibility=llm_breakdown,
            recommendations=recommendations
        )
    
    def _score_static_content(self, result: AnalysisResult) -> ScoreComponent:
        """Score static content quality (25 points)."""
        score = 0.0
        max_score = self.weights['static_content']
        issues = []
        strengths = []
        
        if not result.content_analysis:
            return ScoreComponent(
                name="Static Content Quality",
                score=0.0,
                max_score=max_score,
                percentage=0.0,
                description="No content analysis available",
                issues=["Content analysis missing"]
            )
        
        content = result.content_analysis
        
        # Word count (10 points)
        if content.word_count >= 500:
            score += 10.0
            strengths.append(f"Substantial content ({content.word_count} words)")
        elif content.word_count >= 200:
            score += 7.0
            strengths.append(f"Moderate content ({content.word_count} words)")
        elif content.word_count >= 50:
            score += 4.0
            issues.append(f"Limited content ({content.word_count} words)")
        else:
            issues.append(f"Very little content ({content.word_count} words)")
        
        # Paragraph structure (5 points)
        if content.paragraphs >= 5:
            score += 5.0
            strengths.append(f"Well-structured with {content.paragraphs} paragraphs")
        elif content.paragraphs >= 2:
            score += 3.0
        elif content.paragraphs >= 1:
            score += 1.0
        else:
            issues.append("No paragraphs detected")
        
        # Links (5 points)
        if content.links >= 10:
            score += 5.0
            strengths.append(f"Good navigation with {content.links} links")
        elif content.links >= 5:
            score += 3.0
        elif content.links >= 1:
            score += 1.0
        else:
            issues.append("No links found")
        
        # Media (3 points)
        if content.images >= 3:
            score += 2.0
        elif content.images >= 1:
            score += 1.0
        
        if content.tables >= 1 or content.lists >= 1:
            score += 1.0
        
        # Token efficiency (2 points)
        if content.estimated_tokens > 0:
            token_word_ratio = content.estimated_tokens / max(content.word_count, 1)
            if token_word_ratio <= 1.5:  # Efficient tokenization
                score += 2.0
                strengths.append("Efficient token usage")
            elif token_word_ratio <= 2.0:
                score += 1.0
        
        percentage = (score / max_score) * 100
        
        return ScoreComponent(
            name="Static Content Quality",
            score=score,
            max_score=max_score,
            percentage=percentage,
            description="Quality and quantity of static HTML content",
            issues=issues,
            strengths=strengths
        )
    
    def _score_semantic_html(self, result: AnalysisResult) -> ScoreComponent:
        """Score semantic HTML structure (20 points)."""
        score = 0.0
        max_score = self.weights['semantic_html']
        issues = []
        strengths = []
        
        if not result.structure_analysis:
            return ScoreComponent(
                name="Semantic HTML Structure",
                score=0.0,
                max_score=max_score,
                percentage=0.0,
                description="No structure analysis available",
                issues=["Structure analysis missing"]
            )
        
        structure = result.structure_analysis
        
        # Semantic elements (8 points)
        if structure.has_semantic_html:
            semantic_count = len(structure.semantic_elements)
            if semantic_count >= 5:
                score += 8.0
                strengths.append(f"Excellent use of {semantic_count} semantic elements")
            elif semantic_count >= 3:
                score += 6.0
                strengths.append(f"Good use of {semantic_count} semantic elements")
            elif semantic_count >= 1:
                score += 3.0
                strengths.append(f"Some semantic elements ({semantic_count})")
            else:
                score += 1.0
        else:
            issues.append("No semantic HTML elements detected")
        
        # Heading hierarchy (7 points)
        h1_count = len(structure.heading_hierarchy.h1)
        if h1_count == 1:
            score += 3.0
            strengths.append("Single H1 heading (best practice)")
        elif h1_count > 1:
            score += 1.0
            issues.append(f"Multiple H1 headings ({h1_count})")
        else:
            issues.append("No H1 heading")
        
        h2_count = len(structure.heading_hierarchy.h2)
        if h2_count >= 2:
            score += 2.0
        elif h2_count == 1:
            score += 1.0
        
        h3_count = len(structure.heading_hierarchy.h3)
        if h3_count >= 1:
            score += 2.0
        
        # Proper structure (3 points)
        if structure.has_proper_structure:
            score += 3.0
            strengths.append("Well-structured HTML document")
        else:
            issues.append("HTML structure issues detected")
        
        # DOM depth (2 points)
        if structure.nested_depth <= 10:
            score += 2.0
        elif structure.nested_depth <= 15:
            score += 1.0
        else:
            issues.append(f"Deep DOM nesting ({structure.nested_depth} levels)")
        
        percentage = (score / max_score) * 100
        
        return ScoreComponent(
            name="Semantic HTML Structure",
            score=score,
            max_score=max_score,
            percentage=percentage,
            description="Use of semantic HTML5 elements and proper document structure",
            issues=issues,
            strengths=strengths
        )
    
    def _score_structured_data(self, result: AnalysisResult) -> ScoreComponent:
        """Score structured data implementation (20 points)."""
        score = 0.0
        max_score = self.weights['structured_data']
        issues = []
        strengths = []
        
        if not result.meta_analysis:
            return ScoreComponent(
                name="Structured Data Implementation",
                score=0.0,
                max_score=max_score,
                percentage=0.0,
                description="No meta analysis available",
                issues=["Meta analysis missing"]
            )
        
        meta = result.meta_analysis
        
        # JSON-LD (10 points)
        if meta.has_json_ld:
            json_ld_count = len([d for d in meta.structured_data if d.type == 'json-ld'])
            if json_ld_count >= 2:
                score += 10.0
                strengths.append(f"Excellent JSON-LD implementation ({json_ld_count} schemas)")
            elif json_ld_count == 1:
                score += 7.0
                strengths.append("JSON-LD structured data present")
            else:
                score += 5.0
                strengths.append("JSON-LD detected")
        else:
            issues.append("No JSON-LD structured data")
        
        # Microdata (5 points)
        if meta.has_microdata:
            score += 5.0
            strengths.append("Microdata markup present")
        else:
            issues.append("No Microdata markup")
        
        # RDFa (5 points)
        if meta.has_rdfa:
            score += 5.0
            strengths.append("RDFa markup present")
        else:
            issues.append("No RDFa markup")
        
        percentage = (score / max_score) * 100
        
        return ScoreComponent(
            name="Structured Data Implementation",
            score=score,
            max_score=max_score,
            percentage=percentage,
            description="Implementation of Schema.org structured data (JSON-LD, Microdata, RDFa)",
            issues=issues,
            strengths=strengths
        )
    
    def _score_meta_tags(self, result: AnalysisResult) -> ScoreComponent:
        """Score meta tag completeness (15 points)."""
        score = 0.0
        max_score = self.weights['meta_tags']
        issues = []
        strengths = []
        
        if not result.meta_analysis:
            return ScoreComponent(
                name="Meta Tag Completeness",
                score=0.0,
                max_score=max_score,
                percentage=0.0,
                description="No meta analysis available",
                issues=["Meta analysis missing"]
            )
        
        meta = result.meta_analysis
        
        # Title (4 points)
        if meta.title:
            if 30 <= len(meta.title) <= 60:
                score += 4.0
                strengths.append("Optimal title length")
            elif len(meta.title) > 0:
                score += 2.0
                if len(meta.title) < 30:
                    issues.append("Title too short")
                elif len(meta.title) > 60:
                    issues.append("Title too long")
        else:
            issues.append("No title tag")
        
        # Description (4 points)
        if meta.description:
            if 120 <= len(meta.description) <= 160:
                score += 4.0
                strengths.append("Optimal description length")
            elif len(meta.description) > 0:
                score += 2.0
                if len(meta.description) < 120:
                    issues.append("Description too short")
                elif len(meta.description) > 160:
                    issues.append("Description too long")
        else:
            issues.append("No meta description")
        
        # Open Graph (4 points)
        if meta.open_graph_tags:
            og_count = len(meta.open_graph_tags)
            if og_count >= 4:
                score += 4.0
                strengths.append(f"Complete Open Graph tags ({og_count})")
            elif og_count >= 2:
                score += 2.0
                strengths.append("Basic Open Graph tags")
            else:
                score += 1.0
        else:
            issues.append("No Open Graph tags")
        
        # Twitter Cards (2 points)
        if meta.twitter_card_tags:
            score += 2.0
            strengths.append("Twitter Card tags present")
        else:
            issues.append("No Twitter Card tags")
        
        # Canonical URL (1 point)
        if meta.canonical_url:
            score += 1.0
            strengths.append("Canonical URL specified")
        else:
            issues.append("No canonical URL")
        
        percentage = (score / max_score) * 100
        
        return ScoreComponent(
            name="Meta Tag Completeness",
            score=score,
            max_score=max_score,
            percentage=percentage,
            description="Completeness of meta tags, Open Graph, and Twitter Cards",
            issues=issues,
            strengths=strengths
        )
    
    def _score_javascript(
        self,
        result: AnalysisResult,
        comparison: Optional[ContentComparison]
    ) -> ScoreComponent:
        """Score JavaScript dependency (10 points - higher is better)."""
        score = 0.0
        max_score = self.weights['javascript']
        issues = []
        strengths = []
        
        if not result.javascript_analysis:
            return ScoreComponent(
                name="JavaScript Dependency",
                score=5.0,  # Neutral score if unknown
                max_score=max_score,
                percentage=50.0,
                description="No JavaScript analysis available",
                issues=["JavaScript analysis missing"]
            )
        
        js = result.javascript_analysis
        
        # Low JavaScript is better for scrapers
        if js.total_scripts == 0:
            score += 10.0
            strengths.append("No JavaScript - fully scraper accessible")
        elif js.total_scripts <= 2:
            score += 8.0
            strengths.append("Minimal JavaScript usage")
        elif js.total_scripts <= 5:
            score += 6.0
            strengths.append("Moderate JavaScript usage")
        elif js.total_scripts <= 10:
            score += 4.0
            issues.append(f"{js.total_scripts} scripts detected")
        else:
            score += 2.0
            issues.append(f"Heavy JavaScript usage ({js.total_scripts} scripts)")
        
        # SPA detection
        if js.is_spa:
            score = max(0, score - 3.0)
            issues.append("Single Page Application detected - may limit scraper access")
        
        # Framework detection
        if js.frameworks:
            framework_names = ', '.join([f.name for f in js.frameworks[:3]])
            issues.append(f"Frameworks detected: {framework_names}")
        
        # Content comparison
        if comparison and comparison.javascript_dependent:
            dependency_penalty = min(3.0, (1.0 - comparison.similarity_score) * 5)
            score = max(0, score - dependency_penalty)
            issues.append(f"Content is {(1-comparison.similarity_score)*100:.0f}% JavaScript-dependent")
        
        percentage = (score / max_score) * 100
        
        return ScoreComponent(
            name="JavaScript Dependency",
            score=score,
            max_score=max_score,
            percentage=percentage,
            description="Content accessibility without JavaScript execution",
            issues=issues,
            strengths=strengths
        )
    
    def _score_crawler(self, result: AnalysisResult) -> ScoreComponent:
        """Score crawler accessibility (10 points)."""
        score = 5.0  # Default neutral score
        max_score = self.weights['crawler']
        issues = []
        strengths = []
        
        # For now, give a neutral score since crawler analysis is optional
        # This will be enhanced when crawler analysis is implemented
        
        if result.crawler_analysis:
            crawler = result.crawler_analysis
            
            if crawler.is_crawlable:
                score += 3.0
                strengths.append("Site is crawlable")
            else:
                issues.append("Site blocks crawlers")
            
            if crawler.has_robots_txt:
                score += 1.0
                strengths.append("robots.txt present")
            
            if crawler.has_sitemap:
                score += 1.0
                strengths.append("Sitemap available")
        else:
            strengths.append("Crawler directives assumed permissive")
        
        percentage = (score / max_score) * 100
        
        return ScoreComponent(
            name="Crawler Accessibility",
            score=score,
            max_score=max_score,
            percentage=percentage,
            description="Crawler-friendliness based on robots.txt and other directives",
            issues=issues,
            strengths=strengths
        )
    
    def _calculate_llm_score(
        self,
        result: AnalysisResult,
        comparison: Optional[ContentComparison],
        static_content: ScoreComponent,
        semantic_html: ScoreComponent,
        structured_data: ScoreComponent,
        meta_tags: ScoreComponent
    ) -> ScoreBreakdown:
        """Calculate LLM accessibility score (emphasizes different aspects)."""
        
        # LLM score weights differ - emphasize content structure and semantics
        llm_static = ScoreComponent(
            name=static_content.name,
            score=(static_content.score / static_content.max_score) * 30,  # 30 points
            max_score=30.0,
            percentage=(static_content.score / static_content.max_score) * 100,
            description=static_content.description,
            issues=static_content.issues,
            strengths=static_content.strengths
        )
        
        llm_semantic = ScoreComponent(
            name=semantic_html.name,
            score=(semantic_html.score / semantic_html.max_score) * 25,  # 25 points
            max_score=25.0,
            percentage=(semantic_html.score / semantic_html.max_score) * 100,
            description=semantic_html.description,
            issues=semantic_html.issues,
            strengths=semantic_html.strengths
        )
        
        llm_structured = ScoreComponent(
            name=structured_data.name,
            score=(structured_data.score / structured_data.max_score) * 20,  # 20 points
            max_score=20.0,
            percentage=(structured_data.score / structured_data.max_score) * 100,
            description=structured_data.description,
            issues=structured_data.issues,
            strengths=structured_data.strengths
        )
        
        llm_meta = ScoreComponent(
            name=meta_tags.name,
            score=(meta_tags.score / meta_tags.max_score) * 15,  # 15 points
            max_score=15.0,
            percentage=(meta_tags.score / meta_tags.max_score) * 100,
            description=meta_tags.description,
            issues=meta_tags.issues,
            strengths=meta_tags.strengths
        )
        
        # JavaScript is less critical for LLMs (can use dynamic analysis)
        llm_js = ScoreComponent(
            name="JavaScript Dependency",
            score=5.0,  # Neutral for LLMs
            max_score=5.0,
            percentage=100.0,
            description="Less critical for LLM access (dynamic rendering available)",
            issues=[],
            strengths=["LLMs can handle JavaScript content"]
        )
        
        llm_crawler = ScoreComponent(
            name="Crawler Accessibility",
            score=5.0,
            max_score=5.0,
            percentage=100.0,
            description="Standard crawler rules",
            issues=[],
            strengths=[]
        )
        
        llm_total = (
            llm_static.score +
            llm_semantic.score +
            llm_structured.score +
            llm_meta.score +
            llm_js.score +
            llm_crawler.score
        )
        
        return ScoreBreakdown(
            total_score=llm_total,
            grade=Score.calculate_grade(llm_total),
            static_content_quality=llm_static,
            semantic_html_structure=llm_semantic,
            structured_data_implementation=llm_structured,
            meta_tag_completeness=llm_meta,
            javascript_dependency=llm_js,
            crawler_accessibility=llm_crawler
        )
    
    def _generate_recommendations(
        self,
        result: AnalysisResult,
        comparison: Optional[ContentComparison],
        scraper_score: ScoreBreakdown,
        llm_score: ScoreBreakdown
    ) -> List[Recommendation]:
        """Generate prioritized recommendations."""
        recommendations = []
        
        # Analyze each component and generate recommendations
        self._add_content_recommendations(recommendations, result, scraper_score.static_content_quality)
        self._add_semantic_recommendations(recommendations, result, scraper_score.semantic_html_structure)
        self._add_structured_data_recommendations(recommendations, result, scraper_score.structured_data_implementation)
        self._add_meta_recommendations(recommendations, result, scraper_score.meta_tag_completeness)
        self._add_javascript_recommendations(recommendations, result, comparison, scraper_score.javascript_dependency)
        
        # Sort by priority
        priority_order = {Priority.CRITICAL: 0, Priority.HIGH: 1, Priority.MEDIUM: 2, Priority.LOW: 3}
        recommendations.sort(key=lambda r: priority_order[r.priority])
        
        return recommendations
    
    def _add_content_recommendations(
        self,
        recommendations: List[Recommendation],
        result: AnalysisResult,
        score: ScoreComponent
    ):
        """Add content-related recommendations."""
        if not result.content_analysis:
            return
        
        content = result.content_analysis
        
        if content.word_count < 200:
            recommendations.append(Recommendation(
                title="Increase Content Volume",
                description=f"Your page has only {content.word_count} words. Add more descriptive content (aim for 300-500 words minimum).",
                priority=Priority.HIGH,
                difficulty=Difficulty.EASY,
                impact=ImpactLevel.HIGH,
                category="content",
                code_example="Add more paragraphs with relevant, descriptive content:\n<p>Detailed description of your product/service...</p>",
                resources=["https://developers.google.com/search/docs/fundamentals/creating-helpful-content"]
            ))
        
        if content.paragraphs < 2:
            recommendations.append(Recommendation(
                title="Improve Content Structure",
                description="Add more paragraph tags to structure your content properly.",
                priority=Priority.MEDIUM,
                difficulty=Difficulty.EASY,
                impact=ImpactLevel.MEDIUM,
                category="content"
            ))
    
    def _add_semantic_recommendations(
        self,
        recommendations: List[Recommendation],
        result: AnalysisResult,
        score: ScoreComponent
    ):
        """Add semantic HTML recommendations."""
        if not result.structure_analysis:
            return
        
        structure = result.structure_analysis
        
        if not structure.has_semantic_html:
            recommendations.append(Recommendation(
                title="Use Semantic HTML5 Elements",
                description="Replace generic <div> tags with semantic elements like <header>, <main>, <article>, <section>, <nav>, <footer>.",
                priority=Priority.HIGH,
                difficulty=Difficulty.MEDIUM,
                impact=ImpactLevel.HIGH,
                category="html",
                code_example="<header>\n  <nav>...</nav>\n</header>\n<main>\n  <article>...</article>\n</main>\n<footer>...</footer>",
                resources=["https://developer.mozilla.org/en-US/docs/Web/HTML/Element"]
            ))
        
        h1_count = len(structure.heading_hierarchy.h1)
        if h1_count == 0:
            recommendations.append(Recommendation(
                title="Add H1 Heading",
                description="Every page should have exactly one H1 heading that describes the main topic.",
                priority=Priority.CRITICAL,
                difficulty=Difficulty.EASY,
                impact=ImpactLevel.HIGH,
                category="html",
                code_example="<h1>Main Page Title</h1>"
            ))
        elif h1_count > 1:
            recommendations.append(Recommendation(
                title="Use Only One H1 Heading",
                description=f"You have {h1_count} H1 headings. Use only one H1 per page, and use H2-H6 for subheadings.",
                priority=Priority.MEDIUM,
                difficulty=Difficulty.EASY,
                impact=ImpactLevel.MEDIUM,
                category="html"
            ))
    
    def _add_structured_data_recommendations(
        self,
        recommendations: List[Recommendation],
        result: AnalysisResult,
        score: ScoreComponent
    ):
        """Add structured data recommendations."""
        if not result.meta_analysis:
            return
        
        meta = result.meta_analysis
        
        if not meta.has_json_ld:
            recommendations.append(Recommendation(
                title="Add JSON-LD Structured Data",
                description="Implement Schema.org structured data using JSON-LD format to help search engines and LLMs understand your content.",
                priority=Priority.HIGH,
                difficulty=Difficulty.MEDIUM,
                impact=ImpactLevel.HIGH,
                category="structured_data",
                code_example='<script type="application/ld+json">\n{\n  "@context": "https://schema.org",\n  "@type": "Organization",\n  "name": "Your Company",\n  "url": "https://example.com"\n}\n</script>',
                resources=[
                    "https://schema.org/docs/gs.html",
                    "https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data"
                ]
            ))
    
    def _add_meta_recommendations(
        self,
        recommendations: List[Recommendation],
        result: AnalysisResult,
        score: ScoreComponent
    ):
        """Add meta tag recommendations."""
        if not result.meta_analysis:
            return
        
        meta = result.meta_analysis
        
        if not meta.title or len(meta.title) < 30:
            recommendations.append(Recommendation(
                title="Optimize Page Title",
                description="Add or improve your page title (30-60 characters recommended).",
                priority=Priority.CRITICAL,
                difficulty=Difficulty.EASY,
                impact=ImpactLevel.HIGH,
                category="meta",
                code_example='<title>Descriptive Page Title - Brand Name</title>'
            ))
        
        if not meta.description or len(meta.description) < 120:
            recommendations.append(Recommendation(
                title="Add Meta Description",
                description="Add a compelling meta description (120-160 characters).",
                priority=Priority.HIGH,
                difficulty=Difficulty.EASY,
                impact=ImpactLevel.HIGH,
                category="meta",
                code_example='<meta name="description" content="Clear, compelling description of your page content...">'
            ))
        
        if not meta.open_graph_tags or len(meta.open_graph_tags) < 4:
            recommendations.append(Recommendation(
                title="Implement Open Graph Tags",
                description="Add Open Graph tags for better social media sharing.",
                priority=Priority.MEDIUM,
                difficulty=Difficulty.EASY,
                impact=ImpactLevel.MEDIUM,
                category="meta",
                code_example='<meta property="og:title" content="Page Title">\n<meta property="og:description" content="Description">\n<meta property="og:image" content="https://example.com/image.jpg">\n<meta property="og:url" content="https://example.com/page">'
            ))
    
    def _add_javascript_recommendations(
        self,
        recommendations: List[Recommendation],
        result: AnalysisResult,
        comparison: Optional[ContentComparison],
        score: ScoreComponent
    ):
        """Add JavaScript-related recommendations."""
        if not result.javascript_analysis:
            return
        
        js = result.javascript_analysis
        
        if js.is_spa:
            recommendations.append(Recommendation(
                title="Consider Server-Side Rendering",
                description="Your site appears to be a Single Page Application. Implement SSR or pre-rendering to improve crawler accessibility.",
                priority=Priority.HIGH,
                difficulty=Difficulty.HARD,
                impact=ImpactLevel.HIGH,
                category="javascript",
                resources=[
                    "https://nextjs.org/docs/pages/building-your-application/rendering/server-side-rendering",
                    "https://vuejs.org/guide/scaling-up/ssr.html"
                ]
            ))
        
        if comparison and comparison.javascript_dependent:
            recommendations.append(Recommendation(
                title="Reduce JavaScript Dependency for Content",
                description=f"{len(comparison.missing_in_static)} content sections are only available with JavaScript. Move critical content to static HTML.",
                priority=Priority.HIGH,
                difficulty=Difficulty.MEDIUM,
                impact=ImpactLevel.HIGH,
                category="javascript"
            ))

