"""
Unit tests for StructuredDataParser
"""

import pytest
import json
from src.parsers.structured_data_parser import StructuredDataParser
from src.models.analysis_result import StructuredData


class TestStructuredDataParser:
    """Test suite for StructuredDataParser class"""
    
    @pytest.fixture
    def json_ld_html(self):
        """HTML with JSON-LD structured data"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>JSON-LD Test</title>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": "Test Article",
                "author": {
                    "@type": "Person",
                    "name": "John Doe"
                },
                "datePublished": "2024-01-01"
            }
            </script>
        </head>
        <body>
            <p>Content</p>
        </body>
        </html>
        """
    
    @pytest.fixture
    def multiple_json_ld_html(self):
        """HTML with multiple JSON-LD blocks"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": "Test Org"
            }
            </script>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "WebSite",
                "url": "https://example.com"
            }
            </script>
        </head>
        <body></body>
        </html>
        """
    
    @pytest.fixture
    def microdata_html(self):
        """HTML with Microdata"""
        return """
        <!DOCTYPE html>
        <html>
        <body>
            <div itemscope itemtype="https://schema.org/Person">
                <span itemprop="name">Jane Doe</span>
                <span itemprop="jobTitle">Software Engineer</span>
                <a itemprop="url" href="https://janedoe.com">Website</a>
            </div>
        </body>
        </html>
        """
    
    @pytest.fixture
    def nested_microdata_html(self):
        """HTML with nested Microdata"""
        return """
        <!DOCTYPE html>
        <html>
        <body>
            <div itemscope itemtype="https://schema.org/Person">
                <span itemprop="name">John Smith</span>
                <div itemprop="address" itemscope itemtype="https://schema.org/PostalAddress">
                    <span itemprop="streetAddress">123 Main St</span>
                    <span itemprop="addressLocality">Springfield</span>
                </div>
            </div>
        </body>
        </html>
        """
    
    @pytest.fixture
    def rdfa_html(self):
        """HTML with RDFa"""
        return """
        <!DOCTYPE html>
        <html>
        <body vocab="https://schema.org/">
            <div typeof="Person">
                <span property="name">Bob Johnson</span>
                <span property="jobTitle">Designer</span>
                <a property="url" href="https://bobjohnson.com">Portfolio</a>
            </div>
        </body>
        </html>
        """
    
    @pytest.fixture
    def all_types_html(self):
        """HTML with all types of structured data"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": "Complete Test"
            }
            </script>
        </head>
        <body vocab="https://schema.org/">
            <div itemscope itemtype="https://schema.org/Product">
                <span itemprop="name">Product Name</span>
            </div>
            <div typeof="Organization">
                <span property="name">Company Name</span>
            </div>
        </body>
        </html>
        """
    
    @pytest.fixture
    def no_structured_data_html(self):
        """HTML with no structured data"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Plain Page</title>
        </head>
        <body>
            <p>No structured data here</p>
        </body>
        </html>
        """
    
    def test_parser_initialization(self, json_ld_html):
        """Test parser initializes correctly"""
        parser = StructuredDataParser(json_ld_html)
        assert parser.soup is not None
        assert parser.html_content == json_ld_html
    
    def test_extract_json_ld(self, json_ld_html):
        """Test JSON-LD extraction"""
        parser = StructuredDataParser(json_ld_html)
        json_ld_data = parser.extract_json_ld()
        
        assert len(json_ld_data) == 1
        assert json_ld_data[0]['@type'] == 'Article'
        assert json_ld_data[0]['headline'] == 'Test Article'
        assert json_ld_data[0]['author']['name'] == 'John Doe'
    
    def test_extract_multiple_json_ld(self, multiple_json_ld_html):
        """Test extraction of multiple JSON-LD blocks"""
        parser = StructuredDataParser(multiple_json_ld_html)
        json_ld_data = parser.extract_json_ld()
        
        assert len(json_ld_data) == 2
        types = [data['@type'] for data in json_ld_data]
        assert 'Organization' in types
        assert 'WebSite' in types
    
    def test_extract_json_ld_array(self):
        """Test JSON-LD with array format"""
        html = """
        <html>
        <head>
            <script type="application/ld+json">
            [
                {"@type": "Person", "name": "Alice"},
                {"@type": "Person", "name": "Bob"}
            ]
            </script>
        </head>
        <body></body>
        </html>
        """
        parser = StructuredDataParser(html)
        json_ld_data = parser.extract_json_ld()
        
        assert len(json_ld_data) == 2
        assert json_ld_data[0]['name'] == 'Alice'
        assert json_ld_data[1]['name'] == 'Bob'
    
    def test_extract_microdata(self, microdata_html):
        """Test Microdata extraction"""
        parser = StructuredDataParser(microdata_html)
        microdata = parser.extract_microdata()
        
        assert len(microdata) == 1
        assert microdata[0]['@type'] == 'https://schema.org/Person'
        assert 'properties' in microdata[0]
        assert microdata[0]['properties']['name'] == 'Jane Doe'
        assert microdata[0]['properties']['jobTitle'] == 'Software Engineer'
    
    def test_extract_nested_microdata(self, nested_microdata_html):
        """Test nested Microdata extraction"""
        parser = StructuredDataParser(nested_microdata_html)
        microdata = parser.extract_microdata()
        
        # Nested items are extracted both as standalone and within parent
        assert len(microdata) >= 1
        
        # Find the Person item
        person_item = next((item for item in microdata if item['@type'] == 'https://schema.org/Person'), None)
        assert person_item is not None
        assert person_item['properties']['name'] == 'John Smith'
        assert 'address' in person_item['properties']
        assert isinstance(person_item['properties']['address'], dict)
        assert person_item['properties']['address']['@type'] == 'https://schema.org/PostalAddress'
    
    def test_extract_rdfa(self, rdfa_html):
        """Test RDFa extraction"""
        parser = StructuredDataParser(rdfa_html)
        rdfa_data = parser.extract_rdfa()
        
        assert len(rdfa_data) == 1
        assert rdfa_data[0]['@type'] == 'Person'
        assert 'properties' in rdfa_data[0]
        assert rdfa_data[0]['properties']['name'] == 'Bob Johnson'
        assert rdfa_data[0]['properties']['jobTitle'] == 'Designer'
    
    def test_has_json_ld_positive(self, json_ld_html):
        """Test JSON-LD detection - positive case"""
        parser = StructuredDataParser(json_ld_html)
        assert parser.has_json_ld() is True
    
    def test_has_json_ld_negative(self, no_structured_data_html):
        """Test JSON-LD detection - negative case"""
        parser = StructuredDataParser(no_structured_data_html)
        assert parser.has_json_ld() is False
    
    def test_has_microdata_positive(self, microdata_html):
        """Test Microdata detection - positive case"""
        parser = StructuredDataParser(microdata_html)
        assert parser.has_microdata() is True
    
    def test_has_microdata_negative(self, no_structured_data_html):
        """Test Microdata detection - negative case"""
        parser = StructuredDataParser(no_structured_data_html)
        assert parser.has_microdata() is False
    
    def test_has_rdfa_positive(self, rdfa_html):
        """Test RDFa detection - positive case"""
        parser = StructuredDataParser(rdfa_html)
        assert parser.has_rdfa() is True
    
    def test_has_rdfa_negative(self, no_structured_data_html):
        """Test RDFa detection - negative case"""
        parser = StructuredDataParser(no_structured_data_html)
        assert parser.has_rdfa() is False
    
    def test_get_all_structured_data(self, all_types_html):
        """Test getting all types of structured data"""
        parser = StructuredDataParser(all_types_html)
        all_data = parser.get_all_structured_data()
        
        assert len(all_data) == 3  # JSON-LD + Microdata + RDFa
        assert all(isinstance(item, StructuredData) for item in all_data)
        
        types = [item.type for item in all_data]
        assert 'json-ld' in types
        assert 'microdata' in types
        assert 'rdfa' in types
    
    def test_analyze_complete(self, all_types_html):
        """Test complete analysis"""
        parser = StructuredDataParser(all_types_html)
        result = parser.analyze()
        
        assert 'structured_data' in result
        assert 'has_json_ld' in result
        assert 'has_microdata' in result
        assert 'has_rdfa' in result
        
        assert result['has_json_ld'] is True
        assert result['has_microdata'] is True
        assert result['has_rdfa'] is True
        assert len(result['structured_data']) == 3
    
    def test_no_structured_data(self, no_structured_data_html):
        """Test page with no structured data"""
        parser = StructuredDataParser(no_structured_data_html)
        result = parser.analyze()
        
        assert result['has_json_ld'] is False
        assert result['has_microdata'] is False
        assert result['has_rdfa'] is False
        assert len(result['structured_data']) == 0
    
    def test_malformed_json_ld(self):
        """Test handling of malformed JSON-LD"""
        html = """
        <html>
        <head>
            <script type="application/ld+json">
            {
                "@type": "Article",
                "headline": "Test",
                // This is invalid JSON
            }
            </script>
        </head>
        <body></body>
        </html>
        """
        parser = StructuredDataParser(html)
        json_ld_data = parser.extract_json_ld()
        
        # Should handle gracefully and return empty list
        assert len(json_ld_data) == 0
    
    def test_empty_json_ld_script(self):
        """Test handling of empty JSON-LD script"""
        html = """
        <html>
        <head>
            <script type="application/ld+json"></script>
        </head>
        <body></body>
        </html>
        """
        parser = StructuredDataParser(html)
        json_ld_data = parser.extract_json_ld()
        
        assert len(json_ld_data) == 0
    
    def test_microdata_with_meta_tag(self):
        """Test Microdata with meta tag property"""
        html = """
        <html>
        <body>
            <div itemscope itemtype="https://schema.org/Article">
                <meta itemprop="datePublished" content="2024-01-01">
                <span itemprop="headline">Article Title</span>
            </div>
        </body>
        </html>
        """
        parser = StructuredDataParser(html)
        microdata = parser.extract_microdata()
        
        assert len(microdata) == 1
        assert microdata[0]['properties']['datePublished'] == '2024-01-01'
        assert microdata[0]['properties']['headline'] == 'Article Title'
    
    def test_microdata_with_link(self):
        """Test Microdata with link property"""
        html = """
        <html>
        <body>
            <div itemscope itemtype="https://schema.org/Person">
                <a itemprop="url" href="https://example.com">Website</a>
            </div>
        </body>
        </html>
        """
        parser = StructuredDataParser(html)
        microdata = parser.extract_microdata()
        
        assert microdata[0]['properties']['url'] == 'https://example.com'
    
    def test_microdata_with_image(self):
        """Test Microdata with image property"""
        html = """
        <html>
        <body>
            <div itemscope itemtype="https://schema.org/Product">
                <img itemprop="image" src="product.jpg" alt="Product">
            </div>
        </body>
        </html>
        """
        parser = StructuredDataParser(html)
        microdata = parser.extract_microdata()
        
        assert microdata[0]['properties']['image'] == 'product.jpg'
    
    def test_microdata_with_time(self):
        """Test Microdata with time element"""
        html = """
        <html>
        <body>
            <div itemscope itemtype="https://schema.org/Event">
                <time itemprop="startDate" datetime="2024-12-31T20:00">New Year's Eve</time>
            </div>
        </body>
        </html>
        """
        parser = StructuredDataParser(html)
        microdata = parser.extract_microdata()
        
        assert microdata[0]['properties']['startDate'] == '2024-12-31T20:00'
    
    def test_microdata_multiple_same_property(self):
        """Test Microdata with multiple properties of same name"""
        html = """
        <html>
        <body>
            <div itemscope itemtype="https://schema.org/Person">
                <span itemprop="email">first@example.com</span>
                <span itemprop="email">second@example.com</span>
            </div>
        </body>
        </html>
        """
        parser = StructuredDataParser(html)
        microdata = parser.extract_microdata()
        
        assert isinstance(microdata[0]['properties']['email'], list)
        assert len(microdata[0]['properties']['email']) == 2
        assert 'first@example.com' in microdata[0]['properties']['email']
    
    def test_rdfa_with_vocab(self, rdfa_html):
        """Test RDFa with vocab attribute"""
        parser = StructuredDataParser(rdfa_html)
        rdfa_data = parser.extract_rdfa()
        
        # vocab is on parent element, check typeof element
        assert len(rdfa_data) == 1
    
    def test_rdfa_with_content_attribute(self):
        """Test RDFa with content attribute"""
        html = """
        <html>
        <body vocab="https://schema.org/">
            <div typeof="Article">
                <meta property="datePublished" content="2024-01-01">
                <span property="headline">Article Headline</span>
            </div>
        </body>
        </html>
        """
        parser = StructuredDataParser(html)
        rdfa_data = parser.extract_rdfa()
        
        assert rdfa_data[0]['properties']['datePublished'] == '2024-01-01'
        assert rdfa_data[0]['properties']['headline'] == 'Article Headline'
    
    def test_empty_html(self):
        """Test handling of empty HTML"""
        parser = StructuredDataParser("")
        result = parser.analyze()
        
        assert len(result['structured_data']) == 0
        assert result['has_json_ld'] is False
    
    def test_malformed_html(self):
        """Test handling of malformed HTML"""
        malformed = "<html><body><div itemscope><span itemprop='name'>Test"
        parser = StructuredDataParser(malformed)
        
        # Should not raise exception
        microdata = parser.extract_microdata()
        assert isinstance(microdata, list)
    
    def test_json_ld_with_context_array(self):
        """Test JSON-LD with context as array"""
        html = """
        <html>
        <head>
            <script type="application/ld+json">
            {
                "@context": ["https://schema.org", "https://example.com/vocab"],
                "@type": "Thing",
                "name": "Test"
            }
            </script>
        </head>
        <body></body>
        </html>
        """
        parser = StructuredDataParser(html)
        json_ld_data = parser.extract_json_ld()
        
        assert len(json_ld_data) == 1
        assert json_ld_data[0]['name'] == 'Test'
    
    def test_microdata_with_itemid(self):
        """Test Microdata with itemid attribute"""
        html = """
        <html>
        <body>
            <div itemscope itemtype="https://schema.org/Product" itemid="#product1">
                <span itemprop="name">Product Name</span>
            </div>
        </body>
        </html>
        """
        parser = StructuredDataParser(html)
        microdata = parser.extract_microdata()
        
        assert microdata[0]['@id'] == '#product1'
    
    def test_rdfa_with_resource(self):
        """Test RDFa with resource attribute"""
        html = """
        <html>
        <body vocab="https://schema.org/">
            <div typeof="Person" resource="#person1">
                <span property="name">John Doe</span>
            </div>
        </body>
        </html>
        """
        parser = StructuredDataParser(html)
        rdfa_data = parser.extract_rdfa()
        
        assert rdfa_data[0]['@id'] == '#person1'

