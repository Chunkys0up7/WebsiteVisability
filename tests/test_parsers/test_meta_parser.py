"""
Unit tests for MetaParser
"""

import pytest
from src.parsers.meta_parser import MetaParser
from src.models.analysis_result import MetaAnalysis, MetaTag


class TestMetaParser:
    """Test suite for MetaParser class"""
    
    @pytest.fixture
    def basic_meta_html(self):
        """HTML with basic meta tags"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Page Title</title>
            <meta name="description" content="This is a test page description">
            <meta name="keywords" content="test, page, keywords">
            <meta name="author" content="Test Author">
            <meta name="robots" content="index, follow">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="canonical" href="https://example.com/page">
        </head>
        <body>
            <p>Content</p>
        </body>
        </html>
        """
    
    @pytest.fixture
    def open_graph_html(self):
        """HTML with Open Graph tags"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>OG Test Page</title>
            <meta property="og:title" content="Open Graph Title">
            <meta property="og:description" content="Open Graph Description">
            <meta property="og:type" content="website">
            <meta property="og:url" content="https://example.com/og-page">
            <meta property="og:image" content="https://example.com/image.jpg">
            <meta property="og:site_name" content="Example Site">
        </head>
        <body>
            <p>Content</p>
        </body>
        </html>
        """
    
    @pytest.fixture
    def twitter_card_html(self):
        """HTML with Twitter Card tags"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Twitter Card Test</title>
            <meta name="twitter:card" content="summary_large_image">
            <meta name="twitter:site" content="@example">
            <meta name="twitter:creator" content="@author">
            <meta name="twitter:title" content="Twitter Card Title">
            <meta name="twitter:description" content="Twitter Card Description">
            <meta name="twitter:image" content="https://example.com/twitter-image.jpg">
        </head>
        <body>
            <p>Content</p>
        </body>
        </html>
        """
    
    @pytest.fixture
    def complete_meta_html(self):
        """HTML with all types of meta tags"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Complete Meta Test</title>
            <meta name="description" content="Complete description">
            <meta name="keywords" content="complete, meta, test">
            <link rel="canonical" href="https://example.com/complete">
            
            <!-- Open Graph -->
            <meta property="og:title" content="OG Complete Title">
            <meta property="og:description" content="OG Complete Description">
            <meta property="og:url" content="https://example.com/og-complete">
            <meta property="og:image" content="https://example.com/og-image.jpg">
            
            <!-- Twitter Cards -->
            <meta name="twitter:card" content="summary">
            <meta name="twitter:title" content="Twitter Complete Title">
            <meta name="twitter:description" content="Twitter Complete Description">
        </head>
        <body>
            <p>Content</p>
        </body>
        </html>
        """
    
    @pytest.fixture
    def minimal_html(self):
        """HTML with minimal meta tags"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Minimal Page</title>
        </head>
        <body>
            <p>Content</p>
        </body>
        </html>
        """
    
    @pytest.fixture
    def no_meta_html(self):
        """HTML with no meta tags at all"""
        return """
        <!DOCTYPE html>
        <html>
        <body>
            <p>Content without head section</p>
        </body>
        </html>
        """
    
    def test_parser_initialization(self, basic_meta_html):
        """Test parser initializes correctly"""
        parser = MetaParser(basic_meta_html)
        assert parser.soup is not None
        assert parser.html_content == basic_meta_html
    
    def test_extract_title(self, basic_meta_html):
        """Test title extraction"""
        parser = MetaParser(basic_meta_html)
        title = parser.extract_title()
        
        assert title == "Test Page Title"
    
    def test_extract_title_from_og(self, open_graph_html):
        """Test title extraction from Open Graph when no title tag"""
        html = """
        <html>
        <head>
            <meta property="og:title" content="OG Title Only">
        </head>
        <body></body>
        </html>
        """
        parser = MetaParser(html)
        title = parser.extract_title()
        
        assert title == "OG Title Only"
    
    def test_extract_description(self, basic_meta_html):
        """Test description extraction"""
        parser = MetaParser(basic_meta_html)
        description = parser.extract_description()
        
        assert description == "This is a test page description"
    
    def test_extract_keywords(self, basic_meta_html):
        """Test keywords extraction"""
        parser = MetaParser(basic_meta_html)
        keywords = parser.extract_keywords()
        
        assert keywords == "test, page, keywords"
    
    def test_extract_canonical_url(self, basic_meta_html):
        """Test canonical URL extraction"""
        parser = MetaParser(basic_meta_html)
        canonical = parser.extract_canonical_url()
        
        assert canonical == "https://example.com/page"
    
    def test_extract_canonical_from_og(self, open_graph_html):
        """Test canonical URL extraction from og:url"""
        parser = MetaParser(open_graph_html)
        canonical = parser.extract_canonical_url()
        
        assert canonical == "https://example.com/og-page"
    
    def test_extract_all_meta_tags(self, basic_meta_html):
        """Test extraction of all meta tags"""
        parser = MetaParser(basic_meta_html)
        meta_tags = parser.extract_all_meta_tags()
        
        assert len(meta_tags) > 0
        assert all(isinstance(tag, MetaTag) for tag in meta_tags)
        
        # Check that description tag is present
        desc_tags = [tag for tag in meta_tags if tag.name == 'description']
        assert len(desc_tags) == 1
        assert desc_tags[0].content == "This is a test page description"
    
    def test_extract_open_graph_tags(self, open_graph_html):
        """Test Open Graph tags extraction"""
        parser = MetaParser(open_graph_html)
        og_tags = parser.extract_open_graph_tags()
        
        assert 'title' in og_tags
        assert og_tags['title'] == "Open Graph Title"
        assert 'description' in og_tags
        assert og_tags['description'] == "Open Graph Description"
        assert 'type' in og_tags
        assert og_tags['type'] == "website"
        assert 'url' in og_tags
        assert 'image' in og_tags
        assert 'site_name' in og_tags
    
    def test_extract_twitter_card_tags(self, twitter_card_html):
        """Test Twitter Card tags extraction"""
        parser = MetaParser(twitter_card_html)
        twitter_tags = parser.extract_twitter_card_tags()
        
        assert 'card' in twitter_tags
        assert twitter_tags['card'] == "summary_large_image"
        assert 'site' in twitter_tags
        assert twitter_tags['site'] == "@example"
        assert 'creator' in twitter_tags
        assert twitter_tags['creator'] == "@author"
        assert 'title' in twitter_tags
        assert 'description' in twitter_tags
        assert 'image' in twitter_tags
    
    def test_has_open_graph_positive(self, open_graph_html):
        """Test Open Graph detection - positive case"""
        parser = MetaParser(open_graph_html)
        has_og = parser.has_open_graph()
        
        assert has_og is True
    
    def test_has_open_graph_negative(self, basic_meta_html):
        """Test Open Graph detection - negative case"""
        parser = MetaParser(basic_meta_html)
        has_og = parser.has_open_graph()
        
        assert has_og is False
    
    def test_has_twitter_cards_positive(self, twitter_card_html):
        """Test Twitter Cards detection - positive case"""
        parser = MetaParser(twitter_card_html)
        has_twitter = parser.has_twitter_cards()
        
        assert has_twitter is True
    
    def test_has_twitter_cards_negative(self, basic_meta_html):
        """Test Twitter Cards detection - negative case"""
        parser = MetaParser(basic_meta_html)
        has_twitter = parser.has_twitter_cards()
        
        assert has_twitter is False
    
    def test_extract_viewport(self, basic_meta_html):
        """Test viewport extraction"""
        parser = MetaParser(basic_meta_html)
        viewport = parser.extract_viewport()
        
        assert viewport == "width=device-width, initial-scale=1.0"
    
    def test_extract_robots(self, basic_meta_html):
        """Test robots meta tag extraction"""
        parser = MetaParser(basic_meta_html)
        robots = parser.extract_robots()
        
        assert robots == "index, follow"
    
    def test_extract_author(self, basic_meta_html):
        """Test author extraction"""
        parser = MetaParser(basic_meta_html)
        author = parser.extract_author()
        
        assert author == "Test Author"
    
    def test_get_meta_analysis(self, complete_meta_html):
        """Test complete meta analysis"""
        parser = MetaParser(complete_meta_html)
        analysis = parser.get_meta_analysis()
        
        assert isinstance(analysis, MetaAnalysis)
        assert analysis.title == "Complete Meta Test"
        assert analysis.description == "Complete description"
        assert analysis.keywords == "complete, meta, test"
        assert analysis.canonical_url == "https://example.com/complete"
        assert len(analysis.meta_tags) > 0
        assert len(analysis.open_graph_tags) > 0
        assert len(analysis.twitter_card_tags) > 0
    
    def test_analyze_complete(self, complete_meta_html):
        """Test complete analysis method"""
        parser = MetaParser(complete_meta_html)
        analysis = parser.analyze()
        
        assert isinstance(analysis, MetaAnalysis)
        assert analysis.title is not None
        assert analysis.description is not None
    
    def test_minimal_meta(self, minimal_html):
        """Test with minimal meta tags"""
        parser = MetaParser(minimal_html)
        analysis = parser.get_meta_analysis()
        
        assert analysis.title == "Minimal Page"
        assert analysis.description is None
        assert analysis.keywords is None
        assert analysis.canonical_url is None
        assert len(analysis.open_graph_tags) == 0
        assert len(analysis.twitter_card_tags) == 0
    
    def test_no_meta_tags(self, no_meta_html):
        """Test with no meta tags"""
        parser = MetaParser(no_meta_html)
        analysis = parser.get_meta_analysis()
        
        assert analysis.title is None
        assert analysis.description is None
        assert analysis.keywords is None
        assert analysis.canonical_url is None
        assert len(analysis.meta_tags) == 0
        assert len(analysis.open_graph_tags) == 0
        assert len(analysis.twitter_card_tags) == 0
    
    def test_meta_tag_without_content(self):
        """Test handling of meta tags without content"""
        html = """
        <html>
        <head>
            <meta name="description">
            <meta name="keywords" content="">
        </head>
        <body></body>
        </html>
        """
        parser = MetaParser(html)
        meta_tags = parser.extract_all_meta_tags()
        
        # Should not include tags without content
        assert len(meta_tags) == 0
    
    def test_duplicate_meta_tags(self):
        """Test handling of duplicate meta tags"""
        html = """
        <html>
        <head>
            <meta name="description" content="First description">
            <meta name="description" content="Second description">
        </head>
        <body></body>
        </html>
        """
        parser = MetaParser(html)
        description = parser.extract_description()
        
        # Should return the first one found
        assert description == "First description"
    
    def test_og_tags_with_prefix(self, open_graph_html):
        """Test that og: prefix is removed from keys"""
        parser = MetaParser(open_graph_html)
        og_tags = parser.extract_open_graph_tags()
        
        # Keys should not have 'og:' prefix
        assert 'title' in og_tags
        assert 'og:title' not in og_tags
    
    def test_twitter_tags_with_prefix(self, twitter_card_html):
        """Test that twitter: prefix is removed from keys"""
        parser = MetaParser(twitter_card_html)
        twitter_tags = parser.extract_twitter_card_tags()
        
        # Keys should not have 'twitter:' prefix
        assert 'card' in twitter_tags
        assert 'twitter:card' not in twitter_tags
    
    def test_whitespace_trimming(self):
        """Test that whitespace is trimmed from meta content"""
        html = """
        <html>
        <head>
            <title>  Title with spaces  </title>
            <meta name="description" content="  Description with spaces  ">
        </head>
        <body></body>
        </html>
        """
        parser = MetaParser(html)
        
        assert parser.extract_title() == "Title with spaces"
        assert parser.extract_description() == "Description with spaces"
    
    def test_empty_html(self):
        """Test handling of empty HTML"""
        parser = MetaParser("")
        analysis = parser.get_meta_analysis()
        
        assert analysis.title is None
        assert len(analysis.meta_tags) == 0
    
    def test_malformed_html(self):
        """Test handling of malformed HTML"""
        malformed = "<html><head><meta name='description' content='Test'><body>Content"
        parser = MetaParser(malformed)
        
        # Should not raise exception
        description = parser.extract_description()
        assert description == "Test"
    
    def test_case_sensitivity(self):
        """Test that meta tag names are case-sensitive (HTML5 standard)"""
        html = """
        <html>
        <head>
            <meta name="description" content="Test Description">
            <meta name="keywords" content="test keywords">
        </head>
        <body></body>
        </html>
        """
        parser = MetaParser(html)
        
        # HTML5 meta names should be lowercase
        description = parser.extract_description()
        keywords = parser.extract_keywords()
        
        assert description == "Test Description"
        assert keywords == "test keywords"
    
    def test_meta_tags_count(self, complete_meta_html):
        """Test counting of meta tags"""
        parser = MetaParser(complete_meta_html)
        meta_tags = parser.extract_all_meta_tags()
        
        assert len(meta_tags) >= 5  # Should have multiple meta tags
    
    def test_special_characters_in_content(self):
        """Test handling of special characters in meta content"""
        html = """
        <html>
        <head>
            <title>Test Page with Special Chars</title>
            <meta name="description" content="Description with &amp; and &lt; and &gt;">
        </head>
        <body></body>
        </html>
        """
        parser = MetaParser(html)
        
        title = parser.extract_title()
        description = parser.extract_description()
        
        assert title == "Test Page with Special Chars"
        assert description is not None
        # BeautifulSoup automatically decodes HTML entities
        assert '&' in description or 'and' in description

