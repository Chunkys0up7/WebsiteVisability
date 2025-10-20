# Web Scraper & LLM Content Analysis Application

A comprehensive tool to analyze any website URL and determine exactly what content is accessible to web scrapers and Large Language Models (LLMs).

## Features

- **Dual Analysis Engine**: Compare static HTML parsing vs JavaScript-rendered content
- **Complete Visibility**: Shows exactly what scrapers and LLMs can/cannot access
- **Scraper-Friendliness Score**: Rates websites on 6 key criteria (0-100 scale)
- **LLM Accessibility Analysis**: Evaluates content structure and semantic markup
- **Hidden Content Detection**: Identifies CSS-hidden elements that are still scrapable
- **JavaScript Framework Detection**: Identifies React, Vue, Angular, and other frameworks
- **Structured Data Analysis**: Detects JSON-LD, Microdata, and RDFa markup
- **Meta Tag Analysis**: Comprehensive meta tag, Open Graph, and Twitter Card parsing
- **Crawler Directives**: Analyzes robots.txt and llms.txt files
- **Actionable Recommendations**: Provides specific optimization suggestions
- **Export Capabilities**: Generate PDF, JSON, and CSV reports

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd web_scraper_llm_analyzer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers (for JavaScript rendering):
```bash
playwright install chromium
```

5. Copy the environment file and configure:
```bash
cp .env.example .env
```

## Usage

### Running the Application

Start the Streamlit web interface:
```bash
streamlit run app/main.py
```

The application will open in your browser at `http://localhost:8501`.

### Basic Analysis

1. Enter a website URL in the input field
2. Click "Analyze Website"
3. View comprehensive analysis results across multiple tabs:
   - **Overview**: Summary scores and key findings
   - **Content Analysis**: Detailed text extraction results
   - **Structure Analysis**: HTML hierarchy and semantic elements
   - **Meta Data**: All meta tags and structured data
   - **JavaScript Analysis**: Framework detection and dynamic content
   - **Crawler Directives**: robots.txt and llms.txt analysis
   - **Recommendations**: Actionable optimization suggestions

### Export Results

- Click the "Export Report" button to generate a PDF report
- Use "Download JSON" for raw data export
- Export structured data to CSV for further analysis

## Project Structure

```
web_scraper_llm_analyzer/
├── src/                    # Core application logic
│   ├── analyzers/         # Analysis engines
│   ├── parsers/           # HTML, meta, and structured data parsers
│   ├── utils/             # Utility functions
│   └── models/            # Data models
├── app/                   # Streamlit web interface
│   ├── pages/            # Dashboard pages
│   └── components/       # Reusable UI components
├── tests/                # Unit and integration tests
├── config/               # Configuration files
├── docs/                 # Documentation
└── requirements.txt      # Python dependencies
```

## Key Analysis Components

### Static Content Analyzer
Uses BeautifulSoup to extract content from raw HTML (what basic scrapers see).

### Dynamic Content Analyzer
Uses Playwright/Selenium to render JavaScript and extract dynamic content.

### Content Comparison Engine
Compares static vs dynamic content to identify JavaScript-dependent elements.

### Scoring System
- **Static Content Quality** (25 points)
- **Semantic HTML Structure** (20 points)
- **Structured Data Implementation** (20 points)
- **Meta Tag Completeness** (15 points)
- **JavaScript Dependency** (10 points)
- **Crawler Accessibility** (10 points)

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/ app/ tests/
```

### Type Checking
```bash
mypy src/
```

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

## License

[Your License Here]

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Acknowledgments

Based on comprehensive research about web scraping, LLM content access, and modern web technologies.

