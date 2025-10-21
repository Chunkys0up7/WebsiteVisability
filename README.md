# 🔍 Web Scraper & LLM Analyzer

A comprehensive web application that analyzes websites for their accessibility to web scrapers and Large Language Models (LLMs). Built with Streamlit, this tool provides detailed insights into how well your website's content can be extracted and understood by automated systems.

## 🚀 Features

### Core Analysis Capabilities
- **Static Content Analysis**: Analyzes HTML structure, content, and metadata
- **Dynamic Content Analysis**: Uses headless browsers to detect JavaScript-rendered content
- **LLM Accessibility Analysis**: Evaluates how well LLMs can understand your content
- **Enhanced LLM Analysis**: Detailed analysis of different LLM crawler capabilities
- **Server-Side Rendering (SSR) Detection**: Identifies if your site uses SSR
- **Web Crawler Testing**: Simulates different crawler behaviors (Googlebot, LLM crawlers, etc.)
- **LLMs.txt Analysis**: Analyzes the new llms.txt standard for AI crawler guidance

### Analysis Types
1. **Comprehensive Analysis**: Full analysis with all features
2. **LLM Accessibility Only**: Focused on LLM-specific analysis
3. **Web Crawler Testing**: Tests different crawler behaviors
4. **SSR Detection Only**: Identifies server-side rendering patterns

### Export Capabilities
- **Summary Reports**: Quick overview in text format
- **Detailed Data Export**: Complete analysis data in JSON format
- **Evidence Reports**: Detailed crawler comparison data

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd web_scraper_llm_analyzer
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**
   - **Windows:**
     ```bash
     .venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source .venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

5. **Run the application**
   ```bash
   streamlit run app/main.py
   ```

6. **Access the application**
   Open your browser and navigate to `http://localhost:8501`

## 📁 Project Structure

```
web_scraper_llm_analyzer/
├── app/
│   ├── main.py                 # Main Streamlit application
│   ├── pages/                  # Additional Streamlit pages (future)
│   └── components/             # Custom Streamlit components (future)
├── src/
│   ├── analyzers/              # Analysis engine modules
│   │   ├── static_analyzer.py
│   │   ├── dynamic_analyzer.py
│   │   ├── llm_accessibility_analyzer.py
│   │   ├── enhanced_llm_analyzer.py
│   │   ├── web_crawler_analyzer.py
│   │   ├── ssr_detector.py
│   │   ├── llms_txt_analyzer.py
│   │   ├── evidence_capture.py
│   │   └── separate_analyzer.py
│   ├── parsers/                # Content parsing modules
│   │   ├── html_parser.py
│   │   ├── meta_parser.py
│   │   ├── javascript_parser.py
│   │   └── structured_data_parser.py
│   ├── models/                 # Data models
│   │   └── analysis_result.py
│   ├── utils/                  # Utility functions
│   │   ├── url_validator.py
│   │   └── report_generator.py
│   └── config/                 # Configuration
│       └── settings.py
├── tests/                      # Test files
├── docs/                       # Documentation
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
└── README.md                   # This file
```

## 🎯 How to Use

### Basic Usage

1. **Enter a URL**: In the sidebar, enter the full URL of the website you want to analyze
2. **Select Analysis Type**: Choose from the available analysis types
3. **Configure Options**: Adjust advanced options like crawler types and evidence capture
4. **Start Analysis**: Click "Start Analysis" to begin the process
5. **Review Results**: Navigate through the detailed tabs to see comprehensive results
6. **Export Reports**: Use the Export Report tab to download analysis data

### Analysis Types Explained

#### Comprehensive Analysis
- **Best for**: Complete website evaluation
- **Includes**: All analysis types, scoring, and recommendations
- **Duration**: Longer (2-5 minutes depending on site complexity)

#### LLM Accessibility Only
- **Best for**: Focused LLM optimization
- **Includes**: LLM analysis, enhanced LLM analysis, llms.txt analysis
- **Duration**: Medium (1-3 minutes)

#### Web Crawler Testing
- **Best for**: Understanding crawler behavior
- **Includes**: Multiple crawler simulations, evidence capture
- **Duration**: Medium (1-3 minutes)

#### SSR Detection Only
- **Best for**: Quick SSR identification
- **Includes**: Server-side rendering detection
- **Duration**: Fast (30 seconds - 1 minute)

### Understanding the Results

#### Score Cards
- **Scraper Friendliness**: How well web scrapers can access your content
- **LLM Accessibility**: How well LLMs can understand your content
- **Grades**: A-F scale (A = Excellent, F = Poor)

#### Detailed Tabs
- **Executive Summary**: High-level overview and key takeaways
- **Overview**: Detailed score breakdowns
- **LLM Analysis**: What LLMs can and cannot access
- **Enhanced LLM Analysis**: Detailed LLM crawler capabilities
- **LLMs.txt Analysis**: Analysis of llms.txt file (if present)
- **SSR Detection**: Server-side rendering analysis
- **Crawler Testing**: Results from different crawler simulations
- **Evidence Report**: Detailed evidence from crawler tests
- **Content**: Text content analysis
- **Structure**: HTML structure analysis
- **Meta Data**: Meta tags and structured data
- **JavaScript**: JavaScript usage analysis
- **Recommendations**: Optimization suggestions
- **Export Report**: Download analysis data

## 🔧 Configuration

### Environment Variables
The application uses the following configuration options:

- `MAX_PAGE_SIZE_MB`: Maximum page size for analysis (default: 10MB)
- `DEFAULT_TIMEOUT`: Default timeout for requests (default: 30 seconds)
- `ENABLE_DYNAMIC_ANALYSIS`: Enable/disable dynamic analysis (default: True)

### Advanced Options

#### Crawler Types
- **LLM Crawlers**: Simulates AI crawlers (ChatGPT, Claude, etc.)
- **Googlebot**: Simulates Google's crawler
- **Custom**: Define custom user agents

#### Evidence Capture
- **Enabled**: Captures detailed evidence from crawler tests
- **Disabled**: Skips evidence capture for faster analysis

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_static_analyzer.py

# Run with verbose output
pytest -v
```

### Test Coverage
The project maintains comprehensive test coverage:
- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **End-to-End Tests**: Full workflow testing

## 🚨 Security Considerations

### XSS Protection
- All user input is properly sanitized before rendering
- URLs are HTML-escaped to prevent XSS attacks
- External content is validated before display

### Data Privacy
- No analysis data is stored permanently
- All data is processed locally
- No external API calls (except for website analysis)

## 🐛 Troubleshooting

### Common Issues

#### Dynamic Analysis Fails
- **Cause**: Windows Store Python limitations
- **Solution**: Use regular Python installation or disable dynamic analysis

#### Import Errors
- **Cause**: Missing dependencies
- **Solution**: Run `pip install -r requirements.txt`

#### Memory Issues
- **Cause**: Large websites or multiple concurrent analyses
- **Solution**: Reduce page size limit or restart the application

### Performance Optimization

#### For Large Websites
- Increase timeout settings
- Disable dynamic analysis for faster results
- Use specific analysis types instead of comprehensive

#### For Multiple Users
- Consider deploying with external task queues
- Use load balancing for high-traffic scenarios
- Monitor memory usage

## 🔄 Development

### Adding New Analyzers

1. Create analyzer class in `src/analyzers/`
2. Implement required methods
3. Add to main application
4. Write tests
5. Update documentation

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📊 Performance Metrics

### Analysis Times
- **Simple Static Sites**: 30-60 seconds
- **Complex SPAs**: 2-5 minutes
- **Large Sites**: 3-8 minutes

### Resource Usage
- **Memory**: 100-500MB per analysis
- **CPU**: Moderate during analysis
- **Network**: Depends on site size and complexity

## 🆘 Support

### Getting Help
- Check the troubleshooting section above
- Review the test files for usage examples
- Open an issue for bugs or feature requests

### Reporting Issues
When reporting issues, please include:
- Python version
- Operating system
- Error messages
- Steps to reproduce
- Sample URL (if applicable)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Streamlit**: For the excellent web framework
- **BeautifulSoup**: For HTML parsing capabilities
- **Playwright**: For dynamic content analysis
- **Pydantic**: For data validation and modeling

## 🔮 Future Enhancements

### Planned Features
- **PDF Report Generation**: Professional PDF reports
- **API Integration**: REST API for programmatic access
- **Batch Analysis**: Analyze multiple URLs at once
- **Custom Crawler Definitions**: User-defined crawler behaviors
- **Real-time Monitoring**: Continuous website monitoring
- **Integration with CI/CD**: Automated analysis in deployment pipelines

### Roadmap
- **Q1 2024**: Enhanced reporting and export features
- **Q2 2024**: API development and batch processing
- **Q3 2024**: Real-time monitoring capabilities
- **Q4 2024**: Enterprise features and integrations

---

**Built with ❤️ for the web development community**

*Analyze websites for scraper and LLM accessibility*