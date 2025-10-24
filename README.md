# WebsiteVisability - LLM Visibility Analysis Tool

A comprehensive tool for analyzing how well websites are optimized for Large Language Model (LLM) crawlers like ChatGPT, Claude, and Perplexity AI.

## 🎯 **What This Tool Does**

WebsiteVisability analyzes your website to determine:
- **What content LLMs can actually see** when they crawl your site
- **Whether redirects affect LLM access** to your content
- **Evidence of JavaScript dependencies** that may hide content from AI crawlers
- **Technical recommendations** for improving LLM visibility

## 🚀 **Quick Start**

### Prerequisites
- Python 3.8 or higher
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Chunkys0up7/WebsiteVisability.git
   cd WebsiteVisability
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run app/main.py
   ```

4. **Open your browser:**
   Navigate to `http://localhost:8501`

### First Analysis

1. **Enter your website URL** in the sidebar
2. **Watch the automatic URL verification** - this shows what URL LLMs actually access
3. **Run a Comprehensive Analysis** to get full insights
4. **Check the "URL Verification" tab** for detailed redirect analysis
5. **Review the "LLM Visibility" tab** for evidence of what LLMs can see

## 🔍 **Key Features**

### ✅ **Immediate URL Verification**
- **Automatic verification** when you enter a URL
- **Redirect chain analysis** - see exactly where LLMs end up
- **User-agent redirect detection** - identify if LLMs get different URLs
- **Content accessibility confirmation** - verify LLMs can read your content

### ✅ **Evidence-Based Analysis**
- **No confusing scores** - focus on concrete evidence
- **Raw content preview** - see exactly what LLMs receive
- **JavaScript dependency detection** - identify content hidden by scripts
- **Technical recommendations** - actionable advice for improvements

### ✅ **Comprehensive Testing**
- **Multiple crawler simulation** - test with GPTBot, ClaudeBot, PerplexityBot
- **Static vs Dynamic analysis** - compare server-rendered vs client-rendered content
- **Content comparison** - see differences between human and LLM views
- **Structured data analysis** - verify schema markup accessibility

## 📊 **Understanding Your Results**

### **URL Verification Results**
- **✅ Direct Access** - No redirects (optimal for LLMs)
- **🔄 Single Redirect** - One redirect hop (acceptable)
- **⚠️ Multiple Redirects** - Multiple hops (may cause issues)
- **🚨 User-Agent Redirect** - Different URL for LLMs (requires verification)

### **LLM Visibility Analysis**
- **Raw content preview** - First 1000 characters LLMs see
- **Content statistics** - Word count, character count, accessibility
- **JavaScript evidence** - Detection of script dependencies
- **Meta data analysis** - Title, description, structured data visibility

### **Evidence Framework**
- **Gold Standard Evidence** - Direct proof of LLM accessibility
- **Strong Evidence** - Technical indicators of visibility
- **Supporting Evidence** - Contextual information
- **Business Impact Analysis** - Quantified impact on AI search visibility

## 🛠️ **Analysis Types**

### **Comprehensive Analysis** (Recommended)
- Full static and dynamic analysis
- LLM visibility assessment
- Content comparison
- Evidence collection
- Technical recommendations

### **LLM Accessibility Only**
- Focused on LLM-specific analysis
- Faster execution
- Evidence-based insights
- Technical recommendations

### **Web Crawler Testing**
- Multiple crawler simulation
- User-agent testing
- Redirect verification
- Content accessibility testing

## 📋 **Tabs Overview**

### **Primary Analysis**
- **🔄 Comparison** - LLM vs Scraper comparison
- **🎯 Executive Summary** - High-level findings
- **📊 Overview** - Overall analysis results
- **🤖 LLM Analysis** - LLM-specific insights
- **👁️ LLM Visibility** - Evidence of what LLMs can see
- **💡 Recommendations** - Actionable improvements

### **Technical Analysis**
- **🔬 Enhanced LLM Analysis** - Detailed LLM evidence
- **📄 LLMs.txt Analysis** - AI crawler guidance analysis
- **🕷️ Scraper Analysis** - Traditional crawler analysis
- **🔍 SSR Detection** - Server-side rendering analysis
- **🕷️ Crawler Testing** - Multi-crawler testing results

### **Website Structure**
- **📝 Content** - Content analysis and statistics
- **🏗️ Structure** - HTML structure analysis
- **🏷️ Meta Data** - Meta tags and structured data
- **⚡ JavaScript** - JavaScript dependency analysis

### **Reports**
- **🔍 URL Verification** - Detailed redirect and access analysis
- **📊 Evidence Report** - Comprehensive evidence collection
- **🔬 Evidence Framework** - Evidence-based analysis tools
- **📥 Export Report** - Download analysis results

## 🎯 **Common Use Cases**

### **E-commerce Sites**
- Verify product descriptions are accessible to LLMs
- Check if pricing and specifications are visible
- Ensure structured data is accessible
- Test redirect configurations

### **Content Sites**
- Verify articles and blog posts are accessible
- Check meta descriptions and titles
- Ensure navigation is LLM-friendly
- Test content loading mechanisms

### **SaaS Platforms**
- Verify documentation is accessible
- Check API documentation visibility
- Ensure feature descriptions are available
- Test authentication and redirect flows

### **Corporate Websites**
- Verify service descriptions are accessible
- Check contact information visibility
- Ensure company information is available
- Test redirect and subdomain configurations

## 🔧 **Technical Details**

### **Supported LLM Crawlers**
- **GPTBot** (OpenAI/ChatGPT)
- **ClaudeBot** (Anthropic)
- **PerplexityBot** (Perplexity AI)
- **CCBot** (Common Crawl)

### **Analysis Methods**
- **Static Analysis** - HTML parsing and content extraction
- **Dynamic Analysis** - JavaScript execution simulation
- **Content Comparison** - Static vs dynamic content comparison
- **Evidence Collection** - Systematic evidence gathering

### **Verification Tools**
- **curl with GPTBot user agent** - Exact LLM simulation
- **requests library fallback** - Cross-platform compatibility
- **Redirect chain tracing** - Complete redirect analysis
- **Content accessibility testing** - Verify content reachability

## 📈 **Business Impact**

### **Why LLM Visibility Matters**
- **AI Search Growth** - 40% of search queries now involve AI assistants
- **Competitive Advantage** - Visible content gets recommended by AI
- **Revenue Impact** - Invisible content means lost AI-referred traffic
- **Future-Proofing** - AI search is growing 300%+ year-over-year

### **Common Issues Found**
- **JavaScript-dependent content** - Hidden from most LLM crawlers
- **User-agent redirects** - Sending LLMs to different URLs
- **Multiple redirects** - Causing LLM crawlers to give up
- **Missing structured data** - Reducing AI understanding

## 🚨 **Troubleshooting**

### **Common Issues**

**"ModuleNotFoundError: No module named 'src'"**
- The app should handle this automatically
- If it persists, ensure you're running from the WebsiteVisability directory

**"Port 8501 is already in use"**
- Kill existing Streamlit processes: `taskkill /F /IM streamlit.exe`
- Or use a different port: `streamlit run app/main.py --server.port 8502`

**"curl command not available"**
- The app automatically falls back to requests library
- No action needed - verification will still work

**"Verification failed"**
- Check your internet connection
- Verify the URL is accessible
- Try a different URL to test

### **Getting Help**

1. **Check the Debug Information** - Expand debug sections for error details
2. **Review the Evidence Framework** - Use systematic evidence collection
3. **Test with Different URLs** - Verify the tool works with other sites
4. **Check Network Connectivity** - Ensure you can access the target website

## 📚 **Documentation**

- **[URL Redirect Verification Guide](URL_REDIRECT_VERIFICATION.md)** - Complete guide to testing redirects
- **[Project Analysis Summary](PROJECT_ANALYSIS_SUMMARY.md)** - Technical overview of the analysis engine
- **[Enhancement Backlog](ENHANCEMENT_BACKLOG.md)** - Future development plans
- **[Enhancement Checklist](ENHANCEMENT_CHECKLIST.md)** - Implementation guide

## 🤝 **Contributing**

We welcome contributions! Please see our enhancement backlog for areas where help is needed.

## 📄 **License**

This project is open source. Please check the repository for license details.

## 🆘 **Support**

For issues, questions, or feature requests, please open an issue in the GitHub repository.

---

**WebsiteVisability** - Making your website visible to AI search engines.