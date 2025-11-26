"""
H1.2 Main Dashboard - Comprehensive Test Suite

Tests verify:
- Route exists and requires authentication
- Template renders without errors
- CSS and JS files exist
- No fake data or placeholders
- Homepage integration complete
- Roadmap state updated
"""

import os
import pytest


class TestMainDashboardRoute:
    """Test the /main-dashboard route"""
    
    def test_route_exists_in_web_server(self):
        """Verify the route is defined in web_server.py"""
        with open('web_server.py', 'r', encoding='utf-8') as f:
            content = f.read()
            assert "@app.route('/main-dashboard')" in content, "Route /main-dashboard should exist"
            assert "def main_dashboard():" in content, "Function main_dashboard() should exist"
            assert "@login_required" in content, "Route should require authentication"
    
    def test_route_returns_correct_template(self):
        """Verify the route renders main_dashboard.html"""
        with open('web_server.py', 'r', encoding='utf-8') as f:
            content = f.read()
            # Find the main_dashboard function
            if "def main_dashboard():" in content:
                func_start = content.index("def main_dashboard():")
                func_section = content[func_start:func_start + 500]
                assert "render_template('main_dashboard.html')" in func_section, \
                    "Route should render main_dashboard.html"


class TestMainDashboardFiles:
    """Test that all required files exist"""
    
    def test_template_exists(self):
        """Verify main_dashboard.html template exists"""
        assert os.path.exists('templates/main_dashboard.html'), \
            "Template templates/main_dashboard.html should exist"
    
    def test_css_exists(self):
        """Verify main_dashboard.css exists"""
        assert os.path.exists('static/css/main_dashboard.css'), \
            "CSS file static/css/main_dashboard.css should exist"
    
    def test_js_exists(self):
        """Verify main_dashboard.js exists"""
        assert os.path.exists('static/js/main_dashboard.js'), \
            "JS file static/js/main_dashboard.js should exist"


class TestMainDashboardTemplate:
    """Test the template content"""
    
    def test_template_has_proper_structure(self):
        """Verify template has proper HTML structure"""
        with open('templates/main_dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
            assert '<!DOCTYPE html>' in content, "Template should have DOCTYPE"
            assert '<html' in content, "Template should have html tag"
            assert '<head>' in content, "Template should have head section"
            assert '<body>' in content, "Template should have body section"
    
    def test_template_links_css(self):
        """Verify template links to CSS file"""
        with open('templates/main_dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'main_dashboard.css' in content, "Template should link to main_dashboard.css"
    
    def test_template_links_js(self):
        """Verify template links to JS file"""
        with open('templates/main_dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'main_dashboard.js' in content, "Template should link to main_dashboard.js"
    
    def test_template_has_no_placeholders(self):
        """Verify template has no placeholder text"""
        with open('templates/main_dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read().lower()
            forbidden = ['lorem ipsum', 'placeholder', 'todo', 'fixme', 'coming soon']
            for word in forbidden:
                assert word not in content, f"Template should not contain '{word}'"
    
    def test_template_has_h1_components(self):
        """Verify template includes H1 dashboard components"""
        with open('templates/main_dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
            # Check for key sections
            required_sections = [
                'operational-topbar',  # System health
                'hero-grid',           # Two-column layout
                'analytics-grid'       # Lower analytics
            ]
            for section in required_sections:
                assert section in content, f"Template should contain {section} section"


class TestMainDashboardCSS:
    """Test the CSS file"""
    
    def test_css_has_color_scheme(self):
        """Verify CSS uses proper color scheme"""
        with open('static/css/main_dashboard.css', 'r', encoding='utf-8') as f:
            content = f.read()
            # Check for color variables
            assert ':root' in content or 'var(--' in content, \
                "CSS should use CSS variables or root colors"
    
    def test_css_has_responsive_design(self):
        """Verify CSS includes responsive design"""
        with open('static/css/main_dashboard.css', 'r', encoding='utf-8') as f:
            content = f.read()
            assert '@media' in content, "CSS should include media queries for responsive design"
    
    def test_css_has_no_fake_data(self):
        """Verify CSS has no fake data comments"""
        with open('static/css/main_dashboard.css', 'r', encoding='utf-8') as f:
            content = f.read().lower()
            forbidden = ['fake', 'dummy', 'test data', 'sample data']
            for word in forbidden:
                assert word not in content, f"CSS should not reference '{word}'"


class TestMainDashboardJS:
    """Test the JavaScript file"""
    
    def test_js_has_class_definition(self):
        """Verify JS defines MainDashboard class"""
        with open('static/js/main_dashboard.js', 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'class MainDashboard' in content or 'MainDashboard' in content, \
                "JS should define MainDashboard class or object"
    
    def test_js_has_error_handling(self):
        """Verify JS includes error handling"""
        with open('static/js/main_dashboard.js', 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'try' in content and 'catch' in content, \
                "JS should include try-catch error handling"
    
    def test_js_has_no_fake_data(self):
        """Verify JS doesn't generate fake data"""
        with open('static/js/main_dashboard.js', 'r', encoding='utf-8') as f:
            content = f.read().lower()
            forbidden = ['fake', 'dummy', 'lorem ipsum', 'test data', 'sample data', 'mock data']
            for word in forbidden:
                assert word not in content, f"JS should not contain '{word}'"
    
    def test_js_fetches_real_data(self):
        """Verify JS fetches from real API endpoints"""
        with open('static/js/main_dashboard.js', 'r', encoding='utf-8') as f:
            content = f.read()
            # Should fetch from real endpoints
            assert 'fetch(' in content or 'fetch (' in content, \
                "JS should fetch data from API endpoints"


class TestHomepageIntegration:
    """Test homepage integration"""
    
    def test_homepage_links_to_main_dashboard(self):
        """Verify homepage includes link to main dashboard"""
        with open('templates/homepage_video_background.html', 'r', encoding='utf-8') as f:
            content = f.read()
            assert '/main-dashboard' in content, \
                "Homepage should link to /main-dashboard"
    
    def test_homepage_has_main_dashboard_card(self):
        """Verify homepage has Main Dashboard card"""
        with open('templates/homepage_video_background.html', 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'Main Dashboard' in content, \
                "Homepage should have 'Main Dashboard' card"
            assert 'H1.2' in content or 'H1-2' in content, \
                "Homepage should reference H1.2 module"


class TestRoadmapState:
    """Test roadmap state update"""
    
    def test_h1_2_marked_complete(self):
        """Verify H1.2 is marked as complete in roadmap_state.py"""
        with open('roadmap_state.py', 'r', encoding='utf-8') as f:
            content = f.read()
            # Find h1_2_main_dashboard entry
            assert 'h1_2_main_dashboard' in content, \
                "roadmap_state.py should contain h1_2_main_dashboard key"
            
            # Check if it's marked as done
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'h1_2_main_dashboard' in line:
                    # Check this line and next few lines for "done": True
                    section = '\n'.join(lines[i:i+3])
                    assert '"done": True' in section, \
                        "h1_2_main_dashboard should be marked as done: True"
                    break


class TestNoDeprecatedReferences:
    """Test that no deprecated V2 references exist"""
    
    def test_no_v2_references_in_template(self):
        """Verify template doesn't reference deprecated V2 terminology"""
        with open('templates/main_dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read().lower()
            forbidden = ['signal lab v2', 'v2 dashboard', 'live-signals-v2']
            for phrase in forbidden:
                assert phrase not in content, \
                    f"Template should not reference deprecated '{phrase}'"
    
    def test_no_v2_references_in_js(self):
        """Verify JS doesn't reference deprecated V2 endpoints"""
        with open('static/js/main_dashboard.js', 'r', encoding='utf-8') as f:
            content = f.read().lower()
            # Should not call deprecated V2 endpoints
            forbidden = ['/api/live-signals-v2', 'signal_lab_v2']
            for phrase in forbidden:
                assert phrase not in content, \
                    f"JS should not reference deprecated '{phrase}'"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
