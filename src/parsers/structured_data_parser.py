"""
Structured Data Parser Module

Extracts and parses structured data from HTML including:
- JSON-LD
- Microdata
- RDFa (Resource Description Framework in Attributes)
"""

import json
import logging
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup, Tag

from ..models.analysis_result import StructuredData

logger = logging.getLogger(__name__)


class StructuredDataParser:
    """
    Parse structured data markup from HTML.
    
    Supports:
    - JSON-LD (application/ld+json)
    - Microdata (itemscope, itemprop, itemtype)
    - RDFa (vocab, typeof, property)
    """
    
    def __init__(self, html_content: str, parser: str = 'lxml'):
        """
        Initialize structured data parser.
        
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
    
    def extract_json_ld(self) -> List[Dict[str, Any]]:
        """
        Extract JSON-LD structured data.
        
        JSON-LD is embedded in <script type="application/ld+json"> tags.
        
        Returns:
            List of JSON-LD objects
        """
        json_ld_scripts = []
        
        # Find all script tags with type="application/ld+json"
        for script in self.soup.find_all('script', type='application/ld+json'):
            try:
                # Parse the JSON content
                json_content = script.string
                if json_content:
                    parsed_json = json.loads(json_content.strip())
                    
                    # Handle both single objects and arrays
                    if isinstance(parsed_json, list):
                        json_ld_scripts.extend(parsed_json)
                    else:
                        json_ld_scripts.append(parsed_json)
                        
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON-LD: {e}")
                continue
            except Exception as e:
                logger.warning(f"Error processing JSON-LD script: {e}")
                continue
        
        return json_ld_scripts
    
    def extract_microdata(self) -> List[Dict[str, Any]]:
        """
        Extract Microdata structured data.
        
        Microdata uses itemscope, itemtype, and itemprop attributes.
        
        Returns:
            List of Microdata objects
        """
        microdata_items = []
        
        # Find all elements with itemscope attribute
        for item in self.soup.find_all(attrs={'itemscope': True}):
            microdata_obj = self._parse_microdata_item(item)
            if microdata_obj:
                microdata_items.append(microdata_obj)
        
        return microdata_items
    
    def _parse_microdata_item(self, element: Tag) -> Optional[Dict[str, Any]]:
        """
        Parse a single Microdata item.
        
        Args:
            element: BeautifulSoup Tag with itemscope
            
        Returns:
            Dictionary representing the Microdata item
        """
        item = {}
        
        # Get item type
        itemtype = element.get('itemtype')
        if itemtype:
            item['@type'] = itemtype if isinstance(itemtype, str) else itemtype[0]
        
        # Get item ID
        itemid = element.get('itemid')
        if itemid:
            item['@id'] = itemid
        
        # Find all properties within this item
        properties = {}
        for prop in element.find_all(attrs={'itemprop': True}):
            # Skip nested items (they'll be processed separately)
            if prop.has_attr('itemscope'):
                nested_item = self._parse_microdata_item(prop)
                prop_name = prop.get('itemprop')
                if isinstance(prop_name, list):
                    prop_name = prop_name[0]
                properties[prop_name] = nested_item
                continue
            
            prop_name = prop.get('itemprop')
            if isinstance(prop_name, list):
                prop_name = prop_name[0]
            
            # Get property value
            prop_value = self._get_microdata_property_value(prop)
            
            # Handle multiple properties with same name
            if prop_name in properties:
                if not isinstance(properties[prop_name], list):
                    properties[prop_name] = [properties[prop_name]]
                properties[prop_name].append(prop_value)
            else:
                properties[prop_name] = prop_value
        
        if properties:
            item['properties'] = properties
        
        return item if item else None
    
    def _get_microdata_property_value(self, element: Tag) -> Any:
        """
        Get the value of a Microdata property.
        
        Args:
            element: BeautifulSoup Tag with itemprop
            
        Returns:
            Property value (string, URL, etc.)
        """
        # For meta tags, use content attribute
        if element.name == 'meta':
            return element.get('content', '')
        
        # For link/a tags, use href
        if element.name in ['link', 'a']:
            return element.get('href', '')
        
        # For img/audio/video, use src
        if element.name in ['img', 'audio', 'video', 'source']:
            return element.get('src', '')
        
        # For time tags, use datetime if available
        if element.name == 'time':
            return element.get('datetime', element.get_text().strip())
        
        # For data tags, use value
        if element.name == 'data':
            return element.get('value', element.get_text().strip())
        
        # Default: get text content
        return element.get_text().strip()
    
    def extract_rdfa(self) -> List[Dict[str, Any]]:
        """
        Extract RDFa structured data.
        
        RDFa uses vocab, typeof, property attributes.
        
        Returns:
            List of RDFa objects
        """
        rdfa_items = []
        
        # Find all elements with typeof attribute (RDFa)
        for item in self.soup.find_all(attrs={'typeof': True}):
            rdfa_obj = self._parse_rdfa_item(item)
            if rdfa_obj:
                rdfa_items.append(rdfa_obj)
        
        return rdfa_items
    
    def _parse_rdfa_item(self, element: Tag) -> Optional[Dict[str, Any]]:
        """
        Parse a single RDFa item.
        
        Args:
            element: BeautifulSoup Tag with typeof
            
        Returns:
            Dictionary representing the RDFa item
        """
        item = {}
        
        # Get type
        typeof = element.get('typeof')
        if typeof:
            item['@type'] = typeof if isinstance(typeof, str) else typeof[0]
        
        # Get vocab
        vocab = element.get('vocab')
        if vocab:
            item['@vocab'] = vocab
        
        # Get resource/about (subject)
        resource = element.get('resource') or element.get('about')
        if resource:
            item['@id'] = resource
        
        # Find all properties
        properties = {}
        for prop in element.find_all(attrs={'property': True}):
            # Skip nested items
            if prop.has_attr('typeof') and prop != element:
                nested_item = self._parse_rdfa_item(prop)
                prop_name = prop.get('property')
                if isinstance(prop_name, list):
                    prop_name = prop_name[0]
                properties[prop_name] = nested_item
                continue
            
            prop_name = prop.get('property')
            if isinstance(prop_name, list):
                prop_name = prop_name[0]
            
            # Get property value
            prop_value = self._get_rdfa_property_value(prop)
            
            # Handle multiple properties with same name
            if prop_name in properties:
                if not isinstance(properties[prop_name], list):
                    properties[prop_name] = [properties[prop_name]]
                properties[prop_name].append(prop_value)
            else:
                properties[prop_name] = prop_value
        
        if properties:
            item['properties'] = properties
        
        return item if item else None
    
    def _get_rdfa_property_value(self, element: Tag) -> Any:
        """
        Get the value of an RDFa property.
        
        Args:
            element: BeautifulSoup Tag with property attribute
            
        Returns:
            Property value
        """
        # Check for content attribute
        if element.has_attr('content'):
            return element.get('content')
        
        # Check for resource attribute
        if element.has_attr('resource'):
            return element.get('resource')
        
        # For link/a tags, use href
        if element.name in ['link', 'a'] and element.has_attr('href'):
            return element.get('href')
        
        # Default: get text content
        return element.get_text().strip()
    
    def has_json_ld(self) -> bool:
        """
        Check if page has JSON-LD structured data.
        
        Returns:
            True if JSON-LD is present
        """
        return bool(self.soup.find('script', type='application/ld+json'))
    
    def has_microdata(self) -> bool:
        """
        Check if page has Microdata.
        
        Returns:
            True if Microdata is present
        """
        return bool(self.soup.find(attrs={'itemscope': True}))
    
    def has_rdfa(self) -> bool:
        """
        Check if page has RDFa.
        
        Returns:
            True if RDFa is present
        """
        return bool(self.soup.find(attrs={'typeof': True}))
    
    def get_all_structured_data(self) -> List[StructuredData]:
        """
        Get all structured data from the page.
        
        Returns:
            List of StructuredData objects
        """
        all_data = []
        
        # Extract JSON-LD
        json_ld_data = self.extract_json_ld()
        for data in json_ld_data:
            all_data.append(StructuredData(
                type='json-ld',
                data=data
            ))
        
        # Extract Microdata
        microdata = self.extract_microdata()
        for data in microdata:
            all_data.append(StructuredData(
                type='microdata',
                data=data
            ))
        
        # Extract RDFa
        rdfa_data = self.extract_rdfa()
        for data in rdfa_data:
            all_data.append(StructuredData(
                type='rdfa',
                data=data
            ))
        
        return all_data
    
    def analyze(self) -> Dict[str, Any]:
        """
        Perform complete structured data analysis.
        
        Returns:
            Dictionary with structured data and flags
        """
        logger.info("Starting structured data analysis")
        
        try:
            structured_data = self.get_all_structured_data()
            
            result = {
                'structured_data': structured_data,
                'has_json_ld': self.has_json_ld(),
                'has_microdata': self.has_microdata(),
                'has_rdfa': self.has_rdfa()
            }
            
            logger.info(
                f"Structured data analysis complete: "
                f"JSON-LD={result['has_json_ld']}, "
                f"Microdata={result['has_microdata']}, "
                f"RDFa={result['has_rdfa']}, "
                f"Total items={len(structured_data)}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error during structured data analysis: {e}", exc_info=True)
            raise

