# Quick Start Guide

## Installation

### 1. Clone and Navigate
```bash
cd web_scraper_llm_analyzer
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers
```bash
playwright install chromium
```

### 5. Configure Environment
```bash
# Copy example environment file
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux

# Edit .env file with your preferences (optional)
```

## Running the Application

### Local Development
```bash
streamlit run app/main.py
```

The application will open automatically in your browser at `http://localhost:8501`

### Using Docker
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Usage

1. **Enter URL**: Type or paste a website URL in the input field
2. **Click Analyze**: Start the analysis process
3. **View Results**: Explore different tabs:
   - **Overview**: Summary scores and key findings
   - **Content**: What text content is extractable
   - **Structure**: HTML hierarchy and semantic elements
   - **Meta Data**: Meta tags and structured data
   - **JavaScript**: Framework detection and dynamic content
   - **Crawler**: robots.txt and llms.txt analysis
   - **Recommendations**: Optimization suggestions
4. **Export**: Download reports in PDF, JSON, or CSV format

## What the Tool Analyzes

### ✅ Fully Accessible to Scrapers
- Static HTML content
- HTML structure and semantic elements
- Meta tags (title, description, Open Graph, Twitter Cards)
- Structured data (JSON-LD, Microdata, RDFa)
- CSS-hidden elements (display:none, visibility:hidden)
- HTML comments

### ❌ Requires JavaScript Execution
- Dynamically loaded content
- AJAX/API data
- Single Page Application content
- Interactive elements
- Content behind user interactions

### 📊 Analysis Scores

**Scraper-Friendliness Score (0-100)**
- Static Content Quality (25 points)
- Semantic HTML Structure (20 points)
- Structured Data Implementation (20 points)
- Meta Tag Completeness (15 points)
- JavaScript Dependency (10 points)
- Crawler Accessibility (10 points)

**LLM Accessibility Score (0-100)**
- Content structure and clarity
- Semantic markup presence
- Token efficiency
- Context availability

## Example Analysis

```python
# Example: Analyzing a URL programmatically
from src.analyzers import StaticAnalyzer, DynamicAnalyzer, ContentComparator
from src.utils import validate_url

# Validate URL
is_valid, url, error = validate_url("https://example.com")

if is_valid:
    # Static analysis
    static_analyzer = StaticAnalyzer()
    static_result = static_analyzer.analyze(url)
    
    # Dynamic analysis
    dynamic_analyzer = DynamicAnalyzer()
    dynamic_result = dynamic_analyzer.analyze(url)
    
    # Compare results
    comparator = ContentComparator()
    comparison = comparator.compare(static_result, dynamic_result)
    
    print(f"Static content: {len(static_result.text_content)} chars")
    print(f"Dynamic content: {len(dynamic_result.text_content)} chars")
    print(f"Similarity: {comparison.similarity_score:.2%}")
```

## Common Issues

### Issue: Playwright browsers not installed
**Solution**: Run `playwright install chromium`

### Issue: Port 8501 already in use
**Solution**: 
```bash
streamlit run app/main.py --server.port=8502
```

### Issue: Timeout errors on large websites
**Solution**: Increase timeout in `.env`:
```
DEFAULT_TIMEOUT=60
BROWSER_TIMEOUT=60000
```

### Issue: Memory errors
**Solution**: Reduce max page size in `.env`:
```
MAX_PAGE_SIZE_MB=5
```

## Development

### Run Tests
```bash
pytest
```

### Format Code
```bash
black src/ app/ tests/
```

### Type Checking
```bash
mypy src/
```

## Next Steps

- Read `README.md` for detailed documentation
- Check `Web_Scraper_LLM_Analysis_Plan.md` for implementation roadmap
- Review `PROJECT_STRUCTURE.md` for architecture details
- Explore `docs/` for additional examples

## Support

For issues or questions:
1. Check existing documentation
2. Review error logs in console
3. Open an issue on GitHub
4. Contact the development team

## Key Takeaways

- **CSS styling is ignored** by LLMs and scrapers
- **CSS-hidden content is still accessible** to scrapers
- **JavaScript-rendered content** requires headless browsers
- **Semantic HTML** significantly improves LLM understanding
- **Structured data** (JSON-LD) helps with AI search visibility
- **Static content** is more reliable for scraper access

