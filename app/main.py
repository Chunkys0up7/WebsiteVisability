"""
Main Streamlit Application

Web interface for analyzing website scraper-friendliness and LLM accessibility.
"""

import streamlit as st
import logging
from datetime import datetime
import time
import pandas as pd
import html
from typing import Optional, List, Any

from src.analyzers import StaticAnalyzer, DynamicAnalyzer, ContentComparator, ScoringEngine
from src.analyzers.llm_accessibility_analyzer import LLMAccessibilityAnalyzer
from src.analyzers.ssr_detector import SSRDetector
from src.analyzers.web_crawler_analyzer import WebCrawlerAnalyzer
from src.analyzers.evidence_capture import EvidenceCapture
from src.analyzers.enhanced_llm_analyzer import EnhancedLLMAccessibilityAnalyzer
from src.analyzers.bot_directives_analyzer import BotDirectivesAnalyzer
from src.analyzers.website_comparison_analyzer import WebsiteComparisonAnalyzer
from src.analyzers.llm_content_viewer import LLMContentViewer
from src.analyzers.llm_scraper_comparison import LLMScraperComparisonAnalyzer
from src.utils.validators import URLValidator
from src.utils.report_generator import ComprehensiveReportGenerator, ReportData
from src.models.analysis_result import AnalysisResult
from src.models.scoring_models import Score, Recommendation, ScoreComponent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Web Scraper & LLM Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* General Streamlit Overrides */
    .stApp {
            background-color: #ffffff;
            color: #1a1a1a;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
        }

        /* Fix for responsive layout */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }

        /* Main Header - High contrast, no gradient */
    .main-header {
        font-size: 3.2rem;
            font-weight: 800;
            color: #1a1a1a;
        margin-bottom: 0.5rem;
        padding-top: 1rem;
        line-height: 1.2;
            text-align: center;
            text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    .subtitle {
        font-size: 1.25rem;
            color: #4a4a4a;
        margin-bottom: 2.5rem;
            text-align: center;
            font-weight: 400;
    }

        /* Section Headers - High contrast */
    .section-header {
        font-size: 2rem;
            font-weight: 700;
            color: #1a1a1a;
            border-bottom: 3px solid #2563eb;
        padding-bottom: 0.8rem;
        margin-top: 3rem;
        margin-bottom: 2rem;
    }
    .sub-section-header {
        font-size: 1.6rem;
            font-weight: 600;
            color: #1a1a1a;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }

        /* Score Cards - Enhanced contrast */
    .score-card {
        background-color: #ffffff;
            border-left: 6px solid;
            border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
            min-height: 120px;
            border: 1px solid #e5e7eb;
    }
    .score-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
    }
    .score-card-header {
        font-size: 1.1em;
            font-weight: 600;
        margin-bottom: 0.6rem;
            color: #1a1a1a;
    }
    .score-value {
        font-size: 2.2em;
            font-weight: 800;
        line-height: 1;
            color: #1a1a1a;
            margin: 0.5rem 0;
    }
    .score-grade {
        font-size: 1em;
            font-weight: 500;
            color: #4a4a4a;
        margin-top: 0.5rem;
    }
        /* Score card specific colors - High contrast with proper text colors */
        .score-card.excellent { 
            border-left-color: #059669; 
            background-color: #f0fdf4;
        }
        .score-card.excellent .score-card-header,
        .score-card.excellent .score-value,
        .score-card.excellent .score-grade {
            color: #065f46;
        }
        
        .score-card.good { 
            border-left-color: #2563eb; 
            background-color: #eff6ff;
        }
        .score-card.good .score-card-header,
        .score-card.good .score-value,
        .score-card.good .score-grade {
            color: #1e40af;
        }
        
        .score-card.fair { 
            border-left-color: #d97706; 
            background-color: #fffbeb;
        }
        .score-card.fair .score-card-header,
        .score-card.fair .score-value,
        .score-card.fair .score-grade {
            color: #92400e;
        }
        
        .score-card.poor { 
            border-left-color: #dc2626; 
            background-color: #fef2f2;
        }
        .score-card.poor .score-card-header,
        .score-card.poor .score-value,
        .score-card.poor .score-grade {
            color: #991b1b;
        }
        
        .score-card.neutral { 
            border-left-color: #6b7280; 
            background-color: #f9fafb;
        }
        .score-card.neutral .score-card-header,
        .score-card.neutral .score-value,
        .score-card.neutral .score-grade {
            color: #374151;
        }

        /* Tab Groups and Navigation */
        .tab-group-header {
            margin: 2rem 0 1rem 0;
            padding: 1rem;
            background-color: #f8fafc;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
        }
        .tab-group-header h3 {
            font-size: 1.3rem;
            font-weight: 600;
            color: #1a1a1a;
            margin: 0 0 0.5rem 0;
        }
        .tab-group-header p {
            color: #4a4a4a;
            font-size: 0.95rem;
            margin: 0;
        }

        /* Streamlit Tabs - Enhanced visibility */
    .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            justify-content: flex-start;
            margin-bottom: 1rem;
            flex-wrap: wrap;
            background-color: #f8fafc;
            padding: 12px;
            border-radius: 12px;
            border: 1px solid #e5e7eb;
    }
    .stTabs [data-baseweb="tab"] {
            padding: 12px 20px;
            font-size: 1rem;
        font-weight: 500;
            color: #4a4a4a;
            transition: all 0.2s ease-in-out;
            white-space: nowrap;
            border-radius: 8px;
            background-color: #ffffff;
            border: 1px solid #e5e7eb;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab"]:hover {
            color: #2563eb;
            background-color: #eff6ff;
            border-color: #2563eb;
            transform: translateY(-1px);
    }
    .stTabs [aria-selected="true"] {
            color: #ffffff;
            background-color: #2563eb;
            border-color: #2563eb;
            font-weight: 600;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
        }
        .stTabs [aria-selected="true"]:hover {
            color: #ffffff;
            background-color: #1d4ed8;
        }

        /* Tab Content */
        .stTabs [role="tabpanel"] {
            padding: 1.5rem;
            background-color: #ffffff;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
            margin-top: 1rem;
        }

        /* Tab Navigation Indicators */
        .tab-nav-indicator {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 1rem;
            padding: 0.5rem 1rem;
            background-color: #f8fafc;
            border-radius: 6px;
            border: 1px solid #e5e7eb;
        }
        .tab-nav-indicator .current {
            font-weight: 600;
            color: #2563eb;
        }
        .tab-nav-indicator .separator {
            color: #94a3b8;
        }

        /* Responsive columns */
        @media (max-width: 768px) {
            .main-header {
                font-size: 2.5rem;
            }
            .subtitle {
                font-size: 1.1rem;
            }
            .section-header {
                font-size: 1.6rem;
            }
            .score-value {
                font-size: 1.8em;
            }
            .stTabs [data-baseweb="tab"] {
                padding: 8px 16px;
                font-size: 0.9rem;
            }
        }

        /* Sidebar improvements - Enhanced readability */
        .css-1d391kg {
            background-color: #ffffff;
            border-right: 2px solid #e5e7eb;
            padding: 2rem 1rem;
        }
        
        /* Sidebar header */
        .sidebar-header {
            font-size: 1.5rem;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #2563eb;
        }
        
        /* Sidebar sections */
        .sidebar-section {
            margin-bottom: 1.5rem;
            padding: 1rem;
            background-color: #f8fafc;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
        }
        
        .sidebar-subheader {
            font-size: 1.1rem;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 0.8rem;
        }
        
        .sidebar-description {
            font-size: 0.9rem;
            color: #4a4a4a;
            line-height: 1.5;
            margin-bottom: 1rem;
        }
        
        /* Sidebar form elements */
        .stForm > div[data-testid="stForm"] {
            border: none;
            padding: 0;
        }
        
        .stForm [data-baseweb="select"] {
            margin-top: 0.5rem;
        }
        
        .stForm .stButton button {
            width: 100%;
            margin-top: 1rem;
            background-color: #2563eb;
            color: white;
            font-weight: 600;
            padding: 0.75rem 1rem;
            border: none;
        }
        
        .stForm .stButton button:hover {
            background-color: #1d4ed8;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
        }
        
        /* Sidebar dividers */
        .sidebar-section hr {
            margin: 1rem 0;
            border: none;
            border-top: 1px solid #e5e7eb;
        }
        
        /* Sidebar help text */
        .stForm [data-baseweb="tooltip"] {
            color: #6b7280;
            font-size: 0.9rem;
            margin-top: 0.25rem;
        }
        
        /* Sidebar multiselect */
        .stForm [data-baseweb="multi-select"] {
            margin-top: 0.5rem;
            border-radius: 6px;
            border-color: #d1d5db;
        }
        
        .stForm [data-baseweb="multi-select"]:hover {
            border-color: #2563eb;
        }
        
        /* Sidebar checkboxes */
        .stForm [data-testid="stCheckbox"] {
            margin-top: 1rem;
        }
        
        .stForm [data-testid="stCheckbox"] label {
            color: #1a1a1a;
            font-weight: 500;
        }

        /* Button improvements - Enhanced visibility */
        .stButton > button {
            border-radius: 8px;
            transition: all 0.2s ease-in-out;
            font-weight: 500;
            border: 1px solid #d1d5db;
        }
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            border-color: #2563eb;
        }

        /* Status improvements */
        .stStatus {
            border-radius: 8px;
        }

        /* Progress bar improvements - High contrast */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%);
        }

        /* Text improvements for better readability */
        .stMarkdown {
            color: #1a1a1a;
            line-height: 1.7;
        }
        
        /* All text elements */
        p, div, span, li {
            color: #1a1a1a;
            line-height: 1.6;
        }
        
        /* Headers and titles */
        h1, h2, h3, h4, h5, h6 {
            color: #1a1a1a;
            font-weight: 600;
            line-height: 1.3;
            margin-top: 1.5rem;
            margin-bottom: 0.8rem;
        }
        
        /* Metric improvements */
        .metric-container {
            background-color: #f8fafc;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
        }

        /* Info boxes improvements - Enhanced readability */
        .stAlert {
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            border-left: 4px solid;
        }
        .stInfo {
            background-color: #eff6ff;
            border-left-color: #2563eb;
            color: #1e40af;
        }
        .stInfo .stMarkdown {
            color: #1e40af;
        }
        .stSuccess {
            background-color: #f0fdf4;
            border-left-color: #059669;
            color: #065f46;
        }
        .stSuccess .stMarkdown {
            color: #065f46;
        }
        .stWarning {
            background-color: #fffbeb;
            border-left-color: #d97706;
            color: #92400e;
        }
        .stWarning .stMarkdown {
            color: #92400e;
        }
        .stError {
            background-color: #fef2f2;
            border-left-color: #dc2626;
            color: #991b1b;
        }
        .stError .stMarkdown {
            color: #991b1b;
        }

        /* Expander improvements */
        .streamlit-expanderHeader {
            font-weight: 600;
            color: #1a1a1a;
            font-size: 1.1rem;
        }
        .streamlit-expanderContent {
            color: #1a1a1a;
            line-height: 1.6;
        }

        /* Code blocks */
        .stCode {
            background-color: #f8fafc;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            color: #1a1a1a;
        }
        
        /* Lists and bullet points */
        ul, ol {
            color: #1a1a1a;
            line-height: 1.6;
        }
        li {
            margin-bottom: 0.5rem;
            color: #1a1a1a;
        }
        
        /* Tables */
        .stDataFrame {
            color: #1a1a1a;
        }
        table {
            color: #1a1a1a;
        }
        th, td {
            color: #1a1a1a;
            border-color: #e5e7eb;
        }
        
        /* Streamlit specific elements */
        .stSelectbox label,
        .stTextInput label,
        .stTextArea label,
        .stNumberInput label,
        .stCheckbox label {
            color: #1a1a1a;
            font-weight: 500;
        }
        
        /* Sidebar text */
        .css-1d391kg {
            color: #1a1a1a;
        }
        .css-1d391kg .stMarkdown {
            color: #1a1a1a;
        }
        
        /* Empty state improvements */
        .empty-state {
            text-align: center;
            padding: 2rem;
            color: #6b7280;
            font-style: italic;
        }

        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
            .stApp {
                background-color: #0f172a;
                color: #f1f5f9;
            }
            .main-header {
                color: #f1f5f9;
            }
            .subtitle {
                color: #cbd5e1;
            }
            .section-header {
                color: #f1f5f9;
                border-bottom-color: #3b82f6;
            }
            .sub-section-header {
                color: #f1f5f9;
            }
            
            /* Dark mode text elements */
            .stMarkdown, p, div, span, li {
                color: #f1f5f9;
            }
            h1, h2, h3, h4, h5, h6 {
                color: #f1f5f9;
            }
            .streamlit-expanderHeader,
            .streamlit-expanderContent {
                color: #f1f5f9;
            }
            .stCode {
                background-color: #1e293b;
                color: #f1f5f9;
                border-color: #334155;
            }
            ul, ol, li {
                color: #f1f5f9;
            }
            table, th, td {
                color: #f1f5f9;
                border-color: #334155;
            }
            .stSelectbox label,
            .stTextInput label,
            .stTextArea label,
            .stNumberInput label,
            .stCheckbox label {
                color: #f1f5f9;
            }
            /* Dark mode sidebar */
            .css-1d391kg {
                background-color: #1e293b;
                border-right-color: #334155;
            }
            
            .sidebar-header {
                color: #f1f5f9;
                border-bottom-color: #3b82f6;
            }
            
            .sidebar-section {
                background-color: #0f172a;
                border-color: #334155;
            }
            
            .sidebar-subheader {
                color: #f1f5f9;
            }
            
            .sidebar-description {
                color: #cbd5e1;
            }
            
            .stForm [data-baseweb="select"] {
                background-color: #1e293b;
                color: #f1f5f9;
            }
            
            .stForm .stButton button {
                background-color: #3b82f6;
                color: #f1f5f9;
            }
            
            .stForm .stButton button:hover {
                background-color: #2563eb;
            }
            
            .stForm [data-baseweb="tooltip"] {
                color: #94a3b8;
            }
            
            .stForm [data-baseweb="multi-select"] {
                background-color: #1e293b;
                border-color: #334155;
                color: #f1f5f9;
            }
            
            .stForm [data-testid="stCheckbox"] label {
                color: #f1f5f9;
            }
            
            .sidebar-section hr {
                border-color: #334155;
            }
            .empty-state {
                color: #94a3b8;
            }
            .score-card {
                background-color: #1e293b;
                border-color: #334155;
            }
            .score-card-header {
                color: #f1f5f9;
            }
            .score-value {
                color: #f1f5f9;
            }
            .score-grade {
                color: #cbd5e1;
            }
            /* Dark mode score card specific colors */
            .score-card.excellent { 
                background-color: #064e3b;
            }
            .score-card.excellent .score-card-header,
            .score-card.excellent .score-value,
            .score-card.excellent .score-grade {
                color: #a7f3d0;
            }
            .score-card.good { 
                background-color: #1e3a8a;
            }
            .score-card.good .score-card-header,
            .score-card.good .score-value,
            .score-card.good .score-grade {
                color: #93c5fd;
            }
            .score-card.fair { 
                background-color: #78350f;
            }
            .score-card.fair .score-card-header,
            .score-card.fair .score-value,
            .score-card.fair .score-grade {
                color: #fcd34d;
            }
            .score-card.poor { 
                background-color: #7f1d1d;
            }
            .score-card.poor .score-card-header,
            .score-card.poor .score-value,
            .score-card.poor .score-grade {
                color: #fca5a5;
            }
            .score-card.neutral { 
                background-color: #374151;
            }
            .score-card.neutral .score-card-header,
            .score-card.neutral .score-value,
            .score-card.neutral .score-grade {
                color: #d1d5db;
            }
            /* Dark mode tab groups */
            .tab-group-header {
                background-color: #1e293b;
                border-color: #334155;
            }
            .tab-group-header h3 {
                color: #f1f5f9;
            }
            .tab-group-header p {
                color: #cbd5e1;
            }

            /* Dark mode tabs */
            .stTabs [data-baseweb="tab-list"] {
                background-color: #1e293b;
                border-color: #334155;
            }
            .stTabs [data-baseweb="tab"] {
                color: #cbd5e1;
                background-color: #0f172a;
                border-color: #334155;
                box-shadow: 0 1px 2px rgba(0,0,0,0.2);
            }
            .stTabs [data-baseweb="tab"]:hover {
                color: #60a5fa;
                background-color: #1e293b;
                border-color: #60a5fa;
            }
            .stTabs [aria-selected="true"] {
                color: #f1f5f9;
                background-color: #3b82f6;
                border-color: #60a5fa;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
            }
            .stTabs [aria-selected="true"]:hover {
                background-color: #2563eb;
            }

            /* Dark mode tab content */
            .stTabs [role="tabpanel"] {
                background-color: #1e293b;
                border-color: #334155;
            }

            /* Dark mode tab navigation */
            .tab-nav-indicator {
                background-color: #1e293b;
                border-color: #334155;
            }
            .tab-nav-indicator .current {
                color: #60a5fa;
            }
            .tab-nav-indicator .separator {
                color: #64748b;
            }
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'static_result' not in st.session_state:
        st.session_state.static_result = None
    if 'dynamic_result' not in st.session_state:
        st.session_state.dynamic_result = None
    if 'comparison' not in st.session_state:
        st.session_state.comparison = None
    if 'score' not in st.session_state:
        st.session_state.score = None
    if 'analyzed_url' not in st.session_state:
        st.session_state.analyzed_url = None
    if 'llm_report' not in st.session_state:
        st.session_state.llm_report = None
    if 'ssr_detection' not in st.session_state:
        st.session_state.ssr_detection = None
    if 'crawler_analysis' not in st.session_state:
        st.session_state.crawler_analysis = {}
    if 'evidence_report' not in st.session_state:
        st.session_state.evidence_report = None
    if 'enhanced_llm_report' not in st.session_state:
        st.session_state.enhanced_llm_report = None
    if 'bot_directives' not in st.session_state:
        st.session_state.bot_directives = None
    if 'last_analysis_type' not in st.session_state:
        st.session_state.last_analysis_type = None
    if 'analysis_duration' not in st.session_state:
        st.session_state.analysis_duration = 0.0
    if 'comparison_enabled' not in st.session_state:
        st.session_state.comparison_enabled = False
    if 'comparison_url' not in st.session_state:
        st.session_state.comparison_url = None
    if 'comparison_results' not in st.session_state:
        st.session_state.comparison_results = None
    if 'first_analysis' not in st.session_state:
        st.session_state.first_analysis = None
    if 'comparison_static_result' not in st.session_state:
        st.session_state.comparison_static_result = None
    if 'comparison_dynamic_result' not in st.session_state:
        st.session_state.comparison_dynamic_result = None
    if 'comparison_llm_report' not in st.session_state:
        st.session_state.comparison_llm_report = None
    if 'comparison_enhanced_llm_report' not in st.session_state:
        st.session_state.comparison_enhanced_llm_report = None
    if 'comparison_bot_directives' not in st.session_state:
        st.session_state.comparison_bot_directives = None
    if 'comparison_score' not in st.session_state:
        st.session_state.comparison_score = None

def clear_session_state():
    """Clear all analysis data from session state"""
    keys_to_clear = [
        'analysis_complete', 'static_result', 'dynamic_result', 'comparison', 
        'score', 'analyzed_url', 'llm_report', 'ssr_detection', 'crawler_analysis',
        'evidence_report', 'enhanced_llm_report', 'bot_directives', 
        'last_analysis_type', 'analysis_duration', 'comparison_enabled',
        'comparison_url', 'comparison_results', 'first_analysis',
        'comparison_static_result', 'comparison_dynamic_result',
        'comparison_llm_report', 'comparison_enhanced_llm_report',
        'comparison_bot_directives', 'comparison_score'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    # Reinitialize with defaults
    initialize_session_state()

def _get_grade(score: float) -> str:
    """Calculate letter grade from score"""
    if score >= 97: return "A+"
    elif score >= 93: return "A"
    elif score >= 90: return "A-"
    elif score >= 87: return "B+"
    elif score >= 83: return "B"
    elif score >= 80: return "B-"
    elif score >= 77: return "C+"
    elif score >= 73: return "C"
    elif score >= 70: return "C-"
    elif score >= 67: return "D+"
    elif score >= 63: return "D"
    elif score >= 60: return "D-"
    else: return "F"

def generate_pdf_report() -> str:
    """Generate comprehensive HTML report for PDF export"""
    report = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Website Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1 {{ color: #667eea; border-bottom: 3px solid #764ba2; padding-bottom: 10px; }}
        h2 {{ color: #4A90E2; margin-top: 30px; border-bottom: 2px solid #ddd; padding-bottom: 8px; }}
        h3 {{ color: #2c3e50; margin-top: 20px; }}
        .score-box {{ background: #f8f9fa; border-left: 4px solid #667eea; padding: 15px; margin: 10px 0; }}
        .metric {{ display: inline-block; margin: 10px 20px; }}
        .excellent {{ color: #10b981; font-weight: bold; }}
        .good {{ color: #3b82f6; font-weight: bold; }}
        .fair {{ color: #f59e0b; font-weight: bold; }}
        .poor {{ color: #ef4444; font-weight: bold; }}
        .recommendation {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; margin: 10px 0; }}
        .critical {{ background: #f8d7da; border-left: 4px solid #dc3545; padding: 10px; margin: 10px 0; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #667eea; color: white; }}
        .timestamp {{ color: #6c757d; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>🔍 Website Analysis Report</h1>
    <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="score-box">
        <h2>📊 Executive Summary</h2>
        <p><strong>Primary URL:</strong> {html.escape(st.session_state.analyzed_url)}</p>
"""
    
    # Add comparison info if available
    if st.session_state.comparison_url:
        report += f"""
        <p><strong>Comparison URL:</strong> {html.escape(st.session_state.comparison_url)}</p>
"""
    
    # Add scores
    if st.session_state.score:
        scraper_score = st.session_state.score.scraper_friendliness.total_score
        llm_score = st.session_state.score.llm_accessibility.total_score
        report += f"""
        <div class="metric">
            <h3>Scraper Friendliness</h3>
            <p class="{"excellent" if scraper_score >= 80 else "good" if scraper_score >= 60 else "fair" if scraper_score >= 40 else "poor"}">
                {scraper_score:.1f}/100 ({st.session_state.score.scraper_friendliness.grade})
            </p>
        </div>
        <div class="metric">
            <h3>LLM Accessibility</h3>
            <p class="{"excellent" if llm_score >= 80 else "good" if llm_score >= 60 else "fair" if llm_score >= 40 else "poor"}">
                {llm_score:.1f}/100 ({st.session_state.score.llm_accessibility.grade})
            </p>
        </div>
"""
    report += "</div>"
    
    # Add content analysis
    if st.session_state.static_result and st.session_state.static_result.content_analysis:
        content = st.session_state.static_result.content_analysis
        report += f"""
    <h2>📝 Content Analysis</h2>
    <table>
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>Word Count</td><td>{content.word_count:,}</td></tr>
        <tr><td>Character Count</td><td>{content.character_count:,}</td></tr>
        <tr><td>Paragraphs</td><td>{content.paragraphs}</td></tr>
        <tr><td>Links</td><td>{content.links}</td></tr>
        <tr><td>Images</td><td>{content.images}</td></tr>
        <tr><td>Tables</td><td>{content.tables}</td></tr>
        <tr><td>Lists</td><td>{content.lists}</td></tr>
    </table>
"""
    
    # Add recommendations
    if st.session_state.score and st.session_state.score.recommendations:
        report += "<h2>💡 Key Recommendations</h2>"
        critical = [r for r in st.session_state.score.recommendations if r.priority.value == "critical"]
        high = [r for r in st.session_state.score.recommendations if r.priority.value == "high"]
        
        if critical:
            report += "<h3>🚨 Critical Issues</h3>"
            for rec in critical:
                report += f'<div class="critical"><strong>{html.escape(rec.title)}</strong><br>{html.escape(rec.description)}</div>'
        
        if high:
            report += "<h3>⚠️ High Priority</h3>"
            for rec in high:
                report += f'<div class="recommendation"><strong>{html.escape(rec.title)}</strong><br>{html.escape(rec.description)}</div>'
    
    # Add comparison results
    if st.session_state.comparison_results:
        comparison = st.session_state.comparison_results
        report += f"""
    <h2>🔄 Website Comparison</h2>
    <div class="score-box">
        <p><strong>Overall Similarity:</strong> {comparison.overall_similarity_score:.1f}%</p>
        <h3>Key Insights:</h3>
        <ul>
"""
        for insight in comparison.key_insights[:5]:  # Top 5 insights
            report += f"<li>{html.escape(insight)}</li>"
        report += """
        </ul>
    </div>
"""
    
    # Add bot directives analysis
    if st.session_state.bot_directives:
        analysis = st.session_state.bot_directives
        report += f"""
    <h2>🤖 Bot Directives Analysis</h2>
    <div class="score-box">
        <p><strong>robots.txt:</strong> {'✅ Present' if analysis.robots_txt.is_present else '❌ Missing'}</p>
        <p><strong>llms.txt:</strong> {'✅ Present' if analysis.llms_txt.is_present else '❌ Missing'}</p>
        <p><strong>Compatibility Score:</strong> {analysis.compatibility_score:.1f}/100</p>
    </div>
"""
    
    # Close HTML
    report += """
    <hr>
    <p class="timestamp">End of Report</p>
</body>
</html>
"""
    return report

def get_score_color_class(score: float) -> str:
    """Get CSS class based on score"""
    if score >= 85: return "excellent"
    elif score >= 70: return "good"
    elif score >= 50: return "fair"
    else: return "poor"

def render_score_card(header: str, value: Any, grade: str, score: float = None, is_na: bool = False, na_reason: str = None):
    """Renders a stylized score card."""
    if is_na:
        score_class = "neutral"
        value_display = "N/A"
        grade_display = na_reason if na_reason else "No Data"
    else:
        score_class = get_score_color_class(score) if score is not None else "neutral"
        value_display = f"{value}"
        grade_display = f"Grade: {grade}"

    st.markdown(f"""
    <div class="score-card {score_class}">
        <div class="score-card-header">{header}</div>
        <div class="score-value">{value_display}</div>
        <div class="score-grade">{grade_display}</div>
    </div>
    """, unsafe_allow_html=True)

def perform_analysis(
    url: str,
    analyze_dynamic: bool = True,
    analysis_type: str = "Comprehensive Analysis",
    crawler_types: Optional[List[str]] = None,
    capture_evidence: bool = True,
    comparison_url: Optional[str] = None
):
    """Perform website analysis based on selected focus"""
    start_time = time.time()
    
    try:
        with st.status("🚀 Starting website analysis...", expanded=True) as status:
            st.session_state.analysis_complete = False
            
            # Static Analysis
            static_result = None
            if analysis_type in ["Comprehensive Analysis", "LLM Accessibility Only", "Web Crawler Testing", "SSR Detection Only"]:
                status.update(label="🌐 Fetching initial page content and performing static analysis...", state="running")
                static_analyzer = StaticAnalyzer(timeout=30)
                static_result = static_analyzer.analyze(url)
                
                if static_result.status != "success":
                    error_msg = static_result.error_message or "Unknown error"
                    st.error(f"Static analysis failed: {error_msg}")
                    status.update(label="Static analysis failed.", state="error")
                    return False
                
                st.session_state.static_result = static_result
                logger.info(f"Static analysis completed for {url}")
            
            # Dynamic Analysis
            dynamic_result = None
            if analysis_type == "Comprehensive Analysis" and analyze_dynamic:
                status.update(label="⚙️ Launching headless browser for dynamic rendering...", state="running")
                try:
                    dynamic_analyzer = DynamicAnalyzer(timeout=30, headless=True)
                    dynamic_result = dynamic_analyzer.analyze(url)
                    
                    if dynamic_result and dynamic_result.status != "success":
                        error_msg = dynamic_result.error_message or "Unknown error"
                        st.warning(f"Dynamic analysis failed: {error_msg}")
                        dynamic_result = None
                    else:
                        st.session_state.dynamic_result = dynamic_result
                        logger.info(f"Dynamic analysis completed for {url}")
                except Exception as e:
                    st.warning(f"Dynamic analysis error: {str(e)}")
                    logger.error(f"Dynamic analysis error for {url}: {e}")
                    dynamic_result = None
            
            # Content Comparison
            comparison = None
            if analysis_type == "Comprehensive Analysis" and dynamic_result:
                status.update(label="📊 Comparing static vs dynamic content...", state="running")
                comparator = ContentComparator()
                comparison = comparator.compare(static_result, dynamic_result)
                st.session_state.comparison = comparison
                logger.info(f"Content comparison completed for {url}")
            
            # LLM Accessibility Analysis
            if analysis_type in ["Comprehensive Analysis", "LLM Accessibility Only"]:
                status.update(label="🤖 Analyzing LLM accessibility...", state="running")
                llm_analyzer = LLMAccessibilityAnalyzer()
                llm_report = llm_analyzer.analyze(static_result)
                st.session_state.llm_report = llm_report
                logger.info(f"LLM accessibility analysis completed for {url}")
                
                status.update(label="🔬 Performing enhanced LLM analysis...", state="running")
                enhanced_llm_analyzer = EnhancedLLMAccessibilityAnalyzer()
                enhanced_llm_report = enhanced_llm_analyzer.analyze(static_result)
                st.session_state.enhanced_llm_report = enhanced_llm_report
                logger.info(f"Enhanced LLM analysis completed for {url}")
                
                status.update(label="📄 Analyzing robots.txt and llms.txt files...", state="running")
                bot_directives_analyzer = BotDirectivesAnalyzer()
                bot_directives = bot_directives_analyzer.analyze(url)
                st.session_state.bot_directives = bot_directives
                logger.info(f"Bot directives analysis completed for {url}")
            
            # SSR Detection
            if analysis_type in ["Comprehensive Analysis", "SSR Detection Only"]:
                status.update(label="🔍 Detecting Server-Side Rendering patterns...", state="running")
                ssr_detector = SSRDetector()
                ssr_detection = ssr_detector.detect_ssr(
                    static_result.content_analysis.text_content if static_result and static_result.content_analysis else "", 
                    static_result.javascript_analysis if static_result else None
                )
                st.session_state.ssr_detection = ssr_detection
                logger.info(f"SSR detection completed for {url}")
            
            # Web Crawler Testing
            if analysis_type in ["Comprehensive Analysis", "Web Crawler Testing"]:
                if crawler_types is None:
                    crawler_types = ["llm", "googlebot"]
                
                crawler_analyzer = WebCrawlerAnalyzer()
                crawler_results = {}
                
                for crawler_type in crawler_types:
                    status.update(label=f"🕷️ Testing {crawler_type.replace('_', ' ').title()} accessibility...", state="running")
                    try:
                        crawler_result = crawler_analyzer.analyze_crawler_accessibility(url, crawler_type, static_result)
                        crawler_results[crawler_type] = crawler_result
                        logger.info(f"{crawler_type} analysis completed for {url}")
                    except Exception as e:
                        st.warning(f"Failed to analyze {crawler_type}: {str(e)}")
                        logger.error(f"Crawler analysis error for {crawler_type} on {url}: {e}")
                
                st.session_state.crawler_analysis = crawler_results
            
            # Evidence Capture
            if capture_evidence:
                status.update(label="📊 Capturing evidence and generating reports...", state="running")
                evidence_capture = EvidenceCapture()
                
                evidence_data = {}
                if st.session_state.crawler_analysis:
                    # Convert CrawlerAnalysisResult objects to AnalysisEvidence objects
                    for crawler_type, crawler_result in st.session_state.crawler_analysis.items():
                        evidence = evidence_capture.capture_analysis_evidence(
                            url=url,
                            crawler_type=crawler_type,
                            analysis_result=crawler_result,
                            technical_details={'accessibility_score': crawler_result.accessibility_score}
                        )
                        evidence_data[crawler_type] = evidence
                
                if evidence_data:
                    evidence_report = evidence_capture.create_evidence_report(url, evidence_data)
                    st.session_state.evidence_report = evidence_report
                    logger.info(f"Evidence report generated for {url}")
                else:
                    st.warning("No evidence data available to capture")
            
            # Scoring
            if analysis_type == "Comprehensive Analysis":
                status.update(label="⚡ Calculating scores and generating recommendations...", state="running")
                scoring_engine = ScoringEngine()
                score = scoring_engine.calculate_score(static_result, comparison)
                st.session_state.score = score
                logger.info(f"Scoring completed for {url}")
            else:
                st.session_state.score = None
            
                # If comparison URL is provided, store first analysis results
            if comparison_url and st.session_state.comparison_enabled:
                status.update(label="🔄 Starting comparison analysis...", state="running")
                
                # Store first analysis results
                st.session_state.first_analysis = {
                    'url': url,
                    'static_result': static_result,
                    'dynamic_result': dynamic_result,
                    'bot_directives': st.session_state.bot_directives,
                    'llm_report': st.session_state.llm_report,
                    'score': st.session_state.score
                }
                
                # Validate comparison URL
                is_valid, normalized_comparison_url, error_msg = URLValidator.validate_and_normalize(comparison_url)
                if not is_valid:
                    st.error(f"⚠️ Comparison URL invalid: {error_msg}")
                    return False
                
                # Analyze comparison URL
                comparison_success = perform_analysis(
                    normalized_comparison_url,
                    analyze_dynamic,
                    analysis_type,
                    crawler_types,
                    capture_evidence,
                    None  # No nested comparisons
                )
                
                if not comparison_success:
                    st.error(f"❌ Comparison analysis failed for {normalized_comparison_url}")
                    return False
                
                # Compare the two websites
                status.update(label="📊 Comparing websites...", state="running")
                comparison_analyzer = WebsiteComparisonAnalyzer()
                
                try:
                    comparison_results = comparison_analyzer.compare(
                        url1=st.session_state.first_analysis['url'],
                        url2=comparison_url,
                        analysis1=st.session_state.first_analysis['static_result'],
                        analysis2=st.session_state.static_result,
                        bot_directives1=st.session_state.first_analysis['bot_directives'],
                        bot_directives2=st.session_state.bot_directives,
                        llm_score1=(
                            st.session_state.first_analysis['llm_report'].overall_score 
                            if st.session_state.first_analysis['llm_report'] else None
                        ),
                        llm_score2=(
                            st.session_state.llm_report.overall_score 
                            if st.session_state.llm_report else None
                        ),
                        scraper_score1=(
                            st.session_state.first_analysis['score'].scraper_friendliness.total_score 
                            if st.session_state.first_analysis['score'] else None
                        ),
                        scraper_score2=(
                            st.session_state.score.scraper_friendliness.total_score 
                            if st.session_state.score else None
                        )
                    )
                    st.session_state.comparison_results = comparison_results
                    logger.info(f"Website comparison completed between {st.session_state.first_analysis['url']} and {comparison_url}")
                    
                    # Restore the first analysis as the primary display
                    st.session_state.static_result = st.session_state.first_analysis['static_result']
                    st.session_state.dynamic_result = st.session_state.first_analysis['dynamic_result']
                    st.session_state.bot_directives = st.session_state.first_analysis['bot_directives']
                    st.session_state.llm_report = st.session_state.first_analysis['llm_report']
                    st.session_state.score = st.session_state.first_analysis['score']
                    
                except Exception as e:
                    logger.error(f"Comparison error: {str(e)}")
                    st.error(f"❌ Comparison failed: {str(e)}")
                    return False
            
            st.session_state.analysis_complete = True
            st.session_state.analyzed_url = url
            st.session_state.last_analysis_type = analysis_type
            
            end_time = time.time()
            st.session_state.analysis_duration = end_time - start_time
            
            status.update(
                label="✅ Analysis complete!" + (" (with comparison)" if comparison_url else ""),
                state="complete",
                expanded=False
            )
            return True
        
    except Exception as e:
        st.error(f"❌ Analysis failed: {str(e)}")
        logger.error(f"Analysis error for {url}: {e}")
        st.session_state.analysis_complete = False
        return False

def main():
    """Main application function"""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🔍 Web Scraper & LLM Analyzer</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">Analyze any website to understand what content is accessible to web scrapers and LLMs</p>',
        unsafe_allow_html=True
    )
    
    # Sidebar - Input Form
    with st.sidebar:
        st.markdown('<h2 class="sidebar-header">⚙️ Quick Setup</h2>', unsafe_allow_html=True)
        
        with st.form("analysis_config_form"):
            # URL Input
            url_input = st.text_input(
                "🌐 Website URL",
                value=st.session_state.get('analyzed_url', ''),
                placeholder="https://example.com"
            )
            
            # Comparison toggle
            prev_comparison_enabled = st.session_state.get('comparison_enabled', False)
            prev_comparison_url = st.session_state.get('comparison_url', '')
            
            comparison_enabled = st.checkbox(
                "🔄 Compare with another site",
                value=prev_comparison_enabled,
                key="comparison_enabled_checkbox"
            )
            
            # Show comparison URL input (disabled if not enabled)
            comparison_url = st.text_input(
                "Comparison URL",
                value=prev_comparison_url if prev_comparison_url else "",
                placeholder="https://competitor.com",
                disabled=not comparison_enabled,
                key="comparison_url_input"
            )
            
            # Update session state
            st.session_state.comparison_enabled = comparison_enabled
            st.session_state.comparison_url = comparison_url if comparison_enabled else None
            
            # Clear comparison results if disabled
            if not comparison_enabled and prev_comparison_enabled:
                st.session_state.comparison_results = None
                st.session_state.first_analysis = None
            
            st.markdown("---")
            
            # Analysis type - compact
            analysis_options = ["Comprehensive Analysis", "LLM Accessibility Only", "Web Crawler Testing", "SSR Detection Only"]
            last_analysis = st.session_state.get('last_analysis_type', 'Comprehensive Analysis')
            
            try:
                default_index = analysis_options.index(last_analysis)
            except (ValueError, TypeError):
                default_index = 0
            
            analysis_type = st.selectbox(
                "📊 Analysis Type",
                analysis_options,
                index=default_index
            )
            
            crawler_types = None
            if analysis_type == "Web Crawler Testing":
                crawler_types = st.multiselect(
                    "Crawlers",
                    ["googlebot", "bingbot", "llm", "basic_scraper", "social_crawler"],
                    default=st.session_state.get('last_crawler_types_selection', ["llm", "googlebot"])
                )
                st.session_state.last_crawler_types_selection = crawler_types
            
            # Advanced options - collapsed by default
            with st.expander("⚙️ Advanced", expanded=False):
                analyze_dynamic = False
                if analysis_type == "Comprehensive Analysis":
                    analyze_dynamic = st.checkbox(
                        "Dynamic analysis",
                        value=True
                    )
                
                capture_evidence = st.checkbox(
                    "Detailed evidence",
                    value=st.session_state.get('last_capture_evidence_selection', True)
                )
                st.session_state.last_capture_evidence_selection = capture_evidence
            
            st.markdown("---")
            analyze_button = st.form_submit_button("🚀 Analyze Website", type="primary", use_container_width=True)
        
        # Clear button (if analysis exists)
        if st.session_state.analysis_complete:
            st.markdown("---")
            if st.button("🗑️ Clear & Restart", type="secondary", use_container_width=True):
                clear_session_state()
                st.rerun()
    
    # Process analysis
    if analyze_button:
        if not url_input:
            st.error("⚠️ Please enter a URL to start the analysis.")
        else:
            is_valid, normalized_url, error_msg = URLValidator.validate_and_normalize(url_input)
            if not is_valid:
                st.error(f"⚠️ {error_msg}")
            else:
                url_input = normalized_url
                success = perform_analysis(
                    url_input,
                    analyze_dynamic,
                    analysis_type,
                                         crawler_types,
                    capture_evidence,
                    comparison_url if comparison_enabled else None
                )
                
                if success:
                    st.rerun()
    
    # Display results
    if st.session_state.analysis_complete:
        st.markdown('<h2 class="section-header">✅ Analysis Complete</h2>', unsafe_allow_html=True)
        
        # Action buttons
        col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
        with col_btn1:
            st.markdown(f"**Analyzed:** `{st.session_state.analyzed_url}`")
            if st.session_state.comparison_url:
                st.markdown(f"**Compared with:** `{st.session_state.comparison_url}`")
        with col_btn2:
            # Generate PDF report content
            if st.button("📥 Download PDF Report", type="primary", use_container_width=True):
                pdf_content = generate_pdf_report()
                st.download_button(
                    label="💾 Save Report",
                    data=pdf_content,
                    file_name=f"website_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html",
                    use_container_width=True
                )
        with col_btn3:
            if st.button("🗑️ Clear Results", type="secondary", use_container_width=True):
                clear_session_state()
                st.rerun()
        
        st.markdown("---")
        
        # Score Cards
        st.markdown('<h3 class="section-header">📊 Quick Summary</h3>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.session_state.score:
                scraper_score = st.session_state.score.scraper_friendliness.total_score
                scraper_grade = st.session_state.score.scraper_friendliness.grade
                render_score_card("Scraper Friendliness", f"{scraper_score:.1f}/100", scraper_grade, scraper_score)
            else:
                render_score_card("Scraper Friendliness", None, None, is_na=True,
                                  na_reason=f"N/A ({st.session_state.last_analysis_type})")
        
        with col2:
            if st.session_state.score:
                llm_score = st.session_state.score.llm_accessibility.total_score
                llm_grade = st.session_state.score.llm_accessibility.grade
                render_score_card("LLM Accessibility", f"{llm_score:.1f}/100", llm_grade, llm_score)
            elif st.session_state.enhanced_llm_report:
                llm_score = st.session_state.enhanced_llm_report.overall_score
                llm_grade = st.session_state.enhanced_llm_report.grade
                render_score_card("Enhanced LLM Score", f"{llm_score:.1f}/100", llm_grade, llm_score)
            elif st.session_state.llm_report:
                llm_score = st.session_state.llm_report.overall_score
                llm_grade = st.session_state.llm_report.grade
                render_score_card("LLM Accessibility", f"{llm_score:.1f}/100", llm_grade, llm_score)
            else:
                render_score_card("LLM Accessibility", None, None, is_na=True,
                                  na_reason=f"N/A ({st.session_state.last_analysis_type})")
        
        with col3:
            if st.session_state.static_result and st.session_state.static_result.content_analysis:
                word_count = st.session_state.static_result.content_analysis.word_count
                render_score_card("Total Word Count", f"{word_count:,}", "Static HTML Content", is_na=True, na_reason="Static HTML")
            else:
                render_score_card("Total Word Count", None, None, is_na=True)
        
        with col4:
            if st.session_state.score and st.session_state.score.recommendations:
                recommendations_count = len(st.session_state.score.recommendations)
                critical_count = len([r for r in st.session_state.score.recommendations if r.priority.value == "critical"])
                
                score_for_card = max(0, 100 - (critical_count * 15 + recommendations_count * 2))
                grade_for_card = _get_grade(score_for_card)
                
                render_score_card("Key Recommendations", recommendations_count, grade_for_card, score_for_card)
            else:
                render_score_card("Key Recommendations", None, None, is_na=True, na_reason="No comprehensive score")
        
        st.markdown("---")
        
        # Score Breakdown Section
        if st.session_state.score:
            st.markdown('<h3 class="section-header">🔍 Score Breakdown</h3>', unsafe_allow_html=True)
            
            col_breakdown1, col_breakdown2 = st.columns(2)
            
            with col_breakdown1:
                with st.expander("📊 Scraper Friendliness Score Breakdown", expanded=True):
                    score_obj = st.session_state.score.scraper_friendliness
                    
                    st.markdown(f"""
                    **Total Score:** {score_obj.total_score:.1f}/100 ({score_obj.grade})
                    
                    **Component Scores:**
                    """)
                    
                    # Show each component with its score and details
                    components = [
                        ('static_content_quality', '📝 Static Content Quality'),
                        ('semantic_html_structure', '🏗️ Semantic HTML Structure'),
                        ('structured_data_implementation', '📊 Structured Data'),
                        ('meta_tag_completeness', '🏷️ Meta Tags'),
                        ('javascript_dependency', '⚡ JavaScript Dependency'),
                        ('crawler_accessibility', '🕷️ Crawler Accessibility')
                    ]
                    
                    for attr_name, display_name in components:
                        if hasattr(score_obj, attr_name):
                            component = getattr(score_obj, attr_name)
                            st.write(f"• {display_name}: **{component.score:.1f}/{component.max_score:.0f}** ({component.percentage:.0f}%)")
                            if hasattr(component, 'description') and component.description:
                                st.caption(f"  └─ {component.description}")
                            if hasattr(component, 'issues') and component.issues:
                                for issue in component.issues[:2]:  # Show first 2 issues
                                    st.caption(f"     ⚠️ {issue}")
                            if hasattr(component, 'strengths') and component.strengths:
                                for strength in component.strengths[:2]:  # Show first 2 strengths
                                    st.caption(f"     ✅ {strength}")
                    
                    st.markdown("---")
                    st.markdown(f"""
                    **Calculation Method:**
                    ```
                    Total = Sum of all component scores
                    Final Score = (Total / Max Possible) × 100
                    
                    Each component is weighted based on importance:
                    - Content Quality: 25 points max
                    - Semantic Structure: 20 points max
                    - Structured Data: 15 points max
                    - Meta Tags: 15 points max
                    - JS Dependency: 15 points max (penalty)
                    - Crawler Access: 10 points max
                    ```
                    """)
                    
                    st.markdown(f"""
                    **Evidence:**
                    - Analyzed {st.session_state.static_result.content_analysis.word_count if st.session_state.static_result else 'N/A'} words of content
                    - Found {len(st.session_state.static_result.semantic_structure.semantic_tags) if st.session_state.static_result else 0} semantic HTML elements
                    - Detected {len(st.session_state.static_result.structured_data.json_ld) if st.session_state.static_result else 0} JSON-LD items
                    - Evaluated {len(st.session_state.static_result.meta_tags.all_meta_tags) if st.session_state.static_result else 0} meta tags
                    """)
            
            with col_breakdown2:
                with st.expander("🤖 LLM Accessibility Score Breakdown", expanded=True):
                    score_obj = st.session_state.score.llm_accessibility
                    
                    st.markdown(f"""
                    **Total Score:** {score_obj.total_score:.1f}/100 ({score_obj.grade})
                    
                    **Component Scores:**
                    """)
                    
                    # Show each component with its score and details
                    components = [
                        ('static_content_quality', '📝 Content Quality'),
                        ('semantic_html_structure', '🏗️ Semantic Structure'),
                        ('structured_data_implementation', '📊 Structured Data'),
                        ('meta_tag_completeness', '🏷️ Meta Tags'),
                        ('javascript_dependency', '⚡ JS Dependency'),
                        ('crawler_accessibility', '🤖 LLM Accessibility')
                    ]
                    
                    for attr_name, display_name in components:
                        if hasattr(score_obj, attr_name):
                            component = getattr(score_obj, attr_name)
                            st.write(f"• {display_name}: **{component.score:.1f}/{component.max_score:.0f}** ({component.percentage:.0f}%)")
                            if hasattr(component, 'description') and component.description:
                                st.caption(f"  └─ {component.description}")
                            if hasattr(component, 'issues') and component.issues:
                                for issue in component.issues[:2]:  # Show first 2 issues
                                    st.caption(f"     ⚠️ {issue}")
                            if hasattr(component, 'strengths') and component.strengths:
                                for strength in component.strengths[:2]:  # Show first 2 strengths
                                    st.caption(f"     ✅ {strength}")
                    
                    st.markdown("---")
                    st.markdown(f"""
                    **Calculation Method:**
                    ```
                    Total = Sum of all component scores
                    Final Score = (Total / Max Possible) × 100
                    
                    Each component is weighted for LLM accessibility:
                    - Content Quality: 30 points max (critical for LLMs)
                    - Semantic Structure: 25 points max (helps understanding)
                    - Structured Data: 20 points max (rich context)
                    - Meta Tags: 15 points max (descriptions)
                    - JS Dependency: 10 points max (penalty for SPA)
                    ```
                    """)
                    
                    if st.session_state.llm_report:
                        llm_report = st.session_state.llm_report
                        st.markdown(f"""
                        **Evidence:**
                        - LLMs can access {llm_report.accessible_content['text_content']['word_count']:,} words of text content
                        - Found {len(llm_report.accessible_content['semantic_structure']['semantic_elements'])} semantic elements
                        - Detected {len(llm_report.accessible_content['structured_data']['json_ld'])} JSON-LD schemas
                        - Identified {len(llm_report.limitations)} accessibility limitations
                        - **{llm_report.accessible_content['meta_information']['title'] and llm_report.accessible_content['meta_information']['description']}** meta coverage
                        """)
            
            st.markdown("---")
        
        # Organize tabs into logical groups
        st.markdown("""
        <div class="tab-group-header">
            <h3>📊 Analysis Results</h3>
            <p>Key findings and overview of the analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Primary Analysis Tabs
        primary_tabs = st.tabs([
            "🔄 Comparison",
            "🎯 Executive Summary",
            "📊 Overview",
            "🤖 LLM Analysis",
            "👁️ LLM Visibility",
            "💡 Recommendations"
        ])
        
        st.markdown("""
        <div class="tab-group-header">
            <h3>🔍 Detailed Analysis</h3>
            <p>In-depth analysis of specific website components</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Technical Analysis Tabs
        technical_tabs = st.tabs([
            "🔬 Enhanced LLM Analysis",
            "📄 LLMs.txt Analysis",
            "🕷️ Scraper Analysis",
            "🔍 SSR Detection",
            "🕷️ Crawler Testing"
        ])
        
        st.markdown("""
        <div class="tab-group-header">
            <h3>🏗️ Website Structure</h3>
            <p>Technical breakdown of website components</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Structure Analysis Tabs
        structure_tabs = st.tabs([
            "📝 Content",
            "🏗️ Structure",
            "🏷️ Meta Data",
            "⚡ JavaScript"
        ])
        
        st.markdown("""
        <div class="tab-group-header">
            <h3>📋 Reports</h3>
            <p>Evidence and export options</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Report Tabs
        report_tabs = st.tabs([
            "📊 Evidence Report",
            "📥 Export Report"
        ])
        
        # Combine all tabs for reference
        tabs = primary_tabs + technical_tabs + structure_tabs + report_tabs
        
        with tabs[0]:  # LLM vs Scraper Comparison
            st.markdown('<h2 class="section-header">🔄 LLM vs Scraper Comparison</h2>', unsafe_allow_html=True)
            
            # Debug information
            with st.expander("🔍 Debug Info (click to expand)", expanded=False):
                st.write("comparison_enabled:", st.session_state.comparison_enabled)
                st.write("comparison_url:", st.session_state.comparison_url)
                st.write("comparison_results exists:", st.session_state.comparison_results is not None)
                if st.session_state.comparison_results:
                    st.write("comparison_results type:", type(st.session_state.comparison_results).__name__)
            
            if not st.session_state.comparison_enabled:
                st.info("✨ **Enable website comparison in the sidebar** to compare two websites side-by-side!")
            elif not st.session_state.comparison_url:
                st.info("📝 **Enter a comparison URL in the sidebar** to start the comparison.")
            elif not st.session_state.comparison_results:
                st.info("▶️ **Click 'Analyze Website' button** to run the comparison analysis.")
            else:
                # We have comparison results - display them!
                comparison = st.session_state.comparison_results
                
                # URLs being compared
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; margin-bottom: 1.5rem;">
                    <h3 style="color: white; margin: 0 0 1rem 0;">Comparing:</h3>
                    <p style="color: white; margin: 0.5rem 0;"><strong>URL 1:</strong> <code>{comparison.url1}</code></p>
                    <p style="color: white; margin: 0.5rem 0;"><strong>URL 2:</strong> <code>{comparison.url2}</code></p>
                </div>
                """, unsafe_allow_html=True)
            
                # Overall similarity score
                st.metric(
                    "🎯 Overall Similarity",
                    f"{comparison.overall_similarity_score:.1f}%",
                    help="How similar the two websites are across all dimensions"
                )
                
                # Score Breakdown
                st.markdown('<h3 class="sub-section-header">📊 Similarity Score Breakdown</h3>', unsafe_allow_html=True)
                st.markdown("""
                The overall similarity score is calculated from three main components:
                1. **Content Similarity (40%)**: Text content and HTML structure
                2. **Accessibility (30%)**: LLM and scraper friendliness scores
                3. **Technical (30%)**: JavaScript, meta tags, and structured data
                """)
            
                # Add calculation methodology display
                with st.expander("🧮 Detailed Calculation Methodology", expanded=True):
                    st.markdown("""
                    ### Formula
                    ```
                    Overall Similarity = (Content × 0.4) + (Accessibility × 0.3) + (Technical × 0.3)
                    ```
                    
                    ### Component Calculations
                    **Content Similarity**: Compares text content length, structure, and HTML similarity
                    - Text length comparison
                    - HTML structure analysis
                    - Semantic element comparison
                    
                    **Accessibility**: Compares LLM and scraper friendliness scores
                    - LLM accessibility scores
                    - Scraper friendliness scores
                    - Rendering method (SSR vs CSR)
                    
                    **Technical**: Compares implementation details
                    - JavaScript usage and frameworks
                    - Meta tag completeness
                    - Structured data implementation
                    """)
                
                st.markdown("---")
            
                # Content Comparison
                st.markdown('<h3 class="sub-section-header">📝 Content Comparison</h3>', unsafe_allow_html=True)
                col_content1, col_content2 = st.columns(2)
                with col_content1:
                    st.metric("Content Similarity", f"{comparison.content.similarity_score:.1f}%")
                with col_content2:
                    st.metric("Word Count Difference", f"{comparison.content.word_count_diff:+,}")
                
                if comparison.content.missing_in_url2:
                    with st.expander(f"📄 Content in URL 1 but not URL 2 ({len(comparison.content.missing_in_url2)} items)"):
                        for item in comparison.content.missing_in_url2[:10]:
                            st.write(f"• {item}")
                        if len(comparison.content.missing_in_url2) > 10:
                            st.info(f"...and {len(comparison.content.missing_in_url2) - 10} more items")
                
                if comparison.content.missing_in_url1:
                    with st.expander(f"📄 Content in URL 2 but not URL 1 ({len(comparison.content.missing_in_url1)} items)"):
                        for item in comparison.content.missing_in_url1[:10]:
                            st.write(f"• {item}")
                        if len(comparison.content.missing_in_url1) > 10:
                            st.info(f"...and {len(comparison.content.missing_in_url1) - 10} more items")
                
                st.markdown("---")
                
                # Accessibility Comparison
                st.markdown('<h3 class="sub-section-header">♿ Accessibility Comparison</h3>', unsafe_allow_html=True)
                col_access1, col_access2, col_access3 = st.columns(3)
                with col_access1:
                    st.metric("Accessibility Similarity", f"{comparison.accessibility.similarity_score:.1f}%")
                with col_access2:
                    st.metric("LLM Score Diff", f"{comparison.accessibility.llm_score_diff:+.1f}")
                with col_access3:
                    st.metric("Scraper Score Diff", f"{comparison.accessibility.scraper_score_diff:+.1f}")
                
                if comparison.accessibility.rendering_difference:
                    st.info(f"🔄 **Rendering Difference:** {comparison.accessibility.rendering_difference}")
                
                st.markdown("---")
                
                # Technical Comparison
                st.markdown('<h3 class="sub-section-header">⚙️ Technical Comparison</h3>', unsafe_allow_html=True)
                col_tech1, col_tech2 = st.columns(2)
                with col_tech1:
                    st.metric("Technical Similarity", f"{comparison.technical.similarity_score:.1f}%")
                with col_tech2:
                    st.metric("Scripts Difference", f"{comparison.technical.script_count_diff:+}")
                
                # Key insights
                st.markdown('<h3 class="sub-section-header">💡 Key Insights</h3>', unsafe_allow_html=True)
                for insight in comparison.key_insights:
                    st.info(f"• {insight}")
                
                st.markdown("---")
                
                # Additional differences
                st.markdown('<h3 class="sub-section-header">🔍 Additional Differences</h3>', unsafe_allow_html=True)
                
                # Meta tags
                total_meta_diff = (
                    len(comparison.technical.meta_tags_only_in_url1) +
                    len(comparison.technical.meta_tags_only_in_url2)
                )
                if total_meta_diff > 0:
                    st.write(f"• Meta tags: {total_meta_diff} different tags between sites")
                
                # Structured data
                total_struct_diff = (
                    len(comparison.technical.structured_data_only_in_url1) -
                    len(comparison.technical.structured_data_only_in_url2)
                )
                if total_struct_diff != 0:
                    st.write(f"• Structured data: {abs(total_struct_diff)} {'more' if total_struct_diff > 0 else 'fewer'} items in second site")

                st.markdown("---")

                # Recommendations
                if comparison.recommendations:
                    st.markdown('<h3 class="sub-section-header">💡 Recommendations</h3>', unsafe_allow_html=True)
                    for rec in comparison.recommendations:
                        st.info(f"• {rec}")
        
        with tabs[1]:  # Executive Summary
            st.markdown('<h2 class="section-header">🎯 Executive Summary & Key Takeaways</h2>', unsafe_allow_html=True)
            
            if st.session_state.analyzed_url:
                # Sanitize URL to prevent XSS
                sanitized_url = html.escape(st.session_state.analyzed_url)
                st.markdown(f"**Analysis for:** `{sanitized_url}`")
                st.markdown(f"**Analysis Type:** `{st.session_state.last_analysis_type}`")
                st.markdown(f"**Duration:** `{st.session_state.analysis_duration:.2f} seconds`")
                st.markdown("---")
                
                if st.session_state.score:
                    score = st.session_state.score
                    scraper_score = score.scraper_friendliness.total_score
                    llm_score = score.llm_accessibility.total_score
                    
                    st.markdown('<h3 class="sub-section-header">Overall Performance Snapshot</h3>', unsafe_allow_html=True)
                    
                    col_snap1, col_snap2 = st.columns(2)
                    with col_snap1:
                        render_score_card("Scraper Friendliness", f"{scraper_score:.1f}/100", score.scraper_friendliness.grade, scraper_score)
                    with col_snap2:
                        render_score_card("LLM Accessibility", f"{llm_score:.1f}/100", score.llm_accessibility.grade, llm_score)
                    
                    st.markdown("---")
                    
                    st.markdown('<h3 class="sub-section-header">Top Critical Recommendations</h3>', unsafe_allow_html=True)
                    critical_recs = [r for r in score.recommendations if r.priority.value == "critical"]
                    if critical_recs:
                        for i, rec in enumerate(critical_recs[:3]):
                            st.error(f"**{i+1}. {rec.title}** (Category: {rec.category.replace('_', ' ').title()})")
                            st.write(rec.description)
                            if i < len(critical_recs[:3]) - 1: st.markdown("---")
                        if len(critical_recs) > 3:
                            st.info(f"And {len(critical_recs) - 3} more critical recommendations. See 'Recommendations' tab for full list.")
                    else:
                        st.success("🎉 No critical issues identified! Your site is performing well.")
                    
                    st.markdown("---")
                    
                    st.markdown('<h3 class="sub-section-header">Key Observations</h3>', unsafe_allow_html=True)
                    
                    if st.session_state.comparison and st.session_state.comparison.javascript_dependent:
                        st.warning("⚠️ **JavaScript Dependency Detected:** A significant portion of your content loads dynamically via JavaScript, potentially limiting static scrapers and basic LLMs.")
                    elif st.session_state.ssr_detection and st.session_state.ssr_detection.is_ssr:
                        st.success("✅ **Server-Side Rendering (SSR) in Use:** Your site appears to leverage SSR, which is excellent for scraper and LLM accessibility.")
                    else:
                        st.info("ℹ️ No major JavaScript dependency issues or SSR detection noted. Further details in respective tabs.")
                
                else:
                    st.info("Please run a **'Comprehensive Analysis'** to generate a full Executive Summary. Currently showing results for: **" + st.session_state.last_analysis_type + "**")
            
            else:
                st.info("No URL analyzed yet. Please enter a URL in the sidebar and click 'Start Analysis'.")
        
        with tabs[2]:  # Overview
            st.markdown('<h2 class="section-header">📊 Detailed Analysis Breakdown</h2>', unsafe_allow_html=True)
            
            # Debug information
            with st.expander("🔍 Debug Info (click to expand)", expanded=False):
                st.write("comparison_enabled:", st.session_state.comparison_enabled)
                st.write("comparison_url:", st.session_state.comparison_url)
                st.write("comparison_results exists:", st.session_state.comparison_results is not None)
                if st.session_state.comparison_results:
                    st.write("comparison_results type:", type(st.session_state.comparison_results).__name__)
            
            if not st.session_state.comparison_enabled:
                st.info("✨ **Enable website comparison in the sidebar** to compare two websites side-by-side!")
            elif not st.session_state.comparison_url:
                st.info("📝 **Enter a comparison URL in the sidebar** to start the comparison.")
            elif not st.session_state.comparison_results:
                st.info("▶️ **Click 'Analyze Website' button** to run the comparison analysis.")
            else:
                # We have comparison results - display them!
                comparison = st.session_state.comparison_results
                
                # URLs being compared
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; margin-bottom: 1.5rem;">
                    <h3 style="color: white; margin: 0 0 1rem 0;">Comparing:</h3>
                    <p style="color: white; margin: 0.5rem 0;"><strong>URL 1:</strong> <code>{comparison.url1}</code></p>
                    <p style="color: white; margin: 0.5rem 0;"><strong>URL 2:</strong> <code>{comparison.url2}</code></p>
                </div>
                """, unsafe_allow_html=True)
            
                # Overall similarity score
                st.metric(
                    "🎯 Overall Similarity",
                    f"{comparison.overall_similarity_score:.1f}%",
                    help="How similar the two websites are across all dimensions"
                )
                
                # Score Breakdown
                st.markdown('<h3 class="sub-section-header">📊 Similarity Score Breakdown</h3>', unsafe_allow_html=True)
                st.markdown("""
                The overall similarity score is calculated from three main components:
                1. **Content Similarity (40%)**: Text content and HTML structure
                2. **Accessibility (30%)**: LLM and scraper friendliness scores
                3. **Technical (30%)**: JavaScript, meta tags, and structured data
                """)
            
                # Add calculation methodology display
                with st.expander("🧮 Detailed Calculation Methodology", expanded=True):
                    st.markdown("""
                    ### Formula
                    ```
                    Overall Similarity = (Content × 40%) + (Accessibility × 30%) + (Technical × 30%)
                
                    Where:
                      Content = (Text Similarity × 60%) + (Structure Similarity × 40%)
                      Accessibility = 100% - |LLM Score Diff| - |Scraper Score Diff|
                      Technical = 100% - (Number of Key Differences × 10 points each)
                    ```
                    """)
                
                    # Show actual calculation
                    st.markdown("### Your Calculation:")
                
                    # Content calculation
                    text_sim = comparison.content_comparison.text_similarity_score
                    struct_sim = comparison.content_comparison.structure_similarity_score
                    content_calc = text_sim * 0.6 + struct_sim * 0.4
                    st.write(f"**Content:** ({text_sim:.1f}% × 0.6) + ({struct_sim:.1f}% × 0.4) = {content_calc:.1f}%")
                    st.write(f"  → Contribution: {content_calc:.1f}% × 0.4 = **{content_calc * 0.4:.1f}%**")
                
                    # Accessibility calculation
                    llm_diff = abs(comparison.accessibility_comparison.llm_score_diff) if comparison.accessibility_comparison.llm_score_diff else 0
                    scraper_diff = abs(comparison.accessibility_comparison.scraper_score_diff) if comparison.accessibility_comparison.scraper_score_diff else 0
                    access_calc = max(0.0, 100.0 - llm_diff - scraper_diff)
                    st.write(f"**Accessibility:** 100% - {llm_diff:.1f} - {scraper_diff:.1f} = {access_calc:.1f}%")
                    st.write(f"  → Contribution: {access_calc:.1f}% × 0.3 = **{access_calc * 0.3:.1f}%**")
                
                    # Technical calculation
                    tech_diffs = len(comparison.technical_comparison.key_differences)
                    tech_calc = max(0.0, 100.0 - (tech_diffs * 10))
                    st.write(f"**Technical:** 100% - ({tech_diffs} differences × 10) = {tech_calc:.1f}%")
                    st.write(f"  → Contribution: {tech_calc:.1f}% × 0.3 = **{tech_calc * 0.3:.1f}%**")
                
                    # Final total
                    final_total = (content_calc * 0.4) + (access_calc * 0.3) + (tech_calc * 0.3)
                    st.markdown(f"""
                    ---
                    **Final Overall Similarity:** {content_calc * 0.4:.1f}% + {access_calc * 0.3:.1f}% + {tech_calc * 0.3:.1f}% = **{final_total:.1f}%**
                    """)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    content_score = (
                        comparison.content_comparison.text_similarity_score * 0.6 +
                        comparison.content_comparison.structure_similarity_score * 0.4
                    ) * 0.4
                    st.metric(
                        "Content Score",
                        f"{content_score:.1f}%",
                        help="40% weight: Text similarity (60%) + Structure similarity (40%)"
                    )
                with col2:
                    accessibility_score = 100.0
                    if comparison.accessibility_comparison.llm_score_diff:
                        accessibility_score -= abs(comparison.accessibility_comparison.llm_score_diff)
                    if comparison.accessibility_comparison.scraper_score_diff:
                        accessibility_score -= abs(comparison.accessibility_comparison.scraper_score_diff)
                    accessibility_score = max(0.0, accessibility_score) * 0.3
                    st.metric(
                        "Accessibility Score",
                        f"{accessibility_score:.1f}%",
                        help="30% weight: Based on LLM and scraper score differences"
                    )
                with col3:
                    technical_score = (100.0 - len(comparison.technical_comparison.key_differences) * 10) * 0.3
                    technical_score = max(0.0, technical_score)
                    st.metric(
                        "Technical Score",
                        f"{technical_score:.1f}%",
                        help="30% weight: Based on technical differences found"
                    )
                
                st.markdown("---")
            
                # Key insights
                st.markdown('<h3 class="sub-section-header">🔍 Key Insights</h3>', unsafe_allow_html=True)
                for insight in comparison.key_insights:
                    if insight.startswith("Content differences:"):
                        st.markdown(f"**{insight}**")
                    elif insight.startswith("Accessibility differences:"):
                        st.markdown(f"**{insight}**")
                    elif insight.startswith("Technical differences:"):
                        st.markdown(f"**{insight}**")
                    else:
                        st.write(insight)
                
                st.markdown("---")
            
                # Content comparison
                st.markdown('<h3 class="sub-section-header">📝 Content Comparison</h3>', unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        "Text Similarity",
                        f"{comparison.content_comparison.text_similarity_score:.1f}%",
                        help="How similar the text content is between the two sites"
                    )
                with col2:
                    st.metric(
                        "Structure Similarity",
                        f"{comparison.content_comparison.structure_similarity_score:.1f}%",
                        help="How similar the HTML structure is between the two sites"
                    )
                with col3:
                    word_diff = comparison.content_comparison.word_count_diff
                    st.metric(
                        "Word Count Difference",
                        f"{abs(word_diff):,}",
                        f"{'More' if word_diff > 0 else 'Fewer'} words in second site",
                        help="Difference in total word count between the two sites"
                    )

                # Content details
                col1, col2 = st.columns(2)
                with col1:
                    st.write("Element Differences:")
                    st.write(f"• Links: {abs(comparison.content_comparison.links_diff)} {'more' if comparison.content_comparison.links_diff > 0 else 'fewer'}")
                    st.write(f"• Images: {abs(comparison.content_comparison.images_diff)} {'more' if comparison.content_comparison.images_diff > 0 else 'fewer'}")
                with col2:
                    st.write(f"• Tables: {abs(comparison.content_comparison.tables_diff)} {'more' if comparison.content_comparison.tables_diff > 0 else 'fewer'}")
                    st.write(f"• Lists: {abs(comparison.content_comparison.lists_diff)} {'more' if comparison.content_comparison.lists_diff > 0 else 'fewer'}")

                st.markdown("---")

                # Accessibility comparison
                st.markdown('<h3 class="sub-section-header">♿ Accessibility Comparison</h3>', unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    llm_diff = comparison.accessibility_comparison.llm_score_diff
                    st.metric(
                        "LLM Score Difference",
                        f"{abs(llm_diff):.1f}",
                        f"{'Better' if llm_diff > 0 else 'Worse'} in second site",
                        help="Difference in LLM accessibility scores"
                    )
                with col2:
                    scraper_diff = comparison.accessibility_comparison.scraper_score_diff
                    st.metric(
                        "Scraper Score Difference",
                        f"{abs(scraper_diff):.1f}",
                        f"{'Better' if scraper_diff > 0 else 'Worse'} in second site",
                        help="Difference in scraper friendliness scores"
                    )

                st.info(comparison.accessibility_comparison.ssr_comparison)

                if comparison.accessibility_comparison.bot_directives_comparison:
                    with st.expander("🤖 Bot Directives Comparison"):
                        bot_diff = comparison.accessibility_comparison.bot_directives_comparison

                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("First Site:")
                            st.write(f"• robots.txt: {'Present' if bot_diff['robots_txt_present'][0] else 'Missing'}")
                            st.write(f"• llms.txt: {'Present' if bot_diff['llms_txt_present'][0] else 'Missing'}")
                        with col2:
                            st.write("Second Site:")
                            st.write(f"• robots.txt: {'Present' if bot_diff['robots_txt_present'][1] else 'Missing'}")
                            st.write(f"• llms.txt: {'Present' if bot_diff['llms_txt_present'][1] else 'Missing'}")

                        compat_diff = bot_diff.get('compatibility_score_diff', 0)
                        st.metric(
                            "Compatibility Score Difference",
                            f"{abs(compat_diff):.1f}",
                            f"{'Better' if compat_diff > 0 else 'Worse'} in second site"
                        )

                st.markdown("---")

                # Technical comparison
                st.markdown('<h3 class="sub-section-header">⚙️ Technical Comparison</h3>', unsafe_allow_html=True)

                js_diff = comparison.technical_comparison.js_usage_diff
                meta_diff = comparison.technical_comparison.meta_tags_diff
                struct_diff = comparison.technical_comparison.structured_data_diff

                col1, col2 = st.columns(2)
                with col1:
                    st.write("JavaScript Usage:")
                    st.write(f"• Scripts: {abs(js_diff['total_scripts_diff'])} {'more' if js_diff['total_scripts_diff'] > 0 else 'fewer'} in second site")
                    if js_diff['frameworks']:
                        st.write("• Additional frameworks in second site:", ", ".join(js_diff['frameworks']))
                    if js_diff['spa_difference']:
                        st.write("• Different application architecture")
                    if js_diff['dynamic_content_difference']:
                        st.write("• Different dynamic content handling")

                with col2:
                    st.write("Meta Tags & SEO:")
                    st.write(f"• Open Graph tags: {abs(meta_diff['og_tags_diff'])} {'more' if meta_diff['og_tags_diff'] > 0 else 'fewer'} in second site")
                    st.write(f"• Twitter Card tags: {abs(meta_diff['twitter_tags_diff'])} {'more' if meta_diff['twitter_tags_diff'] > 0 else 'fewer'} in second site")

                    total_struct_diff = (
                        struct_diff['json_ld_diff'] +
                        struct_diff['microdata_diff'] +
                        struct_diff['rdfa_diff']
                    )
                    if total_struct_diff != 0:
                        st.write(f"• Structured data: {abs(total_struct_diff)} {'more' if total_struct_diff > 0 else 'fewer'} items in second site")

                st.markdown("---")

                # Recommendations
                if comparison.recommendations:
                    st.markdown('<h3 class="sub-section-header">💡 Recommendations</h3>', unsafe_allow_html=True)
                    for rec in comparison.recommendations:
                        st.info(f"• {rec}")
        
        with tabs[3]:  # LLM Analysis
            st.markdown('<h2 class="section-header">🤖 LLM Accessibility Analysis</h2>', unsafe_allow_html=True)
            
            if st.session_state.llm_report:
                llm_report = st.session_state.llm_report
                
                # Add methodology explanation
                with st.expander("📋 Analysis Methodology - How We Determined LLM Access", expanded=False):
                    st.markdown("""
                    ### Our Testing Process:
                    
                    **1. Static HTML Fetch (Simulating LLM Crawlers)**
                    - We fetch your website using user agents similar to ChatGPT, Claude, and other LLM crawlers
                    - This request gets ONLY the initial HTML - no JavaScript execution
                    - Similar to how search engines and AI systems read web pages
                    
                    **2. Content Extraction**
                    - Parse all text content from HTML tags
                    - Extract meta tags (title, description, Open Graph)
                    - Identify structured data (JSON-LD, Microdata, RDFa)
                    - Map semantic HTML structure (headers, nav, main, article)
                    
                    **3. JavaScript Analysis**
                    - Detect single-page applications (React, Vue, Angular)
                    - Identify AJAX/fetch requests that load content dynamically
                    - Find CSS-hidden elements (display:none, visibility:hidden)
                    - Locate content requiring user interaction
                    
                    **4. Scoring**
                    - Weight each factor based on LLM accessibility impact
                    - Compare against best practices and industry standards
                    - Generate specific recommendations for improvement
                    
                    **Result:** The scores and findings below are based on what LLMs can ACTUALLY access when they fetch your page, not assumptions.
                    """)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("LLM Accessibility Score", f"{llm_report.overall_score:.1f}/100",
                             delta=f"Grade: {llm_report.grade}",
                             help="Based on analysis of static HTML content, semantic structure, and JavaScript dependencies")
                with col2:
                    st.metric("Accessible Content Categories", f"{len(llm_report.accessible_content)}",
                             help="Types of content LLMs can successfully read without JavaScript execution")
                with col3:
                    st.metric("Limitations Found", f"{len(llm_report.limitations)}",
                             help="Specific issues preventing LLMs from accessing your full content")
                
                st.markdown("---")
                
                st.markdown('<h3 class="sub-section-header">✅ What LLMs CAN Access</h3>', unsafe_allow_html=True)
                
                accessible = llm_report.accessible_content
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📝 Text Content**")
                    st.info(f"**{accessible['text_content']['character_count']:,} characters** ({accessible['text_content']['word_count']:,} words)")
                    st.markdown(f"*{accessible['text_content']['explanation']}*")
                    
                    st.markdown("**🏗️ Semantic Structure**")
                    st.info(f"**{len(accessible['semantic_structure']['semantic_elements'])} semantic elements** detected")
                    st.markdown(f"*{accessible['semantic_structure']['explanation']}*")
                
                with col2:
                    st.markdown("**🏷️ Meta Information**")
                    meta_info = accessible['meta_information']
                    st.info(f"Title: {'✅' if meta_info['title'] else '❌'} | Description: {'✅' if meta_info['description'] else '❌'}")
                    st.markdown(f"*{meta_info['explanation']}*")
                    
                    st.markdown("**📊 Structured Data**")
                    struct_data = accessible['structured_data']
                    total_items = len(struct_data['json_ld']) + len(struct_data['microdata']) + len(struct_data['rdfa'])
                    st.info(f"**{total_items} structured data items** found")
                    st.markdown(f"*{struct_data['explanation']}*")
                
                st.markdown("---")
                
                st.markdown('<h3 class="sub-section-header">❌ What LLMs CANNOT Access</h3>', unsafe_allow_html=True)
                
                inaccessible = llm_report.inaccessible_content
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**⚡ JavaScript-Dependent Content**")
                    js_content = inaccessible['javascript_dependent_content']
                    if js_content['dynamic_content']:
                        st.error("🚨 Dynamic content detected - LLMs typically cannot execute JavaScript in static analysis.")
                        st.markdown(f"**Scripts detected:** {js_content['total_scripts']}")
                        if js_content["frameworks_detected"]:
                            st.markdown(f"**Frameworks:** {', '.join(js_content['frameworks_detected'])}")
                    if js_content['ajax_content']:
                        st.error("🚨 AJAX content detected - Not accessible to LLMs without dynamic rendering.")
                    if js_content['spa_content']:
                        st.error("🚨 Single Page Application detected - Requires JavaScript for full content.")
                    
                    st.markdown(f"*{js_content['explanation']}*")
                    
                    st.markdown("**👁️ CSS-Hidden Content**")
                    hidden_content = inaccessible['css_hidden_content']
                    if hidden_content['hidden_elements']:
                        st.warning(f"⚠️ {len(hidden_content['hidden_elements'])} elements detected as hidden by CSS.")
                    st.markdown(f"*{hidden_content['explanation']}*")
                
                with col2:
                    st.markdown("**🎮 Interactive Elements**")
                    interactive = inaccessible['interactive_elements']
                    st.info(f"Forms: {interactive['forms']} | Buttons: {interactive['buttons']}")
                    st.markdown(f"*{interactive['explanation']}*")
                    
                    st.markdown("**📱 Media Content**")
                    media = inaccessible['media_content']
                    st.info(f"Images: {media['images']} | Videos: {media['videos']} | Audio: {media['audio']}")
                    st.markdown(f"*{media['explanation']}*")
                
                st.markdown("---")
                
                st.markdown('<h3 class="sub-section-header">⚠️ Specific Limitations Identified</h3>', unsafe_allow_html=True)
                
                if llm_report.limitations:
                    for i, limitation in enumerate(llm_report.limitations, 1):
                        st.error(f"**{i}.** {limitation}")
                else:
                    st.success("🎉 No major limitations identified!")
                
                st.markdown("---")
                
                st.markdown('<h3 class="sub-section-header">💡 Recommendations for Better LLM Access</h3>', unsafe_allow_html=True)
                
                if llm_report.recommendations:
                    for i, rec in enumerate(llm_report.recommendations, 1):
                        if rec.startswith("CRITICAL"):
                            st.error(f"**{i}.** {rec}")
                        elif rec.startswith("HIGH"):
                            st.warning(f"**{i}.** {rec}")
                        else:
                            st.info(f"**{i}.** {rec}")
                else:
                    st.success("🎉 No recommendations needed - your site is LLM-friendly!")
            else:
                st.info("LLM analysis not available. Please run the analysis first with **'Comprehensive Analysis'** or **'LLM Accessibility Only'**.")
        
        with tabs[4]:  # LLM Visibility
            st.markdown('<h2 class="section-header">👁️ LLM Content Visibility</h2>', unsafe_allow_html=True)
            
            st.markdown("""
            <div style="background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 20px; margin: 20px 0;">
                <h4 style="color: #495057; margin-bottom: 15px;">🔍 See Exactly What LLMs See</h4>
                <p style="color: #6c757d; margin-bottom: 10px;">This section shows the raw content that Large Language Models receive when they fetch your website.</p>
                <p style="color: #6c757d; margin-bottom: 0;">No formatting, no summaries - exactly as LLMs see it.</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.session_state.url:
                # Add LLM Visibility Analysis
                with st.spinner("Analyzing LLM content visibility..."):
                    try:
                        with LLMContentViewer() as viewer:
                            visibility_analysis = viewer.analyze_llm_visibility(st.session_state.url)
                            
                            # Display visibility score
                            score = visibility_analysis.visibility_score
                            if score >= 80:
                                score_color = "#28a745"
                                grade = "Excellent"
                            elif score >= 60:
                                score_color = "#17a2b8"
                                grade = "Good"
                            elif score >= 40:
                                score_color = "#ffc107"
                                grade = "Fair"
                            else:
                                score_color = "#dc3545"
                                grade = "Poor"
                            
                            st.markdown(f"""
                            <div style="text-align: center; background-color: {score_color}20; border: 2px solid {score_color}; border-radius: 8px; padding: 20px; margin: 20px 0;">
                                <h3 style="color: {score_color}; margin-bottom: 10px;">LLM Visibility Score: {score:.1f}/100</h3>
                                <p style="color: {score_color}; font-size: 1.2rem; margin: 0;">Grade: {grade}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Content breakdown
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.subheader("📄 Raw Content (What LLMs See)")
                                st.markdown("""
                                <div style="background-color: #ffffff; border: 1px solid #ced4da; border-radius: 4px; padding: 15px; font-family: 'Courier New', monospace; font-size: 14px; line-height: 1.4; max-height: 400px; overflow-y: auto; white-space: pre-wrap; word-wrap: break-word;">
                                """, unsafe_allow_html=True)
                                
                                # Show first 1000 characters of raw content
                                preview_content = visibility_analysis.llm_visible_content[:1000]
                                if len(visibility_analysis.llm_visible_content) > 1000:
                                    preview_content += "\n\n... (content truncated, download full content below)"
                                
                                st.text(preview_content)
                                st.markdown("</div>", unsafe_allow_html=True)
                                
                                # Download button
                                st.download_button(
                                    label="📥 Download Full Raw Content",
                                    data=visibility_analysis.llm_visible_content,
                                    file_name=f"llm_content_{int(time.time())}.txt",
                                    mime="text/plain"
                                )
                            
                            with col2:
                                st.subheader("📊 Content Analysis")
                                
                                visible = visibility_analysis.content_breakdown
                                st.metric("Total Characters", f"{visible['total_content']:,}")
                                st.metric("Visibility Percentage", f"{visible['visible_percentage']}%")
                                st.metric("Content Type", visible['content_type'].title())
                                
                                st.subheader("❌ Hidden Content Issues")
                                hidden = visibility_analysis.hidden_content_summary
                                
                                for issue, status in hidden.items():
                                    if status:
                                        st.error(f"⚠️ {issue.replace('_', ' ').title()}")
                                    else:
                                        st.success(f"✅ {issue.replace('_', ' ').title()}")
                            
                            # Recommendations
                            st.subheader("🎯 LLM Visibility Recommendations")
                            
                            for recommendation in visibility_analysis.recommendations:
                                if "CRITICAL" in recommendation:
                                    st.error(f"🚨 **{recommendation}**")
                                elif "HIGH" in recommendation:
                                    st.warning(f"⚠️ **{recommendation}**")
                                else:
                                    st.info(f"💡 **{recommendation}**")
                            
                            # Evidence-based insights
                            st.subheader("🔍 How We Determined What LLMs Can See")
                            
                            st.markdown("**Analysis Method:**")
                            st.info("""
                            We simulated how LLMs fetch and parse web pages by:
                            1. Making HTTP requests with LLM-like user agents (similar to ChatGPT, Claude)
                            2. Parsing the initial HTML response WITHOUT executing JavaScript
                            3. Extracting all text, meta tags, and structured data
                            4. Measuring what's immediately available vs. what requires JavaScript
                            """)
                            
                            st.markdown("**Evidence from Your Website:**")
                            
                            col_ev1, col_ev2 = st.columns(2)
                            
                            with col_ev1:
                                st.markdown("✅ **What We Found Accessible:**")
                                if st.session_state.static_result:
                                    static = st.session_state.static_result
                                    st.success(f"📝 **{static.content_analysis.word_count:,} words** of text in initial HTML")
                                    st.success(f"🏗️ **{len(static.semantic_structure.semantic_tags)} semantic elements** (header, nav, article, etc.)")
                                    st.success(f"🏷️ **Title tag**: {'Present' if static.meta_tags.title else 'Missing'}")
                                    st.success(f"📊 **{len(static.structured_data.json_ld)} JSON-LD schemas** providing context")
                                    st.success(f"🔗 **{len(static.content_analysis.all_links)} links** for discovery")
                            
                            with col_ev2:
                                st.markdown("❌ **What We Found Inaccessible:**")
                                if st.session_state.static_result:
                                    static = st.session_state.static_result
                                    js_analysis = static.javascript_analysis
                                    
                                    if js_analysis.is_spa:
                                        st.error(f"⚠️ **Single Page Application** detected - content requires JavaScript execution")
                                    if js_analysis.total_scripts > 0:
                                        st.warning(f"⚡ **{js_analysis.total_scripts} JavaScript files** - may hide dynamic content")
                                    if js_analysis.frameworks_detected:
                                        st.warning(f"🎨 **Frameworks**: {', '.join(js_analysis.frameworks_detected[:3])}")
                                    if js_analysis.ajax_indicators:
                                        st.error(f"🔄 **AJAX content** detected - won't load for LLMs")
                                    
                                    if not (js_analysis.is_spa or js_analysis.ajax_indicators):
                                        st.success("✅ No major JavaScript-dependent content detected!")
                            
                            st.markdown("---")
                            st.markdown("**Conclusion:**")
                            if st.session_state.static_result:
                                static = st.session_state.static_result
                                content_ratio = (static.content_analysis.word_count / max(static.content_analysis.word_count + 500, 1)) * 100
                                
                                if content_ratio > 80 and not static.javascript_analysis.is_spa:
                                    st.success(f"🎉 **{content_ratio:.0f}%** of your content is LLM-accessible! Your site is well-optimized for LLMs.")
                                elif content_ratio > 50:
                                    st.info(f"✅ **{content_ratio:.0f}%** of content is LLM-accessible. Consider reducing JavaScript dependency for better coverage.")
                                else:
                                    st.warning(f"⚠️ Only **~{content_ratio:.0f}%** of content is immediately LLM-accessible. Consider implementing SSR or static HTML fallbacks.")
                            
                            # Search Simulation Section
                            st.markdown("---")
                            st.subheader("🔍 Search Simulation")
                            st.markdown("**See how your content appears in LLM search results:**")
                            
                            # Search query input
                            search_query = st.text_input(
                                "Enter search query",
                                placeholder="mortgage rates",
                                help="Enter terms that users might search for to find your content"
                            )
                            
                            if search_query:
                                with st.spinner("Simulating LLM search results..."):
                                    search_results = viewer.simulate_llm_search(search_query)
                                
                                st.markdown("**Search Results (What LLMs See):**")
                                
                                for i, result in enumerate(search_results, 1):
                                    with st.container():
                                        st.markdown(f"""
                                        <div style="background-color: #ffffff; border: 1px solid #e9ecef; border-radius: 6px; padding: 15px; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                            <div style="font-size: 1.1rem; font-weight: bold; color: #1a73e8; margin-bottom: 5px;">{result.title}</div>
                                            <div style="font-size: 0.9rem; color: #5f6368; margin-bottom: 8px;">{result.url}</div>
                                            <div style="font-size: 0.95rem; line-height: 1.4; color: #3c4043;">{result.snippet}</div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                        
                                        # Show relevance score
                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            st.metric("Relevance", f"{result.relevance_score:.2f}")
                                        with col2:
                                            st.metric("Source", result.source)
                                        with col3:
                                            st.metric("Result #", i)
                                        
                                        st.divider()
                                
                                # Search insights
                                st.subheader("🔍 Search Insights")
                                st.info(f"""
                                **What LLMs see in search results:**
                                - **Titles:** {len(search_results)} result titles
                                - **Snippets:** Brief content summaries
                                - **URLs:** Direct links to pages
                                - **Relevance:** How well results match the query
                                
                                **Key Points:**
                                - LLMs use these snippets to understand content before visiting pages
                                - Snippet quality affects whether LLMs will fetch the full page
                                - Titles and descriptions are crucial for search visibility
                                """)
                            
                    except Exception as e:
                        st.error(f"Error analyzing LLM visibility: {str(e)}")
                        st.info("Please ensure the URL is accessible and try again.")
            else:
                st.info("Please enter a URL and run the analysis to see LLM content visibility.")
        
        with tabs[5]:  # Recommendations
            st.markdown('<h2 class="section-header">💡 Optimization Recommendations</h2>', unsafe_allow_html=True)
            
            if st.session_state.score and st.session_state.score.recommendations:
                st.markdown("### 📋 Analysis Summary")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Recommendations", len(st.session_state.score.recommendations))
                with col2:
                    critical_count = sum(1 for r in st.session_state.score.recommendations if r.priority.value == "critical")
                    st.metric("Critical Issues", critical_count, delta="High priority", delta_color="inverse" if critical_count > 0 else "off")
                with col3:
                    high_count = sum(1 for r in st.session_state.score.recommendations if r.priority.value == "high")
                    st.metric("High Priority", high_count)
                
                st.markdown("---")
                
                # Group by priority
                critical_recs = [r for r in st.session_state.score.recommendations if r.priority.value == "critical"]
                high_recs = [r for r in st.session_state.score.recommendations if r.priority.value == "high"]
                medium_recs = [r for r in st.session_state.score.recommendations if r.priority.value == "medium"]
                
                # Critical Issues
                if critical_recs:
                    st.markdown('<h3 class="sub-section-header">🚨 Critical Issues</h3>', unsafe_allow_html=True)
                    for i, rec in enumerate(critical_recs, 1):
                        with st.expander(f"CRITICAL: {rec.title}", expanded=True):
                            st.markdown(f"**Issue:** {rec.description}")
                            st.markdown(f"**Category:** `{rec.category}`")
                            if rec.code_example:
                                st.markdown("**💻 Code Example:**")
                                st.code(rec.code_example, language="html")
                            st.markdown("---")
                            st.markdown(f"**Impact on Scraper Friendliness:** {rec.impact.scraper_friendliness}")
                            st.markdown(f"**Impact on LLM Accessibility:** {rec.impact.llm_accessibility}")
                
                # High Priority
                if high_recs:
                    st.markdown('<h3 class="sub-section-header">⚠️ High Priority</h3>', unsafe_allow_html=True)
                    for i, rec in enumerate(high_recs, 1):
                        with st.expander(f"HIGH: {rec.title}"):
                            st.markdown(f"**Issue:** {rec.description}")
                            st.markdown(f"**Category:** `{rec.category}`")
                            if rec.code_example:
                                st.markdown("**💻 Code Example:**")
                                st.code(rec.code_example, language="html")
                            st.markdown("---")
                            st.markdown(f"**Impact on Scraper Friendliness:** {rec.impact.scraper_friendliness}")
                            st.markdown(f"**Impact on LLM Accessibility:** {rec.impact.llm_accessibility}")
                
                # Medium Priority
                if medium_recs:
                    st.markdown('<h3 class="sub-section-header">📝 Medium Priority</h3>', unsafe_allow_html=True)
                    for i, rec in enumerate(medium_recs, 1):
                        with st.expander(f"MEDIUM: {rec.title}"):
                            st.markdown(f"**Issue:** {rec.description}")
                            st.markdown(f"**Category:** `{rec.category}`")
                            if rec.code_example:
                                st.markdown("**💻 Code Example:**")
                                st.code(rec.code_example, language="html")
                            st.markdown("---")
                            st.markdown(f"**Impact on Scraper Friendliness:** {rec.impact.scraper_friendliness}")
                            st.markdown(f"**Impact on LLM Accessibility:** {rec.impact.llm_accessibility}")
            else:
                st.info("**'Recommendations' tab is populated only after a 'Comprehensive Analysis'.** Please select this option from the sidebar.")
                if st.session_state.last_analysis_type:
                    st.markdown(f"Currently showing results for: **{st.session_state.last_analysis_type}**")
        
        with tabs[6]:  # Enhanced LLM Analysis
            st.markdown('<h2 class="section-header">🔬 Enhanced LLM Analysis</h2>', unsafe_allow_html=True)
            
            if st.session_state.enhanced_llm_report:
                report = st.session_state.enhanced_llm_report
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Enhanced LLM Score", f"{report.overall_score:.1f}/100", 
                             delta=f"Grade: {report.grade}")
                with col2:
                    st.metric("Crawler Capabilities", f"{len(report.crawler_analysis)}")
                with col3:
                    st.metric("Technical Issues", f"{len(report.technical_explanations)}")
                
                st.markdown("---")
                
                st.markdown('<h3 class="sub-section-header">🤖 LLM Crawler Capabilities</h3>', unsafe_allow_html=True)
                
                for crawler_name, capability in report.crawler_analysis.items():
                    with st.expander(f"**{capability.name}**"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Capabilities:**")
                            st.write(f"• JavaScript Execution: {'✅' if capability.executes_javascript else '❌'}")
                            st.write(f"• Headless Browser: {'✅' if capability.uses_headless_browser else '❌'}")
                            st.write(f"• Real-time Access: {'✅' if capability.real_time_access else '❌'}")
                        
                        with col2:
                            st.markdown("**Strategy:**")
                            st.write(f"• Chunking: {capability.chunking_strategy}")
                            st.write(f"• Vectorization: {capability.vectorization_quality}")
                            st.write(f"• Schema Preference: {capability.schema_preference}")
                        
                        if capability.limitations:
                            st.markdown("**Limitations:**")
                            for limitation in capability.limitations:
                                st.write(f"• {limitation}")
                
                st.markdown("---")
                
                st.markdown('<h3 class="sub-section-header">📊 Technical Analysis</h3>', unsafe_allow_html=True)
                
                for category, explanation in report.technical_explanations.items():
                    st.markdown(f"**{category.replace('_', ' ').title()}:**")
                    st.write(explanation)
                    st.markdown("---")
            else:
                st.info("Enhanced LLM analysis not available. Please run a 'Comprehensive Analysis' or 'LLM Accessibility Only'.")
        
        with tabs[7]:  # Bot Directives Analysis
            st.markdown('<h2 class="section-header">📄 Bot Directives Analysis</h2>', unsafe_allow_html=True)
            
            if st.session_state.bot_directives:
                analysis = st.session_state.bot_directives
                
                # Overall metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Compatibility Score", f"{analysis.compatibility_score:.1f}/100")
                with col2:
                    st.metric("robots.txt", "✅ Present" if analysis.robots_txt.is_present else "❌ Missing")
                with col3:
                    st.metric("llms.txt", "✅ Present" if analysis.llms_txt.is_present else "❌ Missing")
                
                st.markdown("---")
                
                # robots.txt Analysis
                st.markdown('<h3 class="sub-section-header">🤖 robots.txt Analysis</h3>', unsafe_allow_html=True)
                
                if analysis.robots_txt.is_present:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("User Agents", len(analysis.robots_txt.user_agents))
                    with col2:
                        st.metric("Disallowed Paths", len(analysis.robots_txt.disallowed_paths))
                    with col3:
                        st.metric("Sitemaps", len(analysis.robots_txt.sitemaps))
                    
                    with st.expander("📄 View robots.txt Content"):
                        st.code(analysis.robots_txt.content, language="text")
                    
                    if analysis.robots_txt.user_agents:
                        with st.expander("🤖 User Agents"):
                            for agent in analysis.robots_txt.user_agents:
                                st.write(f"• {agent}")
                    
                    if analysis.robots_txt.disallowed_paths:
                        with st.expander("🚫 Disallowed Paths"):
                            for path in analysis.robots_txt.disallowed_paths:
                                st.write(f"• {path}")
                    
                    if analysis.robots_txt.allowed_paths:
                        with st.expander("✅ Allowed Paths"):
                            for path in analysis.robots_txt.allowed_paths:
                                st.write(f"• {path}")
                    
                    if analysis.robots_txt.sitemaps:
                        with st.expander("🗺️ Sitemaps"):
                            for sitemap in analysis.robots_txt.sitemaps:
                                st.write(f"• {sitemap}")
                    
                    if analysis.robots_txt.crawl_delay:
                        st.info(f"⏱️ Crawl Delay: {analysis.robots_txt.crawl_delay} seconds")
                else:
                    st.warning("No robots.txt file found at the website root.")
                    st.info("robots.txt is essential for guiding web crawlers on what content they can and cannot access.")
                
                st.markdown("---")
                
                # llms.txt Analysis
                st.markdown('<h3 class="sub-section-header">🤖 llms.txt Analysis</h3>', unsafe_allow_html=True)
                
                if analysis.llms_txt.is_present:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Quality Score", f"{analysis.llms_txt.quality_score:.1f}/100")
                    with col2:
                        st.metric("Format Valid", "✅ Yes" if analysis.llms_txt.format_valid else "❌ No")
                    
                    with st.expander("📄 View llms.txt Content"):
                        st.code(analysis.llms_txt.content, language="markdown")
                    
                    if analysis.llms_txt.sections:
                        st.markdown('<h4 class="sub-section-header">📋 Sections Found</h4>', unsafe_allow_html=True)
                        for section_name, section_content in analysis.llms_txt.sections.items():
                            with st.expander(f"📝 {section_name}"):
                                for line in section_content:
                                    st.write(f"• {line}")
                    
                    if analysis.llms_txt.benefits:
                        with st.expander("✅ Benefits"):
                            for benefit in analysis.llms_txt.benefits:
                                st.write(f"• {benefit}")
                else:
                    st.warning("No llms.txt file found at the website root.")
                    st.info("**What is llms.txt?** It's a new standard (2024-2025) for guiding AI crawlers to quality content, different from robots.txt which focuses on exclusion.")
                
                st.markdown("---")
                
                # Combined Analysis
                st.markdown('<h3 class="sub-section-header">🔄 Combined Analysis</h3>', unsafe_allow_html=True)
                
                if analysis.combined_issues:
                    st.markdown('<h4 class="sub-section-header">⚠️ Issues</h4>', unsafe_allow_html=True)
                    for issue in analysis.combined_issues:
                        st.warning(f"• {issue}")
                
                if analysis.combined_recommendations:
                    st.markdown('<h4 class="sub-section-header">💡 Recommendations</h4>', unsafe_allow_html=True)
                    for rec in analysis.combined_recommendations:
                        st.info(f"• {rec}")
            else:
                st.info("Bot directives analysis not available. Please run a 'Comprehensive Analysis' or 'LLM Accessibility Only'.")
        
        with tabs[8]:  # SSR Detection
            st.markdown('<h2 class="section-header">🔍 Server-Side Rendering (SSR) Detection</h2>', unsafe_allow_html=True)
            
            if st.session_state.ssr_detection:
                ssr = st.session_state.ssr_detection
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("SSR Detected", "✅ Yes" if ssr.is_ssr else "❌ No")
                with col2:
                    st.metric("Confidence", f"{ssr.confidence:.1%}" if hasattr(ssr, 'confidence') else "N/A")
                with col3:
                    st.metric("Rendering Type", ssr.rendering_type if hasattr(ssr, 'rendering_type') else "Unknown")
                
                st.markdown("---")
                
                if hasattr(ssr, 'reasoning') and ssr.reasoning:
                    st.markdown('<h3 class="sub-section-header">🔍 Analysis Reasoning</h3>', unsafe_allow_html=True)
                    st.write(ssr.reasoning)
                
                if hasattr(ssr, 'indicators') and ssr.indicators:
                    st.markdown('<h3 class="sub-section-header">📊 Detection Indicators</h3>', unsafe_allow_html=True)
                    for indicator in ssr.indicators:
                        st.write(f"• {indicator}")
                
                if ssr.is_ssr:
                    st.success("✅ **Your site uses Server-Side Rendering!** This is excellent for web crawlers and LLMs as content is immediately available.")
                else:
                    st.warning("⚠️ **No strong SSR detected.** Consider implementing Server-Side Rendering for better accessibility to crawlers and LLMs.")
                    
                    st.markdown('<h3 class="sub-section-header">💡 SSR Benefits</h3>', unsafe_allow_html=True)
                    st.write("• **Immediate Content Availability**: Content is rendered on the server before sending to browsers")
                    st.write("• **Better SEO**: Search engines can easily crawl and index your content")
                    st.write("• **LLM Accessibility**: AI systems can read your content without executing JavaScript")
                    st.write("• **Faster Initial Load**: Users see content immediately, even on slow connections")
            else:
                st.info("SSR detection not available. Please run a 'Comprehensive Analysis' or 'SSR Detection Only'.")
        
        with tabs[9]:  # Crawler Testing
            st.markdown('<h2 class="section-header">🕷️ Web Crawler Testing</h2>', unsafe_allow_html=True)
            
            if st.session_state.crawler_analysis:
                st.markdown('<h3 class="sub-section-header">🤖 Crawler Analysis Results</h3>', unsafe_allow_html=True)
                
                for crawler_type, result in st.session_state.crawler_analysis.items():
                    with st.expander(f"**{result.crawler_name}** - Score: {result.accessibility_score:.1f}/100"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**✅ Accessible Content:**")
                            for content_type, details in result.content_accessible.items():
                                if isinstance(details, dict) and details.get('available'):
                                    st.write(f"• {content_type}: {details.get('explanation', 'Available')}")
                        
                        with col2:
                            st.markdown("**❌ Inaccessible Content:**")
                            for content_type, details in result.content_inaccessible.items():
                                if isinstance(details, dict) and not details.get('available', True):
                                    st.write(f"• {content_type}: {details.get('explanation', 'Not available')}")
                        
                        if result.evidence:
                            st.markdown("**🔍 Evidence:**")
                            for evidence_item in result.evidence[:5]:  # Show first 5 items
                                st.write(f"• {evidence_item}")
                        
                        if result.recommendations:
                            st.markdown("**💡 Recommendations:**")
                            for rec in result.recommendations[:3]:  # Show first 3 recommendations
                                st.info(f"• {rec}")
            else:
                st.info("Crawler testing not available. Please run a 'Comprehensive Analysis' or 'Web Crawler Testing'.")
        
        with tabs[10]:  # Evidence Report
            st.markdown('<h2 class="section-header">📊 Evidence Report</h2>', unsafe_allow_html=True)
            
            if st.session_state.evidence_report:
                report = st.session_state.evidence_report
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Analysis ID", report.analysis_id[:8] + "...")
                with col2:
                    st.metric("Crawlers Tested", len(report.crawler_comparisons))
                with col3:
                    st.metric("Total Issues", report.summary.get('total_issues', 0))
                
                st.markdown("---")
                
                st.markdown('<h3 class="sub-section-header">📋 Summary</h3>', unsafe_allow_html=True)
                for key, value in report.summary.items():
                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                
                st.markdown("---")
                
                st.markdown('<h3 class="sub-section-header">🔍 Crawler Comparisons</h3>', unsafe_allow_html=True)
                for crawler_type, evidence in report.crawler_comparisons.items():
                    with st.expander(f"**{crawler_type}** Evidence"):
                        st.write(f"**Timestamp:** {evidence.timestamp}")
                        st.write(f"**URL:** {evidence.url}")
                        st.write(f"**Evidence Hash:** {evidence.evidence_hash[:8]}...")
                        
                        st.markdown("**Content Sample:**")
                        st.code(evidence.content_sample[:500] + "..." if len(evidence.content_sample) > 500 else evidence.content_sample)
                        
                        if evidence.accessibility_issues:
                            st.markdown("**Accessibility Issues:**")
                            for issue in evidence.accessibility_issues:
                                st.warning(f"• {issue}")
                        
                        if evidence.recommendations:
                            st.markdown("**Recommendations:**")
                            for rec in evidence.recommendations:
                                st.info(f"• {rec}")
                
                if report.recommendations:
                    st.markdown('<h3 class="sub-section-header">💡 Overall Recommendations</h3>', unsafe_allow_html=True)
                    for rec in report.recommendations:
                        st.info(f"• {rec}")
            else:
                st.info("Evidence report not available. Please run a 'Comprehensive Analysis' or 'Web Crawler Testing'.")
        
        with tabs[11]:  # Content
            st.markdown('<h2 class="section-header">📝 Content Analysis</h2>', unsafe_allow_html=True)
            
            if st.session_state.static_result and st.session_state.static_result.content_analysis:
                content = st.session_state.static_result.content_analysis
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Characters", f"{content.character_count:,}")
                with col2:
                    st.metric("Words", f"{content.word_count:,}")
                with col3:
                    st.metric("Paragraphs", content.paragraphs)
                with col4:
                    st.metric("Estimated Tokens", f"{content.estimated_tokens:,}")
                
                st.markdown("---")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Links", content.links)
                with col2:
                    st.metric("Images", content.images)
                with col3:
                    st.metric("Tables", content.tables)
                with col4:
                    st.metric("Lists", content.lists)
                
                st.markdown("---")
                
                st.markdown('<h3 class="sub-section-header">📄 Text Content Sample</h3>', unsafe_allow_html=True)
                # Show first 1000 characters of text content
                text_sample = content.text_content[:1000] + "..." if len(content.text_content) > 1000 else content.text_content
                st.text_area("Content Preview", text_sample, height=200, disabled=True)
            else:
                st.info("Content analysis not available. Please run a 'Comprehensive Analysis' or 'LLM Accessibility Only'.")
        
        with tabs[12]:  # Structure
            st.markdown('<h2 class="section-header">🏗️ HTML Structure Analysis</h2>', unsafe_allow_html=True)
            
            if st.session_state.static_result and st.session_state.static_result.structure_analysis:
                structure = st.session_state.static_result.structure_analysis
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Elements", structure.total_elements)
                with col2:
                    st.metric("Semantic Elements", len(structure.semantic_elements))
                with col3:
                    st.metric("Nested Depth", structure.nested_depth)
                with col4:
                    st.metric("Proper Structure", "✅ Yes" if structure.has_proper_structure else "❌ No")
                
                st.markdown("---")
                
                st.markdown('<h3 class="sub-section-header">📊 Semantic Elements Found</h3>', unsafe_allow_html=True)
                if structure.semantic_elements:
                    for element in structure.semantic_elements:
                        st.write(f"• `<{element}>`")
                else:
                    st.warning("No semantic HTML elements found. Consider using semantic tags like `<header>`, `<main>`, `<article>`, `<section>`, `<nav>`, `<footer>`.")
                
                st.markdown("---")
                
                st.markdown('<h3 class="sub-section-header">📋 Heading Hierarchy</h3>', unsafe_allow_html=True)
                hierarchy = structure.heading_hierarchy
                
                if hierarchy.h1:
                    st.write("**H1 Headings:**")
                    for heading in hierarchy.h1:
                        st.write(f"• {heading}")
                
                if hierarchy.h2:
                    st.write("**H2 Headings:**")
                    for heading in hierarchy.h2:
                        st.write(f"• {heading}")
                
                if hierarchy.h3:
                    st.write("**H3 Headings:**")
                    for heading in hierarchy.h3:
                        st.write(f"• {heading}")
            else:
                st.info("Structure analysis not available. Please run a 'Comprehensive Analysis' or 'LLM Accessibility Only'.")
        
        with tabs[13]:  # Meta Data
            st.markdown('<h2 class="section-header">🏷️ Meta Data Analysis</h2>', unsafe_allow_html=True)
            
            if st.session_state.static_result and st.session_state.static_result.meta_analysis:
                meta = st.session_state.static_result.meta_analysis
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Title", "✅ Present" if meta.title else "❌ Missing")
                with col2:
                    st.metric("Description", "✅ Present" if meta.description else "❌ Missing")
                with col3:
                    st.metric("Keywords", "✅ Present" if meta.keywords else "❌ Missing")
                with col4:
                    st.metric("Canonical URL", "✅ Present" if meta.canonical_url else "❌ Missing")
                
                st.markdown("---")
                
                if meta.title:
                    st.markdown('<h3 class="sub-section-header">📝 Page Title</h3>', unsafe_allow_html=True)
                    st.write(meta.title)
                
                if meta.description:
                    st.markdown('<h3 class="sub-section-header">📄 Meta Description</h3>', unsafe_allow_html=True)
                    st.write(meta.description)
                
                if meta.keywords:
                    st.markdown('<h3 class="sub-section-header">🏷️ Keywords</h3>', unsafe_allow_html=True)
                    st.write(meta.keywords)
                
                st.markdown("---")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("JSON-LD", "✅ Present" if meta.has_json_ld else "❌ Missing")
                with col2:
                    st.metric("Microdata", "✅ Present" if meta.has_microdata else "❌ Missing")
                with col3:
                    st.metric("RDFa", "✅ Present" if meta.has_rdfa else "❌ Missing")
                
                if meta.structured_data:
                    st.markdown('<h3 class="sub-section-header">📊 Structured Data Found</h3>', unsafe_allow_html=True)
                    for i, data in enumerate(meta.structured_data[:5]):  # Show first 5
                        st.write(f"**{i+1}. {data.type.upper()}:**")
                        st.json(data.data)
                        st.markdown("---")
                
                if meta.open_graph_tags:
                    st.markdown('<h3 class="sub-section-header">📱 Open Graph Tags</h3>', unsafe_allow_html=True)
                    for key, value in meta.open_graph_tags.items():
                        st.write(f"**{key}:** {value}")
                
                if meta.twitter_card_tags:
                    st.markdown('<h3 class="sub-section-header">🐦 Twitter Card Tags</h3>', unsafe_allow_html=True)
                    for key, value in meta.twitter_card_tags.items():
                        st.write(f"**{key}:** {value}")
            else:
                st.info("Meta data analysis not available. Please run a 'Comprehensive Analysis' or 'LLM Accessibility Only'.")
        
        with tabs[14]:  # JavaScript
            st.markdown('<h2 class="section-header">⚡ JavaScript Analysis</h2>', unsafe_allow_html=True)
            
            if st.session_state.static_result and st.session_state.static_result.javascript_analysis:
                js = st.session_state.static_result.javascript_analysis
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Scripts", js.total_scripts)
                with col2:
                    st.metric("Inline Scripts", js.inline_scripts)
                with col3:
                    st.metric("External Scripts", js.external_scripts)
                with col4:
                    st.metric("SPA Detected", "✅ Yes" if js.is_spa else "❌ No")
                
                st.markdown("---")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("AJAX Present", "✅ Yes" if js.has_ajax else "❌ No")
                with col2:
                    st.metric("Dynamic Content", "✅ Yes" if js.dynamic_content_detected else "❌ No")
                with col3:
                    st.metric("Frameworks", len(js.frameworks))
                
                if js.frameworks:
                    st.markdown('<h3 class="sub-section-header">🛠️ JavaScript Frameworks Detected</h3>', unsafe_allow_html=True)
                    for framework in js.frameworks:
                        with st.expander(f"**{framework.name}** (Confidence: {framework.confidence:.1%})"):
                            st.write(f"**Indicators:**")
                            for indicator in framework.indicators:
                                st.write(f"• {indicator}")
                
                if js.is_spa:
                    st.warning("⚠️ **Single Page Application (SPA) detected!** This may impact crawler accessibility as content is loaded dynamically.")
                elif js.dynamic_content_detected:
                    st.info("ℹ️ **Dynamic content detected.** Some content may not be accessible to basic crawlers.")
                else:
                    st.success("✅ **Static content detected.** Good for crawler accessibility!")
            else:
                st.info("JavaScript analysis not available. Please run a 'Comprehensive Analysis' or 'LLM Accessibility Only'.")
        
        with tabs[15]:  # Export Report
            st.markdown('<h2 class="section-header">📥 Export Analysis Report</h2>', unsafe_allow_html=True)
            
            if st.session_state.analysis_complete:
                st.markdown('<h3 class="sub-section-header">📊 Available Export Options</h3>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📄 Summary Report**")
                    st.write("Quick overview with key metrics and recommendations")
                    
                    if st.button("📥 Download Summary Report", use_container_width=True):
                        # Create a simple text summary
                        summary_data = f"""
Web Scraper & LLM Analysis Report
================================

URL: {st.session_state.analyzed_url}
Analysis Type: {st.session_state.last_analysis_type}
Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Duration: {st.session_state.analysis_duration:.2f} seconds

OVERALL SCORES:
"""
                        if st.session_state.score:
                            summary_data += f"""
Scraper Friendliness: {st.session_state.score.scraper_friendliness.total_score:.1f}/100 ({st.session_state.score.scraper_friendliness.grade})
LLM Accessibility: {st.session_state.score.llm_accessibility.total_score:.1f}/100 ({st.session_state.score.llm_accessibility.grade})
"""
                        
                        if st.session_state.llm_report:
                            summary_data += f"""
LLM Analysis Score: {st.session_state.llm_report.overall_score:.1f}/100 ({st.session_state.llm_report.grade})
"""
                        
                        summary_data += "\nKEY FINDINGS:\n"
                        
                        if st.session_state.static_result:
                            content = st.session_state.static_result.content_analysis
                            summary_data += f"• Content: {content.word_count:,} words, {content.character_count:,} characters\n"
                            
                            if st.session_state.static_result.javascript_analysis:
                                js = st.session_state.static_result.javascript_analysis
                                summary_data += f"• JavaScript: {js.total_scripts} scripts, SPA: {'Yes' if js.is_spa else 'No'}\n"
                        
                        if st.session_state.ssr_detection:
                            summary_data += f"• SSR Detection: {'Yes' if st.session_state.ssr_detection.is_ssr else 'No'}\n"
                        
                        summary_data += "\nRECOMMENDATIONS:\n"
                        if st.session_state.score and st.session_state.score.recommendations:
                            for i, rec in enumerate(st.session_state.score.recommendations[:5], 1):
                                summary_data += f"{i}. {rec.title}: {rec.description}\n"
                        else:
                            summary_data += "No specific recommendations available.\n"
                        
                        st.download_button(
                            label="📥 Download Summary Report",
                            data=summary_data,
                            file_name=f"web_analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                
                with col2:
                    st.markdown("**📊 Detailed Data Export**")
                    st.write("Complete analysis data in JSON format")
                    
                    if st.button("📥 Download Detailed Data", use_container_width=True):
                        import json
                        
                        export_data = {
                            "analysis_info": {
                                "url": st.session_state.analyzed_url,
                                "analysis_type": st.session_state.last_analysis_type,
                                "timestamp": datetime.now().isoformat(),
                                "duration": st.session_state.analysis_duration
                            },
                            "scores": {},
                            "analysis_results": {}
                        }
                        
                        if st.session_state.score:
                            export_data["scores"] = {
                                "scraper_friendliness": {
                                    "score": st.session_state.score.scraper_friendliness.total_score,
                                    "grade": st.session_state.score.scraper_friendliness.grade
                                },
                                "llm_accessibility": {
                                    "score": st.session_state.score.llm_accessibility.total_score,
                                    "grade": st.session_state.score.llm_accessibility.grade
                                }
                            }
                        
                        if st.session_state.llm_report:
                            export_data["analysis_results"]["llm_report"] = {
                                "overall_score": st.session_state.llm_report.overall_score,
                                "grade": st.session_state.llm_report.grade,
                                "limitations": st.session_state.llm_report.limitations,
                                "recommendations": st.session_state.llm_report.recommendations
                            }
                        
                        if st.session_state.static_result:
                            export_data["analysis_results"]["static_analysis"] = {
                                "content": {
                                    "word_count": st.session_state.static_result.content_analysis.word_count,
                                    "character_count": st.session_state.static_result.content_analysis.character_count,
                                    "links": st.session_state.static_result.content_analysis.links,
                                    "images": st.session_state.static_result.content_analysis.images
                                },
                                "structure": {
                                    "total_elements": st.session_state.static_result.structure_analysis.total_elements,
                                    "semantic_elements": st.session_state.static_result.structure_analysis.semantic_elements,
                                    "has_proper_structure": st.session_state.static_result.structure_analysis.has_proper_structure
                                },
                                "javascript": {
                                    "total_scripts": st.session_state.static_result.javascript_analysis.total_scripts,
                                    "is_spa": st.session_state.static_result.javascript_analysis.is_spa,
                                    "dynamic_content_detected": st.session_state.static_result.javascript_analysis.dynamic_content_detected
                                }
                            }
                        
                        json_data = json.dumps(export_data, indent=2, default=str)
                        
                        st.download_button(
                            label="📥 Download Detailed Data",
                            data=json_data,
                            file_name=f"web_analysis_detailed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                
                st.markdown("---")
                
                st.markdown('<h3 class="sub-section-header">📋 Report Contents</h3>', unsafe_allow_html=True)
                
                report_sections = []
                if st.session_state.score:
                    report_sections.append("✅ Overall Scores & Grades")
                if st.session_state.llm_report:
                    report_sections.append("✅ LLM Accessibility Analysis")
                if st.session_state.enhanced_llm_report:
                    report_sections.append("✅ Enhanced LLM Analysis")
                if st.session_state.static_result:
                    report_sections.append("✅ Static Content Analysis")
                if st.session_state.dynamic_result:
                    report_sections.append("✅ Dynamic Content Analysis")
                if st.session_state.comparison:
                    report_sections.append("✅ Content Comparison")
                if st.session_state.ssr_detection:
                    report_sections.append("✅ SSR Detection")
                if st.session_state.crawler_analysis:
                    report_sections.append("✅ Crawler Testing Results")
                if st.session_state.evidence_report:
                    report_sections.append("✅ Evidence Report")
                if st.session_state.bot_directives:
                    report_sections.append("✅ Bot Directives Analysis")
                
                if report_sections:
                    st.write("**Included in this report:**")
                    for section in report_sections:
                        st.write(f"• {section}")
                else:
                    st.warning("No analysis data available for export.")
                
                st.markdown("---")
                
                st.info("💡 **Tip:** Use the Summary Report for quick sharing and the Detailed Data for further analysis or integration with other tools.")
            else:
                st.info("Please complete an analysis before attempting to export a report.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem 0;">
        <p>Built with Streamlit • Powered by BeautifulSoup & Playwright</p>
        <p style="font-size: 0.9rem;">Analyze websites for scraper and LLM accessibility</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()