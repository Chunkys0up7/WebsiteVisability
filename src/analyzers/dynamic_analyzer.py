"""
Dynamic Website Analyzer

Analyzes websites using a headless browser to capture dynamically rendered content.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import platform
import sys

from playwright.async_api import async_playwright, Browser, Page
from ..models.analysis_result import AnalysisResult, AnalysisStatus

logger = logging.getLogger(__name__)


class DynamicAnalyzer:
    """
    Analyzes websites using Playwright for dynamic content.
    
    Handles cases where dynamic analysis is not supported (e.g., Windows Store Python).
    """
    
    def __init__(self, timeout: int = 30, headless: bool = True):
        """Initialize the dynamic analyzer."""
        self.timeout = timeout
        self.headless = headless
        self.logger = logging.getLogger(__name__)
        self._playwright = None
        self._browser = None
        self._context = None
        self._is_supported = self._check_dynamic_support()
    
    def _check_dynamic_support(self) -> bool:
        """Check if dynamic analysis is supported on this platform."""
        # Windows Store Python doesn't support asyncio subprocess
        if sys.platform == "win32" and "WindowsApps" in sys.executable:
            return False
        return True
    
    def analyze(self, url: str) -> AnalysisResult:
        """
        Analyze a website using dynamic analysis.
        
        Args:
            url: URL to analyze
            
        Returns:
            Analysis results including dynamic content
        """
        if not self._is_supported:
            self.logger.warning("Dynamic analysis is not supported on this platform")
            return AnalysisResult(
                url=url,
                status=AnalysisStatus.SKIPPED,
                error_message="Dynamic analysis is not supported on this platform. "
                            "For full analysis, please use regular Python installation.",
                content_analysis={
                    'word_count': 0,
                    'text_content': '',
                    'character_count': 0,
                    'estimated_tokens': 0,
                    'paragraphs': 0,
                    'links': 0,
                    'images': 0,
                    'tables': 0,
                    'lists': 0,
                    'hidden_content': []
                },
                structure_analysis={
                    'semantic_elements': [],
                    'has_semantic_html': False,
                    'heading_hierarchy': {
                        'h1': [], 'h2': [], 'h3': [],
                        'h4': [], 'h5': [], 'h6': []
                    },
                    'total_elements': 0,
                    'nested_depth': 0,
                    'has_proper_structure': False,
                    'navigation_elements': []
                },
                meta_analysis={
                    'title': None,
                    'description': None,
                    'keywords': None,
                    'meta_tags': [],
                    'open_graph_tags': {},
                    'twitter_card_tags': {},
                    'structured_data': [],
                    'has_json_ld': False,
                    'has_microdata': False,
                    'has_rdfa': False
                },
                javascript_analysis={
                    'total_scripts': 0,
                    'inline_scripts': 0,
                    'external_scripts': 0,
                    'frameworks': [],
                    'is_spa': False,
                    'has_ajax': False,
                    'dynamic_content_detected': False,
                    'ajax_requests': []
                },
                ssr_detection={
                    'is_ssr': None,
                    'confidence': 0.0,
                    'evidence': ["Dynamic analysis not supported - cannot detect SSR"]
                }
            )
        
        try:
            return asyncio.run(self.analyze_async(url))
        except Exception as e:
            self.logger.error(f"Dynamic analysis failed: {e}")
            return AnalysisResult(
                url=url,
                status=AnalysisStatus.ERROR,
                error_message=str(e),
                content_analysis={
                    'word_count': 0,
                    'text_content': '',
                    'character_count': 0,
                    'estimated_tokens': 0,
                    'paragraphs': 0,
                    'links': 0,
                    'images': 0,
                    'tables': 0,
                    'lists': 0,
                    'hidden_content': []
                },
                structure_analysis={
                    'semantic_elements': [],
                    'has_semantic_html': False,
                    'heading_hierarchy': {
                        'h1': [], 'h2': [], 'h3': [],
                        'h4': [], 'h5': [], 'h6': []
                    },
                    'total_elements': 0,
                    'nested_depth': 0,
                    'has_proper_structure': False,
                    'navigation_elements': []
                },
                meta_analysis={
                    'title': None,
                    'description': None,
                    'keywords': None,
                    'meta_tags': [],
                    'open_graph_tags': {},
                    'twitter_card_tags': {},
                    'structured_data': [],
                    'has_json_ld': False,
                    'has_microdata': False,
                    'has_rdfa': False
                },
                javascript_analysis={
                    'total_scripts': 0,
                    'inline_scripts': 0,
                    'external_scripts': 0,
                    'frameworks': [],
                    'is_spa': False,
                    'has_ajax': False,
                    'dynamic_content_detected': False,
                    'ajax_requests': []
                },
                ssr_detection={
                    'is_ssr': None,
                    'confidence': 0.0,
                    'evidence': ["Dynamic analysis failed - cannot detect SSR"]
                }
            )
    
    async def analyze_async(self, url: str) -> AnalysisResult:
        """Asynchronously analyze a website."""
        self.logger.info(f"Starting dynamic analysis of: {url}")
        self.logger.info(f"Rendering URL with browser: {url}")
        
        try:
            # Get rendered HTML
            html_content, status_code, response_time, ajax_requests = await self.fetch_rendered_html(
                url, self.timeout
            )
            
            # Parse content
            content_analysis = self._analyze_content(html_content)
            structure_analysis = self._analyze_structure(html_content)
            meta_analysis = self._analyze_meta(html_content)
            javascript_analysis = self._analyze_javascript(html_content, ajax_requests)
            ssr_detection = self._detect_ssr(html_content, response_time)
            
            return AnalysisResult(
                status="success",
                error_message=None,
                content_analysis=content_analysis,
                structure_analysis=structure_analysis,
                meta_analysis=meta_analysis,
                javascript_analysis=javascript_analysis,
                ssr_detection=ssr_detection
            )
            
        except Exception as e:
            self.logger.error(f"Unexpected error during dynamic analysis: {e}")
            raise
        
        finally:
            await self._cleanup()
    
    async def fetch_rendered_html(
        self, url: str, timeout: int
    ) -> Tuple[str, int, float, List[Dict[str, Any]]]:
        """Fetch rendered HTML using Playwright."""
        page = await self._create_page()
        
        try:
            # Navigate and wait for network idle
            response = await page.goto(url, wait_until='networkidle', timeout=timeout * 1000)
            if not response:
                raise Exception(f"Failed to load {url}")
            
            # Wait for any remaining dynamic content
            await page.wait_for_timeout(1000)  # 1s grace period
            
            # Get final HTML and timing
            html = await page.content()
            status = response.status
            timing = response.request.timing
            response_time = timing['responseEnd'] - timing['requestStart'] if timing else 0
            
            # Get AJAX requests
            ajax_requests = await self._get_ajax_requests(page)
            
            return html, status, response_time, ajax_requests
            
        finally:
            await page.close()
    
    async def _create_page(self) -> Page:
        """Create a new browser page."""
        if not self._browser:
            await self._init_browser()
        return await self._context.new_page()
    
    async def _init_browser(self):
        """Initialize the browser."""
        if not self._is_supported:
            raise NotImplementedError(
                "Dynamic analysis is not supported on Windows Store Python due to "
                "asyncio limitations. Please use regular Python installation."
            )
        
        self.logger.info("Initializing Playwright browser...")
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.headless)
        self._context = await self._browser.new_context()
    
    async def _cleanup(self):
        """Clean up browser resources."""
        if self._context:
            await self._context.close()
            self._context = None
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
    
    async def _get_ajax_requests(self, page: Page) -> List[Dict[str, Any]]:
        """Get AJAX requests made during page load."""
        requests = []
        async with page.expect_request("**/*") as request_info:
            request = await request_info.value
            if request.resource_type in ['xhr', 'fetch']:
                requests.append({
                    'url': request.url,
                    'method': request.method,
                    'type': request.resource_type
                })
        return requests
    
    def _analyze_content(self, html: str) -> Dict[str, Any]:
        """Analyze rendered content."""
        # Implement content analysis
        return {
            'word_count': len(html.split()),
            'text_content': html,
            'links': 0,  # TODO: Implement
            'images': 0,
            'tables': 0,
            'lists': 0,
            'hidden_content': []
        }
    
    def _analyze_structure(self, html: str) -> Dict[str, Any]:
        """Analyze HTML structure."""
        return {
            'semantic_elements': [],  # TODO: Implement
            'heading_structure': [],
            'navigation_elements': []
        }
    
    def _analyze_meta(self, html: str) -> Dict[str, Any]:
        """Analyze meta information."""
        return {
            'title': None,  # TODO: Implement
            'description': None,
            'keywords': None,
            'open_graph_tags': [],
            'twitter_card_tags': [],
            'structured_data': {}
        }
    
    def _analyze_javascript(
        self, html: str, ajax_requests: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze JavaScript usage."""
        return {
            'total_scripts': 0,  # TODO: Implement
            'frameworks': [],
            'is_spa': False,
            'dynamic_content_detected': bool(ajax_requests),
            'ajax_requests': ajax_requests
        }
    
    def _detect_ssr(self, html: str, response_time: float) -> Dict[str, Any]:
        """Detect server-side rendering."""
        # If dynamic analysis is not supported, we can't reliably detect SSR
        if not self._is_supported:
            return {
                'is_ssr': None,
                'confidence': 0.0,
                'evidence': ["Dynamic analysis not supported - cannot detect SSR"]
            }

        # Simple heuristic: fast response + complete HTML = likely SSR
        is_ssr = response_time < 0.5 and len(html) > 1000
        confidence = 0.8 if is_ssr else 0.2
        
        return {
            'is_ssr': is_ssr,
            'confidence': confidence,
            'evidence': [
                f"Response time: {response_time:.2f}s",
                f"Initial HTML size: {len(html)} bytes",
                "Based on response time and initial HTML size"
            ]
        }