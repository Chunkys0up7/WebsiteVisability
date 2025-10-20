"""
Unit tests for ScoringEngine
"""

import pytest
from src.analyzers.scoring_engine import ScoringEngine
from src.models.analysis_result import (
    AnalysisResult,
    ContentAnalysis,
    StructureAnalysis,
    HeadingHierarchy,
    MetaAnalysis,
    JavaScriptAnalysis,
    ContentComparison
)
from src.models.scoring_models import Priority, Difficulty, ImpactLevel, Score
from src.models.analysis_result import StructuredData
from datetime import datetime


class TestScoringEngine:
    """Test suite for ScoringEngine class"""
    
    @pytest.fixture
    def engine(self):
        """Create scoring engine instance"""
        return ScoringEngine()
    
    @pytest.fixture
    def complete_result(self):
        """Create a complete, high-quality analysis result"""
        content = ContentAnalysis(
            text_content="This is excellent content with substantial information. " * 100,
            word_count=600,
            character_count=3600,
            estimated_tokens=750,
            paragraphs=10,
            links=15,
            images=5,
            tables=2,
            lists=3
        )
        
        hierarchy = HeadingHierarchy(
            h1=["Main Heading"],
            h2=["Section 1", "Section 2", "Section 3"],
            h3=["Subsection A", "Subsection B"],
            h4=[],
            h5=[],
            h6=[]
        )
        
        structure = StructureAnalysis(
            has_semantic_html=True,
            semantic_elements=["header", "main", "article", "section", "nav", "footer"],
            heading_hierarchy=hierarchy,
            total_elements=50,
            nested_depth=8,
            has_proper_structure=True
        )
        
        meta = MetaAnalysis(
            title="Perfect Page Title - Brand",
            description="This is an optimal meta description with the right length to provide good information for search engines.",
            keywords="test, seo, optimization",
            canonical_url="https://example.com/page",
            meta_tags=[],
            open_graph_tags={
                "og:title": "Page Title",
                "og:description": "Description",
                "og:image": "https://example.com/image.jpg",
                "og:url": "https://example.com/page"
            },
            twitter_card_tags={"twitter:card": "summary"},
            structured_data=[StructuredData(type="json-ld", data={"@type": "Organization", "name": "Test"})],
            has_json_ld=True,
            has_microdata=True,
            has_rdfa=False
        )
        
        js = JavaScriptAnalysis(
            total_scripts=2,
            inline_scripts=1,
            external_scripts=1,
            frameworks=[],
            is_spa=False,
            has_ajax=False,
            dynamic_content_detected=False
        )
        
        return AnalysisResult(
            url="https://example.com",
            analyzed_at=datetime.now(),
            status="success",
            content_analysis=content,
            structure_analysis=structure,
            meta_analysis=meta,
            javascript_analysis=js
        )
    
    @pytest.fixture
    def minimal_result(self):
        """Create a minimal, low-quality analysis result"""
        content = ContentAnalysis(
            text_content="Short content.",
            word_count=2,
            character_count=14,
            estimated_tokens=3,
            paragraphs=0,
            links=0,
            images=0,
            tables=0,
            lists=0
        )
        
        hierarchy = HeadingHierarchy(h1=[], h2=[], h3=[], h4=[], h5=[], h6=[])
        
        structure = StructureAnalysis(
            has_semantic_html=False,
            semantic_elements=[],
            heading_hierarchy=hierarchy,
            total_elements=5,
            nested_depth=2,
            has_proper_structure=False
        )
        
        meta = MetaAnalysis(
            title=None,
            description=None,
            keywords=None,
            canonical_url=None,
            meta_tags=[],
            open_graph_tags={},
            twitter_card_tags={},
            structured_data=[],
            has_json_ld=False,
            has_microdata=False,
            has_rdfa=False
        )
        
        js = JavaScriptAnalysis(
            total_scripts=0,
            inline_scripts=0,
            external_scripts=0,
            frameworks=[],
            is_spa=False,
            has_ajax=False,
            dynamic_content_detected=False
        )
        
        return AnalysisResult(
            url="https://example.com",
            analyzed_at=datetime.now(),
            status="success",
            content_analysis=content,
            structure_analysis=structure,
            meta_analysis=meta,
            javascript_analysis=js
        )
    
    def test_engine_initialization(self, engine):
        """Test engine initializes with correct weights"""
        assert engine.weights['static_content'] == 25.0
        assert engine.weights['semantic_html'] == 20.0
        assert engine.weights['structured_data'] == 20.0
        assert engine.weights['meta_tags'] == 15.0
        assert engine.weights['javascript'] == 10.0
        assert engine.weights['crawler'] == 10.0
        assert sum(engine.weights.values()) == 100.0
    
    def test_calculate_score_complete(self, engine, complete_result):
        """Test scoring with complete, high-quality result"""
        score = engine.calculate_score(complete_result)
        
        assert score.scraper_friendliness.total_score > 70
        assert score.llm_accessibility.total_score > 70
        assert len(score.recommendations) >= 0
        assert score.scraper_friendliness.grade in ['A+', 'A', 'A-', 'B+', 'B', 'B-']
    
    def test_calculate_score_minimal(self, engine, minimal_result):
        """Test scoring with minimal, low-quality result"""
        score = engine.calculate_score(minimal_result)
        
        assert score.scraper_friendliness.total_score < 50
        assert len(score.recommendations) > 0
        assert score.scraper_friendliness.grade in ['D', 'F']
    
    def test_static_content_scoring(self, engine, complete_result):
        """Test static content component scoring"""
        component = engine._score_static_content(complete_result)
        
        assert component.name == "Static Content Quality"
        assert component.max_score == 25.0
        assert component.score > 15.0  # Good content should score well
        assert len(component.strengths) > 0
    
    def test_semantic_html_scoring(self, engine, complete_result):
        """Test semantic HTML component scoring"""
        component = engine._score_semantic_html(complete_result)
        
        assert component.name == "Semantic HTML Structure"
        assert component.max_score == 20.0
        assert component.score > 12.0  # Good semantics should score well
        assert len(component.strengths) > 0
    
    def test_structured_data_scoring(self, engine, complete_result):
        """Test structured data component scoring"""
        component = engine._score_structured_data(complete_result)
        
        assert component.name == "Structured Data Implementation"
        assert component.max_score == 20.0
        assert component.score > 10.0  # Has JSON-LD and Microdata
    
    def test_meta_tags_scoring(self, engine, complete_result):
        """Test meta tags component scoring"""
        component = engine._score_meta_tags(complete_result)
        
        assert component.name == "Meta Tag Completeness"
        assert component.max_score == 15.0
        assert component.score > 10.0  # Good meta tags
    
    def test_javascript_scoring_no_js(self, engine, complete_result):
        """Test JavaScript scoring with minimal JS"""
        component = engine._score_javascript(complete_result, None)
        
        assert component.name == "JavaScript Dependency"
        assert component.max_score == 10.0
        assert component.score >= 6.0  # Low JS is good for scrapers
    
    def test_crawler_scoring(self, engine, complete_result):
        """Test crawler accessibility scoring"""
        component = engine._score_crawler(complete_result)
        
        assert component.name == "Crawler Accessibility"
        assert component.max_score == 10.0
        assert component.score > 0
    
    def test_recommendations_generated(self, engine, minimal_result):
        """Test that recommendations are generated for poor results"""
        score = engine.calculate_score(minimal_result)
        
        assert len(score.recommendations) > 0
        
        # Check that recommendations have required fields
        for rec in score.recommendations:
            assert rec.title is not None
            assert rec.description is not None
            assert rec.priority in [Priority.CRITICAL, Priority.HIGH, Priority.MEDIUM, Priority.LOW]
            assert rec.difficulty in [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]
            assert rec.impact in [ImpactLevel.HIGH, ImpactLevel.MEDIUM, ImpactLevel.LOW]
            assert rec.category is not None
    
    def test_recommendations_prioritized(self, engine, minimal_result):
        """Test that recommendations are sorted by priority"""
        score = engine.calculate_score(minimal_result)
        
        priorities = [r.priority for r in score.recommendations]
        
        # Check that critical/high priorities come first
        if len(priorities) > 1:
            priority_values = {Priority.CRITICAL: 0, Priority.HIGH: 1, Priority.MEDIUM: 2, Priority.LOW: 3}
            for i in range(len(priorities) - 1):
                assert priority_values[priorities[i]] <= priority_values[priorities[i + 1]]
    
    def test_grade_calculation(self):
        """Test grade calculation for various scores"""
        assert Score.calculate_grade(98) == "A+"
        assert Score.calculate_grade(95) == "A"
        assert Score.calculate_grade(92) == "A-"
        assert Score.calculate_grade(88) == "B+"
        assert Score.calculate_grade(84) == "B"
        assert Score.calculate_grade(78) == "C+"
        assert Score.calculate_grade(74) == "C"
        assert Score.calculate_grade(68) == "D+"
        assert Score.calculate_grade(64) == "D"
        assert Score.calculate_grade(50) == "F"
    
    def test_score_with_comparison(self, engine, complete_result):
        """Test scoring with content comparison"""
        comparison = ContentComparison(
            static_content_length=1000,
            dynamic_content_length=1200,
            content_difference=200,
            similarity_score=0.85,
            javascript_dependent=True,
            missing_in_static=["Dynamic content"],
            added_elements=["2 paragraphs"]
        )
        
        score = engine.calculate_score(complete_result, comparison)
        
        assert score.scraper_friendliness.total_score > 0
        # JavaScript dependency should be penalized
        assert score.scraper_friendliness.javascript_dependency.score < 10.0
    
    def test_llm_score_different_from_scraper(self, engine, complete_result):
        """Test that LLM score weighs components differently"""
        score = engine.calculate_score(complete_result)
        
        # LLM score should exist
        assert score.llm_accessibility.total_score > 0
        assert score.llm_accessibility.grade is not None
        
        # Weights should be different (LLM emphasizes content/semantics more)
        assert score.llm_accessibility.static_content_quality.max_score == 30.0
        assert score.llm_accessibility.semantic_html_structure.max_score == 25.0
    
    def test_no_h1_generates_critical_recommendation(self, engine, minimal_result):
        """Test that missing H1 generates critical recommendation"""
        score = engine.calculate_score(minimal_result)
        
        h1_recommendations = [r for r in score.recommendations if "H1" in r.title]
        assert len(h1_recommendations) > 0
        assert any(r.priority == Priority.CRITICAL for r in h1_recommendations)
    
    def test_low_content_generates_recommendation(self, engine, minimal_result):
        """Test that low content generates recommendation"""
        score = engine.calculate_score(minimal_result)
        
        content_recommendations = [r for r in score.recommendations if "content" in r.title.lower()]
        assert len(content_recommendations) > 0
    
    def test_missing_structured_data_generates_recommendation(self, engine, minimal_result):
        """Test that missing structured data generates recommendation"""
        score = engine.calculate_score(minimal_result)
        
        structured_recommendations = [r for r in score.recommendations if "structured data" in r.title.lower() or "json-ld" in r.title.lower()]
        assert len(structured_recommendations) > 0
    
    def test_score_components_have_percentages(self, engine, complete_result):
        """Test that all score components calculate percentages"""
        score = engine.calculate_score(complete_result)
        
        components = [
            score.scraper_friendliness.static_content_quality,
            score.scraper_friendliness.semantic_html_structure,
            score.scraper_friendliness.structured_data_implementation,
            score.scraper_friendliness.meta_tag_completeness,
            score.scraper_friendliness.javascript_dependency,
            score.scraper_friendliness.crawler_accessibility
        ]
        
        for component in components:
            assert 0 <= component.percentage <= 100
            assert component.score <= component.max_score

