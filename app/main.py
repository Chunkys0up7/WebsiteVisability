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
from src.utils.validators import URLValidator
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
    """Perform complete website analysis"""
    try:
        # Static Analysis
        with st.spinner("🔍 Performing static analysis..."):
            static_analyzer = StaticAnalyzer(timeout=30)
            static_result = static_analyzer.analyze(url)
            
            if static_result.status != "success":
                st.error(f"Static analysis failed: {static_result.message}")
                return False
            
            st.session_state.static_result = static_result
            logger.info(f"Static analysis completed for {url}")
        
        # Dynamic Analysis (optional)
        dynamic_result = None
        if analyze_dynamic:
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
        
        # Content Comparison
        comparison = None
        if dynamic_result:
            with st.spinner("📊 Comparing static vs dynamic content..."):
                comparator = ContentComparator()
                comparison = comparator.compare(static_result, dynamic_result)
                st.session_state.comparison = comparison
                logger.info(f"Content comparison completed for {url}")
        
               # LLM Accessibility Analysis
               with st.spinner("🤖 Analyzing LLM accessibility..."):
                   llm_analyzer = LLMAccessibilityAnalyzer()
                   llm_report = llm_analyzer.analyze(static_result)
                   st.session_state.llm_report = llm_report
                   logger.info(f"LLM accessibility analysis completed for {url}")
               
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
               
               # Evidence Capture
               if capture_evidence and st.session_state.crawler_analysis:
                   with st.spinner("📊 Capturing evidence and generating reports..."):
                       evidence_capture = EvidenceCapture()
                       evidence_report = evidence_capture.create_evidence_report(url, st.session_state.crawler_analysis)
                       st.session_state.evidence_report = evidence_report
                       logger.info(f"Evidence report generated for {url}")
        
        # Scoring
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
                    st.balloons()
    
    # Display results
    if st.session_state.analysis_complete and st.session_state.score:
        st.markdown("---")
        
        # Quick Overview
        score = st.session_state.score
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            scraper_score = score.scraper_friendliness.total_score
            scraper_grade = score.scraper_friendliness.grade
            score_class = get_score_color_class(scraper_score)
            st.metric(
                "Scraper Friendliness",
                f"{scraper_score:.1f}/100",
                delta=f"Grade: {scraper_grade}"
            )
        
        with col2:
            llm_score = score.llm_accessibility.total_score
            llm_grade = score.llm_accessibility.grade
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
            recommendations_count = len(score.recommendations)
            critical_count = len([r for r in score.recommendations if r.priority.value == "critical"])
            st.metric(
                "Recommendations",
                recommendations_count,
                delta=f"{critical_count} critical" if critical_count > 0 else "No critical issues"
            )
        
        st.markdown("---")
        
        # Detailed Results in Tabs
        tabs = st.tabs([
            "📊 Overview",
            "🤖 LLM Analysis", 
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
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🎯 Scraper Friendliness Breakdown")
                
                components = [
                    score.scraper_friendliness.static_content_quality,
                    score.scraper_friendliness.semantic_html_structure,
                    score.scraper_friendliness.structured_data_implementation,
                    score.scraper_friendliness.meta_tag_completeness,
                    score.scraper_friendliness.javascript_dependency,
                    score.scraper_friendliness.crawler_accessibility
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
                    score.llm_accessibility.static_content_quality,
                    score.llm_accessibility.semantic_html_structure,
                    score.llm_accessibility.structured_data_implementation,
                    score.llm_accessibility.meta_tag_completeness
                ]
                
                for comp in llm_components:
                    st.markdown(f"**{comp.name}**: {comp.score:.1f}/{comp.max_score:.0f} ({comp.percentage:.0f}%)")
                    st.progress(comp.percentage / 100)
        
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
        
        with tabs[2]:  # Scraper Analysis
            st.header("🕷️ Scraper Analysis")
            
            if st.session_state.score:
                score = st.session_state.score
                
                # Scraper-specific metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Scraper Friendliness", f"{score.scraper_friendliness.total_score:.1f}/100", 
                             delta=f"Grade: {score.scraper_friendliness.grade}")
                with col2:
                    st.metric("Static Content Quality", f"{score.scraper_friendliness.static_content_quality.score:.1f}/25")
                with col3:
                    st.metric("Semantic HTML", f"{score.scraper_friendliness.semantic_html_structure.score:.1f}/20")
                
                st.markdown("---")
                
                # Scraper-specific breakdown
                st.subheader("🎯 Scraper Friendliness Breakdown")
                
                scraper_components = [
                    score.scraper_friendliness.static_content_quality,
                    score.scraper_friendliness.semantic_html_structure,
                    score.scraper_friendliness.structured_data_implementation,
                    score.scraper_friendliness.meta_tag_completeness,
                    score.scraper_friendliness.javascript_dependency,
                    score.scraper_friendliness.crawler_accessibility
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
                
                scraper_recommendations = [r for r in score.recommendations 
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
        
        with tabs[3]:  # SSR Detection
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
        
        with tabs[4]:  # Crawler Testing
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
        
        with tabs[5]:  # Evidence Report
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
        
        with tabs[6]:  # Content
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
        
        with tabs[7]:  # Structure
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
        
        with tabs[8]:  # Meta Data
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
        
        with tabs[9]:  # JavaScript
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
        
        with tabs[10]:  # Recommendations
            st.header("💡 Optimization Recommendations")
            
            if score.recommendations:
                # Group by priority
                critical = [r for r in score.recommendations if r.priority.value == "critical"]
                high = [r for r in score.recommendations if r.priority.value == "high"]
                medium = [r for r in score.recommendations if r.priority.value == "medium"]
                low = [r for r in score.recommendations if r.priority.value == "low"]
                
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
            else:
                st.success("🎉 No recommendations - your site is perfectly optimized!")
    
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

