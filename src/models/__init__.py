"""
Data models for analysis results
"""

from .analysis_result import (
    AnalysisResult,
    ContentAnalysis,
    StructureAnalysis,
    MetaAnalysis,
    JavaScriptAnalysis,
    CrawlerAnalysis,
)
from .scoring_models import (
    Score,
    ScoreBreakdown,
    Recommendation,
)

__all__ = [
    "AnalysisResult",
    "ContentAnalysis",
    "StructureAnalysis",
    "MetaAnalysis",
    "JavaScriptAnalysis",
    "CrawlerAnalysis",
    "Score",
    "ScoreBreakdown",
    "Recommendation",
]

