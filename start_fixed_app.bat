@echo off
echo 🔍 Web Scraper ^& LLM Analyzer - Fixed Version
echo ================================================
echo.

REM Change to the correct directory
cd /d "C:\Users\camer\Projects\GitHub\WebKnowledge\web_scraper_llm_analyzer"

echo 📁 Current directory: %CD%
echo.

REM Check if the streamlined app exists
if exist "app\main_streamlined.py" (
    echo ✅ Found streamlined application
    echo 🔧 All errors have been fixed:
    echo    - URLValidator method name corrected
    echo    - SSRDetector method name corrected  
    echo    - AnalysisResult raw_html attribute fixed
    echo    - Score object attributes corrected
    echo.
    echo 🚀 Starting Streamlit application...
    echo 🌐 The application will open in your browser at http://localhost:8501
    echo ⏹️  Press Ctrl+C to stop the application
    echo.
    streamlit run app/main_streamlined.py
) else (
    echo ❌ Error: app\main_streamlined.py not found
    echo 📁 Make sure you're in the correct directory:
    echo    C:\Users\camer\Projects\GitHub\WebKnowledge\web_scraper_llm_analyzer
    echo.
    pause
)
