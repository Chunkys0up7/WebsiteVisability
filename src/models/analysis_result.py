"""
Data models for analysis results
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field, ConfigDict


class ContentAnalysis(BaseModel):
    """Content extraction results"""
    text_content: str
    character_count: int
    word_count: int
    estimated_tokens: int
    paragraphs: int
    links: int
    images: int
    tables: int
    lists: int


class HeadingHierarchy(BaseModel):
    """Heading structure"""
    h1: List[str] = Field(default_factory=list)
    h2: List[str] = Field(default_factory=list)
    h3: List[str] = Field(default_factory=list)
    h4: List[str] = Field(default_factory=list)
    h5: List[str] = Field(default_factory=list)
    h6: List[str] = Field(default_factory=list)


class StructureAnalysis(BaseModel):
    """HTML structure analysis"""
    has_semantic_html: bool
    semantic_elements: List[str]
    heading_hierarchy: HeadingHierarchy
    total_elements: int
    nested_depth: int
    has_proper_structure: bool


class HiddenContent(BaseModel):
    """CSS-hidden content detection"""
    display_none_count: int
    visibility_hidden_count: int
    hidden_attribute_count: int
    hidden_elements: List[Dict[str, str]]


class MetaTag(BaseModel):
    """Individual meta tag"""
    name: Optional[str] = None
    property: Optional[str] = None
    content: str


class StructuredData(BaseModel):
    """Structured data markup"""
    type: str  # json-ld, microdata, rdfa
    data: Dict[str, Any]


class MetaAnalysis(BaseModel):
    """Meta tags and structured data"""
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[str] = None
    canonical_url: Optional[str] = None
    meta_tags: List[MetaTag]
    open_graph_tags: Dict[str, str]
    twitter_card_tags: Dict[str, str]
    structured_data: List[StructuredData]
    has_json_ld: bool
    has_microdata: bool
    has_rdfa: bool


class JavaScriptFramework(BaseModel):
    """Detected JavaScript framework"""
    name: str
    confidence: float  # 0.0 to 1.0
    indicators: List[str]


class JavaScriptAnalysis(BaseModel):
    """JavaScript detection and analysis"""
    total_scripts: int
    inline_scripts: int
    external_scripts: int
    frameworks: List[JavaScriptFramework]
    is_spa: bool
    has_ajax: bool
    dynamic_content_detected: bool


class CrawlerDirective(BaseModel):
    """Crawler directive entry"""
    user_agent: str
    rules: List[str]


class CrawlerAnalysis(BaseModel):
    """robots.txt and crawler directives"""
    has_robots_txt: bool
    robots_txt_content: Optional[str] = None
    robots_directives: List[CrawlerDirective]
    has_llms_txt: bool
    llms_txt_content: Optional[str] = None
    has_sitemap: bool
    sitemap_urls: List[str]
    is_crawlable: bool


class ContentComparison(BaseModel):
    """Comparison between static and dynamic content"""
    static_content_length: int
    dynamic_content_length: int
    content_difference: int
    similarity_score: float  # 0.0 to 1.0
    javascript_dependent: bool
    missing_in_static: List[str]
    added_elements: List[str] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    """Complete analysis result"""
    url: str
    analyzed_at: datetime = Field(default_factory=datetime.now)
    status: str  # success, error, partial
    error_message: Optional[str] = None
    
    # Analysis components
    content_analysis: Optional[ContentAnalysis] = None
    structure_analysis: Optional[StructureAnalysis] = None
    hidden_content: Optional[HiddenContent] = None
    meta_analysis: Optional[MetaAnalysis] = None
    javascript_analysis: Optional[JavaScriptAnalysis] = None
    crawler_analysis: Optional[CrawlerAnalysis] = None
    content_comparison: Optional[ContentComparison] = None
    
    # Scores
    scraper_friendliness_score: Optional[float] = None
    llm_accessibility_score: Optional[float] = None
    
    # Performance metrics
    analysis_duration_seconds: Optional[float] = None
    page_load_time_seconds: Optional[float] = None
    page_size_bytes: Optional[int] = None
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

