# Web Scraper & LLM Analyzer - Quick Start
Write-Host "🔍 Web Scraper & LLM Analyzer - Quick Start" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Change to the correct directory
$targetDir = "C:\Users\camer\Projects\GitHub\WebKnowledge\web_scraper_llm_analyzer"
Set-Location $targetDir

Write-Host "📁 Current directory: $(Get-Location)" -ForegroundColor Green
Write-Host ""

# Check if the streamlined app exists
if (Test-Path "app\main_streamlined.py") {
    Write-Host "✅ Found streamlined application" -ForegroundColor Green
    Write-Host "🚀 Starting Streamlit application..." -ForegroundColor Yellow
    Write-Host "🌐 The application will open in your browser at http://localhost:8501" -ForegroundColor Cyan
    Write-Host "⏹️  Press Ctrl+C to stop the application" -ForegroundColor Red
    Write-Host ""
    
    # Start the application
    streamlit run app/main_streamlined.py
} else {
    Write-Host "❌ Error: app\main_streamlined.py not found" -ForegroundColor Red
    Write-Host "📁 Make sure you're in the correct directory:" -ForegroundColor Yellow
    Write-Host "   C:\Users\camer\Projects\GitHub\WebKnowledge\web_scraper_llm_analyzer" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to continue"
}
