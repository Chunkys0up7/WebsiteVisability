"""
SSR (Server-Side Rendering) Detection Module

Detects whether a website uses server-side rendering, client-side rendering,
or hybrid rendering approaches.
"""

import logging
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SSRDetectionResult:
    """Results from SSR detection analysis"""
    is_ssr: bool
    rendering_type: str  # 'ssr', 'csr', 'hybrid', 'unknown'
    confidence: float  # 0-1
    evidence: List[str]
    framework_indicators: List[str]
    performance_indicators: Dict[str, Any]


class SSRDetector:
    """
    Detects server-side rendering patterns and framework usage.
    
    Analyzes HTML content, JavaScript patterns, and meta tags to determine
    if a website uses SSR, CSR, or hybrid rendering.
    """
    
    def __init__(self):
        """Initialize the SSR detector."""
        self.logger = logging.getLogger(__name__)
        
        # SSR indicators
        self.ssr_indicators = [
            # Meta tags indicating SSR
            r'<meta[^>]*name=["\']?generator["\']?[^>]*content=["\']?(next\.js|nuxt\.js|gatsby|sveltekit)',
            r'<meta[^>]*name=["\']?framework["\']?[^>]*content=["\']?(next|nuxt|gatsby|sveltekit)',
            
            # HTML structure indicators
            r'<div[^>]*id=["\']?__next["\']?',  # Next.js
            r'<div[^>]*id=["\']?__nuxt["\']?',  # Nuxt.js
            r'<div[^>]*id=["\']?___gatsby["\']?',  # Gatsby
            
            # Data attributes
            r'data-reactroot',  # React SSR
            r'data-vue-ssr-id',  # Vue SSR
            r'data-svelte-hydrate',  # Svelte SSR
        ]
        
        # CSR indicators
        self.csr_indicators = [
            # Empty or minimal initial content
            r'<body[^>]*>\s*<div[^>]*id=["\']?app["\']?[^>]*>\s*</div>',
            r'<body[^>]*>\s*<div[^>]*id=["\']?root["\']?[^>]*>\s*</div>',
            
            # Loading indicators
            r'<div[^>]*class=["\'][^"\']*loading[^"\']*["\'][^>]*>',
            r'<div[^>]*id=["\']?loading["\']?[^>]*>',
        ]
        
        # Framework-specific patterns
        self.framework_patterns = {
            'next.js': [
                r'_next/static/',
                r'__NEXT_DATA__',
                r'next\.js',
                r'<div[^>]*id=["\']?__next["\']?'
            ],
            'nuxt.js': [
                r'_nuxt/',
                r'__NUXT__',
                r'nuxt\.js',
                r'<div[^>]*id=["\']?__nuxt["\']?'
            ],
            'gatsby': [
                r'___gatsby',
                r'gatsby',
                r'<div[^>]*id=["\']?___gatsby["\']?'
            ],
            'sveltekit': [
                r'_app/',
                r'sveltekit',
                r'<div[^>]*data-svelte-hydrate'
            ],
            'react': [
                r'react',
                r'data-reactroot',
                r'ReactDOM\.render'
            ],
            'vue': [
                r'vue\.js',
                r'data-vue-ssr-id',
                r'Vue\.createApp'
            ],
            'angular': [
                r'angular',
                r'ng-',
                r'<app-root'
            ]
        }
    
    def detect_ssr(self, html_content: str, js_analysis: Optional[Any] = None) -> SSRDetectionResult:
        """
        Detect if the website uses server-side rendering.
        
        Args:
            html_content: Raw HTML content
            js_analysis: Optional JavaScript analysis results
            
        Returns:
            SSRDetectionResult with detection details
        """
        self.logger.info("Starting SSR detection analysis...")
        
        evidence = []
        framework_indicators = []
        confidence = 0.0
        
        # Check for SSR indicators
        ssr_score = 0
        for pattern in self.ssr_indicators:
            if re.search(pattern, html_content, re.IGNORECASE):
                ssr_score += 1
                evidence.append(f"Found SSR indicator: {pattern}")
        
        # Check for CSR indicators
        csr_score = 0
        for pattern in self.csr_indicators:
            if re.search(pattern, html_content, re.IGNORECASE):
                csr_score += 1
                evidence.append(f"Found CSR indicator: {pattern}")
        
        # Detect frameworks
        detected_frameworks = []
        for framework, patterns in self.framework_patterns.items():
            for pattern in patterns:
                if re.search(pattern, html_content, re.IGNORECASE):
                    detected_frameworks.append(framework)
                    framework_indicators.append(f"{framework}: {pattern}")
                    break
        
        # Analyze JavaScript patterns if available
        js_indicators = {}
        if js_analysis:
            js_indicators = self._analyze_js_patterns(js_analysis)
        
        # Determine rendering type and confidence
        rendering_type, confidence = self._determine_rendering_type(
            ssr_score, csr_score, detected_frameworks, js_indicators
        )
        
        # Performance indicators
        performance_indicators = self._analyze_performance_indicators(html_content)
        
        self.logger.info(f"SSR detection complete: {rendering_type} (confidence: {confidence:.2f})")
        
        return SSRDetectionResult(
            is_ssr=(rendering_type == 'ssr'),
            rendering_type=rendering_type,
            confidence=confidence,
            evidence=evidence,
            framework_indicators=framework_indicators,
            performance_indicators=performance_indicators
        )
    
    def _analyze_js_patterns(self, js_analysis: Any) -> Dict[str, Any]:
        """Analyze JavaScript patterns for rendering clues."""
        indicators = {
            'has_ssr_frameworks': False,
            'has_csr_frameworks': False,
            'dynamic_content': False,
            'spa_patterns': False
        }
        
        if hasattr(js_analysis, 'frameworks'):
            for framework in js_analysis.frameworks:
                if hasattr(framework, 'name'):
                    framework_name = framework.name.lower()
                    if framework_name in ['next.js', 'nuxt.js', 'gatsby', 'sveltekit']:
                        indicators['has_ssr_frameworks'] = True
                    elif framework_name in ['react', 'vue', 'angular']:
                        indicators['has_csr_frameworks'] = True
        
        if hasattr(js_analysis, 'dynamic_content_detected'):
            indicators['dynamic_content'] = js_analysis.dynamic_content_detected
        
        if hasattr(js_analysis, 'is_spa'):
            indicators['spa_patterns'] = js_analysis.is_spa
        
        return indicators
    
    def _determine_rendering_type(self, ssr_score: int, csr_score: int, 
                                frameworks: List[str], js_indicators: Dict[str, Any]) -> tuple[str, float]:
        """Determine rendering type and confidence score."""
        
        # SSR frameworks
        ssr_frameworks = ['next.js', 'nuxt.js', 'gatsby', 'sveltekit']
        csr_frameworks = ['react', 'vue', 'angular']
        
        has_ssr_framework = any(fw in frameworks for fw in ssr_frameworks)
        has_csr_framework = any(fw in frameworks for fw in csr_frameworks)
        
        # Calculate confidence
        confidence = 0.0
        
        if has_ssr_framework and ssr_score > 0:
            rendering_type = 'ssr'
            confidence = min(0.9, 0.5 + (ssr_score * 0.1) + (len(frameworks) * 0.1))
        elif has_csr_framework and csr_score > 0:
            rendering_type = 'csr'
            confidence = min(0.9, 0.5 + (csr_score * 0.1) + (len(frameworks) * 0.1))
        elif ssr_score > csr_score:
            rendering_type = 'ssr'
            confidence = min(0.7, 0.3 + (ssr_score * 0.1))
        elif csr_score > ssr_score:
            rendering_type = 'csr'
            confidence = min(0.7, 0.3 + (csr_score * 0.1))
        elif has_ssr_framework and has_csr_framework:
            rendering_type = 'hybrid'
            confidence = 0.8
        else:
            rendering_type = 'unknown'
            confidence = 0.2
        
        return rendering_type, confidence
    
    def _analyze_performance_indicators(self, html_content: str) -> Dict[str, Any]:
        """Analyze performance-related indicators."""
        indicators = {
            'has_critical_css': False,
            'has_preload_links': False,
            'has_resource_hints': False,
            'estimated_initial_content': 0
        }
        
        # Check for critical CSS
        if re.search(r'<style[^>]*>.*</style>', html_content, re.DOTALL):
            indicators['has_critical_css'] = True
        
        # Check for preload links
        if re.search(r'<link[^>]*rel=["\']?preload["\']?', html_content, re.IGNORECASE):
            indicators['has_preload_links'] = True
        
        # Check for resource hints
        if re.search(r'<link[^>]*rel=["\']?(preload|prefetch|dns-prefetch)["\']?', html_content, re.IGNORECASE):
            indicators['has_resource_hints'] = True
        
        # Estimate initial content size
        body_match = re.search(r'<body[^>]*>(.*)</body>', html_content, re.DOTALL | re.IGNORECASE)
        if body_match:
            body_content = body_match.group(1)
            # Remove script tags for content estimation
            content_without_scripts = re.sub(r'<script[^>]*>.*?</script>', '', body_content, flags=re.DOTALL)
            indicators['estimated_initial_content'] = len(content_without_scripts.strip())
        
        return indicators
