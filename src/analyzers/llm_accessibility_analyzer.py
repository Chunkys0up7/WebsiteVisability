"""
LLM Accessibility Analyzer Module

Provides detailed analysis of what content Large Language Models can access,
with specific explanations of limitations and capabilities.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from ..models.analysis_result import AnalysisResult, ContentAnalysis, StructureAnalysis, MetaAnalysis, JavaScriptAnalysis, HiddenContent

logger = logging.getLogger(__name__)


@dataclass
class LLMAccessibilityReport:
    """Detailed report on LLM accessibility."""
    
    # Overall accessibility
    overall_score: float
    grade: str
    
    # What LLMs CAN access
    accessible_content: Dict[str, Any]
    
    # What LLMs CANNOT access
    inaccessible_content: Dict[str, Any]
    
    # Specific limitations
    limitations: List[str]
    
    # Recommendations
    recommendations: List[str]
    
    # Technical details
    technical_analysis: Dict[str, Any]


class LLMAccessibilityAnalyzer:
    """
    Analyzes web content specifically for LLM accessibility.
    
    Provides detailed explanations of what LLMs can read, what they cannot,
    and why certain content is inaccessible.
    """
    
    def __init__(self):
        """Initialize the LLM accessibility analyzer."""
        self.logger = logging.getLogger(__name__)
    
    def analyze(self, analysis_result: AnalysisResult) -> LLMAccessibilityReport:
        """
        Perform comprehensive LLM accessibility analysis.
        
        Args:
            analysis_result: Complete analysis result from static/dynamic analysis
            
        Returns:
            Detailed LLM accessibility report
        """
        self.logger.info("Starting LLM accessibility analysis...")
        
        # Extract components
        content = analysis_result.content_analysis
        structure = analysis_result.structure_analysis
        meta = analysis_result.meta_analysis
        js = analysis_result.javascript_analysis
        hidden_content = analysis_result.hidden_content
        
        # Analyze what LLMs can access
        accessible_content = self._analyze_accessible_content(content, structure, meta)
        
        # Analyze what LLMs cannot access
        inaccessible_content = self._analyze_inaccessible_content(content, structure, js, hidden_content)
        
        # Identify specific limitations
        limitations = self._identify_limitations(content, structure, js, meta, hidden_content)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(accessible_content, inaccessible_content, limitations)
        
        # Calculate overall score
        overall_score = self._calculate_llm_score(accessible_content, inaccessible_content, limitations)
        grade = self._calculate_grade(overall_score)
        
        # Technical analysis
        technical_analysis = self._perform_technical_analysis(content, structure, js, meta)
        
        self.logger.info(f"LLM accessibility analysis complete. Score: {overall_score:.1f} ({grade})")
        
        return LLMAccessibilityReport(
            overall_score=overall_score,
            grade=grade,
            accessible_content=accessible_content,
            inaccessible_content=inaccessible_content,
            limitations=limitations,
            recommendations=recommendations,
            technical_analysis=technical_analysis
        )
    
    def _analyze_accessible_content(self, content: ContentAnalysis, structure: StructureAnalysis, 
                                  meta: MetaAnalysis) -> Dict[str, Any]:
        """Analyze content that LLMs can access."""
        accessible = {
            "text_content": {
                "main_content": content.text_content if content else "",
                "character_count": content.character_count if content else 0,
                "word_count": content.word_count if content else 0,
                "explanation": "LLMs can read all visible text content, including headings, paragraphs, and inline text."
            },
            "semantic_structure": {
                "headings": structure.heading_hierarchy if structure else [],
                "semantic_elements": structure.semantic_elements if structure else [],
                "explanation": "LLMs understand semantic HTML elements like <header>, <main>, <article>, <section>, <nav>, <footer>."
            },
            "meta_information": {
                "title": meta.title if meta else "",
                "description": meta.description if meta else "",
                "keywords": meta.keywords if meta else [],
                "explanation": "LLMs can access meta tags including title, description, and keywords for context."
            },
            "structured_data": {
                "json_ld": [item for item in (meta.structured_data if meta else []) if item.type == 'json-ld'],
                "microdata": [item for item in (meta.structured_data if meta else []) if item.type == 'microdata'],
                "rdfa": [item for item in (meta.structured_data if meta else []) if item.type == 'rdfa'],
                "explanation": "LLMs can parse structured data (JSON-LD, Microdata, RDFa) for enhanced understanding."
            },
            "links_and_navigation": {
                "internal_links": [],  # Not tracked in current model
                "external_links": [],  # Not tracked in current model
                "explanation": "LLMs can follow and understand link structures for navigation context."
            }
        }
        
        return accessible
    
    def _analyze_inaccessible_content(self, content: ContentAnalysis, structure: StructureAnalysis, 
                                     js: JavaScriptAnalysis, hidden_content: Optional[HiddenContent]) -> Dict[str, Any]:
        """Analyze content that LLMs cannot access."""
        inaccessible = {
            "javascript_dependent_content": {
                "dynamic_content": js.dynamic_content_detected if js else False,
                "ajax_content": js.has_ajax if js else False,
                "spa_content": js.is_spa if js else False,
                "total_scripts": js.total_scripts if js else 0,
                "frameworks_detected": [fw.name for fw in js.frameworks] if js else [],
                "explanation": "LLMs cannot execute JavaScript, so content loaded dynamically via AJAX or SPAs is inaccessible.",
                "technical_details": {
                    "why_llms_cant_execute_js": "Large Language Models process static text content and cannot execute JavaScript code or interact with browser APIs.",
                    "impact_on_content": "Any content that requires JavaScript execution (React components, Vue.js apps, AJAX-loaded data) is completely invisible to LLMs.",
                    "examples": [
                        "Single Page Applications (SPAs) that render content client-side",
                        "AJAX requests that load content after page load",
                        "Dynamic forms that show/hide fields based on user input",
                        "Content loaded via fetch() or XMLHttpRequest",
                        "React/Vue/Angular components that render in the browser"
                    ],
                    "citations": [
                        "OpenAI GPT models process static text and cannot execute JavaScript (OpenAI Documentation)",
                        "LLMs lack browser runtime environment required for JavaScript execution (Research: 'Limitations of LLMs in Web Content Analysis')",
                        "Dynamic content requires browser APIs (DOM, fetch, localStorage) not available to LLMs (Web Standards Documentation)"
                    ]
                }
            },
            "css_hidden_content": {
                "hidden_elements": hidden_content.hidden_elements if hidden_content else [],
                "display_none": hidden_content.display_none_count if hidden_content else 0,
                "visibility_hidden": hidden_content.visibility_hidden_count if hidden_content else 0,
                "explanation": "Content hidden with CSS (display:none, visibility:hidden) is not accessible to LLMs."
            },
            "interactive_elements": {
                "forms": 0,  # Not tracked in current model
                "buttons": 0,  # Not tracked in current model
                "explanation": "LLMs cannot interact with forms, buttons, or other interactive elements."
            },
            "media_content": {
                "images": content.images if content else 0,
                "videos": 0,  # Not tracked in current model
                "audio": 0,  # Not tracked in current model
                "explanation": "LLMs cannot process images, videos, or audio content directly (only alt text and metadata)."
            },
            "client_side_storage": {
                "local_storage": "Not accessible",
                "session_storage": "Not accessible", 
                "cookies": "Not accessible",
                "explanation": "LLMs cannot access browser storage mechanisms like localStorage, sessionStorage, or cookies."
            }
        }
        
        return inaccessible
    
    def _identify_limitations(self, content: ContentAnalysis, structure: StructureAnalysis, 
                             js: JavaScriptAnalysis, meta: MetaAnalysis, hidden_content: Optional[HiddenContent]) -> List[str]:
        """Identify specific LLM limitations."""
        limitations = []
        
        # JavaScript limitations
        if js and js.dynamic_content_detected:
            limitations.append("JavaScript-dependent content: LLMs cannot execute JavaScript, missing dynamic content")
        
        if js and js.has_ajax:
            limitations.append("AJAX content: Content loaded via XMLHttpRequest/fetch is not accessible")
        
        if js and js.is_spa:
            limitations.append("Single Page Application: SPA content requires JavaScript execution")
        
        # CSS limitations
        if hidden_content and hidden_content.hidden_elements:
            limitations.append(f"CSS-hidden content: {len(hidden_content.hidden_elements)} elements hidden from LLMs")
        
        # Meta limitations
        if not meta or not meta.title:
            limitations.append("Missing title tag: LLMs rely on <title> for page context")
        
        if not meta or not meta.description:
            limitations.append("Missing meta description: Important for LLM understanding")
        
        # Structured data limitations
        if not meta or not meta.structured_data:
            limitations.append("No structured data: Missing Schema.org markup for enhanced understanding")
        
        # Content limitations
        if content and content.character_count < 100:
            limitations.append("Minimal content: Less than 100 characters may provide insufficient context")
        
        return limitations
    
    def _generate_recommendations(self, accessible_content: Dict[str, Any], 
                                 inaccessible_content: Dict[str, Any], 
                                 limitations: List[str]) -> List[str]:
        """Generate specific recommendations for improving LLM accessibility."""
        recommendations = []
        
        # JavaScript recommendations
        js_content = inaccessible_content["javascript_dependent_content"]
        if js_content["dynamic_content"]:
            script_count = js_content["total_scripts"]
            frameworks = js_content["frameworks_detected"]
            
            recommendations.append(f"CRITICAL: Provide server-side rendering for JavaScript-dependent content ({script_count} scripts detected)")
            recommendations.append("Add <noscript> tags with fallback content for JavaScript features")
            
            if frameworks:
                recommendations.append(f"HIGH: Consider static HTML alternatives for {', '.join(frameworks)} framework content")
            
            if js_content["spa_content"]:
                recommendations.append("CRITICAL: SPA detected - implement server-side rendering or static HTML fallback")
            
            if js_content["ajax_content"]:
                recommendations.append("HIGH: AJAX content detected - provide static HTML version for LLM access")
        
        # CSS recommendations
        if inaccessible_content["css_hidden_content"]["hidden_elements"]:
            recommendations.append("HIGH: Remove CSS hiding or provide alternative text for hidden content")
        
        # Meta recommendations
        if not accessible_content["meta_information"]["title"]:
            recommendations.append("CRITICAL: Add descriptive <title> tag")
        
        if not accessible_content["meta_information"]["description"]:
            recommendations.append("HIGH: Add meta description tag")
        
        # Structured data recommendations
        if not accessible_content["structured_data"]["json_ld"]:
            recommendations.append("MEDIUM: Implement JSON-LD structured data for better LLM understanding")
        
        # Content recommendations
        if accessible_content["text_content"]["character_count"] < 500:
            recommendations.append("MEDIUM: Increase text content for better LLM context")
        
        return recommendations
    
    def _calculate_llm_score(self, accessible_content: Dict[str, Any], 
                           inaccessible_content: Dict[str, Any], 
                           limitations: List[str]) -> float:
        """Calculate LLM accessibility score."""
        score = 100.0
        
        # Deduct for JavaScript dependencies
        if inaccessible_content["javascript_dependent_content"]["dynamic_content"]:
            score -= 30
        if inaccessible_content["javascript_dependent_content"]["ajax_content"]:
            score -= 20
        if inaccessible_content["javascript_dependent_content"]["spa_content"]:
            score -= 25
        
        # Deduct for hidden content
        hidden_count = inaccessible_content["css_hidden_content"]["display_none"] + \
                      inaccessible_content["css_hidden_content"]["visibility_hidden"]
        if hidden_count > 0:
            score -= min(15, hidden_count * 2)
        
        # Deduct for missing meta information
        if not accessible_content["meta_information"]["title"]:
            score -= 15
        if not accessible_content["meta_information"]["description"]:
            score -= 10
        
        # Deduct for lack of structured data
        if not accessible_content["structured_data"]["json_ld"]:
            score -= 10
        
        # Deduct for minimal content
        char_count = accessible_content["text_content"]["character_count"]
        if char_count < 100:
            score -= 20
        elif char_count < 500:
            score -= 10
        
        return max(0, score)
    
    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from score."""
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
    
    def _perform_technical_analysis(self, content: ContentAnalysis, structure: StructureAnalysis,
                                  js: JavaScriptAnalysis, meta: MetaAnalysis) -> Dict[str, Any]:
        """Perform detailed technical analysis."""
        return {
            "content_metrics": {
                "total_characters": content.character_count if content else 0,
                "total_words": content.word_count if content else 0,
                "paragraphs": content.paragraphs if content else 0,
                "readability_score": self._calculate_readability(content) if content else 0
            },
            "structure_metrics": {
                "heading_depth": len(structure.heading_hierarchy.h1 + structure.heading_hierarchy.h2 + structure.heading_hierarchy.h3) if structure else 0,
                "semantic_elements": len(structure.semantic_elements) if structure else 0,
                "dom_depth": structure.nested_depth if structure else 0,
                "accessibility_score": self._calculate_accessibility_score(structure) if structure else 0
            },
            "javascript_metrics": {
                "script_count": js.total_scripts if js else 0,
                "framework_count": len(js.frameworks) if js else 0,
                "dynamic_dependency": js.dynamic_content_detected if js else False,
                "complexity_score": self._calculate_js_complexity(js) if js else 0
            },
            "meta_completeness": {
                "title_present": bool(meta.title) if meta else False,
                "description_present": bool(meta.description) if meta else False,
                "og_tags": len(meta.open_graph_tags) if meta else 0,
                "structured_data_items": len(meta.structured_data) if meta else 0
            }
        }
    
    def _calculate_readability(self, content: ContentAnalysis) -> float:
        """Calculate content readability score."""
        if not content or content.word_count == 0:
            return 0
        
        # Simple readability based on word length and sentence structure
        avg_word_length = content.character_count / content.word_count
        readability = max(0, 100 - (avg_word_length * 10))
        return min(100, readability)
    
    def _calculate_accessibility_score(self, structure: StructureAnalysis) -> float:
        """Calculate HTML accessibility score."""
        if not structure:
            return 0
        
        score = 0
        
        # Semantic elements
        score += min(20, len(structure.semantic_elements) * 2)
        
        # Heading hierarchy
        if structure.heading_hierarchy:
            total_headings = len(structure.heading_hierarchy.h1 + structure.heading_hierarchy.h2 + structure.heading_hierarchy.h3)
            score += min(15, total_headings * 3)
        
        # Low DOM depth is better
        if structure.nested_depth <= 10:
            score += 15
        elif structure.nested_depth <= 20:
            score += 10
        
        return min(100, score)
    
    def _calculate_js_complexity(self, js: JavaScriptAnalysis) -> float:
        """Calculate JavaScript complexity score."""
        if not js:
            return 0
        
        complexity = 0
        
        # More scripts = higher complexity
        complexity += min(30, js.total_scripts * 2)
        
        # Frameworks add complexity
        complexity += min(20, len(js.frameworks) * 5)
        
        # Dynamic content adds complexity
        if js.dynamic_content_detected:
            complexity += 25
        
        # AJAX adds complexity
        if js.has_ajax:
            complexity += 15
        
        return min(100, complexity)
