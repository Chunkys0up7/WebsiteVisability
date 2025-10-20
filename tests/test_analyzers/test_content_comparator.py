"""
Unit tests for ContentComparator
"""

import pytest
from src.analyzers.content_comparator import ContentComparator
from src.models.analysis_result import (
    AnalysisResult,
    ContentAnalysis,
    StructureAnalysis,
    HeadingHierarchy,
    ContentComparison
)
from datetime import datetime


class TestContentComparator:
    """Test suite for ContentComparator class"""
    
    @pytest.fixture
    def comparator(self):
        """Create a content comparator instance"""
        return ContentComparator()
    
    @pytest.fixture
    def identical_results(self):
        """Create identical static and dynamic results"""
        content = ContentAnalysis(
            text_content="This is a test page with some content.",
            word_count=8,
            character_count=40,
            estimated_tokens=10,
            paragraphs=1,
            links=0,
            images=0,
            tables=0,
            lists=0
        )
        
        hierarchy = HeadingHierarchy(h1=["Main"], h2=[], h3=[], h4=[], h5=[], h6=[])
        structure = StructureAnalysis(
            has_semantic_html=True,
            semantic_elements=["header", "main"],
            heading_hierarchy=hierarchy,
            total_elements=10,
            nested_depth=3,
            has_proper_structure=True
        )
        
        result = AnalysisResult(
            url="https://example.com",
            analyzed_at=datetime.now(),
            status="success",
            content_analysis=content,
            structure_analysis=structure
        )
        
        return result, result
    
    @pytest.fixture
    def different_results(self):
        """Create different static and dynamic results"""
        static_content = ContentAnalysis(
            text_content="This is static content.",
            word_count=4,
            character_count=23,
            estimated_tokens=6,
            paragraphs=1,
            links=0,
            images=0,
            tables=0,
            lists=0
        )
        
        dynamic_content = ContentAnalysis(
            text_content="This is static content. This is additional dynamic content loaded by JavaScript.",
            word_count=13,
            character_count=81,
            estimated_tokens=20,
            paragraphs=2,
            links=2,
            images=1,
            tables=1,
            lists=1
        )
        
        static_hierarchy = HeadingHierarchy(h1=["Main"], h2=[], h3=[], h4=[], h5=[], h6=[])
        dynamic_hierarchy = HeadingHierarchy(h1=["Main"], h2=["Section 1", "Section 2"], h3=[], h4=[], h5=[], h6=[])
        
        static_structure = StructureAnalysis(
            has_semantic_html=True,
            semantic_elements=["header"],
            heading_hierarchy=static_hierarchy,
            total_elements=5,
            nested_depth=2,
            has_proper_structure=True
        )
        
        dynamic_structure = StructureAnalysis(
            has_semantic_html=True,
            semantic_elements=["header", "main", "article"],
            heading_hierarchy=dynamic_hierarchy,
            total_elements=15,
            nested_depth=4,
            has_proper_structure=True
        )
        
        static_result = AnalysisResult(
            url="https://example.com",
            analyzed_at=datetime.now(),
            status="success",
            content_analysis=static_content,
            structure_analysis=static_structure
        )
        
        dynamic_result = AnalysisResult(
            url="https://example.com",
            analyzed_at=datetime.now(),
            status="success",
            content_analysis=dynamic_content,
            structure_analysis=dynamic_structure
        )
        
        return static_result, dynamic_result
    
    def test_comparator_initialization(self):
        """Test comparator initializes correctly"""
        comparator = ContentComparator()
        assert comparator.similarity_threshold == 0.95
    
    def test_custom_similarity_threshold(self):
        """Test custom similarity threshold"""
        comparator = ContentComparator(similarity_threshold=0.8)
        assert comparator.similarity_threshold == 0.8
    
    def test_compare_identical_content(self, comparator, identical_results):
        """Test comparison of identical content"""
        static, dynamic = identical_results
        comparison = comparator.compare(static, dynamic)
        
        assert isinstance(comparison, ContentComparison)
        assert comparison.similarity_score > 0.95
        assert comparison.content_difference == 0
        assert comparison.javascript_dependent is False
    
    def test_compare_different_content(self, comparator, different_results):
        """Test comparison of different content"""
        static, dynamic = different_results
        comparison = comparator.compare(static, dynamic)
        
        assert isinstance(comparison, ContentComparison)
        assert comparison.similarity_score < 0.95
        assert comparison.content_difference > 0
        assert comparison.javascript_dependent is True
        assert comparison.dynamic_content_length > comparison.static_content_length
    
    def test_missing_content_detection(self, comparator, different_results):
        """Test detection of missing content in static"""
        static, dynamic = different_results
        comparison = comparator.compare(static, dynamic)
        
        assert len(comparison.missing_in_static) > 0
    
    def test_structural_additions(self, comparator, different_results):
        """Test detection of structural additions"""
        static, dynamic = different_results
        comparison = comparator.compare(static, dynamic)
        
        assert len(comparison.added_elements) > 0
        # Should detect additional H2 headings, paragraphs, links, etc.
        added_text = ' '.join(comparison.added_elements)
        assert 'heading' in added_text or 'paragraph' in added_text or 'link' in added_text
    
    def test_empty_static_content(self, comparator, different_results):
        """Test comparison with empty static content"""
        static, dynamic = different_results
        static.content_analysis.text_content = ""
        
        comparison = comparator.compare(static, dynamic)
        
        assert comparison.static_content_length == 0
        assert comparison.dynamic_content_length > 0
        assert comparison.javascript_dependent is True
    
    def test_empty_dynamic_content(self, comparator, different_results):
        """Test comparison with empty dynamic content"""
        static, dynamic = different_results
        dynamic.content_analysis.text_content = ""
        
        comparison = comparator.compare(static, dynamic)
        
        assert comparison.dynamic_content_length == 0
        assert comparison.similarity_score >= 0.0
    
    def test_calculate_dependency_score_none(self, comparator, identical_results):
        """Test dependency score for identical content"""
        static, dynamic = identical_results
        comparison = comparator.compare(static, dynamic)
        
        score = comparator.calculate_javascript_dependency_score(comparison)
        assert score < 0.1  # Minimal dependency
    
    def test_calculate_dependency_score_high(self, comparator, different_results):
        """Test dependency score for different content"""
        static, dynamic = different_results
        comparison = comparator.compare(static, dynamic)
        
        score = comparator.calculate_javascript_dependency_score(comparison)
        assert score > 0.0  # Some dependency
    
    def test_calculate_dependency_score_full(self, comparator):
        """Test dependency score when all content is dynamic"""
        static_content = ContentAnalysis(
            text_content="",
            word_count=0,
            character_count=0,
            estimated_tokens=0,
            paragraphs=0,
            links=0,
            images=0,
            tables=0,
            lists=0
        )
        
        dynamic_content = ContentAnalysis(
            text_content="All dynamic content loaded by JavaScript.",
            word_count=6,
            character_count=42,
            estimated_tokens=10,
            paragraphs=1,
            links=0,
            images=0,
            tables=0,
            lists=0
        )
        
        static_result = AnalysisResult(
            url="https://example.com",
            analyzed_at=datetime.now(),
            status="success",
            content_analysis=static_content
        )
        
        dynamic_result = AnalysisResult(
            url="https://example.com",
            analyzed_at=datetime.now(),
            status="success",
            content_analysis=dynamic_content
        )
        
        comparison = comparator.compare(static_result, dynamic_result)
        score = comparator.calculate_javascript_dependency_score(comparison)
        
        assert score == 1.0  # Full dependency
    
    def test_generate_summary(self, comparator, different_results):
        """Test generation of comparison summary"""
        static, dynamic = different_results
        comparison = comparator.compare(static, dynamic)
        
        summary = comparator.generate_comparison_summary(comparison)
        
        assert "similarity_percentage" in summary
        assert "content_difference_chars" in summary
        assert "javascript_dependent" in summary
        assert "dependency_level" in summary
        assert "dependency_score" in summary
        assert "verdict" in summary
    
    def test_summary_dependency_levels(self, comparator):
        """Test all dependency level classifications"""
        # Test each level by creating different comparisons
        levels = []
        
        # Minimal dependency
        comp = ContentComparison(
            static_content_length=100,
            dynamic_content_length=100,
            content_difference=0,
            similarity_score=1.0,
            javascript_dependent=False,
            missing_in_static=[],
            added_elements=[]
        )
        summary = comparator.generate_comparison_summary(comp)
        assert summary["dependency_level"] == "Minimal"
        
        # Low dependency
        comp = ContentComparison(
            static_content_length=100,
            dynamic_content_length=110,
            content_difference=10,
            similarity_score=0.85,
            javascript_dependent=False,
            missing_in_static=[],
            added_elements=[]
        )
        summary = comparator.generate_comparison_summary(comp)
        assert summary["dependency_level"] in ["Minimal", "Low"]
        
        # High dependency
        comp = ContentComparison(
            static_content_length=50,
            dynamic_content_length=200,
            content_difference=150,
            similarity_score=0.3,
            javascript_dependent=True,
            missing_in_static=["content"],
            added_elements=["element"]
        )
        summary = comparator.generate_comparison_summary(comp)
        assert summary["dependency_level"] in ["High", "Critical"]
    
    def test_verdict_generation(self, comparator):
        """Test verdict generation for different scenarios"""
        # Excellent verdict
        comp = ContentComparison(
            static_content_length=100,
            dynamic_content_length=100,
            content_difference=0,
            similarity_score=1.0,
            javascript_dependent=False,
            missing_in_static=[],
            added_elements=[]
        )
        summary = comparator.generate_comparison_summary(comp)
        assert "Excellent" in summary["verdict"] or "minimal" in summary["verdict"].lower()
    
    def test_missing_content_filtering(self, comparator):
        """Test that very short sentences are filtered out"""
        static_content = ContentAnalysis(
            text_content="Hello.",
            word_count=1,
            character_count=6,
            estimated_tokens=2,
            paragraphs=1,
            links=0,
            images=0,
            tables=0,
            lists=0
        )
        
        dynamic_content = ContentAnalysis(
            text_content="Hello. Hi. This is a longer sentence that should be detected as missing content.",
            word_count=14,
            character_count=80,
            estimated_tokens=20,
            paragraphs=1,
            links=0,
            images=0,
            tables=0,
            lists=0
        )
        
        static_result = AnalysisResult(
            url="https://example.com",
            analyzed_at=datetime.now(),
            status="success",
            content_analysis=static_content
        )
        
        dynamic_result = AnalysisResult(
            url="https://example.com",
            analyzed_at=datetime.now(),
            status="success",
            content_analysis=dynamic_content
        )
        
        comparison = comparator.compare(static_result, dynamic_result)
        
        # Should only include the longer sentence
        for missing in comparison.missing_in_static:
            assert len(missing) > 20
    
    def test_compare_without_structure(self, comparator):
        """Test comparison when structure analysis is missing"""
        content = ContentAnalysis(
            text_content="Test content",
            word_count=2,
            character_count=12,
            estimated_tokens=3,
            paragraphs=1,
            links=0,
            images=0,
            tables=0,
            lists=0
        )
        
        result = AnalysisResult(
            url="https://example.com",
            analyzed_at=datetime.now(),
            status="success",
            content_analysis=content,
            structure_analysis=None
        )
        
        comparison = comparator.compare(result, result)
        
        assert isinstance(comparison, ContentComparison)
        assert len(comparison.added_elements) == 0
    
    def test_compare_without_content_analysis(self, comparator):
        """Test comparison when content analysis is missing"""
        result = AnalysisResult(
            url="https://example.com",
            analyzed_at=datetime.now(),
            status="success",
            content_analysis=None,
            structure_analysis=None
        )
        
        comparison = comparator.compare(result, result)
        
        assert isinstance(comparison, ContentComparison)
        assert comparison.static_content_length == 0
        assert comparison.dynamic_content_length == 0
    
    def test_heading_level_comparison(self, comparator):
        """Test comparison of all heading levels"""
        static_hierarchy = HeadingHierarchy(
            h1=["Main"],
            h2=["Section"],
            h3=[],
            h4=[],
            h5=[],
            h6=[]
        )
        
        dynamic_hierarchy = HeadingHierarchy(
            h1=["Main"],
            h2=["Section", "Another Section"],
            h3=["Subsection 1", "Subsection 2"],
            h4=["Detail"],
            h5=[],
            h6=[]
        )
        
        static_structure = StructureAnalysis(
            has_semantic_html=True,
            semantic_elements=["header"],
            heading_hierarchy=static_hierarchy,
            total_elements=5,
            nested_depth=2,
            has_proper_structure=True
        )
        
        dynamic_structure = StructureAnalysis(
            has_semantic_html=True,
            semantic_elements=["header", "main"],
            heading_hierarchy=dynamic_hierarchy,
            total_elements=10,
            nested_depth=3,
            has_proper_structure=True
        )
        
        static_result = AnalysisResult(
            url="https://example.com",
            analyzed_at=datetime.now(),
            status="success",
            structure_analysis=static_structure
        )
        
        dynamic_result = AnalysisResult(
            url="https://example.com",
            analyzed_at=datetime.now(),
            status="success",
            structure_analysis=dynamic_structure
        )
        
        comparison = comparator.compare(static_result, dynamic_result)
        
        # Should detect additions at H2, H3, and H4 levels
        added_text = ' '.join(comparison.added_elements)
        assert 'H2' in added_text or 'H3' in added_text or 'H4' in added_text

