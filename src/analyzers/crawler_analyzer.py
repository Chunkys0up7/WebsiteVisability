"""
Crawler Analysis Module

Analyzes robots.txt, sitemaps, and crawler directives.
"""

import logging
import requests
from typing import Optional, List, Dict, Any
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree as ET

from ..utils.validators import URLValidator

logger = logging.getLogger(__name__)


class RobotsTxtParser:
    """Parser for robots.txt files"""
    
    def __init__(self, content: str):
        """
        Initialize parser with robots.txt content
        
        Args:
            content: Raw robots.txt content
        """
        self.content = content
        self.rules: Dict[str, List[Dict[str, Any]]] = {}
        self._parse()
    
    def _parse(self):
        """Parse robots.txt content"""
        if not self.content:
            return
        
        current_agents = []
        
        for line in self.content.split('\n'):
            line = line.split('#')[0].strip()  # Remove comments
            
            if not line:
                continue
            
            if ':' not in line:
                continue
            
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            
            if key == 'user-agent':
                current_agents.append(value)
            elif key in ['disallow', 'allow', 'crawl-delay', 'sitemap']:
                for agent in current_agents or ['*']:
                    if agent not in self.rules:
                        self.rules[agent] = []
                    self.rules[agent].append({
                        'directive': key,
                        'value': value
                    })
                
                if key == 'sitemap':
                    current_agents = []
    
    def is_allowed(self, path: str, user_agent: str = '*') -> bool:
        """
        Check if path is allowed for user agent
        
        Args:
            path: URL path to check
            user_agent: User agent name
            
        Returns:
            True if allowed, False if disallowed
        """
        # Check specific agent rules first
        rules = self.rules.get(user_agent, []) + self.rules.get('*', [])
        
        for rule in rules:
            if rule['directive'] == 'disallow':
                pattern = rule['value']
                if pattern and path.startswith(pattern):
                    return False
            elif rule['directive'] == 'allow':
                pattern = rule['value']
                if pattern and path.startswith(pattern):
                    return True
        
        return True
    
    def get_crawl_delay(self, user_agent: str = '*') -> Optional[float]:
        """Get crawl delay for user agent"""
        rules = self.rules.get(user_agent, []) + self.rules.get('*', [])
        
        for rule in rules:
            if rule['directive'] == 'crawl-delay':
                try:
                    return float(rule['value'])
                except ValueError:
                    pass
        
        return None
    
    def get_sitemaps(self) -> List[str]:
        """Get list of sitemap URLs"""
        sitemaps = []
        
        for agent_rules in self.rules.values():
            for rule in agent_rules:
                if rule['directive'] == 'sitemap':
                    sitemaps.append(rule['value'])
        
        return list(set(sitemaps))


class CrawlerAnalyzer:
    """
    Analyzer for crawler directives and accessibility
    
    Checks robots.txt, sitemaps, and other crawler-related configurations.
    """
    
    def __init__(self, timeout: int = 10):
        """
        Initialize crawler analyzer
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; WebScraperAnalyzer/1.0)'
        })
    
    def fetch_robots_txt(self, base_url: str) -> Optional[str]:
        """
        Fetch robots.txt content
        
        Args:
            base_url: Base URL of the website
            
        Returns:
            robots.txt content or None if not found
        """
        robots_url = urljoin(base_url, '/robots.txt')
        
        try:
            logger.info(f"Fetching robots.txt from {robots_url}")
            response = self.session.get(robots_url, timeout=self.timeout)
            
            if response.status_code == 200:
                return response.text
            else:
                logger.info(f"robots.txt not found (status {response.status_code})")
                return None
        except requests.RequestException as e:
            logger.warning(f"Error fetching robots.txt: {e}")
            return None
    
    def fetch_llms_txt(self, base_url: str) -> Optional[str]:
        """
        Fetch llms.txt content (new standard for LLM crawlers)
        
        Args:
            base_url: Base URL of the website
            
        Returns:
            llms.txt content or None if not found
        """
        llms_url = urljoin(base_url, '/llms.txt')
        
        try:
            logger.info(f"Fetching llms.txt from {llms_url}")
            response = self.session.get(llms_url, timeout=self.timeout)
            
            if response.status_code == 200:
                return response.text
            else:
                logger.info(f"llms.txt not found (status {response.status_code})")
                return None
        except requests.RequestException as e:
            logger.warning(f"Error fetching llms.txt: {e}")
            return None
    
    def fetch_sitemap(self, sitemap_url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch and parse XML sitemap
        
        Args:
            sitemap_url: URL of the sitemap
            
        Returns:
            Parsed sitemap data or None
        """
        try:
            logger.info(f"Fetching sitemap from {sitemap_url}")
            response = self.session.get(sitemap_url, timeout=self.timeout)
            
            if response.status_code != 200:
                return None
            
            # Parse XML
            root = ET.fromstring(response.content)
            
            # Handle namespace
            ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            urls = []
            for url_elem in root.findall('.//ns:url', ns):
                loc = url_elem.find('ns:loc', ns)
                lastmod = url_elem.find('ns:lastmod', ns)
                changefreq = url_elem.find('ns:changefreq', ns)
                priority = url_elem.find('ns:priority', ns)
                
                url_data = {
                    'loc': loc.text if loc is not None else None,
                    'lastmod': lastmod.text if lastmod is not None else None,
                    'changefreq': changefreq.text if changefreq is not None else None,
                    'priority': priority.text if priority is not None else None
                }
                urls.append(url_data)
            
            return {
                'url': sitemap_url,
                'urls': urls,
                'url_count': len(urls)
            }
        
        except ET.ParseError as e:
            logger.warning(f"Error parsing sitemap XML: {e}")
            return None
        except requests.RequestException as e:
            logger.warning(f"Error fetching sitemap: {e}")
            return None
    
    def analyze(self, url: str) -> Dict[str, Any]:
        """
        Perform complete crawler analysis
        
        Args:
            url: Website URL to analyze
            
        Returns:
            Dictionary with crawler analysis results
        """
        # Normalize URL
        is_valid, normalized_url, error = URLValidator.validate_and_normalize(url)
        if not is_valid:
            logger.error(f"Invalid URL: {error}")
            return {
                'has_robots_txt': False,
                'has_llms_txt': False,
                'is_crawlable': True,  # Assume crawlable if no robots.txt
                'robots_txt_content': None,
                'llms_txt_content': None,
                'crawl_delay': None,
                'sitemaps': [],
                'sitemap_data': [],
                'disallowed_paths': [],
                'error': error
            }
        
        # Parse base URL
        parsed = urlparse(normalized_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # Fetch robots.txt
        robots_content = self.fetch_robots_txt(base_url)
        has_robots = robots_content is not None
        
        # Parse robots.txt
        robots_parser = None
        is_crawlable = True
        crawl_delay = None
        sitemap_urls = []
        disallowed_paths = []
        
        if has_robots:
            robots_parser = RobotsTxtParser(robots_content)
            is_crawlable = robots_parser.is_allowed(parsed.path or '/')
            crawl_delay = robots_parser.get_crawl_delay()
            sitemap_urls = robots_parser.get_sitemaps()
            
            # Extract disallowed paths
            for agent, rules in robots_parser.rules.items():
                for rule in rules:
                    if rule['directive'] == 'disallow' and rule['value']:
                        disallowed_paths.append(rule['value'])
        
        # Fetch llms.txt
        llms_content = self.fetch_llms_txt(base_url)
        has_llms = llms_content is not None
        
        # Fetch sitemaps
        sitemap_data = []
        for sitemap_url in sitemap_urls[:3]:  # Limit to first 3 sitemaps
            sitemap = self.fetch_sitemap(sitemap_url)
            if sitemap:
                sitemap_data.append(sitemap)
        
        # If no sitemaps in robots.txt, try default location
        if not sitemap_urls:
            default_sitemap = urljoin(base_url, '/sitemap.xml')
            sitemap = self.fetch_sitemap(default_sitemap)
            if sitemap:
                sitemap_data.append(sitemap)
                sitemap_urls.append(default_sitemap)
        
        return {
            'has_robots_txt': has_robots,
            'has_llms_txt': has_llms,
            'is_crawlable': is_crawlable,
            'robots_txt_content': robots_content,
            'llms_txt_content': llms_content,
            'crawl_delay': crawl_delay,
            'sitemaps': sitemap_urls,
            'sitemap_data': sitemap_data,
            'disallowed_paths': list(set(disallowed_paths)),
            'has_sitemap': len(sitemap_data) > 0,
            'total_urls_in_sitemaps': sum(s.get('url_count', 0) for s in sitemap_data)
        }
    
    def close(self):
        """Close the session"""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

