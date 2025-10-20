"""
Web Crawler Analysis Module

Analyzes how different types of web crawlers (Google, Bing, LLMs, etc.)
would perceive and access website content.
"""

import logging
import requests
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


@dataclass
class CrawlerCapability:
    """Defines what a crawler can and cannot do"""
    name: str
    can_execute_js: bool
    can_process_images: bool
    can_access_css: bool
    can_follow_redirects: bool
    can_handle_ajax: bool
    user_agent: str
    limitations: List[str]


@dataclass
class CrawlerAnalysisResult:
    """Results from crawler analysis"""
    crawler_name: str
    accessibility_score: float
    content_accessible: Dict[str, Any]
    content_inaccessible: Dict[str, Any]
    evidence: List[str]
    recommendations: List[str]


class WebCrawlerAnalyzer:
    """
    Analyzes how different web crawlers would access and process website content.
    
    Simulates different crawler behaviors and identifies content accessibility
    issues for specific crawler types.
    """
    
    def __init__(self):
        """Initialize the web crawler analyzer."""
        self.logger = logging.getLogger(__name__)
        
        # Define crawler capabilities
        self.crawler_capabilities = {
            'googlebot': CrawlerCapability(
                name='Googlebot',
                can_execute_js=True,
                can_process_images=True,
                can_access_css=True,
                can_follow_redirects=True,
                can_handle_ajax=True,
                user_agent='Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                limitations=['Limited JavaScript execution', 'May not execute all JS frameworks']
            ),
            'bingbot': CrawlerCapability(
                name='Bingbot',
                can_execute_js=True,
                can_process_images=True,
                can_access_css=True,
                can_follow_redirects=True,
                can_handle_ajax=True,
                user_agent='Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)',
                limitations=['JavaScript execution limitations', 'May not support all modern JS features']
            ),
            'llm': CrawlerCapability(
                name='LLM (GPT/Claude)',
                can_execute_js=False,
                can_process_images=False,
                can_access_css=False,
                can_follow_redirects=True,
                can_handle_ajax=False,
                user_agent='Mozilla/5.0 (compatible; LLM-Crawler/1.0)',
                limitations=['Cannot execute JavaScript', 'Cannot process images', 'Cannot access CSS', 'Cannot handle AJAX']
            ),
            'basic_scraper': CrawlerCapability(
                name='Basic Web Scraper',
                can_execute_js=False,
                can_process_images=False,
                can_access_css=False,
                can_follow_redirects=True,
                can_handle_ajax=False,
                user_agent='Mozilla/5.0 (compatible; BasicScraper/1.0)',
                limitations=['No JavaScript execution', 'No image processing', 'No CSS access', 'No AJAX support']
            ),
            'social_crawler': CrawlerCapability(
                name='Social Media Crawler',
                can_execute_js=True,
                can_process_images=True,
                can_access_css=True,
                can_follow_redirects=True,
                can_handle_ajax=True,
                user_agent='Mozilla/5.0 (compatible; SocialCrawler/1.0)',
                limitations=['Limited JavaScript execution', 'Focus on Open Graph content']
            )
        }
    
    def analyze_crawler_accessibility(self, url: str, crawler_type: str, 
                                    analysis_result: Optional[Any] = None) -> CrawlerAnalysisResult:
        """
        Analyze how a specific crawler would access the website.
        
        Args:
            url: Website URL to analyze
            crawler_type: Type of crawler ('googlebot', 'bingbot', 'llm', 'basic_scraper', 'social_crawler')
            analysis_result: Optional existing analysis result
            
        Returns:
            CrawlerAnalysisResult with accessibility details
        """
        self.logger.info(f"Analyzing {crawler_type} accessibility for {url}")
        
        if crawler_type not in self.crawler_capabilities:
            raise ValueError(f"Unknown crawler type: {crawler_type}")
        
        crawler = self.crawler_capabilities[crawler_type]
        
        # Fetch content with crawler-specific user agent
        content, status_code = self._fetch_with_crawler_ua(url, crawler.user_agent)
        
        if not content:
            return CrawlerAnalysisResult(
                crawler_name=crawler.name,
                accessibility_score=0.0,
                content_accessible={},
                content_inaccessible={'error': 'Failed to fetch content'},
                evidence=['Failed to fetch content with crawler user agent'],
                recommendations=['Check if website blocks this crawler type']
            )
        
        # Analyze accessible content
        accessible_content = self._analyze_accessible_content(content, crawler)
        
        # Analyze inaccessible content
        inaccessible_content = self._analyze_inaccessible_content(content, crawler, analysis_result)
        
        # Calculate accessibility score
        accessibility_score = self._calculate_accessibility_score(accessible_content, inaccessible_content, crawler)
        
        # Generate evidence
        evidence = self._generate_evidence(content, crawler, accessible_content, inaccessible_content)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(crawler, inaccessible_content, accessibility_score)
        
        self.logger.info(f"{crawler_type} analysis complete. Score: {accessibility_score:.1f}")
        
        return CrawlerAnalysisResult(
            crawler_name=crawler.name,
            accessibility_score=accessibility_score,
            content_accessible=accessible_content,
            content_inaccessible=inaccessible_content,
            evidence=evidence,
            recommendations=recommendations
        )
    
    def _fetch_with_crawler_ua(self, url: str, user_agent: str) -> Tuple[Optional[str], Optional[int]]:
        """Fetch content using crawler-specific user agent."""
        try:
            headers = {
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            return response.text, response.status_code
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch {url} with {user_agent}: {e}")
            return None, None
    
    def _analyze_accessible_content(self, content: str, crawler: CrawlerCapability) -> Dict[str, Any]:
        """Analyze content that the crawler can access."""
        accessible = {
            'text_content': {
                'available': True,
                'explanation': 'All crawlers can read visible text content'
            },
            'html_structure': {
                'available': True,
                'explanation': 'All crawlers can parse HTML structure'
            },
            'meta_tags': {
                'available': True,
                'explanation': 'All crawlers can read meta tags'
            },
            'links': {
                'available': True,
                'explanation': 'All crawlers can follow links'
            }
        }
        
        # Add crawler-specific capabilities
        if crawler.can_execute_js:
            accessible['javascript'] = {
                'available': True,
                'explanation': f'{crawler.name} can execute JavaScript (with limitations)'
            }
        
        if crawler.can_process_images:
            accessible['images'] = {
                'available': True,
                'explanation': f'{crawler.name} can process images'
            }
        
        if crawler.can_access_css:
            accessible['css'] = {
                'available': True,
                'explanation': f'{crawler.name} can access CSS'
            }
        
        return accessible
    
    def _analyze_inaccessible_content(self, content: str, crawler: CrawlerCapability, 
                                    analysis_result: Optional[Any] = None) -> Dict[str, Any]:
        """Analyze content that the crawler cannot access."""
        inaccessible = {}
        
        # JavaScript-dependent content
        if not crawler.can_execute_js:
            inaccessible['javascript_content'] = {
                'available': False,
                'explanation': f'{crawler.name} cannot execute JavaScript',
                'impact': 'High - Dynamic content will be missed'
            }
        
        # Image content
        if not crawler.can_process_images:
            inaccessible['image_content'] = {
                'available': False,
                'explanation': f'{crawler.name} cannot process images',
                'impact': 'Medium - Visual content will be missed'
            }
        
        # CSS-dependent content
        if not crawler.can_access_css:
            inaccessible['css_content'] = {
                'available': False,
                'explanation': f'{crawler.name} cannot access CSS',
                'impact': 'Low - Styling information will be missed'
            }
        
        # AJAX content
        if not crawler.can_handle_ajax:
            inaccessible['ajax_content'] = {
                'available': False,
                'explanation': f'{crawler.name} cannot handle AJAX requests',
                'impact': 'High - Dynamically loaded content will be missed'
            }
        
        # Add specific limitations from analysis result
        if analysis_result and hasattr(analysis_result, 'javascript_analysis'):
            js_analysis = analysis_result.javascript_analysis
            if hasattr(js_analysis, 'dynamic_content_detected') and js_analysis.dynamic_content_detected:
                inaccessible['dynamic_content'] = {
                    'available': False,
                    'explanation': 'Content requires JavaScript execution',
                    'impact': 'Critical - Main content may be inaccessible'
                }
        
        return inaccessible
    
    def _calculate_accessibility_score(self, accessible: Dict[str, Any], 
                                     inaccessible: Dict[str, Any], 
                                     crawler: CrawlerCapability) -> float:
        """Calculate accessibility score for the crawler."""
        base_score = 100.0
        
        # Penalties for inaccessible content
        for content_type, details in inaccessible.items():
            impact = details.get('impact', 'Low')
            if impact == 'Critical':
                base_score -= 40
            elif impact == 'High':
                base_score -= 25
            elif impact == 'Medium':
                base_score -= 15
            else:
                base_score -= 5
        
        # Bonus for crawler capabilities
        if crawler.can_execute_js:
            base_score += 10
        if crawler.can_process_images:
            base_score += 5
        if crawler.can_access_css:
            base_score += 5
        
        return max(0.0, min(100.0, base_score))
    
    def _generate_evidence(self, content: str, crawler: CrawlerCapability, 
                         accessible: Dict[str, Any], inaccessible: Dict[str, Any]) -> List[str]:
        """Generate evidence for the analysis."""
        evidence = []
        
        # Add crawler-specific evidence
        evidence.append(f"Analyzed with {crawler.name} user agent: {crawler.user_agent}")
        
        # Add capability evidence
        capabilities = []
        if crawler.can_execute_js:
            capabilities.append("JavaScript execution")
        if crawler.can_process_images:
            capabilities.append("Image processing")
        if crawler.can_access_css:
            capabilities.append("CSS access")
        if crawler.can_handle_ajax:
            capabilities.append("AJAX handling")
        
        evidence.append(f"Crawler capabilities: {', '.join(capabilities) if capabilities else 'Basic HTML parsing only'}")
        
        # Add limitation evidence
        if crawler.limitations:
            evidence.append(f"Crawler limitations: {', '.join(crawler.limitations)}")
        
        # Add content accessibility evidence
        evidence.append(f"Content types accessible: {len(accessible)}")
        evidence.append(f"Content types inaccessible: {len(inaccessible)}")
        
        return evidence
    
    def _generate_recommendations(self, crawler: CrawlerCapability, 
                                inaccessible: Dict[str, Any], 
                                score: float) -> List[str]:
        """Generate recommendations for improving crawler accessibility."""
        recommendations = []
        
        # General recommendations based on score
        if score < 50:
            recommendations.append(f"CRITICAL: Website has poor accessibility for {crawler.name}")
        elif score < 70:
            recommendations.append(f"HIGH: Website has moderate accessibility issues for {crawler.name}")
        
        # Specific recommendations based on inaccessible content
        for content_type, details in inaccessible.items():
            impact = details.get('impact', 'Low')
            explanation = details.get('explanation', '')
            
            if impact == 'Critical':
                recommendations.append(f"CRITICAL: {explanation}")
            elif impact == 'High':
                recommendations.append(f"HIGH: {explanation}")
            elif impact == 'Medium':
                recommendations.append(f"MEDIUM: {explanation}")
        
        # Crawler-specific recommendations
        if crawler.name == 'LLM (GPT/Claude)':
            recommendations.extend([
                "Ensure all important content is in static HTML",
                "Provide fallback content for JavaScript features",
                "Use semantic HTML structure",
                "Include comprehensive meta descriptions"
            ])
        elif crawler.name == 'Googlebot':
            recommendations.extend([
                "Ensure JavaScript content is crawlable",
                "Use proper meta tags and structured data",
                "Implement proper internal linking",
                "Optimize page load speed"
            ])
        
        return recommendations
