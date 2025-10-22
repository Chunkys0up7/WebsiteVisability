"""
Bot Directives Analyzer

Analyzes both robots.txt and llms.txt files to understand crawler and LLM directives.
Combines traditional web crawler directives with modern LLM guidance.
"""

import logging
import requests
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import re

logger = logging.getLogger(__name__)


@dataclass
class RobotsTxtAnalysis:
    """Analysis results for robots.txt file"""
    is_present: bool
    url: Optional[str]
    content: Optional[str]
    format_valid: bool
    sections: Dict[str, List[str]]
    user_agents: List[str]
    disallowed_paths: List[str]
    allowed_paths: List[str]
    sitemaps: List[str]
    crawl_delay: Optional[int]
    recommendations: List[str]
    issues: List[str]


@dataclass
class LLMsTxtAnalysis:
    """Analysis results for llms.txt file"""
    is_present: bool
    url: Optional[str]
    content: Optional[str]
    format_valid: bool
    sections: Dict[str, List[str]]
    quality_score: float
    recommendations: List[str]
    issues: List[str]
    benefits: List[str]


@dataclass
class BotDirectivesAnalysis:
    """Combined analysis of robots.txt and llms.txt"""
    robots_txt: RobotsTxtAnalysis
    llms_txt: LLMsTxtAnalysis
    combined_recommendations: List[str]
    combined_issues: List[str]
    compatibility_score: float


class BotDirectivesAnalyzer:
    """
    Analyzes both robots.txt and llms.txt files.
    
    Provides insights into how well the site manages both traditional web crawlers
    and modern LLM-based systems.
    """
    
    def __init__(self, timeout: int = 10, user_agent: str = "Mozilla/5.0 (compatible; WebScraperLLMAnalyzer/1.0)"):
        """Initialize the analyzer."""
        self.timeout = timeout
        self.user_agent = user_agent
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})
    
    def analyze(self, base_url: str) -> BotDirectivesAnalysis:
        """
        Analyze both robots.txt and llms.txt files.
        
        Args:
            base_url: Base URL of the website
            
        Returns:
            Combined analysis of both files
        """
        logger.info(f"Starting bot directives analysis for {base_url}")
        
        # Analyze robots.txt
        robots_txt = self._analyze_robots_txt(base_url)
        
        # Analyze llms.txt
        llms_txt = self._analyze_llms_txt(base_url)
        
        # Generate combined insights
        combined_recommendations = self._generate_combined_recommendations(robots_txt, llms_txt)
        combined_issues = self._generate_combined_issues(robots_txt, llms_txt)
        compatibility_score = self._calculate_compatibility_score(robots_txt, llms_txt)
        
        return BotDirectivesAnalysis(
            robots_txt=robots_txt,
            llms_txt=llms_txt,
            combined_recommendations=combined_recommendations,
            combined_issues=combined_issues,
            compatibility_score=compatibility_score
        )
    
    def _analyze_robots_txt(self, base_url: str) -> RobotsTxtAnalysis:
        """Analyze robots.txt file."""
        robots_url = urljoin(base_url, "/robots.txt")
        content = self._fetch_file(robots_url)
        
        if not content:
            return RobotsTxtAnalysis(
                is_present=False,
                url=None,
                content=None,
                format_valid=False,
                sections={},
                user_agents=[],
                disallowed_paths=[],
                allowed_paths=[],
                sitemaps=[],
                crawl_delay=None,
                recommendations=["Create a robots.txt file to guide web crawlers"],
                issues=["No robots.txt file found"]
            )
        
        # Parse robots.txt content
        sections = {}
        user_agents = []
        disallowed_paths = []
        allowed_paths = []
        sitemaps = []
        crawl_delay = None
        
        current_section = None
        
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if ':' in line:
                key, value = [x.strip() for x in line.split(':', 1)]
                key = key.lower()
                
                if key == 'user-agent':
                    current_section = value
                    user_agents.append(value)
                    if value not in sections:
                        sections[value] = []
                elif key == 'disallow' and current_section:
                    disallowed_paths.append(value)
                    sections[current_section].append(f"Disallow: {value}")
                elif key == 'allow' and current_section:
                    allowed_paths.append(value)
                    sections[current_section].append(f"Allow: {value}")
                elif key == 'sitemap':
                    sitemaps.append(value)
                elif key == 'crawl-delay' and current_section:
                    try:
                        crawl_delay = int(value)
                    except ValueError:
                        pass
        
        # Generate recommendations and issues
        recommendations = []
        issues = []
        
        if not user_agents:
            issues.append("No User-agent directives found")
            recommendations.append("Add User-agent directives to specify crawler permissions")
        
        if not sitemaps:
            recommendations.append("Consider adding a Sitemap directive to help crawlers")
        
        if len(disallowed_paths) > 20:
            issues.append("Large number of Disallow directives may indicate overly restrictive crawling")
        
        return RobotsTxtAnalysis(
            is_present=True,
            url=robots_url,
            content=content,
            format_valid=bool(sections),
            sections=sections,
            user_agents=user_agents,
            disallowed_paths=disallowed_paths,
            allowed_paths=allowed_paths,
            sitemaps=sitemaps,
            crawl_delay=crawl_delay,
            recommendations=recommendations,
            issues=issues
        )
    
    def _analyze_llms_txt(self, base_url: str) -> LLMsTxtAnalysis:
        """Analyze llms.txt file."""
        llms_url = urljoin(base_url, "/llms.txt")
        content = self._fetch_file(llms_url)
        
        if not content:
            return LLMsTxtAnalysis(
                is_present=False,
                url=None,
                content=None,
                format_valid=False,
                sections={},
                quality_score=0.0,
                recommendations=["Create an llms.txt file to guide AI crawlers"],
                issues=["No llms.txt file found"],
                benefits=[]
            )
        
        # Parse llms.txt content (Markdown format)
        sections = {}
        current_section = None
        current_content = []
        
        for line in content.splitlines():
            if line.startswith('#'):
                if current_section and current_content:
                    sections[current_section] = current_content
                current_section = line.lstrip('#').strip()
                current_content = []
            elif line.strip() and current_section:
                current_content.append(line.strip())
        
        if current_section and current_content:
            sections[current_section] = current_content
        
        # Calculate quality score
        quality_score = self._calculate_llms_quality_score(sections)
        
        # Generate recommendations and benefits
        recommendations = []
        issues = []
        benefits = []
        
        if 'Content Guidelines' not in sections:
            issues.append("Missing Content Guidelines section")
            recommendations.append("Add a Content Guidelines section to help LLMs understand content structure")
        
        if 'Preferred Access' not in sections:
            issues.append("Missing Preferred Access section")
            recommendations.append("Add a Preferred Access section to guide LLMs to high-quality content")
        
        if sections:
            benefits.append("Provides explicit guidance for LLM crawlers")
            if 'Content Guidelines' in sections:
                benefits.append("Clear content structure documentation")
            if 'Preferred Access' in sections:
                benefits.append("Optimized content discovery paths")
        
        return LLMsTxtAnalysis(
            is_present=True,
            url=llms_url,
            content=content,
            format_valid=bool(sections),
            sections=sections,
            quality_score=quality_score,
            recommendations=recommendations,
            issues=issues,
            benefits=benefits
        )
    
    def _fetch_file(self, url: str) -> Optional[str]:
        """Fetch file content."""
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200:
                return response.text
            logger.info(f"File not found at {url} (status {response.status_code})")
            return None
        except requests.RequestException as e:
            logger.warning(f"Error fetching {url}: {e}")
            return None
    
    def _calculate_llms_quality_score(self, sections: Dict[str, List[str]]) -> float:
        """Calculate quality score for llms.txt content."""
        score = 0.0
        max_score = 100.0
        
        # Core sections
        core_sections = {
            'Content Guidelines': 25,
            'Preferred Access': 25,
            'API Integration': 15,
            'Updates': 10,
            'Contact': 10,
            'License': 15
        }
        
        # Score based on present sections
        for section, points in core_sections.items():
            if section in sections:
                score += points
        
        # Bonus points for section content quality
        for section, content in sections.items():
            if len(content) >= 5:  # Good detail
                score += 5
            elif len(content) >= 3:  # Moderate detail
                score += 3
        
        # Cap at 100
        return min(score, max_score)
    
    def _generate_combined_recommendations(
        self, robots_txt: RobotsTxtAnalysis, llms_txt: LLMsTxtAnalysis
    ) -> List[str]:
        """Generate combined recommendations."""
        recommendations = []
        
        # Check for basic presence
        if not robots_txt.is_present and not llms_txt.is_present:
            recommendations.append("Create both robots.txt and llms.txt files to properly guide all types of crawlers")
        elif not robots_txt.is_present:
            recommendations.append("Add robots.txt file to complement existing llms.txt")
        elif not llms_txt.is_present:
            recommendations.append("Add llms.txt file to complement existing robots.txt")
        
        # Check for compatibility
        if robots_txt.is_present and llms_txt.is_present:
            # Check if robots.txt blocks paths that llms.txt recommends
            if llms_txt.sections.get('Preferred Access'):
                for path in llms_txt.sections['Preferred Access']:
                    if any(path.startswith(disallow) for disallow in robots_txt.disallowed_paths):
                        recommendations.append(
                            f"Conflict detected: {path} is recommended in llms.txt but blocked in robots.txt"
                        )
        
        # Add specific recommendations
        recommendations.extend(robots_txt.recommendations)
        recommendations.extend(llms_txt.recommendations)
        
        return list(set(recommendations))  # Remove duplicates
    
    def _generate_combined_issues(
        self, robots_txt: RobotsTxtAnalysis, llms_txt: LLMsTxtAnalysis
    ) -> List[str]:
        """Generate combined issues list."""
        issues = []
        
        # Add file-specific issues
        issues.extend(robots_txt.issues)
        issues.extend(llms_txt.issues)
        
        # Check for conflicts
        if robots_txt.is_present and llms_txt.is_present:
            if robots_txt.crawl_delay and robots_txt.crawl_delay > 5:
                issues.append("High crawl delay may impact LLM content discovery")
        
        return list(set(issues))  # Remove duplicates
    
    def _calculate_compatibility_score(
        self, robots_txt: RobotsTxtAnalysis, llms_txt: LLMsTxtAnalysis
    ) -> float:
        """Calculate compatibility score between robots.txt and llms.txt."""
        score = 0.0
        max_score = 100.0
        
        # If neither file exists, score is 0
        if not robots_txt.is_present and not llms_txt.is_present:
            return score
        
        # Base score for having the files
        if robots_txt.is_present:
            score += 40
        if llms_txt.is_present:
            score += 40
        
        # Check for conflicts
        if robots_txt.is_present and llms_txt.is_present:
            conflicts = 0
            if llms_txt.sections.get('Preferred Access'):
                for path in llms_txt.sections['Preferred Access']:
                    if any(path.startswith(disallow) for disallow in robots_txt.disallowed_paths):
                        conflicts += 1
            
            # Deduct points for conflicts
            score -= (conflicts * 10)
            
            # Bonus for good compatibility
            if conflicts == 0:
                score += 20
        
        return max(0.0, min(score, max_score))  # Keep between 0 and 100
