# Project Structure Overview

## Directory Layout

```
web_scraper_llm_analyzer/
├── src/                           # Core application logic
│   ├── __init__.py
│   ├── analyzers/                 # Analysis engines
│   │   ├── __init__.py
│   │   ├── static_analyzer.py    # BeautifulSoup-based static analysis
│   │   ├── dynamic_analyzer.py   # Playwright/Selenium dynamic analysis
│   │   ├── content_comparator.py # Compare static vs dynamic content
│   │   └── scoring_engine.py     # Calculate scraper-friendliness scores
│   ├── parsers/                   # Content parsers
│   │   ├── __init__.py
│   │   ├── html_parser.py        # HTML structure parsing
│   │   ├── meta_parser.py        # Meta tags and Open Graph
│   │   ├── structured_data_parser.py  # JSON-LD, Microdata, RDFa
│   │   └── javascript_parser.py  # JavaScript framework detection
│   ├── utils/                     # Utility functions
│   │   ├── __init__.py
│   │   ├── validators.py         # URL validation
│   │   ├── token_counter.py      # Token counting for LLMs
│   │   └── helpers.py            # General helpers
│   └── models/                    # Data models
│       ├── __init__.py
│       ├── analysis_result.py    # Analysis result models
│       └── scoring_models.py     # Scoring and recommendation models
├── app/                           # Streamlit web interface
│   ├── __init__.py
│   ├── main.py                   # Main Streamlit application
│   ├── pages/                    # Dashboard pages
│   │   ├── __init__.py
│   │   ├── overview.py           # Summary dashboard
│   │   ├── content_analysis.py   # Content extraction results
│   │   ├── structure_analysis.py # HTML structure analysis
│   │   ├── meta_analysis.py      # Meta tags and structured data
│   │   ├── javascript_analysis.py # JavaScript detection
│   │   ├── crawler_analysis.py   # robots.txt and llms.txt
│   │   └── recommendations.py    # Optimization suggestions
│   └── components/               # Reusable UI components
│       ├── __init__.py
│       ├── charts.py             # Visualization components
│       ├── tables.py             # Table components
│       └── forms.py              # Form components
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── test_analyzers/          # Analyzer tests
│   ├── test_parsers/            # Parser tests
│   └── test_utils/              # Utility tests
├── config/                       # Configuration
│   ├── __init__.py
│   ├── settings.py              # Application settings
│   └── logging_config.py        # Logging configuration
├── docs/                        # Documentation
│   └── examples/                # Usage examples
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Development dependencies
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── README.md                    # Project documentation
├── Dockerfile                   # Docker container definition
├── docker-compose.yml           # Docker Compose configuration
└── pytest.ini                   # Pytest configuration
```

## Module Descriptions

### Core Analyzers (`src/analyzers/`)

#### `static_analyzer.py`
- Uses BeautifulSoup and requests
- Extracts content from raw HTML
- Simulates basic web scraper behavior
- No JavaScript execution

#### `dynamic_analyzer.py`
- Uses Playwright/Selenium
- Renders JavaScript
- Extracts dynamically loaded content
- Simulates modern browser behavior

#### `content_comparator.py`
- Compares static vs dynamic content
- Identifies JavaScript-dependent elements
- Calculates similarity scores
- Highlights missing content in static analysis

#### `scoring_engine.py`
- Calculates scraper-friendliness score (0-100)
- Evaluates LLM accessibility
- Generates recommendations
- Prioritizes optimization opportunities

### Parsers (`src/parsers/`)

#### `html_parser.py`
- Parses HTML structure
- Extracts semantic elements
- Analyzes heading hierarchy
- Detects hidden content (CSS-hidden elements)

#### `meta_parser.py`
- Extracts meta tags
- Parses Open Graph tags
- Analyzes Twitter Card metadata
- Validates canonical URLs

#### `structured_data_parser.py`
- Detects JSON-LD
- Extracts Microdata
- Parses RDFa markup
- Validates Schema.org implementation

#### `javascript_parser.py`
- Detects JavaScript frameworks (React, Vue, Angular, etc.)
- Identifies Single Page Applications
- Counts inline and external scripts
- Analyzes AJAX usage

### Utilities (`src/utils/`)

#### `validators.py`
- URL validation and normalization
- Input sanitization
- Domain extraction

#### `token_counter.py`
- Token counting using tiktoken
- Cost estimation for LLM processing
- Multiple model support

#### `helpers.py`
- Text cleaning and normalization
- Similarity calculations
- Formatting utilities

### Data Models (`src/models/`)

#### `analysis_result.py`
- Complete analysis result structure
- Content, structure, meta, JavaScript analysis
- Performance metrics
- Status tracking

#### `scoring_models.py`
- Score breakdown models
- Recommendation structure
- Priority and impact levels
- Grade calculation

### Web Interface (`app/`)

#### `main.py`
- Main Streamlit application
- URL input and validation
- Analysis orchestration
- Results display

#### Pages (`app/pages/`)
- Modular dashboard pages
- Each page focuses on specific analysis aspect
- Interactive visualizations
- Export functionality

#### Components (`app/components/`)
- Reusable UI components
- Charts and graphs
- Data tables
- Forms and inputs

## Configuration

### Environment Variables (`.env`)
```
APP_NAME=Web Scraper & LLM Analyzer
DEBUG=False
LOG_LEVEL=INFO
DEFAULT_TIMEOUT=30
MAX_PAGE_SIZE_MB=10
ENABLE_HEADLESS_BROWSER=True
BROWSER_TYPE=chromium
```

### Settings (`config/settings.py`)
- Pydantic-based configuration
- Environment variable loading
- Type validation
- Default values

### Logging (`config/logging_config.py`)
- Colored console output
- File logging support
- Configurable log levels
- Third-party logger suppression

## Testing

### Test Structure
```
tests/
├── test_analyzers/
│   ├── test_static_analyzer.py
│   ├── test_dynamic_analyzer.py
│   ├── test_content_comparator.py
│   └── test_scoring_engine.py
├── test_parsers/
│   ├── test_html_parser.py
│   ├── test_meta_parser.py
│   ├── test_structured_data_parser.py
│   └── test_javascript_parser.py
└── test_utils/
    ├── test_validators.py
    ├── test_token_counter.py
    └── test_helpers.py
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_analyzers/test_static_analyzer.py

# Run tests by marker
pytest -m unit
pytest -m "not slow"
```

## Deployment

### Docker
```bash
# Build image
docker build -t web-scraper-llm-analyzer .

# Run container
docker run -p 8501:8501 web-scraper-llm-analyzer
```

### Docker Compose
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Development Workflow

1. **Setup Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements-dev.txt
   playwright install chromium
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Write Code**
   - Follow PEP 8 style guide
   - Add type hints
   - Write docstrings
   - Create tests

4. **Format and Lint**
   ```bash
   black src/ app/ tests/
   flake8 src/ app/ tests/
   mypy src/
   ```

5. **Run Tests**
   ```bash
   pytest
   ```

6. **Commit and Push**
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin feature/your-feature-name
   ```

## Next Steps

The following modules need to be implemented:

1. **HTML Parser** (`src/parsers/html_parser.py`)
2. **Static Analyzer** (`src/analyzers/static_analyzer.py`)
3. **Dynamic Analyzer** (`src/analyzers/dynamic_analyzer.py`)
4. **Content Comparator** (`src/analyzers/content_comparator.py`)
5. **Scoring Engine** (`src/analyzers/scoring_engine.py`)
6. **Streamlit Main App** (`app/main.py`)
7. **Dashboard Pages** (`app/pages/*.py`)

See `Web_Scraper_LLM_Analysis_Plan.md` for detailed implementation checklist.

