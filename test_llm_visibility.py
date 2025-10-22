#!/usr/bin/env python3
"""
Test script for LLM Content Viewer

This script demonstrates the LLM content visibility functionality
by testing it with the Chase mortgage URL from the conversation.
"""

import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.analyzers.llm_content_viewer import LLMContentViewer

def test_chase_mortgage():
    """Test with the Chase mortgage URL from the conversation."""
    
    url = "https://www.chase.com/personal/mortgage-b"
    
    print("🔍 Testing LLM Content Visibility")
    print("=" * 50)
    print(f"URL: {url}")
    print()
    
    with LLMContentViewer() as viewer:
        # Test raw content fetching
        print("📄 Fetching raw content (what LLMs see)...")
        content_result = viewer.get_raw_llm_content(url)
        
        print(f"✅ Successfully fetched {content_result.character_count:,} characters")
        print(f"📊 Word count: {content_result.word_count:,}")
        print(f"🕒 Timestamp: {content_result.timestamp}")
        print(f"🤖 User Agent: {content_result.user_agent}")
        print()
        
        # Show first 500 characters of raw content
        print("📝 Raw Content Preview (First 500 characters):")
        print("-" * 50)
        preview = content_result.raw_content[:500]
        if len(content_result.raw_content) > 500:
            preview += "..."
        print(preview)
        print("-" * 50)
        print()
        
        # Test search simulation
        print("🔍 Testing search simulation...")
        search_results = viewer.simulate_llm_search("chase mortgage rates")
        
        print(f"✅ Generated {len(search_results)} search results")
        print()
        
        for i, result in enumerate(search_results, 1):
            print(f"Result {i}:")
            print(f"  Title: {result.title}")
            print(f"  URL: {result.url}")
            print(f"  Snippet: {result.snippet[:100]}...")
            print(f"  Relevance: {result.relevance_score:.2f}")
            print()
        
        # Test visibility analysis
        print("👁️ Testing visibility analysis...")
        visibility_analysis = viewer.analyze_llm_visibility(url)
        
        print(f"✅ Visibility Score: {visibility_analysis.visibility_score:.1f}/100")
        print()
        
        print("📊 Content Breakdown:")
        breakdown = visibility_analysis.content_breakdown
        print(f"  Total Content: {breakdown['total_content']:,} characters")
        print(f"  Visibility: {breakdown['visible_percentage']}%")
        print(f"  Content Type: {breakdown['content_type']}")
        print()
        
        print("❌ Hidden Content Issues:")
        hidden = visibility_analysis.hidden_content_summary
        for issue, status in hidden.items():
            status_icon = "⚠️" if status else "✅"
            print(f"  {status_icon} {issue.replace('_', ' ').title()}: {'Yes' if status else 'No'}")
        print()
        
        print("🎯 Recommendations:")
        for recommendation in visibility_analysis.recommendations:
            print(f"  • {recommendation}")
        print()
        
        print("✅ Test completed successfully!")

def test_generic_search():
    """Test with generic search queries."""
    
    print("\n🔍 Testing Generic Search Simulation")
    print("=" * 50)
    
    with LLMContentViewer() as viewer:
        queries = ["artificial intelligence", "mortgage rates", "web development"]
        
        for query in queries:
            print(f"\nSearch Query: '{query}'")
            results = viewer.simulate_llm_search(query, num_results=3)
            
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result.title}")
                print(f"     {result.snippet[:80]}...")
                print(f"     Relevance: {result.relevance_score:.2f}")

if __name__ == "__main__":
    try:
        test_chase_mortgage()
        test_generic_search()
        
        print("\n🎉 All tests completed successfully!")
        print("\nTo use this in the web application:")
        print("1. Run: streamlit run app/main.py")
        print("2. Navigate to the '👁️ LLM Visibility' tab")
        print("3. Enter a URL and click 'Analyze LLM Visibility'")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print("Make sure you have all required dependencies installed:")
        print("pip install -r requirements.txt")
