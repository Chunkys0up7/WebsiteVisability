"""
Parsers for HTML, meta tags, and structured data
"""

from .html_parser import HTMLParser

# Import other parsers when they're implemented
try:
    from .meta_parser import MetaParser
except ImportError:
    MetaParser = None

try:
    from .structured_data_parser import StructuredDataParser
except ImportError:
    StructuredDataParser = None

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

