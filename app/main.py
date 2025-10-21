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
from src.analyzers.llms_txt_analyzer import LLMsTxtAnalyzer
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
        background-color: #f8f9fa;
        color: #333;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Fix for responsive layout */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }

    /* Main Header */
    .main-header {
        font-size: 3.2rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        padding-top: 1rem;
        line-height: 1.2;
        text-align: center;
    }
    .subtitle {
        font-size: 1.25rem;
        color: #555;
        margin-bottom: 2.5rem;
        text-align: center;
    }

    /* Section Headers */
    .section-header {
        font-size: 2rem;
        font-weight: bold;
        color: #4A90E2;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 0.8rem;
        margin-top: 3rem;
        margin-bottom: 2rem;
    }
    .sub-section-header {
        font-size: 1.6rem;
        font-weight: bold;
        color: #333;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }

    /* Score Cards */
    .score-card {
        background-color: #ffffff;
        border-left: 5px solid;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: transform 0.2s ease-in-out;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 120px;
    }
    .score-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }
    .score-card-header {
        font-size: 1.1em;
        font-weight: bold;
        margin-bottom: 0.6rem;
        color: #444;
    }
    .score-value {
        font-size: 2.2em;
        font-weight: bolder;
        line-height: 1;
        color: #222;
        margin: 0.5rem 0;
    }
    .score-grade {
        font-size: 1em;
        color: #666;
        margin-top: 0.5rem;
    }
    /* Score card specific colors */
    .score-card.excellent { border-left-color: #10b981; }
    .score-card.good { border-left-color: #3b82f6; }
    .score-card.fair { border-left-color: #f59e0b; }
    .score-card.poor { border-left-color: #ef4444; }
    .score-card.neutral { border-left-color: #95a5a6; }

    /* Streamlit Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        justify-content: center;
        margin-bottom: 2rem;
        flex-wrap: wrap;
    }
    .stTabs [data-baseweb="tab"] {
        padding-right: 25px;
        padding-left: 25px;
        font-size: 1.05rem;
        font-weight: 500;
        color: #666;
        transition: color 0.2s ease-in-out, border-bottom 0.2s ease-in-out;
        white-space: nowrap;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #667eea;
    }
    .stTabs [aria-selected="true"] {
        color: #764ba2;
        border-bottom: 3px solid #764ba2;
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
    }

    /* Sidebar improvements */
    .css-1d391kg {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }

    /* Button improvements */
    .stButton > button {
        border-radius: 8px;
        transition: all 0.2s ease-in-out;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* Status improvements */
    .stStatus {
        border-radius: 8px;
    }

    /* Progress bar improvements */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
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
    if 'llms_txt_analysis' not in st.session_state:
        st.session_state.llms_txt_analysis = None
    if 'last_analysis_type' not in st.session_state:
        st.session_state.last_analysis_type = None
    if 'analysis_duration' not in st.session_state:
        st.session_state.analysis_duration = 0.0

def clear_session_state():
    """Clear all analysis data from session state"""
    keys_to_clear = [
        'analysis_complete', 'static_result', 'dynamic_result', 'comparison', 
        'score', 'analyzed_url', 'llm_report', 'ssr_detection', 'crawler_analysis',
        'evidence_report', 'enhanced_llm_report', 'llms_txt_analysis', 
        'last_analysis_type', 'analysis_duration'
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

def perform_analysis(url: str, analyze_dynamic: bool = True, analysis_type: str = "Comprehensive Analysis", 
                    crawler_types: Optional[List[str]] = None, capture_evidence: bool = True):
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
                
                status.update(label="📄 Analyzing llms.txt file...", state="running")
                llms_txt_analyzer = LLMsTxtAnalyzer()
                llms_txt_analysis = llms_txt_analyzer.analyze(url)
                st.session_state.llms_txt_analysis = llms_txt_analysis
                logger.info(f"LLMs.txt analysis completed for {url}")
            
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
            
            st.session_state.analysis_complete = True
            st.session_state.analyzed_url = url
            st.session_state.last_analysis_type = analysis_type
            
            end_time = time.time()
            st.session_state.analysis_duration = end_time - start_time
            
            status.update(label="✅ Analysis complete!", state="complete", expanded=False)
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
        st.header("⚙️ Configuration")
        
        with st.form("analysis_config_form"):
            st.subheader("1. Target Website")
            url_input = st.text_input(
                "Website URL",
                value=st.session_state.get('analyzed_url', ''),
                placeholder="https://example.com",
                help="Enter the full URL including https://"
            )
            
            st.subheader("2. Analysis Focus")
            analysis_options = ["Comprehensive Analysis", "LLM Accessibility Only", "Web Crawler Testing", "SSR Detection Only"]
            last_analysis = st.session_state.get('last_analysis_type', 'Comprehensive Analysis')
            
            # Handle case where last_analysis_type might be None or not in list
            try:
                default_index = analysis_options.index(last_analysis)
            except (ValueError, TypeError):
                default_index = 0  # Default to "Comprehensive Analysis"
            
            analysis_type = st.selectbox(
                "Choose Analysis Type",
                analysis_options,
                index=default_index,
                help="Select the specific type of analysis to perform."
            )
            
            crawler_types = None
            if analysis_type == "Web Crawler Testing":
                crawler_types = st.multiselect(
                    "Select Crawlers to Test",
                    ["googlebot", "bingbot", "llm", "basic_scraper", "social_crawler"],
                    default=st.session_state.get('last_crawler_types_selection', ["llm", "googlebot"]),
                    help="Choose which crawler types to simulate."
                )
                st.session_state.last_crawler_types_selection = crawler_types
            
            st.subheader("3. Advanced Options")
            with st.expander("Advanced Analysis Settings", expanded=False):
                analyze_dynamic = False
                if analysis_type == "Comprehensive Analysis":
                    analyze_dynamic = st.checkbox(
                        "Include dynamic analysis (renders content with browser)",
                        value=True,
                        help="Dynamic analysis fetches content after JavaScript execution."
                    )
                    st.info("✅ Dynamic analysis is now fully supported!")
                else:
                    st.info("Dynamic analysis is only applicable for 'Comprehensive Analysis'.")
                
                capture_evidence = st.checkbox(
                    "Generate Detailed Evidence Report",
                    value=st.session_state.get('last_capture_evidence_selection', True),
                    help="Enable to capture detailed data points and observations."
                )
                st.session_state.last_capture_evidence_selection = capture_evidence
            
            st.markdown("---")
            analyze_button = st.form_submit_button("🚀 Start Analysis", type="primary", use_container_width=True)
        
        st.markdown("---")
        
        # Clear Analysis Button
        if st.session_state.analysis_complete:
            st.subheader("🔄 Reset Analysis")
            if st.button("🗑️ Clear All Analysis Data", type="secondary", use_container_width=True):
                clear_session_state()
                st.success("✅ Analysis data cleared! You can now start a fresh analysis.")
                st.rerun()
        
        st.markdown("---")
        
        # Info section
        with st.expander("ℹ️ How This Tool Works"):
            st.markdown("""
            This application analyzes websites to determine:
            
            - **Scraper Accessibility**: What content can be extracted by web scrapers
            - **LLM Accessibility**: How well the content is structured for AI understanding
            - **JavaScript Dependency**: Content that requires JavaScript to load
            - **SEO & Metadata**: Quality of meta tags and structured data
            
            The analysis provides actionable recommendations to improve your site's
            accessibility to both scrapers and LLMs.
            """)
    
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
                success = perform_analysis(url_input, analyze_dynamic, analysis_type,
                                         crawler_types,
                                         capture_evidence)
                
                if success:
                    st.rerun()
    
    # Display results
    if st.session_state.analysis_complete:
        st.markdown('<h2 class="section-header">Overall Analysis Summary</h2>', unsafe_allow_html=True)
        
        # Score Cards
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
        
        # Detailed Results in Tabs
        tabs = st.tabs([
            "🎯 Executive Summary",
            "📊 Overview",
            "🤖 LLM Analysis",
            "🔬 Enhanced LLM Analysis",
            "📄 LLMs.txt Analysis",
            "🕷️ Scraper Analysis",
            "🔍 SSR Detection",
            "🕷️ Crawler Testing",
            "📊 Evidence Report",
            "📝 Content",
            "🏗️ Structure",
            "🏷️ Meta Data",
            "⚡ JavaScript",
            "💡 Recommendations",
            "📥 Export Report"
        ])
        
        with tabs[0]:  # Executive Summary
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
        
        with tabs[1]:  # Overview
            st.markdown('<h2 class="section-header">Detailed Analysis Breakdown</h2>', unsafe_allow_html=True)
            
            if st.session_state.score:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<h3 class="sub-section-header">🎯 Scraper Friendliness Breakdown</h3>', unsafe_allow_html=True)
                    
                    components = [
                        st.session_state.score.scraper_friendliness.static_content_quality,
                        st.session_state.score.scraper_friendliness.semantic_html_structure,
                        st.session_state.score.scraper_friendliness.structured_data_implementation,
                        st.session_state.score.scraper_friendliness.meta_tag_completeness,
                        st.session_state.score.scraper_friendliness.javascript_dependency,
                        st.session_state.score.scraper_friendliness.crawler_accessibility
                    ]
                    
                    for comp in components:
                        st.markdown(f"**{comp.name}**: {comp.score:.1f}/{comp.max_score:.0f} ({comp.percentage:.0f}%)")
                        st.progress(comp.percentage / 100)
                        
                        if comp.strengths:
                            with st.expander("✅ Strengths"):
                                for strength in comp.strengths:
                                    st.markdown(f"- {strength}")
                        
                        if comp.issues:
                            with st.expander("⚠️ Issues"):
                                for issue in comp.issues:
                                    st.markdown(f"- {issue}")
                        
                        st.markdown("---")
                
                with col2:
                    st.markdown('<h3 class="sub-section-header">🤖 LLM Accessibility Breakdown</h3>', unsafe_allow_html=True)
                    
                    st.info("""
                    LLM scoring emphasizes content quality and semantic structure over
                    JavaScript dependency, as LLMs can use dynamic rendering capabilities.
                    """)
                    
                    llm_components = [
                        st.session_state.score.llm_accessibility.static_content_quality,
                        st.session_state.score.llm_accessibility.semantic_html_structure,
                        st.session_state.score.llm_accessibility.structured_data_implementation,
                        st.session_state.score.llm_accessibility.meta_tag_completeness
                    ]
                    
                    for comp in llm_components:
                        st.markdown(f"**{comp.name}**: {comp.score:.1f}/{comp.max_score:.0f} ({comp.percentage:.0f}%)")
                        st.progress(comp.percentage / 100)
                        if comp.strengths:
                            with st.expander("✅ Strengths"):
                                for strength in comp.strengths:
                                    st.markdown(f"- {strength}")
                        if comp.issues:
                            with st.expander("⚠️ Issues"):
                                for issue in comp.issues:
                                    st.markdown(f"- {issue}")
                        st.markdown("---")
            else:
                st.info(f"**'Overview' tab is populated only after a 'Comprehensive Analysis'.** Please select this option from the sidebar to view full score breakdowns.")
                if st.session_state.last_analysis_type:
                    st.markdown(f"Currently showing results for: **{st.session_state.last_analysis_type}**")
        
        with tabs[2]:  # LLM Analysis
            st.markdown('<h2 class="section-header">🤖 LLM Accessibility Analysis</h2>', unsafe_allow_html=True)
            
            if st.session_state.llm_report:
                llm_report = st.session_state.llm_report
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("LLM Accessibility Score", f"{llm_report.overall_score:.1f}/100",
                             delta=f"Grade: {llm_report.grade}")
                with col2:
                    st.metric("Accessible Content Categories", f"{len(llm_report.accessible_content)}")
                with col3:
                    st.metric("Limitations Found", f"{len(llm_report.limitations)}")
                
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
        
        with tabs[3]:  # Enhanced LLM Analysis
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
                    with st.expander(f"**{capability.name}** - Score: {capability.accessibility_score:.1f}/100"):
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
        
        with tabs[4]:  # LLMs.txt Analysis
            st.markdown('<h2 class="section-header">📄 LLMs.txt Analysis</h2>', unsafe_allow_html=True)
            
            if st.session_state.llms_txt_analysis:
                analysis = st.session_state.llms_txt_analysis
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("LLMs.txt Present", "✅ Yes" if analysis.is_present else "❌ No")
                with col2:
                    st.metric("Quality Score", f"{analysis.quality_score:.1f}/100" if analysis.is_present else "N/A")
                with col3:
                    st.metric("Format Valid", "✅ Yes" if analysis.format_valid else "❌ No")
                
                st.markdown("---")
                
                if analysis.is_present:
                    st.markdown('<h3 class="sub-section-header">📄 File Content</h3>', unsafe_allow_html=True)
                    st.code(analysis.content, language="markdown")
                    
                    if analysis.sections:
                        st.markdown('<h3 class="sub-section-header">📋 Sections Found</h3>', unsafe_allow_html=True)
                        for section_name, section_content in analysis.sections.items():
                            st.markdown(f"**{section_name}:**")
                            st.write(section_content)
                            st.markdown("---")
                    
                    if analysis.benefits:
                        st.markdown('<h3 class="sub-section-header">✅ Benefits</h3>', unsafe_allow_html=True)
                        for benefit in analysis.benefits:
                            st.write(f"• {benefit}")
                    
                    if analysis.issues:
                        st.markdown('<h3 class="sub-section-header">⚠️ Issues Found</h3>', unsafe_allow_html=True)
                        for issue in analysis.issues:
                            st.warning(f"• {issue}")
                    
                    if analysis.recommendations:
                        st.markdown('<h3 class="sub-section-header">💡 Recommendations</h3>', unsafe_allow_html=True)
                        for rec in analysis.recommendations:
                            st.info(f"• {rec}")
                else:
                    st.warning("No llms.txt file found at the website root.")
                    st.info("**What is llms.txt?** It's a new standard (2024-2025) for guiding AI crawlers to quality content, different from robots.txt which focuses on exclusion.")
                    
                    st.markdown('<h3 class="sub-section-header">💡 Recommendations</h3>', unsafe_allow_html=True)
                    for rec in analysis.recommendations:
                        st.info(f"• {rec}")
            else:
                st.info("LLMs.txt analysis not available. Please run a 'Comprehensive Analysis' or 'LLM Accessibility Only'.")
        
        with tabs[6]:  # SSR Detection
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
        
        with tabs[7]:  # Crawler Testing
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
        
        with tabs[8]:  # Evidence Report
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
        
        with tabs[9]:  # Content
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
        
        with tabs[10]:  # Structure
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
        
        with tabs[11]:  # Meta Data
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
        
        with tabs[12]:  # JavaScript
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
        
        # Add more tabs as needed...
        with tabs[13]:  # Recommendations
            st.markdown('<h2 class="section-header">💡 Optimization Recommendations</h2>', unsafe_allow_html=True)
            
            if st.session_state.score and st.session_state.score.recommendations:
                for rec in st.session_state.score.recommendations:
                    if rec.priority.value == "critical":
                        st.error(f"**{rec.priority.value.upper()}**: {rec.title}")
                        st.write(rec.description)
                    elif rec.priority.value == "high":
                        st.warning(f"**{rec.priority.value.upper()}**: {rec.title}")
                        st.write(rec.description)
                    else:
                        st.info(f"**{rec.priority.value.upper()}**: {rec.title}")
                        st.write(rec.description)
                    
                    if rec.code_example:
                        with st.expander("💻 Code Example"):
                            st.code(rec.code_example, language="html")
                    
                    st.markdown("---")
                
                if not st.session_state.score.recommendations:
                    st.success("🎉 No significant recommendations found - your site is well-optimized!")
            else:
                st.info("No comprehensive scoring analysis available. Run **'Comprehensive Analysis'** to see optimization recommendations.")
        
        with tabs[14]:  # Export Report
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
                if st.session_state.llms_txt_analysis:
                    report_sections.append("✅ LLMs.txt Analysis")
                
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