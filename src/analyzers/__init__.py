"""
Analysis engines for web content evaluation
"""

# Import analyzers when they're implemented
from .static_analyzer import StaticAnalyzer
from .dynamic_analyzer import DynamicAnalyzer

try:
    from .content_comparator import ContentComparator
except ImportError:
    ContentComparator = None

try:
    from .scoring_engine import ScoringEngine
except ImportError:
    ScoringEngine = None

__all__ = [
    "StaticAnalyzer",
    "DynamicAnalyzer",
    "ContentComparator",
    "ScoringEngine",
]

