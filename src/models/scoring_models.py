"""
Scoring models and recommendations
"""

from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class Priority(str, Enum):
    """Recommendation priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Difficulty(str, Enum):
    """Implementation difficulty"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ImpactLevel(str, Enum):
    """Expected impact of recommendation"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Recommendation(BaseModel):
    """Individual optimization recommendation"""
    title: str
    description: str
    priority: Priority
    difficulty: Difficulty
    impact: ImpactLevel
    category: str  # html, meta, javascript, structured_data, etc.
    code_example: Optional[str] = None
    resources: List[str] = Field(default_factory=list)


class ScoreComponent(BaseModel):
    """Individual score component"""
    name: str
    score: float  # 0-100 or specific max
    max_score: float
    percentage: float
    description: str
    issues: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)


class ScoreBreakdown(BaseModel):
    """Detailed score breakdown"""
    total_score: float  # 0-100
    grade: str  # A+, A, B+, B, C+, C, D, F
    
    # Component scores
    static_content_quality: ScoreComponent
    semantic_html_structure: ScoreComponent
    structured_data_implementation: ScoreComponent
    meta_tag_completeness: ScoreComponent
    javascript_dependency: ScoreComponent
    crawler_accessibility: ScoreComponent


class Score(BaseModel):
    """Complete scoring result"""
    scraper_friendliness: ScoreBreakdown
    llm_accessibility: ScoreBreakdown
    recommendations: List[Recommendation]
    
    @staticmethod
    def calculate_grade(score: float) -> str:
        """Calculate letter grade from score"""
        if score >= 97:
            return "A+"
        elif score >= 93:
            return "A"
        elif score >= 90:
            return "A-"
        elif score >= 87:
            return "B+"
        elif score >= 83:
            return "B"
        elif score >= 80:
            return "B-"
        elif score >= 77:
            return "C+"
        elif score >= 73:
            return "C"
        elif score >= 70:
            return "C-"
        elif score >= 67:
            return "D+"
        elif score >= 63:
            return "D"
        elif score >= 60:
            return "D-"
        else:
            return "F"

