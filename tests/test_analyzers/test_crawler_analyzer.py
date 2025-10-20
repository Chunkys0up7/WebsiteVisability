"""
Unit tests for CrawlerAnalyzer
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.analyzers.crawler_analyzer import CrawlerAnalyzer, RobotsTxtParser


class TestRobotsTxtParser:
    """Test suite for RobotsTxtParser"""
    
    @pytest.fixture
    def simple_robots(self):
        """Simple robots.txt content"""
        return """
User-agent: *
Disallow: /admin/
Disallow: /private/
Allow: /public/
Sitemap: https://example.com/sitemap.xml
"""
    
    @pytest.fixture
    def complex_robots(self):
        """Complex robots.txt with multiple agents"""
        return """
User-agent: Googlebot
Disallow: /nogoogle/
Crawl-delay: 10

User-agent: Bingbot
Disallow: /nobing/
Allow: /public/

User-agent: *
Disallow: /admin/
Sitemap: https://example.com/sitemap.xml
Sitemap: https://example.com/sitemap-news.xml
"""
    
    def test_parser_initialization(self, simple_robots):
        """Test parser initializes correctly"""
        parser = RobotsTxtParser(simple_robots)
        assert parser.content == simple_robots
        assert isinstance(parser.rules, dict)
    
    def test_parse_simple_robots(self, simple_robots):
        """Test parsing simple robots.txt"""
        parser = RobotsTxtParser(simple_robots)
        
        assert '*' in parser.rules
        rules = parser.rules['*']
        
        # Check disallow rules
        disallows = [r for r in rules if r['directive'] == 'disallow']
        assert len(disallows) == 2
        assert any(r['value'] == '/admin/' for r in disallows)
        assert any(r['value'] == '/private/' for r in disallows)
    
    def test_parse_complex_robots(self, complex_robots):
        """Test parsing complex robots.txt with multiple agents"""
        parser = RobotsTxtParser(complex_robots)
        
        assert 'Googlebot' in parser.rules
        assert 'Bingbot' in parser.rules
        assert '*' in parser.rules
    
    def test_is_allowed_path(self, simple_robots):
        """Test checking if path is allowed"""
        parser = RobotsTxtParser(simple_robots)
        
        assert parser.is_allowed('/home') is True
        assert parser.is_allowed('/admin/') is False
        assert parser.is_allowed('/admin/users') is False
        assert parser.is_allowed('/public/page') is True
    
    def test_is_allowed_default(self):
        """Test default behavior when no robots.txt"""
        parser = RobotsTxtParser("")
        assert parser.is_allowed('/any/path') is True
    
    def test_get_crawl_delay(self, complex_robots):
        """Test extracting crawl delay"""
        parser = RobotsTxtParser(complex_robots)
        
        delay = parser.get_crawl_delay('Googlebot')
        assert delay == 10.0
        
        delay = parser.get_crawl_delay('*')
        assert delay is None
    
    def test_get_sitemaps(self, complex_robots):
        """Test extracting sitemap URLs"""
        parser = RobotsTxtParser(complex_robots)
        
        sitemaps = parser.get_sitemaps()
        assert len(sitemaps) == 2
        assert 'https://example.com/sitemap.xml' in sitemaps
        assert 'https://example.com/sitemap-news.xml' in sitemaps
    
    def test_parse_with_comments(self):
        """Test parsing robots.txt with comments"""
        robots = """
# This is a comment
User-agent: *
Disallow: /admin/  # Inline comment
# Another comment
"""
        parser = RobotsTxtParser(robots)
        assert '*' in parser.rules
        
        rules = parser.rules['*']
        disallows = [r for r in rules if r['directive'] == 'disallow']
        assert len(disallows) == 1
        assert disallows[0]['value'] == '/admin/'
    
    def test_parse_empty_robots(self):
        """Test parsing empty robots.txt"""
        parser = RobotsTxtParser("")
        assert len(parser.rules) == 0
    
    def test_parse_malformed_lines(self):
        """Test handling malformed lines"""
        robots = """
User-agent: *
InvalidLine
Disallow /no-colon
Disallow: /valid/
"""
        parser = RobotsTxtParser(robots)
        
        rules = parser.rules.get('*', [])
        disallows = [r for r in rules if r['directive'] == 'disallow']
        # Should only get the valid disallow
        assert len(disallows) == 1
        assert disallows[0]['value'] == '/valid/'


class TestCrawlerAnalyzer:
    """Test suite for CrawlerAnalyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance"""
        return CrawlerAnalyzer(timeout=10)
    
    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initializes correctly"""
        assert analyzer.timeout == 10
        assert analyzer.session is not None
        assert 'User-Agent' in analyzer.session.headers
    
    @patch('src.analyzers.crawler_analyzer.requests.Session.get')
    def test_fetch_robots_txt_success(self, mock_get, analyzer):
        """Test successful robots.txt fetch"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "User-agent: *\nDisallow: /admin/"
        mock_get.return_value = mock_response
        
        content = analyzer.fetch_robots_txt("https://example.com")
        
        assert content is not None
        assert "User-agent: *" in content
        mock_get.assert_called_once()
    
    @patch('src.analyzers.crawler_analyzer.requests.Session.get')
    def test_fetch_robots_txt_not_found(self, mock_get, analyzer):
        """Test robots.txt not found"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        content = analyzer.fetch_robots_txt("https://example.com")
        
        assert content is None
    
    @patch('src.analyzers.crawler_analyzer.requests.Session.get')
    def test_fetch_robots_txt_error(self, mock_get, analyzer):
        """Test robots.txt fetch error"""
        import requests
        mock_get.side_effect = requests.RequestException("Network error")
        
        content = analyzer.fetch_robots_txt("https://example.com")
        
        assert content is None
    
    @patch('src.analyzers.crawler_analyzer.requests.Session.get')
    def test_fetch_llms_txt_success(self, mock_get, analyzer):
        """Test successful llms.txt fetch"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "# LLM directives\nAllow: /api/llm"
        mock_get.return_value = mock_response
        
        content = analyzer.fetch_llms_txt("https://example.com")
        
        assert content is not None
        assert "LLM directives" in content
    
    @patch('src.analyzers.crawler_analyzer.requests.Session.get')
    def test_fetch_llms_txt_not_found(self, mock_get, analyzer):
        """Test llms.txt not found"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        content = analyzer.fetch_llms_txt("https://example.com")
        
        assert content is None
    
    @patch('src.analyzers.crawler_analyzer.requests.Session.get')
    def test_fetch_sitemap_success(self, mock_get, analyzer):
        """Test successful sitemap fetch"""
        sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/page1</loc>
    <lastmod>2024-01-01</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://example.com/page2</loc>
  </url>
</urlset>"""
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = sitemap_xml.encode('utf-8')
        mock_get.return_value = mock_response
        
        sitemap = analyzer.fetch_sitemap("https://example.com/sitemap.xml")
        
        assert sitemap is not None
        assert sitemap['url_count'] == 2
        assert len(sitemap['urls']) == 2
        assert sitemap['urls'][0]['loc'] == 'https://example.com/page1'
        assert sitemap['urls'][0]['lastmod'] == '2024-01-01'
    
    @patch('src.analyzers.crawler_analyzer.requests.Session.get')
    def test_fetch_sitemap_malformed(self, mock_get, analyzer):
        """Test malformed sitemap XML"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"Not valid XML"
        mock_get.return_value = mock_response
        
        sitemap = analyzer.fetch_sitemap("https://example.com/sitemap.xml")
        
        assert sitemap is None
    
    @patch('src.analyzers.crawler_analyzer.requests.Session.get')
    def test_analyze_with_robots(self, mock_get, analyzer):
        """Test complete analysis with robots.txt"""
        def side_effect(url, **kwargs):
            mock_resp = Mock()
            if 'robots.txt' in url:
                mock_resp.status_code = 200
                mock_resp.text = "User-agent: *\nDisallow: /admin/\nSitemap: https://example.com/sitemap.xml"
            elif 'llms.txt' in url:
                mock_resp.status_code = 404
            elif 'sitemap.xml' in url:
                mock_resp.status_code = 200
                mock_resp.content = b"""<?xml version="1.0"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://example.com/page1</loc></url>
</urlset>"""
            else:
                mock_resp.status_code = 404
            return mock_resp
        
        mock_get.side_effect = side_effect
        
        result = analyzer.analyze("https://example.com")
        
        assert result['has_robots_txt'] is True
        assert result['has_llms_txt'] is False
        assert result['is_crawlable'] is True
        assert len(result['sitemaps']) > 0
        assert len(result['disallowed_paths']) > 0
    
    @patch('src.analyzers.crawler_analyzer.requests.Session.get')
    def test_analyze_without_robots(self, mock_get, analyzer):
        """Test analysis without robots.txt"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = analyzer.analyze("https://example.com")
        
        assert result['has_robots_txt'] is False
        assert result['has_llms_txt'] is False
        assert result['is_crawlable'] is True  # Default to crawlable
        assert len(result['sitemaps']) == 0
    
    @patch('src.analyzers.crawler_analyzer.requests.Session.get')
    def test_analyze_with_llms_txt(self, mock_get, analyzer):
        """Test analysis with llms.txt"""
        def side_effect(url, **kwargs):
            mock_resp = Mock()
            if 'robots.txt' in url:
                mock_resp.status_code = 404
            elif 'llms.txt' in url:
                mock_resp.status_code = 200
                mock_resp.text = "# LLM configuration"
            else:
                mock_resp.status_code = 404
            return mock_resp
        
        mock_get.side_effect = side_effect
        
        result = analyzer.analyze("https://example.com")
        
        assert result['has_llms_txt'] is True
        assert result['llms_txt_content'] is not None
    
    def test_analyze_invalid_url(self, analyzer):
        """Test analysis with invalid URL"""
        result = analyzer.analyze("not-a-url")
        
        assert 'error' in result
        assert result['has_robots_txt'] is False
    
    def test_context_manager(self):
        """Test context manager usage"""
        with CrawlerAnalyzer() as analyzer:
            assert analyzer.session is not None
        
        # Session should be closed after context
        # (we can't easily test this without implementation details)
    
    def test_close_session(self, analyzer):
        """Test closing session"""
        analyzer.close()
        # Session close should succeed without error
    
    @patch('src.analyzers.crawler_analyzer.requests.Session.get')
    def test_analyze_disallowed_path(self, mock_get, analyzer):
        """Test analysis when path is disallowed"""
        def side_effect(url, **kwargs):
            mock_resp = Mock()
            if 'robots.txt' in url:
                mock_resp.status_code = 200
                mock_resp.text = "User-agent: *\nDisallow: /admin/"
            else:
                mock_resp.status_code = 404
            return mock_resp
        
        mock_get.side_effect = side_effect
        
        result = analyzer.analyze("https://example.com/admin/panel")
        
        assert result['has_robots_txt'] is True
        assert result['is_crawlable'] is False
    
    @patch('src.analyzers.crawler_analyzer.requests.Session.get')
    def test_analyze_with_crawl_delay(self, mock_get, analyzer):
        """Test analysis with crawl delay"""
        def side_effect(url, **kwargs):
            mock_resp = Mock()
            if 'robots.txt' in url:
                mock_resp.status_code = 200
                mock_resp.text = "User-agent: *\nCrawl-delay: 5"
            else:
                mock_resp.status_code = 404
            return mock_resp
        
        mock_get.side_effect = side_effect
        
        result = analyzer.analyze("https://example.com")
        
        assert result['crawl_delay'] == 5.0
    
    @patch('src.analyzers.crawler_analyzer.requests.Session.get')
    def test_analyze_multiple_sitemaps(self, mock_get, analyzer):
        """Test analysis with multiple sitemaps"""
        def side_effect(url, **kwargs):
            mock_resp = Mock()
            if 'robots.txt' in url:
                mock_resp.status_code = 200
                mock_resp.text = """User-agent: *
Sitemap: https://example.com/sitemap1.xml
Sitemap: https://example.com/sitemap2.xml
Sitemap: https://example.com/sitemap3.xml"""
            elif 'sitemap' in url:
                mock_resp.status_code = 200
                mock_resp.content = b"""<?xml version="1.0"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://example.com/</loc></url>
</urlset>"""
            else:
                mock_resp.status_code = 404
            return mock_resp
        
        mock_get.side_effect = side_effect
        
        result = analyzer.analyze("https://example.com")
        
        assert len(result['sitemaps']) == 3
    
    @patch('src.analyzers.crawler_analyzer.requests.Session.get')
    def test_analyze_default_sitemap(self, mock_get, analyzer):
        """Test finding default sitemap.xml"""
        def side_effect(url, **kwargs):
            mock_resp = Mock()
            if 'robots.txt' in url:
                mock_resp.status_code = 404
            elif 'sitemap.xml' in url:
                mock_resp.status_code = 200
                mock_resp.content = b"""<?xml version="1.0"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://example.com/</loc></url>
</urlset>"""
            else:
                mock_resp.status_code = 404
            return mock_resp
        
        mock_get.side_effect = side_effect
        
        result = analyzer.analyze("https://example.com")
        
        assert result['has_sitemap'] is True
        assert len(result['sitemap_data']) > 0

