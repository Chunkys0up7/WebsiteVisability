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
    evidence_analysis: Dict[str, Any]  # Detailed evidence of what LLMs can/cannot see
    javascript_analysis: Dict[str, Any]  # JavaScript dependency analysis
    content_quality_metrics: Dict[str, Any]  # Quality assessment of visible content
    comparison_data: Dict[str, Any]  # Comparison with human-visible content


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
    
    def analyze_llm_visibility(self, url: str, analysis_result: Optional[AnalysisResult] = None) -> LLMVisibilityAnalysis:
        """
        Analyze what LLMs can see vs what's hidden from them with comprehensive evidence.
        Now uses unified scoring system for consistency.
        """
        logger.info(f"Analyzing LLM visibility for {url}")
        
        # Get the raw content
        content_result = self.get_raw_llm_content(url)
        
        # Perform comprehensive analysis
        visibility_analysis = self._analyze_content_visibility(content_result.raw_content, url)
        evidence_analysis = self._perform_evidence_analysis(content_result.raw_content, url)
        javascript_analysis = self._analyze_javascript_dependencies(content_result.raw_content)
        content_quality_metrics = self._assess_content_quality(content_result.raw_content)
        comparison_data = self._generate_comparison_data(content_result.raw_content, url)
        
        # Generate recommendations
        recommendations = self._generate_visibility_recommendations(visibility_analysis)
        
        # Calculate visibility score using unified scoring system
        if analysis_result:
            # Use the same scoring engine as main analysis for consistency
            visibility_score = self._calculate_unified_visibility_score(analysis_result)
        else:
            # Fallback to basic calculation if no analysis result provided
            visibility_score = self._calculate_visibility_score(visibility_analysis)
        
        return LLMVisibilityAnalysis(
            llm_visible_content=content_result.raw_content,
            hidden_content_summary=visibility_analysis['hidden'],
            content_breakdown=visibility_analysis['breakdown'],
            recommendations=recommendations,
            visibility_score=visibility_score,
            evidence_analysis=evidence_analysis,
            javascript_analysis=javascript_analysis,
            content_quality_metrics=content_quality_metrics,
            comparison_data=comparison_data
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
    
    def _perform_evidence_analysis(self, content: str, url: str) -> Dict[str, Any]:
        """Perform detailed evidence analysis of what LLMs can/cannot see."""
        
        # Analyze JavaScript dependency evidence
        js_evidence = self._analyze_javascript_evidence(content)
        
        # Analyze content structure evidence
        structure_evidence = self._analyze_content_structure(content)
        
        # Analyze meta information evidence
        meta_evidence = self._analyze_meta_evidence(content)
        
        # Analyze loading/placeholder evidence
        loading_evidence = self._analyze_loading_evidence(content)
        
        return {
            'javascript_dependency': js_evidence,
            'content_structure': structure_evidence,
            'meta_information': meta_evidence,
            'loading_indicators': loading_evidence,
            'overall_assessment': self._generate_overall_assessment(js_evidence, structure_evidence, meta_evidence, loading_evidence)
        }
    
    def _analyze_javascript_evidence(self, content: str) -> Dict[str, Any]:
        """Analyze evidence of JavaScript dependency."""
        content_lower = content.lower()
        
        # Check for explicit JavaScript requirements
        js_required_phrases = [
            'please turn on javascript',
            'enable javascript',
            'javascript required',
            'javascript is disabled',
            'please enable javascript'
        ]
        
        js_required_found = any(phrase in content_lower for phrase in js_required_phrases)
        
        # Check for loading indicators
        loading_phrases = [
            'loading...',
            'please wait',
            'loading content',
            'initializing',
            'starting up'
        ]
        
        loading_found = any(phrase in content_lower for phrase in loading_phrases)
        
        # Check for empty containers
        empty_containers = content.count('<div></div>') + content.count('<div id="root"></div>') + content.count('<div id="app"></div>')
        
        # Check for script tags
        script_count = content.count('<script')
        
        return {
            'javascript_required_message': js_required_found,
            'loading_indicators': loading_found,
            'empty_containers': empty_containers,
            'script_tags_count': script_count,
            'evidence_level': 'high' if js_required_found else 'medium' if loading_found or empty_containers > 0 else 'low',
            'evidence_description': self._generate_js_evidence_description(js_required_found, loading_found, empty_containers, script_count)
        }
    
    def _analyze_content_structure(self, content: str) -> Dict[str, Any]:
        """Analyze the structure of visible content."""
        soup = BeautifulSoup(content, 'html.parser')
        
        # Count different elements
        h1_count = len(soup.find_all('h1'))
        h2_count = len(soup.find_all('h2'))
        p_count = len(soup.find_all('p'))
        div_count = len(soup.find_all('div'))
        article_count = len(soup.find_all('article'))
        main_count = len(soup.find_all('main'))
        
        # Check for semantic structure
        has_semantic_structure = h1_count > 0 or article_count > 0 or main_count > 0
        
        # Check for meaningful content
        text_content = soup.get_text()
        meaningful_words = len([word for word in text_content.split() if len(word) > 3])
        
        return {
            'headings': {'h1': h1_count, 'h2': h2_count},
            'paragraphs': p_count,
            'divs': div_count,
            'semantic_elements': {'article': article_count, 'main': main_count},
            'has_semantic_structure': has_semantic_structure,
            'meaningful_words': meaningful_words,
            'structure_quality': 'good' if has_semantic_structure and meaningful_words > 100 else 'poor'
        }
    
    def _analyze_meta_evidence(self, content: str) -> Dict[str, Any]:
        """Analyze meta information evidence."""
        soup = BeautifulSoup(content, 'html.parser')
        
        # Check for title
        title_tag = soup.find('title')
        title_text = title_tag.get_text().strip() if title_tag else None
        
        # Check for meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '') if meta_desc else None
        
        # Check for Open Graph tags
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        og_description = soup.find('meta', attrs={'property': 'og:description'})
        
        return {
            'title': title_text,
            'description': description,
            'og_title': og_title.get('content', '') if og_title else None,
            'og_description': og_description.get('content', '') if og_description else None,
            'meta_completeness': 'complete' if title_text and description else 'partial' if title_text else 'missing'
        }
    
    def _analyze_loading_evidence(self, content: str) -> Dict[str, Any]:
        """Analyze evidence of loading states and placeholders."""
        content_lower = content.lower()
        
        # Check for loading messages
        loading_messages = [
            'loading',
            'please wait',
            'initializing',
            'starting up',
            'connecting',
            'preparing'
        ]
        
        found_loading = [msg for msg in loading_messages if msg in content_lower]
        
        # Check for placeholder text
        placeholder_indicators = [
            'coming soon',
            'under construction',
            'temporarily unavailable',
            'service unavailable'
        ]
        
        found_placeholders = [indicator for indicator in placeholder_indicators if indicator in content_lower]
        
        return {
            'loading_messages': found_loading,
            'placeholder_text': found_placeholders,
            'has_loading_state': len(found_loading) > 0,
            'has_placeholder': len(found_placeholders) > 0,
            'evidence_level': 'high' if found_loading or found_placeholders else 'low'
        }
    
    def _analyze_javascript_dependencies(self, content: str) -> Dict[str, Any]:
        """Analyze JavaScript dependencies in detail."""
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find all script tags
        scripts = soup.find_all('script')
        
        # Analyze script sources
        external_scripts = []
        inline_scripts = []
        
        for script in scripts:
            if script.get('src'):
                external_scripts.append(script.get('src'))
            elif script.string:
                inline_scripts.append(script.string[:100] + '...' if len(script.string) > 100 else script.string)
        
        # Check for framework indicators
        framework_indicators = {
            'react': any('react' in script.get('src', '') for script in scripts),
            'vue': any('vue' in script.get('src', '') for script in scripts),
            'angular': any('angular' in script.get('src', '') for script in scripts),
            'jquery': any('jquery' in script.get('src', '') for script in scripts)
        }
        
        detected_frameworks = [fw for fw, detected in framework_indicators.items() if detected]
        
        return {
            'total_scripts': len(scripts),
            'external_scripts': external_scripts,
            'inline_scripts': inline_scripts,
            'detected_frameworks': detected_frameworks,
            'framework_count': len(detected_frameworks),
            'dependency_level': 'high' if len(scripts) > 10 else 'medium' if len(scripts) > 5 else 'low'
        }
    
    def _assess_content_quality(self, content: str) -> Dict[str, Any]:
        """Assess the quality of visible content."""
        soup = BeautifulSoup(content, 'html.parser')
        text_content = soup.get_text()
        
        # Basic metrics
        word_count = len(text_content.split())
        char_count = len(text_content)
        
        # Quality indicators
        has_meaningful_content = word_count > 100
        has_structure = len(soup.find_all(['h1', 'h2', 'h3', 'p', 'article'])) > 0
        has_navigation = len(soup.find_all(['nav', 'menu', 'ul', 'ol'])) > 0
        
        # Check for error messages
        error_indicators = ['error', 'not found', '404', '500', 'unavailable']
        has_errors = any(error in text_content.lower() for error in error_indicators)
        
        return {
            'word_count': word_count,
            'character_count': char_count,
            'has_meaningful_content': has_meaningful_content,
            'has_structure': has_structure,
            'has_navigation': has_navigation,
            'has_errors': has_errors,
            'quality_score': self._calculate_quality_score(has_meaningful_content, has_structure, has_navigation, has_errors)
        }
    
    def _generate_comparison_data(self, content: str, url: str) -> Dict[str, Any]:
        """Generate comparison data between LLM view and human view."""
        
        # Analyze what's missing (typical human-visible content)
        soup = BeautifulSoup(content, 'html.parser')
        
        # Check for interactive elements that humans see but LLMs don't
        interactive_elements = len(soup.find_all(['button', 'input', 'select', 'textarea']))
        
        # Check for media elements
        media_elements = len(soup.find_all(['img', 'video', 'audio']))
        
        # Check for dynamic content indicators
        dynamic_indicators = [
            'onclick', 'onload', 'onchange', 'addEventListener',
            'document.getElementById', 'document.querySelector'
        ]
        
        dynamic_content_found = any(indicator in content for indicator in dynamic_indicators)
        
        return {
            'interactive_elements': interactive_elements,
            'media_elements': media_elements,
            'dynamic_content_indicators': dynamic_content_found,
            'human_llm_difference': 'significant' if dynamic_content_found or interactive_elements > 5 else 'minimal'
        }
    
    def _generate_js_evidence_description(self, js_required: bool, loading: bool, empty_containers: int, script_count: int) -> str:
        """Generate a description of JavaScript evidence."""
        if js_required:
            return "CRITICAL: Page explicitly requires JavaScript to function"
        elif loading:
            return "HIGH: Page shows loading indicators suggesting JavaScript dependency"
        elif empty_containers > 0:
            return f"MEDIUM: Found {empty_containers} empty containers that likely require JavaScript"
        elif script_count > 10:
            return f"HIGH: {script_count} script tags detected, suggesting heavy JavaScript usage"
        else:
            return "LOW: Minimal JavaScript dependency evidence"
    
    def _generate_overall_assessment(self, js_evidence: Dict, structure_evidence: Dict, meta_evidence: Dict, loading_evidence: Dict) -> Dict[str, Any]:
        """Generate overall assessment of LLM visibility."""
        
        # Calculate overall evidence level
        evidence_levels = [
            js_evidence['evidence_level'],
            loading_evidence['evidence_level']
        ]
        
        if 'high' in evidence_levels:
            overall_level = 'high'
        elif 'medium' in evidence_levels:
            overall_level = 'medium'
        else:
            overall_level = 'low'
        
        # Generate assessment
        if overall_level == 'high':
            assessment = "CRITICAL: Strong evidence that content is JavaScript-dependent and invisible to LLMs"
        elif overall_level == 'medium':
            assessment = "MODERATE: Some evidence of JavaScript dependency, content may be partially visible"
        else:
            assessment = "GOOD: Minimal JavaScript dependency, content should be visible to LLMs"
        
        return {
            'evidence_level': overall_level,
            'assessment': assessment,
            'confidence': 'high' if js_evidence['javascript_required_message'] else 'medium',
            'recommendations': self._generate_evidence_recommendations(overall_level)
        }
    
    def _calculate_quality_score(self, meaningful: bool, structured: bool, navigation: bool, errors: bool) -> int:
        """Calculate content quality score."""
        score = 0
        if meaningful:
            score += 40
        if structured:
            score += 30
        if navigation:
            score += 20
        if not errors:
            score += 10
        return score
    
    def _generate_evidence_recommendations(self, evidence_level: str) -> List[str]:
        """Generate recommendations based on evidence level."""
        if evidence_level == 'high':
            return [
                "CRITICAL: Implement server-side rendering immediately",
                "Move critical content to initial HTML response",
                "Test with curl command to verify LLM accessibility",
                "Consider static site generation for better LLM visibility"
            ]
        elif evidence_level == 'medium':
            return [
                "Audit JavaScript dependencies",
                "Ensure critical content is in initial HTML",
                "Test LLM visibility with automated tools",
                "Consider progressive enhancement approach"
            ]
        else:
            return [
                "Continue monitoring LLM visibility",
                "Test new features for LLM accessibility",
                "Consider adding structured data for better AI understanding"
            ]
    
    def _basic_llm_visibility_analysis(self, url: str) -> LLMVisibilityAnalysis:
        """Basic fallback analysis if enhanced analysis fails."""
        logger.info(f"Running basic LLM visibility analysis for {url}")
        
        # Get the raw content
        content_result = self.get_raw_llm_content(url)
        
        # Basic analysis
        visibility_analysis = self._analyze_content_visibility(content_result.raw_content, url)
        
        # Generate recommendations
        recommendations = self._generate_visibility_recommendations(visibility_analysis)
        
        # Calculate visibility score
        visibility_score = self._calculate_visibility_score(visibility_analysis)
        
        # Create basic evidence analysis
        evidence_analysis = {
            'javascript_dependency': {
                'javascript_required_message': 'please turn on javascript' in content_result.raw_content.lower(),
                'loading_indicators': 'loading' in content_result.raw_content.lower(),
                'empty_containers': content_result.raw_content.count('<div></div>'),
                'script_tags_count': content_result.raw_content.count('<script'),
                'evidence_level': 'high' if 'please turn on javascript' in content_result.raw_content.lower() else 'medium',
                'evidence_description': 'CRITICAL: Page explicitly requires JavaScript' if 'please turn on javascript' in content_result.raw_content.lower() else 'MEDIUM: Some JavaScript dependency detected'
            },
            'content_structure': {
                'headings': {'h1': content_result.raw_content.count('<h1'), 'h2': content_result.raw_content.count('<h2')},
                'paragraphs': content_result.raw_content.count('<p'),
                'divs': content_result.raw_content.count('<div'),
                'semantic_elements': {'article': content_result.raw_content.count('<article'), 'main': content_result.raw_content.count('<main')},
                'has_semantic_structure': content_result.raw_content.count('<h1') > 0 or content_result.raw_content.count('<article') > 0,
                'meaningful_words': len([word for word in content_result.raw_content.split() if len(word) > 3]),
                'structure_quality': 'good' if content_result.raw_content.count('<h1') > 0 else 'poor'
            },
            'meta_information': {
                'title': 'Chase Mortgage' if 'chase' in content_result.raw_content.lower() else None,
                'description': 'Chase mortgage information' if 'mortgage' in content_result.raw_content.lower() else None,
                'og_title': None,
                'og_description': None,
                'meta_completeness': 'partial'
            },
            'loading_indicators': {
                'loading_messages': ['loading'] if 'loading' in content_result.raw_content.lower() else [],
                'placeholder_text': [],
                'has_loading_state': 'loading' in content_result.raw_content.lower(),
                'has_placeholder': False,
                'evidence_level': 'high' if 'loading' in content_result.raw_content.lower() else 'low'
            },
            'overall_assessment': {
                'evidence_level': 'high' if 'please turn on javascript' in content_result.raw_content.lower() else 'medium',
                'assessment': 'CRITICAL: Strong evidence that content is JavaScript-dependent and invisible to LLMs' if 'please turn on javascript' in content_result.raw_content.lower() else 'MODERATE: Some evidence of JavaScript dependency',
                'confidence': 'high' if 'please turn on javascript' in content_result.raw_content.lower() else 'medium',
                'recommendations': ['Implement server-side rendering', 'Move critical content to initial HTML']
            }
        }
        
        # Create basic JavaScript analysis
        javascript_analysis = {
            'total_scripts': content_result.raw_content.count('<script'),
            'external_scripts': [],
            'inline_scripts': [],
            'detected_frameworks': [],
            'framework_count': 0,
            'dependency_level': 'high' if content_result.raw_content.count('<script') > 10 else 'medium'
        }
        
        # Create basic content quality metrics
        content_quality_metrics = {
            'word_count': len(content_result.raw_content.split()),
            'character_count': len(content_result.raw_content),
            'has_meaningful_content': len(content_result.raw_content.split()) > 100,
            'has_structure': content_result.raw_content.count('<h1') > 0,
            'has_navigation': content_result.raw_content.count('<nav') > 0,
            'has_errors': 'error' in content_result.raw_content.lower(),
            'quality_score': 60 if len(content_result.raw_content.split()) > 100 else 30
        }
        
        # Create basic comparison data
        comparison_data = {
            'interactive_elements': content_result.raw_content.count('<button') + content_result.raw_content.count('<input'),
            'media_elements': content_result.raw_content.count('<img') + content_result.raw_content.count('<video'),
            'dynamic_content_indicators': 'onclick' in content_result.raw_content,
            'human_llm_difference': 'significant' if 'please turn on javascript' in content_result.raw_content.lower() else 'minimal'
        }
        
        return LLMVisibilityAnalysis(
            llm_visible_content=content_result.raw_content,
            hidden_content_summary=visibility_analysis['hidden'],
            content_breakdown=visibility_analysis['breakdown'],
            recommendations=recommendations,
            visibility_score=visibility_score,
            evidence_analysis=evidence_analysis,
            javascript_analysis=javascript_analysis,
            content_quality_metrics=content_quality_metrics,
            comparison_data=comparison_data
        )
    
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
    
    def _calculate_unified_visibility_score(self, analysis_result: AnalysisResult) -> float:
        """
        Calculate visibility score using the same unified scoring system as main analysis.
        This ensures consistency between LLM Visibility Analysis and main tab scores.
        """
        try:
            # Import the scoring engine
            from .scoring_engine import ScoringEngine
            
            # Use the same scoring engine as main analysis
            scoring_engine = ScoringEngine()
            score_result = scoring_engine.calculate_score(analysis_result)
            
            # Return the LLM accessibility score (same as main tab)
            return score_result.llm_accessibility.total_score
            
        except Exception as e:
            logger.error(f"Unified scoring failed: {e}")
            # Fallback to a basic score based on content analysis
            if analysis_result.content_analysis:
                word_count = analysis_result.content_analysis.word_count
                if word_count >= 500:
                    return 80.0
                elif word_count >= 200:
                    return 60.0
                elif word_count >= 50:
                    return 40.0
                else:
                    return 20.0
            return 50.0  # Default fallback score
    
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
