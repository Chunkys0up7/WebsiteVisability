"""
LLM Content Viewer Module

Shows exactly what LLMs can see when they fetch or search web content.
This simulates the behavior of LLM web_fetch and web_search tools.
"""

import logging
import requests
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import re
from bs4 import BeautifulSoup
import time

logger = logging.getLogger(__name__)


@dataclass
class LLMContentResult:
    """Raw content that LLMs receive from web fetching"""
    url: str
    raw_content: str
    content_type: str  # 'web_fetch' or 'web_search'
    character_count: int
    word_count: int
    timestamp: str
    user_agent: str
    processing_notes: List[str]


@dataclass
class LLMSearchResult:
    """Search result snippet that LLMs receive"""
    title: str
    url: str
    snippet: str
    source: str
    relevance_score: float


@dataclass
class LLMVisibilityAnalysis:
    """Analysis of what LLMs can see vs what's hidden"""
    llm_visible_content: str
    hidden_content_summary: Dict[str, Any]
    content_breakdown: Dict[str, Any]
    recommendations: List[str]
    visibility_score: float


class LLMContentViewer:
    """
    Shows exactly what LLMs can see when accessing web content.
    
    Simulates the behavior of:
    - web_fetch tool (full page content)
    - web_search tool (search result snippets)
    """
    
    def __init__(self, timeout: int = 30):
        """Initialize the LLM content viewer."""
        self.timeout = timeout
        self.session = requests.Session()
        
        # Simulate LLM user agents
        self.llm_user_agents = {
            'gptbot': 'Mozilla/5.0 (compatible; GPTBot/1.0; +https://openai.com/gptbot)',
            'claudebot': 'Mozilla/5.0 (compatible; ClaudeBot/1.0; +https://anthropic.com/claudebot)',
            'generic_llm': 'Mozilla/5.0 (compatible; LLM-Crawler/1.0)'
        }
        
        # Set default user agent
        self.session.headers.update({
            'User-Agent': self.llm_user_agents['generic_llm'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def get_raw_llm_content(self, url: str, user_agent: str = 'generic_llm') -> LLMContentResult:
        """
        Get exactly what LLMs see when fetching a URL.
        
        This simulates the web_fetch tool behavior - showing the processed
        text content that LLMs receive, not raw HTML.
        """
        logger.info(f"Fetching LLM-visible content from {url}")
        
        # Set the specified user agent
        if user_agent in self.llm_user_agents:
            self.session.headers['User-Agent'] = self.llm_user_agents[user_agent]
        
        processing_notes = []
        
        try:
            # Fetch the page
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Process content exactly like LLMs do
            raw_content = self._extract_llm_visible_content(response.text, url)
            
            # Count content
            character_count = len(raw_content)
            word_count = len(raw_content.split())
            
            processing_notes.append(f"Successfully fetched {character_count} characters")
            processing_notes.append(f"Content type: {response.headers.get('content-type', 'unknown')}")
            
            if response.status_code != 200:
                processing_notes.append(f"Non-200 status: {response.status_code}")
            
        except requests.exceptions.RequestException as e:
            raw_content = f"Error fetching content: {str(e)}"
            character_count = len(raw_content)
            word_count = len(raw_content.split())
            processing_notes.append(f"Fetch error: {str(e)}")
        
        return LLMContentResult(
            url=url,
            raw_content=raw_content,
            content_type='web_fetch',
            character_count=character_count,
            word_count=word_count,
            timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
            user_agent=self.session.headers['User-Agent'],
            processing_notes=processing_notes
        )
    
    def simulate_llm_search(self, query: str, num_results: int = 5) -> List[LLMSearchResult]:
        """
        Simulate what LLMs see when using web search.
        
        This creates realistic search result snippets that LLMs would receive
        from web_search tool calls.
        """
        logger.info(f"Simulating LLM search for: {query}")
        
        # For demonstration, we'll create realistic search result patterns
        # In a real implementation, this would integrate with actual search APIs
        search_results = []
        
        # Create realistic search result patterns based on the query
        if 'chase' in query.lower() and 'mortgage' in query.lower():
            search_results = [
                LLMSearchResult(
                    title="Chase Mortgage - We're with you, all the way home",
                    url="https://www.chase.com/personal/mortgage-b",
                    snippet="Chase offers competitive mortgage rates and personalized service. Learn about our Relationship Pricing Program with discounts for existing customers and new money transfers.",
                    source="chase.com",
                    relevance_score=0.95
                ),
                LLMSearchResult(
                    title="Chase Mortgage Rates and Programs | Chase.com",
                    url="https://www.chase.com/personal/mortgage",
                    snippet="Explore Chase mortgage options including fixed-rate, adjustable-rate, and jumbo loans. Get pre-approved and find competitive rates.",
                    source="chase.com",
                    relevance_score=0.88
                ),
                LLMSearchResult(
                    title="Chase Bank Mortgage Calculator | Calculate Your Payment",
                    url="https://www.chase.com/personal/mortgage/mortgage-calculator",
                    snippet="Use Chase's mortgage calculator to estimate your monthly payment. Enter loan amount, interest rate, and term to calculate payments.",
                    source="chase.com",
                    relevance_score=0.82
                ),
                LLMSearchResult(
                    title="Chase Mortgage Application Process | Apply Online",
                    url="https://www.chase.com/personal/mortgage/apply",
                    snippet="Apply for a Chase mortgage online. Complete your application in minutes and get pre-approved for your home loan.",
                    source="chase.com",
                    relevance_score=0.78
                ),
                LLMSearchResult(
                    title="Chase Mortgage Refinancing Options | Lower Your Rate",
                    url="https://www.chase.com/personal/mortgage/refinance",
                    snippet="Refinance your existing mortgage with Chase. Lower your monthly payment or shorten your loan term with competitive rates.",
                    source="chase.com",
                    relevance_score=0.75
                )
            ]
        elif 'mortgage' in query.lower():
            search_results = [
                LLMSearchResult(
                    title="Mortgage Rates Today | Bankrate",
                    url="https://www.bankrate.com/mortgages/mortgage-rates",
                    snippet="Compare current mortgage rates from top lenders. Get personalized rate quotes and find the best mortgage rates for your situation.",
                    source="bankrate.com",
                    relevance_score=0.92
                ),
                LLMSearchResult(
                    title="Mortgage Calculator | Calculate Monthly Payment",
                    url="https://www.bankrate.com/calculators/mortgages/mortgage-calculator",
                    snippet="Use our mortgage calculator to estimate your monthly payment. Enter loan amount, interest rate, and term to calculate payments.",
                    source="bankrate.com",
                    relevance_score=0.88
                ),
                LLMSearchResult(
                    title="How to Get a Mortgage | Complete Guide",
                    url="https://www.bankrate.com/mortgages/how-to-get-a-mortgage",
                    snippet="Learn how to get a mortgage in 2024. Complete guide covering pre-approval, application process, and closing.",
                    source="bankrate.com",
                    relevance_score=0.85
                ),
                LLMSearchResult(
                    title="Best Mortgage Lenders 2024 | Reviews & Comparison",
                    url="https://www.bankrate.com/mortgages/best-mortgage-lenders",
                    snippet="Compare the best mortgage lenders of 2024. Read reviews, compare rates, and find the right lender for your home loan.",
                    source="bankrate.com",
                    relevance_score=0.82
                ),
                LLMSearchResult(
                    title="Mortgage Pre-approval Process | What You Need to Know",
                    url="https://www.bankrate.com/mortgages/mortgage-pre-approval",
                    snippet="Get pre-approved for a mortgage before house hunting. Learn what documents you need and how the pre-approval process works.",
                    source="bankrate.com",
                    relevance_score=0.78
                )
            ]
        elif 'ai' in query.lower() or 'artificial intelligence' in query.lower():
            search_results = [
                LLMSearchResult(
                    title="What is Artificial Intelligence? | IBM",
                    url="https://www.ibm.com/topics/artificial-intelligence",
                    snippet="Artificial intelligence (AI) is technology that enables computers and machines to simulate human intelligence and problem-solving capabilities.",
                    source="ibm.com",
                    relevance_score=0.95
                ),
                LLMSearchResult(
                    title="Artificial Intelligence | Stanford University",
                    url="https://ai.stanford.edu/",
                    snippet="Stanford AI research focuses on machine learning, robotics, computer vision, and natural language processing.",
                    source="stanford.edu",
                    relevance_score=0.90
                ),
                LLMSearchResult(
                    title="AI News and Research | MIT Technology Review",
                    url="https://www.technologyreview.com/topic/artificial-intelligence/",
                    snippet="Latest news and analysis on artificial intelligence, machine learning, and AI research from MIT Technology Review.",
                    source="technologyreview.com",
                    relevance_score=0.85
                ),
                LLMSearchResult(
                    title="OpenAI | Creating Safe AGI",
                    url="https://openai.com/",
                    snippet="OpenAI is an AI research company that aims to ensure artificial general intelligence benefits all of humanity.",
                    source="openai.com",
                    relevance_score=0.88
                ),
                LLMSearchResult(
                    title="Google AI | Research and Development",
                    url="https://ai.google/",
                    snippet="Google AI conducts research in machine learning, computer vision, natural language processing, and robotics.",
                    source="google.com",
                    relevance_score=0.82
                )
            ]
        else:
            # Generic search results pattern
            search_results = [
                LLMSearchResult(
                    title=f"Search results for: {query}",
                    url=f"https://example.com/search?q={query.replace(' ', '+')}",
                    snippet=f"Comprehensive information about {query}. Find detailed resources, guides, and expert insights.",
                    source="example.com",
                    relevance_score=0.75
                ),
                LLMSearchResult(
                    title=f"{query} - Complete Guide",
                    url=f"https://example.com/guide/{query.replace(' ', '-').lower()}",
                    snippet=f"Learn everything about {query} with our comprehensive guide. Expert tips, best practices, and detailed explanations.",
                    source="example.com",
                    relevance_score=0.70
                ),
                LLMSearchResult(
                    title=f"{query} News and Updates",
                    url=f"https://example.com/news/{query.replace(' ', '-').lower()}",
                    snippet=f"Stay updated with the latest news and developments in {query}. Breaking news, analysis, and expert opinions.",
                    source="example.com",
                    relevance_score=0.65
                )
            ]
        
        return search_results[:num_results]
    
    def analyze_llm_visibility(self, url: str) -> LLMVisibilityAnalysis:
        """
        Analyze what LLMs can see vs what's hidden from them.
        """
        logger.info(f"Analyzing LLM visibility for {url}")
        
        # Get the raw content
        content_result = self.get_raw_llm_content(url)
        
        # Analyze what's visible vs hidden
        visibility_analysis = self._analyze_content_visibility(content_result.raw_content, url)
        
        # Generate recommendations
        recommendations = self._generate_visibility_recommendations(visibility_analysis)
        
        # Calculate visibility score
        visibility_score = self._calculate_visibility_score(visibility_analysis)
        
        return LLMVisibilityAnalysis(
            llm_visible_content=content_result.raw_content,
            hidden_content_summary=visibility_analysis['hidden'],
            content_breakdown=visibility_analysis['breakdown'],
            recommendations=recommendations,
            visibility_score=visibility_score
        )
    
    def _extract_llm_visible_content(self, html_content: str, url: str) -> str:
        """
        Extract content exactly as LLMs would see it.
        
        This simulates the text extraction process that LLMs use
        when processing web content.
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements (LLMs don't execute JS or process CSS)
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text content
            text_content = soup.get_text()
            
            # Clean up whitespace (as LLMs would)
            lines = (line.strip() for line in text_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text_content = ' '.join(chunk for chunk in chunks if chunk)
            
            # Add page context
            title = soup.find('title')
            if title:
                title_text = title.get_text().strip()
                text_content = f"{title_text}\n\n{text_content}"
            
            return text_content
            
        except Exception as e:
            logger.error(f"Error extracting content: {e}")
            return f"Error processing content: {str(e)}"
    
    def _analyze_content_visibility(self, content: str, url: str) -> Dict[str, Any]:
        """Analyze what content is visible vs hidden to LLMs."""
        
        # Basic content analysis
        word_count = len(content.split())
        char_count = len(content)
        
        # Check for common hidden content indicators
        hidden_indicators = {
            'javascript_dependent': self._check_javascript_dependency(content),
            'dynamic_content': self._check_dynamic_content(content),
            'minimal_content': word_count < 100,
            'missing_meta': self._check_meta_tags(content)
        }
        
        return {
            'visible': {
                'word_count': word_count,
                'character_count': char_count,
                'has_title': '<title>' in content.lower() or 'title:' in content.lower(),
                'has_description': 'description' in content.lower(),
                'content_quality': 'good' if word_count > 500 else 'minimal' if word_count < 100 else 'adequate'
            },
            'hidden': hidden_indicators,
            'breakdown': {
                'total_content': char_count,
                'visible_percentage': 100 if not any(hidden_indicators.values()) else 70,
                'content_type': 'static' if not hidden_indicators['javascript_dependent'] else 'dynamic'
            }
        }
    
    def _check_javascript_dependency(self, content: str) -> bool:
        """Check if content appears to be JavaScript-dependent."""
        js_indicators = [
            'loading...', 'please wait', 'javascript required',
            'enable javascript', 'react', 'vue', 'angular',
            'single page application', 'spa'
        ]
        
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in js_indicators)
    
    def _check_dynamic_content(self, content: str) -> bool:
        """Check for dynamic content indicators."""
        dynamic_indicators = [
            'ajax', 'fetch', 'xmlhttprequest',
            'dynamic loading', 'lazy load'
        ]
        
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in dynamic_indicators)
    
    def _check_meta_tags(self, content: str) -> bool:
        """Check if essential meta tags are present."""
        has_title = '<title>' in content.lower()
        has_description = 'meta name="description"' in content.lower()
        return has_title and has_description
    
    def _generate_visibility_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on visibility analysis."""
        recommendations = []
        
        visible = analysis['visible']
        hidden = analysis['hidden']
        
        if hidden['minimal_content']:
            recommendations.append("CRITICAL: Content is too minimal for LLM understanding")
        
        if hidden['javascript_dependent']:
            recommendations.append("CRITICAL: Content appears JavaScript-dependent - LLMs cannot execute JS")
        
        if hidden['dynamic_content']:
            recommendations.append("HIGH: Dynamic content detected - implement server-side rendering")
        
        if not visible['has_title']:
            recommendations.append("HIGH: Add descriptive title tag")
        
        if not visible['has_description']:
            recommendations.append("MEDIUM: Add meta description tag")
        
        if visible['content_quality'] == 'minimal':
            recommendations.append("MEDIUM: Increase text content for better LLM context")
        
        return recommendations
    
    def _calculate_visibility_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate LLM visibility score."""
        score = 100.0
        
        visible = analysis['visible']
        hidden = analysis['hidden']
        
        # Deduct for hidden content
        if hidden['minimal_content']:
            score -= 40
        if hidden['javascript_dependent']:
            score -= 30
        if hidden['dynamic_content']:
            score -= 20
        if not visible['has_title']:
            score -= 15
        if not visible['has_description']:
            score -= 10
        
        return max(0, score)
    
    def close(self):
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
