"""
Streamlined Main Streamlit Application

Web interface for analyzing website scraper-friendliness and LLM accessibility.
Reorganized with clean tabbed interface following instructions.md requirements.
"""

import streamlit as st
import logging
from datetime import datetime
import time
import pandas as pd
import html
import sys
import os
from typing import Optional, List, Any

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

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

# Clean, minimal CSS for better styling
st.markdown("""
<style>
    /* Simple, clean styling */
    .stApp {
        background-color: #ffffff;
        color: #1a1a1a;
    }
    
    .stSidebar {
        background-color: #f8f9fa;
    }
    
    .stSelectbox {
        background-color: #ffffff;
        color: #1a1a1a;
    }
    
    .stSelectbox input {
        background-color: #ffffff;
        color: #1a1a1a;
    }
    
    .stTextInput input {
        background-color: #ffffff;
        color: #1a1a1a;
    }
    
    .main-header {
        font-size: 3.2rem;
        font-weight: 800;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
        padding-top: 1rem;
        line-height: 1.2;
        text-align: center;
    }
    
    .subtitle {
        font-size: 1.25rem;
        color: #4a4a4a;
        margin-bottom: 2.5rem;
        text-align: center;
        font-weight: 400;
    }
    
    .section-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a1a;
        border-bottom: 3px solid #2563eb;
        padding-bottom: 0.8rem;
        margin-top: 3rem;
        margin-bottom: 2rem;
    }
    
    .content-card {
        background-color: #ffffff;
        border: 2px solid #e9ecef;
        border-radius: 12px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .score-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .score-label {
        font-size: 1.1rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'url' not in st.session_state:
        st.session_state.url = ""
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'static_result' not in st.session_state:
        st.session_state.static_result = None
    if 'dynamic_result' not in st.session_state:
        st.session_state.dynamic_result = None
    if 'score' not in st.session_state:
        st.session_state.score = None
    if 'llm_report' not in st.session_state:
        st.session_state.llm_report = None
    if 'enhanced_llm_report' not in st.session_state:
        st.session_state.enhanced_llm_report = None
    if 'ssr_detection' not in st.session_state:
        st.session_state.ssr_detection = None
    if 'last_analysis_type' not in st.session_state:
        st.session_state.last_analysis_type = None

def render_sidebar():
    """Render the sidebar with analysis options."""
    with st.sidebar:
        st.markdown("## 🔧 Analysis Configuration")
        
        # URL Input
        url = st.text_input(
            "Website URL",
            value=st.session_state.url,
            placeholder="https://example.com",
            help="Enter the full URL of the website you want to analyze"
        )
        
        if url != st.session_state.url:
            st.session_state.url = url
            st.session_state.analysis_complete = False
        
        # Analysis Type Selection
        analysis_type = st.selectbox(
            "Analysis Type",
            [
                "Comprehensive Analysis",
                "LLM Accessibility Only", 
                "Web Crawler Testing",
                "SSR Detection Only",
                "Quick Analysis"
            ],
            help="Choose the type of analysis to perform"
        )
        
        # Advanced Options
        with st.expander("⚙️ Advanced Options", expanded=False):
            enable_dynamic = st.checkbox(
                "Enable Dynamic Analysis",
                value=True,
                help="Use headless browser to detect JavaScript-rendered content"
            )
            
            crawler_types = st.multiselect(
                "Crawler Types to Test",
                ["LLM Crawlers", "Googlebot", "Bingbot", "Custom"],
                default=["LLM Crawlers", "Googlebot"],
                help="Select which crawler types to simulate"
            )
            
            evidence_capture = st.checkbox(
                "Enable Evidence Capture",
                value=True,
                help="Capture detailed evidence from crawler tests"
            )
        
        # Analysis Button
        analyze_button = st.button(
            "🔍 Start Analysis",
            type="primary",
            use_container_width=True
        )
        
        if analyze_button and url:
            if not URLValidator.is_valid(url):
                st.error("Please enter a valid URL")
                return False
            
            st.session_state.last_analysis_type = analysis_type
            return True
        
        elif analyze_button and not url:
            st.warning("Please enter a URL to analyze")
            return False
        
        return False

def render_overview_tab():
    """Render the overview tab with key metrics."""
    st.markdown('<h2 class="section-header">📊 Analysis Overview</h2>', unsafe_allow_html=True)
    
    if not st.session_state.analysis_complete:
        st.info("Please run an analysis to see the overview.")
        return
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.session_state.score:
            # Calculate overall score as average of scraper and LLM scores
            scraper_score = st.session_state.score.scraper_friendliness.total_score
            llm_score = st.session_state.score.llm_accessibility.total_score
            overall_score = (scraper_score + llm_score) / 2
            grade = st.session_state.score.scraper_friendliness.grade
            
            if overall_score >= 90:
                status_class = "status-excellent"
            elif overall_score >= 70:
                status_class = "status-good"
            elif overall_score >= 50:
                status_class = "status-fair"
            else:
                status_class = "status-poor"
            
            st.markdown(f"""
            <div class="score-card">
                <div class="score-value {status_class}">{overall_score:.1f}</div>
                <div class="score-label">Overall Score</div>
                <div class="score-label">Grade: {grade}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if st.session_state.score:
            llm_score = st.session_state.score.llm_accessibility.total_score
            st.markdown(f"""
            <div class="score-card">
                <div class="score-value">{llm_score:.1f}</div>
                <div class="score-label">LLM Accessibility</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if st.session_state.score:
            scraper_score = st.session_state.score.scraper_friendliness.total_score
            st.markdown(f"""
            <div class="score-card">
                <div class="score-value">{scraper_score:.1f}</div>
                <div class="score-label">Scraper Friendly</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        if st.session_state.static_result and st.session_state.static_result.content_analysis:
            char_count = st.session_state.static_result.content_analysis.character_count
            st.markdown(f"""
            <div class="score-card">
                <div class="score-value">{char_count:,}</div>
                <div class="score-label">Characters</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Analysis Summary
    st.markdown("---")
    st.subheader("📋 Analysis Summary")
    
    if st.session_state.last_analysis_type:
        st.info(f"**Analysis Type:** {st.session_state.last_analysis_type}")
    
    if st.session_state.url:
        sanitized_url = html.escape(st.session_state.url)
        st.info(f"**Analyzed URL:** `{sanitized_url}`")
    
    # Quick Stats
    if st.session_state.static_result:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📝 Content Statistics")
            if st.session_state.static_result.content_analysis:
                content = st.session_state.static_result.content_analysis
                st.metric("Words", f"{content.word_count:,}")
                st.metric("Paragraphs", content.paragraphs)
                st.metric("Images", content.images)
                st.metric("Links", content.links)
        
        with col2:
            st.markdown("### 🏗️ Structure Statistics")
            if st.session_state.static_result.structure_analysis:
                structure = st.session_state.static_result.structure_analysis
                st.metric("Semantic Elements", len(structure.semantic_elements))
                st.metric("DOM Depth", structure.nested_depth)
                if structure.heading_hierarchy:
                    h1_count = len(structure.heading_hierarchy.h1)
                    h2_count = len(structure.heading_hierarchy.h2)
                    st.metric("H1 Tags", h1_count)
                    st.metric("H2 Tags", h2_count)

def render_llm_analysis_tab():
    """Render the LLM analysis tab."""
    st.markdown('<h2 class="section-header">🤖 LLM Analysis</h2>', unsafe_allow_html=True)
    
    if not st.session_state.analysis_complete:
        st.info("Please run an analysis to see LLM analysis results.")
        return
    
    # LLM Accessibility Report
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
        
        # Detailed LLM Visibility Explanation
        st.markdown('<h3 class="sub-section-header">🔬 How We Analyze LLM Visibility</h3>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="content-card">
            <h4>📋 LLM Content Analysis Process</h4>
            <p><strong>We simulate exactly how LLMs access web content:</strong></p>
            
            <h5>Step 1: Raw HTML Fetching</h5>
            <ul>
                <li>We make a standard HTTP GET request to the URL</li>
                <li>We receive the raw HTML response (no JavaScript execution)</li>
                <li>This is exactly what LLMs see - the "source code" of the page</li>
            </ul>
            
            <h5>Step 2: Content Extraction</h5>
            <ul>
                <li>We extract text content from HTML elements (p, h1-h6, li, etc.)</li>
                <li>We preserve the semantic structure and hierarchy</li>
                <li>We identify semantic elements (article, section, nav, etc.)</li>
                <li>We extract meta tags, structured data, and alt text</li>
            </ul>
            
            <h5>Step 3: Visibility Assessment</h5>
            <ul>
                <li>We measure how much content is accessible without JavaScript</li>
                <li>We evaluate the clarity of semantic structure</li>
                <li>We assess the presence of structured data for entity recognition</li>
                <li>We check for proper meta descriptions and titles</li>
            </ul>
            
            <p><strong>Key Insight:</strong> LLMs see the "raw" HTML content, not the rendered page. This means JavaScript-dependent content is invisible to them, making server-side rendering crucial for LLM accessibility.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # What LLMs CAN Access
        st.markdown('<h3 class="sub-section-header">✅ What LLMs CAN Access</h3>', unsafe_allow_html=True)
        
        accessible = llm_report.accessible_content
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Text Content:**")
            st.info(f"• {accessible['text_content']['explanation']}")
            st.metric("Character Count", f"{accessible['text_content']['character_count']:,}")
            
            st.markdown("**Semantic Structure:**")
            st.info(f"• {accessible['semantic_structure']['explanation']}")
            if accessible['semantic_structure']['semantic_elements']:
                st.write("Semantic elements found:", len(accessible['semantic_structure']['semantic_elements']))
        
        with col2:
            st.markdown("**Meta Information:**")
            st.info(f"• {accessible['meta_information']['explanation']}")
            if accessible['meta_information']['title']:
                st.write("Title:", accessible['meta_information']['title'][:50] + "...")
            
            st.markdown("**Structured Data:**")
            st.info(f"• {accessible['structured_data']['explanation']}")
            json_ld_count = len(accessible['structured_data']['json_ld'])
            if json_ld_count > 0:
                st.write(f"JSON-LD items: {json_ld_count}")
        
        # Raw Content Preview
        st.markdown('<h3 class="sub-section-header">👁️ Raw Content LLMs Actually See</h3>', unsafe_allow_html=True)
        
        if st.session_state.static_result and st.session_state.static_result.content_analysis:
            content = st.session_state.static_result.content_analysis.text_content
            
            st.markdown("""
            <div class="content-card">
                <h4>📄 This is the exact text content LLMs receive:</h4>
                <p><em>Note: This is the raw text extracted from HTML elements, without any JavaScript-rendered content.</em></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show first 1000 characters as preview
            preview_text = content[:1000] if len(content) > 1000 else content
            st.text_area(
                "LLM-Visible Content Preview (first 1000 characters):",
                preview_text,
                height=200,
                help="This is exactly what LLMs see when they access your page"
            )
            
            if len(content) > 1000:
                st.info(f"📊 Total LLM-visible content: {len(content):,} characters ({len(content.split()):,} words)")
            
            # Show what's missing
            if st.session_state.dynamic_result and st.session_state.dynamic_result.content_analysis:
                dynamic_content = st.session_state.dynamic_result.content_analysis.text_content
                if len(dynamic_content) > len(content):
                    missing_chars = len(dynamic_content) - len(content)
                    st.warning(f"⚠️ {missing_chars:,} characters are hidden from LLMs (likely JavaScript-rendered content)")
        
        # What LLMs CANNOT Access
        st.markdown('<h3 class="sub-section-header">❌ What LLMs CANNOT Access</h3>', unsafe_allow_html=True)
        
        inaccessible = llm_report.inaccessible_content
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**JavaScript-Dependent Content:**")
            js_content = inaccessible['javascript_dependent_content']
            if js_content['dynamic_content']:
                st.error(f"• {js_content['explanation']}")
                st.write(f"Scripts detected: {js_content['total_scripts']}")
                if js_content['frameworks_detected']:
                    st.write(f"Frameworks: {', '.join(js_content['frameworks_detected'])}")
            else:
                st.success("• No JavaScript-dependent content detected")
        
        with col2:
            st.markdown("**CSS-Hidden Content:**")
            css_content = inaccessible['css_hidden_content']
            if css_content['hidden_elements']:
                st.warning(f"• {css_content['explanation']}")
                st.write(f"Hidden elements: {len(css_content['hidden_elements'])}")
            else:
                st.success("• No CSS-hidden content issues")
        
        # Recommendations
        st.markdown('<h3 class="sub-section-header">💡 Recommendations</h3>', unsafe_allow_html=True)
        
        for i, recommendation in enumerate(llm_report.recommendations, 1):
            if "CRITICAL" in recommendation:
                st.error(f"**{i}.** {recommendation}")
            elif "HIGH" in recommendation:
                st.warning(f"**{i}.** {recommendation}")
            else:
                st.info(f"**{i}.** {recommendation}")
    
    else:
        st.info("LLM analysis not available. Please run a comprehensive analysis.")

def render_comparison_tab():
    """Render the LLM vs Scraper comparison tab."""
    st.markdown('<h2 class="section-header">🔄 LLM vs Scraper Comparison</h2>', unsafe_allow_html=True)
    
    if not st.session_state.url:
        st.info("Please enter a URL and run the analysis to see LLM vs Scraper comparison.")
        return
    
    with st.spinner("Comparing LLM vs Scraper content access..."):
        try:
            with LLMScraperComparisonAnalyzer() as comparator:
                comparison = comparator.compare_content_access(st.session_state.url)
                
                # Display comparison overview
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "LLM Visibility Score",
                        f"{comparison.llm_visibility_score:.1f}/100",
                        help="How well LLMs can access and understand the content"
                    )
                
                with col2:
                    st.metric(
                        "Scraper Accessibility Score", 
                        f"{comparison.scraper_accessibility_score:.1f}/100",
                        help="How well web scrapers can access the content"
                    )
                
                with col3:
                    st.metric(
                        "Access Gap",
                        f"{comparison.access_gap_score:.1f}",
                        help="Difference between LLM and scraper access scores"
                    )
                
                # Content volume comparison
                st.markdown("---")
                st.subheader("📊 Content Access Comparison")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🤖 LLM Perspective")
                    st.metric("Characters", f"{comparison.llm_character_count:,}")
                    st.metric("Words", f"{comparison.llm_word_count:,}")
                    
                    # Show LLM limitations
                    if comparison.llm_limitations:
                        st.markdown("**LLM Limitations:**")
                        for limitation in comparison.llm_limitations:
                            st.error(f"⚠️ {limitation}")
                    else:
                        st.success("✅ No major LLM limitations detected")
                
                with col2:
                    st.markdown("### 🕷️ Scraper Perspective")
                    st.metric("Characters", f"{comparison.scraper_character_count:,}")
                    st.metric("Words", f"{comparison.scraper_word_count:,}")
                    
                    # Show scraper capabilities
                    if comparison.scraper_capabilities:
                        st.markdown("**Scraper Capabilities:**")
                        for capability in comparison.scraper_capabilities:
                            st.success(f"✅ {capability}")
                    else:
                        st.info("ℹ️ Basic scraper access only")
                
                # Side-by-side content comparison
                st.markdown("---")
                st.subheader("📄 Content Comparison")
                
                tab1, tab2 = st.tabs(["🤖 LLM Content", "🕷️ Scraper Content"])
                
                with tab1:
                    st.markdown("**What LLMs See:**")
                    st.markdown("""
                    <div style="background-color: #ffffff; border: 1px solid #ced4da; border-radius: 4px; padding: 15px; font-family: 'Courier New', monospace; font-size: 14px; line-height: 1.4; max-height: 400px; overflow-y: auto; white-space: pre-wrap; word-wrap: break-word;">
                    """, unsafe_allow_html=True)
                    
                    # Show first 1000 characters of LLM content
                    llm_preview = comparison.llm_content[:1000]
                    if len(comparison.llm_content) > 1000:
                        llm_preview += "\n\n... (content truncated)"
                    
                    st.text(llm_preview)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with tab2:
                    st.markdown("**What Scrapers See:**")
                    st.markdown("""
                    <div style="background-color: #ffffff; border: 1px solid #ced4da; border-radius: 4px; padding: 15px; font-family: 'Courier New', monospace; font-size: 14px; line-height: 1.4; max-height: 400px; overflow-y: auto; white-space: pre-wrap; word-wrap: break-word;">
                    """, unsafe_allow_html=True)
                    
                    # Show first 1000 characters of scraper content
                    scraper_preview = comparison.scraper_content[:1000]
                    if len(comparison.scraper_content) > 1000:
                        scraper_preview += "\n\n... (content truncated)"
                    
                    st.text(scraper_preview)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Recommendations
                st.markdown("---")
                st.subheader("🎯 Optimization Recommendations")
                
                for recommendation in comparison.recommendations:
                    if "CRITICAL" in recommendation:
                        st.error(f"🚨 **{recommendation}**")
                    elif "HIGH" in recommendation:
                        st.warning(f"⚠️ **{recommendation}**")
                    else:
                        st.info(f"💡 **{recommendation}**")
                
        except Exception as e:
            st.error(f"Error comparing LLM vs Scraper access: {str(e)}")
            st.info("Please ensure the URL is accessible and try again.")

    # Detailed Score Breakdown
    st.markdown("---")
    st.markdown('<h3 class="sub-section-header">🎯 Score Calculation Details</h3>', unsafe_allow_html=True)
    
    if st.session_state.score:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="content-card">
                <h4>🔍 Scraper Friendliness Score</h4>
                <p><strong>How we calculate this:</strong></p>
                <ul>
                    <li><strong>Content Quality (25%):</strong> Word count, semantic HTML structure, proper headings</li>
                    <li><strong>Technical Structure (20%):</strong> Meta tags, structured data, clean HTML</li>
                    <li><strong>Accessibility (20%):</strong> Alt text, proper links, semantic elements</li>
                    <li><strong>Crawler Support (15%):</strong> robots.txt, sitemaps, proper redirects</li>
                    <li><strong>Performance (10%):</strong> Page size, load time, efficient structure</li>
                    <li><strong>JavaScript Impact (10%):</strong> Minimal JS dependency, server-side rendering</li>
                </ul>
                <p><strong>What this means:</strong> Higher scores indicate better accessibility for traditional web crawlers and search engines.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="content-card">
                <h4>🤖 LLM Accessibility Score</h4>
                <p><strong>How we calculate this:</strong></p>
                <ul>
                    <li><strong>Content Visibility (30%):</strong> Text content accessible without JavaScript</li>
                    <li><strong>Semantic Structure (25%):</strong> Clear headings, paragraphs, lists</li>
                    <li><strong>Entity Recognition (20%):</strong> Structured data, meta descriptions</li>
                    <li><strong>Context Clarity (15%):</strong> Clear page purpose, logical flow</li>
                    <li><strong>Technical Accessibility (10%):</strong> Clean HTML, minimal dependencies</li>
                </ul>
                <p><strong>What this means:</strong> Higher scores indicate better content visibility for AI systems and LLMs.</p>
            </div>
            """, unsafe_allow_html=True)
    
    # LLM Visibility Explanation
    st.markdown("---")
    st.markdown('<h3 class="sub-section-header">👁️ How We Determine What LLMs See</h3>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="content-card">
        <h4>🔬 LLM Content Analysis Methodology</h4>
        <p><strong>Our approach simulates how LLMs actually access web content:</strong></p>
        
        <h5>1. Raw HTML Fetching</h5>
        <ul>
            <li>We fetch the page using standard HTTP requests (like LLMs do)</li>
            <li>We extract only the text content from HTML elements</li>
            <li>We ignore JavaScript-rendered content (LLMs can't execute JS)</li>
            <li>We preserve the semantic structure (headings, paragraphs, lists)</li>
        </ul>
        
        <h5>2. Content Processing</h5>
        <ul>
            <li>We strip out HTML tags but preserve text content</li>
            <li>We maintain the logical flow of information</li>
            <li>We extract structured data (JSON-LD, microdata) when present</li>
            <li>We identify semantic elements that help LLMs understand context</li>
        </ul>
        
        <h5>3. Visibility Assessment</h5>
        <ul>
            <li>We measure how much content is accessible without JavaScript</li>
            <li>We evaluate the clarity of semantic structure</li>
            <li>We assess the presence of structured data for entity recognition</li>
            <li>We check for proper meta descriptions and titles</li>
        </ul>
        
        <p><strong>Key Insight:</strong> LLMs see the "raw" HTML content, not the rendered page. This means JavaScript-dependent content is invisible to them, making server-side rendering crucial for LLM accessibility.</p>
    </div>
    """, unsafe_allow_html=True)

def render_technical_tab():
    """Render the technical analysis tab."""
    st.markdown('<h2 class="section-header">⚙️ Technical Analysis</h2>', unsafe_allow_html=True)
    
    if not st.session_state.analysis_complete:
        st.info("Please run an analysis to see technical analysis results.")
        return
    
    # JavaScript Analysis
    if st.session_state.static_result and st.session_state.static_result.javascript_analysis:
        js = st.session_state.static_result.javascript_analysis
        
        st.subheader("⚡ JavaScript Analysis")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Scripts", js.total_scripts)
        with col2:
            st.metric("Frameworks Detected", len(js.frameworks))
        with col3:
            st.metric("Dynamic Content", "Yes" if js.dynamic_content_detected else "No")
        
        if js.frameworks:
            st.markdown("**Frameworks Detected:**")
            for framework in js.frameworks:
                st.write(f"• {framework.name} (Confidence: {framework.confidence:.1%})")
                if framework.indicators:
                    st.write(f"  Indicators: {', '.join(framework.indicators[:3])}")  # Show first 3 indicators
        
        if js.dynamic_content_detected:
            st.warning("⚠️ **Dynamic content detected** - may affect LLM accessibility")
        else:
            st.success("✅ **Static content detected** - good for LLM accessibility")
    
    # Meta Data Analysis
    if st.session_state.static_result and st.session_state.static_result.meta_analysis:
        meta = st.session_state.static_result.meta_analysis
        
        st.markdown("---")
        st.subheader("🏷️ Meta Data Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Basic Meta Tags:**")
            if meta.title:
                st.success(f"✅ Title: {meta.title}")
            else:
                st.error("❌ No title tag found")
            
            if meta.description:
                st.success(f"✅ Description: {meta.description[:100]}...")
            else:
                st.error("❌ No meta description found")
        
        with col2:
            st.markdown("**Structured Data:**")
            if meta.structured_data:
                st.success(f"✅ {len(meta.structured_data)} structured data items found")
                for item in meta.structured_data[:3]:  # Show first 3
                    st.write(f"• {item.type}")
            else:
                st.warning("⚠️ No structured data found")
    
    # SSR Detection
    if st.session_state.ssr_detection:
        ssr = st.session_state.ssr_detection
        
        st.markdown("---")
        st.subheader("🔍 Server-Side Rendering Detection")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("SSR Confidence", f"{ssr.confidence:.1%}")
            st.metric("Rendering Type", ssr.rendering_type.title())
        
        with col2:
            if ssr.is_ssr:
                st.success("✅ **Server-Side Rendering detected**")
                st.write("Benefits:")
                st.write("• Better LLM accessibility")
                st.write("• Faster initial page load")
                st.write("• Better SEO performance")
            else:
                st.warning("⚠️ **Client-Side Rendering detected**")
                st.write("Considerations:")
                st.write("• May affect LLM accessibility")
                st.write("• Requires JavaScript execution")
                st.write("• Slower initial content availability")

def render_recommendations_tab():
    """Render the recommendations tab."""
    st.markdown('<h2 class="section-header">💡 Optimization Recommendations</h2>', unsafe_allow_html=True)
    
    if not st.session_state.analysis_complete:
        st.info("Please run an analysis to see recommendations.")
        return
    
    if st.session_state.score and st.session_state.score.recommendations:
        st.markdown("### 📋 Analysis Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Recommendations", len(st.session_state.score.recommendations))
        with col2:
            critical_count = sum(1 for r in st.session_state.score.recommendations if r.priority == "CRITICAL")
            st.metric("Critical Issues", critical_count, delta="High priority", delta_color="inverse" if critical_count > 0 else "off")
        with col3:
            high_count = sum(1 for r in st.session_state.score.recommendations if r.priority == "HIGH")
            st.metric("High Priority", high_count)
        
        st.markdown("---")
        
        # Group recommendations by priority
        critical_recs = [r for r in st.session_state.score.recommendations if r.priority == "CRITICAL"]
        high_recs = [r for r in st.session_state.score.recommendations if r.priority == "HIGH"]
        medium_recs = [r for r in st.session_state.score.recommendations if r.priority == "MEDIUM"]
        
        if critical_recs:
            st.markdown("### 🚨 Critical Issues")
            for i, rec in enumerate(critical_recs, 1):
                st.error(f"**{i}.** {rec.description}")
        
        if high_recs:
            st.markdown("### ⚠️ High Priority")
            for i, rec in enumerate(high_recs, 1):
                st.warning(f"**{i}.** {rec.description}")
        
        if medium_recs:
            st.markdown("### 💡 Medium Priority")
            for i, rec in enumerate(medium_recs, 1):
                st.info(f"**{i}.** {rec.description}")
    
    else:
        st.success("🎉 No recommendations needed - your site is well-optimized!")

def run_analysis(analysis_type: str):
    """Run the analysis based on the selected type."""
    url = st.session_state.url
    
    with st.spinner(f"Running {analysis_type}..."):
        try:
            # Static Analysis (always run)
            static_analyzer = StaticAnalyzer()
            static_result = static_analyzer.analyze(url)
            st.session_state.static_result = static_result
            
            # Dynamic Analysis (if enabled)
            if analysis_type in ["Comprehensive Analysis", "Quick Analysis"]:
                try:
                    dynamic_analyzer = DynamicAnalyzer()
                    dynamic_result = dynamic_analyzer.analyze(url)
                    st.session_state.dynamic_result = dynamic_result
                except Exception as e:
                    st.warning(f"Dynamic analysis failed: {e}")
            
            # LLM Analysis
            if analysis_type in ["Comprehensive Analysis", "LLM Accessibility Only"]:
                llm_analyzer = LLMAccessibilityAnalyzer()
                llm_report = llm_analyzer.analyze(static_result)
                st.session_state.llm_report = llm_report
            
            # Enhanced LLM Analysis
            if analysis_type in ["Comprehensive Analysis", "LLM Accessibility Only"]:
                enhanced_llm_analyzer = EnhancedLLMAccessibilityAnalyzer()
                enhanced_llm_report = enhanced_llm_analyzer.analyze(static_result)
                st.session_state.enhanced_llm_report = enhanced_llm_report
            
            # SSR Detection
            if analysis_type in ["Comprehensive Analysis", "SSR Detection Only"]:
                try:
                    ssr_detector = SSRDetector()
                    # We need to fetch the HTML again for SSR detection
                    import requests
                    response = requests.get(url, timeout=10)
                    html_content = response.text
                    ssr_detection = ssr_detector.detect_ssr(html_content)
                    st.session_state.ssr_detection = ssr_detection
                except Exception as e:
                    logger.warning(f"SSR detection failed: {e}")
                    st.session_state.ssr_detection = None
            
            # Scoring
            scoring_engine = ScoringEngine()
            score = scoring_engine.calculate_score(static_result, None)
            st.session_state.score = score
            
            st.session_state.analysis_complete = True
            st.success("✅ Analysis completed successfully!")
            
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")
            logger.error(f"Analysis error: {e}")

def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 class="main-header">🔍 Web Scraper & LLM Analyzer</h1>
        <p class="subtitle">Analyze websites for scraper-friendliness and LLM accessibility</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    should_run_analysis = render_sidebar()
    
    # Main content
    if should_run_analysis:
        run_analysis(st.session_state.last_analysis_type)
    
    # Results tabs
    if st.session_state.analysis_complete:
        # Create main tabs
        main_tabs = st.tabs([
            "📊 Overview",
            "🤖 LLM Analysis", 
            "🔄 Comparison",
            "⚙️ Technical",
            "💡 Recommendations"
        ])
        
        with main_tabs[0]:
            render_overview_tab()
        
        with main_tabs[1]:
            render_llm_analysis_tab()
        
        with main_tabs[2]:
            render_comparison_tab()
        
        with main_tabs[3]:
            render_technical_tab()
        
        with main_tabs[4]:
            render_recommendations_tab()
    
    else:
        # Show instructions when no analysis is complete
        st.markdown("""
        <div class="content-card">
            <h3>🎯 How to Get Started</h3>
            <ol style="color: #1a1a1a; font-weight: 500;">
                <li><strong>Enter a URL</strong> in the sidebar</li>
                <li><strong>Select analysis type</strong> (Comprehensive Analysis recommended)</li>
                <li><strong>Click "Start Analysis"</strong> to begin</li>
                <li><strong>Review results</strong> in the tabs above</li>
            </ol>
            
            <h4 style="color: #1a1a1a; font-weight: 700; margin-top: 25px;">📋 Analysis Types:</h4>
            <ul style="color: #1a1a1a; font-weight: 500;">
                <li><strong>Comprehensive Analysis:</strong> Full analysis with all features</li>
                <li><strong>LLM Accessibility Only:</strong> Focused on LLM-specific analysis</li>
                <li><strong>Web Crawler Testing:</strong> Tests different crawler behaviors</li>
                <li><strong>SSR Detection Only:</strong> Identifies server-side rendering patterns</li>
                <li><strong>Quick Analysis:</strong> Fast analysis with basic metrics</li>
            </ul>
            
            <div style="background-color: #e3f2fd; border: 2px solid #2196f3; border-radius: 8px; padding: 20px; margin-top: 25px;">
                <h4 style="color: #1976d2; font-weight: 700; margin-bottom: 15px;">💡 Pro Tips:</h4>
                <ul style="color: #1976d2; font-weight: 500;">
                    <li>Start with <strong>Comprehensive Analysis</strong> for the best overview</li>
                    <li>Use <strong>LLM Accessibility Only</strong> to focus on AI-specific issues</li>
                    <li>Try <strong>Web Crawler Testing</strong> to see how different bots access your site</li>
                    <li>Check <strong>SSR Detection</strong> to understand your rendering approach</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
