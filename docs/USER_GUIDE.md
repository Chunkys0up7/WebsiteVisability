# Web Scraper & LLM Analyzer - User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Understanding the Analysis](#understanding-the-analysis)
4. [Using the Web Interface](#using-the-web-interface)
5. [Interpreting Results](#interpreting-results)
6. [Optimization Guide](#optimization-guide)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

---

## Introduction

### What is the Web Scraper & LLM Analyzer?

The Web Scraper & LLM Analyzer is a comprehensive tool that analyzes websites to determine exactly what content is accessible to web scrapers and Large Language Models (LLMs). It helps you:

- **Understand visibility**: See what content scrapers and LLMs can extract from your website
- **Identify barriers**: Discover JavaScript dependencies and hidden content
- **Optimize accessibility**: Get actionable recommendations to improve content discoverability
- **Track performance**: Monitor your scraper-friendliness and LLM accessibility scores

### Who Should Use This Tool?

- **Website Owners**: Ensure your content is accessible to search engines and AI
- **SEO Professionals**: Optimize websites for better crawler accessibility
- **Content Strategists**: Understand how LLMs perceive your content
- **Web Developers**: Identify technical barriers to content extraction
- **Digital Marketers**: Improve content discoverability for AI-powered search

### What Makes Content Accessible?

✅ **Good for Scrapers & LLMs**:
- Static HTML content
- Semantic HTML5 elements
- Proper heading hierarchy
- Meta tags and structured data
- Server-side rendered content

❌ **Problematic for Scrapers & LLMs**:
- JavaScript-only rendered content
- Content behind user interactions
- Single Page Applications without SSR
- Heavy AJAX dependencies
- Missing meta data

---

## Getting Started

### Installation

#### Prerequisites
- Python 3.8 or higher
- pip package manager
- 2GB free RAM minimum

#### Step 1: Clone the Repository
```bash
git clone https://github.com/Chunkys0up7/WebsiteVisability.git
cd WebsiteVisability/web_scraper_llm_analyzer
```

#### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 3: Install Playwright Browsers (for dynamic analysis)
```bash
playwright install chromium
```

### Running the Application

#### Start the Web Interface
```bash
streamlit run app/main.py
```

The application will open automatically in your browser at `http://localhost:8501`

#### Alternative: Command Line Access
```bash
# Run tests
pytest tests/ -v

# Generate coverage report
pytest tests/ --cov=src --cov-report=html
```

---

## Understanding the Analysis

### Analysis Types

#### 1. Static Analysis (Always Performed)
**What it does**: Fetches and parses raw HTML without executing JavaScript

**What it reveals**:
- Content visible in HTML source code
- HTML structure and semantic elements
- Meta tags and structured data
- What basic scrapers can see

**Time**: ~2-5 seconds

#### 2. Dynamic Analysis (Optional)
**What it does**: Renders the page in a headless browser with JavaScript execution

**What it reveals**:
- Content loaded by JavaScript
- AJAX-fetched content
- What modern browsers see
- Difference from static content

**Time**: ~10-20 seconds

**When to use dynamic analysis**:
- ✅ Testing Single Page Applications (SPAs)
- ✅ Analyzing JavaScript-heavy websites
- ✅ Comparing static vs rendered content
- ❌ Quick checks (use static only)
- ❌ Very slow websites (may timeout)

### Scoring System

#### Scraper-Friendliness Score (0-100)
Measures how easily web scrapers can extract your content.

**Components**:
- **Static Content Quality** (25 pts): Word count, structure, media
- **Semantic HTML** (20 pts): Proper HTML5 elements, heading hierarchy
- **Structured Data** (20 pts): JSON-LD, Microdata, RDFa
- **Meta Tags** (15 pts): Title, description, Open Graph, Twitter Cards
- **JavaScript Dependency** (10 pts): Content accessibility without JS
- **Crawler Accessibility** (10 pts): robots.txt, sitemaps

#### LLM Accessibility Score (0-100)
Measures how well LLMs can understand and extract your content.

**Key Differences from Scraper Score**:
- **Emphasizes content quality and semantic structure**
- **Less concerned with JavaScript** (LLMs can use headless browsers)
- **Values token efficiency** and clear context

#### Letter Grades
- **A+ (97-100)**: Exceptional - Best practices implemented
- **A (93-96)**: Excellent - Very well optimized
- **A- (90-92)**: Excellent - Minor improvements possible
- **B+ (87-89)**: Good - Some optimization opportunities
- **B (83-86)**: Good - Several improvements recommended
- **B- (80-82)**: Good - Multiple areas to enhance
- **C+ (77-79)**: Fair - Significant improvements needed
- **C (73-76)**: Fair - Many optimization opportunities
- **C- (70-72)**: Fair - Major enhancements required
- **D+ (67-69)**: Poor - Critical issues present
- **D (63-66)**: Poor - Serious accessibility problems
- **D- (60-62)**: Poor - Minimal accessibility
- **F (<60)**: Failing - Major overhaul needed

---

## Using the Web Interface

### Main Interface

#### 1. Configuration Sidebar (Left)

**URL Input**:
- Enter the complete URL including `https://`
- Example: `https://example.com`
- Validation occurs automatically

**Analysis Options**:
- ☑️ **Include dynamic analysis**: Check to render page with JavaScript
- Uncheck for faster, static-only analysis

**Analyze Button**:
- Click "🚀 Analyze Website" to start analysis
- Loading spinners indicate progress
- Success message with balloons when complete

**Information Sections**:
- 📘 **About This Tool**: Overview of capabilities
- 📊 **Scoring Breakdown**: Explanation of scoring components

#### 2. Results Dashboard (Main Area)

After analysis, you'll see **quick metrics** in 4 cards:

1. **Scraper Friendliness**: Score and letter grade
2. **LLM Accessibility**: Score and letter grade  
3. **Word Count**: Total words found
4. **Recommendations**: Count of suggestions (with critical count)

### Results Tabs

#### Tab 1: 📊 Overview

**Purpose**: High-level summary of your site's accessibility

**What you'll see**:

**Scraper Friendliness Breakdown**:
- Each component with score and max score
- Percentage bars showing performance
- **✅ Strengths**: Things you're doing well
- **⚠️ Issues**: Areas needing attention

**LLM Accessibility Breakdown**:
- Similar component breakdown
- Emphasis on content and structure
- Note about LLM handling of JavaScript

**How to use it**:
1. Check overall grade first
2. Identify lowest-scoring components
3. Expand issue sections for details
4. Note strengths to maintain

#### Tab 2: 📝 Content

**Purpose**: Analyze the content scrapers and LLMs can extract

**Metrics Displayed**:
- **Characters**: Total character count
- **Words**: Total word count
- **Estimated Tokens**: For LLM processing cost estimation
- **Paragraphs**: Number of <p> tags
- **Links**: Clickable links found
- **Images**: Image elements
- **Tables**: Data tables
- **Lists**: Ordered and unordered lists

**Content Preview**:
- First 5,000 characters of extracted text
- Shows exactly what scrapers see
- Useful for verifying content extraction

**How to use it**:
1. Verify word count is substantial (500+ recommended)
2. Check that important text appears in preview
3. Ensure structural elements are present
4. Compare with what you see visually on the page

#### Tab 3: 🏗️ Structure

**Purpose**: Analyze HTML structure and semantic markup

**Metrics Displayed**:
- **Total Elements**: All HTML elements found
- **DOM Depth**: Nesting level (lower is better)
- **Semantic Elements**: Count of HTML5 semantic tags

**Heading Hierarchy**:
- Lists all H1-H6 headings
- Shows heading text
- Displays up to 5 per level

**Semantic HTML Elements**:
- Lists detected semantic tags
- Examples: `<header>`, `<main>`, `<article>`, `<nav>`, `<section>`, `<footer>`

**How to use it**:
1. Ensure **exactly one H1** heading
2. Check logical H2-H6 progression
3. Verify semantic elements are used
4. Keep DOM depth reasonable (< 15 levels)

#### Tab 4: 🏷️ Meta Data

**Purpose**: Review meta tags and structured data

**Basic Meta Tags**:
- **Title**: Page title (30-60 chars recommended)
- **Description**: Meta description (120-160 chars recommended)
- **Canonical URL**: Preferred URL for this page

**Open Graph Tags**:
- Social media sharing metadata
- `og:title`, `og:description`, `og:image`, `og:url`
- Used by Facebook, LinkedIn, etc.

**Twitter Card Tags**:
- Twitter-specific sharing metadata
- `twitter:card`, `twitter:title`, `twitter:description`

**Structured Data**:
- ✅ **JSON-LD**: Found/Not found
- ✅ **Microdata**: Found/Not found
- ✅ **RDFa**: Found/Not found
- Expandable JSON viewer for data inspection

**How to use it**:
1. Verify title and description exist and are optimal length
2. Check Open Graph tags for social sharing
3. Confirm structured data is implemented
4. Review JSON-LD for accuracy

#### Tab 5: ⚡ JavaScript

**Purpose**: Understand JavaScript dependencies and framework usage

**Script Metrics**:
- **Total Scripts**: All JavaScript files/blocks
- **Inline Scripts**: Scripts embedded in HTML
- **External Scripts**: Loaded from URLs
- **Frameworks**: Number of detected frameworks

**Indicators**:
- **SPA Detected**: Yes/No (Single Page Application)
- **AJAX Usage**: Yes/No (Asynchronous data fetching)
- **Dynamic Content**: Yes/No (JavaScript-rendered content)

**Detected Frameworks**:
- Lists all identified frameworks
- Shows confidence level
- Supports: React, Vue, Angular, jQuery, Svelte, Next.js, Nuxt, Gatsby, Alpine, Backbone, Ember

**Static vs Dynamic Comparison** (if dynamic analysis performed):
- **Similarity Score**: Percentage match between static and dynamic
- **Content Difference**: Character count difference
- **JS Dependent**: Whether content requires JavaScript
- **Missing in Static**: List of content only visible with JavaScript

**How to use it**:
1. High script count (>10) may indicate accessibility issues
2. SPA = "Yes" means content likely needs JavaScript
3. Low similarity score (<80%) = significant JS dependency
4. Review "Missing in Static" to find problematic content

#### Tab 6: 💡 Recommendations

**Purpose**: Get specific, actionable optimization suggestions

**Priority Levels**:

🔴 **Critical Issues** (Red, expanded by default):
- Must-fix problems
- Severely impact accessibility
- Examples: Missing H1, no meta description

🟠 **High Priority** (Orange, expanded by default):
- Important improvements
- Significant impact on scores
- Examples: Add JSON-LD, use semantic HTML

🟡 **Medium Priority** (Collapsed):
- Helpful enhancements
- Moderate impact
- Examples: Improve content structure

🟢 **Low Priority** (Collapsed):
- Minor optimizations
- Small improvements
- Examples: Add additional meta tags

**Each Recommendation Includes**:
- **Title**: What to fix
- **Description**: Why it matters
- **Difficulty**: How hard to implement (Easy/Medium/Hard)
- **Impact**: Expected improvement (High/Medium/Low)
- **Category**: Area affected (content, html, meta, etc.)
- **Code Example**: Actual code to implement
- **Resources**: Links to documentation

**How to use it**:
1. Start with Critical issues
2. Implement High priority items next
3. Review code examples for implementation
4. Use resource links for detailed guidance
5. Re-analyze after changes to track improvement

---

## Interpreting Results

### Common Scenarios

#### Scenario 1: Low Content Score
**Symptoms**:
- Static Content Quality < 15/25
- Low word count (<200 words)
- Few structural elements

**Diagnosis**: Insufficient content

**Solution**:
1. Add more descriptive text content
2. Break content into paragraphs
3. Add relevant links and media
4. Aim for 500+ words minimum

#### Scenario 2: Poor Semantic HTML
**Symptoms**:
- Semantic HTML Structure < 12/20
- No semantic elements detected
- Multiple H1 headings or none

**Diagnosis**: Using generic div/span instead of semantic HTML

**Solution**:
1. Replace divs with semantic elements
2. Use `<header>`, `<main>`, `<article>`, `<nav>`, `<footer>`
3. Implement proper heading hierarchy (one H1, then H2-H6)
4. Use `<section>` and `<aside>` appropriately

#### Scenario 3: Missing Structured Data
**Symptoms**:
- Structured Data Score < 10/20
- No JSON-LD, Microdata, or RDFa found

**Diagnosis**: Missing Schema.org markup

**Solution**:
1. Add JSON-LD script in `<head>`
2. Use Schema.org appropriate type (Organization, Article, Product, etc.)
3. Include key properties (name, description, image, url)
4. Validate with Google's Rich Results Test

#### Scenario 4: JavaScript Dependency
**Symptoms**:
- JavaScript Score < 6/10
- Low similarity score (<70%)
- Many items in "Missing in Static"
- SPA detected

**Diagnosis**: Content requires JavaScript to display

**Solution**:
1. Implement Server-Side Rendering (SSR)
2. Use frameworks with SSR support (Next.js, Nuxt.js)
3. Move critical content to static HTML
4. Consider pre-rendering for static sites

#### Scenario 5: Meta Tag Issues
**Symptoms**:
- Meta Tag Score < 10/15
- Missing or poorly formatted title/description
- No Open Graph or Twitter Cards

**Diagnosis**: Incomplete meta data

**Solution**:
1. Add/optimize title tag (30-60 characters)
2. Write compelling description (120-160 characters)
3. Implement Open Graph tags for social sharing
4. Add Twitter Card tags
5. Set canonical URL

---

## Optimization Guide

### Quick Wins (Easy Implementations)

#### 1. Add Missing Meta Tags (15 minutes)
```html
<!-- In <head> section -->
<title>Your Page Title - Brand Name</title>
<meta name="description" content="Compelling description of your page content.">
<link rel="canonical" href="https://yoursite.com/page">
```

#### 2. Fix Heading Hierarchy (30 minutes)
```html
<!-- Use ONE H1 -->
<h1>Main Page Title</h1>

<!-- Then H2 for main sections -->
<h2>First Section</h2>
<p>Content...</p>

<h2>Second Section</h2>
<!-- Use H3 for subsections -->
<h3>Subsection</h3>
<p>Content...</p>
```

#### 3. Add JSON-LD Structured Data (20 minutes)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Your Company Name",
  "url": "https://yoursite.com",
  "logo": "https://yoursite.com/logo.png",
  "description": "What your company does"
}
</script>
```

#### 4. Implement Open Graph Tags (15 minutes)
```html
<meta property="og:title" content="Your Page Title">
<meta property="og:description" content="Page description">
<meta property="og:image" content="https://yoursite.com/image.jpg">
<meta property="og:url" content="https://yoursite.com/page">
<meta property="og:type" content="website">
```

### Medium-Term Improvements

#### 1. Use Semantic HTML (2-4 hours)
**Before**:
```html
<div class="header">
  <div class="nav">...</div>
</div>
<div class="content">
  <div class="article">...</div>
</div>
<div class="footer">...</div>
```

**After**:
```html
<header>
  <nav>...</nav>
</header>
<main>
  <article>...</article>
</main>
<footer>...</footer>
```

#### 2. Improve Content Structure (4-8 hours)
- Add descriptive paragraphs (aim for 500+ words)
- Include relevant internal/external links
- Add descriptive alt text to images
- Structure data in proper HTML tables
- Use lists for enumerated items

#### 3. Optimize for Token Efficiency (2-4 hours)
- Remove redundant content
- Use clear, concise language
- Avoid excessive formatting in text
- Structure content logically
- Use heading to break up long content

### Long-Term Strategies

#### 1. Implement Server-Side Rendering (1-2 weeks)
If you're using a JavaScript framework:

**React**: Migrate to Next.js
```bash
npm install next react react-dom
```

**Vue**: Migrate to Nuxt.js
```bash
npm install nuxt
```

**Benefits**:
- Content visible in initial HTML
- Better crawler accessibility
- Improved SEO
- Faster initial page load

#### 2. Create Comprehensive Structured Data (1 week)
- Implement appropriate Schema.org types
- Add breadcrumbs markup
- Include FAQ schema if applicable
- Add Product schema for e-commerce
- Implement Article schema for blog posts

#### 3. Optimize for LLM Accessibility (Ongoing)
- Create `/llms.txt` file (like robots.txt for LLMs)
- Use clear, descriptive headings
- Structure content with semantic meaning
- Provide context and definitions
- Link related content

---

## Troubleshooting

### Common Issues

#### Issue: "Invalid URL" Error
**Symptoms**: Error message when clicking Analyze

**Causes**:
- Missing `https://` or `http://`
- Malformed URL
- Invalid domain name

**Solutions**:
1. Ensure URL starts with `https://` or `http://`
2. Check for typos in domain name
3. Test URL in a browser first

#### Issue: Analysis Takes Too Long
**Symptoms**: Spinner runs for > 60 seconds

**Causes**:
- Website is very slow
- Too many scripts to load
- Network issues

**Solutions**:
1. Try static-only analysis (uncheck dynamic option)
2. Check website loads in browser
3. Increase timeout in settings
4. Try a different, faster page

#### Issue: "Failed to fetch" Error
**Symptoms**: Error during static analysis

**Causes**:
- Website is down
- Firewall blocking requests
- Invalid SSL certificate
- robots.txt blocking

**Solutions**:
1. Verify site is accessible in browser
2. Check if site blocks automated requests
3. Try a different page on same site
4. Check robots.txt allows crawling

#### Issue: Dynamic Analysis Fails
**Symptoms**: Static works, but dynamic fails

**Causes**:
- Playwright browsers not installed
- Insufficient memory
- JavaScript errors on page

**Solutions**:
1. Run `playwright install chromium`
2. Close other applications
3. Try static-only analysis
4. Check browser console for page errors

#### Issue: Low Scores Despite Good Content
**Symptoms**: Scores lower than expected

**Causes**:
- Content is JavaScript-rendered
- Missing meta tags
- Poor HTML structure
- No structured data

**Solutions**:
1. Run dynamic analysis to compare
2. Check recommendations tab
3. Verify meta tags in browser DevTools
4. Review HTML source (View Source)

---

## FAQ

### General Questions

**Q: Is this tool free to use?**
A: Yes, the tool is open source and free to use.

**Q: Do I need technical knowledge to use this?**
A: No, the web interface is designed for non-technical users. However, implementing recommendations may require development skills.

**Q: Will analyzing my site affect its performance?**
A: No, the analysis is read-only and doesn't modify your website.

**Q: Can I analyze competitor websites?**
A: Yes, you can analyze any publicly accessible website.

**Q: How often should I run analysis?**
A: Run analysis after major website changes or at least quarterly.

### Technical Questions

**Q: What's the difference between static and dynamic analysis?**
A: Static analysis reads raw HTML without JavaScript. Dynamic analysis renders the page in a browser with JavaScript execution.

**Q: Why are my scores different from my competitors?**
A: Scores reflect objective technical criteria. Different content strategies and implementations produce different scores.

**Q: Can this tool improve my SEO?**
A: Indirectly, yes. Better crawler accessibility often correlates with better SEO, but SEO involves many other factors.

**Q: Does this analyze my site's speed?**
A: No, this tool focuses on content accessibility, not performance. Use tools like Google PageSpeed Insights for speed analysis.

**Q: Will this work with password-protected pages?**
A: No, the tool can only analyze publicly accessible pages.

### Scoring Questions

**Q: What's a good score?**
A: 
- **A (90+)**: Excellent
- **B (80-89)**: Good, minor improvements
- **C (70-79)**: Fair, needs optimization
- **D/F (<70)**: Poor, significant issues

**Q: Why is my LLM score different from my Scraper score?**
A: LLM scoring emphasizes content quality and semantic structure more than JavaScript dependency, since LLMs can use headless browsers.

**Q: Can I get a perfect 100 score?**
A: It's possible but difficult. Even well-optimized sites usually score 85-95. Focus on getting above 80.

**Q: My competitor has a lower score but ranks higher. Why?**
A: This tool measures crawler accessibility, not SEO ranking. Rankings depend on many factors including backlinks, domain authority, and content quality.

### Implementation Questions

**Q: How long does it take to implement recommendations?**
A: 
- **Critical/Easy**: 1-4 hours
- **High/Medium**: 1-2 days
- **Complex (SSR)**: 1-2 weeks

**Q: Do I need to implement all recommendations?**
A: Focus on Critical and High priority items first. Medium and Low are optional enhancements.

**Q: Will implementing recommendations break my site?**
A: Proper implementation shouldn't break anything. Always test changes in a staging environment first.

**Q: Can I hire someone to implement these changes?**
A: Yes, any web developer familiar with HTML, meta tags, and your framework can implement these recommendations.

---

## Getting Help

### Support Resources

**Documentation**:
- This User Guide
- README.md
- API Documentation (in `/docs`)

**Community**:
- GitHub Issues: Report bugs or request features
- Discussions: Ask questions and share experiences

**Professional Support**:
For custom implementations or consulting, contact your web development team.

---

## Appendix

### Keyboard Shortcuts

In Streamlit interface:
- `Ctrl/Cmd + R`: Refresh page
- `Ctrl/Cmd + Enter`: Rerun analysis
- `Ctrl/Cmd + K`: Open settings

### Browser Compatibility

**Recommended Browsers**:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### System Requirements

**Minimum**:
- 2GB RAM
- 1GB free disk space
- Internet connection

**Recommended**:
- 4GB RAM
- 2GB free disk space
- Fast internet connection

---

**Last Updated**: October 20, 2025  
**Version**: 1.0.0  
**For Support**: Open an issue on GitHub

