"""
Meta Parser Module

Extracts meta tags, Open Graph tags, Twitter Cards, and canonical URLs from HTML.
"""

import logging
from typing import List, Dict, Optional
from bs4 import BeautifulSoup, Tag

from ..models.analysis_result import MetaTag, MetaAnalysis

logger = logging.getLogger(__name__)


class MetaParser:
    """
    Parse meta tags and related metadata from HTML.
    
    Extracts:
    - Standard meta tags (title, description, keywords)
    - Open Graph tags (og:*)
    - Twitter Card tags (twitter:*)
    - Canonical URL
    """
    
    def __init__(self, html_content: str, parser: str = 'lxml'):
        """
        Initialize meta parser.
        
        Args:
            html_content: Raw HTML content as string
            parser: BeautifulSoup parser to use (lxml, html5lib, html.parser)
        """
        self.html_content = html_content
        self.parser = parser
        
        try:
            self.soup = BeautifulSoup(html_content, parser)
        except Exception as e:
            logger.error(f"Failed to parse HTML with {parser}: {e}")
            # Fallback to html.parser
            self.soup = BeautifulSoup(html_content, 'html.parser')
    
    def extract_title(self) -> Optional[str]:
        """
        Extract page title.
        
        Returns:
            Page title or None if not found
        """
        # Try <title> tag first
        title_tag = self.soup.find('title')
        if title_tag and title_tag.string:
            return title_tag.string.strip()
        
        # Try og:title
        og_title = self.soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title.get('content').strip()
        
        # Try twitter:title
        twitter_title = self.soup.find('meta', attrs={'name': 'twitter:title'})
        if twitter_title and twitter_title.get('content'):
            return twitter_title.get('content').strip()
        
        return None
    
    def extract_description(self) -> Optional[str]:
        """
        Extract page description.
        
        Returns:
            Page description or None if not found
        """
        # Try standard description meta tag
        desc_tag = self.soup.find('meta', attrs={'name': 'description'})
        if desc_tag and desc_tag.get('content'):
            return desc_tag.get('content').strip()
        
        # Try og:description
        og_desc = self.soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            return og_desc.get('content').strip()
        
        # Try twitter:description
        twitter_desc = self.soup.find('meta', attrs={'name': 'twitter:description'})
        if twitter_desc and twitter_desc.get('content'):
            return twitter_desc.get('content').strip()
        
        return None
    
    def extract_keywords(self) -> Optional[str]:
        """
        Extract keywords meta tag.
        
        Returns:
            Keywords string or None if not found
        """
        keywords_tag = self.soup.find('meta', attrs={'name': 'keywords'})
        if keywords_tag and keywords_tag.get('content'):
            return keywords_tag.get('content').strip()
        
        return None
    
    def extract_canonical_url(self) -> Optional[str]:
        """
        Extract canonical URL.
        
        Returns:
            Canonical URL or None if not found
        """
        # Try <link rel="canonical">
        canonical_tag = self.soup.find('link', rel='canonical')
        if canonical_tag and canonical_tag.get('href'):
            return canonical_tag.get('href').strip()
        
        # Try og:url
        og_url = self.soup.find('meta', property='og:url')
        if og_url and og_url.get('content'):
            return og_url.get('content').strip()
        
        return None
    
    def extract_all_meta_tags(self) -> List[MetaTag]:
        """
        Extract all meta tags from the page.
        
        Returns:
            List of MetaTag objects
        """
        meta_tags = []
        
        for tag in self.soup.find_all('meta'):
            content = tag.get('content')
            if not content:
                continue
            
            name = tag.get('name')
            property_attr = tag.get('property')
            
            # Skip if neither name nor property exists
            if not name and not property_attr:
                continue
            
            meta_tags.append(MetaTag(
                name=name,
                property=property_attr,
                content=content.strip()
            ))
        
        return meta_tags
    
    def extract_open_graph_tags(self) -> Dict[str, str]:
        """
        Extract Open Graph (og:*) tags.
        
        Returns:
            Dictionary of Open Graph tags
        """
        og_tags = {}
        
        for tag in self.soup.find_all('meta', property=True):
            property_name = tag.get('property', '')
            if property_name.startswith('og:'):
                content = tag.get('content')
                if content:
                    # Remove 'og:' prefix for cleaner keys
                    key = property_name[3:]  # Remove 'og:' prefix
                    og_tags[key] = content.strip()
        
        return og_tags
    
    def extract_twitter_card_tags(self) -> Dict[str, str]:
        """
        Extract Twitter Card (twitter:*) tags.
        
        Returns:
            Dictionary of Twitter Card tags
        """
        twitter_tags = {}
        
        for tag in self.soup.find_all('meta', attrs={'name': True}):
            name = tag.get('name', '')
            if name.startswith('twitter:'):
                content = tag.get('content')
                if content:
                    # Remove 'twitter:' prefix for cleaner keys
                    key = name[8:]  # Remove 'twitter:' prefix
                    twitter_tags[key] = content.strip()
        
        return twitter_tags
    
    def has_open_graph(self) -> bool:
        """
        Check if page has Open Graph tags.
        
        Returns:
            True if Open Graph tags are present
        """
        return bool(self.soup.find('meta', property=lambda x: x and x.startswith('og:')))
    
    def has_twitter_cards(self) -> bool:
        """
        Check if page has Twitter Card tags.
        
        Returns:
            True if Twitter Card tags are present
        """
        return bool(self.soup.find('meta', attrs={'name': lambda x: x and x.startswith('twitter:')}))
    
    def extract_viewport(self) -> Optional[str]:
        """
        Extract viewport meta tag.
        
        Returns:
            Viewport content or None
        """
        viewport_tag = self.soup.find('meta', attrs={'name': 'viewport'})
        if viewport_tag and viewport_tag.get('content'):
            return viewport_tag.get('content').strip()
        
        return None
    
    def extract_robots(self) -> Optional[str]:
        """
        Extract robots meta tag.
        
        Returns:
            Robots directives or None
        """
        robots_tag = self.soup.find('meta', attrs={'name': 'robots'})
        if robots_tag and robots_tag.get('content'):
            return robots_tag.get('content').strip()
        
        return None
    
    def extract_author(self) -> Optional[str]:
        """
        Extract author meta tag.
        
        Returns:
            Author name or None
        """
        author_tag = self.soup.find('meta', attrs={'name': 'author'})
        if author_tag and author_tag.get('content'):
            return author_tag.get('content').strip()
        
        return None
    
    def get_meta_analysis(self) -> MetaAnalysis:
        """
        Get complete meta analysis.
        
        Note: structured_data fields will be populated by StructuredDataParser
        
        Returns:
            MetaAnalysis model with all meta information
        """
        return MetaAnalysis(
            title=self.extract_title(),
            description=self.extract_description(),
            keywords=self.extract_keywords(),
            canonical_url=self.extract_canonical_url(),
            meta_tags=self.extract_all_meta_tags(),
            open_graph_tags=self.extract_open_graph_tags(),
            twitter_card_tags=self.extract_twitter_card_tags(),
            structured_data=[],  # Will be populated by StructuredDataParser
            has_json_ld=False,  # Will be set by StructuredDataParser
            has_microdata=False,  # Will be set by StructuredDataParser
            has_rdfa=False  # Will be set by StructuredDataParser
        )
    
    def analyze(self) -> MetaAnalysis:
        """
        Perform complete meta tag analysis.
        
        Returns:
            MetaAnalysis model
        """
        logger.info("Starting meta tag analysis")
        
        try:
            meta_analysis = self.get_meta_analysis()
            
            logger.info(
                f"Meta analysis complete: title={'Yes' if meta_analysis.title else 'No'}, "
                f"description={'Yes' if meta_analysis.description else 'No'}, "
                f"OG tags={len(meta_analysis.open_graph_tags)}, "
                f"Twitter tags={len(meta_analysis.twitter_card_tags)}"
            )
            
            return meta_analysis
            
        except Exception as e:
            logger.error(f"Error during meta analysis: {e}", exc_info=True)
            raise

