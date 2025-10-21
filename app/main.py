"""
Main Streamlit Application

Web interface for analyzing website scraper-friendliness and LLM accessibility.
"""

import streamlit as st
import logging
from datetime import datetime

from src.analyzers import StaticAnalyzer, DynamicAnalyzer, ContentComparator, ScoringEngine
from src.analyzers.llm_accessibility_analyzer import LLMAccessibilityAnalyzer
from src.analyzers.separate_analyzer import SeparateAnalyzer # Not used in code, but imported. Keep for now.
from src.analyzers.ssr_detector import SSRDetector
from src.analyzers.web_crawler_analyzer import WebCrawlerAnalyzer
from src.analyzers.evidence_capture import EvidenceCapture
from src.analyzers.enhanced_llm_analyzer import EnhancedLLMAccessibilityAnalyzer
from src.analyzers.llms_txt_analyzer import LLMsTxtAnalyzer
from src.utils.validators import URLValidator
from src.utils.report_generator import ComprehensiveReportGenerator, ReportData
from src.models.analysis_result import AnalysisResult
from src.models.scoring_models import Score # Not directly used, but implied by score object

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

# Custom CSS for better styling and new components
st.markdown("""
<style>
    /* General Streamlit Overrides */
    .stApp {
        background-color: #f8f9fa; /* Light background for the app */
        color: #333;
    }

    /* Main Header */
    .main-header {
        font-size: 3.2rem; /* Slightly larger */
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        padding-top: 1rem; /* Add some space at the top */
    }
    .subtitle {
        font-size: 1.25rem; /* Slightly larger */
        color: #555; /* Darker gray */
        margin-bottom: 2.5rem; /* More spacing */
    }

    /* Section Headers for main content area */
    .section-header {
        font-size: 2rem;
        font-weight: bold;
        color: #4A90E2; /* A modern blue */
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

    /* Score Cards for Overview */
    .score-card {
        background-color: #ffffff; /* White background */
        border-left: 5px solid; /* For accent color */
        border-radius: 8px;
        padding: 1.5rem; /* More padding */
        margin-bottom: 1.5rem; /* More spacing between cards */
        box-shadow: 0 4px 12px rgba(0,0,0,0.08); /* Stronger, but still soft shadow */
        transition: transform 0.2s ease-in-out; /* Subtle hover effect */
    }
    .score-card:hover {
        transform: translateY(-3px);
    }
    .score-card-header {
        font-size: 1.1em;
        font-weight: bold;
        margin-bottom: 0.6rem;
        color: #444;
    }
    .score-value {
        font-size: 2.2em; /* Larger score value */
        font-weight: bolder;
        line-height: 1;
        color: #222;
    }
    .score-grade {
        font-size: 1em;
        color: #666;
        margin-top: 0.5rem;
    }
    /* Score card specific colors */
    .score-card.excellent { border-left-color: #10b981; } /* Green */
    .score-card.good { border-left-color: #3b82f6; } /* Blue */
    .score-card.fair { border-left-color: #f59e0b; } /* Orange */
    .score-card.poor { border-left-color: #ef4444; } /* Red */
    .score-card.neutral { border-left-color: #95a5a6; } /* Gray for general metrics */

    /* Score breakdown colors (original classes, kept for internal use if needed) */
    .score-excellent { color: #10b981; font-weight: bold; }
    .score-good { color: #3b82f6; font-weight: bold; }
    .score-fair { color: #f59e0b; font-weight: bold; }
    .score-poor { color: #ef4444; font-weight: bold; }

    /* Streamlit Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px; /* Increased gap */
        justify-content: center; /* Center tabs */
    }
    .stTabs [data-baseweb="tab"] {
        padding-right: 25px; /* More padding */
        padding-left: 25px;
        font-size: 1.05rem; /* Slightly larger text */
        font-weight: 500;
        color: #666;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #667eea; /* Hover color */
    }
    .stTabs [aria-selected="true"] {
        color: #764ba2; /* Selected tab color */
        border-bottom: 3px solid #764ba2; /* Thicker underline */
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #34495e;
    }

    /* Custom Info Box for LLMs.txt missing */
    .llms-txt-info-box {
        background-color: #e8f5e9; /* Light green */
        border-left: 5px solid #4CAF50; /* Green border */
        padding: 1.5rem;
        border-radius: 8px;
        margin-top: 2rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .llms-txt-info-box h5 {
        color: #388E3C; /* Darker green */
        margin-bottom: 0.8rem;
    }
    .llms-txt-info-box ul {
        list-style-type: disc;
        margin-left: 1.5rem;
        margin-top: 0.8rem;
    }
    .llms-txt-info-box p {
        margin-bottom: 0.5rem;
    }

    /* General containers/divs for better visual separation */
    div[data-testid="stVerticalBlock"] > div:first-child {
        padding-top: 1rem;
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
    if 'separate_analyzer' not in st.session_state:
        st.session_state.separate_analyzer = None
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

def _get_grade(score: float) -> str:
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

def get_score_color_class(score: float) -> str:
    """Get CSS class based on score"""
    if score >= 85:
        return "score-excellent"
    elif score >= 70:
        return "score-good"
    elif score >= 50:
        return "score-fair"
    else:
        return "score-poor"

def perform_analysis(url: str, analyze_dynamic: bool = True, analysis_type: str = "Comprehensive Analysis", 
                    crawler_types: list = None, capture_evidence: bool = True):
    """Perform website analysis based on selected focus"""
    try:
        # Use st.status for granular progress feedback
        with st.status("🚀 Starting website analysis...", expanded=True) as status:
            # Always need static analysis as base for most analysis types
            static_result = None
            if analysis_type in ["Comprehensive Analysis", "LLM Accessibility Only", "Web Crawler Testing", "SSR Detection Only"]:
                status.update(label="🔍 Performing static analysis...", state="running")
                static_analyzer = StaticAnalyzer(timeout=30)
                static_result = static_analyzer.analyze(url)
                
                if static_result.status != "success":
                    st.error(f"Static analysis failed: {static_result.message}")
                    status.update(label="Static analysis failed.", state="error")
                    return False
                
                st.session_state.static_result = static_result
                logger.info(f"Static analysis completed for {url}")
            
            # Dynamic Analysis (only for Comprehensive Analysis)
            dynamic_result = None
            if analysis_type == "Comprehensive Analysis" and analyze_dynamic:
                status.update(label="🌐 Performing dynamic analysis (rendering with browser)...", state="running")
                try:
                    dynamic_analyzer = DynamicAnalyzer(timeout=30, headless=True)
                    dynamic_result = dynamic_analyzer.analyze(url)
                    
                    if dynamic_result and dynamic_result.status != "success":
                        st.warning(f"Dynamic analysis failed: {dynamic_result.message}")
                        dynamic_result = None
                    else:
                        st.session_state.dynamic_result = dynamic_result
                        logger.info(f"Dynamic analysis completed for {url}")
                except Exception as e:
                    st.warning(f"Dynamic analysis error: {str(e)}")
                    logger.error(f"Dynamic analysis error for {url}: {e}")
                    dynamic_result = None
            
            # Content Comparison (only for Comprehensive Analysis with dynamic results)
            comparison = None
            if analysis_type == "Comprehensive Analysis" and dynamic_result:
                status.update(label="📊 Comparing static vs dynamic content...", state="running")
                comparator = ContentComparator()
                comparison = comparator.compare(static_result, dynamic_result)
                st.session_state.comparison = comparison
                logger.info(f"Content comparison completed for {url}")
            
            # LLM Accessibility Analysis (for Comprehensive Analysis and LLM Accessibility Only)
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
                status.update(label="🔍 Detecting SSR patterns...", state="running")
                ssr_detector = SSRDetector()
                ssr_detection = ssr_detector.detect_ssr(static_result.content_analysis.text_content if static_result and static_result.content_analysis else "", 
                                                        static_result.javascript_analysis if static_result else None)
                st.session_state.ssr_detection = ssr_detection
                logger.info(f"SSR detection completed for {url}")
            
            # Web Crawler Testing
            if analysis_type in ["Comprehensive Analysis", "Web Crawler Testing"]:
                if crawler_types is None:
                    crawler_types = ["llm", "googlebot"]
                
                crawler_analyzer = WebCrawlerAnalyzer()
                crawler_results = {}
                
                for crawler_type in crawler_types:
                    status.update(label=f"🕷️ Testing {crawler_type} accessibility...", state="running")
                    try:
                        crawler_result = crawler_analyzer.analyze_crawler_accessibility(url, crawler_type, static_result)
                        crawler_results[crawler_type] = crawler_result
                        logger.info(f"{crawler_type} analysis completed for {url}")
                    except Exception as e:
                        st.warning(f"Failed to analyze {crawler_type}: {str(e)}")
                        logger.error(f"Crawler analysis error for {crawler_type} on {url}: {e}")
                
                st.session_state.crawler_analysis = crawler_results
            
            # Evidence Capture (only if enabled)
            if capture_evidence:
                status.update(label="📊 Capturing evidence and generating reports...", state="running")
                evidence_capture = EvidenceCapture()
                
                evidence_data = {}
                if st.session_state.crawler_analysis:
                    evidence_data.update(st.session_state.crawler_analysis)
                if st.session_state.llm_report:
                    # Convert LLM recommendations to priority-based issues for evidence report
                    llm_issues = []
                    if st.session_state.llm_report.recommendations:
                        for rec in st.session_state.llm_report.recommendations:
                            if rec.startswith("CRITICAL"):
                                llm_issues.append(f"CRITICAL: {rec}")
                            elif rec.startswith("HIGH"):
                                llm_issues.append(f"HIGH: {rec}")
                            elif rec.startswith("MEDIUM"):
                                llm_issues.append(f"MEDIUM: {rec}")
                            else:
                                llm_issues.append(f"LOW: {rec}")
                    
                    llm_evidence = type('obj', (object,), {
                        'crawler_name': 'LLM Analysis',
                        'crawler_type': 'LLM Analysis',
                        'accessibility_score': st.session_state.llm_report.overall_score if st.session_state.llm_report else 0,
                        'content_accessible': {'text_content': {'available': True}},
                        'content_inaccessible': {'javascript_dependent_content': {'available': False}},
                        'evidence': [f"LLM accessibility score: {st.session_state.llm_report.overall_score:.1f}"] if st.session_state.llm_report else [],
                        'recommendations': st.session_state.llm_report.recommendations if st.session_state.llm_report else [],
                        'accessibility_issues': llm_issues
                    })()
                    evidence_data['llm_analysis'] = llm_evidence
                if st.session_state.ssr_detection:
                    # Convert SSR detection to priority-based issues for evidence report
                    ssr_issues = []
                    if not st.session_state.ssr_detection.is_ssr:
                        ssr_issues.append("HIGH: SSR not detected - consider implementing server-side rendering for better LLM accessibility")
                    else:
                        ssr_issues.append("LOW: SSR detected - good for LLM accessibility")
                    
                    ssr_evidence = type('obj', (object,), {
                        'crawler_name': 'SSR Detection',
                        'crawler_type': 'SSR Detection',
                        'accessibility_score': st.session_state.ssr_detection.confidence * 100,
                        'content_accessible': {'ssr_detected': st.session_state.ssr_detection.is_ssr},
                        'content_inaccessible': {'rendering_type': st.session_state.ssr_detection.rendering_type},
                        'evidence': st.session_state.ssr_detection.evidence,
                        'recommendations': ['SSR detection completed'] if st.session_state.ssr_detection.is_ssr else ['Consider implementing SSR'],
                        'accessibility_issues': ssr_issues
                    })()
                    evidence_data['ssr_detection'] = ssr_evidence
                
                if evidence_data:
                    evidence_report = evidence_capture.create_evidence_report(url, evidence_data)
                    st.session_state.evidence_report = evidence_report
                    logger.info(f"Evidence report generated for {url}")
                else:
                    st.warning("No evidence data available to capture")
            
            # Scoring (only for Comprehensive Analysis)
            if analysis_type == "Comprehensive Analysis":
                status.update(label="⚡ Calculating scores and generating recommendations...", state="running")
                scoring_engine = ScoringEngine()
                score = scoring_engine.calculate_score(static_result, comparison)
                st.session_state.score = score
                logger.info(f"Scoring completed for {url}")
            else:
                st.session_state.score = None # Clear score if not comprehensive
            
            st.session_state.analysis_complete = True
            st.session_state.analyzed_url = url
            st.session_state.last_analysis_type = analysis_type # Store analysis type for consistent display
            status.update(label="✅ Analysis complete!", state="complete", expanded=False)
            return True
        
    except Exception as e:
        status.update(label="❌ Analysis failed!", state="error")
        st.error(f"❌ Analysis failed: {str(e)}")
        logger.error(f"Analysis error for {url}: {e}")
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
                placeholder="https://example.com",
                help="Enter the full URL including https://"
            )
            
            st.subheader("2. Analysis Focus")
            analysis_type = st.selectbox(
                "Choose Analysis Type",
                ["Comprehensive Analysis", "LLM Accessibility Only", "Web Crawler Testing", "SSR Detection Only"],
                help="Select the specific type of analysis to perform."
            )
            
            crawler_types = None
            if analysis_type == "Web Crawler Testing":
                crawler_types = st.multiselect(
                    "Select Crawlers to Test",
                    ["googlebot", "bingbot", "llm", "basic_scraper", "social_crawler"],
                    default=["llm", "googlebot"],
                    help="Choose which crawler types to simulate."
                )
            
            st.subheader("3. Advanced Options")
            
            # Dynamic Analysis (Conditional & Explained)
            analyze_dynamic = False # Default to False
            if analysis_type == "Comprehensive Analysis":
                analyze_dynamic_disabled_reason = "Dynamic analysis is not supported on Windows Store Python due to asyncio limitations. Static analysis provides comprehensive LLM accessibility insights."
                analyze_dynamic = st.checkbox(
                    "Include dynamic analysis (renders content with browser)",
                    value=False,
                    disabled=True, # Keeping original disabled state
                    help=f"Dynamic analysis fetches content after JavaScript execution. {analyze_dynamic_disabled_reason}"
                )
                if analyze_dynamic_disabled_reason: # Display info if it's disabled for a reason
                    st.info(f"⚠️ {analyze_dynamic_disabled_reason}")
            else:
                st.info("Dynamic analysis is only applicable for 'Comprehensive Analysis'.")
            
            capture_evidence = st.checkbox(
                "Generate Detailed Evidence Report",
                value=True,
                help="Enable to capture detailed data points for a comprehensive evidence report."
            )
            
            st.markdown("---")
            analyze_button = st.form_submit_button("🚀 Start Analysis", type="primary", use_container_width=True)
            
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
            
            ---
            
            **📊 Scoring Breakdown**
            
            **Scraper-Friendliness Score (100 pts)**
            - Static Content Quality: 25 pts
            - Semantic HTML Structure: 20 pts
            - Structured Data: 20 pts
            - Meta Tags: 15 pts
            - JavaScript Dependency: 10 pts
            - Crawler Accessibility: 10 pts
            
            **Letter Grades**
            - A: 90-100 (Excellent)
            - B: 80-89 (Good)
            - C: 70-79 (Fair)
            - D: 60-69 (Poor)
            - F: <60 (Failing)
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
                st.session_state.analysis_complete = False # Reset before new analysis
                success = perform_analysis(url_input, analyze_dynamic, analysis_type, 
                                         crawler_types, 
                                         capture_evidence)
                
                if success:
                    st.success("✅ Analysis complete! Review the tabs below for detailed insights.")
                
    # Display results
    if st.session_state.analysis_complete:
        st.markdown('<h2 class="section-header">Overall Analysis Summary</h2>', unsafe_allow_html=True)
        
        # Consistent Quick Overview with custom scorecards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.session_state.score:
                scraper_score = st.session_state.score.scraper_friendliness.total_score
                scraper_grade = st.session_state.score.scraper_friendliness.grade
                score_class = get_score_color_class(scraper_score).replace('score-', '')
                st.markdown(f"""
                <div class="score-card {score_class}">
                    <div class="score-card-header">Scraper Friendliness</div>
                    <div class="score-value">{scraper_score:.1f}/100</div>
                    <div class="score-grade">Grade: {scraper_grade}</div>
                </div>
                """, unsafe_allow_html=True)
            elif st.session_state.last_analysis_type in ["Web Crawler Testing", "SSR Detection Only", "LLM Accessibility Only"]:
                st.markdown(f"""
                <div class="score-card neutral">
                    <div class="score-card-header">Scraper Friendliness</div>
                    <div class="score-value">N/A</div>
                    <div class="score-grade">Not in focus</div>
                </div>
                """, unsafe_allow_html=True)
            else: # Should not happen if analysis_complete is True, but as fallback
                st.markdown(f"""
                <div class="score-card neutral">
                    <div class="score-card-header">Scraper Friendliness</div>
                    <div class="score-value">--</div>
                    <div class="score-grade">No data</div>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            if st.session_state.score:
                llm_score = st.session_state.score.llm_accessibility.total_score
                llm_grade = st.session_state.score.llm_accessibility.grade
                score_class = get_score_color_class(llm_score).replace('score-', '')
                st.markdown(f"""
                <div class="score-card {score_class}">
                    <div class="score-card-header">LLM Accessibility</div>
                    <div class="score-value">{llm_score:.1f}/100</div>
                    <div class="score-grade">Grade: {llm_grade}</div>
                </div>
                """, unsafe_allow_html=True)
            elif st.session_state.enhanced_llm_report:
                llm_score = st.session_state.enhanced_llm_report.overall_score
                llm_grade = st.session_state.enhanced_llm_report.grade
                score_class = get_score_color_class(llm_score).replace('score-', '')
                st.markdown(f"""
                <div class="score-card {score_class}">
                    <div class="score-card-header">Enhanced LLM Score</div>
                    <div class="score-value">{llm_score:.1f}/100</div>
                    <div class="score-grade">Grade: {llm_grade}</div>
                </div>
                """, unsafe_allow_html=True)
            elif st.session_state.llm_report:
                llm_score = st.session_state.llm_report.overall_score
                llm_grade = st.session_state.llm_report.grade
                score_class = get_score_color_class(llm_score).replace('score-', '')
                st.markdown(f"""
                <div class="score-card {score_class}">
                    <div class="score-card-header">LLM Accessibility</div>
                    <div class="score-value">{llm_score:.1f}/100</div>
                    <div class="score-grade">Grade: {llm_grade}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                 st.markdown(f"""
                <div class="score-card neutral">
                    <div class="score-card-header">LLM Accessibility</div>
                    <div class="score-value">N/A</div>
                    <div class="score-grade">Not in focus</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col3:
            if st.session_state.static_result and st.session_state.static_result.content_analysis:
                word_count = st.session_state.static_result.content_analysis.word_count
                st.markdown(f"""
                <div class="score-card neutral">
                    <div class="score-card-header">Total Word Count</div>
                    <div class="score-value">{word_count:,}</div>
                    <div class="score-grade">Static HTML</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                 st.markdown(f"""
                <div class="score-card neutral">
                    <div class="score-card-header">Total Word Count</div>
                    <div class="score-value">--</div>
                    <div class="score-grade">No data</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col4:
            # Count recommendations from all sources for consistency
            recommendations_count = 0
            critical_count = 0
            
            # Count from scoring engine if available
            if st.session_state.score and st.session_state.score.recommendations:
                recommendations_count += len(st.session_state.score.recommendations)
                critical_count += len([r for r in st.session_state.score.recommendations if r.priority.value == "critical"])
            
            # Count from LLM report if available
            if st.session_state.llm_report and st.session_state.llm_report.recommendations:
                recommendations_count += len(st.session_state.llm_report.recommendations)
                critical_count += len([r for r in st.session_state.llm_report.recommendations if r.startswith("CRITICAL")])
            
            # Count from enhanced LLM report if available
            if st.session_state.enhanced_llm_report and st.session_state.enhanced_llm_report.critical_recommendations:
                recommendations_count += len(st.session_state.enhanced_llm_report.critical_recommendations)
                critical_count += len(st.session_state.enhanced_llm_report.critical_recommendations)
            
            score_class = "poor" if critical_count > 0 else "excellent" if recommendations_count == 0 else "good"
            st.markdown(f"""
            <div class="score-card {score_class}">
                <div class="score-card-header">Key Recommendations</div>
                <div class="score-value">{recommendations_count}</div>
                <div class="score-grade">Critical: {critical_count}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Detailed Results in Tabs
        tabs = st.tabs([
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
            "📥 Export Report" # New tab for downloads
        ])
        
        with tabs[0]:  # Overview
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
                st.info("Comprehensive Analysis required for a full score breakdown.")
                if st.session_state.last_analysis_type:
                    st.markdown(f"Currently showing results for: **{st.session_state.last_analysis_type}**")
        
        with tabs[1]:  # LLM Analysis
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
                    
                    if js_content['dynamic_content']:
                        with st.expander("🔬 Technical Details & Citations"):
                            tech_details = js_content['technical_details']
                            st.markdown(f"**Why LLMs can't execute JavaScript:** {tech_details['why_llms_cant_execute_js']}")
                            st.markdown(f"**Impact on content:** {tech_details['impact_on_content']}")
                            
                            st.markdown("**Examples of inaccessible content:**")
                            for example in tech_details['examples']:
                                st.markdown(f"- {example}")
                            
                            st.markdown("**Citations:**")
                            for citation in tech_details['citations']:
                                st.markdown(f"- [{citation}]({citation})")
                    
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
                
                st.markdown("---")
                
                st.markdown('<h3 class="sub-section-header">🔬 Technical Analysis</h3>', unsafe_allow_html=True)
                
                tech = llm_report.technical_analysis
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📊 Content Metrics**")
                    content_metrics = tech['content_metrics']
                    st.metric("Readability Score", f"{content_metrics['readability_score']:.1f}/100")
                    st.metric("Total Paragraphs", content_metrics['paragraphs'])
                    
                    st.markdown("**🏗️ Structure Metrics**")
                    structure_metrics = tech['structure_metrics']
                    st.metric("Accessibility Score", f"{structure_metrics['accessibility_score']:.1f}/100")
                    st.metric("DOM Depth", structure_metrics['dom_depth'])
                
                with col2:
                    st.markdown("**⚡ JavaScript Metrics**")
                    js_metrics = tech['javascript_metrics']
                    st.metric("Complexity Score", f"{js_metrics['complexity_score']:.1f}/100")
                    st.metric("Script Count", js_metrics['script_count'])
                    
                    st.markdown("**🏷️ Meta Completeness**")
                    meta_completeness = tech['meta_completeness']
                    st.metric("Title Present", "✅" if meta_completeness['title_present'] else "❌")
                    st.metric("Description Present", "✅" if meta_completeness['description_present'] else "❌")
            else:
                st.info("LLM analysis not available. Please run the analysis first with 'Comprehensive Analysis' or 'LLM Accessibility Only'.")
        
        with tabs[2]:  # Enhanced LLM Analysis
            st.markdown('<h2 class="section-header">🔬 Enhanced LLM Analysis</h2>', unsafe_allow_html=True)
            
            if st.session_state.enhanced_llm_report:
                enhanced_report = st.session_state.enhanced_llm_report
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Enhanced LLM Score", f"{enhanced_report.overall_score:.1f}/100", 
                             delta=f"Grade: {enhanced_report.grade}")
                with col2:
                    st.metric("Semantic HTML Score", f"{enhanced_report.semantic_html_score:.1f}/100")
                with col3:
                    st.metric("JavaScript Impact", f"{enhanced_report.javascript_impact_score:.1f}/100")
                
                st.markdown("---")
                
                st.markdown('<h3 class="sub-section-header">🕷️ LLM Crawler Capabilities</h3>', unsafe_allow_html=True)
                
                for crawler_name, capability in enhanced_report.crawler_analysis.items():
                    with st.expander(f"⚙️ {capability.name} Analysis"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Capabilities:**")
                            st.write(f"✅ Executes JavaScript: {capability.executes_javascript}")
                            st.write(f"✅ Uses Headless Browser: {capability.uses_headless_browser}")
                            st.write(f"✅ Real-time Access: {capability.real_time_access}")
                            
                        with col2:
                            st.markdown("**Strategy:**")
                            st.write(f"📊 Chunking: {capability.chunking_strategy}")
                            st.write(f"🔢 Vectorization: {capability.vectorization_quality}")
                            st.write(f"📋 Schema Preference: {capability.schema_preference}")
                        
                        st.markdown("**Limitations:**")
                        for limitation in capability.limitations:
                            st.write(f"⚠️ {limitation}")
                
                st.markdown("---")
                
                st.markdown('<h3 class="sub-section-header">📊 Content Chunking Analysis</h3>', unsafe_allow_html=True)
                
                chunking = enhanced_report.chunking_analysis
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Semantic Boundaries", chunking.semantic_boundaries)
                with col2:
                    st.metric("Heading Quality", f"{chunking.heading_hierarchy_quality:.2f}")
                with col3:
                    st.metric("Chunking Score", f"{chunking.chunking_score:.1f}/100")
                
                if chunking.issues:
                    st.markdown("**⚠️ Chunking Issues:**")
                    for issue in chunking.issues:
                        st.error(issue)
                
                if chunking.recommendations:
                    st.markdown("**💡 Chunking Recommendations:**")
                    for rec in chunking.recommendations:
                        st.info(rec)
                
                st.markdown("---")
                
                st.markdown('<h3 class="sub-section-header">📋 Schema.org Analysis</h3>', unsafe_allow_html=True)
                
                schema = enhanced_report.schema_analysis
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("JSON-LD Items", schema.json_ld_items)
                with col2:
                    st.metric("Microdata Items", schema.microdata_items)
                with col3:
                    st.metric("Schema Quality", f"{schema.schema_quality_score:.1f}/100")
                
                if schema.entity_types:
                    st.markdown("**🏷️ Entity Types Found:**")
                    for entity_type in schema.entity_types:
                        st.write(f"• {entity_type}")
                
                if schema.llm_benefits:
                    st.markdown("**✅ LLM Benefits:**")
                    for benefit in schema.llm_benefits:
                        st.success(benefit)
                
                if schema.missing_opportunities:
                    st.markdown("**💡 Missing Opportunities:**")
                    for opportunity in schema.missing_opportunities:
                        st.info(opportunity)
                
                st.markdown("---")
                
                st.markdown('<h3 class="sub-section-header">🔄 Rendering Impact Analysis</h3>', unsafe_allow_html=True)
                
                rendering = enhanced_report.rendering_analysis
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Rendering Type", rendering.rendering_type)
                    st.metric("Initial Content Size", f"{rendering.initial_content_size:,} chars")
                with col2:
                    st.metric("JS Dependency Score", f"{rendering.javascript_dependency_score:.2f}")
                    st.metric("Visibility Score", f"{rendering.visibility_score:.1f}/100")
                
                st.markdown(f"**Framework Impact:** {rendering.framework_impact}")
                
                if rendering.ssr_benefits:
                    st.markdown("**✅ SSR Benefits:**")
                    for benefit in rendering.ssr_benefits:
                        st.success(benefit)
                
                if rendering.csr_limitations:
                    st.markdown("**❌ CSR Limitations:**")
                    for limitation in rendering.csr_limitations:
                        st.error(limitation)
                
                st.markdown("---")
                
                st.markdown('<h3 class="sub-section-header">👁️ CSS Visibility Analysis</h3>', unsafe_allow_html=True)
                
                css_analysis = enhanced_report.css_visibility_analysis
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Display: None", css_analysis['display_none_elements'])
                with col2:
                    st.metric("Visibility: Hidden", css_analysis['visibility_hidden_elements'])
                with col3:
                    st.metric("Total Hidden", css_analysis['total_hidden_elements'])
                
                st.info(f"**LLM Impact:** {css_analysis['llm_impact']}")
                st.markdown(f"*{css_analysis['explanation']}*")
                
                if css_analysis['recommendations']:
                    st.markdown("**💡 CSS Recommendations:**")
                    for rec in css_analysis['recommendations']:
                        st.info(rec)
                
                st.markdown("---")
                
                st.markdown('<h3 class="sub-section-header">💡 Enhanced Recommendations</h3>', unsafe_allow_html=True)
                
                if enhanced_report.critical_recommendations:
                    st.markdown("**🚨 Critical Issues:**")
                    for rec in enhanced_report.critical_recommendations:
                        st.error(rec)
                
                if enhanced_report.high_priority_recommendations:
                    st.markdown("**⚠️ High Priority:**")
                    for rec in enhanced_report.high_priority_recommendations:
                        st.warning(rec)
                
                if enhanced_report.medium_priority_recommendations:
                    st.markdown("**💡 Medium Priority:**")
                    for rec in enhanced_report.medium_priority_recommendations:
                        st.info(rec)
                
                st.markdown("---")
                
                st.markdown('<h3 class="sub-section-header">🔬 Technical Explanations</h3>', unsafe_allow_html=True)
                
                for key, explanation in enhanced_report.technical_explanations.items():
                    with st.expander(f"About {key.replace('_', ' ').title()}"):
                        st.markdown(explanation)
                
                st.markdown("**📚 Evidence Sources:**")
                for source in enhanced_report.evidence_sources:
                    st.write(f"• {source}")
            
            else:
                st.info("Enhanced LLM analysis not available. Run analysis with 'LLM Accessibility Only' or 'Comprehensive Analysis' focus.")
        
        with tabs[3]:  # LLMs.txt Analysis
            st.markdown('<h2 class="section-header">📄 LLMs.txt Analysis</h2>', unsafe_allow_html=True)
            
            if st.session_state.llms_txt_analysis and st.session_state.llms_txt_analysis.is_present:
                llms_analysis = st.session_state.llms_txt_analysis
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    status_icon = "✅" if llms_analysis.is_present else "❌"
                    st.metric("LLMs.txt Status", f"{status_icon} {'Present' if llms_analysis.is_present else 'Missing'}")
                with col2:
                    st.metric("Quality Score", f"{llms_analysis.quality_score:.1f}/100")
                with col3:
                    st.metric("Format Valid", "✅" if llms_analysis.format_valid else "❌")
                
                st.markdown("---")
                
                st.markdown('<h3 class="sub-section-header">📄 File Content</h3>', unsafe_allow_html=True)
                st.code(llms_analysis.content, language="markdown")
                
                st.markdown("---")
                
                st.markdown('<h3 class="sub-section-header">📋 Sections Analysis</h3>', unsafe_allow_html=True)
                
                for section_name, items in llms_analysis.sections.items():
                    if items:
                        with st.expander(f"{section_name.title()} ({len(items)} items)"):
                            for item in items:
                                st.write(f"• {item}")
                
                st.markdown("---")
                
                if llms_analysis.benefits:
                    st.markdown('<h3 class="sub-section-header">✅ Benefits</h3>', unsafe_allow_html=True)
                    for benefit in llms_analysis.benefits:
                        st.success(benefit)
                
                if llms_analysis.issues:
                    st.markdown('<h3 class="sub-section-header">⚠️ Issues</h3>', unsafe_allow_html=True)
                    for issue in llms_analysis.issues:
                        st.warning(issue)
                
                if llms_analysis.recommendations:
                    st.markdown('<h3 class="sub-section-header">💡 Recommendations</h3>', unsafe_allow_html=True)
                    for rec in llms_analysis.recommendations:
                        st.info(rec)
            
            else:
                st.error("🚨 No `llms.txt` file found at the website root!")
                st.markdown("""
                <div class="llms-txt-info-box">
                    <h5>💡 What is LLMs.txt and Why Does it Matter?</h5>
                    <p>The <code>llms.txt</code> file is an emerging standard for guiding Large Language Models (LLMs) to the most relevant and high-quality content on your website.</p>
                    <p><strong>Benefits of adopting <code>llms.txt</code>:</strong></p>
                    <ul>
                        <li>🎯 Directs AI crawlers to authoritative content.</li>
                        <li>✨ Improves brand representation in AI summaries and answers.</li>
                        <li>🧩 Complements <code>robots.txt</code> and <code>sitemap.xml</code> for AI optimization.</li>
                    </ul>
                    <p><strong>Action:</strong> Consider creating an <code>llms.txt</code> file at your site's root (e.g., <code>https://example.com/llms.txt</code>) to enhance LLM accessibility and content discovery.</p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("📄 Example llms.txt File"):
                    st.code("""
                    # Company Name - LLM Guide
                    
                    ## About
                    Brief description of site and content, e.g., "This site provides comprehensive documentation for our AI-powered analytics platform."
                    
                    ## Key Pages (Prioritize these for LLM summarization)
                    - /products/overview: Main product description
                    - /docs/api-reference: Our API documentation
                    - /blog/latest-features: Recent feature announcements
                    
                    ## Documentation (For deeper dives, less for quick summaries)
                    Developer guides and detailed tutorials at /docs/
                    
                    ## Contact
                    For support, visit /support/ or email support@example.com
                    
                    # You can also use 'Disallow' like robots.txt for sensitive areas,
                    # but its primary purpose is guidance, not exclusion.
                    # Disallow: /private-data/
                    """, language="markdown")
        
        with tabs[4]:  # Scraper Analysis
            st.markdown('<h2 class="section-header">🕷️ Scraper Analysis</h2>', unsafe_allow_html=True)
            
            if st.session_state.score:
                score = st.session_state.score
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Scraper Friendliness", f"{st.session_state.score.scraper_friendliness.total_score:.1f}/100", 
                             delta=f"Grade: {st.session_state.score.scraper_friendliness.grade}")
                with col2:
                    st.metric("Static Content Quality", f"{st.session_state.score.scraper_friendliness.static_content_quality.score:.1f}/25")
                with col3:
                    st.metric("Semantic HTML", f"{st.session_state.score.scraper_friendliness.semantic_html_structure.score:.1f}/20")
                
                st.markdown("---")
                
                st.markdown('<h3 class="sub-section-header">🎯 Scraper Friendliness Breakdown</h3>', unsafe_allow_html=True)
                
                scraper_components = [
                    st.session_state.score.scraper_friendliness.static_content_quality,
                    st.session_state.score.scraper_friendliness.semantic_html_structure,
                    st.session_state.score.scraper_friendliness.structured_data_implementation,
                    st.session_state.score.scraper_friendliness.meta_tag_completeness,
                    st.session_state.score.scraper_friendliness.javascript_dependency,
                    st.session_state.score.scraper_friendliness.crawler_accessibility
                ]
                
                for comp in scraper_components:
                    score_class = get_score_color_class(comp.percentage)
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
                
                st.markdown('<h3 class="sub-section-header">💡 Scraper Optimization Recommendations</h3>', unsafe_allow_html=True)
                
                scraper_recommendations = [r for r in st.session_state.score.recommendations 
                                         if r.category in ["static_content", "semantic_html", "structured_data", "meta_tags", "crawler_accessibility"]]
                
                if scraper_recommendations:
                    for rec in scraper_recommendations:
                        if rec.priority.value == "critical":
                            st.error(f"**{rec.priority.value.upper()}**: {rec.description}")
                        elif rec.priority.value == "high":
                            st.warning(f"**{rec.priority.value.upper()}**: {rec.description}")
                        else:
                            st.info(f"**{rec.priority.value.upper()}**: {rec.description}")
                        
                        if rec.code_example:
                            with st.expander("💻 Code Example"):
                                st.code(rec.code_example, language="html")
                else:
                    st.success("🎉 No scraper-specific recommendations needed!")
            else:
                st.info("Scraper analysis not available. Please run the analysis first with 'Comprehensive Analysis'.")
        
        with tabs[5]:  # SSR Detection
            st.markdown('<h2 class="section-header">🔍 Server-Side Rendering (SSR) Detection</h2>', unsafe_allow_html=True)
            
            if st.session_state.ssr_detection:
                ssr = st.session_state.ssr_detection
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if ssr.is_ssr:
                        st.success("✅ SSR Detected")
                    else:
                        st.warning("⚠️ No SSR Detected")
                
                with col2:
                    st.metric("Rendering Type", ssr.rendering_type.title())
                
                with col3:
                    st.metric("Confidence", f"{ssr.confidence:.1%}")
                
                st.markdown("---")
                
                st.markdown('<h3 class="sub-section-header">🎯 Framework Indicators</h3>', unsafe_allow_html=True)
                if ssr.framework_indicators:
                    for indicator in ssr.framework_indicators:
                        st.markdown(f"- {indicator}")
                else:
                    st.info("No specific framework indicators detected.")
                
                st.markdown('<h3 class="sub-section-header">🔍 Detection Evidence</h3>', unsafe_allow_html=True)
                if ssr.evidence:
                    for evidence in ssr.evidence:
                        st.markdown(f"- {evidence}")
                
                st.markdown('<h3 class="sub-section-header">⚡ Performance Indicators</h3>', unsafe_allow_html=True)
                if ssr.performance_indicators:
                    perf = ssr.performance_indicators
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Critical CSS", "✅" if perf.get('has_critical_css') else "❌")
                    with col2:
                        st.metric("Preload Links", "✅" if perf.get('has_preload_links') else "❌")
                    with col3:
                        st.metric("Resource Hints", "✅" if perf.get('has_resource_hints') else "❌")
                    with col4:
                        st.metric("Initial Content", f"{perf.get('estimated_initial_content', 0):,} chars")
                
                st.markdown('<h3 class="sub-section-header">💡 SSR Recommendations</h3>', unsafe_allow_html=True)
                if ssr.is_ssr:
                    st.success("🎉 Your website uses SSR! This is excellent for LLM accessibility and performance.")
                    st.info("""
                    **Benefits of SSR:**
                    - Content is immediately available to LLMs and crawlers.
                    - Improved SEO performance.
                    - Faster initial page load times.
                    - Enhanced accessibility for various agents.
                    """)
                else:
                    st.warning("⚠️ Your website may not be using SSR effectively, or is a Client-Side Rendered (CSR) application.")
                    st.info("""
                    **Consider implementing or enhancing SSR for:**
                    - Better LLM and scraper accessibility.
                    - Improved SEO and discoverability.
                    - Faster initial content delivery for users.
                    - Enhanced overall user experience.
                    """)
            else:
                st.info("SSR detection not available. Please run the analysis first with 'Comprehensive Analysis' or 'SSR Detection Only'.")
        
        with tabs[6]:  # Crawler Testing
            st.markdown('<h2 class="section-header">🕷️ Web Crawler Testing</h2>', unsafe_allow_html=True)
            
            if st.session_state.crawler_analysis:
                crawler_results = st.session_state.crawler_analysis
                
                st.markdown('<h3 class="sub-section-header">📊 Crawler Accessibility Summary</h3>', unsafe_allow_html=True)
                
                cols = st.columns(len(crawler_results))
                for i, (crawler_type, result) in enumerate(crawler_results.items()):
                    with cols[i]:
                        score_class = get_score_color_class(result.accessibility_score).replace('score-', '')
                        st.markdown(f"""
                        <div class="score-card {score_class}" style="padding: 1rem; margin-bottom: 1rem;">
                            <div class="score-card-header" style="font-size: 1em;">{result.crawler_name}</div>
                            <div class="score-value" style="font-size: 1.8em;">{result.accessibility_score:.1f}/100</div>
                            <div class="score-grade" style="font-size: 0.9em;">Grade: {_get_grade(result.accessibility_score)}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                st.markdown('<h3 class="sub-section-header">🔍 Detailed Crawler Analysis</h3>', unsafe_allow_html=True)
                for crawler_type, result in crawler_results.items():
                    with st.expander(f"⚙️ {result.crawler_name} Analysis Details", expanded=False):
                        
                        st.markdown(f"**Accessibility Score:** {result.accessibility_score:.1f}/100")
                        st.progress(result.accessibility_score / 100)
                        
                        if result.content_accessible:
                            st.markdown("**✅ Accessible Content:**")
                            for content_type, details in result.content_accessible.items():
                                if isinstance(details, dict) and details.get('available'):
                                    st.markdown(f"- **{content_type.replace('_', ' ').title()}**: {details.get('explanation', '')}")
                        
                        if result.content_inaccessible:
                            st.markdown("**❌ Inaccessible Content:**")
                            for content_type, details in result.content_inaccessible.items():
                                if isinstance(details, dict) and not details.get('available', True):
                                    impact = details.get('impact', 'Unknown')
                                    explanation = details.get('explanation', '')
                                    st.markdown(f"- **{content_type.replace('_', ' ').title()}**: {explanation} (Impact: {impact})")
                        
                        if result.evidence:
                            st.markdown("**🔍 Evidence:**")
                            for evidence in result.evidence:
                                st.markdown(f"- {evidence}")
                        
                        if result.recommendations:
                            st.markdown("**💡 Recommendations:**")
                            for rec in result.recommendations:
                                if 'CRITICAL' in rec:
                                    st.error(rec)
                                elif 'HIGH' in rec:
                                    st.warning(rec)
                                else:
                                    st.info(rec)
            else:
                st.info("Crawler testing not available. Please run 'Web Crawler Testing' analysis first.")
        
        with tabs[7]:  # Evidence Report
            st.markdown('<h2 class="section-header">📊 Evidence Report</h2>', unsafe_allow_html=True)
            
            if st.session_state.evidence_report:
                report = st.session_state.evidence_report
                
                st.markdown('<h3 class="sub-section-header">📋 Analysis Summary</h3>', unsafe_allow_html=True)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="score-card neutral" style="background: #e9f0f6; border-left-color: #667eea;">
                        <div class="score-card-header">📊 Overall Evidence Summary</div>
                        <p><strong>Analysis ID:</strong> <code>{report.analysis_id}</code></p>
                        <p><strong>Crawlers Tested:</strong> {report.summary['total_crawlers']}</p>
                        <p><strong>Total Issues Found:</strong> {report.summary['total_issues']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="score-card neutral" style="background: #e9f0f6; border-left-color: #ef4444;">
                        <div class="score-card-header">🚨 Issue Priority Breakdown</div>
                        <div style="margin-bottom: 0.5rem;">
                            <span class="score-poor">Critical:</span> {report.summary['critical_issues']}
                        </div>
                        <div style="margin-bottom: 0.5rem;">
                            <span class="score-fair">High:</span> {report.summary['high_issues']}
                        </div>
                        <div style="margin-bottom: 0.5rem;">
                            <span style="color: #f1c40f; font-weight: bold;">Medium:</span> {report.summary['medium_issues']}
                        </div>
                        <div>
                            <span class="score-excellent">Low:</span> {report.summary['low_issues']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown('<h3 class="sub-section-header">🔍 Detailed Evidence per Crawler</h3>', unsafe_allow_html=True)
                
                if report.crawler_comparisons:
                    for crawler_name, evidence in report.crawler_comparisons.items():
                        with st.expander(f"🤖 {evidence.crawler_type} - Score: {evidence.accessibility_score:.1f}/100", expanded=False):
                            col1, col2 = st.columns([1, 2])
                            
                            with col1:
                                st.metric("Accessibility Score", f"{evidence.accessibility_score:.1f}/100")
                                st.metric("Issues Found", len(evidence.accessibility_issues))
                            
                            with col2:
                                if evidence.accessibility_issues:
                                    st.write("**Issues Identified:**")
                                    for issue in evidence.accessibility_issues[:5]:
                                        st.write(f"• {issue}")
                                    if len(evidence.accessibility_issues) > 5:
                                        st.write(f"... and {len(evidence.accessibility_issues) - 5} more issues.")
                                else:
                                    st.success("No issues found for this crawler!")
                
                if report.recommendations:
                    st.markdown('<h3 class="sub-section-header">💡 Key Recommendations from Evidence</h3>', unsafe_allow_html=True)
                    
                    critical_recs = [r for r in report.recommendations if 'CRITICAL' in r]
                    high_recs = [r for r in report.recommendations if 'HIGH' in r and r not in critical_recs]
                    other_recs = [r for r in report.recommendations if r not in critical_recs + high_recs]
                    
                    if critical_recs:
                        st.error("🚨 **Critical Issues:**")
                        for rec in critical_recs[:3]:
                            st.write(f"• {rec}")
                        if len(critical_recs) > 3: st.write(f"... and {len(critical_recs) - 3} more.")
                    
                    if high_recs:
                        st.warning("⚠️ **High Priority:**")
                        for rec in high_recs[:3]:
                            st.write(f"• {rec}")
                        if len(high_recs) > 3: st.write(f"... and {len(high_recs) - 3} more.")
                    
                    if other_recs:
                        st.info("📋 **Other Recommendations:**")
                        for rec in other_recs[:3]:
                            st.write(f"• {rec}")
                        if len(other_recs) > 3: st.write(f"... and {len(other_recs) - 3} more.")
            else:
                st.info("📋 No evidence report available. Run analysis with 'Generate Detailed Evidence Report' enabled.")
        
        with tabs[8]:  # Content
            st.markdown('<h2 class="section-header">📝 Content Analysis</h2>', unsafe_allow_html=True)
            
            if st.session_state.static_result and st.session_state.static_result.content_analysis:
                content = st.session_state.static_result.content_analysis
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Characters", f"{content.character_count:,}")
                col2.metric("Words", f"{content.word_count:,}")
                col3.metric("Estimated Tokens", f"{content.estimated_tokens:,}")
                col4.metric("Paragraphs", content.paragraphs)
                
                st.markdown("---")
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Links", content.links)
                col2.metric("Images", content.images)
                col3.metric("Tables", content.tables)
                col4.metric("Lists", content.lists)
                
                st.markdown("---")
                
                st.markdown('<h3 class="sub-section-header">Content Preview</h3>', unsafe_allow_html=True)
                with st.expander("View extracted text content", expanded=False):
                    st.text_area(
                        "Extracted Content",
                        content.text_content[:5000] + ("..." if len(content.text_content) > 5000 else ""),
                        height=300
                    )
            else:
                st.info("Content analysis not available. Please run the analysis first.")
        
        with tabs[9]:  # Structure
            st.markdown('<h2 class="section-header">🏗️ HTML Structure Analysis</h2>', unsafe_allow_html=True)
            
            if st.session_state.static_result and st.session_state.static_result.structure_analysis:
                structure = st.session_state.static_result.structure_analysis
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Elements", structure.total_elements)
                col2.metric("DOM Depth", structure.nested_depth)
                col3.metric("Semantic Elements", len(structure.semantic_elements))
                
                st.markdown("---")
                
                st.markdown('<h3 class="sub-section-header">Heading Hierarchy</h3>', unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                
                with col1:
                    hierarchy = structure.heading_hierarchy
                    st.markdown(f"**H1**: {len(hierarchy.h1)}")
                    for h1 in hierarchy.h1[:5]:
                        st.markdown(f"- {h1}")
                    if len(hierarchy.h1) > 5: st.markdown("...")
                    
                    st.markdown(f"**H2**: {len(hierarchy.h2)}")
                    for h2 in hierarchy.h2[:5]:
                        st.markdown(f"- {h2}")
                    if len(hierarchy.h2) > 5: st.markdown("...")
                    
                    st.markdown(f"**H3**: {len(hierarchy.h3)}")
                    for h3 in hierarchy.h3[:5]:
                        st.markdown(f"- {h3}")
                    if len(hierarchy.h3) > 5: st.markdown("...")

                with col2:
                    st.markdown('<h3 class="sub-section-header">Semantic HTML Elements</h3>', unsafe_allow_html=True)
                    if structure.semantic_elements:
                        for elem in list(set(structure.semantic_elements))[:10]: # Display unique top 10
                            st.markdown(f"- `<{elem}>`")
                        if len(set(structure.semantic_elements)) > 10: st.markdown("...")
                    else:
                        st.warning("No semantic HTML5 elements detected.")
            else:
                st.info("Structure analysis not available. Please run the analysis first.")
        
        with tabs[10]:  # Meta Data
            st.markdown('<h2 class="section-header">🏷️ Meta Data & Structured Data</h2>', unsafe_allow_html=True)
            
            if st.session_state.static_result and st.session_state.static_result.meta_analysis:
                meta = st.session_state.static_result.meta_analysis
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<h3 class="sub-section-header">Basic Meta Tags</h3>', unsafe_allow_html=True)
                    st.markdown(f"**Title**: {meta.title or 'Not found'}")
                    st.markdown(f"**Description**: {meta.description or 'Not found'}")
                    st.markdown(f"**Canonical URL**: {meta.canonical_url or 'Not found'}")
                    
                    st.markdown('<h3 class="sub-section-header">Open Graph Tags</h3>', unsafe_allow_html=True)
                    if meta.open_graph_tags:
                        for key, value in list(meta.open_graph_tags.items())[:10]:
                            st.markdown(f"**{key}**: {value}")
                        if len(meta.open_graph_tags) > 10: st.markdown("...")
                    else:
                        st.warning("No Open Graph tags found.")
                
                with col2:
                    st.markdown('<h3 class="sub-section-header">Twitter Card Tags</h3>', unsafe_allow_html=True)
                    if meta.twitter_card_tags:
                        for key, value in meta.twitter_card_tags.items():
                            st.markdown(f"**{key}**: {value}")
                    else:
                        st.warning("No Twitter Card tags found.")
                    
                    st.markdown('<h3 class="sub-section-header">Structured Data</h3>', unsafe_allow_html=True)
                    st.markdown(f"- **JSON-LD**: {'✅ Found' if meta.has_json_ld else '❌ Not found'}")
                    st.markdown(f"- **Microdata**: {'✅ Found' if meta.has_microdata else '❌ Not found'}")
                    st.markdown(f"- **RDFa**: {'✅ Found' if meta.has_rdfa else '❌ Not found'}")
                    
                    if meta.structured_data:
                        with st.expander(f"View {len(meta.structured_data)} structured data items", expanded=False):
                            for i, data in enumerate(meta.structured_data[:5], 1):
                                st.json(data.data)
                            if len(meta.structured_data) > 5: st.markdown("...")
            else:
                st.info("Meta data analysis not available. Please run the analysis first.")
        
        with tabs[11]:  # JavaScript
            st.markdown('<h2 class="section-header">⚡ JavaScript Analysis</h2>', unsafe_allow_html=True)
            
            if st.session_state.static_result and st.session_state.static_result.javascript_analysis:
                js = st.session_state.static_result.javascript_analysis
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Scripts", js.total_scripts)
                col2.metric("Inline Scripts", js.inline_scripts)
                col3.metric("External Scripts", js.external_scripts)
                col4.metric("JS Frameworks", len(js.frameworks))
                
                st.markdown("---")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("SPA Detected", "Yes" if js.is_spa else "No")
                col2.metric("AJAX Usage", "Yes" if js.has_ajax else "No")
                col3.metric("Dynamic Content", "Yes" if js.dynamic_content_detected else "No")
                
                if js.frameworks:
                    st.markdown('<h3 class="sub-section-header">Detected Frameworks</h3>', unsafe_allow_html=True)
                    for fw in js.frameworks:
                        st.markdown(f"- **{fw.name}** (confidence: {fw.confidence})")
                
                if st.session_state.comparison:
                    st.markdown("---")
                    st.markdown('<h3 class="sub-section-header">Static vs Dynamic Content Comparison</h3>', unsafe_allow_html=True)
                    
                    comp = st.session_state.comparison
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Similarity Score", f"{comp.similarity_score:.1%}")
                    col2.metric("Content Difference", f"{comp.content_difference} chars")
                    col3.metric("JS Dependent Content", "Yes" if comp.javascript_dependent else "No")
                    
                    if comp.missing_in_static:
                        with st.expander(f"⚠️ {len(comp.missing_in_static)} items loaded dynamically (missing in static HTML)", expanded=False):
                            for item in comp.missing_in_static[:10]:
                                st.markdown(f"- {item}")
                            if len(comp.missing_in_static) > 10: st.markdown("...")
            else:
                st.info("JavaScript analysis not available. Please run the analysis first (consider 'Comprehensive Analysis').")
        
        with tabs[12]:  # Recommendations
            st.markdown('<h2 class="section-header">💡 Optimization Recommendations</h2>', unsafe_allow_html=True)
            
            if st.session_state.score and st.session_state.score.recommendations:
                # Group by priority
                critical = [r for r in st.session_state.score.recommendations if r.priority.value == "critical"]
                high = [r for r in st.session_state.score.recommendations if r.priority.value == "high"]
                medium = [r for r in st.session_state.score.recommendations if r.priority.value == "medium"]
                low = [r for r in st.session_state.score.recommendations if r.priority.value == "low"]
                
                def display_recommendations_group(recs, emoji, title_text, color_code):
                    if recs:
                        st.markdown(f'<h3 class="sub-section-header" style="color: {color_code};">{emoji} {title_text} ({len(recs)})</h3>', unsafe_allow_html=True)
                        for i, rec in enumerate(recs):
                            with st.expander(f"**{i+1}.** {rec.title} (**Category**: {rec.category.replace('_', ' ').title()})"):
                                st.markdown(rec.description)
                                col_diff, col_impact = st.columns(2)
                                with col_diff:
                                    st.markdown(f"**Difficulty**: `{rec.difficulty.value.title()}`")
                                with col_impact:
                                    st.markdown(f"**Impact**: `{rec.impact.value.title()}`")
                                
                                if rec.code_example:
                                    st.markdown("---")
                                    st.markdown("**💻 Code Example:**")
                                    st.code(rec.code_example, language="html")
                                if rec.resources:
                                    st.markdown("---")
                                    st.markdown("**📚 Resources:**")
                                    for resource in rec.resources:
                                        st.markdown(f"- [{resource}]({resource})")
                                # No explicit divider needed inside expander, Streamlit handles it well
                
                display_recommendations_group(critical, "🚨", "Critical Issues", "#EF4444") # Red
                display_recommendations_group(high, "⚠️", "High Priority Recommendations", "#F59E0B") # Orange
                display_recommendations_group(medium, "💡", "Medium Priority Recommendations", "#F1C40F") # Yellow-Orange
                display_recommendations_group(low, "🟢", "Low Priority Recommendations", "#10B981") # Green
                
                if not (critical or high or medium or low):
                    st.success("🎉 No significant recommendations found - your site is well-optimized!")
            else:
                st.info("No comprehensive scoring analysis available. Run 'Comprehensive Analysis' to see optimization recommendations.")
        
        with tabs[13]: # Export Report
            st.markdown('<h2 class="section-header">📥 Export Comprehensive Report</h2>', unsafe_allow_html=True)
            
            # Create report data once for download section
            report_data = ReportData(
                url=st.session_state.analyzed_url,
                analysis_type=st.session_state.last_analysis_type,
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                analysis_id=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                static_result=st.session_state.static_result,
                dynamic_result=st.session_state.dynamic_result,
                comparison=st.session_state.comparison,
                score=st.session_state.score,
                llm_report=st.session_state.llm_report,
                enhanced_llm_report=st.session_state.enhanced_llm_report,
                llms_txt_analysis=st.session_state.llms_txt_analysis,
                ssr_detection=st.session_state.ssr_detection,
                crawler_analysis=st.session_state.crawler_analysis,
                evidence_report=st.session_state.evidence_report,
                analysis_duration=0.0, # Placeholder, could be calculated in perform_analysis
                user_agent="Web Scraper & LLM Analyzer",
                analysis_notes=f"Analysis type: {st.session_state.last_analysis_type}"
            )
            
            report_generator = ComprehensiveReportGenerator()
            
            st.markdown('<h3 class="sub-section-header">Download Formats</h3>', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                try:
                    html_report = report_generator.generate_report(report_data, 'html')
                    st.download_button(
                        label="📄 Download HTML Report",
                        data=html_report,
                        file_name=f"web_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                        mime="text/html",
                        help="Download a comprehensive HTML report with charts and visualizations."
                    )
                except Exception as e:
                    st.error(f"Error generating HTML report: {str(e)}")
            
            with col2:
                try:
                    markdown_report = report_generator.generate_report(report_data, 'markdown')
                    st.download_button(
                        label="📋 Download Markdown Report",
                        data=markdown_report,
                        file_name=f"web_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown",
                        help="Download a Markdown report suitable for documentation."
                    )
                except Exception as e:
                    st.error(f"Error generating Markdown report: {str(e)}")
            
            with col3:
                try:
                    json_report = report_generator.generate_report(report_data, 'json')
                    st.download_button(
                        label="📊 Download JSON Data",
                        data=json_report,
                        file_name=f"web_analysis_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        help="Download raw analysis data in JSON format for further processing."
                    )
                except Exception as e:
                    st.error(f"Error generating JSON report: {str(e)}")
            
            with col4:
                try:
                    if st.session_state.evidence_report:
                        evidence_capture = EvidenceCapture()
                        evidence_html = evidence_capture.export_evidence_report(
                            st.session_state.evidence_report.analysis_id, 'html'
                        )
                        
                        st.download_button(
                            label="📈 Download Evidence Report",
                            data=evidence_html,
                            file_name=f"evidence_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                            mime="text/html",
                            help="Download a detailed evidence report capturing specific findings."
                        )
                    else:
                        st.info("No evidence report available for download.")
                except Exception as e:
                    st.error(f"Error generating evidence report: {str(e)}")

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