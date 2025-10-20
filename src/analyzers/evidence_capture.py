"""
Evidence Capture Module

Captures and stores evidence of analysis results for different crawler types,
including screenshots, content samples, and technical details.
"""

import logging
import json
import base64
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class AnalysisEvidence:
    """Evidence captured during analysis"""
    timestamp: str
    url: str
    crawler_type: str
    content_sample: str
    technical_details: Dict[str, Any]
    accessibility_issues: List[str]
    recommendations: List[str]
    evidence_hash: str


@dataclass
class EvidenceReport:
    """Complete evidence report"""
    analysis_id: str
    timestamp: str
    url: str
    crawler_comparisons: Dict[str, AnalysisEvidence]
    summary: Dict[str, Any]
    recommendations: List[str]


class EvidenceCapture:
    """
    Captures and manages evidence from web crawler analysis.
    
    Stores detailed evidence of how different crawlers access content,
    including content samples, technical details, and accessibility issues.
    """
    
    def __init__(self):
        """Initialize the evidence capture system."""
        self.logger = logging.getLogger(__name__)
        self.evidence_storage: Dict[str, EvidenceReport] = {}
    
    def capture_analysis_evidence(self, url: str, crawler_type: str, 
                                analysis_result: Any, 
                                technical_details: Dict[str, Any]) -> AnalysisEvidence:
        """
        Capture evidence from a single crawler analysis.
        
        Args:
            url: Website URL analyzed
            crawler_type: Type of crawler used
            analysis_result: Results from crawler analysis
            technical_details: Additional technical information
            
        Returns:
            AnalysisEvidence object with captured data
        """
        self.logger.info(f"Capturing evidence for {crawler_type} analysis of {url}")
        
        # Extract content sample
        content_sample = self._extract_content_sample(analysis_result)
        
        # Extract accessibility issues
        accessibility_issues = self._extract_accessibility_issues(analysis_result)
        
        # Extract recommendations
        recommendations = self._extract_recommendations(analysis_result)
        
        # Generate evidence hash
        evidence_data = {
            'url': url,
            'crawler_type': crawler_type,
            'content_sample': content_sample,
            'technical_details': technical_details,
            'accessibility_issues': accessibility_issues
        }
        evidence_hash = self._generate_hash(evidence_data)
        
        evidence = AnalysisEvidence(
            timestamp=datetime.now().isoformat(),
            url=url,
            crawler_type=crawler_type,
            content_sample=content_sample,
            technical_details=technical_details,
            accessibility_issues=accessibility_issues,
            recommendations=recommendations,
            evidence_hash=evidence_hash
        )
        
        self.logger.info(f"Evidence captured for {crawler_type}. Hash: {evidence_hash[:8]}...")
        return evidence
    
    def create_evidence_report(self, url: str, crawler_evidences: Dict[str, AnalysisEvidence]) -> EvidenceReport:
        """
        Create a comprehensive evidence report comparing multiple crawlers.
        
        Args:
            url: Website URL analyzed
            crawler_evidences: Dictionary of crawler type -> evidence
            
        Returns:
            EvidenceReport with comprehensive analysis
        """
        self.logger.info(f"Creating evidence report for {url} with {len(crawler_evidences)} crawlers")
        
        analysis_id = self._generate_analysis_id(url)
        
        # Generate summary
        summary = self._generate_summary(crawler_evidences)
        
        # Generate recommendations
        recommendations = self._generate_report_recommendations(crawler_evidences)
        
        report = EvidenceReport(
            analysis_id=analysis_id,
            timestamp=datetime.now().isoformat(),
            url=url,
            crawler_comparisons=crawler_evidences,
            summary=summary,
            recommendations=recommendations
        )
        
        # Store the report
        self.evidence_storage[analysis_id] = report
        
        self.logger.info(f"Evidence report created: {analysis_id}")
        return report
    
    def get_evidence_report(self, analysis_id: str) -> Optional[EvidenceReport]:
        """Retrieve a stored evidence report."""
        return self.evidence_storage.get(analysis_id)
    
    def export_evidence_report(self, analysis_id: str, format: str = 'json') -> str:
        """
        Export evidence report in specified format.
        
        Args:
            analysis_id: ID of the report to export
            format: Export format ('json', 'html', 'markdown')
            
        Returns:
            Exported report as string
        """
        report = self.get_evidence_report(analysis_id)
        if not report:
            raise ValueError(f"Report {analysis_id} not found")
        
        if format == 'json':
            return json.dumps(asdict(report), indent=2)
        elif format == 'html':
            return self._export_html_report(report)
        elif format == 'markdown':
            return self._export_markdown_report(report)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _extract_content_sample(self, analysis_result: Any) -> str:
        """Extract a representative content sample."""
        sample = ""
        
        # Try to get text content
        if hasattr(analysis_result, 'content_analysis') and analysis_result.content_analysis:
            if hasattr(analysis_result.content_analysis, 'text_content'):
                text = analysis_result.content_analysis.text_content
                sample = text[:1000] + "..." if len(text) > 1000 else text
        
        # Fallback to URL if no content
        if not sample and hasattr(analysis_result, 'url'):
            sample = f"Content from: {analysis_result.url}"
        
        return sample or "No content sample available"
    
    def _extract_accessibility_issues(self, analysis_result: Any) -> List[str]:
        """Extract accessibility issues from analysis result."""
        issues = []
        
        # Extract from crawler analysis result
        if hasattr(analysis_result, 'content_inaccessible'):
            inaccessible = analysis_result.content_inaccessible
            for content_type, details in inaccessible.items():
                if isinstance(details, dict) and details.get('available') is False:
                    explanation = details.get('explanation', 'Content not accessible')
                    impact = details.get('impact', 'Unknown impact')
                    issues.append(f"{content_type}: {explanation} ({impact})")
        
        # Extract from general analysis
        if hasattr(analysis_result, 'accessibility_score'):
            score = analysis_result.accessibility_score
            if score < 50:
                issues.append(f"Low accessibility score: {score:.1f}/100")
            elif score < 70:
                issues.append(f"Moderate accessibility issues: {score:.1f}/100")
        
        return issues
    
    def _extract_recommendations(self, analysis_result: Any) -> List[str]:
        """Extract recommendations from analysis result."""
        recommendations = []
        
        if hasattr(analysis_result, 'recommendations'):
            recommendations.extend(analysis_result.recommendations)
        
        return recommendations
    
    def _generate_hash(self, data: Dict[str, Any]) -> str:
        """Generate a hash for the evidence data."""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _generate_analysis_id(self, url: str) -> str:
        """Generate a unique analysis ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        return f"analysis_{timestamp}_{url_hash}"
    
    def _generate_summary(self, crawler_evidences: Dict[str, AnalysisEvidence]) -> Dict[str, Any]:
        """Generate summary statistics from crawler evidences."""
        summary = {
            'total_crawlers': len(crawler_evidences),
            'crawler_types': list(crawler_evidences.keys()),
            'total_issues': 0,
            'critical_issues': 0,
            'high_issues': 0,
            'medium_issues': 0,
            'low_issues': 0
        }
        
        for evidence in crawler_evidences.values():
            summary['total_issues'] += len(evidence.accessibility_issues)
            
            for issue in evidence.accessibility_issues:
                if 'CRITICAL' in issue.upper():
                    summary['critical_issues'] += 1
                elif 'HIGH' in issue.upper():
                    summary['high_issues'] += 1
                elif 'MEDIUM' in issue.upper():
                    summary['medium_issues'] += 1
                else:
                    summary['low_issues'] += 1
        
        return summary
    
    def _generate_report_recommendations(self, crawler_evidences: Dict[str, AnalysisEvidence]) -> List[str]:
        """Generate comprehensive recommendations from all crawler evidences."""
        all_recommendations = []
        
        for evidence in crawler_evidences.values():
            all_recommendations.extend(evidence.recommendations)
        
        # Remove duplicates while preserving order
        unique_recommendations = []
        seen = set()
        for rec in all_recommendations:
            if rec not in seen:
                unique_recommendations.append(rec)
                seen.add(rec)
        
        return unique_recommendations
    
    def _export_html_report(self, report: EvidenceReport) -> str:
        """Export report as HTML."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Evidence Report - {report.url}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .crawler {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .issue {{ color: #d32f2f; margin: 5px 0; }}
                .recommendation {{ color: #1976d2; margin: 5px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Evidence Report</h1>
                <p><strong>URL:</strong> {report.url}</p>
                <p><strong>Analysis ID:</strong> {report.analysis_id}</p>
                <p><strong>Timestamp:</strong> {report.timestamp}</p>
            </div>
            
            <div class="section">
                <h2>Summary</h2>
                <p>Total Crawlers: {report.summary['total_crawlers']}</p>
                <p>Total Issues: {report.summary['total_issues']}</p>
                <p>Critical Issues: {report.summary['critical_issues']}</p>
                <p>High Issues: {report.summary['high_issues']}</p>
            </div>
            
            <div class="section">
                <h2>Crawler Analysis</h2>
        """
        
        for crawler_type, evidence in report.crawler_comparisons.items():
            html += f"""
                <div class="crawler">
                    <h3>{crawler_type}</h3>
                    <p><strong>Evidence Hash:</strong> {evidence.evidence_hash[:16]}...</p>
                    
                    <h4>Accessibility Issues:</h4>
                    <ul>
            """
            for issue in evidence.accessibility_issues:
                html += f'<li class="issue">{issue}</li>'
            
            html += """
                    </ul>
                    
                    <h4>Recommendations:</h4>
                    <ul>
            """
            for rec in evidence.recommendations:
                html += f'<li class="recommendation">{rec}</li>'
            
            html += """
                    </ul>
                </div>
            """
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _export_markdown_report(self, report: EvidenceReport) -> str:
        """Export report as Markdown."""
        md = f"""# Evidence Report

**URL:** {report.url}  
**Analysis ID:** {report.analysis_id}  
**Timestamp:** {report.timestamp}

## Summary

- **Total Crawlers:** {report.summary['total_crawlers']}
- **Total Issues:** {report.summary['total_issues']}
- **Critical Issues:** {report.summary['critical_issues']}
- **High Issues:** {report.summary['high_issues']}

## Crawler Analysis

"""
        
        for crawler_type, evidence in report.crawler_comparisons.items():
            md += f"""### {crawler_type}

**Evidence Hash:** `{evidence.evidence_hash[:16]}...`

#### Accessibility Issues
"""
            for issue in evidence.accessibility_issues:
                md += f"- ❌ {issue}\n"
            
            md += "\n#### Recommendations\n"
            for rec in evidence.recommendations:
                md += f"- 💡 {rec}\n"
            
            md += "\n"
        
        return md
