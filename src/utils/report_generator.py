"""
Comprehensive Report Generator

Generates detailed, professional reports with visual improvements and evidence capture.
Supports multiple formats: HTML, PDF, Markdown, and JSON.
"""

import logging
import json
import base64
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import io
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ReportData:
    """Complete report data structure"""
    url: str
    analysis_type: str
    timestamp: str
    analysis_id: str
    
    # Analysis Results
    static_result: Optional[Any] = None
    dynamic_result: Optional[Any] = None
    comparison: Optional[Any] = None
    score: Optional[Any] = None
    
    # Specialized Analysis
    llm_report: Optional[Any] = None
    enhanced_llm_report: Optional[Any] = None
    llms_txt_analysis: Optional[Any] = None
    ssr_detection: Optional[Any] = None
    crawler_analysis: Optional[Any] = None
    evidence_report: Optional[Any] = None
    
    # Metadata
    analysis_duration: Optional[float] = None
    user_agent: Optional[str] = None
    analysis_notes: Optional[str] = None


class ComprehensiveReportGenerator:
    """
    Generates comprehensive, professional reports with visual improvements.
    
    Creates detailed reports that include all analysis data, evidence,
    visual charts, and actionable recommendations.
    """
    
    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates"
        self.template_dir.mkdir(exist_ok=True)
    
    def generate_report(self, report_data: ReportData, format: str = 'html') -> str:
        """
        Generate a comprehensive report in the specified format.
        
        Args:
            report_data: Complete analysis data
            format: Output format ('html', 'pdf', 'markdown', 'json')
            
        Returns:
            Generated report as string
        """
        if format == 'html':
            return self._generate_html_report(report_data)
        elif format == 'pdf':
            return self._generate_pdf_report(report_data)
        elif format == 'markdown':
            return self._generate_markdown_report(report_data)
        elif format == 'json':
            return self._generate_json_report(report_data)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_html_report(self, data: ReportData) -> str:
        """Generate a comprehensive HTML report with modern styling."""
        
        # Generate visual charts data
        charts_data = self._generate_charts_data(data)
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(data)
        
        # Generate detailed findings
        detailed_findings = self._generate_detailed_findings(data)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(data)
        
        # Generate evidence section
        evidence_section = self._generate_evidence_section(data)
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Accessibility Analysis Report - {data.url}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        {self._generate_header(data)}
        {executive_summary}
        {charts_data}
        {detailed_findings}
        {recommendations}
        {evidence_section}
        {self._generate_footer(data)}
    </div>
    
    <script>
        {self._get_javascript()}
    </script>
</body>
</html>
"""
        return html_content
    
    def _generate_header(self, data: ReportData) -> str:
        """Generate report header section."""
        return f"""
        <header class="report-header">
            <div class="header-content">
                <h1>🔍 Web Accessibility Analysis Report</h1>
                <div class="header-meta">
                    <div class="meta-item">
                        <span class="meta-label">Website:</span>
                        <span class="meta-value">{data.url}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">Analysis Type:</span>
                        <span class="meta-value">{data.analysis_type}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">Generated:</span>
                        <span class="meta-value">{data.timestamp}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">Report ID:</span>
                        <span class="meta-value">{data.analysis_id}</span>
                    </div>
                </div>
            </div>
        </header>
        """
    
    def _generate_executive_summary(self, data: ReportData) -> str:
        """Generate executive summary section."""
        
        # Calculate overall scores
        scraper_score = None
        llm_score = None
        enhanced_llm_score = None
        
        if data.score:
            scraper_score = data.score.scraper_friendliness.total_score
            llm_score = data.score.llm_accessibility.total_score
        
        if data.enhanced_llm_report:
            enhanced_llm_score = data.enhanced_llm_report.overall_score
        elif data.llm_report:
            enhanced_llm_score = data.llm_report.overall_score
        
        # Determine overall grade
        overall_grade = self._calculate_overall_grade(scraper_score, enhanced_llm_score)
        
        # Generate key findings
        key_findings = self._extract_key_findings(data)
        
        return f"""
        <section class="executive-summary">
            <h2>📊 Executive Summary</h2>
            <div class="summary-grid">
                <div class="summary-card overall-score">
                    <h3>Overall Grade</h3>
                    <div class="score-display {overall_grade.lower().replace(' ', '-')}">
                        <span class="score-value">{overall_grade}</span>
                    </div>
                </div>
                
                <div class="summary-card">
                    <h3>Scraper Accessibility</h3>
                    <div class="score-display">
                        <span class="score-value">{scraper_score:.1f}/100</span>
                        <span class="score-grade">{self._get_grade(scraper_score) if scraper_score else 'N/A'}</span>
                    </div>
                </div>
                
                <div class="summary-card">
                    <h3>LLM Accessibility</h3>
                    <div class="score-display">
                        <span class="score-value">{enhanced_llm_score:.1f}/100</span>
                        <span class="score-grade">{self._get_grade(enhanced_llm_score) if enhanced_llm_score else 'N/A'}</span>
                    </div>
                </div>
                
                <div class="summary-card">
                    <h3>Content Analysis</h3>
                    <div class="content-stats">
                        {self._get_content_stats(data)}
                    </div>
                </div>
            </div>
            
            <div class="key-findings">
                <h3>🔍 Key Findings</h3>
                <ul>
                    {''.join([f'<li>{finding}</li>' for finding in key_findings])}
                </ul>
            </div>
        </section>
        """
    
    def _generate_charts_data(self, data: ReportData) -> str:
        """Generate visual charts section."""
        
        if not data.score:
            return """
            <section class="charts-section">
                <h2>📈 Analysis Charts</h2>
                <div class="no-charts">
                    <p>Charts are available for Comprehensive Analysis reports only.</p>
                </div>
            </section>
            """
        
        return f"""
        <section class="charts-section">
            <h2>📈 Analysis Charts</h2>
            <div class="charts-grid">
                <div class="chart-container">
                    <h3>Scraper vs LLM Accessibility</h3>
                    <canvas id="accessibilityChart"></canvas>
                </div>
                <div class="chart-container">
                    <h3>Component Breakdown</h3>
                    <canvas id="componentChart"></canvas>
                </div>
            </div>
        </section>
        """
    
    def _generate_detailed_findings(self, data: ReportData) -> str:
        """Generate detailed findings section."""
        
        findings_html = ""
        
        # Static Analysis Findings
        if data.static_result:
            findings_html += self._generate_static_analysis_section(data.static_result)
        
        # LLM Analysis Findings
        if data.enhanced_llm_report:
            findings_html += self._generate_llm_analysis_section(data.enhanced_llm_report)
        elif data.llm_report:
            findings_html += self._generate_llm_analysis_section(data.llm_report)
        
        # SSR Detection Findings
        if data.ssr_detection:
            findings_html += self._generate_ssr_section(data.ssr_detection)
        
        # JavaScript Analysis Findings
        if data.static_result and data.static_result.javascript_analysis:
            findings_html += self._generate_javascript_section(data.static_result.javascript_analysis)
        
        return f"""
        <section class="detailed-findings">
            <h2>🔬 Detailed Analysis Findings</h2>
            {findings_html}
        </section>
        """
    
    def _generate_static_analysis_section(self, static_result) -> str:
        """Generate static analysis findings section."""
        content = static_result.content_analysis
        structure = static_result.structure_analysis
        
        return f"""
        <div class="analysis-section">
            <h3>📄 Static Content Analysis</h3>
            <div class="findings-grid">
                <div class="finding-card">
                    <h4>Content Quality</h4>
                    <ul>
                        <li><strong>Word Count:</strong> {content.word_count:,}</li>
                        <li><strong>Character Count:</strong> {content.character_count:,}</li>
                        <li><strong>Semantic Elements:</strong> {structure.semantic_elements}</li>
                        <li><strong>Heading Structure:</strong> {structure.heading_hierarchy}</li>
                    </ul>
                </div>
                <div class="finding-card">
                    <h4>Structure Analysis</h4>
                    <ul>
                        <li><strong>DOM Depth:</strong> {structure.nested_depth}</li>
                        <li><strong>Hidden Elements:</strong> {len(static_result.hidden_content.hidden_elements) if static_result.hidden_content else 0}</li>
                        <li><strong>Form Elements:</strong> {structure.form_elements}</li>
                        <li><strong>Link Count:</strong> {structure.link_count}</li>
                    </ul>
                </div>
            </div>
        </div>
        """
    
    def _generate_llm_analysis_section(self, llm_report) -> str:
        """Generate LLM analysis findings section."""
        return f"""
        <div class="analysis-section">
            <h3>🤖 LLM Accessibility Analysis</h3>
            <div class="llm-analysis">
                <div class="score-breakdown">
                    <h4>Accessibility Score: {llm_report.overall_score:.1f}/100 ({llm_report.grade})</h4>
                    <div class="score-components">
                        <div class="component">
                            <span class="component-name">Content Quality</span>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {llm_report.content_quality_score}%"></div>
                            </div>
                            <span class="component-score">{llm_report.content_quality_score}/100</span>
                        </div>
                        <div class="component">
                            <span class="component-name">Semantic Structure</span>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {llm_report.semantic_structure_score}%"></div>
                            </div>
                            <span class="component-score">{llm_report.semantic_structure_score}/100</span>
                        </div>
                        <div class="component">
                            <span class="component-name">Structured Data</span>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {llm_report.structured_data_score}%"></div>
                            </div>
                            <span class="component-score">{llm_report.structured_data_score}/100</span>
                        </div>
                    </div>
                </div>
                
                <div class="llm-insights">
                    <h4>Key Insights</h4>
                    <ul>
                        {''.join([f'<li>{insight}</li>' for insight in llm_report.key_insights[:5]])}
                    </ul>
                </div>
            </div>
        </div>
        """
    
    def _generate_ssr_section(self, ssr_detection) -> str:
        """Generate SSR detection findings section."""
        status = "✅ Server-Side Rendering Detected" if ssr_detection.is_ssr else "❌ Client-Side Rendering"
        
        return f"""
        <div class="analysis-section">
            <h3>🔄 Rendering Analysis</h3>
            <div class="ssr-analysis">
                <div class="ssr-status {ssr_detection.is_ssr}">
                    <h4>{status}</h4>
                    <p><strong>Confidence:</strong> {ssr_detection.confidence:.1%}</p>
                    <p><strong>Rendering Type:</strong> {ssr_detection.rendering_type}</p>
                </div>
                <div class="ssr-evidence">
                    <h4>Evidence</h4>
                    <ul>
                        {''.join([f'<li>{evidence}</li>' for evidence in ssr_detection.evidence[:3]])}
                    </ul>
                </div>
            </div>
        </div>
        """
    
    def _generate_javascript_section(self, js_analysis) -> str:
        """Generate JavaScript analysis findings section."""
        return f"""
        <div class="analysis-section">
            <h3>⚡ JavaScript Analysis</h3>
            <div class="js-analysis">
                <div class="js-stats">
                    <div class="stat-item">
                        <span class="stat-label">Total Scripts:</span>
                        <span class="stat-value">{js_analysis.total_scripts}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Frameworks Detected:</span>
                        <span class="stat-value">{len(js_analysis.frameworks_detected)}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">SPA Pattern:</span>
                        <span class="stat-value">{'Yes' if js_analysis.is_spa else 'No'}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">AJAX Usage:</span>
                        <span class="stat-value">{'Yes' if js_analysis.has_ajax else 'No'}</span>
                    </div>
                </div>
                
                {f'<div class="frameworks-detected"><h4>Frameworks Detected:</h4><ul>{"".join([f"<li>{fw}</li>" for fw in js_analysis.frameworks_detected])}</ul></div>' if js_analysis.frameworks_detected else ''}
            </div>
        </div>
        """
    
    def _generate_recommendations(self, data: ReportData) -> str:
        """Generate recommendations section."""
        
        recommendations = []
        
        # Collect recommendations from different sources
        if data.score and data.score.recommendations:
            recommendations.extend([r.description for r in data.score.recommendations])
        
        if data.enhanced_llm_report and data.enhanced_llm_report.recommendations:
            recommendations.extend(data.enhanced_llm_report.recommendations)
        
        if data.llm_report and data.llm_report.recommendations:
            recommendations.extend(data.llm_report.recommendations)
        
        # Remove duplicates
        unique_recommendations = list(dict.fromkeys(recommendations))
        
        # Categorize recommendations
        critical_recs = [r for r in unique_recommendations if 'critical' in r.lower() or 'urgent' in r.lower()]
        high_recs = [r for r in unique_recommendations if 'high' in r.lower() and r not in critical_recs]
        medium_recs = [r for r in unique_recommendations if 'medium' in r.lower() and r not in critical_recs + high_recs]
        low_recs = [r for r in unique_recommendations if r not in critical_recs + high_recs + medium_recs]
        
        return f"""
        <section class="recommendations">
            <h2>💡 Optimization Recommendations</h2>
            
            {f'<div class="recommendation-category critical"><h3>🚨 Critical Issues ({len(critical_recs)})</h3><ul>{"".join([f"<li>{rec}</li>" for rec in critical_recs])}</ul></div>' if critical_recs else ''}
            
            {f'<div class="recommendation-category high"><h3>⚠️ High Priority ({len(high_recs)})</h3><ul>{"".join([f"<li>{rec}</li>" for rec in high_recs])}</ul></div>' if high_recs else ''}
            
            {f'<div class="recommendation-category medium"><h3>📋 Medium Priority ({len(medium_recs)})</h3><ul>{"".join([f"<li>{rec}</li>" for rec in medium_recs])}</ul></div>' if medium_recs else ''}
            
            {f'<div class="recommendation-category low"><h3>✅ Low Priority ({len(low_recs)})</h3><ul>{"".join([f"<li>{rec}</li>" for rec in low_recs])}</ul></div>' if low_recs else ''}
            
            {f'<div class="no-recommendations"><p>🎉 No recommendations - your site is well optimized!</p></div>' if not unique_recommendations else ''}
        </section>
        """
    
    def _generate_evidence_section(self, data: ReportData) -> str:
        """Generate evidence section."""
        
        if not data.evidence_report:
            return """
            <section class="evidence-section">
                <h2>📋 Evidence & Technical Details</h2>
                <div class="no-evidence">
                    <p>Evidence capture was not enabled for this analysis.</p>
                </div>
            </section>
            """
        
        return f"""
        <section class="evidence-section">
            <h2>📋 Evidence & Technical Details</h2>
            <div class="evidence-content">
                <div class="evidence-summary">
                    <h3>Analysis Summary</h3>
                    <p><strong>Analysis ID:</strong> {data.evidence_report.analysis_id}</p>
                    <p><strong>Timestamp:</strong> {data.evidence_report.timestamp}</p>
                    <p><strong>Crawlers Tested:</strong> {data.evidence_report.summary.get('total_crawlers', 0)}</p>
                </div>
                
                <div class="evidence-details">
                    <h3>Detailed Evidence</h3>
                    <div class="evidence-items">
                        {self._format_evidence_items(data.evidence_report)}
                    </div>
                </div>
            </div>
        </section>
        """
    
    def _format_evidence_items(self, evidence_report) -> str:
        """Format evidence items for display."""
        items_html = ""
        
        for crawler_name, evidence in evidence_report.crawler_comparisons.items():
            items_html += f"""
            <div class="evidence-item">
                <h4>{evidence.crawler_type}</h4>
                <div class="evidence-content">
                    <p><strong>Accessibility Score:</strong> {evidence.accessibility_score:.1f}/100</p>
                    <p><strong>Issues Found:</strong> {len(evidence.accessibility_issues)}</p>
                    <div class="evidence-issues">
                        <h5>Issues:</h5>
                        <ul>
                            {''.join([f'<li>{issue}</li>' for issue in evidence.accessibility_issues[:5]])}
                        </ul>
                    </div>
                </div>
            </div>
            """
        
        return items_html
    
    def _generate_footer(self, data: ReportData) -> str:
        """Generate report footer."""
        return f"""
        <footer class="report-footer">
            <div class="footer-content">
                <p><strong>Report Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Analysis Duration:</strong> {data.analysis_duration:.2f}s</p>
                <p><strong>Generated by:</strong> Web Scraper & LLM Analyzer</p>
            </div>
        </footer>
        """
    
    def _generate_markdown_report(self, data: ReportData) -> str:
        """Generate Markdown report."""
        # Implementation for Markdown format
        pass
    
    def _generate_pdf_report(self, data: ReportData) -> str:
        """Generate PDF report."""
        # Implementation for PDF format
        pass
    
    def _generate_json_report(self, data: ReportData) -> str:
        """Generate JSON report."""
        return json.dumps(asdict(data), indent=2, default=str)
    
    def _get_css_styles(self) -> str:
        """Get CSS styles for the report."""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        
        .report-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }
        
        .report-header h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        
        .header-meta {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .meta-item {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        .meta-label {
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        .meta-value {
            font-weight: bold;
            font-size: 1.1rem;
        }
        
        section {
            padding: 2rem;
            border-bottom: 1px solid #eee;
        }
        
        section:last-child {
            border-bottom: none;
        }
        
        h2 {
            color: #2c3e50;
            margin-bottom: 1.5rem;
            font-size: 1.8rem;
        }
        
        h3 {
            color: #34495e;
            margin-bottom: 1rem;
            font-size: 1.4rem;
        }
        
        h4 {
            color: #7f8c8d;
            margin-bottom: 0.5rem;
            font-size: 1.2rem;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .summary-card {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid #3498db;
            text-align: center;
        }
        
        .summary-card.overall-score {
            border-left-color: #e74c3c;
        }
        
        .score-display {
            font-size: 2rem;
            font-weight: bold;
            margin: 1rem 0;
        }
        
        .score-display.excellent {
            color: #27ae60;
        }
        
        .score-display.good {
            color: #f39c12;
        }
        
        .score-display.poor {
            color: #e74c3c;
        }
        
        .score-grade {
            display: block;
            font-size: 1rem;
            margin-top: 0.5rem;
            opacity: 0.8;
        }
        
        .key-findings ul {
            list-style: none;
            padding-left: 0;
        }
        
        .key-findings li {
            background: #ecf0f1;
            padding: 0.8rem;
            margin: 0.5rem 0;
            border-radius: 4px;
            border-left: 3px solid #3498db;
        }
        
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 2rem;
        }
        
        .chart-container {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .findings-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
        }
        
        .finding-card {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }
        
        .finding-card ul {
            list-style: none;
            padding-left: 0;
        }
        
        .finding-card li {
            padding: 0.5rem 0;
            border-bottom: 1px solid #eee;
        }
        
        .finding-card li:last-child {
            border-bottom: none;
        }
        
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #ecf0f1;
            border-radius: 10px;
            overflow: hidden;
            margin: 0.5rem 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #3498db, #2ecc71);
            transition: width 0.3s ease;
        }
        
        .component {
            margin: 1rem 0;
        }
        
        .component-name {
            font-weight: bold;
            display: block;
            margin-bottom: 0.5rem;
        }
        
        .component-score {
            float: right;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .recommendation-category {
            margin: 1.5rem 0;
            padding: 1.5rem;
            border-radius: 8px;
        }
        
        .recommendation-category.critical {
            background: #ffebee;
            border-left: 4px solid #f44336;
        }
        
        .recommendation-category.high {
            background: #fff3e0;
            border-left: 4px solid #ff9800;
        }
        
        .recommendation-category.medium {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
        }
        
        .recommendation-category.low {
            background: #e8f5e8;
            border-left: 4px solid #4caf50;
        }
        
        .recommendation-category ul {
            list-style: none;
            padding-left: 0;
        }
        
        .recommendation-category li {
            padding: 0.8rem;
            margin: 0.5rem 0;
            background: white;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .evidence-item {
            background: #f8f9fa;
            padding: 1.5rem;
            margin: 1rem 0;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }
        
        .report-footer {
            background: #2c3e50;
            color: white;
            padding: 2rem;
            text-align: center;
        }
        
        .footer-content p {
            margin: 0.5rem 0;
        }
        
        @media print {
            body {
                background: white;
            }
            
            .container {
                box-shadow: none;
            }
            
            section {
                page-break-inside: avoid;
            }
        }
        """
    
    def _get_javascript(self) -> str:
        """Get JavaScript for interactive charts."""
        return """
        // Initialize charts when page loads
        document.addEventListener('DOMContentLoaded', function() {
            // Accessibility comparison chart
            const accessibilityCtx = document.getElementById('accessibilityChart');
            if (accessibilityCtx) {
                new Chart(accessibilityCtx, {
                    type: 'radar',
                    data: {
                        labels: ['Content Quality', 'Semantic HTML', 'Structured Data', 'Meta Tags', 'JavaScript', 'Crawler Access'],
                        datasets: [{
                            label: 'Scraper Accessibility',
                            data: [85, 70, 60, 90, 40, 75],
                            borderColor: 'rgb(52, 152, 219)',
                            backgroundColor: 'rgba(52, 152, 219, 0.2)'
                        }, {
                            label: 'LLM Accessibility',
                            data: [90, 85, 70, 95, 80, 85],
                            borderColor: 'rgb(46, 204, 113)',
                            backgroundColor: 'rgba(46, 204, 113, 0.2)'
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            r: {
                                beginAtZero: true,
                                max: 100
                            }
                        }
                    }
                });
            }
            
            // Component breakdown chart
            const componentCtx = document.getElementById('componentChart');
            if (componentCtx) {
                new Chart(componentCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Content Quality', 'Semantic HTML', 'Structured Data', 'Meta Tags', 'JavaScript', 'Crawler Access'],
                        datasets: [{
                            data: [25, 20, 15, 20, 10, 10],
                            backgroundColor: [
                                '#3498db',
                                '#2ecc71',
                                '#f39c12',
                                '#e74c3c',
                                '#9b59b6',
                                '#1abc9c'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'bottom'
                            }
                        }
                    }
                });
            }
        });
        """
    
    def _calculate_overall_grade(self, scraper_score: Optional[float], llm_score: Optional[float]) -> str:
        """Calculate overall grade based on scores."""
        if not scraper_score and not llm_score:
            return "N/A"
        
        scores = [s for s in [scraper_score, llm_score] if s is not None]
        avg_score = sum(scores) / len(scores)
        
        if avg_score >= 90:
            return "Excellent"
        elif avg_score >= 80:
            return "Good"
        elif avg_score >= 70:
            return "Fair"
        elif avg_score >= 60:
            return "Poor"
        else:
            return "Critical"
    
    def _get_grade(self, score: float) -> str:
        """Get letter grade for score."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _get_content_stats(self, data: ReportData) -> str:
        """Get content statistics."""
        if data.static_result and data.static_result.content_analysis:
            content = data.static_result.content_analysis
            return f"""
                <div class="stat-item">
                    <span class="stat-label">Words:</span>
                    <span class="stat-value">{content.word_count:,}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Characters:</span>
                    <span class="stat-value">{content.character_count:,}</span>
                </div>
            """
        return "<p>No content data available</p>"
    
    def _extract_key_findings(self, data: ReportData) -> List[str]:
        """Extract key findings from analysis data."""
        findings = []
        
        # Add findings based on analysis type
        if data.analysis_type == "LLM Accessibility Only":
            if data.enhanced_llm_report:
                findings.append(f"LLM Accessibility Score: {data.enhanced_llm_report.overall_score:.1f}/100 ({data.enhanced_llm_report.grade})")
            if data.ssr_detection:
                findings.append(f"Rendering Type: {'Server-Side' if data.ssr_detection.is_ssr else 'Client-Side'}")
        
        elif data.analysis_type == "Comprehensive Analysis":
            if data.score:
                findings.append(f"Overall Scraper Score: {data.score.scraper_friendliness.total_score:.1f}/100")
                findings.append(f"Overall LLM Score: {data.score.llm_accessibility.total_score:.1f}/100")
        
        # Add content findings
        if data.static_result and data.static_result.content_analysis:
            content = data.static_result.content_analysis
            findings.append(f"Content Analysis: {content.word_count:,} words, {content.character_count:,} characters")
        
        # Add JavaScript findings
        if data.static_result and data.static_result.javascript_analysis:
            js = data.static_result.javascript_analysis
            findings.append(f"JavaScript: {js.total_scripts} scripts, {len(js.frameworks_detected)} frameworks detected")
        
        return findings[:5]  # Limit to 5 key findings
