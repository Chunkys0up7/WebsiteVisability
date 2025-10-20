"""
Static Analyzer Module

Analyzes HTML content using static parsing (no JavaScript execution).
Simulates what basic web scrapers can extract.
"""

import logging
import time
from typing import Optional
from datetime import datetime
import requests

from ..parsers.html_parser import HTMLParser
from ..parsers.meta_parser import MetaParser
from ..parsers.structured_data_parser import StructuredDataParser
from ..parsers.javascript_parser import JavaScriptParser
from ..models.analysis_result import AnalysisResult
from ..utils.validators import validate_url
from ..utils.helpers import format_bytes
from config.settings import get_settings

logger = logging.getLogger(__name__)


class StaticAnalyzer:
    """
    Analyze web pages using static HTML parsing.
    
    This analyzer fetches HTML using HTTP requests and parses it with
    BeautifulSoup. It simulates what basic web scrapers can access
    without JavaScript execution.
    """
    
    def __init__(self, timeout: Optional[int] = None, user_agent: Optional[str] = None):
        """
        Initialize static analyzer.
        
        Args:
            timeout: Request timeout in seconds (default from settings)
            user_agent: Custom user agent string (default from settings)
        """
        self.settings = get_settings()
        self.timeout = timeout or self.settings.default_timeout
        self.user_agent = user_agent or self.settings.user_agent
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def fetch_html(self, url: str) -> tuple[str, int, float]:
        """
        Fetch HTML content from URL.
        
        Args:
            url: URL to fetch
            
        Returns:
            Tuple of (html_content, status_code, response_time)
            
        Raises:
            requests.RequestException: If request fails
        """
        logger.info(f"Fetching URL: {url}")
        
        start_time = time.time()
        
        try:
            response = self.session.get(
                url,
                timeout=self.timeout,
                allow_redirects=True
            )
            
            response_time = time.time() - start_time
            
            # Raise for bad status codes
            response.raise_for_status()
            
            # Get content
            html_content = response.text
            
            logger.info(
                f"Successfully fetched {url}: "
                f"Status={response.status_code}, "
                f"Size={format_bytes(len(html_content.encode('utf-8')))}, "
                f"Time={response_time:.2f}s"
            )
            
            return html_content, response.status_code, response_time
            
        except requests.Timeout:
            logger.error(f"Timeout fetching {url} after {self.timeout}s")
            raise
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            raise
    
    def analyze(self, url: str) -> AnalysisResult:
        """
        Perform complete static analysis of a URL.
        
        Args:
            url: URL to analyze
            
        Returns:
            AnalysisResult with all analysis data
        """
        logger.info(f"Starting static analysis of: {url}")
        analysis_start = time.time()
        
        # Validate URL
        is_valid, normalized_url, error = validate_url(url)
        if not is_valid:
            logger.error(f"Invalid URL: {error}")
            return AnalysisResult(
                url=url,
                analyzed_at=datetime.now(),
                status='error',
                error_message=f"Invalid URL: {error}"
            )
        
        try:
            # Fetch HTML
            html_content, status_code, response_time = self.fetch_html(normalized_url)
            page_size = len(html_content.encode('utf-8'))
            
            # Check page size limit
            max_size_bytes = self.settings.max_page_size_mb * 1024 * 1024
            if page_size > max_size_bytes:
                logger.warning(
                    f"Page size ({format_bytes(page_size)}) exceeds limit "
                    f"({format_bytes(max_size_bytes)})"
                )
                return AnalysisResult(
                    url=normalized_url,
                    analyzed_at=datetime.now(),
                    status='error',
                    error_message=f"Page size exceeds {self.settings.max_page_size_mb}MB limit"
                )
            
            # Parse HTML
            logger.info("Parsing HTML structure...")
            html_parser = HTMLParser(html_content)
            content_analysis, structure_analysis, hidden_content = html_parser.analyze()
            
            # Parse meta tags
            logger.info("Parsing meta tags...")
            meta_parser = MetaParser(html_content)
            meta_analysis = meta_parser.analyze()
            
            # Parse structured data
            logger.info("Parsing structured data...")
            structured_parser = StructuredDataParser(html_content)
            structured_result = structured_parser.analyze()
            
            # Update meta analysis with structured data
            meta_analysis.structured_data = structured_result['structured_data']
            meta_analysis.has_json_ld = structured_result['has_json_ld']
            meta_analysis.has_microdata = structured_result['has_microdata']
            meta_analysis.has_rdfa = structured_result['has_rdfa']
            
            # Parse JavaScript
            logger.info("Analyzing JavaScript usage...")
            js_parser = JavaScriptParser(html_content)
            js_analysis = js_parser.analyze()
            
            # Calculate analysis duration
            analysis_duration = time.time() - analysis_start
            
            # Create result
            result = AnalysisResult(
                url=normalized_url,
                analyzed_at=datetime.now(),
                status='success',
                content_analysis=content_analysis,
                structure_analysis=structure_analysis,
                hidden_content=hidden_content,
                meta_analysis=meta_analysis,
                javascript_analysis=js_analysis,
                crawler_analysis=None,  # Will be added by crawler analyzer if needed
                content_comparison=None,  # Will be added by comparator if dynamic analysis done
                analysis_duration_seconds=analysis_duration,
                page_load_time_seconds=response_time,
                page_size_bytes=page_size
            )
            
            logger.info(
                f"Static analysis complete in {analysis_duration:.2f}s: "
                f"{content_analysis.word_count} words, "
                f"{len(structure_analysis.semantic_elements)} semantic elements, "
                f"{js_analysis.total_scripts} scripts"
            )
            
            return result
            
        except requests.Timeout:
            return AnalysisResult(
                url=normalized_url,
                analyzed_at=datetime.now(),
                status='error',
                error_message=f"Request timeout after {self.timeout} seconds"
            )
        except requests.RequestException as e:
            return AnalysisResult(
                url=normalized_url,
                analyzed_at=datetime.now(),
                status='error',
                error_message=f"Request failed: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error during analysis: {e}", exc_info=True)
            return AnalysisResult(
                url=normalized_url,
                analyzed_at=datetime.now(),
                status='error',
                error_message=f"Analysis failed: {str(e)}"
            )
    
    def close(self):
        """Close the requests session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

