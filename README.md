# Web Scraper & LLM Analyzer

A comprehensive tool to analyze website accessibility for web scrapers and Large Language Models (LLMs).

## Features

- **Dual Analysis Engine**: Static HTML parsing and dynamic JavaScript rendering
- **Comprehensive Scoring**: 100-point scoring system for scraper-friendliness and LLM accessibility
- **Actionable Recommendations**: Priority-based suggestions with code examples
- **Beautiful Web Interface**: Built with Streamlit for easy analysis
- **Detailed Reports**: Analyze content, structure, meta data, JavaScript usage, and more

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Chunkys0up7/WebsiteVisability.git
cd WebsiteVisability/web_scraper_llm_analyzer

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for dynamic analysis)
playwright install chromium
```

### Run the Web Application

```bash
streamlit run app/main.py
```

The application will open in your browser at `http://localhost:8501`.

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html
```

## Project Structure

```
web_scraper_llm_analyzer/
├── src/                      # Core application code
│   ├── analyzers/            # Analysis engines
│   │   ├── static_analyzer.py
│   │   ├── dynamic_analyzer.py
│   │   ├── content_comparator.py
│   │   └── scoring_engine.py
│   ├── parsers/              # Content parsers
│   │   ├── html_parser.py
│   │   ├── meta_parser.py
│   │   ├── structured_data_parser.py
│   │   └── javascript_parser.py
│   ├── models/               # Data models
│   └── utils/                # Utility functions
├── app/                      # Streamlit web interface
│   └── main.py
├── tests/                    # Unit tests
└── docs/                     # Documentation
```

## How It Works

### 1. Static Analysis
- Fetches raw HTML using requests
- Parses with BeautifulSoup
- Extracts content, structure, and metadata
- Simulates basic web scraper behavior

### 2. Dynamic Analysis (Optional)
- Renders page with Playwright (headless Chrome)
- Executes JavaScript
- Captures fully rendered HTML
- Detects AJAX-loaded content

### 3. Content Comparison
- Compares static vs dynamic content
- Identifies JavaScript-dependent sections
- Calculates similarity score

### 4. Scoring & Recommendations
- **Static Content Quality** (25 pts): Word count, paragraphs, links, media
- **Semantic HTML Structure** (20 pts): Proper heading hierarchy, semantic elements
- **Structured Data** (20 pts): JSON-LD, Microdata, RDFa implementation
- **Meta Tags** (15 pts): Title, description, Open Graph, Twitter Cards
- **JavaScript Dependency** (10 pts): Content accessibility without JS
- **Crawler Accessibility** (10 pts): robots.txt, sitemaps

## Scoring System

### Letter Grades
- **A (90-100)**: Excellent - Fully optimized for scrapers and LLMs
- **B (80-89)**: Good - Minor improvements possible
- **C (70-79)**: Fair - Several optimization opportunities
- **D (60-69)**: Poor - Significant issues to address
- **F (<60)**: Failing - Major accessibility problems

### LLM vs Scraper Scoring
- **Scraper Score**: Emphasizes static content and low JavaScript dependency
- **LLM Score**: Emphasizes content quality and semantic structure (LLMs can handle dynamic content)

## Usage Examples

### Analyze a Website

1. Open the Streamlit app
2. Enter a URL (e.g., `https://example.com`)
3. Choose whether to include dynamic analysis
4. Click "Analyze Website"
5. View comprehensive results in 6 tabs:
   - Overview: Score breakdowns
   - Content: Text analysis
   - Structure: HTML structure
   - Meta Data: SEO and structured data
   - JavaScript: Framework detection
   - Recommendations: Prioritized improvements

### Interpreting Results

**High Scores (A/B)**:
- Content is easily accessible to scrapers
- Well-structured for LLM understanding
- Good SEO practices
- Minimal JavaScript dependency for critical content

**Low Scores (D/F)**:
- Heavy JavaScript dependency
- Missing or poor meta tags
- No structured data
- Poor HTML structure
- Limited static content

## Key Recommendations

### For Better Scraper Accessibility:
1. Use semantic HTML5 elements (`<header>`, `<main>`, `<article>`, etc.)
2. Implement proper heading hierarchy (single H1, H2-H6 structure)
3. Add JSON-LD structured data
4. Ensure critical content is in static HTML
5. Include comprehensive meta tags

### For Better LLM Accessibility:
1. Use descriptive, semantic HTML
2. Include Schema.org structured data
3. Write clear, descriptive content
4. Use proper document structure
5. Avoid hiding important content

## Technology Stack

- **Python 3.8+**
- **BeautifulSoup4**: HTML parsing
- **Playwright**: Headless browser automation
- **Streamlit**: Web interface
- **Pydantic**: Data validation
- **pytest**: Testing framework

## Test Coverage

- **194 tests** with **87% coverage**
- All core parsers: 85-93% coverage
- All analyzers: 75-100% coverage
- Comprehensive unit and integration tests

## Development

### Running in Development Mode

```bash
# Run with auto-reload
streamlit run app/main.py --server.runOnSave=true

# Run specific test file
pytest tests/test_analyzers/test_scoring_engine.py -v

# Generate coverage report
pytest tests/ --cov=src --cov-report=term-missing
```

### Adding New Features

1. Follow the existing code structure
2. Write tests first (TDD approach)
3. Ensure 100% of tests pass
4. Update `IMPLEMENTATION_CHECKLIST.md`
5. Commit with descriptive messages
6. Push to main branch

## Project Progress

**Overall: 46.4% Complete** (97/209 tasks)

- ✅ Setup: 100% Complete
- ✅ Core Parsers: 100% Complete (4/4)
- ✅ Analysis Engines: 100% Complete (4/4)
- ⏳ Web Interface: 13% Complete (9/70)
- ⏳ Testing: 50% Complete (8/16)
- ⏳ Export: 0% Complete (0/6)
- ⏳ Advanced Features: 0% Complete (0/11)
- ⏳ Documentation: 0% Complete (0/8)
- ⏳ Deployment: 0% Complete (0/10)

## Contributing

1. Follow the code quality guidelines in `instructions.md`
2. Test all code thoroughly
3. Maintain project structure
4. Update checklist after each change
5. Commit and push to main after verification

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Built with ❤️ for better web accessibility**
