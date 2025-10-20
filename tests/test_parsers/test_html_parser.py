"""
Unit tests for HTMLParser
"""

import pytest
from src.parsers.html_parser import HTMLParser
from src.models.analysis_result import ContentAnalysis, StructureAnalysis, HiddenContent


class TestHTMLParser:
    """Test suite for HTMLParser class"""
    
    @pytest.fixture
    def simple_html(self):
        """Simple HTML for basic testing"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <h1>Main Heading</h1>
            <p>This is a paragraph with some text.</p>
            <p>Another paragraph here.</p>
        </body>
        </html>
        """
    
    @pytest.fixture
    def semantic_html(self):
        """HTML with semantic elements"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Semantic Test</title>
        </head>
        <body>
            <header>
                <h1>Website Header</h1>
                <nav>
                    <a href="/">Home</a>
                    <a href="/about">About</a>
                </nav>
            </header>
            <main>
                <article>
                    <h2>Article Title</h2>
                    <p>Article content goes here.</p>
                </article>
                <aside>
                    <h3>Sidebar</h3>
                    <p>Sidebar content.</p>
                </aside>
            </main>
            <footer>
                <p>Footer content</p>
            </footer>
        </body>
        </html>
        """
    
    @pytest.fixture
    def hidden_content_html(self):
        """HTML with hidden elements"""
        return """
        <!DOCTYPE html>
        <html>
        <body>
            <p>Visible content</p>
            <p style="display:none">Hidden with display none</p>
            <p style="visibility:hidden">Hidden with visibility</p>
            <p hidden>Hidden with attribute</p>
            <div style="display: none;">Another hidden div</div>
        </body>
        </html>
        """
    
    @pytest.fixture
    def complex_structure_html(self):
        """HTML with complex structure"""
        return """
        <!DOCTYPE html>
        <html>
        <body>
            <h1>H1 Heading</h1>
            <h2>H2 Heading</h2>
            <h3>H3 Heading</h3>
            <p>Paragraph 1</p>
            <p>Paragraph 2</p>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
            <ol>
                <li>Ordered 1</li>
            </ol>
            <a href="https://example.com">Link 1</a>
            <a href="/page2">Link 2</a>
            <img src="image1.jpg" alt="Image 1">
            <img src="image2.jpg" alt="Image 2">
            <table>
                <tr><td>Cell</td></tr>
            </table>
        </body>
        </html>
        """
    
    def test_parser_initialization(self, simple_html):
        """Test parser initializes correctly"""
        parser = HTMLParser(simple_html)
        assert parser.soup is not None
        assert parser.html_content == simple_html
    
    def test_extract_text(self, simple_html):
        """Test text extraction"""
        parser = HTMLParser(simple_html)
        text = parser.extract_text()
        
        assert "Main Heading" in text
        assert "This is a paragraph" in text
        assert "Another paragraph" in text
        assert len(text) > 0
    
    def test_parse_heading_hierarchy(self, complex_structure_html):
        """Test heading hierarchy extraction"""
        parser = HTMLParser(complex_structure_html)
        hierarchy = parser.parse_heading_hierarchy()
        
        assert len(hierarchy.h1) == 1
        assert "H1 Heading" in hierarchy.h1[0]
        assert len(hierarchy.h2) == 1
        assert "H2 Heading" in hierarchy.h2[0]
        assert len(hierarchy.h3) == 1
        assert "H3 Heading" in hierarchy.h3[0]
    
    def test_detect_semantic_elements(self, semantic_html):
        """Test semantic element detection"""
        parser = HTMLParser(semantic_html)
        semantic_elements = parser.detect_semantic_elements()
        
        assert 'header' in semantic_elements
        assert 'main' in semantic_elements
        assert 'footer' in semantic_elements
        assert 'nav' in semantic_elements
        assert 'article' in semantic_elements
        assert 'aside' in semantic_elements
    
    def test_no_semantic_elements(self, simple_html):
        """Test detection when no semantic elements present"""
        parser = HTMLParser(simple_html)
        semantic_elements = parser.detect_semantic_elements()
        
        assert len(semantic_elements) == 0
    
    def test_count_structural_elements(self, complex_structure_html):
        """Test counting of structural elements"""
        parser = HTMLParser(complex_structure_html)
        counts = parser.count_structural_elements()
        
        assert counts['paragraphs'] == 2
        assert counts['links'] == 2
        assert counts['images'] == 2
        assert counts['tables'] == 1
        assert counts['lists'] == 2  # ul + ol
    
    def test_detect_hidden_content(self, hidden_content_html):
        """Test hidden content detection"""
        parser = HTMLParser(hidden_content_html)
        hidden = parser.detect_hidden_content()
        
        assert hidden.display_none_count >= 2  # At least 2 display:none elements
        assert hidden.visibility_hidden_count >= 1
        assert hidden.hidden_attribute_count >= 1
        assert len(hidden.hidden_elements) > 0
    
    def test_hidden_content_still_accessible(self, hidden_content_html):
        """Test that hidden content is still in extracted text"""
        parser = HTMLParser(hidden_content_html)
        text = parser.extract_text()
        
        # Hidden content should still be extractable by scrapers
        assert "Hidden with display none" in text
        assert "Hidden with visibility" in text
        assert "Hidden with attribute" in text
    
    def test_calculate_dom_depth(self, semantic_html):
        """Test DOM depth calculation"""
        parser = HTMLParser(semantic_html)
        depth = parser.calculate_dom_depth()
        
        assert depth > 0
        assert isinstance(depth, int)
    
    def test_has_proper_structure_positive(self, semantic_html):
        """Test proper structure detection - positive case"""
        parser = HTMLParser(semantic_html)
        has_structure = parser.has_proper_structure()
        
        assert has_structure is True
    
    def test_has_proper_structure_negative(self, simple_html):
        """Test proper structure detection - negative case"""
        parser = HTMLParser(simple_html)
        has_structure = parser.has_proper_structure()
        
        assert has_structure is False
    
    def test_get_content_analysis(self, simple_html):
        """Test complete content analysis"""
        parser = HTMLParser(simple_html)
        content = parser.get_content_analysis()
        
        assert isinstance(content, ContentAnalysis)
        assert content.character_count > 0
        assert content.word_count > 0
        assert content.estimated_tokens > 0
        assert content.paragraphs == 2
    
    def test_get_structure_analysis(self, semantic_html):
        """Test complete structure analysis"""
        parser = HTMLParser(semantic_html)
        structure = parser.get_structure_analysis()
        
        assert isinstance(structure, StructureAnalysis)
        assert structure.has_semantic_html is True
        assert len(structure.semantic_elements) > 0
        assert structure.total_elements > 0
        assert structure.nested_depth > 0
        assert structure.has_proper_structure is True
    
    def test_get_all_links(self, semantic_html):
        """Test link extraction"""
        parser = HTMLParser(semantic_html)
        links = parser.get_all_links()
        
        assert len(links) == 2
        assert any(link['href'] == '/' for link in links)
        assert any(link['href'] == '/about' for link in links)
        assert all('text' in link for link in links)
    
    def test_get_all_images(self, complex_structure_html):
        """Test image extraction"""
        parser = HTMLParser(complex_structure_html)
        images = parser.get_all_images()
        
        assert len(images) == 2
        assert any(img['src'] == 'image1.jpg' for img in images)
        assert any(img['alt'] == 'Image 1' for img in images)
    
    def test_analyze_complete(self, semantic_html):
        """Test complete analysis"""
        parser = HTMLParser(semantic_html)
        content, structure, hidden = parser.analyze()
        
        assert isinstance(content, ContentAnalysis)
        assert isinstance(structure, StructureAnalysis)
        assert isinstance(hidden, HiddenContent)
        
        assert content.word_count > 0
        assert structure.has_semantic_html is True
    
    def test_empty_html(self):
        """Test handling of empty HTML"""
        parser = HTMLParser("")
        text = parser.extract_text()
        
        assert text == ""
    
    def test_malformed_html(self):
        """Test handling of malformed HTML"""
        malformed = "<html><body><p>Unclosed paragraph<div>Content</body>"
        parser = HTMLParser(malformed)
        
        # Should not raise exception
        text = parser.extract_text()
        assert len(text) > 0
    
    def test_script_and_style_excluded(self):
        """Test that script and style tags are excluded from text"""
        html = """
        <html>
        <body>
            <p>Visible text</p>
            <script>var x = 1;</script>
            <style>.class { color: red; }</style>
        </body>
        </html>
        """
        parser = HTMLParser(html)
        text = parser.extract_text()
        
        assert "Visible text" in text
        assert "var x = 1" not in text
        assert "color: red" not in text
    
    def test_nested_elements(self):
        """Test handling of deeply nested elements"""
        html = """
        <html>
        <body>
            <div>
                <div>
                    <div>
                        <div>
                            <p>Deeply nested content</p>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        parser = HTMLParser(html)
        depth = parser.calculate_dom_depth()
        
        assert depth >= 5
    
    def test_multiple_h1_headings(self):
        """Test handling of multiple H1 headings"""
        html = """
        <html>
        <body>
            <h1>First H1</h1>
            <h1>Second H1</h1>
            <h1>Third H1</h1>
        </body>
        </html>
        """
        parser = HTMLParser(html)
        hierarchy = parser.parse_heading_hierarchy()
        
        assert len(hierarchy.h1) == 3
    
    def test_links_without_href(self):
        """Test handling of links without href attribute"""
        html = """
        <html>
        <body>
            <a>Link without href</a>
            <a href="page.html">Link with href</a>
        </body>
        </html>
        """
        parser = HTMLParser(html)
        links = parser.get_all_links()
        
        # Should only return links with href
        assert len(links) == 1
        assert links[0]['href'] == 'page.html'
    
    def test_images_without_alt(self):
        """Test handling of images without alt text"""
        html = """
        <html>
        <body>
            <img src="image.jpg">
            <img src="image2.jpg" alt="Description">
        </body>
        </html>
        """
        parser = HTMLParser(html)
        images = parser.get_all_images()
        
        assert len(images) == 2
        assert images[0]['alt'] == ''
        assert images[1]['alt'] == 'Description'

