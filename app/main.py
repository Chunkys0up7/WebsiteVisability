"""
Main Streamlit Application

Web interface for analyzing website scraper-friendliness and LLM accessibility.
"""

import streamlit as st
import logging
from datetime import datetime

from src.analyzers import StaticAnalyzer, DynamicAnalyzer, ContentComparator, ScoringEngine
from src.analyzers.llm_accessibility_analyzer import LLMAccessibilityAnalyzer
from src.analyzers.separate_analyzer import SeparateAnalyzer
from src.analyzers.ssr_detector import SSRDetector
from src.analyzers.web_crawler_analyzer import WebCrawlerAnalyzer
from src.analyzers.evidence_capture import EvidenceCapture
from src.analyzers.enhanced_llm_analyzer import EnhancedLLMAccessibilityAnalyzer
from src.analyzers.llms_txt_analyzer import LLMsTxtAnalyzer
from src.utils.validators import URLValidator
from src.utils.report_generator import ComprehensiveReportGenerator, ReportData
from src.models.analysis_result import AnalysisResult
from src.models.scoring_models import Score

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
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #667eea;
    }
    .score-excellent {
        color: #10b981;
        font-weight: bold;
    }
    .score-good {
        color: #3b82f6;
        font-weight: bold;
    }
    .score-fair {
        color: #f59e0b;
        font-weight: bold;
    }
    .score-poor {
        color: #ef4444;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-right: 20px;
        padding-left: 20px;
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
        # Always need static analysis as base for most analysis types
        static_result = None
        if analysis_type in ["Comprehensive Analysis", "LLM Accessibility Only", "Web Crawler Testing", "SSR Detection Only"]:
            with st.spinner("🔍 Performing static analysis..."):
                static_analyzer = StaticAnalyzer(timeout=30)
                static_result = static_analyzer.analyze(url)
                
                if static_result.status != "success":
                    st.error(f"Static analysis failed: {static_result.message}")
                    return False
                
                st.session_state.static_result = static_result
                logger.info(f"Static analysis completed for {url}")
        
        # Dynamic Analysis (only for Comprehensive Analysis)
        dynamic_result = None
        if analysis_type == "Comprehensive Analysis" and analyze_dynamic:
            with st.spinner("🌐 Performing dynamic analysis (rendering with browser)..."):
                try:
                    dynamic_analyzer = DynamicAnalyzer(timeout=30, headless=True)
                    dynamic_result = dynamic_analyzer.analyze(url)
                    
                    if dynamic_result.status != "success":
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
            with st.spinner("📊 Comparing static vs dynamic content..."):
                comparator = ContentComparator()
                comparison = comparator.compare(static_result, dynamic_result)
                st.session_state.comparison = comparison
                logger.info(f"Content comparison completed for {url}")
        
        # LLM Accessibility Analysis (for Comprehensive Analysis and LLM Accessibility Only)
        if analysis_type in ["Comprehensive Analysis", "LLM Accessibility Only"]:
            with st.spinner("🤖 Analyzing LLM accessibility..."):
                llm_analyzer = LLMAccessibilityAnalyzer()
                llm_report = llm_analyzer.analyze(static_result)
                st.session_state.llm_report = llm_report
                logger.info(f"LLM accessibility analysis completed for {url}")
                
                # Enhanced LLM Analysis
                with st.spinner("🔬 Performing enhanced LLM analysis..."):
                    enhanced_llm_analyzer = EnhancedLLMAccessibilityAnalyzer()
                    enhanced_llm_report = enhanced_llm_analyzer.analyze(static_result)
                    st.session_state.enhanced_llm_report = enhanced_llm_report
                    logger.info(f"Enhanced LLM analysis completed for {url}")
                
                # LLMs.txt Analysis
                with st.spinner("📄 Analyzing llms.txt file..."):
                    llms_txt_analyzer = LLMsTxtAnalyzer()
                    llms_txt_analysis = llms_txt_analyzer.analyze(url)
                    st.session_state.llms_txt_analysis = llms_txt_analysis
                    logger.info(f"LLMs.txt analysis completed for {url}")
        
        # SSR Detection
        if analysis_type in ["Comprehensive Analysis", "SSR Detection Only"]:
            with st.spinner("🔍 Detecting SSR patterns..."):
                ssr_detector = SSRDetector()
                ssr_detection = ssr_detector.detect_ssr(static_result.content_analysis.text_content if static_result.content_analysis else "", 
                                                        static_result.javascript_analysis)
                st.session_state.ssr_detection = ssr_detection
                logger.info(f"SSR detection completed for {url}")
        
        # Web Crawler Testing
        if analysis_type in ["Comprehensive Analysis", "Web Crawler Testing"]:
            if crawler_types is None:
                crawler_types = ["llm", "googlebot"]
            
            crawler_analyzer = WebCrawlerAnalyzer()
            crawler_results = {}
            
            for crawler_type in crawler_types:
                with st.spinner(f"🕷️ Testing {crawler_type} accessibility..."):
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
            with st.spinner("📊 Capturing evidence and generating reports..."):
                evidence_capture = EvidenceCapture()
                
                # Create evidence for different analysis types
                evidence_data = {}
                
                # Add crawler analysis evidence if available
                if st.session_state.crawler_analysis:
                    evidence_data.update(st.session_state.crawler_analysis)
                
                # Add LLM analysis evidence if available
                if st.session_state.llm_report:
                    # Create a mock crawler result for LLM analysis
                    llm_evidence = type('obj', (object,), {
                        'crawler_name': 'LLM Analysis',
                        'accessibility_score': st.session_state.llm_report.overall_score,
                        'content_accessible': st.session_state.llm_report.accessible_content,
                        'content_inaccessible': st.session_state.llm_report.inaccessible_content,
                        'evidence': [f"LLM accessibility score: {st.session_state.llm_report.overall_score:.1f}"],
                        'recommendations': st.session_state.llm_report.recommendations,
                        'accessibility_issues': st.session_state.llm_report.limitations
                    })()
                    evidence_data['llm_analysis'] = llm_evidence
                
                # Add SSR detection evidence if available
                if st.session_state.ssr_detection:
                    ssr_evidence = type('obj', (object,), {
                        'crawler_name': 'SSR Detection',
                        'accessibility_score': st.session_state.ssr_detection.confidence * 100,
                        'content_accessible': {'ssr_detected': st.session_state.ssr_detection.is_ssr},
                        'content_inaccessible': {'rendering_type': st.session_state.ssr_detection.rendering_type},
                        'evidence': st.session_state.ssr_detection.evidence,
                        'recommendations': ['SSR detection completed'] if st.session_state.ssr_detection.is_ssr else ['Consider implementing SSR'],
                        'accessibility_issues': ['SSR not detected'] if not st.session_state.ssr_detection.is_ssr else []
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
            with st.spinner("⚡ Calculating scores and generating recommendations..."):
                scoring_engine = ScoringEngine()
                score = scoring_engine.calculate_score(static_result, comparison)
                st.session_state.score = score
                logger.info(f"Scoring completed for {url}")
        
        st.session_state.analysis_complete = True
        st.session_state.analyzed_url = url
        return True
        
    except Exception as e:
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
        
        url_input = st.text_input(
            "Website URL",
            placeholder="https://example.com",
            help="Enter the full URL including https://"
        )
        
        analyze_dynamic = st.checkbox(
            "Include dynamic analysis (⚠️ Disabled on Windows Store Python)",
            value=False,
            disabled=True,
            help="Dynamic analysis is not supported on Windows Store Python due to asyncio limitations. Static analysis provides comprehensive LLM accessibility insights."
        )
        
        st.markdown("---")
        
        st.subheader("🔍 Analysis Options")
        
        analysis_type = st.selectbox(
            "Analysis Focus",
            ["Comprehensive Analysis", "LLM Accessibility Only", "Web Crawler Testing", "SSR Detection Only"],
            help="Choose the type of analysis to perform"
        )
        
        if analysis_type == "Web Crawler Testing":
            crawler_types = st.multiselect(
                "Select Crawlers to Test",
                ["googlebot", "bingbot", "llm", "basic_scraper", "social_crawler"],
                default=["llm", "googlebot"],
                help="Choose which crawler types to test"
            )
        
        capture_evidence = st.checkbox(
            "Capture Evidence",
            value=True,
            help="Capture detailed evidence and generate reports"
        )
        
        analyze_button = st.button("🚀 Analyze Website", type="primary", use_container_width=True)
        
        st.markdown("---")
        
        # Info section
        with st.expander("ℹ️ About This Tool"):
            st.markdown("""
            This tool analyzes websites to determine:
            
            - **Scraper Accessibility**: What content can be extracted by web scrapers
            - **LLM Accessibility**: How well the content is structured for AI understanding
            - **JavaScript Dependency**: Content that requires JavaScript to load
            - **SEO & Metadata**: Quality of meta tags and structured data
            
            The analysis provides actionable recommendations to improve your site's 
            accessibility to both scrapers and LLMs.
            """)
        
        with st.expander("📊 Scoring Breakdown"):
            st.markdown("""
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
            st.error("⚠️ Please enter a URL")
        else:
            # Validate and normalize URL
            is_valid, normalized_url, error_msg = URLValidator.validate_and_normalize(url_input)
            if not is_valid:
                st.error(f"⚠️ {error_msg}")
            else:
                url_input = normalized_url
                st.session_state.analysis_complete = False
                success = perform_analysis(url_input, analyze_dynamic, analysis_type, 
                                         crawler_types if analysis_type == "Web Crawler Testing" else None, 
                                         capture_evidence)
                
                if success:
                    st.success("✅ Analysis complete!")
    
    # Display results
    if st.session_state.analysis_complete:
        st.markdown("---")
        
        # Quick Overview
        if st.session_state.score:
            score = st.session_state.score
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                scraper_score = st.session_state.score.scraper_friendliness.total_score
                scraper_grade = st.session_state.score.scraper_friendliness.grade
                score_class = get_score_color_class(scraper_score)
                st.metric(
                    "Scraper Friendliness",
                    f"{scraper_score:.1f}/100",
                    delta=f"Grade: {scraper_grade}"
                )
        
            with col2:
                llm_score = st.session_state.score.llm_accessibility.total_score
                llm_grade = st.session_state.score.llm_accessibility.grade
                score_class = get_score_color_class(llm_score)
                st.metric(
                    "LLM Accessibility",
                    f"{llm_score:.1f}/100",
                    delta=f"Grade: {llm_grade}"
                )
        
            with col3:
                if st.session_state.static_result:
                    word_count = st.session_state.static_result.content_analysis.word_count
                    st.metric(
                        "Word Count",
                        f"{word_count:,}",
                        help="Total words found in static HTML"
                    )
        
            with col4:
                recommendations_count = len(st.session_state.score.recommendations)
                critical_count = len([r for r in st.session_state.score.recommendations if r.priority.value == "critical"])
                st.metric(
                    "Recommendations",
                    recommendations_count,
                    delta=f"{critical_count} critical" if critical_count > 0 else "No critical issues"
                )
        
        else:
            # Show analysis type specific overview when no score is available
            st.subheader("📊 Analysis Overview")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.session_state.enhanced_llm_report:
                    st.metric(
                        "Enhanced LLM Score",
                        f"{st.session_state.enhanced_llm_report.overall_score:.1f}/100",
                        delta=f"Grade: {st.session_state.enhanced_llm_report.grade}"
                    )
                elif st.session_state.llm_report:
                    st.metric(
                        "LLM Accessibility Score",
                        f"{st.session_state.llm_report.overall_score:.1f}/100",
                        delta=f"Grade: {st.session_state.llm_report.grade}"
                    )
            
            with col2:
                if st.session_state.ssr_detection:
                    ssr_status = "✅ SSR Detected" if st.session_state.ssr_detection.is_ssr else "❌ No SSR"
                    st.metric(
                        "SSR Status",
                        ssr_status,
                        delta=f"Confidence: {st.session_state.ssr_detection.confidence:.1%}"
                    )
            
            with col3:
                if st.session_state.static_result and st.session_state.static_result.content_analysis:
                    word_count = st.session_state.static_result.content_analysis.word_count
                    st.metric(
                        "Content Size",
                        f"{word_count:,} words",
                        delta=f"{st.session_state.static_result.content_analysis.character_count:,} chars"
                    )
        
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
            "💡 Recommendations"
        ])
        
        with tabs[0]:  # Overview
            st.header("Analysis Overview")
            
            if st.session_state.score:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🎯 Scraper Friendliness Breakdown")
                    
                    components = [
                        st.session_state.score.scraper_friendliness.static_content_quality,
                        st.session_state.score.scraper_friendliness.semantic_html_structure,
                        st.session_state.score.scraper_friendliness.structured_data_implementation,
                        st.session_state.score.scraper_friendliness.meta_tag_completeness,
                        st.session_state.score.scraper_friendliness.javascript_dependency,
                        st.session_state.score.scraper_friendliness.crawler_accessibility
                    ]
                
                for comp in components:
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
                
                with col2:
                    st.subheader("🤖 LLM Accessibility Breakdown")
                    
                    st.info("""
                    LLM scoring emphasizes content quality and semantic structure over
                    JavaScript dependency, as LLMs can use dynamic rendering.
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
            else:
                # Show analysis-specific overview when no score is available
                st.subheader("📊 Analysis Results")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.session_state.enhanced_llm_report:
                        st.metric(
                            "Enhanced LLM Score",
                            f"{st.session_state.enhanced_llm_report.overall_score:.1f}/100",
                            delta=f"Grade: {st.session_state.enhanced_llm_report.grade}"
                        )
                    elif st.session_state.llm_report:
                        st.metric(
                            "LLM Accessibility Score",
                            f"{st.session_state.llm_report.overall_score:.1f}/100",
                            delta=f"Grade: {st.session_state.llm_report.grade}"
                        )
                
                with col2:
                    if st.session_state.ssr_detection:
                        ssr_status = "✅ SSR Detected" if st.session_state.ssr_detection.is_ssr else "❌ No SSR"
                        st.metric(
                            "SSR Status",
                            ssr_status,
                            delta=f"Confidence: {st.session_state.ssr_detection.confidence:.1%}"
                        )
                
                with col3:
                    if st.session_state.static_result and st.session_state.static_result.content_analysis:
                        word_count = st.session_state.static_result.content_analysis.word_count
                        st.metric(
                            "Content Size",
                            f"{word_count:,} words",
                            delta=f"{st.session_state.static_result.content_analysis.character_count:,} chars"
                        )
        
        with tabs[1]:  # LLM Analysis
            st.header("🤖 LLM Accessibility Analysis")
            
            if st.session_state.llm_report:
                llm_report = st.session_state.llm_report
                
                # Overall Score
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("LLM Accessibility Score", f"{llm_report.overall_score:.1f}/100", 
                             delta=f"Grade: {llm_report.grade}")
                with col2:
                    st.metric("Accessible Content", f"{len(llm_report.accessible_content)} categories")
                with col3:
                    st.metric("Limitations Found", f"{len(llm_report.limitations)} issues")
                
                st.markdown("---")
                
                # What LLMs CAN Access
                st.subheader("✅ What LLMs CAN Access")
                
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
                
                # What LLMs CANNOT Access
                st.subheader("❌ What LLMs CANNOT Access")
                
                inaccessible = llm_report.inaccessible_content
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**⚡ JavaScript-Dependent Content**")
                    js_content = inaccessible['javascript_dependent_content']
                    if js_content['dynamic_content']:
                        st.error("🚨 Dynamic content detected - LLMs cannot execute JavaScript")
                        st.markdown(f"**Scripts detected:** {js_content['total_scripts']}")
                        if js_content["frameworks_detected"]:
                            st.markdown(f"**Frameworks:** {', '.join(js_content['frameworks_detected'])}")
                    if js_content['ajax_content']:
                        st.error("🚨 AJAX content detected - Not accessible to LLMs")
                    if js_content['spa_content']:
                        st.error("🚨 Single Page Application detected - Requires JavaScript")
                    
                    # Show technical details
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
                                st.markdown(f"- {citation}")
                    
                    st.markdown(f"*{js_content['explanation']}*")
                    
                    st.markdown("**👁️ CSS-Hidden Content**")
                    hidden_content = inaccessible['css_hidden_content']
                    if hidden_content['hidden_elements']:
                        st.warning(f"⚠️ {len(hidden_content['hidden_elements'])} elements hidden from LLMs")
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
                
                # Specific Limitations
                st.subheader("⚠️ Specific Limitations Identified")
                
                if llm_report.limitations:
                    for i, limitation in enumerate(llm_report.limitations, 1):
                        st.markdown(f"**{i}.** {limitation}")
                else:
                    st.success("🎉 No major limitations identified!")
                
                st.markdown("---")
                
                # Recommendations
                st.subheader("💡 Recommendations for Better LLM Access")
                
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
                
                # Technical Analysis
                st.subheader("🔬 Technical Analysis")
                
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
                st.warning("LLM analysis not available. Please run the analysis first.")
        
        with tabs[2]:  # Enhanced LLM Analysis
            st.header("🔬 Enhanced LLM Analysis")
            
            if st.session_state.enhanced_llm_report:
                enhanced_report = st.session_state.enhanced_llm_report
                
                # Overall Score
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Enhanced LLM Score", f"{enhanced_report.overall_score:.1f}/100", 
                             delta=f"Grade: {enhanced_report.grade}")
                with col2:
                    st.metric("Semantic HTML Score", f"{enhanced_report.semantic_html_score:.1f}/100")
                with col3:
                    st.metric("JavaScript Impact", f"{enhanced_report.javascript_impact_score:.1f}/100")
                
                st.markdown("---")
                
                # Crawler-Specific Analysis
                st.subheader("🕷️ LLM Crawler Capabilities")
                
                for crawler_name, capability in enhanced_report.crawler_analysis.items():
                    with st.expander(f"{capability.name} Analysis"):
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
                
                # Content Chunking Analysis
                st.subheader("📊 Content Chunking Analysis")
                
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
                
                # Schema Analysis
                st.subheader("📋 Schema.org Analysis")
                
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
                
                # Rendering Analysis
                st.subheader("🔄 Rendering Impact Analysis")
                
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
                
                # CSS Visibility Analysis
                st.subheader("👁️ CSS Visibility Analysis")
                
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
                
                # Enhanced Recommendations
                st.subheader("💡 Enhanced Recommendations")
                
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
                
                # Technical Explanations
                st.subheader("🔬 Technical Explanations")
                
                for key, explanation in enhanced_report.technical_explanations.items():
                    with st.expander(f"About {key.replace('_', ' ').title()}"):
                        st.markdown(explanation)
                
                # Evidence Sources
                st.markdown("**📚 Evidence Sources:**")
                for source in enhanced_report.evidence_sources:
                    st.write(f"• {source}")
            
            else:
                st.info("Enhanced LLM analysis not available. Run analysis with 'LLM Accessibility Only' or 'Comprehensive Analysis' focus.")
        
        with tabs[3]:  # LLMs.txt Analysis
            st.header("📄 LLMs.txt Analysis")
            
            if st.session_state.llms_txt_analysis:
                llms_analysis = st.session_state.llms_txt_analysis
                
                # Overall Status
                col1, col2, col3 = st.columns(3)
                with col1:
                    status_icon = "✅" if llms_analysis.is_present else "❌"
                    st.metric("LLMs.txt Status", f"{status_icon} {'Present' if llms_analysis.is_present else 'Missing'}")
                with col2:
                    st.metric("Quality Score", f"{llms_analysis.quality_score:.1f}/100")
                with col3:
                    st.metric("Format Valid", "✅" if llms_analysis.format_valid else "❌")
                
                if llms_analysis.is_present:
                    st.markdown("---")
                    
                    # File Content
                    st.subheader("📄 File Content")
                    st.code(llms_analysis.content, language="markdown")
                    
                    st.markdown("---")
                    
                    # Sections Analysis
                    st.subheader("📋 Sections Analysis")
                    
                    for section_name, items in llms_analysis.sections.items():
                        if items:
                            with st.expander(f"{section_name.title()} ({len(items)} items)"):
                                for item in items:
                                    st.write(f"• {item}")
                    
                    st.markdown("---")
                    
                    # Benefits
                    if llms_analysis.benefits:
                        st.subheader("✅ Benefits")
                        for benefit in llms_analysis.benefits:
                            st.success(benefit)
                    
                    # Issues
                    if llms_analysis.issues:
                        st.subheader("⚠️ Issues")
                        for issue in llms_analysis.issues:
                            st.warning(issue)
                    
                    # Recommendations
                    if llms_analysis.recommendations:
                        st.subheader("💡 Recommendations")
                        for rec in llms_analysis.recommendations:
                            st.info(rec)
                
                else:
                    st.markdown("---")
                    st.warning("No llms.txt file found at the website root.")
                    st.markdown("""
                    **What is llms.txt?**
                    
                    llms.txt is a new standard (2024-2025) for guiding LLMs to quality content on your website.
                    It's different from robots.txt - while robots.txt focuses on exclusion, llms.txt focuses on guidance.
                    
                    **Benefits:**
                    - Directs AI crawlers to most important pages
                    - Reduces confusion from cluttered navigation  
                    - Improves brand representation in AI answers
                    - Works alongside robots.txt and sitemap.xml
                    
                    **Example llms.txt:**
                    ```markdown
                    # Company Name - LLM Guide
                    
                    ## About
                    Brief description of site and content
                    
                    ## Key Pages
                    - /products/main: Main product description
                    - /docs/api: API documentation
                    - /blog/important: Key article
                    
                    ## Documentation
                    Developer docs at /docs/ - comprehensive guides
                    ```
                    """)
            
            else:
                st.info("LLMs.txt analysis not available. Run analysis with 'LLM Accessibility Only' or 'Comprehensive Analysis' focus.")
        
        with tabs[4]:  # Scraper Analysis
            st.header("🕷️ Scraper Analysis")
            
            if st.session_state.score:
                score = st.session_state.score
                
                # Scraper-specific metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Scraper Friendliness", f"{st.session_state.score.scraper_friendliness.total_score:.1f}/100", 
                             delta=f"Grade: {st.session_state.score.scraper_friendliness.grade}")
                with col2:
                    st.metric("Static Content Quality", f"{st.session_state.score.scraper_friendliness.static_content_quality.score:.1f}/25")
                with col3:
                    st.metric("Semantic HTML", f"{st.session_state.score.scraper_friendliness.semantic_html_structure.score:.1f}/20")
                
                st.markdown("---")
                
                # Scraper-specific breakdown
                st.subheader("🎯 Scraper Friendliness Breakdown")
                
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
                
                # Scraper-specific recommendations
                st.subheader("💡 Scraper Optimization Recommendations")
                
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
                st.warning("Scraper analysis not available. Please run the analysis first.")
        
        with tabs[5]:  # SSR Detection
            st.header("🔍 Server-Side Rendering (SSR) Detection")
            
            if st.session_state.ssr_detection:
                ssr = st.session_state.ssr_detection
                
                # SSR Status
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
                
                # Framework Detection
                if ssr.framework_indicators:
                    st.subheader("🎯 Framework Indicators")
                    for indicator in ssr.framework_indicators:
                        st.markdown(f"- {indicator}")
                else:
                    st.info("No specific framework indicators detected")
                
                # Evidence
                if ssr.evidence:
                    st.subheader("🔍 Detection Evidence")
                    for evidence in ssr.evidence:
                        st.markdown(f"- {evidence}")
                
                # Performance Indicators
                if ssr.performance_indicators:
                    st.subheader("⚡ Performance Indicators")
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
                
                # Recommendations
                st.subheader("💡 SSR Recommendations")
                if ssr.is_ssr:
                    st.success("🎉 Your website uses SSR! This is excellent for LLM accessibility.")
                    st.info("""
                    **Benefits of SSR:**
                    - Content is immediately available to LLMs
                    - Better SEO performance
                    - Faster initial page load
                    - Improved accessibility
                    """)
                else:
                    st.warning("⚠️ Your website may not be using SSR effectively.")
                    st.info("""
                    **Consider implementing SSR for:**
                    - Better LLM accessibility
                    - Improved SEO
                    - Faster initial content delivery
                    - Enhanced user experience
                    """)
            else:
                st.warning("SSR detection not available. Please run the analysis first.")
        
        with tabs[6]:  # Crawler Testing
            st.header("🕷️ Web Crawler Testing")
            
            if st.session_state.crawler_analysis:
                crawler_results = st.session_state.crawler_analysis
                
                # Summary metrics
                st.subheader("📊 Crawler Accessibility Summary")
                
                cols = st.columns(len(crawler_results))
                for i, (crawler_type, result) in enumerate(crawler_results.items()):
                    with cols[i]:
                        score_class = get_score_color_class(result.accessibility_score)
                        st.metric(
                            result.crawler_name,
                            f"{result.accessibility_score:.1f}/100",
                            delta=f"Grade: {_get_grade(result.accessibility_score)}"
                        )
                
                st.markdown("---")
                
                # Detailed analysis for each crawler
                for crawler_type, result in crawler_results.items():
                    with st.expander(f"🔍 {result.crawler_name} Analysis"):
                        
                        # Accessibility Score
                        st.markdown(f"**Accessibility Score:** {result.accessibility_score:.1f}/100")
                        st.progress(result.accessibility_score / 100)
                        
                        # Accessible Content
                        if result.content_accessible:
                            st.markdown("**✅ Accessible Content:**")
                            for content_type, details in result.content_accessible.items():
                                if isinstance(details, dict) and details.get('available'):
                                    st.markdown(f"- {content_type}: {details.get('explanation', '')}")
                        
                        # Inaccessible Content
                        if result.content_inaccessible:
                            st.markdown("**❌ Inaccessible Content:**")
                            for content_type, details in result.content_inaccessible.items():
                                if isinstance(details, dict) and not details.get('available', True):
                                    impact = details.get('impact', 'Unknown')
                                    explanation = details.get('explanation', '')
                                    st.markdown(f"- {content_type}: {explanation} ({impact})")
                        
                        # Evidence
                        if result.evidence:
                            st.markdown("**🔍 Evidence:**")
                            for evidence in result.evidence:
                                st.markdown(f"- {evidence}")
                        
                        # Recommendations
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
                st.warning("Crawler testing not available. Please run 'Web Crawler Testing' analysis first.")
        
        with tabs[7]:  # Evidence Report
            st.header("📊 Evidence Report")
            
            if st.session_state.evidence_report:
                report = st.session_state.evidence_report
                
                # Report Header
                st.subheader("📋 Report Summary")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Analysis ID", report.analysis_id)
                with col2:
                    st.metric("Crawlers Tested", report.summary['total_crawlers'])
                with col3:
                    st.metric("Total Issues", report.summary['total_issues'])
                
                # Issue Breakdown
                st.subheader("📊 Issue Breakdown")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Critical", report.summary['critical_issues'], delta="🔴")
                with col2:
                    st.metric("High", report.summary['high_issues'], delta="🟠")
                with col3:
                    st.metric("Medium", report.summary['medium_issues'], delta="🟡")
                with col4:
                    st.metric("Low", report.summary['low_issues'], delta="🟢")
                
                # Export Options
                st.subheader("📤 Export Report")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📄 Export JSON"):
                        evidence_capture = EvidenceCapture()
                        json_report = evidence_capture.export_evidence_report(report.analysis_id, 'json')
                        st.download_button(
                            label="Download JSON",
                            data=json_report,
                            file_name=f"evidence_report_{report.analysis_id}.json",
                            mime="application/json"
                        )
                
                with col2:
                    if st.button("📄 Export HTML"):
                        evidence_capture = EvidenceCapture()
                        html_report = evidence_capture.export_evidence_report(report.analysis_id, 'html')
                        st.download_button(
                            label="Download HTML",
                            data=html_report,
                            file_name=f"evidence_report_{report.analysis_id}.html",
                            mime="text/html"
                        )
                
                with col3:
                    if st.button("📄 Export Markdown"):
                        evidence_capture = EvidenceCapture()
                        md_report = evidence_capture.export_evidence_report(report.analysis_id, 'markdown')
                        st.download_button(
                            label="Download Markdown",
                            data=md_report,
                            file_name=f"evidence_report_{report.analysis_id}.md",
                            mime="text/markdown"
                        )
                
                # Comprehensive Recommendations
                if report.recommendations:
                    st.subheader("💡 Comprehensive Recommendations")
                    for rec in report.recommendations:
                        if 'CRITICAL' in rec:
                            st.error(rec)
                        elif 'HIGH' in rec:
                            st.warning(rec)
                        else:
                            st.info(rec)
            else:
                st.warning("Evidence report not available. Please run analysis with 'Capture Evidence' enabled.")
        
        with tabs[8]:  # Content
            st.header("Content Analysis")
            
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
                
                st.subheader("Content Preview")
                with st.expander("View extracted text content"):
                    st.text_area(
                        "Extracted Content",
                        content.text_content[:5000] + ("..." if len(content.text_content) > 5000 else ""),
                        height=300
                    )
        
        with tabs[9]:  # Structure
            st.header("HTML Structure Analysis")
            
            if st.session_state.static_result and st.session_state.static_result.structure_analysis:
                structure = st.session_state.static_result.structure_analysis
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Elements", structure.total_elements)
                col2.metric("DOM Depth", structure.nested_depth)
                col3.metric("Semantic Elements", len(structure.semantic_elements))
                
                st.markdown("---")
                
                st.subheader("Heading Hierarchy")
                col1, col2 = st.columns(2)
                
                with col1:
                    hierarchy = structure.heading_hierarchy
                    st.markdown(f"**H1**: {len(hierarchy.h1)}")
                    for h1 in hierarchy.h1[:5]:
                        st.markdown(f"- {h1}")
                    
                    st.markdown(f"**H2**: {len(hierarchy.h2)}")
                    for h2 in hierarchy.h2[:5]:
                        st.markdown(f"- {h2}")
                    
                    st.markdown(f"**H3**: {len(hierarchy.h3)}")
                    for h3 in hierarchy.h3[:5]:
                        st.markdown(f"- {h3}")
                
                with col2:
                    st.subheader("Semantic HTML Elements")
                    if structure.semantic_elements:
                        for elem in structure.semantic_elements:
                            st.markdown(f"- `<{elem}>`")
                    else:
                        st.warning("No semantic HTML5 elements detected")
        
        with tabs[10]:  # Meta Data
            st.header("Meta Data & Structured Data")
            
            if st.session_state.static_result and st.session_state.static_result.meta_analysis:
                meta = st.session_state.static_result.meta_analysis
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Basic Meta Tags")
                    st.markdown(f"**Title**: {meta.title or 'Not found'}")
                    st.markdown(f"**Description**: {meta.description or 'Not found'}")
                    st.markdown(f"**Canonical URL**: {meta.canonical_url or 'Not found'}")
                    
                    st.subheader("Open Graph Tags")
                    if meta.open_graph_tags:
                        for key, value in list(meta.open_graph_tags.items())[:10]:
                            st.markdown(f"**{key}**: {value}")
                    else:
                        st.warning("No Open Graph tags found")
                
                with col2:
                    st.subheader("Twitter Card Tags")
                    if meta.twitter_card_tags:
                        for key, value in meta.twitter_card_tags.items():
                            st.markdown(f"**{key}**: {value}")
                    else:
                        st.warning("No Twitter Card tags found")
                    
                    st.subheader("Structured Data")
                    st.markdown(f"- **JSON-LD**: {'✅ Found' if meta.has_json_ld else '❌ Not found'}")
                    st.markdown(f"- **Microdata**: {'✅ Found' if meta.has_microdata else '❌ Not found'}")
                    st.markdown(f"- **RDFa**: {'✅ Found' if meta.has_rdfa else '❌ Not found'}")
                    
                    if meta.structured_data:
                        with st.expander(f"View {len(meta.structured_data)} structured data items"):
                            for i, data in enumerate(meta.structured_data[:5], 1):
                                st.json(data.data)
        
        with tabs[11]:  # JavaScript
            st.header("JavaScript Analysis")
            
            if st.session_state.static_result and st.session_state.static_result.javascript_analysis:
                js = st.session_state.static_result.javascript_analysis
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Scripts", js.total_scripts)
                col2.metric("Inline Scripts", js.inline_scripts)
                col3.metric("External Scripts", js.external_scripts)
                col4.metric("Frameworks", len(js.frameworks))
                
                st.markdown("---")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("SPA Detected", "Yes" if js.is_spa else "No")
                col2.metric("AJAX Usage", "Yes" if js.has_ajax else "No")
                col3.metric("Dynamic Content", "Yes" if js.dynamic_content_detected else "No")
                
                if js.frameworks:
                    st.subheader("Detected Frameworks")
                    for fw in js.frameworks:
                        st.markdown(f"- **{fw.name}** (confidence: {fw.confidence})")
                
                if st.session_state.comparison:
                    st.markdown("---")
                    st.subheader("Static vs Dynamic Comparison")
                    
                    comp = st.session_state.comparison
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Similarity Score", f"{comp.similarity_score:.1%}")
                    col2.metric("Content Difference", f"{comp.content_difference} chars")
                    col3.metric("JS Dependent", "Yes" if comp.javascript_dependent else "No")
                    
                    if comp.missing_in_static:
                        with st.expander(f"⚠️ {len(comp.missing_in_static)} items missing in static HTML"):
                            for item in comp.missing_in_static[:10]:
                                st.markdown(f"- {item}")
        
        with tabs[12]:  # Recommendations
            st.header("💡 Optimization Recommendations")
            
            if st.session_state.score and st.session_state.score.recommendations:
                # Group by priority
                critical = [r for r in st.session_state.score.recommendations if r.priority.value == "critical"]
                high = [r for r in st.session_state.score.recommendations if r.priority.value == "high"]
                medium = [r for r in st.session_state.score.recommendations if r.priority.value == "medium"]
                low = [r for r in st.session_state.score.recommendations if r.priority.value == "low"]
                
                if critical:
                    st.error(f"🚨 {len(critical)} Critical Issues")
                    for rec in critical:
                        with st.expander(f"🔴 {rec.title}"):
                            st.markdown(rec.description)
                            st.markdown(f"**Difficulty**: {rec.difficulty.value.title()}")
                            st.markdown(f"**Impact**: {rec.impact.value.title()}")
                            st.markdown(f"**Category**: {rec.category}")
                            if rec.code_example:
                                st.code(rec.code_example, language="html")
                            if rec.resources:
                                st.markdown("**Resources**:")
                                for resource in rec.resources:
                                    st.markdown(f"- {resource}")
                
                if high:
                    st.warning(f"⚠️ {len(high)} High Priority Recommendations")
                    for rec in high:
                        with st.expander(f"🟠 {rec.title}"):
                            st.markdown(rec.description)
                            st.markdown(f"**Difficulty**: {rec.difficulty.value.title()}")
                            st.markdown(f"**Impact**: {rec.impact.value.title()}")
                            st.markdown(f"**Category**: {rec.category}")
                            if rec.code_example:
                                st.code(rec.code_example, language="html")
                            if rec.resources:
                                st.markdown("**Resources**:")
                                for resource in rec.resources:
                                    st.markdown(f"- {resource}")
                
                if medium:
                    with st.expander(f"🟡 {len(medium)} Medium Priority Recommendations"):
                        for rec in medium:
                            st.markdown(f"**{rec.title}**")
                            st.markdown(rec.description)
                            st.markdown("---")
                
                if low:
                    with st.expander(f"🟢 {len(low)} Low Priority Recommendations"):
                        for rec in low:
                            st.markdown(f"**{rec.title}**")
                            st.markdown(rec.description)
                            st.markdown("---")
                
                if not (critical or high or medium or low):
                    st.success("🎉 No recommendations - your site is perfectly optimized!")
            else:
                st.info("No scoring analysis available. Run 'Comprehensive Analysis' to see optimization recommendations.")
    
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

