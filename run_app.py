#!/usr/bin/env python3
"""
Application Launcher

This script helps you run the correct Streamlit application.
"""

import subprocess
import sys
import os

def main():
    """Launch the appropriate Streamlit application."""
    
    print("🔍 Web Scraper & LLM Analyzer")
    print("=" * 40)
    print()
    print("Choose which version to run:")
    print()
    print("1. 🆕 Streamlined Interface (Recommended)")
    print("   - Clean tabbed interface")
    print("   - Better organization")
    print("   - Improved user experience")
    print()
    print("2. 📄 Original Interface")
    print("   - Long page layout")
    print("   - All features in one view")
    print()
    
    while True:
        choice = input("Enter your choice (1 or 2): ").strip()
        
        if choice == "1":
            app_file = "app/main_streamlined.py"
            print("\n🚀 Launching Streamlined Interface...")
            break
        elif choice == "2":
            app_file = "app/main.py"
            print("\n🚀 Launching Original Interface...")
            break
        else:
            print("❌ Invalid choice. Please enter 1 or 2.")
    
    print(f"📁 Running: {app_file}")
    print("🌐 The application will open in your browser")
    print("⏹️  Press Ctrl+C to stop the application")
    print()
    
    try:
        # Run the Streamlit application
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", app_file
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running application: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you're in the correct directory")
        print("2. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("3. Check that the file exists: app/main_streamlined.py")

if __name__ == "__main__":
    main()
