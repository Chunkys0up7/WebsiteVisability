"""
HTML Parser Module

Parses HTML content to extract structure, text, and metadata.
Detects semantic elements, heading hierarchy, and CSS-hidden content.
"""

import logging
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup, Tag, NavigableString
import re

from ..models.analysis_result import (
    ContentAnalysis,
    StructureAnalysis,
    HeadingHierarchy,
    HiddenContent,
)
from ..utils.helpers import clean_text, count_words
from ..utils.token_counter import estimate_tokens

logger = logging.getLogger(__name__)


class HTMLParser:
    """
    Parse HTML content and extract structure, text, and metadata.
    
    This parser analyzes HTML to determine what content is accessible
    to web scrapers and LLMs, including detection of CSS-hidden elements.
    """
    
    # Semantic HTML5 elements
    SEMANTIC_ELEMENTS = {
        'article', 'aside', 'details', 'figcaption', 'figure',
        'footer', 'header', 'main', 'mark', 'nav', 'section',
        'summary', 'time'
    }
    
    # Elements to exclude from text extraction
    EXCLUDED_ELEMENTS = {
        'script', 'style', 'noscript', 'iframe', 'svg', 'path'
    }
    
    def __init__(self, html_content: str, parser: str = 'lxml'):
        """
        Initialize HTML parser.
        
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
    
    def extract_text(self, clean: bool = True) -> str:
        """
        Extract all visible text content from HTML.
        
        Args:
            clean: Whether to clean and normalize the text
            
        Returns:
            Extracted text content
        """
        # Remove excluded elements
        for element in self.EXCLUDED_ELEMENTS:
            for tag in self.soup.find_all(element):
                tag.decompose()
        
        # Get text
        text = self.soup.get_text(separator=' ', strip=True)
        
        if clean:
            text = clean_text(text)
        
        return text
    
    def parse_heading_hierarchy(self) -> HeadingHierarchy:
        """
        Extract heading hierarchy (H1-H6).
        
        Returns:
            HeadingHierarchy model with all headings
        """
        hierarchy = HeadingHierarchy()
        
        for level in range(1, 7):
            tag_name = f'h{level}'
            headings = self.soup.find_all(tag_name)
            heading_texts = [clean_text(h.get_text()) for h in headings if h.get_text().strip()]
            
            setattr(hierarchy, tag_name.replace('h', 'h'), heading_texts)
        
        return hierarchy
    
    def detect_semantic_elements(self) -> List[str]:
        """
        Detect semantic HTML5 elements.
        
        Returns:
            List of semantic element names found
        """
        found_elements = set()
        
        for element in self.SEMANTIC_ELEMENTS:
            if self.soup.find(element):
                found_elements.add(element)
        
        return sorted(list(found_elements))
    
    def count_structural_elements(self) -> Dict[str, int]:
        """
        Count various structural elements.
        
        Returns:
            Dictionary with counts of different element types
        """
        return {
            'paragraphs': len(self.soup.find_all('p')),
            'links': len(self.soup.find_all('a')),
            'images': len(self.soup.find_all('img')),
            'tables': len(self.soup.find_all('table')),
            'lists': len(self.soup.find_all(['ul', 'ol'])),
            'divs': len(self.soup.find_all('div')),
            'spans': len(self.soup.find_all('span')),
        }
    
    def detect_hidden_content(self) -> HiddenContent:
        """
        Detect CSS-hidden elements that are still accessible to scrapers.
        
        CSS properties like display:none and visibility:hidden hide content
        from users but NOT from web scrapers.
        
        Returns:
            HiddenContent model with hidden element counts and details
        """
        display_none = []
        visibility_hidden = []
        hidden_attr = []
        
        # Find elements with display:none
        for element in self.soup.find_all(style=True):
            style = element.get('style', '')
            if 'display:none' in style.replace(' ', '').lower():
                display_none.append({
                    'tag': element.name,
                    'text': clean_text(element.get_text())[:100],  # First 100 chars
                    'style': style
                })
        
        # Find elements with visibility:hidden
        for element in self.soup.find_all(style=True):
            style = element.get('style', '')
            if 'visibility:hidden' in style.replace(' ', '').lower():
                visibility_hidden.append({
                    'tag': element.name,
                    'text': clean_text(element.get_text())[:100],
                    'style': style
                })
        
        # Find elements with hidden attribute
        for element in self.soup.find_all(hidden=True):
            hidden_attr.append({
                'tag': element.name,
                'text': clean_text(element.get_text())[:100],
            })
        
        # Also check for class-based hiding (common patterns)
        for element in self.soup.find_all(class_=True):
            classes = element.get('class', [])
            if any(cls in ['hidden', 'd-none', 'hide', 'invisible'] for cls in classes):
                # This might be hidden by CSS, but we can't be 100% sure without CSS
                pass
        
        return HiddenContent(
            display_none_count=len(display_none),
            visibility_hidden_count=len(visibility_hidden),
            hidden_attribute_count=len(hidden_attr),
            hidden_elements=display_none + visibility_hidden + hidden_attr
        )
    
    def calculate_dom_depth(self) -> int:
        """
        Calculate maximum DOM nesting depth.
        
        Returns:
            Maximum nesting depth of HTML elements
        """
        def get_depth(element, current_depth=0):
            if not isinstance(element, Tag):
                return current_depth
            
            max_child_depth = current_depth
            for child in element.children:
                if isinstance(child, Tag):
                    child_depth = get_depth(child, current_depth + 1)
                    max_child_depth = max(max_child_depth, child_depth)
            
            return max_child_depth
        
        if self.soup.body:
            return get_depth(self.soup.body)
        return get_depth(self.soup)
    
    def has_proper_structure(self) -> bool:
        """
        Check if HTML has proper semantic structure.
        
        Returns:
            True if HTML has good semantic structure
        """
        # Check for basic structural elements
        has_header = bool(self.soup.find('header'))
        has_main = bool(self.soup.find('main'))
        has_footer = bool(self.soup.find('footer'))
        has_nav = bool(self.soup.find('nav'))
        
        # Check for heading hierarchy
        has_h1 = bool(self.soup.find('h1'))
        
        # Good structure should have at least some semantic elements
        semantic_score = sum([has_header, has_main, has_footer, has_nav, has_h1])
        
        return semantic_score >= 2
    
    def get_content_analysis(self) -> ContentAnalysis:
        """
        Get complete content analysis.
        
        Returns:
            ContentAnalysis model with all content metrics
        """
        text_content = self.extract_text()
        counts = self.count_structural_elements()
        
        return ContentAnalysis(
            text_content=text_content,
            character_count=len(text_content),
            word_count=count_words(text_content),
            estimated_tokens=estimate_tokens(text_content),
            paragraphs=counts['paragraphs'],
            links=counts['links'],
            images=counts['images'],
            tables=counts['tables'],
            lists=counts['lists']
        )
    
    def get_structure_analysis(self) -> StructureAnalysis:
        """
        Get complete structure analysis.
        
        Returns:
            StructureAnalysis model with all structure metrics
        """
        semantic_elements = self.detect_semantic_elements()
        heading_hierarchy = self.parse_heading_hierarchy()
        
        return StructureAnalysis(
            has_semantic_html=len(semantic_elements) > 0,
            semantic_elements=semantic_elements,
            heading_hierarchy=heading_hierarchy,
            total_elements=len(self.soup.find_all()),
            nested_depth=self.calculate_dom_depth(),
            has_proper_structure=self.has_proper_structure()
        )
    
    def get_all_links(self) -> List[Dict[str, str]]:
        """
        Extract all links with their text and href.
        
        Returns:
            List of dictionaries with link information
        """
        links = []
        for link in self.soup.find_all('a', href=True):
            links.append({
                'text': clean_text(link.get_text()),
                'href': link.get('href'),
                'title': link.get('title', '')
            })
        return links
    
    def get_all_images(self) -> List[Dict[str, str]]:
        """
        Extract all images with their attributes.
        
        Returns:
            List of dictionaries with image information
        """
        images = []
        for img in self.soup.find_all('img'):
            images.append({
                'src': img.get('src', ''),
                'alt': img.get('alt', ''),
                'title': img.get('title', ''),
                'width': img.get('width', ''),
                'height': img.get('height', '')
            })
        return images
    
    def analyze(self) -> Tuple[ContentAnalysis, StructureAnalysis, HiddenContent]:
        """
        Perform complete HTML analysis.
        
        Returns:
            Tuple of (ContentAnalysis, StructureAnalysis, HiddenContent)
        """
        logger.info("Starting HTML analysis")
        
        try:
            content_analysis = self.get_content_analysis()
            structure_analysis = self.get_structure_analysis()
            hidden_content = self.detect_hidden_content()
            
            logger.info(
                f"HTML analysis complete: {content_analysis.word_count} words, "
                f"{len(structure_analysis.semantic_elements)} semantic elements, "
                f"{hidden_content.display_none_count + hidden_content.visibility_hidden_count} hidden elements"
            )
            
            return content_analysis, structure_analysis, hidden_content
            
        except Exception as e:
            logger.error(f"Error during HTML analysis: {e}", exc_info=True)
            raise

