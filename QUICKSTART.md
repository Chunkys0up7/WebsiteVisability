# 🚀 WebsiteVisability Quick Start Guide

Get up and running with WebsiteVisability in 5 minutes!

## ⚡ **Super Quick Start**

### 1. **Install & Run**
```bash
git clone https://github.com/Chunkys0up7/WebsiteVisability.git
cd WebsiteVisability
pip install -r requirements.txt
streamlit run app/main.py
```

### 2. **Open Browser**
Navigate to: `http://localhost:8501`

### 3. **Test Your First URL**
1. Enter your website URL in the sidebar
2. Watch the automatic URL verification
3. Click "Run Comprehensive Analysis"
4. Check the "URL Verification" tab for results

## 🎯 **What You'll See**

### **Immediate URL Verification** (Sidebar)
```
🔍 LLM URL Verification
✅ Direct Access - No redirects detected
LLMs access the same URL as browsers (optimal)

✅ No User-Agent Redirect - GPTBot gets same URL
📄 Content: 15,432 bytes, 2,341 words
✅ Content accessible to LLMs
```

### **Analysis Results** (Main Tabs)
- **📊 Overview** - Overall analysis results
- **🤖 LLM Analysis** - LLM-specific insights  
- **👁️ LLM Visibility** - Evidence of what LLMs can see
- **🔍 URL Verification** - Detailed redirect analysis
- **💡 Recommendations** - Actionable improvements

## 🔍 **Key Features to Try**

### **URL Verification**
- **Automatic verification** when you enter a URL
- **Redirect chain analysis** - see where LLMs end up
- **User-agent redirect detection** - identify different URLs for LLMs
- **Content accessibility** - verify LLMs can read your content

### **LLM Visibility Analysis**
- **Raw content preview** - see exactly what LLMs receive
- **JavaScript dependency detection** - find hidden content
- **Evidence-based analysis** - concrete proof of visibility
- **Technical recommendations** - actionable improvements

### **Evidence Framework**
- **Gold Standard Evidence** - direct proof of accessibility
- **Business Impact Analysis** - quantified impact on AI search
- **Competitive Context** - how you compare to competitors
- **Export Reports** - download analysis results

## 📊 **Understanding Results**

### **URL Verification Status**
- **✅ Direct Access** - No redirects (optimal)
- **🔄 Single Redirect** - One redirect (acceptable)
- **⚠️ Multiple Redirects** - Multiple hops (may cause issues)
- **🚨 User-Agent Redirect** - Different URL for LLMs (needs verification)

### **LLM Visibility Evidence**
- **Raw content preview** - First 1000 characters LLMs see
- **Content statistics** - Word count, accessibility metrics
- **JavaScript evidence** - Detection of script dependencies
- **Meta data analysis** - Title, description, structured data

## 🎯 **Common Scenarios**

### **E-commerce Site**
1. Enter your product page URL
2. Check if product descriptions are accessible
3. Verify pricing and specifications are visible
4. Test redirect configurations

### **Content/Blog Site**
1. Enter your article URL
2. Check if content is accessible to LLMs
3. Verify meta descriptions and titles
4. Test content loading mechanisms

### **SaaS Platform**
1. Enter your documentation URL
2. Check if docs are accessible to LLMs
3. Verify API documentation visibility
4. Test authentication flows

## 🚨 **Troubleshooting**

### **App Won't Start**
```bash
# Kill existing processes
taskkill /F /IM streamlit.exe

# Try different port
streamlit run app/main.py --server.port 8502
```

### **Verification Fails**
- Check internet connection
- Verify URL is accessible
- Try a different URL to test
- Check debug information in the app

### **Module Errors**
- Ensure you're in the WebsiteVisability directory
- Run: `pip install -r requirements.txt`
- The app should handle most import issues automatically

## 🎯 **Next Steps**

### **After Your First Analysis**
1. **Check the "URL Verification" tab** for detailed redirect analysis
2. **Review the "LLM Visibility" tab** for evidence of content accessibility
3. **Read the "Recommendations" tab** for actionable improvements
4. **Export your report** from the "Export Report" tab

### **Advanced Usage**
1. **Test multiple URLs** to understand your site's LLM visibility
2. **Use the Evidence Framework** for systematic analysis
3. **Compare with competitors** using the comparison feature
4. **Monitor regularly** to ensure ongoing LLM accessibility

## 📚 **Learn More**

- **[Complete README](README.md)** - Full documentation
- **[URL Redirect Verification Guide](URL_REDIRECT_VERIFICATION.md)** - Detailed redirect testing
- **[Project Analysis Summary](PROJECT_ANALYSIS_SUMMARY.md)** - Technical overview

## 🆘 **Need Help?**

1. **Check the Debug Information** in the app
2. **Review the Evidence Framework** for systematic analysis
3. **Open an issue** in the GitHub repository
4. **Test with different URLs** to verify functionality

---

**Ready to make your website visible to AI search engines?** 🚀
