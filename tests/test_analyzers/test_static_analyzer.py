"""
Unit tests for StaticAnalyzer
"""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from src.analyzers.static_analyzer import StaticAnalyzer
from src.models.analysis_result import AnalysisResult


class TestStaticAnalyzer:
    """Test suite for StaticAnalyzer class"""
    
    @pytest.fixture
    def sample_html(self):
        """Sample HTML for testing"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Page</title>
            <meta name="description" content="Test description">
            <script type="application/ld+json">
            {"@context": "https://schema.org", "@type": "Article", "headline": "Test"}
            </script>
        </head>
        <body>
            <header>
                <h1>Main Heading</h1>
                <nav><a href="/about">About</a></nav>
            </header>
            <main>
                <article>
                    <h2>Article Title</h2>
                    <p>This is a test paragraph with some content.</p>
                </article>
            </main>
            <script src="https://cdn.example.com/script.js"></script>
        </body>
        </html>
        """
    
    @pytest.fixture
    def mock_response(self, sample_html):
        """Mock HTTP response"""
        response = Mock()
        response.text = sample_html
        response.status_code = 200
        response.raise_for_status = Mock()
        return response
    
    def test_analyzer_initialization(self):
        """Test analyzer initializes correctly"""
        analyzer = StaticAnalyzer()
        assert analyzer.session is not None
        assert analyzer.timeout > 0
        assert analyzer.user_agent is not None
    
    def test_custom_timeout(self):
        """Test custom timeout setting"""
        analyzer = StaticAnalyzer(timeout=60)
        assert analyzer.timeout == 60
    
    def test_custom_user_agent(self):
        """Test custom user agent setting"""
        custom_ua = "CustomBot/1.0"
        analyzer = StaticAnalyzer(user_agent=custom_ua)
        assert analyzer.user_agent == custom_ua
    
    @patch('src.analyzers.static_analyzer.requests.Session.get')
    def test_fetch_html_success(self, mock_get, mock_response, sample_html):
        """Test successful HTML fetch"""
        mock_get.return_value = mock_response
        
        analyzer = StaticAnalyzer()
        html, status, response_time = analyzer.fetch_html('https://example.com')
        
        assert html == sample_html
        assert status == 200
        assert response_time >= 0
        mock_get.assert_called_once()
    
    @patch('src.analyzers.static_analyzer.requests.Session.get')
    def test_fetch_html_timeout(self, mock_get):
        """Test fetch HTML with timeout"""
        mock_get.side_effect = requests.Timeout("Request timeout")
        
        analyzer = StaticAnalyzer()
        with pytest.raises(requests.Timeout):
            analyzer.fetch_html('https://example.com')
    
    @patch('src.analyzers.static_analyzer.requests.Session.get')
    def test_fetch_html_request_error(self, mock_get):
        """Test fetch HTML with request error"""
        mock_get.side_effect = requests.RequestException("Connection error")
        
        analyzer = StaticAnalyzer()
        with pytest.raises(requests.RequestException):
            analyzer.fetch_html('https://example.com')
    
    @patch('src.analyzers.static_analyzer.requests.Session.get')
    def test_analyze_success(self, mock_get, mock_response):
        """Test successful analysis"""
        mock_get.return_value = mock_response
        
        analyzer = StaticAnalyzer()
        result = analyzer.analyze('https://example.com')
        
        assert isinstance(result, AnalysisResult)
        assert result.status == 'success'
        assert result.url == 'https://example.com'
        assert result.content_analysis is not None
        assert result.structure_analysis is not None
        assert result.meta_analysis is not None
        assert result.javascript_analysis is not None
        assert result.analysis_duration_seconds is not None
        assert result.page_load_time_seconds is not None
        assert result.page_size_bytes is not None
    
    @patch('src.analyzers.static_analyzer.requests.Session.get')
    def test_analyze_content_analysis(self, mock_get, mock_response):
        """Test content analysis in result"""
        mock_get.return_value = mock_response
        
        analyzer = StaticAnalyzer()
        result = analyzer.analyze('https://example.com')
        
        assert result.content_analysis.word_count > 0
        assert result.content_analysis.character_count > 0
        assert result.content_analysis.paragraphs > 0
    
    @patch('src.analyzers.static_analyzer.requests.Session.get')
    def test_analyze_structure_analysis(self, mock_get, mock_response):
        """Test structure analysis in result"""
        mock_get.return_value = mock_response
        
        analyzer = StaticAnalyzer()
        result = analyzer.analyze('https://example.com')
        
        assert result.structure_analysis.has_semantic_html is True
        assert len(result.structure_analysis.semantic_elements) > 0
        assert len(result.structure_analysis.heading_hierarchy.h1) > 0
    
    @patch('src.analyzers.static_analyzer.requests.Session.get')
    def test_analyze_meta_analysis(self, mock_get, mock_response):
        """Test meta analysis in result"""
        mock_get.return_value = mock_response
        
        analyzer = StaticAnalyzer()
        result = analyzer.analyze('https://example.com')
        
        assert result.meta_analysis.title == "Test Page"
        assert result.meta_analysis.description == "Test description"
    
    @patch('src.analyzers.static_analyzer.requests.Session.get')
    def test_analyze_structured_data(self, mock_get, mock_response):
        """Test structured data analysis in result"""
        mock_get.return_value = mock_response
        
        analyzer = StaticAnalyzer()
        result = analyzer.analyze('https://example.com')
        
        assert result.meta_analysis.has_json_ld is True
        assert len(result.meta_analysis.structured_data) > 0
    
    @patch('src.analyzers.static_analyzer.requests.Session.get')
    def test_analyze_javascript_analysis(self, mock_get, mock_response):
        """Test JavaScript analysis in result"""
        mock_get.return_value = mock_response
        
        analyzer = StaticAnalyzer()
        result = analyzer.analyze('https://example.com')
        
        assert result.javascript_analysis.total_scripts > 0
        assert result.javascript_analysis.external_scripts > 0
    
    def test_analyze_invalid_url(self):
        """Test analysis with invalid URL"""
        analyzer = StaticAnalyzer()
        result = analyzer.analyze('not-a-valid-url')
        
        assert result.status == 'error'
        assert 'Invalid URL' in result.error_message
    
    def test_analyze_empty_url(self):
        """Test analysis with empty URL"""
        analyzer = StaticAnalyzer()
        result = analyzer.analyze('')
        
        assert result.status == 'error'
        assert result.error_message is not None
    
    @patch('src.analyzers.static_analyzer.requests.Session.get')
    def test_analyze_timeout_error(self, mock_get):
        """Test analysis with timeout error"""
        mock_get.side_effect = requests.Timeout("Timeout")
        
        analyzer = StaticAnalyzer()
        result = analyzer.analyze('https://example.com')
        
        assert result.status == 'error'
        assert 'timeout' in result.error_message.lower()
    
    @patch('src.analyzers.static_analyzer.requests.Session.get')
    def test_analyze_request_error(self, mock_get):
        """Test analysis with request error"""
        mock_get.side_effect = requests.RequestException("Connection failed")
        
        analyzer = StaticAnalyzer()
        result = analyzer.analyze('https://example.com')
        
        assert result.status == 'error'
        assert 'failed' in result.error_message.lower()
    
    @patch('src.analyzers.static_analyzer.requests.Session.get')
    def test_analyze_page_size_limit(self, mock_get):
        """Test analysis with page size exceeding limit"""
        # Create a very large HTML content
        large_html = "<html><body>" + ("x" * 20 * 1024 * 1024) + "</body></html>"
        response = Mock()
        response.text = large_html
        response.status_code = 200
        response.raise_for_status = Mock()
        mock_get.return_value = response
        
        analyzer = StaticAnalyzer()
        result = analyzer.analyze('https://example.com')
        
        assert result.status == 'error'
        assert 'size exceeds' in result.error_message.lower()
    
    @patch('src.analyzers.static_analyzer.requests.Session.get')
    def test_analyze_with_redirects(self, mock_get, mock_response):
        """Test analysis follows redirects"""
        mock_get.return_value = mock_response
        
        analyzer = StaticAnalyzer()
        result = analyzer.analyze('http://example.com')
        
        # Verify allow_redirects was passed
        call_kwargs = mock_get.call_args[1]
        assert call_kwargs['allow_redirects'] is True
    
    def test_context_manager(self):
        """Test analyzer as context manager"""
        with StaticAnalyzer() as analyzer:
            assert analyzer.session is not None
        # Session should be closed after context
    
    def test_close_session(self):
        """Test closing session"""
        analyzer = StaticAnalyzer()
        analyzer.close()
        # Should not raise exception
    
    @patch('src.analyzers.static_analyzer.requests.Session.get')
    def test_user_agent_in_headers(self, mock_get, mock_response):
        """Test User-Agent header is set"""
        mock_get.return_value = mock_response
        
        analyzer = StaticAnalyzer()
        analyzer.fetch_html('https://example.com')
        
        assert 'User-Agent' in analyzer.session.headers
    
    @patch('src.analyzers.static_analyzer.requests.Session.get')
    def test_accept_headers(self, mock_get, mock_response):
        """Test Accept headers are set correctly"""
        mock_get.return_value = mock_response
        
        analyzer = StaticAnalyzer()
        analyzer.fetch_html('https://example.com')
        
        assert 'Accept' in analyzer.session.headers
        assert 'Accept-Language' in analyzer.session.headers
    
    @patch('src.analyzers.static_analyzer.requests.Session.get')
    def test_url_normalization(self, mock_get, mock_response):
        """Test URL normalization"""
        mock_get.return_value = mock_response
        
        analyzer = StaticAnalyzer()
        result = analyzer.analyze('example.com')  # No scheme
        
        # Should normalize to https://example.com
        assert result.url == 'https://example.com'
    
    @patch('src.analyzers.static_analyzer.requests.Session.get')
    def test_analyze_timing_metrics(self, mock_get, mock_response):
        """Test timing metrics are captured"""
        mock_get.return_value = mock_response
        
        analyzer = StaticAnalyzer()
        result = analyzer.analyze('https://example.com')
        
        assert result.analysis_duration_seconds is not None
        assert result.analysis_duration_seconds > 0
        assert result.page_load_time_seconds is not None
        assert result.page_load_time_seconds >= 0
    
    @patch('src.analyzers.static_analyzer.requests.Session.get')
    def test_analyze_page_size(self, mock_get, mock_response, sample_html):
        """Test page size is calculated"""
        mock_get.return_value = mock_response
        
        analyzer = StaticAnalyzer()
        result = analyzer.analyze('https://example.com')
        
        assert result.page_size_bytes is not None
        assert result.page_size_bytes == len(sample_html.encode('utf-8'))
    
    @patch('src.analyzers.static_analyzer.requests.Session.get')
    def test_analyze_timestamp(self, mock_get, mock_response):
        """Test analyzed_at timestamp is set"""
        mock_get.return_value = mock_response
        
        analyzer = StaticAnalyzer()
        result = analyzer.analyze('https://example.com')
        
        assert result.analyzed_at is not None
        from datetime import datetime
        assert isinstance(result.analyzed_at, datetime)
    
    @patch('src.analyzers.static_analyzer.HTMLParser')
    @patch('src.analyzers.static_analyzer.requests.Session.get')
    def test_analyze_parser_exception(self, mock_get, mock_parser, mock_response):
        """Test analysis handles parser exceptions"""
        mock_get.return_value = mock_response
        mock_parser.side_effect = Exception("Parser error")
        
        analyzer = StaticAnalyzer()
        result = analyzer.analyze('https://example.com')
        
        assert result.status == 'error'
        assert 'failed' in result.error_message.lower()

