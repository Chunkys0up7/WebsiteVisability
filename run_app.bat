@echo off
echo 🔍 Web Scraper ^& LLM Analyzer
echo ================================
echo.
echo Choose which version to run:
echo.
echo 1. 🆕 Streamlined Interface (Recommended)
echo    - Clean tabbed interface
echo    - Better organization
echo    - Improved user experience
echo.
echo 2. 📄 Original Interface
echo    - Long page layout
echo    - All features in one view
echo.
set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo 🚀 Launching Streamlined Interface...
    echo 📁 Running: app/main_streamlined.py
    echo 🌐 The application will open in your browser
    echo ⏹️  Press Ctrl+C to stop the application
    echo.
    streamlit run app/main_streamlined.py
) else if "%choice%"=="2" (
    echo.
    echo 🚀 Launching Original Interface...
    echo 📁 Running: app/main.py
    echo 🌐 The application will open in your browser
    echo ⏹️  Press Ctrl+C to stop the application
    echo.
    streamlit run app/main.py
) else (
    echo ❌ Invalid choice. Please run the script again and enter 1 or 2.
    pause
)