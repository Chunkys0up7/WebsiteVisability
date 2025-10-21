"""
LLMs.txt File Analyzer

Analyzes llms.txt files according to the 2025 standard for guiding
LLMs to quality content on websites.
"""

import logging
import requests
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import re

logger = logging.getLogger(__name__)


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


class LLMsTxtAnalyzer:
    """
    Analyzes llms.txt files for LLM optimization.
    
    The llms.txt file is a new standard (2024-2025) for guiding LLMs
    to quality content, different from robots.txt which focuses on exclusion.
    """
    
    def __init__(self, timeout: int = 10, user_agent: str = "Mozilla/5.0 (compatible; WebScraperLLMAnalyzer/1.0)"):
        """Initialize the llms.txt analyzer."""
        self.timeout = timeout
        self.user_agent = user_agent
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})
    
    def analyze(self, base_url: str) -> LLMsTxtAnalysis:
        """
        Analyze llms.txt file for a given website.
        
        Args:
            base_url: Base URL of the website
            
        Returns:
            LLMsTxtAnalysis with detailed results
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Analyzing llms.txt for {base_url}")
        
        # Check for llms.txt file
        llms_url = urljoin(base_url, "/llms.txt")
        content = self._fetch_llms_txt(llms_url)
        
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
        
        # Parse and analyze the content
        sections = self._parse_llms_txt(content)
        format_valid = self._validate_format(content)
        quality_score = self._calculate_quality_score(sections, content)
        recommendations = self._generate_recommendations(sections, content)
        issues = self._identify_issues(sections, content)
        benefits = self._identify_benefits(sections)
        
        self.logger.info(f"llms.txt analysis complete. Quality score: {quality_score:.1f}")
        
        return LLMsTxtAnalysis(
            is_present=True,
            url=llms_url,
            content=content,
            format_valid=format_valid,
            sections=sections,
            quality_score=quality_score,
            recommendations=recommendations,
            issues=issues,
            benefits=benefits
        )
    
    def _fetch_llms_txt(self, llms_url: str) -> Optional[str]:
        """Fetch llms.txt content."""
        try:
            response = self.session.get(llms_url, timeout=self.timeout)
            response.raise_for_status()
            
            # Check if content looks like llms.txt (Markdown format)
            content = response.text
            if self._looks_like_llms_txt(content):
                return content
            else:
                self.logger.warning(f"Content at {llms_url} doesn't appear to be llms.txt format")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.info(f"Could not fetch llms.txt from {llms_url}: {e}")
            return None
    
    def _looks_like_llms_txt(self, content: str) -> bool:
        """Check if content looks like a valid llms.txt file."""
        # llms.txt should be in Markdown format
        # Look for common llms.txt patterns
        patterns = [
            r'#\s+.*LLM',  # Header with LLM
            r'##\s+(About|Key Pages|Documentation)',  # Common sections
            r'-\s+/',  # List items with paths
            r'\[.*\]\(.*\)',  # Markdown links
        ]
        
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        # If it's very short and doesn't look like HTML, assume it's llms.txt
        if len(content) < 1000 and not content.strip().startswith('<'):
            return True
        
        return False
    
    def _parse_llms_txt(self, content: str) -> Dict[str, List[str]]:
        """Parse llms.txt content into sections."""
        sections = {
            'about': [],
            'key_pages': [],
            'documentation': [],
            'other': []
        }
        
        current_section = 'other'
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            if line.startswith('##'):
                section_name = line[2:].strip().lower()
                if 'about' in section_name:
                    current_section = 'about'
                elif 'key' in section_name and 'page' in section_name:
                    current_section = 'key_pages'
                elif 'documentation' in section_name or 'docs' in section_name:
                    current_section = 'documentation'
                else:
                    current_section = 'other'
            elif line.startswith('#'):
                # Main header
                current_section = 'about'
            elif line.startswith('-') or line.startswith('*'):
                # List item
                item = line[1:].strip()
                if item:
                    sections[current_section].append(item)
            elif line and not line.startswith('#'):
                # Regular content
                sections[current_section].append(line)
        
        return sections
    
    def _validate_format(self, content: str) -> bool:
        """Validate llms.txt format."""
        # Basic validation checks
        checks = [
            len(content) > 50,  # Not too short
            len(content) < 10000,  # Not too long
            '#' in content,  # Has headers
            not content.strip().startswith('<'),  # Not HTML
        ]
        
        return all(checks)
    
    def _calculate_quality_score(self, sections: Dict[str, List[str]], content: str) -> float:
        """Calculate quality score for llms.txt file."""
        score = 0.0
        
        # Base score for having the file
        score += 20.0
        
        # Section completeness
        if sections['about']:
            score += 20.0
        if sections['key_pages']:
            score += 25.0
        if sections['documentation']:
            score += 15.0
        
        # Content quality indicators
        if len(content) > 200:
            score += 10.0
        if len(content) > 500:
            score += 5.0
        
        # Path validation
        valid_paths = 0
        total_paths = 0
        for section_items in sections.values():
            for item in section_items:
                if '/' in item and not item.startswith('http'):
                    total_paths += 1
                    if self._is_valid_path(item):
                        valid_paths += 1
        
        if total_paths > 0:
            path_score = (valid_paths / total_paths) * 10.0
            score += path_score
        
        return min(score, 100.0)
    
    def _is_valid_path(self, path: str) -> bool:
        """Check if a path looks valid."""
        # Extract path from markdown link if present
        if '[' in path and ']' in path:
            # Extract the URL part
            match = re.search(r'\[.*?\]\((.*?)\)', path)
            if match:
                path = match.group(1)
        
        # Basic path validation
        if path.startswith('/') or path.startswith('http'):
            return True
        
        return False
    
    def _generate_recommendations(self, sections: Dict[str, List[str]], content: str) -> List[str]:
        """Generate recommendations for improving llms.txt."""
        recommendations = []
        
        if not sections['about']:
            recommendations.append("Add an 'About' section describing your site and content")
        
        if not sections['key_pages']:
            recommendations.append("Add a 'Key Pages' section listing important URLs")
        
        if not sections['documentation']:
            recommendations.append("Consider adding a 'Documentation' section for technical content")
        
        if len(content) < 200:
            recommendations.append("Expand content to provide more guidance for AI crawlers")
        
        # Check for common improvements
        if 'robots.txt' in content.lower():
            recommendations.append("Note: llms.txt is different from robots.txt - focus on guidance, not exclusion")
        
        if len(sections['key_pages']) < 3:
            recommendations.append("Add more key pages to help AI crawlers find important content")
        
        return recommendations
    
    def _identify_issues(self, sections: Dict[str, List[str]], content: str) -> List[str]:
        """Identify issues with the llms.txt file."""
        issues = []
        
        if len(content) < 100:
            issues.append("Content is too short to be useful")
        
        if not any(sections.values()):
            issues.append("No clear sections or structure")
        
        # Check for broken links or invalid paths
        invalid_paths = 0
        for section_items in sections.values():
            for item in section_items:
                if '/' in item and not self._is_valid_path(item):
                    invalid_paths += 1
        
        if invalid_paths > 0:
            issues.append(f"Found {invalid_paths} potentially invalid paths")
        
        return issues
    
    def _identify_benefits(self, sections: Dict[str, List[str]]) -> List[str]:
        """Identify benefits of the llms.txt file."""
        benefits = []
        
        if sections['about']:
            benefits.append("Provides context about site purpose and content")
        
        if sections['key_pages']:
            benefits.append("Directs AI crawlers to most important pages")
        
        if sections['documentation']:
            benefits.append("Helps AI crawlers find technical documentation")
        
        if len(sections['key_pages']) > 5:
            benefits.append("Comprehensive page guidance for AI crawlers")
        
        benefits.append("Improves brand representation in AI answers")
        benefits.append("Reduces confusion from cluttered navigation")
        
        return benefits
    
    def close(self):
        """Close the requests session."""
        self.session.close()
        self.logger.info("Requests session closed for LLMsTxtAnalyzer.")
