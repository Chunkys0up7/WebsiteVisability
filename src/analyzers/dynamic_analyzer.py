"""
Dynamic Analyzer Module

Analyzes HTML content using headless browser (Playwright) for JavaScript execution.
Simulates what modern browsers and sophisticated crawlers can access.
"""

import logging
import time
import asyncio
import platform
from typing import Optional
from datetime import datetime

# Check if we're on Windows Store Python and handle Playwright accordingly
try:
    from playwright.async_api import async_playwright, Browser, Page, Error as PlaywrightError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    async_playwright = None
    Browser = None
    Page = None
    PlaywrightError = Exception

from ..parsers.html_parser import HTMLParser
from ..parsers.meta_parser import MetaParser
from ..parsers.structured_data_parser import StructuredDataParser
from ..parsers.javascript_parser import JavaScriptParser
from ..models.analysis_result import AnalysisResult
from ..utils.validators import validate_url
from ..utils.helpers import format_bytes
from config.settings import get_settings

logger = logging.getLogger(__name__)


class DynamicAnalyzer:
    """
    Analyze web pages using headless browser with JavaScript execution.
    
    This analyzer uses Playwright to render pages like a real browser,
    executing JavaScript and capturing dynamically loaded content.
    """
    
    def __init__(
        self,
        timeout: Optional[int] = None,
        user_agent: Optional[str] = None,
        headless: bool = True
    ):
        """
        Initialize dynamic analyzer.
        
        Args:
            timeout: Page load timeout in seconds (default from settings)
            user_agent: Custom user agent string (default from settings)
            headless: Run browser in headless mode (default True)
        """
        self.settings = get_settings()
        self.timeout = (timeout or self.settings.default_timeout) * 1000  # Convert to ms
        self.user_agent = user_agent or self.settings.user_agent
        self.headless = headless
        
        self._browser: Optional[Browser] = None
        self._playwright = None
        
        # Check for Windows Store Python compatibility
        self._is_windows_store_python = self._check_windows_store_python()
        if self._is_windows_store_python:
            logger.warning("Windows Store Python detected. Dynamic analysis may not work due to asyncio limitations.")
    
    def _check_windows_store_python(self) -> bool:
        """Check if running on Windows Store Python with asyncio limitations."""
        if platform.system() != "Windows":
            return False
        
        # Check for Windows Store Python path patterns
        import sys
        python_path = sys.executable.lower()
        return "windowsapps" in python_path or "microsoft" in python_path
    
    async def _init_browser(self):
        """Initialize Playwright browser."""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright is not available. Please install it with: pip install playwright && playwright install")
        
        if self._is_windows_store_python:
            raise NotImplementedError("Dynamic analysis is not supported on Windows Store Python due to asyncio limitations. Please use regular Python installation.")
        
        if self._browser is None:
            logger.info("Initializing Playwright browser...")
            try:
                self._playwright = await async_playwright().start()
                self._browser = await self._playwright.chromium.launch(
                    headless=self.headless,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ]
                )
            except NotImplementedError as e:
                logger.error(f"Playwright initialization failed due to Windows Store Python: {e}")
                raise NotImplementedError("Dynamic analysis is not supported on Windows Store Python due to asyncio limitations. Please use regular Python installation.")
            logger.info("Browser initialized successfully")
    
    async def _close_browser(self):
        """Close Playwright browser."""
        if self._browser:
            logger.info("Closing browser...")
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
    
    async def _create_page(self) -> Page:
        """
        Create a new browser page with custom settings.
        
        Returns:
            Configured Page instance
        """
        await self._init_browser()
        
        context = await self._browser.new_context(
            user_agent=self.user_agent,
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/New_York'
        )
        
        page = await context.new_page()
        
        # Set default timeout
        page.set_default_timeout(self.timeout)
        
        return page
    
    async def fetch_rendered_html(self, url: str) -> tuple[str, int, float, list[str]]:
        """
        Fetch and render HTML content from URL.
        
        Args:
            url: URL to fetch
            
        Returns:
            Tuple of (html_content, status_code, response_time, ajax_requests)
            
        Raises:
            PlaywrightError: If page navigation fails
        """
        logger.info(f"Rendering URL with browser: {url}")
        
        page = await self._create_page()
        ajax_requests = []
        
        # Track AJAX requests
        async def handle_request(request):
            if request.resource_type in ['xhr', 'fetch']:
                ajax_requests.append(request.url)
        
        page.on('request', handle_request)
        
        try:
            start_time = time.time()
            
            # Navigate to page
            response = await page.goto(url, wait_until='networkidle')
            
            # Wait for page to be fully loaded
            await page.wait_for_load_state('networkidle')
            
            response_time = time.time() - start_time
            
            # Get rendered HTML
            html_content = await page.content()
            
            # Get status code
            status_code = response.status if response else 0
            
            logger.info(
                f"Successfully rendered {url}: "
                f"Status={status_code}, "
                f"Size={format_bytes(len(html_content.encode('utf-8')))}, "
                f"Time={response_time:.2f}s, "
                f"AJAX={len(ajax_requests)}"
            )
            
            return html_content, status_code, response_time, ajax_requests
            
        except PlaywrightError as e:
            logger.error(f"Playwright error rendering {url}: {e}")
            raise
        finally:
            await page.close()
            await page.context.close()
    
    async def analyze_async(self, url: str) -> AnalysisResult:
        """
        Perform complete dynamic analysis of a URL (async).
        
        Args:
            url: URL to analyze
            
        Returns:
            AnalysisResult with all analysis data
        """
        logger.info(f"Starting dynamic analysis of: {url}")
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
            # Fetch and render HTML
            html_content, status_code, response_time, ajax_requests = await self.fetch_rendered_html(
                normalized_url
            )
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
            logger.info("Parsing rendered HTML structure...")
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
            
            # Note: AJAX requests are tracked separately in ajax_requests list
            # The js_analysis.has_ajax field indicates static AJAX code detection
            
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
                crawler_analysis=None,
                content_comparison=None,
                analysis_duration_seconds=analysis_duration,
                page_load_time_seconds=response_time,
                page_size_bytes=page_size
            )
            
            logger.info(
                f"Dynamic analysis complete in {analysis_duration:.2f}s: "
                f"{content_analysis.word_count} words, "
                f"{len(structure_analysis.semantic_elements)} semantic elements, "
                f"{js_analysis.total_scripts} scripts, "
                f"{len(ajax_requests)} AJAX requests"
            )
            
            return result
            
        except PlaywrightError as e:
            error_msg = str(e)
            if 'Timeout' in error_msg or 'timeout' in error_msg:
                return AnalysisResult(
                    url=normalized_url,
                    analyzed_at=datetime.now(),
                    status='error',
                    error_message=f"Page load timeout after {self.timeout/1000} seconds"
                )
            return AnalysisResult(
                url=normalized_url,
                analyzed_at=datetime.now(),
                status='error',
                error_message=f"Browser error: {error_msg}"
            )
        except Exception as e:
            logger.error(f"Unexpected error during dynamic analysis: {e}", exc_info=True)
            return AnalysisResult(
                url=normalized_url,
                analyzed_at=datetime.now(),
                status='error',
                error_message=f"Analysis failed: {str(e)}"
            )
        finally:
            # Ensure browser is closed
            await self._close_browser()
    
    def analyze(self, url: str) -> AnalysisResult:
        """
        Perform complete dynamic analysis of a URL (synchronous wrapper).
        
        Args:
            url: URL to analyze
            
        Returns:
            AnalysisResult with all analysis data
        """
        # Create or get event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run async analysis
        return loop.run_until_complete(self.analyze_async(url))
    
    async def close(self):
        """Close the browser (async)."""
        await self._close_browser()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

