@echo off
REM Start the Web Scraper & LLM Analyzer application

echo.
echo ========================================
echo   Web Scraper ^& LLM Analyzer
echo ========================================
echo.

REM Check if virtual environment exists
if exist .venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo WARNING: Virtual environment not found!
    echo Please run: python -m venv .venv
    echo Then: .venv\Scripts\activate
    echo Then: pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo Starting application...
echo.
echo Press Ctrl+C to stop the application
echo.

REM Run the Streamlit application
python -m streamlit run app/main.py

pause
