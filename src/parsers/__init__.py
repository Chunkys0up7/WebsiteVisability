"""
Parsers for HTML, meta tags, and structured data
"""

from .html_parser import HTMLParser
from .meta_parser import MetaParser
from .structured_data_parser import StructuredDataParser

# Import other parsers when they're implemented

try:
    from .javascript_parser import JavaScriptParser
except ImportError:
    JavaScriptParser = None

__all__ = [
    "HTMLParser",
    "MetaParser",
    "StructuredDataParser",
    "JavaScriptParser",
]

