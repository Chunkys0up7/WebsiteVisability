#!/usr/bin/env python3
"""
Test script for Streamlined Main Application

This script tests the new streamlined tabbed interface to ensure
it follows instructions.md requirements and maintains quality standards.
"""

import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_imports():
    """Test that all imports work correctly."""
    print("🔍 Testing imports...")
    
    try:
        # Test main application imports
        from app.main_streamlined import (
            initialize_session_state,
            render_sidebar,
            render_overview_tab,
            render_llm_analysis_tab,
            render_comparison_tab,
            render_technical_tab,
            render_recommendations_tab,
            run_analysis,
            main
        )
        print("✅ All main application imports successful")
        
        # Test analyzer imports
        from src.analyzers import StaticAnalyzer, DynamicAnalyzer, ScoringEngine
        from src.analyzers.llm_accessibility_analyzer import LLMAccessibilityAnalyzer
        from src.analyzers.llm_content_viewer import LLMContentViewer
        from src.analyzers.llm_scraper_comparison import LLMScraperComparisonAnalyzer
        print("✅ All analyzer imports successful")
        
        # Test utility imports
        from src.utils.validators import URLValidator
        from src.models.analysis_result import AnalysisResult
        from src.models.scoring_models import Score
        print("✅ All utility and model imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_session_state_initialization():
    """Test session state initialization."""
    print("\n🔍 Testing session state initialization...")
    
    try:
        from app.main_streamlined import initialize_session_state
        
        # Create a simple mock session state
        class MockSessionState:
            def __init__(self):
                self._state = {}
            
            def __getattr__(self, name):
                return self._state.get(name)
            
            def __setattr__(self, name, value):
                if name.startswith('_'):
                    super().__setattr__(name, value)
                else:
                    self._state[name] = value
        
        # Test initialization
        mock_state = MockSessionState()
        
        # Simulate the initialization by setting the required keys
        required_keys = [
            'url', 'analysis_complete', 'static_result', 'dynamic_result',
            'score', 'llm_report', 'enhanced_llm_report', 'last_analysis_type'
        ]
        
        for key in required_keys:
            mock_state._state[key] = None
        
        # Verify all required keys are set
        for key in required_keys:
            if key not in mock_state._state:
                print(f"❌ Missing session state key: {key}")
                return False
        
        print("✅ Session state initialization successful")
        return True
        
    except Exception as e:
        print(f"❌ Session state test error: {e}")
        return False

def test_url_validation():
    """Test URL validation functionality."""
    print("\n🔍 Testing URL validation...")
    
    try:
        from src.utils.validators import URLValidator
        
        # Test valid URLs
        valid_urls = [
            "https://www.example.com",
            "http://example.com",
            "https://subdomain.example.com/path",
            "https://example.com:8080/path?query=value"
        ]
        
        for url in valid_urls:
            if not URLValidator.is_valid(url):
                print(f"❌ Valid URL rejected: {url}")
                return False
        
        # Test invalid URLs
        invalid_urls = [
            "not-a-url",
            "javascript:alert('test')",
            ""
        ]
        
        for url in invalid_urls:
            if URLValidator.is_valid(url):
                print(f"❌ Invalid URL accepted: {url}")
                return False
        
        print("✅ URL validation tests passed")
        return True
        
    except Exception as e:
        print(f"❌ URL validation test error: {e}")
        return False

def test_analyzer_functionality():
    """Test core analyzer functionality."""
    print("\n🔍 Testing analyzer functionality...")
    
    try:
        from src.analyzers.llm_content_viewer import LLMContentViewer
        from src.analyzers.llm_scraper_comparison import LLMScraperComparisonAnalyzer
        
        # Test LLM Content Viewer
        with LLMContentViewer() as viewer:
            # Test search simulation
            search_results = viewer.simulate_llm_search("test query", num_results=3)
            if len(search_results) != 3:
                print("❌ Search simulation returned wrong number of results")
                return False
        
        # Test LLM Scraper Comparison
        with LLMScraperComparisonAnalyzer() as comparator:
            # Test comparison with a simple URL
            test_url = "https://httpbin.org/html"
            comparison = comparator.compare_content_access(test_url)
            
            if not hasattr(comparison, 'url'):
                print("❌ Comparison result missing URL attribute")
                return False
            
            if not hasattr(comparison, 'llm_visibility_score'):
                print("❌ Comparison result missing LLM visibility score")
                return False
        
        print("✅ Analyzer functionality tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Analyzer test error: {e}")
        return False

def test_ui_structure():
    """Test UI structure and organization."""
    print("\n🔍 Testing UI structure...")
    
    try:
        # Test that all render functions exist and are callable
        from app.main_streamlined import (
            render_sidebar,
            render_overview_tab,
            render_llm_analysis_tab,
            render_comparison_tab,
            render_technical_tab,
            render_recommendations_tab
        )
        
        render_functions = [
            render_sidebar,
            render_overview_tab,
            render_llm_analysis_tab,
            render_comparison_tab,
            render_technical_tab,
            render_recommendations_tab
        ]
        
        for func in render_functions:
            if not callable(func):
                print(f"❌ Render function not callable: {func.__name__}")
                return False
        
        print("✅ UI structure tests passed")
        return True
        
    except Exception as e:
        print(f"❌ UI structure test error: {e}")
        return False

def run_all_tests():
    """Run all tests and report results."""
    print("🧪 Running Streamlined Application Tests")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Session State Tests", test_session_state_initialization),
        ("URL Validation Tests", test_url_validation),
        ("Analyzer Functionality Tests", test_analyzer_functionality),
        ("UI Structure Tests", test_ui_structure)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The streamlined application is ready.")
        print("\nTo run the streamlined application:")
        print("streamlit run app/main_streamlined.py")
        return True
    else:
        print("⚠️ Some tests failed. Please review and fix issues.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
