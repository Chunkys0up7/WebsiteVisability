"""
Unit tests for DynamicAnalyzer
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from playwright.async_api import Error as PlaywrightError
from src.analyzers.dynamic_analyzer import DynamicAnalyzer
from src.models.analysis_result import AnalysisResult


class TestDynamicAnalyzer:
    """Test suite for DynamicAnalyzer class"""
    
    @pytest.fixture
    def sample_html(self):
        """Sample rendered HTML for testing"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dynamic Test Page</title>
            <meta name="description" content="Dynamically rendered content">
            <script type="application/ld+json">
            {"@context": "https://schema.org", "@type": "WebPage", "name": "Test"}
            </script>
        </head>
        <body>
            <header>
                <h1>Dynamically Loaded Content</h1>
                <nav><a href="/home">Home</a></nav>
            </header>
            <main id="app">
                <article>
                    <h2>Article rendered by JavaScript</h2>
                    <p>This content was loaded dynamically.</p>
                </article>
            </main>
            <script src="https://cdn.example.com/react.js"></script>
            <script>
                fetch('/api/data').then(r => r.json());
            </script>
        </body>
        </html>
        """
    
    def test_analyzer_initialization(self):
        """Test analyzer initializes correctly"""
        analyzer = DynamicAnalyzer()
        assert analyzer.timeout > 0
        assert analyzer.user_agent is not None
        assert analyzer.headless is True
    
    def test_custom_timeout(self):
        """Test custom timeout setting"""
        analyzer = DynamicAnalyzer(timeout=60)
        assert analyzer.timeout == 60000  # Converted to milliseconds
    
    def test_custom_user_agent(self):
        """Test custom user agent setting"""
        custom_ua = "CustomBot/2.0"
        analyzer = DynamicAnalyzer(user_agent=custom_ua)
        assert analyzer.user_agent == custom_ua
    
    def test_headless_mode(self):
        """Test headless mode configuration"""
        analyzer = DynamicAnalyzer(headless=False)
        assert analyzer.headless is False
    
    @pytest.mark.asyncio
    async def test_close_browser(self):
        """Test browser closing"""
        analyzer = DynamicAnalyzer()
        mock_browser = AsyncMock()
        mock_playwright = AsyncMock()
        
        analyzer._browser = mock_browser
        analyzer._playwright = mock_playwright
        
        await analyzer._close_browser()
        
        mock_browser.close.assert_called_once()
        mock_playwright.stop.assert_called_once()
        assert analyzer._browser is None
        assert analyzer._playwright is None
    
    def test_analyze_invalid_url(self):
        """Test analysis with invalid URL"""
        analyzer = DynamicAnalyzer()
        result = analyzer.analyze('not-a-valid-url')
        
        assert result.status == 'error'
        assert 'Invalid URL' in result.error_message
    
    def test_analyze_empty_url(self):
        """Test analysis with empty URL"""
        analyzer = DynamicAnalyzer()
        result = analyzer.analyze('')
        
        assert result.status == 'error'
        assert result.error_message is not None
    
    @pytest.mark.asyncio
    async def test_analyze_async_invalid_url(self):
        """Test async analysis with invalid URL"""
        analyzer = DynamicAnalyzer()
        result = await analyzer.analyze_async('invalid-url')
        
        assert result.status == 'error'
        assert 'Invalid URL' in result.error_message
    
    @pytest.mark.asyncio
    async def test_context_manager_async(self):
        """Test async context manager"""
        with patch('src.analyzers.dynamic_analyzer.async_playwright'):
            async with DynamicAnalyzer() as analyzer:
                assert analyzer is not None
            # Browser should be closed after context
    
    def test_analyze_synchronous_wrapper(self, sample_html):
        """Test synchronous analyze wrapper"""
        with patch('src.analyzers.dynamic_analyzer.async_playwright') as mock_pw_factory:
            # Create complete mock chain
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock(return_value=Mock(status=200))
            mock_page.wait_for_load_state = AsyncMock()
            mock_page.content = AsyncMock(return_value=sample_html)
            mock_page.close = AsyncMock()
            mock_page.set_default_timeout = Mock()
            mock_page.on = Mock()
            
            mock_context = AsyncMock()
            mock_context.new_page = AsyncMock(return_value=mock_page)
            mock_context.close = AsyncMock()
            mock_page.context = mock_context
            
            mock_browser = AsyncMock()
            mock_browser.new_context = AsyncMock(return_value=mock_context)
            mock_browser.close = AsyncMock()
            
            mock_playwright = AsyncMock()
            mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_playwright.stop = AsyncMock()
            
            mock_pw_factory.return_value.start = AsyncMock(return_value=mock_playwright)
            
            analyzer = DynamicAnalyzer()
            result = analyzer.analyze('https://example.com')
            
            assert isinstance(result, AnalysisResult)
            assert result.status == 'success'
            assert result.content_analysis is not None
    
    @pytest.mark.asyncio
    async def test_analyze_async_success(self, sample_html):
        """Test successful async analysis"""
        with patch('src.analyzers.dynamic_analyzer.async_playwright') as mock_pw_factory:
            # Mock Windows Store Python detection to return False
            with patch.object(DynamicAnalyzer, '_check_windows_store_python', return_value=False):
                mock_page = AsyncMock()
                mock_page.goto = AsyncMock(return_value=Mock(status=200))
                mock_page.wait_for_load_state = AsyncMock()
                mock_page.content = AsyncMock(return_value=sample_html)
                mock_page.close = AsyncMock()
                mock_page.set_default_timeout = Mock()
                mock_page.on = Mock()
                
                mock_context = AsyncMock()
                mock_context.new_page = AsyncMock(return_value=mock_page)
                mock_context.close = AsyncMock()
                mock_page.context = mock_context
                
                mock_browser = AsyncMock()
                mock_browser.new_context = AsyncMock(return_value=mock_context)
                mock_browser.close = AsyncMock()
                
                mock_playwright = AsyncMock()
                mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
                mock_playwright.stop = AsyncMock()
                
                mock_pw_factory.return_value.start = AsyncMock(return_value=mock_playwright)
                
                analyzer = DynamicAnalyzer()
                result = await analyzer.analyze_async('https://example.com')
                
                assert isinstance(result, AnalysisResult)
                assert result.status == 'success'
                assert result.url == 'https://example.com'
            assert result.content_analysis is not None
            assert result.structure_analysis is not None
            assert result.meta_analysis is not None
            assert result.javascript_analysis is not None
    
    @pytest.mark.asyncio
    async def test_fetch_rendered_html_success(self, sample_html):
        """Test successful HTML fetch and render"""
        with patch('src.analyzers.dynamic_analyzer.async_playwright') as mock_pw_factory:
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock(return_value=Mock(status=200))
            mock_page.wait_for_load_state = AsyncMock()
            mock_page.content = AsyncMock(return_value=sample_html)
            mock_page.close = AsyncMock()
            mock_page.set_default_timeout = Mock()
            mock_page.on = Mock()
            
            mock_context = AsyncMock()
            mock_context.new_page = AsyncMock(return_value=mock_page)
            mock_context.close = AsyncMock()
            mock_page.context = mock_context
            
            mock_browser = AsyncMock()
            mock_browser.new_context = AsyncMock(return_value=mock_context)
            mock_browser.close = AsyncMock()
            
            mock_playwright = AsyncMock()
            mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_playwright.stop = AsyncMock()
            
            mock_pw_factory.return_value.start = AsyncMock(return_value=mock_playwright)
            
            analyzer = DynamicAnalyzer()
            html, status, response_time, ajax_requests = await analyzer.fetch_rendered_html(
                'https://example.com'
            )
            
            assert html == sample_html
            assert status == 200
            assert response_time >= 0
            assert isinstance(ajax_requests, list)
    
    @pytest.mark.asyncio
    async def test_analyze_timeout_error(self):
        """Test analysis with timeout error"""
        with patch('src.analyzers.dynamic_analyzer.async_playwright') as mock_pw_factory:
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock(side_effect=PlaywrightError("Timeout 30000ms exceeded"))
            mock_page.close = AsyncMock()
            mock_page.set_default_timeout = Mock()
            mock_page.on = Mock()
            
            mock_context = AsyncMock()
            mock_context.new_page = AsyncMock(return_value=mock_page)
            mock_context.close = AsyncMock()
            mock_page.context = mock_context
            
            mock_browser = AsyncMock()
            mock_browser.new_context = AsyncMock(return_value=mock_context)
            mock_browser.close = AsyncMock()
            
            mock_playwright = AsyncMock()
            mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_playwright.stop = AsyncMock()
            
            mock_pw_factory.return_value.start = AsyncMock(return_value=mock_playwright)
            
            analyzer = DynamicAnalyzer()
            result = await analyzer.analyze_async('https://example.com')
            
            assert result.status == 'error'
            assert 'timeout' in result.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_analyze_page_size_limit(self):
        """Test analysis with page size exceeding limit"""
        large_html = "<html><body>" + ("x" * 20 * 1024 * 1024) + "</body></html>"
        
        with patch('src.analyzers.dynamic_analyzer.async_playwright') as mock_pw_factory:
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock(return_value=Mock(status=200))
            mock_page.wait_for_load_state = AsyncMock()
            mock_page.content = AsyncMock(return_value=large_html)
            mock_page.close = AsyncMock()
            mock_page.set_default_timeout = Mock()
            mock_page.on = Mock()
            
            mock_context = AsyncMock()
            mock_context.new_page = AsyncMock(return_value=mock_page)
            mock_context.close = AsyncMock()
            mock_page.context = mock_context
            
            mock_browser = AsyncMock()
            mock_browser.new_context = AsyncMock(return_value=mock_context)
            mock_browser.close = AsyncMock()
            
            mock_playwright = AsyncMock()
            mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_playwright.stop = AsyncMock()
            
            mock_pw_factory.return_value.start = AsyncMock(return_value=mock_playwright)
            
            analyzer = DynamicAnalyzer()
            result = await analyzer.analyze_async('https://example.com')
            
            assert result.status == 'error'
            assert 'size exceeds' in result.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_url_normalization(self, sample_html):
        """Test URL normalization in dynamic analyzer"""
        with patch('src.analyzers.dynamic_analyzer.async_playwright') as mock_pw_factory:
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock(return_value=Mock(status=200))
            mock_page.wait_for_load_state = AsyncMock()
            mock_page.content = AsyncMock(return_value=sample_html)
            mock_page.close = AsyncMock()
            mock_page.set_default_timeout = Mock()
            mock_page.on = Mock()
            
            mock_context = AsyncMock()
            mock_context.new_page = AsyncMock(return_value=mock_page)
            mock_context.close = AsyncMock()
            mock_page.context = mock_context
            
            mock_browser = AsyncMock()
            mock_browser.new_context = AsyncMock(return_value=mock_context)
            mock_browser.close = AsyncMock()
            
            mock_playwright = AsyncMock()
            mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_playwright.stop = AsyncMock()
            
            mock_pw_factory.return_value.start = AsyncMock(return_value=mock_playwright)
            
            analyzer = DynamicAnalyzer()
            result = await analyzer.analyze_async('example.com')
            
            # Should normalize to https://example.com
            assert result.url == 'https://example.com'
    
    @pytest.mark.asyncio
    async def test_timing_metrics(self, sample_html):
        """Test timing metrics are captured"""
        with patch('src.analyzers.dynamic_analyzer.async_playwright') as mock_pw_factory:
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock(return_value=Mock(status=200))
            mock_page.wait_for_load_state = AsyncMock()
            mock_page.content = AsyncMock(return_value=sample_html)
            mock_page.close = AsyncMock()
            mock_page.set_default_timeout = Mock()
            mock_page.on = Mock()
            
            mock_context = AsyncMock()
            mock_context.new_page = AsyncMock(return_value=mock_page)
            mock_context.close = AsyncMock()
            mock_page.context = mock_context
            
            mock_browser = AsyncMock()
            mock_browser.new_context = AsyncMock(return_value=mock_context)
            mock_browser.close = AsyncMock()
            
            mock_playwright = AsyncMock()
            mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_playwright.stop = AsyncMock()
            
            mock_pw_factory.return_value.start = AsyncMock(return_value=mock_playwright)
            
            analyzer = DynamicAnalyzer()
            result = await analyzer.analyze_async('https://example.com')
            
            assert result.analysis_duration_seconds is not None
            assert result.analysis_duration_seconds > 0
            assert result.page_load_time_seconds is not None
            assert result.page_load_time_seconds >= 0
