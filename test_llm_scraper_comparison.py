#!/usr/bin/env python3
"""
Test script for LLM vs Scraper Comparison

This script demonstrates the new comparison functionality that shows
the difference between what LLMs see versus what web scrapers see.
"""

import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.analyzers.llm_scraper_comparison import LLMScraperComparisonAnalyzer

def test_llm_scraper_comparison():
    """Test the LLM vs Scraper comparison with Chase mortgage URL."""
    
    url = "https://www.chase.com/personal/mortgage-b"
    
    print("🔄 Testing LLM vs Scraper Comparison")
    print("=" * 50)
    print(f"URL: {url}")
    print()
    
    with LLMScraperComparisonAnalyzer() as comparator:
        print("🔍 Comparing LLM vs Scraper content access...")
        comparison = comparator.compare_content_access(url)
        
        print(f"✅ Comparison complete!")
        print(f"📅 Analysis Time: {comparison.analysis_timestamp}")
        print()
        
        # Display comparison overview
        print("📊 Comparison Overview:")
        print(f"  LLM Visibility Score: {comparison.llm_visibility_score:.1f}/100")
        print(f"  Scraper Accessibility Score: {comparison.scraper_accessibility_score:.1f}/100")
        print(f"  Access Gap: {comparison.access_gap_score:.1f}")
        print()
        
        # Content volume comparison
        print("📄 Content Volume Comparison:")
        print(f"  LLM Characters: {comparison.llm_character_count:,}")
        print(f"  Scraper Characters: {comparison.scraper_character_count:,}")
        print(f"  Content Difference: {comparison.content_difference_percentage:.1f}%")
        print()
        
        # LLM limitations
        if comparison.llm_limitations:
            print("⚠️ LLM Limitations:")
            for limitation in comparison.llm_limitations:
                print(f"  • {limitation}")
        else:
            print("✅ No major LLM limitations detected")
        print()
        
        # Scraper capabilities
        if comparison.scraper_capabilities:
            print("✅ Scraper Capabilities:")
            for capability in comparison.scraper_capabilities:
                print(f"  • {capability}")
        else:
            print("ℹ️ Basic scraper access only")
        print()
        
        # Key differences
        if comparison.key_differences:
            print("🔍 Key Differences:")
            for difference in comparison.key_differences:
                print(f"  • {difference}")
        print()
        
        # Recommendations
        if comparison.recommendations:
            print("🎯 Recommendations:")
            for recommendation in comparison.recommendations:
                print(f"  • {recommendation}")
        print()
        
        # Content previews
        print("📝 Content Previews:")
        print()
        
        print("🤖 LLM Content (first 200 characters):")
        print("-" * 50)
        llm_preview = comparison.llm_content[:200]
        if len(comparison.llm_content) > 200:
            llm_preview += "..."
        print(llm_preview)
        print("-" * 50)
        print()
        
        print("🕷️ Scraper Content (first 200 characters):")
        print("-" * 50)
        scraper_preview = comparison.scraper_content[:200]
        if len(comparison.scraper_content) > 200:
            scraper_preview += "..."
        print(scraper_preview)
        print("-" * 50)
        print()
        
        print("✅ LLM vs Scraper comparison test completed successfully!")
        print()
        print("Key Insights:")
        print("• This shows exactly what each system can see from the same URL")
        print("• LLMs and scrapers often see different content due to JavaScript execution")
        print("• Understanding these differences helps optimize for both systems")

if __name__ == "__main__":
    try:
        test_llm_scraper_comparison()
        
        print("\n🎉 Test completed successfully!")
        print("\nTo use this in the web application:")
        print("1. Run: streamlit run app/main.py")
        print("2. Navigate to the '🔄 LLM vs Scraper Comparison' tab")
        print("3. Enter a URL and run the analysis")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print("Make sure you have all required dependencies installed:")
        print("pip install -r requirements.txt")
