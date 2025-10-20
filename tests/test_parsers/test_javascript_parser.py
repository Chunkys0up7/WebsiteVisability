"""
Unit tests for JavaScriptParser
"""

import pytest
from src.parsers.javascript_parser import JavaScriptParser
from src.models.analysis_result import JavaScriptAnalysis, JavaScriptFramework


class TestJavaScriptParser:
    """Test suite for JavaScriptParser class"""
    
    @pytest.fixture
    def basic_script_html(self):
        """HTML with basic scripts"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://example.com/script.js"></script>
            <script>
                console.log('Inline script');
            </script>
        </head>
        <body>
            <script src="https://example.com/another.js"></script>
        </body>
        </html>
        """
    
    @pytest.fixture
    def react_html(self):
        """HTML with React"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
            <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
        </head>
        <body>
            <div id="root" data-reactroot></div>
            <script>
                ReactDOM.render(<App />, document.getElementById('root'));
            </script>
        </body>
        </html>
        """
    
    @pytest.fixture
    def vue_html(self):
        """HTML with Vue.js"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.jsdelivr.net/npm/vue@3/dist/vue.global.js"></script>
        </head>
        <body>
            <div id="app">
                <p v-if="seen">Now you see me</p>
                <input v-model="message">
            </div>
            <script>
                new Vue({
                    el: '#app',
                    data: { message: 'Hello' }
                });
            </script>
        </body>
        </html>
        """
    
    @pytest.fixture
    def angular_html(self):
        """HTML with Angular"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.8.2/angular.min.js"></script>
        </head>
        <body ng-app="myApp">
            <div ng-controller="myCtrl">
                <p>{{ message }}</p>
                <input ng-model="name">
            </div>
        </body>
        </html>
        """
    
    @pytest.fixture
    def jquery_html(self):
        """HTML with jQuery"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        </head>
        <body>
            <script>
                $(document).ready(function() {
                    $('p').click(function() {
                        $(this).hide();
                    });
                });
            </script>
        </body>
        </html>
        """
    
    @pytest.fixture
    def nextjs_html(self):
        """HTML with Next.js"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <script id="__NEXT_DATA__" type="application/json">
                {"props": {"pageProps": {}}}
            </script>
        </head>
        <body>
            <div id="__next"></div>
            <script src="/_next/static/chunks/main.js"></script>
        </body>
        </html>
        """
    
    @pytest.fixture
    def spa_html(self):
        """HTML with SPA pattern"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>SPA App</title>
        </head>
        <body>
            <div id="app"></div>
            <script src="/js/app.js"></script>
        </body>
        </html>
        """
    
    @pytest.fixture
    def ajax_html(self):
        """HTML with AJAX"""
        return """
        <!DOCTYPE html>
        <html>
        <body>
            <script>
                fetch('/api/data')
                    .then(response => response.json())
                    .then(data => console.log(data));
                
                const xhr = new XMLHttpRequest();
                xhr.open('GET', '/api/users');
            </script>
        </body>
        </html>
        """
    
    @pytest.fixture
    def no_javascript_html(self):
        """HTML with no JavaScript"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Plain HTML</title>
        </head>
        <body>
            <p>No JavaScript here</p>
        </body>
        </html>
        """
    
    def test_parser_initialization(self, basic_script_html):
        """Test parser initializes correctly"""
        parser = JavaScriptParser(basic_script_html)
        assert parser.soup is not None
        assert parser.html_content == basic_script_html
    
    def test_count_scripts(self, basic_script_html):
        """Test script counting"""
        parser = JavaScriptParser(basic_script_html)
        counts = parser.count_scripts()
        
        assert counts['total'] == 3
        assert counts['inline'] == 1
        assert counts['external'] == 2
    
    def test_count_scripts_no_javascript(self, no_javascript_html):
        """Test script counting with no JavaScript"""
        parser = JavaScriptParser(no_javascript_html)
        counts = parser.count_scripts()
        
        assert counts['total'] == 0
        assert counts['inline'] == 0
        assert counts['external'] == 0
    
    def test_detect_react(self, react_html):
        """Test React detection"""
        parser = JavaScriptParser(react_html)
        frameworks = parser.detect_frameworks()
        
        react = next((fw for fw in frameworks if fw.name == 'React'), None)
        assert react is not None
        assert react.confidence > 0
        assert len(react.indicators) > 0
    
    def test_detect_vue(self, vue_html):
        """Test Vue.js detection"""
        parser = JavaScriptParser(vue_html)
        frameworks = parser.detect_frameworks()
        
        vue = next((fw for fw in frameworks if fw.name == 'Vue'), None)
        assert vue is not None
        assert vue.confidence > 0
    
    def test_detect_angular(self, angular_html):
        """Test Angular detection"""
        parser = JavaScriptParser(angular_html)
        frameworks = parser.detect_frameworks()
        
        angular = next((fw for fw in frameworks if fw.name == 'Angular'), None)
        assert angular is not None
        assert angular.confidence > 0
    
    def test_detect_jquery(self, jquery_html):
        """Test jQuery detection"""
        parser = JavaScriptParser(jquery_html)
        frameworks = parser.detect_frameworks()
        
        jquery = next((fw for fw in frameworks if fw.name == 'jQuery'), None)
        assert jquery is not None
        assert jquery.confidence > 0
    
    def test_detect_nextjs(self, nextjs_html):
        """Test Next.js detection"""
        parser = JavaScriptParser(nextjs_html)
        frameworks = parser.detect_frameworks()
        
        nextjs = next((fw for fw in frameworks if fw.name == 'Next.js'), None)
        assert nextjs is not None
        assert nextjs.confidence > 0
    
    def test_no_frameworks_detected(self, no_javascript_html):
        """Test no frameworks detected"""
        parser = JavaScriptParser(no_javascript_html)
        frameworks = parser.detect_frameworks()
        
        assert len(frameworks) == 0
    
    def test_detect_spa_patterns_positive(self, spa_html):
        """Test SPA pattern detection - positive case"""
        parser = JavaScriptParser(spa_html)
        is_spa = parser.detect_spa_patterns()
        
        assert is_spa is True
    
    def test_detect_spa_patterns_react(self, react_html):
        """Test SPA pattern detection with React"""
        parser = JavaScriptParser(react_html)
        is_spa = parser.detect_spa_patterns()
        
        assert is_spa is True
    
    def test_detect_spa_patterns_negative(self, no_javascript_html):
        """Test SPA pattern detection - negative case"""
        parser = JavaScriptParser(no_javascript_html)
        is_spa = parser.detect_spa_patterns()
        
        assert is_spa is False
    
    def test_detect_ajax_usage_positive(self, ajax_html):
        """Test AJAX detection - positive case"""
        parser = JavaScriptParser(ajax_html)
        has_ajax = parser.detect_ajax_usage()
        
        assert has_ajax is True
    
    def test_detect_ajax_usage_negative(self, no_javascript_html):
        """Test AJAX detection - negative case"""
        parser = JavaScriptParser(no_javascript_html)
        has_ajax = parser.detect_ajax_usage()
        
        assert has_ajax is False
    
    def test_detect_dynamic_content_spa_framework(self, react_html):
        """Test dynamic content detection with SPA framework"""
        parser = JavaScriptParser(react_html)
        is_dynamic = parser.detect_dynamic_content()
        
        assert is_dynamic is True
    
    def test_detect_dynamic_content_ajax(self, ajax_html):
        """Test dynamic content detection with AJAX"""
        parser = JavaScriptParser(ajax_html)
        is_dynamic = parser.detect_dynamic_content()
        
        assert is_dynamic is True
    
    def test_detect_dynamic_content_negative(self, no_javascript_html):
        """Test dynamic content detection - negative case"""
        parser = JavaScriptParser(no_javascript_html)
        is_dynamic = parser.detect_dynamic_content()
        
        assert is_dynamic is False
    
    def test_get_external_script_sources(self, basic_script_html):
        """Test extraction of external script sources"""
        parser = JavaScriptParser(basic_script_html)
        sources = parser.get_external_script_sources()
        
        assert len(sources) == 2
        assert 'https://example.com/script.js' in sources
        assert 'https://example.com/another.js' in sources
    
    def test_analyze_complete(self, react_html):
        """Test complete analysis"""
        parser = JavaScriptParser(react_html)
        analysis = parser.analyze()
        
        assert isinstance(analysis, JavaScriptAnalysis)
        assert analysis.total_scripts > 0
        assert len(analysis.frameworks) > 0
        assert analysis.is_spa is True
        assert analysis.dynamic_content_detected is True
    
    def test_analyze_no_javascript(self, no_javascript_html):
        """Test analysis with no JavaScript"""
        parser = JavaScriptParser(no_javascript_html)
        analysis = parser.analyze()
        
        assert analysis.total_scripts == 0
        assert len(analysis.frameworks) == 0
        assert analysis.is_spa is False
        assert analysis.has_ajax is False
        assert analysis.dynamic_content_detected is False
    
    def test_multiple_frameworks(self):
        """Test detection of multiple frameworks"""
        html = """
        <html>
        <head>
            <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
            <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
        </head>
        <body>
            <div id="root" data-reactroot></div>
            <script>
                jQuery(document).ready();
                ReactDOM.render();
            </script>
        </body>
        </html>
        """
        parser = JavaScriptParser(html)
        frameworks = parser.detect_frameworks()
        
        assert len(frameworks) >= 2
        framework_names = [fw.name for fw in frameworks]
        assert 'React' in framework_names
        assert 'jQuery' in framework_names
    
    def test_framework_confidence_sorting(self):
        """Test frameworks are sorted by confidence"""
        html = """
        <html>
        <head>
            <script src="/react.js"></script>
        </head>
        <body>
            <div data-reactroot id="root"></div>
            <script>ReactDOM.render();</script>
        </body>
        </html>
        """
        parser = JavaScriptParser(html)
        frameworks = parser.detect_frameworks()
        
        if len(frameworks) > 1:
            for i in range(len(frameworks) - 1):
                assert frameworks[i].confidence >= frameworks[i + 1].confidence
    
    def test_empty_script_tags(self):
        """Test handling of empty script tags"""
        html = """
        <html>
        <body>
            <script></script>
            <script src="test.js"></script>
        </body>
        </html>
        """
        parser = JavaScriptParser(html)
        counts = parser.count_scripts()
        
        assert counts['total'] == 2
        assert counts['external'] == 1
    
    def test_script_type_application_json(self):
        """Test scripts with type='application/json' are counted"""
        html = """
        <html>
        <body>
            <script type="application/json">{"data": "value"}</script>
            <script>console.log('test');</script>
        </body>
        </html>
        """
        parser = JavaScriptParser(html)
        counts = parser.count_scripts()
        
        assert counts['total'] == 2
    
    def test_malformed_html(self):
        """Test handling of malformed HTML"""
        malformed = "<html><script src='test.js'><body>Content"
        parser = JavaScriptParser(malformed)
        
        # Should not raise exception
        counts = parser.count_scripts()
        assert isinstance(counts, dict)
    
    def test_empty_html(self):
        """Test handling of empty HTML"""
        parser = JavaScriptParser("")
        analysis = parser.analyze()
        
        assert analysis.total_scripts == 0
        assert len(analysis.frameworks) == 0
    
    def test_case_insensitive_framework_detection(self):
        """Test framework detection is case-insensitive"""
        html = """
        <html>
        <body>
            <script>
                JQUERY('div').hide();
            </script>
        </body>
        </html>
        """
        parser = JavaScriptParser(html)
        frameworks = parser.detect_frameworks()
        
        jquery = next((fw for fw in frameworks if fw.name == 'jQuery'), None)
        assert jquery is not None
    
    def test_axios_ajax_detection(self):
        """Test detection of axios for AJAX"""
        html = """
        <html>
        <body>
            <script>
                axios.get('/api/data').then(response => {});
            </script>
        </body>
        </html>
        """
        parser = JavaScriptParser(html)
        has_ajax = parser.detect_ajax_usage()
        
        assert has_ajax is True
    
    def test_framework_indicators_limited(self):
        """Test framework indicators are limited to 5"""
        html = """
        <html>
        <head>
            <script src="/react.js"></script>
        </head>
        <body>
            <div data-reactroot data-reactid id="root"></div>
            <script>
                ReactDOM.render();
                React.Component;
                _reactRootContainer;
            </script>
        </body>
        </html>
        """
        parser = JavaScriptParser(html)
        frameworks = parser.detect_frameworks()
        
        react = next((fw for fw in frameworks if fw.name == 'React'), None)
        if react:
            assert len(react.indicators) <= 5
    
    def test_svelte_detection(self):
        """Test Svelte detection"""
        html = """
        <html>
        <head>
            <script src="/build/bundle.js"></script>
        </head>
        <body>
            <script>
                // Svelte component
                const _svelte = true;
            </script>
        </body>
        </html>
        """
        parser = JavaScriptParser(html)
        frameworks = parser.detect_frameworks()
        
        svelte = next((fw for fw in frameworks if fw.name == 'Svelte'), None)
        assert svelte is not None
    
    def test_alpine_detection(self):
        """Test Alpine.js detection"""
        html = """
        <html>
        <head>
            <script src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
        </head>
        <body>
            <div x-data="{ open: false }">
                <button x-bind:class="open ? 'active' : ''">Toggle</button>
            </div>
        </body>
        </html>
        """
        parser = JavaScriptParser(html)
        frameworks = parser.detect_frameworks()
        
        alpine = next((fw for fw in frameworks if fw.name == 'Alpine'), None)
        assert alpine is not None

