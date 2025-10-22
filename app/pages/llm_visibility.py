"""
LLM Content Visibility Page

Dedicated page for showing exactly what LLMs can see when accessing websites.
This simulates the behavior of LLM web_fetch and web_search tools.
"""

import streamlit as st
import logging
from datetime import datetime
import time
from typing import Optional, List, Dict, Any

from src.analyzers.llm_content_viewer import LLMContentViewer, LLMContentResult, LLMSearchResult, LLMVisibilityAnalysis
from src.utils.validators import URLValidator

logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="LLM Content Visibility",
    page_icon="👁️",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .llm-content-container {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
    }
    
    .raw-content-display {
        background-color: #ffffff;
        border: 1px solid #ced4da;
        border-radius: 4px;
        padding: 15px;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        line-height: 1.4;
        max-height: 600px;
        overflow-y: auto;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    
    .visibility-score {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
        padding: 20px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .score-excellent { background-color: #d4edda; color: #155724; }
    .score-good { background-color: #d1ecf1; color: #0c5460; }
    .score-fair { background-color: #fff3cd; color: #856404; }
    .score-poor { background-color: #f8d7da; color: #721c24; }
    
    .search-result {
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 6px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .search-title {
        font-size: 1.1rem;
        font-weight: bold;
        color: #1a73e8;
        margin-bottom: 5px;
    }
    
    .search-url {
        font-size: 0.9rem;
        color: #5f6368;
        margin-bottom: 8px;
    }
    
    .search-snippet {
        font-size: 0.95rem;
        line-height: 1.4;
        color: #3c4043;
    }
    
    .recommendation-item {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 10px 15px;
        margin: 5px 0;
        border-radius: 0 4px 4px 0;
    }
    
    .critical-recommendation {
        background-color: #f8d7da;
        border-left-color: #dc3545;
    }
    
    .high-recommendation {
        background-color: #f8d7da;
        border-left-color: #dc3545;
    }
    
    .medium-recommendation {
        background-color: #d1ecf1;
        border-left-color: #17a2b8;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main function for LLM Content Visibility page."""
    
    # Header
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: #1a1a1a; margin-bottom: 0.5rem;">👁️ LLM Content Visibility</h1>
        <p style="color: #666; font-size: 1.1rem;">See exactly what Large Language Models can see when they access your website</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for input
    with st.sidebar:
        st.header("🔧 Analysis Options")
        
        # Mode selection
        analysis_mode = st.radio(
            "Analysis Mode",
            ["Full Page Content", "Search Results", "Visibility Analysis"],
            help="Choose how to analyze LLM content visibility"
        )
        
        # URL input
        url = st.text_input(
            "Website URL",
            placeholder="https://example.com",
            help="Enter the URL you want to analyze"
        )
        
        # User agent selection
        user_agent = st.selectbox(
            "LLM User Agent",
            ["generic_llm", "gptbot", "claudebot"],
            help="Simulate different LLM crawlers"
        )
        
        # Search query (for search mode)
        search_query = ""
        if analysis_mode == "Search Results":
            search_query = st.text_input(
                "Search Query",
                placeholder="mortgage rates",
                help="Enter search terms to simulate LLM search"
            )
        
        # Analysis button
        analyze_button = st.button("🔍 Analyze LLM Visibility", type="primary")
    
    # Main content area
    if analyze_button and url:
        if not URLValidator.is_valid(url):
            st.error("Please enter a valid URL")
            return
        
        # Initialize analyzer
        with LLMContentViewer() as viewer:
            if analysis_mode == "Full Page Content":
                show_full_page_analysis(viewer, url, user_agent)
            elif analysis_mode == "Search Results":
                if search_query:
                    show_search_analysis(viewer, search_query)
                else:
                    st.warning("Please enter a search query")
            elif analysis_mode == "Visibility Analysis":
                show_visibility_analysis(viewer, url)
    
    elif analyze_button and not url:
        st.warning("Please enter a URL to analyze")
    
    else:
        # Show instructions
        show_instructions()

def show_full_page_analysis(viewer: LLMContentViewer, url: str, user_agent: str):
    """Show full page content analysis."""
    
    st.header("📄 Full Page Content Analysis")
    st.markdown(f"**Analyzing:** `{url}`")
    st.markdown(f"**User Agent:** `{user_agent}`")
    
    # Show progress
    with st.spinner("Fetching content as LLMs would see it..."):
        content_result = viewer.get_raw_llm_content(url, user_agent)
    
    # Display results
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔍 Raw Content (Exactly What LLMs See)")
        st.markdown("""
        <div class="raw-content-display">
        """, unsafe_allow_html=True)
        
        # Display the raw content
        st.text(content_result.raw_content)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.subheader("📊 Content Statistics")
        
        # Content metrics
        st.metric("Characters", f"{content_result.character_count:,}")
        st.metric("Words", f"{content_result.word_count:,}")
        st.metric("Fetch Time", content_result.timestamp)
        
        # Processing notes
        st.subheader("🔧 Processing Notes")
        for note in content_result.processing_notes:
            st.info(note)
        
        # User agent info
        st.subheader("🤖 User Agent")
        st.code(content_result.user_agent, language="text")
    
    # Download option
    st.subheader("💾 Download Content")
    st.download_button(
        label="Download Raw Content",
        data=content_result.raw_content,
        file_name=f"llm_content_{int(time.time())}.txt",
        mime="text/plain"
    )

def show_search_analysis(viewer: LLMContentViewer, query: str):
    """Show search results analysis."""
    
    st.header("🔍 Search Results Analysis")
    st.markdown(f"**Search Query:** `{query}`")
    
    # Show progress
    with st.spinner("Simulating LLM search results..."):
        search_results = viewer.simulate_llm_search(query)
    
    st.subheader("📋 Search Results (What LLMs See)")
    
    for i, result in enumerate(search_results, 1):
        with st.container():
            st.markdown(f"""
            <div class="search-result">
                <div class="search-title">{result.title}</div>
                <div class="search-url">{result.url}</div>
                <div class="search-snippet">{result.snippet}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show relevance score
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                st.metric("Relevance", f"{result.relevance_score:.2f}")
            with col2:
                st.metric("Source", result.source)
            with col3:
                st.metric("Result #", i)
            
            st.divider()
    
    # Search insights
    st.subheader("💡 Search Insights")
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

def show_visibility_analysis(viewer: LLMContentViewer, url: str):
    """Show comprehensive visibility analysis."""
    
    st.header("👁️ LLM Visibility Analysis")
    st.markdown(f"**Analyzing:** `{url}`")
    
    # Show progress
    with st.spinner("Analyzing LLM visibility..."):
        visibility_analysis = viewer.analyze_llm_visibility(url)
    
    # Visibility score
    score = visibility_analysis.visibility_score
    if score >= 80:
        score_class = "score-excellent"
        grade = "Excellent"
    elif score >= 60:
        score_class = "score-good"
        grade = "Good"
    elif score >= 40:
        score_class = "score-fair"
        grade = "Fair"
    else:
        score_class = "score-poor"
        grade = "Poor"
    
    st.markdown(f"""
    <div class="visibility-score {score_class}">
        LLM Visibility Score: {score:.1f}/100<br>
        Grade: {grade}
    </div>
    """, unsafe_allow_html=True)
    
    # Content breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Visible Content")
        visible = visibility_analysis.content_breakdown
        
        st.metric("Total Characters", f"{visible['total_content']:,}")
        st.metric("Visibility Percentage", f"{visible['visible_percentage']}%")
        st.metric("Content Type", visible['content_type'].title())
        
        # Show raw content preview
        st.subheader("📄 Content Preview")
        preview_length = 500
        preview_content = visibility_analysis.llm_visible_content[:preview_length]
        if len(visibility_analysis.llm_visible_content) > preview_length:
            preview_content += "..."
        
        st.text_area("LLM-Visible Content", preview_content, height=200)
    
    with col2:
        st.subheader("❌ Hidden Content Issues")
        hidden = visibility_analysis.hidden_content_summary
        
        for issue, status in hidden.items():
            if status:
                st.error(f"⚠️ {issue.replace('_', ' ').title()}")
            else:
                st.success(f"✅ {issue.replace('_', ' ').title()}")
    
    # Recommendations
    st.subheader("🎯 Recommendations")
    
    for recommendation in visibility_analysis.recommendations:
        if "CRITICAL" in recommendation:
            st.markdown(f"""
            <div class="recommendation-item critical-recommendation">
                <strong>🚨 {recommendation}</strong>
            </div>
            """, unsafe_allow_html=True)
        elif "HIGH" in recommendation:
            st.markdown(f"""
            <div class="recommendation-item high-recommendation">
                <strong>⚠️ {recommendation}</strong>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="recommendation-item medium-recommendation">
                <strong>💡 {recommendation}</strong>
            </div>
            """, unsafe_allow_html=True)
    
    # Full content download
    st.subheader("💾 Download Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="Download Full Content",
            data=visibility_analysis.llm_visible_content,
            file_name=f"llm_content_{int(time.time())}.txt",
            mime="text/plain"
        )
    
    with col2:
        # Create analysis report
        report = f"""
LLM Visibility Analysis Report
=============================

URL: {url}
Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Visibility Score: {score:.1f}/100
Grade: {grade}

Content Statistics:
- Total Characters: {visible['total_content']:,}
- Visibility Percentage: {visible['visible_percentage']}%
- Content Type: {visible['content_type']}

Issues Found:
{chr(10).join([f"- {issue.replace('_', ' ').title()}: {'Yes' if status else 'No'}" for issue, status in hidden.items()])}

Recommendations:
{chr(10).join([f"- {rec}" for rec in visibility_analysis.recommendations])}

Raw Content:
{visibility_analysis.llm_visible_content}
        """
        
        st.download_button(
            label="Download Analysis Report",
            data=report,
            file_name=f"llm_visibility_report_{int(time.time())}.txt",
            mime="text/plain"
        )

def show_instructions():
    """Show usage instructions."""
    
    st.markdown("""
    ## 🎯 How to Use LLM Content Visibility
    
    This tool shows you **exactly what Large Language Models can see** when they access your website. 
    It simulates the behavior of LLM web_fetch and web_search tools.
    
    ### 📋 Analysis Modes
    
    1. **Full Page Content** - See the raw text content that LLMs receive when fetching a URL
    2. **Search Results** - See the search result snippets that LLMs receive when searching
    3. **Visibility Analysis** - Comprehensive analysis of what's visible vs hidden to LLMs
    
    ### 🔍 What This Tool Shows
    
    - **Raw Content**: Exactly what LLMs see (no formatting, no summaries)
    - **Hidden Content**: What LLMs cannot access (JavaScript-dependent, dynamic content)
    - **Search Visibility**: How your content appears in LLM search results
    - **Recommendations**: Specific improvements for LLM accessibility
    
    ### 💡 Key Insights
    
    - **LLMs cannot execute JavaScript** - Dynamic content is invisible
    - **CSS hiding doesn't affect LLMs** - They can still read hidden content
    - **Semantic HTML helps** - Better structure improves LLM understanding
    - **Server-side rendering is crucial** - Static HTML is most accessible
    
    ### 🚀 Getting Started
    
    1. Enter a URL in the sidebar
    2. Choose your analysis mode
    3. Click "Analyze LLM Visibility"
    4. Review the results and recommendations
    
    ### 📊 Example Use Cases
    
    - **Content Optimization**: See what LLMs can actually read from your pages
    - **SEO for AI**: Optimize for AI search engines and LLM crawlers
    - **Accessibility Testing**: Ensure your content is accessible to AI systems
    - **Competitive Analysis**: See how competitors' content appears to LLMs
    """)

if __name__ == "__main__":
    main()
