"""
JavaScript Parser Module

Detects JavaScript usage, frameworks, and dynamic content patterns.
"""

import re
import logging
from typing import List, Dict, Set
from bs4 import BeautifulSoup

from ..models.analysis_result import JavaScriptFramework, JavaScriptAnalysis

logger = logging.getLogger(__name__)


class JavaScriptParser:
    """
    Parse and analyze JavaScript usage in HTML.
    
    Detects:
    - Script tags (inline and external)
    - JavaScript frameworks (React, Vue, Angular, etc.)
    - Single Page Application patterns
    - AJAX usage indicators
    """
    
    # Framework detection patterns
    FRAMEWORK_PATTERNS = {
        'React': [
            r'react\.js',
            r'react-dom',
            r'ReactDOM',
            r'__REACT_DEVTOOLS',
            r'data-reactroot',
            r'data-reactid',
            r'_reactRootContainer',
        ],
        'Vue': [
            r'vue\.js',
            r'Vue\.js',
            r'new Vue\(',
            r'v-bind',
            r'v-if',
            r'v-for',
            r'v-model',
            r'__vue__',
        ],
        'Angular': [
            r'angular\.js',
            r'ng-app',
            r'ng-controller',
            r'ng-model',
            r'ng-bind',
            r'\[ngFor\]',
            r'\*ngIf',
            r'platformBrowserDynamic',
        ],
        'Next.js': [
            r'_next/static',
            r'__NEXT_DATA__',
            r'next\.js',
        ],
        'Nuxt': [
            r'__NUXT__',
            r'nuxt\.js',
        ],
        'Svelte': [
            r'svelte',
            r'_svelte',
        ],
        'jQuery': [
            r'jquery\.js',
            r'jQuery',
            r'\$\(',  # jQuery selector
        ],
        'Backbone': [
            r'backbone\.js',
            r'Backbone\.',
        ],
        'Ember': [
            r'ember\.js',
            r'Ember\.',
        ],
        'Gatsby': [
            r'gatsby',
            r'___gatsby',
        ],
        'Alpine': [
            r'alpine\.js',
            r'x-data',
            r'x-bind',
        ],
    }
    
    # SPA indicators
    SPA_INDICATORS = [
        r'<div id="app"',
        r'<div id="root"',
        r'<div id="__next"',
        r'data-reactroot',
        r'ng-app',
        r'v-app',
    ]
    
    # AJAX indicators
    AJAX_INDICATORS = [
        r'XMLHttpRequest',
        r'\.fetch\(',
        r'axios',
        r'ajax\(',
        r'\.get\(',
        r'\.post\(',
    ]
    
    def __init__(self, html_content: str, parser: str = 'lxml'):
        """
        Initialize JavaScript parser.
        
        Args:
            html_content: Raw HTML content as string
            parser: BeautifulSoup parser to use (lxml, html5lib, html.parser)
        """
        self.html_content = html_content
        self.parser = parser
        
        try:
            self.soup = BeautifulSoup(html_content, parser)
        except Exception as e:
            logger.error(f"Failed to parse HTML with {parser}: {e}")
            # Fallback to html.parser
            self.soup = BeautifulSoup(html_content, 'html.parser')
    
    def count_scripts(self) -> Dict[str, int]:
        """
        Count script tags (inline and external).
        
        Returns:
            Dictionary with script counts
        """
        all_scripts = self.soup.find_all('script')
        
        inline = 0
        external = 0
        
        for script in all_scripts:
            if script.get('src'):
                external += 1
            else:
                # Inline script (has content but no src)
                if script.string:
                    inline += 1
        
        return {
            'total': len(all_scripts),
            'inline': inline,
            'external': external
        }
    
    def detect_frameworks(self) -> List[JavaScriptFramework]:
        """
        Detect JavaScript frameworks used.
        
        Returns:
            List of detected frameworks with confidence scores
        """
        detected_frameworks = []
        
        # Get all script content
        script_content = self._get_all_script_content()
        
        # Check each framework
        for framework_name, patterns in self.FRAMEWORK_PATTERNS.items():
            matches = []
            
            for pattern in patterns:
                # Check in script content
                if re.search(pattern, script_content, re.IGNORECASE):
                    matches.append(f"Script: {pattern}")
                
                # Check in HTML attributes and structure
                if re.search(pattern, self.html_content, re.IGNORECASE):
                    matches.append(f"HTML: {pattern}")
            
            if matches:
                # Calculate confidence based on number of matches
                confidence = min(len(matches) / len(patterns), 1.0)
                
                detected_frameworks.append(JavaScriptFramework(
                    name=framework_name,
                    confidence=confidence,
                    indicators=matches[:5]  # Limit to first 5 indicators
                ))
        
        # Sort by confidence (highest first)
        detected_frameworks.sort(key=lambda x: x.confidence, reverse=True)
        
        return detected_frameworks
    
    def _get_all_script_content(self) -> str:
        """
        Get concatenated content of all script tags.
        
        Returns:
            Combined script content
        """
        scripts = self.soup.find_all('script')
        content_parts = []
        
        for script in scripts:
            # Get src attribute
            src = script.get('src', '')
            if src:
                content_parts.append(src)
            
            # Get script content
            if script.string:
                content_parts.append(script.string)
        
        return ' '.join(content_parts)
    
    def detect_spa_patterns(self) -> bool:
        """
        Detect Single Page Application patterns.
        
        Returns:
            True if SPA patterns are detected
        """
        for pattern in self.SPA_INDICATORS:
            if re.search(pattern, self.html_content, re.IGNORECASE):
                return True
        
        return False
    
    def detect_ajax_usage(self) -> bool:
        """
        Detect AJAX usage patterns.
        
        Returns:
            True if AJAX patterns are detected
        """
        script_content = self._get_all_script_content()
        
        for pattern in self.AJAX_INDICATORS:
            if re.search(pattern, script_content, re.IGNORECASE):
                return True
        
        return False
    
    def detect_dynamic_content(self) -> bool:
        """
        Detect indicators of dynamic content loading.
        
        Returns:
            True if dynamic content patterns are detected
        """
        # Check for SPA frameworks
        frameworks = self.detect_frameworks()
        spa_frameworks = ['React', 'Vue', 'Angular', 'Next.js', 'Nuxt', 'Svelte', 'Gatsby']
        
        has_spa_framework = any(
            fw.name in spa_frameworks and fw.confidence > 0.3
            for fw in frameworks
        )
        
        # Check for AJAX
        has_ajax = self.detect_ajax_usage()
        
        # Check for SPA patterns
        has_spa_pattern = self.detect_spa_patterns()
        
        return has_spa_framework or has_ajax or has_spa_pattern
    
    def get_external_script_sources(self) -> List[str]:
        """
        Get list of external script sources.
        
        Returns:
            List of script src URLs
        """
        sources = []
        
        for script in self.soup.find_all('script', src=True):
            src = script.get('src')
            if src:
                sources.append(src)
        
        return sources
    
    def analyze(self) -> JavaScriptAnalysis:
        """
        Perform complete JavaScript analysis.
        
        Returns:
            JavaScriptAnalysis model
        """
        logger.info("Starting JavaScript analysis")
        
        try:
            script_counts = self.count_scripts()
            frameworks = self.detect_frameworks()
            is_spa = self.detect_spa_patterns()
            has_ajax = self.detect_ajax_usage()
            dynamic_content = self.detect_dynamic_content()
            
            result = JavaScriptAnalysis(
                total_scripts=script_counts['total'],
                inline_scripts=script_counts['inline'],
                external_scripts=script_counts['external'],
                frameworks=frameworks,
                is_spa=is_spa,
                has_ajax=has_ajax,
                dynamic_content_detected=dynamic_content
            )
            
            logger.info(
                f"JavaScript analysis complete: {script_counts['total']} scripts, "
                f"{len(frameworks)} frameworks detected, "
                f"SPA={is_spa}, AJAX={has_ajax}, Dynamic={dynamic_content}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error during JavaScript analysis: {e}", exc_info=True)
            raise

