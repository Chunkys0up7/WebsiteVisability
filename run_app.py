#!/usr/bin/env python3
"""
Application Launcher

This script launches the Web Scraper & LLM Analyzer application.
"""

import subprocess
import sys

def main():
    """Launch the Streamlit application."""
    
    print("🔍 Web Scraper & LLM Analyzer")
    print("=" * 40)
    print()
    print("🚀 Launching application...")
    print("🌐 The application will open in your browser")
    print("⏹️  Press Ctrl+C to stop the application")
    print()
    
    try:
        # Run the Streamlit application
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app/main.py"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running application: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you're in the correct directory")
        print("2. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("3. Check that the file exists: app/main.py")

if __name__ == "__main__":
    main()
