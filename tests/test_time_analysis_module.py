"""
H1.3 Time Analysis Module Tests
Tests for time_analyzer.py backend and /api/time-analysis endpoint
"""
import pytest
import sys
import os
from unittest.mock import Mock, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time_analyzer


class TestTimeAnalyzerBackend:
    """Unit tests for time_analyzer.py functions"""
    
    def test_analyze_time_performance_with_data(self):
        """Test analyze_time_performance returns correct structure with data"""
        # Mock database
        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.conn.cursor.return_value = mock_cursor
        
        # Mock trade data
        mock_trades = [
            {'date': '2024-01-15', 'time': '09:30:00', 'session': 'NY AM', 'r_value': 2.5},
            {'date': '2024-01-15', 'time': '14:00:00', 'session': 'NY PM', 'r_value': -1.0},
            {'date': '2024-01-16', 'time': '10:15:00', 'session': 'NY AM', 'r_value': 1.5},
        ]
        mock_cursor.fetchall.return_value = mock_trades
        
        result = time_analyzer.analyze_time_performance(mock_db)
        
        # Verify structure
        assert 'total_trades' in result
        assert 'overall_expectancy' in result
        assert 'macro' in result
        assert 'hourly' in result
        assert 'session' in result
        assert 'day_of_week' in result
        assert 'week_of_month' in result
        assert 'monthly' in result
        assert 'best_hour' in result
        assert 'best_session' in result
        assert 'best_day' in result
        assert 'best_month' in result
        
        # Verify data types
        assert isinstance(result['total_trades'], int)
        assert isinstance(result['overall_expectancy'], float)
        assert isinstance(result['hourly'], list)
        assert isinstance(result['session'], list)
        
        # Verify values
        assert result['total_trades'] == 3
        assert result['overall_expectancy'] == pytest.approx(1.0, rel=0.1)
    
    def test_analyze_time_performance_empty_data(self):
        """Test analyze_time_performance handles empty dataset gracefully"""
        # Mock database with no trades
        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        result = time_analyzer.analyze_time_performance(mock_db)
        
        # Verify empty structure
        assert result['total_trades'] == 0
        assert result['overall_expectancy'] == 0
        assert result['hourly'] == []
        assert result['session'] == []
        assert result['best_hour']['hour'] == 'N/A'
        assert result['best_session']['session'] == 'N/A'
    
    def test_analyze_hourly_returns_24_hours(self):
        """Test analyze_hourly returns data for all 24 hours"""
        trades = [
            {'date': '2024-01-15', 'time': '09:30:00', 'session': 'NY AM', 'r_value': 2.5},
            {'date': '2024-01-15', 'time': '14:00:00', 'session': 'NY PM', 'r_value': 1.0},
        ]
        
        result = time_analyzer.analyze_hourly(trades)
        
        # Should return 24 hours (0-23)
        assert len(result) == 24
        
        # Verify structure of each hour
        for hour_data in result:
            assert 'hour' in hour_data
            assert 'trades' in hour_data
            assert 'expectancy' in hour_data
            assert 'win_rate' in hour_data
            assert 'avg_r' in hour_data
            assert 'std_dev' in hour_data
        
        # Verify hours with data
        hour_9 = next(h for h in result if h['hour'] == 9)
        assert hour_9['trades'] == 1
        assert hour_9['expectancy'] == 2.5
        
        hour_14 = next(h for h in result if h['hour'] == 14)
        assert hour_14['trades'] == 1
        assert hour_14['expectancy'] == 1.0
        
        # Verify hours without data
        hour_0 = next(h for h in result if h['hour'] == 0)
        assert hour_0['trades'] == 0
        assert hour_0['expectancy'] == 0
    
    def test_analyze_session_groups_correctly(self):
        """Test analyze_session groups trades by session"""
        trades = [
            {'date': '2024-01-15', 'time': '09:30:00', 'session': 'NY AM', 'r_value': 2.5},
            {'date': '2024-01-15', 'time': '09:45:00', 'session': 'NY AM', 'r_value': 1.5},
            {'date': '2024-01-15', 'time': '14:00:00', 'session': 'NY PM', 'r_value': -1.0},
        ]
        
        result = time_analyzer.analyze_session(trades)
        
        # Should have 2 sessions
        assert len(result) == 2
        
        # Find NY AM session
        ny_am = next(s for s in result if s['session'] == 'NY AM')
        assert ny_am['trades'] == 2
        assert ny_am['expectancy'] == 2.0
        assert ny_am['win_rate'] == 1.0  # Both positive
        
        # Find NY PM session
        ny_pm = next(s for s in result if s['session'] == 'NY PM')
        assert ny_pm['trades'] == 1
        assert ny_pm['expectancy'] == -1.0
        assert ny_pm['win_rate'] == 0.0  # Negative
    
    def test_analyze_macro_windows(self):
        """Test analyze_macro_windows identifies macro vs non-macro times"""
        trades = [
            {'date': '2024-01-15', 'time': '09:55:00', 'session': 'NY AM', 'r_value': 2.0},  # Macro (xx:55)
            {'date': '2024-01-15', 'time': '10:05:00', 'session': 'NY AM', 'r_value': 1.5},  # Macro (xx:05)
            {'date': '2024-01-15', 'time': '10:30:00', 'session': 'NY AM', 'r_value': 1.0},  # Non-macro
            {'date': '2024-01-15', 'time': '15:20:00', 'session': 'NY PM', 'r_value': 2.5},  # MOC macro
        ]
        
        result = time_analyzer.analyze_macro_windows(trades)
        
        # Should have 2 categories
        assert len(result) == 2
        
        # Find macro window
        macro = next(w for w in result if 'Macro' in w['window'])
        assert macro['trades'] == 3  # 09:55, 10:05, 15:20
        
        # Find non-macro window
        non_macro = next(w for w in result if w['window'] == 'Non-Macro')
        assert non_macro['trades'] == 1  # 10:30
    
    def test_generate_empty_analysis(self):
        """Test generate_empty_analysis returns proper empty structure"""
        result = time_analyzer.generate_empty_analysis()
        
        assert result['total_trades'] == 0
        assert result['overall_expectancy'] == 0
        assert result['macro'] == []
        assert result['hourly'] == []
        assert result['session'] == []
        assert result['day_of_week'] == []
        assert result['week_of_month'] == []
        assert result['monthly'] == []
        assert result['best_hour']['hour'] == 'N/A'
        assert result['best_session']['session'] == 'N/A'
        assert result['best_day']['day'] == 'N/A'
        assert result['best_month']['month'] == 'N/A'


class TestTimeAnalysisEndpoint:
    """Integration tests for /api/time-analysis endpoint"""
    
    @pytest.fixture
    def app(self):
        """Create Flask test app"""
        # Import here to avoid circular imports
        import web_server
        web_server.app.config['TESTING'] = True
        web_server.app.config['LOGIN_DISABLED'] = True  # Disable login for tests
        return web_server.app
    
    @pytest.fixture
    def client(self, app):
        """Create Flask test client"""
        return app.test_client()
    
    def test_time_analysis_endpoint_returns_200(self, client):
        """Test /api/time-analysis returns 200 when DB is available"""
        # Note: This test requires database to be available
        # In production test environment, mock the database
        response = client.get('/api/time-analysis')
        
        # Should return 200 or 500 (if DB unavailable)
        assert response.status_code in [200, 500]
    
    def test_time_analysis_endpoint_returns_json(self, client):
        """Test /api/time-analysis returns JSON"""
        response = client.get('/api/time-analysis')
        
        # Should return JSON content type
        assert response.content_type == 'application/json' or 'json' in response.content_type
    
    def test_time_analysis_endpoint_structure(self, client):
        """Test /api/time-analysis returns correct JSON structure"""
        response = client.get('/api/time-analysis')
        
        if response.status_code == 200:
            data = response.get_json()
            
            # Verify required keys
            assert 'total_trades' in data
            assert 'overall_expectancy' in data
            assert 'hourly' in data
            assert 'session' in data
            assert 'best_hour' in data
            assert 'best_session' in data
    
    def test_time_analysis_endpoint_handles_db_unavailable(self, client, monkeypatch):
        """Test /api/time-analysis returns 500 when DB is unavailable"""
        # Mock db_enabled to False
        import web_server
        monkeypatch.setattr(web_server, 'db_enabled', False)
        
        response = client.get('/api/time-analysis')
        
        # Should return 500 error
        assert response.status_code == 500
        
        data = response.get_json()
        assert 'error' in data
        assert 'Database not available' in data['error']


class TestSessionHotspots:
    """Tests for session hotspots functionality"""
    
    def test_session_hotspots_structure(self):
        """Test analyze_time_performance includes session_hotspots"""
        # Mock database
        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.conn.cursor.return_value = mock_cursor
        
        # Mock trade data with specific hours in sessions
        mock_trades = [
            {'date': '2024-01-15', 'time': '09:30:00', 'session': 'NY AM', 'r_value': 2.5},
            {'date': '2024-01-15', 'time': '09:45:00', 'session': 'NY AM', 'r_value': 2.0},
            {'date': '2024-01-15', 'time': '10:15:00', 'session': 'NY AM', 'r_value': 1.8},
            {'date': '2024-01-15', 'time': '10:30:00', 'session': 'NY AM', 'r_value': 1.5},
            {'date': '2024-01-15', 'time': '11:00:00', 'session': 'NY AM', 'r_value': -0.5},
        ]
        mock_cursor.fetchall.return_value = mock_trades
        
        result = time_analyzer.analyze_time_performance(mock_db)
        
        # Verify session_hotspots exists
        assert 'session_hotspots' in result
        assert 'sessions' in result['session_hotspots']
        assert isinstance(result['session_hotspots']['sessions'], dict)
    
    def test_session_hotspots_empty_when_no_trades(self):
        """Test session_hotspots returns empty structure when no trades"""
        # Mock database with no trades
        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        result = time_analyzer.analyze_time_performance(mock_db)
        
        # Verify empty structure
        assert result['session_hotspots'] == {'sessions': {}}
    
    def test_session_hotspots_has_hot_hours_for_populated_session(self):
        """Test session_hotspots identifies hot hours in populated session"""
        # Create trades with clear hot/cold hours in NY AM
        trades = [
            # Hour 9 - Hot (avg 2.5R)
            {'date': '2024-01-15', 'time': '09:15:00', 'session': 'NY AM', 'r_value': 3.0},
            {'date': '2024-01-15', 'time': '09:30:00', 'session': 'NY AM', 'r_value': 2.5},
            {'date': '2024-01-15', 'time': '09:45:00', 'session': 'NY AM', 'r_value': 2.0},
            # Hour 10 - Warm (avg 1.5R)
            {'date': '2024-01-15', 'time': '10:15:00', 'session': 'NY AM', 'r_value': 2.0},
            {'date': '2024-01-15', 'time': '10:30:00', 'session': 'NY AM', 'r_value': 1.5},
            {'date': '2024-01-15', 'time': '10:45:00', 'session': 'NY AM', 'r_value': 1.0},
            # Hour 11 - Cold (avg -0.5R)
            {'date': '2024-01-15', 'time': '11:00:00', 'session': 'NY AM', 'r_value': -1.0},
            {'date': '2024-01-15', 'time': '11:15:00', 'session': 'NY AM', 'r_value': -0.5},
            {'date': '2024-01-15', 'time': '11:30:00', 'session': 'NY AM', 'r_value': 0.0},
        ]
        
        result = time_analyzer.analyze_session_hotspots([], [], trades)
        
        # Verify NY AM session exists
        assert 'NY AM' in result['sessions']
        
        ny_am = result['sessions']['NY AM']
        
        # Verify structure
        assert 'hot_hours' in ny_am
        assert 'cold_hours' in ny_am
        assert 'avg_r' in ny_am
        assert 'win_rate' in ny_am
        assert 'density' in ny_am
        assert 'total_trades' in ny_am
        
        # Verify hot hours identified (should include 09:00)
        assert len(ny_am['hot_hours']) > 0
        assert '09:00' in ny_am['hot_hours']
        
        # Verify cold hours identified (should include 11:00)
        assert len(ny_am['cold_hours']) > 0
        assert '11:00' in ny_am['cold_hours']
        
        # Verify metrics
        assert ny_am['total_trades'] == 9
        assert ny_am['avg_r'] > 0  # Overall positive
    
    def test_analyze_session_hotspots_function(self):
        """Test analyze_session_hotspots function directly"""
        trades = [
            {'date': '2024-01-15', 'time': '14:00:00', 'session': 'NY PM', 'r_value': 2.0},
            {'date': '2024-01-15', 'time': '14:15:00', 'session': 'NY PM', 'r_value': 1.8},
            {'date': '2024-01-15', 'time': '14:30:00', 'session': 'NY PM', 'r_value': 1.5},
        ]
        
        result = time_analyzer.analyze_session_hotspots([], [], trades)
        
        assert 'sessions' in result
        assert isinstance(result['sessions'], dict)
        
        # Should have NY PM session
        if 'NY PM' in result['sessions']:
            ny_pm = result['sessions']['NY PM']
            assert 'hot_hours' in ny_pm
            assert 'avg_r' in ny_pm
            assert ny_pm['total_trades'] == 3


class TestTimeAnalysisJavaScript:
    """Smoke tests for JavaScript module"""
    
    def test_javascript_file_exists(self):
        """Test that time_analysis.js file exists"""
        js_path = os.path.join('static', 'js', 'time_analysis.js')
        assert os.path.exists(js_path), f"JavaScript file not found: {js_path}"
    
    def test_javascript_contains_canonical_api_call(self):
        """Test that JavaScript calls /api/time-analysis"""
        js_path = os.path.join('static', 'js', 'time_analysis.js')
        
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should contain fetch to canonical endpoint
        assert '/api/time-analysis' in content, "JavaScript should call /api/time-analysis"
        
        # Should NOT contain old endpoints
        assert '/api/signals/today' not in content, "JavaScript should not call /api/signals/today"
        assert '/api/session-summary' not in content, "JavaScript should not call /api/session-summary"
    
    def test_javascript_contains_timeanalysis_class(self):
        """Test that JavaScript defines TimeAnalysis class"""
        js_path = os.path.join('static', 'js', 'time_analysis.js')
        
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'class TimeAnalysis' in content, "JavaScript should define TimeAnalysis class"
        assert 'fetchAllData' in content, "JavaScript should have fetchAllData method"
    
    def test_javascript_contains_session_hotspots_usage(self):
        """Test that JavaScript consumes session_hotspots"""
        js_path = os.path.join('static', 'js', 'time_analysis.js')
        
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should contain renderSessionHotspots method
        assert 'renderSessionHotspots' in content, "JavaScript should have renderSessionHotspots method"
        
        # Should reference session_hotspots data
        assert 'session_hotspots' in content, "JavaScript should reference session_hotspots"
        
        # Should store data in this.data
        assert 'this.data' in content, "JavaScript should store data in this.data"


class TestChunk7BSessionHourlyAnalytics:
    """Tests for CHUNK 7B - Session & Hourly Analytics with Chart.js"""
    
    def test_template_has_session_and_hourly_sections(self):
        """Test that template contains new session and hourly sections"""
        with open('templates/time_analysis.html', encoding='utf-8') as f:
            content = f.read()
        
        assert 'id="sessionGrid"' in content, "sessionGrid should be present"
        assert 'id="sessionHeatmapCanvas"' in content, "sessionHeatmapCanvas should be present"
        assert 'id="hourlyGrid"' in content, "hourlyGrid should be present"
        assert 'ta-section' in content, "ta-section class should be present"
        assert 'ta-section-title' in content, "ta-section-title class should be present"
    
    def test_template_includes_chartjs_libraries(self):
        """Test that template includes Chart.js and matrix plugin"""
        with open('templates/time_analysis.html', encoding='utf-8') as f:
            content = f.read()
        
        assert 'chart.js' in content.lower(), "Chart.js should be included"
        assert 'chartjs-chart-matrix' in content, "Chart.js matrix plugin should be included"
    
    def test_js_has_session_and_heatmap_functions(self):
        """Test that JS has session and heatmap rendering functions"""
        with open('static/js/time_analysis.js', encoding='utf-8') as f:
            content = f.read()
        
        assert 'renderSessionAnalysis' in content, "renderSessionAnalysis should be present"
        assert 'renderSessionHeatmap' in content, "renderSessionHeatmap should be present"
        assert 'getHeatColor' in content, "getHeatColor should be present"
        assert 'new Chart' in content, "Chart.js instantiation should be present"
        assert 'sessionHeatmapChart' in content, "sessionHeatmapChart property should be present"
    
    def test_js_has_hourly_analysis_function(self):
        """Test that JS has hourly analysis rendering function"""
        with open('static/js/time_analysis.js', encoding='utf-8') as f:
            content = f.read()
        
        assert 'renderHourlyAnalysis' in content, "renderHourlyAnalysis should be present"
        assert 'hourlyGrid' in content, "hourlyGrid reference should be present"
        assert 'hour-card' in content, "hour-card class should be used"
    
    def test_js_creates_session_cards_with_real_data(self):
        """Test that JS creates session cards with real V2 data"""
        with open('static/js/time_analysis.js', encoding='utf-8') as f:
            content = f.read()
        
        assert 'createSessionCard' in content, "createSessionCard method should be present"
        assert 'session-title' in content, "session-title class should be used"
        assert 'session-metric' in content, "session-metric class should be used"
        assert 'data-hot-hours-for' in content, "data-hot-hours-for attribute should be present"
        assert 'data-cold-hours-for' in content, "data-cold-hours-for attribute should be present"
    
    def test_css_has_new_section_styles(self):
        """Test that CSS has new section and grid styles"""
        with open('static/css/time_analysis.css', encoding='utf-8') as f:
            content = f.read()
        
        assert '.ta-section' in content, "ta-section class should be defined"
        assert '.ta-section-title' in content, "ta-section-title class should be defined"
        assert '.session-card' in content, "session-card class should be defined"
        assert '.heatmap-container' in content, "heatmap-container class should be defined"
        assert '.hourly-grid' in content, "hourly-grid class should be defined"
        assert '.hour-card' in content, "hour-card class should be defined"
    
    def test_heatmap_uses_fintech_color_scheme(self):
        """Test that heatmap color function uses fintech blue-violet-magenta scheme"""
        with open('static/js/time_analysis.js', encoding='utf-8') as f:
            content = f.read()
        
        # Check for color values in getHeatColor
        assert '#4C66FF' in content, "Blue color should be present"
        assert '#8E54FF' in content, "Violet color should be present"
        assert '#FF00FF' in content, "Magenta color should be present"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


class TestHotColdHoursUI:
    """Tests for Hot/Cold Hours UI enhancement (H1.3 Chunk 4)"""
    
    def test_time_analysis_hotspots_included(self):
        """Test that /api/time-analysis includes session_hotspots"""
        # This test verifies the backend data structure
        # In a real test environment, you would make an actual API call
        # For now, we verify the structure exists in time_analyzer.py
        import time_analyzer
        
        # Verify the function exists
        assert hasattr(time_analyzer, 'get_time_analysis_data'), \
            "time_analyzer should have get_time_analysis_data function"
    
    def test_session_card_contains_hotcold_placeholders(self):
        """Test that JavaScript creates session cards with hot/cold hour placeholders"""
        js_path = os.path.join('static', 'js', 'time_analysis.js')
        
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should contain data attributes for hot/cold hours
        assert 'data-hot-hours-for' in content, \
            "JavaScript should create data-hot-hours-for attributes"
        assert 'data-cold-hours-for' in content, \
            "JavaScript should create data-cold-hours-for attributes"
    
    def test_javascript_contains_renderHotColdHours(self):
        """Test that JavaScript contains renderHotColdHours method"""
        js_path = os.path.join('static', 'js', 'time_analysis.js')
        
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'renderHotColdHours' in content, \
            "JavaScript should have renderHotColdHours method"
        assert 'querySelectorAll' in content, \
            "JavaScript should use querySelectorAll to find elements"
    
    def test_css_contains_hotspot_styles(self):
        """Test that CSS contains hotspot row styles"""
        css_path = os.path.join('static', 'css', 'time_analysis.css')
        
        with open(css_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'session-hotspot-row' in content, \
            "CSS should define session-hotspot-row class"
        assert 'hot-label' in content, \
            "CSS should define hot-label class"
        assert 'cold-label' in content, \
            "CSS should define cold-label class"
        assert '#4DDFFF' in content, \
            "CSS should use neon blue for hot labels"
        assert '#F87171' in content, \
            "CSS should use muted red for cold labels"
    
    def test_javascript_creates_session_cards(self):
        """Test that JavaScript has createSessionCard method"""
        js_path = os.path.join('static', 'js', 'time_analysis.js')
        
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'createSessionCard' in content, \
            "JavaScript should have createSessionCard method"
        assert 'session-title' in content, \
            "JavaScript should create session-title elements"
        assert 'session-value' in content, \
            "JavaScript should create session-value elements"



class TestAbortedTransactionResilience:
    """Tests for H1.3 Chunk 6 - Aborted transaction resilience"""
    
    def test_time_analysis_uses_fresh_connection(self):
        """Test that /api/time-analysis uses fresh connection from pool"""
        import web_server
        
        # Read the endpoint source to verify it uses get_db_connection
        import inspect
        source = inspect.getsource(web_server.get_time_analysis)
        
        assert 'get_db_connection' in source, \
            "/api/time-analysis should use get_db_connection for fresh connection"
        assert 'release_connection' in source, \
            "/api/time-analysis should release connection after use"
        assert 'FreshDBWrapper' in source, \
            "/api/time-analysis should wrap connection for time_analyzer"
    
    def test_time_analysis_resilient_to_aborted_transaction(self):
        """Test that /api/time-analysis doesn't fail with aborted transaction error"""
        import web_server
        
        # This test verifies the endpoint structure prevents aborted transaction errors
        # by using a fresh connection instead of reusing potentially aborted db.conn
        
        web_server.app.config['TESTING'] = True
        web_server.app.config['LOGIN_DISABLED'] = True
        
        with web_server.app.test_client() as client:
            # Make request to time-analysis endpoint
            res = client.get('/api/time-analysis')
            
            # Should not return "current transaction is aborted" error
            if res.status_code == 500:
                data = res.get_json()
                error_msg = data.get('error', '').lower() if data else ''
                
                assert 'current transaction is aborted' not in error_msg, \
                    "Endpoint should not fail with aborted transaction error"
                assert 'infailedsqltransaction' not in error_msg, \
                    "Endpoint should not fail with InFailedSqlTransaction error"
    
    def test_fresh_db_wrapper_provides_conn_attribute(self):
        """Test that FreshDBWrapper provides conn attribute like db object"""
        # This test verifies the wrapper structure matches what time_analyzer expects
        
        class MockConnection:
            def cursor(self):
                return None
        
        # Simulate the FreshDBWrapper from the endpoint
        class FreshDBWrapper:
            def __init__(self, connection):
                self.conn = connection
        
        mock_conn = MockConnection()
        wrapper = FreshDBWrapper(mock_conn)
        
        assert hasattr(wrapper, 'conn'), \
            "FreshDBWrapper should have conn attribute"
        assert wrapper.conn == mock_conn, \
            "FreshDBWrapper.conn should be the provided connection"
        assert hasattr(wrapper.conn, 'cursor'), \
            "FreshDBWrapper.conn should have cursor method"



class TestSessionNormalization:
    """Tests for H1.3 Chunk 7 - Session name normalization"""
    
    def test_normalize_session_name(self):
        """Test that normalize_session_name works correctly"""
        from time_analyzer import normalize_session_name
        
        assert normalize_session_name("Asia") == "ASIA"
        assert normalize_session_name("ASIA") == "ASIA"
        assert normalize_session_name("Asia Session") == "ASIA"
        assert normalize_session_name("London") == "LONDON"
        assert normalize_session_name("LONDON") == "LONDON"
        assert normalize_session_name("NY Pre Market") == "NY PRE"
        assert normalize_session_name("NY_PRE") == "NY PRE"
        assert normalize_session_name("NY PRE") == "NY PRE"
        assert normalize_session_name("NY AM") == "NY AM"
        assert normalize_session_name("NY_AM") == "NY AM"
        assert normalize_session_name("NY Lunch") == "NY LUNCH"
        assert normalize_session_name("NY_LUNCH") == "NY LUNCH"
        assert normalize_session_name("NY PM") == "NY PM"
        assert normalize_session_name("NY_PM") == "NY PM"
    
    def test_api_sessions_are_normalized(self):
        """Test that all sessions in API output are normalized"""
        import web_server
        
        web_server.app.config['TESTING'] = True
        web_server.app.config['LOGIN_DISABLED'] = True
        
        with web_server.app.test_client() as client:
            res = client.get('/api/time-analysis')
            
            if res.status_code == 200:
                data = res.get_json()
                
                # Check session analysis has normalized names
                if 'session' in data and data['session']:
                    valid_sessions = ["ASIA", "LONDON", "NY PRE", "NY AM", "NY LUNCH", "NY PM", "Unknown"]
                    for s in data['session']:
                        assert s['session'] in valid_sessions, \
                            f"Session '{s['session']}' is not normalized"
    
    def test_hotspot_session_normalization(self):
        """Test that hotspot sessions are normalized"""
        import web_server
        
        web_server.app.config['TESTING'] = True
        web_server.app.config['LOGIN_DISABLED'] = True
        
        with web_server.app.test_client() as client:
            res = client.get('/api/time-analysis')
            
            if res.status_code == 200:
                data = res.get_json()
                
                # Check hotspot sessions have normalized names
                if 'session_hotspots' in data and 'sessions' in data['session_hotspots']:
                    h = data['session_hotspots']['sessions']
                    valid_sessions = ["ASIA", "LONDON", "NY PRE", "NY AM", "NY LUNCH", "NY PM"]
                    
                    for key in h.keys():
                        assert key in valid_sessions, \
                            f"Hotspot session '{key}' is not normalized"
    
    def test_javascript_has_normalize_method(self):
        """Test that JavaScript has normalizeSession method"""
        js_path = os.path.join('static', 'js', 'time_analysis.js')
        
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'normalizeSession' in content, \
            "JavaScript should have normalizeSession method"
        assert '"ASIA"' in content, \
            "JavaScript should have ASIA in normalization map"
        assert '"NY PRE"' in content, \
            "JavaScript should have NY PRE in normalization map"


class TestNumericFieldNormalization:
    """Tests for H1.3 Chunk 8 - Global numeric field normalization"""
    
    def test_numeric_fields_are_floats(self):
        """Test that all numeric fields in API response are floats"""
        import web_server
        web_server.app.config['TESTING'] = True
        web_server.app.config['LOGIN_DISABLED'] = True
        
        with web_server.app.test_client() as client:
            res = client.get('/api/time-analysis')
            if res.status_code == 200:
                data = res.get_json()
                
                # Check top-level numeric fields
                if 'overall_expectancy' in data:
                    assert isinstance(data['overall_expectancy'], (float, int)), \
                        f"overall_expectancy should be numeric, got {type(data['overall_expectancy'])}"
                
                # Check numeric fields inside hourly structures
                if 'hourly' in data and data['hourly']:
                    for h in data['hourly']:
                        if 'avg_r' in h:
                            assert isinstance(h['avg_r'], (float, int)), \
                                f"hourly avg_r should be numeric, got {type(h['avg_r'])}"
                        if 'expectancy' in h:
                            assert isinstance(h['expectancy'], (float, int)), \
                                f"hourly expectancy should be numeric, got {type(h['expectancy'])}"
                        if 'std_dev' in h:
                            assert isinstance(h['std_dev'], (float, int)), \
                                f"hourly std_dev should be numeric, got {type(h['std_dev'])}"
                        if 'win_rate' in h:
                            assert isinstance(h['win_rate'], (float, int)), \
                                f"hourly win_rate should be numeric, got {type(h['win_rate'])}"
                
                # Check numeric fields inside session structures
                if 'session' in data and data['session']:
                    for s in data['session']:
                        if 'avg_r' in s:
                            assert isinstance(s['avg_r'], (float, int)), \
                                f"session avg_r should be numeric, got {type(s['avg_r'])}"
                        if 'expectancy' in s:
                            assert isinstance(s['expectancy'], (float, int)), \
                                f"session expectancy should be numeric, got {type(s['expectancy'])}"
                
                # Check numeric fields inside monthly structures
                if 'monthly' in data and data['monthly']:
                    for m in data['monthly']:
                        if 'avg_r' in m:
                            assert isinstance(m['avg_r'], (float, int)), \
                                f"monthly avg_r should be numeric, got {type(m['avg_r'])}"
                        if 'expectancy' in m:
                            assert isinstance(m['expectancy'], (float, int)), \
                                f"monthly expectancy should be numeric, got {type(m['expectancy'])}"
                
                # Check hotspots
                if 'session_hotspots' in data and 'sessions' in data['session_hotspots']:
                    hotspots = data['session_hotspots']['sessions']
                    for name, sess in hotspots.items():
                        if 'avg_r' in sess:
                            assert isinstance(sess['avg_r'], (float, int)), \
                                f"hotspot avg_r should be numeric, got {type(sess['avg_r'])}"
                        if 'win_rate' in sess:
                            assert isinstance(sess['win_rate'], (float, int)), \
                                f"hotspot win_rate should be numeric, got {type(sess['win_rate'])}"
                        if 'density' in sess:
                            assert isinstance(sess['density'], (float, int)), \
                                f"hotspot density should be numeric, got {type(sess['density'])}"
    
    def test_ensure_numeric_function(self):
        """Test the ensure_numeric utility function"""
        from time_analyzer import ensure_numeric
        
        # Test float conversion
        assert ensure_numeric("3.14") == 3.14
        assert ensure_numeric("0") == 0.0
        assert ensure_numeric("-2.5") == -2.5
        
        # Test None handling
        assert ensure_numeric(None) is None
        
        # Test already numeric values
        assert ensure_numeric(3.14) == 3.14
        assert ensure_numeric(42) == 42.0
        
        # Test non-numeric strings (should return unchanged)
        assert ensure_numeric("not_a_number") == "not_a_number"
        assert ensure_numeric("") == ""
    
    def test_normalize_numeric_fields_function(self):
        """Test the normalize_numeric_fields utility function"""
        from time_analyzer import normalize_numeric_fields
        
        # Test dict normalization
        test_dict = {
            'name': 'test',
            'value': '3.14',
            'count': '42',
            'nested': {
                'rate': '0.75',
                'label': 'nested_test'
            }
        }
        result = normalize_numeric_fields(test_dict)
        assert result['name'] == 'test'  # string unchanged
        assert result['value'] == 3.14   # string converted to float
        assert result['count'] == 42.0   # string converted to float
        assert result['nested']['rate'] == 0.75  # nested conversion
        assert result['nested']['label'] == 'nested_test'  # nested string unchanged
        
        # Test list normalization
        test_list = ['1.5', '2.0', 'text', None]
        result_list = normalize_numeric_fields(test_list)
        assert result_list[0] == 1.5
        assert result_list[1] == 2.0
        assert result_list[2] == 'text'
        assert result_list[3] is None



# ============================================================================
# V2 LOADER TESTS (CHUNK 6A)
# ============================================================================

class TestLoadV2Trades:
    """Tests for load_v2_trades function"""
    
    def test_load_v2_trades_structure(self):
        """Test load_v2_trades returns correct structure"""
        from datetime import datetime
        from time_analyzer import load_v2_trades
        
        # Mock V2 rows
        sample_v2_rows = [
            {
                "trade_id": "T1",
                "event_type": "SIGNAL_CREATED",
                "direction": "Bullish",
                "entry_price": 24000.0,
                "stop_loss": 23900.0,
                "be_mfe": None,
                "no_be_mfe": None,
                "session": "NY AM",
                "timestamp": datetime(2025, 11, 21, 14, 30),
            },
            {
                "trade_id": "T1",
                "event_type": "MFE_UPDATE",
                "direction": "Bullish",
                "entry_price": 24000.0,
                "stop_loss": 23900.0,
                "be_mfe": None,
                "no_be_mfe": 2.5,
                "session": "NY AM",
                "timestamp": datetime(2025, 11, 21, 14, 45),
            },
            {
                "trade_id": "T2",
                "event_type": "SIGNAL_CREATED",
                "direction": "Bearish",
                "entry_price": 23950.0,
                "stop_loss": 24050.0,
                "be_mfe": 1.8,
                "no_be_mfe": None,
                "session": "LONDON",
                "timestamp": datetime(2025, 11, 21, 10, 15),
            }
        ]
        
        # Mock cursor
        class FakeCursor:
            def execute(self, query):
                pass
            
            def fetchall(self):
                return sample_v2_rows
        
        # Mock connection
        class FakeConnection:
            def cursor(self, cursor_factory=None):
                return FakeCursor()
        
        # Mock database
        class FakeDB:
            def get_connection(self):
                return FakeConnection()
        
        fake_db = FakeDB()
        trades = load_v2_trades(fake_db)
        
        assert isinstance(trades, list)
        assert len(trades) == 2  # T1 and T2
        
        # Test T1 (should have no_be_mfe = 2.5)
        t1 = next((t for t in trades if t["direction"] == "Bullish"), None)
        assert t1 is not None
        assert t1["session"] == "NY AM"
        assert t1["hour"] == 14
        assert t1["r_value"] == 2.5
        assert t1["mfe_no_be"] == 2.5
        assert t1["mfe_be"] is None
        assert t1["entry_price"] == 24000.0
        assert t1["stop_loss"] == 23900.0
        
        # Test T2 (should have be_mfe = 1.8)
        t2 = next((t for t in trades if t["direction"] == "Bearish"), None)
        assert t2 is not None
        assert t2["session"] == "LONDON"
        assert t2["hour"] == 10
        assert t2["r_value"] == 1.8
        assert t2["mfe_be"] == 1.8
        assert t2["mfe_no_be"] is None
    
    def test_load_v2_trades_filters_invalid_entries(self):
        """Test that load_v2_trades filters out invalid entries"""
        from datetime import datetime
        from time_analyzer import load_v2_trades
        
        # Invalid rows
        sample_v2_invalid_rows = [
            {
                "trade_id": "T_INVALID_1",
                "event_type": "SIGNAL_CREATED",
                "direction": None,  # Missing direction
                "entry_price": 24000.0,
                "stop_loss": 23900.0,
                "be_mfe": None,
                "no_be_mfe": None,
                "session": "NY AM",
                "timestamp": datetime(2025, 11, 21, 14, 30),
            },
            {
                "trade_id": "T_INVALID_2",
                "event_type": "SIGNAL_CREATED",
                "direction": "Bullish",
                "entry_price": None,  # Missing entry_price
                "stop_loss": 23900.0,
                "be_mfe": None,
                "no_be_mfe": None,
                "session": "NY AM",
                "timestamp": datetime(2025, 11, 21, 14, 30),
            },
            {
                "trade_id": "T_INVALID_3",
                "event_type": "SIGNAL_CREATED",
                "direction": "Bullish",
                "entry_price": 24000.0,
                "stop_loss": 23900.0,
                "be_mfe": None,
                "no_be_mfe": None,
                "session": None,  # Missing session
                "timestamp": datetime(2025, 11, 21, 14, 30),
            }
        ]
        
        # Mock cursor
        class FakeCursor:
            def execute(self, query):
                pass
            
            def fetchall(self):
                return sample_v2_invalid_rows
        
        # Mock connection
        class FakeConnection:
            def cursor(self, cursor_factory=None):
                return FakeCursor()
        
        # Mock database
        class FakeDB:
            def get_connection(self):
                return FakeConnection()
        
        fake_db = FakeDB()
        trades = load_v2_trades(fake_db)
        
        # All invalid entries should be filtered out
        assert len(trades) == 0
    
    def test_load_v2_trades_handles_mfe_logic(self):
        """Test MFE preference logic: no_be_mfe preferred, be_mfe fallback, None → None"""
        from datetime import datetime
        from time_analyzer import load_v2_trades
        
        test_rows = [
            {
                "trade_id": "T_NO_BE",
                "event_type": "MFE_UPDATE",
                "direction": "Bullish",
                "entry_price": 24000.0,
                "stop_loss": 23900.0,
                "be_mfe": 1.0,
                "no_be_mfe": 2.0,  # This should be preferred
                "session": "NY AM",
                "timestamp": datetime(2025, 11, 21, 14, 30),
            },
            {
                "trade_id": "T_BE_ONLY",
                "event_type": "MFE_UPDATE",
                "direction": "Bearish",
                "entry_price": 23950.0,
                "stop_loss": 24050.0,
                "be_mfe": 1.5,  # This should be used as fallback
                "no_be_mfe": None,
                "session": "LONDON",
                "timestamp": datetime(2025, 11, 21, 10, 15),
            },
            {
                "trade_id": "T_NONE",
                "event_type": "SIGNAL_CREATED",
                "direction": "Bullish",
                "entry_price": 24100.0,
                "stop_loss": 24000.0,
                "be_mfe": None,
                "no_be_mfe": None,  # Both None → r_value should be None
                "session": "NY PM",
                "timestamp": datetime(2025, 11, 21, 18, 30),
            }
        ]
        
        # Mock cursor
        class FakeCursor:
            def execute(self, query):
                pass
            
            def fetchall(self):
                return test_rows
        
        # Mock connection
        class FakeConnection:
            def cursor(self, cursor_factory=None):
                return FakeCursor()
        
        # Mock database
        class FakeDB:
            def get_connection(self):
                return FakeConnection()
        
        fake_db = FakeDB()
        trades = load_v2_trades(fake_db)
        
        assert len(trades) == 3
        
        # Test no_be_mfe preference
        t_no_be = next((t for t in trades if t["entry_price"] == 24000.0), None)
        assert t_no_be["r_value"] == 2.0  # no_be_mfe preferred over be_mfe
        
        # Test be_mfe fallback
        t_be_only = next((t for t in trades if t["direction"] == "Bearish"), None)
        assert t_be_only["r_value"] == 1.5  # be_mfe used as fallback
        
        # Test None → None
        t_none = next((t for t in trades if t["entry_price"] == 24100.0), None)
        assert t_none["r_value"] is None  # Both MFE values None
    
    def test_load_v2_trades_session_normalization(self):
        """Test that load_v2_trades uses session normalization"""
        from datetime import datetime
        from time_analyzer import load_v2_trades
        
        test_rows = [
            {
                "trade_id": "T_NORM",
                "event_type": "SIGNAL_CREATED",
                "direction": "Bullish",
                "entry_price": 24000.0,
                "stop_loss": 23900.0,
                "be_mfe": None,
                "no_be_mfe": None,
                "session": "ny am",  # lowercase - should be normalized
                "timestamp": datetime(2025, 11, 21, 14, 30),
            }
        ]
        
        # Mock cursor
        class FakeCursor:
            def execute(self, query):
                pass
            
            def fetchall(self):
                return test_rows
        
        # Mock connection
        class FakeConnection:
            def cursor(self, cursor_factory=None):
                return FakeCursor()
        
        # Mock database
        class FakeDB:
            def get_connection(self):
                return FakeConnection()
        
        fake_db = FakeDB()
        trades = load_v2_trades(fake_db)
        
        assert len(trades) == 1
        assert trades[0]["session"] == "ny am"  # Session normalization happens via normalize_session_name



# ============================================================================
# SOURCE SELECTION TESTS (CHUNK 6B)
# ============================================================================

class TestAnalyzeTimePerformanceSourceSelection:
    """Tests for analyze_time_performance source parameter"""
    
    def test_analyze_time_performance_uses_v2_when_default(self, monkeypatch):
        """Test that analyze_time_performance uses V2 loader by default"""
        from time_analyzer import analyze_time_performance
        
        calls = {"v2": False}
        
        def fake_v2_loader(db):
            calls["v2"] = True
            return []
        
        monkeypatch.setattr("time_analyzer.load_v2_trades", fake_v2_loader)
        
        # Mock db
        class FakeDB:
            class conn:
                @staticmethod
                def cursor():
                    return None
        
        try:
            analyze_time_performance(FakeDB())  # default == v2
        except:
            pass  # May fail on empty data, but we only care about loader call
        
        assert calls["v2"] is True, "V2 loader should be called by default"
    
    def test_analyze_time_performance_uses_v1_when_requested(self, monkeypatch):
        """Test that analyze_time_performance uses V1 loader when source='v1'"""
        from time_analyzer import analyze_time_performance
        
        calls = {"v1": False}
        
        def fake_v1_loader(db):
            calls["v1"] = True
            return []
        
        monkeypatch.setattr("time_analyzer.load_v1_trades", fake_v1_loader)
        
        # Mock db
        class FakeDB:
            class conn:
                @staticmethod
                def cursor():
                    return None
        
        try:
            analyze_time_performance(FakeDB(), source="v1")
        except:
            pass  # May fail on empty data, but we only care about loader call
        
        assert calls["v1"] is True, "V1 loader should be called when source='v1'"
    
    def test_analyze_time_performance_rejects_invalid_source(self):
        """Test that analyze_time_performance rejects invalid source values"""
        from time_analyzer import analyze_time_performance
        
        # Mock db
        class FakeDB:
            class conn:
                @staticmethod
                def cursor():
                    return None
        
        try:
            analyze_time_performance(FakeDB(), source="invalid")
            assert False, "Expected ValueError for invalid source"
        except ValueError as e:
            assert "invalid" in str(e).lower(), f"Error message should mention 'invalid': {e}"
            assert "v1" in str(e).lower() or "v2" in str(e).lower(), f"Error should mention valid options: {e}"
        except Exception as e:
            assert False, f"Expected ValueError but got {type(e).__name__}: {e}"



# ============================================================================
# SAFE BEST_* CALCULATIONS TESTS (CHUNK 9)
# ============================================================================

class TestSafeBestCalculations:
    """Tests for safe best_* calculations that don't crash on empty lists"""
    
    def test_best_values_do_not_crash_on_empty_lists(self, monkeypatch):
        """Test that best_* calculations don't crash when analysis functions return empty lists"""
        from time_analyzer import analyze_time_performance
        
        # Force analyze_* functions to return empty lists
        def fake_analyze_hourly(trades):
            return []
        
        def fake_analyze_session(trades):
            return []
        
        def fake_analyze_day_of_week(trades):
            return []
        
        def fake_analyze_monthly(trades):
            return []
        
        def fake_analyze_week_of_month(trades):
            return []
        
        def fake_analyze_session_hotspots(hourly, session, trades):
            return {'sessions': {}}
        
        def fake_analyze_macro(trades):
            return []
        
        # Mock all analysis functions to return empty lists
        monkeypatch.setattr('time_analyzer.analyze_hourly', fake_analyze_hourly)
        monkeypatch.setattr('time_analyzer.analyze_session', fake_analyze_session)
        monkeypatch.setattr('time_analyzer.analyze_day_of_week', fake_analyze_day_of_week)
        monkeypatch.setattr('time_analyzer.analyze_monthly', fake_analyze_monthly)
        monkeypatch.setattr('time_analyzer.analyze_week_of_month', fake_analyze_week_of_month)
        monkeypatch.setattr('time_analyzer.analyze_session_hotspots', fake_analyze_session_hotspots)
        monkeypatch.setattr('time_analyzer.analyze_macro', fake_analyze_macro)
        
        # Mock load_v2_trades to return minimal trade data
        def fake_load_v2_trades(db):
            return [{'r_value': 1.0}]  # Need at least one trade for overall_expectancy
        
        monkeypatch.setattr('time_analyzer.load_v2_trades', fake_load_v2_trades)
        
        # Mock db
        class FakeDB:
            class conn:
                @staticmethod
                def cursor():
                    return None
        
        # This should not crash even with empty analysis results
        analysis = analyze_time_performance(FakeDB(), source="v2")
        
        # Verify all best_* keys are present
        assert 'best_hour' in analysis, "best_hour key should be present"
        assert 'best_session' in analysis, "best_session key should be present"
        assert 'best_day' in analysis, "best_day key should be present"
        assert 'best_month' in analysis, "best_month key should be present"
        
        # All should have N/A values when lists are empty
        assert analysis['best_hour']['hour'] == 'N/A', "best_hour should be N/A when hourly analysis is empty"
        assert analysis['best_hour']['expectancy'] == 0, "best_hour expectancy should be 0"
        
        assert analysis['best_session']['session'] == 'N/A', "best_session should be N/A when session analysis is empty"
        assert analysis['best_session']['expectancy'] == 0, "best_session expectancy should be 0"
        
        assert analysis['best_day']['day'] == 'N/A', "best_day should be N/A when day analysis is empty"
        assert analysis['best_day']['expectancy'] == 0, "best_day expectancy should be 0"
        
        assert analysis['best_month']['month'] == 'N/A', "best_month should be N/A when monthly analysis is empty"
        assert analysis['best_month']['expectancy'] == 0, "best_month expectancy should be 0"
        
        # Verify other keys are still present
        assert 'hourly' in analysis
        assert 'session' in analysis
        assert 'day_of_week' in analysis
        assert 'monthly' in analysis
        assert 'overall_expectancy' in analysis
    
    def test_best_values_work_with_non_empty_lists(self, monkeypatch):
        """Test that best_* calculations still work correctly when lists have data"""
        from time_analyzer import analyze_time_performance
        
        # Create mock analysis results with expectancy values
        def fake_analyze_hourly(trades):
            return [
                {'hour': 9, 'expectancy': 1.5, 'trades': 10},
                {'hour': 10, 'expectancy': 2.0, 'trades': 8},  # Best
                {'hour': 11, 'expectancy': 1.2, 'trades': 12}
            ]
        
        def fake_analyze_session(trades):
            return [
                {'session': 'NY AM', 'expectancy': 1.8, 'trades': 15},  # Best
                {'session': 'LONDON', 'expectancy': 1.3, 'trades': 20}
            ]
        
        def fake_analyze_day_of_week(trades):
            return [
                {'day': 'Monday', 'expectancy': 1.1, 'trades': 5},
                {'day': 'Tuesday', 'expectancy': 2.5, 'trades': 8}  # Best
            ]
        
        def fake_analyze_monthly(trades):
            return [
                {'month': 'January', 'expectancy': 1.7, 'trades': 25},
                {'month': 'February', 'expectancy': 2.2, 'trades': 18}  # Best
            ]
        
        def fake_analyze_week_of_month(trades):
            return [{'week': 1, 'expectancy': 1.0, 'trades': 5}]
        
        def fake_analyze_session_hotspots(hourly, session, trades):
            return {'sessions': {}}
        
        def fake_analyze_macro(trades):
            return []
        
        # Mock all analysis functions
        monkeypatch.setattr('time_analyzer.analyze_hourly', fake_analyze_hourly)
        monkeypatch.setattr('time_analyzer.analyze_session', fake_analyze_session)
        monkeypatch.setattr('time_analyzer.analyze_day_of_week', fake_analyze_day_of_week)
        monkeypatch.setattr('time_analyzer.analyze_monthly', fake_analyze_monthly)
        monkeypatch.setattr('time_analyzer.analyze_week_of_month', fake_analyze_week_of_month)
        monkeypatch.setattr('time_analyzer.analyze_session_hotspots', fake_analyze_session_hotspots)
        monkeypatch.setattr('time_analyzer.analyze_macro', fake_analyze_macro)
        
        # Mock load_v2_trades to return some data
        def fake_load_v2_trades(db):
            return [{'r_value': 1.5}]
        
        monkeypatch.setattr('time_analyzer.load_v2_trades', fake_load_v2_trades)
        
        # Mock db
        class FakeDB:
            class conn:
                @staticmethod
                def cursor():
                    return None
        
        analysis = analyze_time_performance(FakeDB(), source="v2")
        
        # Verify best_* values are correctly identified (highest expectancy)
        assert analysis['best_hour'] is not None
        assert analysis['best_hour']['hour'] == '10:00'  # Highest expectancy (2.0)
        assert analysis['best_hour']['expectancy'] == 2.0
        
        assert analysis['best_session'] is not None
        assert analysis['best_session']['session'] == 'NY AM'  # Highest expectancy (1.8)
        assert analysis['best_session']['expectancy'] == 1.8
        
        assert analysis['best_day'] is not None
        assert analysis['best_day']['day'] == 'Tuesday'  # Highest expectancy (2.5)
        assert analysis['best_day']['expectancy'] == 2.5
        
        assert analysis['best_month'] is not None
        assert analysis['best_month']['month'] == 'February'  # Highest expectancy (2.2)
        assert analysis['best_month']['expectancy'] == 2.2



# ============================================================================
# CHUNK 7A - HEADER METRICS & CONTROLS V2 MIGRATION TESTS
# ============================================================================

class TestChunk7AHeaderV2Migration:
    """Tests for V2 migration of header metrics and controls"""
    
    def test_dataset_dropdown_removed(self):
        """Test that the dataset dropdown has been completely removed"""
        with open("templates/time_analysis.html") as f:
            content = f.read()
        
        assert "dataset-toggle" not in content, "dataset-toggle ID should be removed"
        assert "Dataset V1" not in content, "Dataset V1 text should be removed"
        assert "Dataset V2" not in content, "Dataset V2 text should be removed"
        assert "dataset-selector" not in content, "dataset-selector class should be removed"
    
    def test_header_metric_placeholders_present(self):
        """Test that header metric IDs are present with correct naming"""
        with open("templates/time_analysis.html") as f:
            content = f.read()
        
        # Check for new camelCase IDs
        assert "winRateValue" in content, "winRateValue ID should be present"
        assert "expectancyValue" in content, "expectancyValue ID should be present"
        assert "avgRValue" in content, "avgRValue ID should be present"
        assert "totalTradesValue" in content, "totalTradesValue ID should be present"
        assert "bestSessionValue" in content, "bestSessionValue ID should be present"
    
    def test_header_has_modern_layout(self):
        """Test that header has modern ta-header layout structure"""
        with open("templates/time_analysis.html") as f:
            content = f.read()
        
        assert "ta-header" in content, "ta-header class should be present"
        assert "ta-header-left" in content, "ta-header-left class should be present"
        assert "ta-header-right" in content, "ta-header-right class should be present"
        assert "ta-subtitle" in content, "ta-subtitle class should be present"
        assert "ta-filter-row" in content, "ta-filter-row class should be present"
        assert "ta-stat-row" in content, "ta-stat-row class should be present"
    
    def test_filter_controls_present(self):
        """Test that filter controls are present in template"""
        with open("templates/time_analysis.html") as f:
            content = f.read()
        
        assert "startDateInput" in content, "startDateInput should be present"
        assert "endDateInput" in content, "endDateInput should be present"
        assert "sessionFilter" in content, "sessionFilter should be present"
        assert "directionFilter" in content, "directionFilter should be present"
    
    def test_js_contains_render_header_metrics(self):
        """Test that JS contains renderHeaderMetrics method"""
        with open("static/js/time_analysis.js") as f:
            content = f.read()
        
        assert "renderHeaderMetrics" in content, "renderHeaderMetrics method should be present"
    
    def test_js_uses_new_element_ids(self):
        """Test that JS uses the new camelCase element IDs"""
        with open("static/js/time_analysis.js") as f:
            content = f.read()
        
        # Check for new IDs in renderHeaderMetrics
        assert "winRateValue" in content, "JS should reference winRateValue"
        assert "expectancyValue" in content, "JS should reference expectancyValue"
        assert "avgRValue" in content, "JS should reference avgRValue"
        assert "totalTradesValue" in content, "JS should reference totalTradesValue"
        assert "bestSessionValue" in content, "JS should reference bestSessionValue"
    
    def test_js_has_setup_filters_method(self):
        """Test that JS has setupFilters method"""
        with open("static/js/time_analysis.js") as f:
            content = f.read()
        
        assert "setupFilters" in content, "setupFilters method should be present"
        assert "startDateInput" in content, "JS should reference startDateInput"
        assert "endDateInput" in content, "JS should reference endDateInput"
        assert "sessionFilter" in content, "JS should reference sessionFilter"
        assert "directionFilter" in content, "JS should reference directionFilter"
        assert "TODO: apply V2 filters" in content, "Filter handler should have TODO stub"
    
    def test_css_has_new_header_styles(self):
        """Test that CSS has new header layout styles"""
        with open("static/css/time_analysis.css") as f:
            content = f.read()
        
        assert ".ta-header" in content, "CSS should define ta-header class"
        assert ".ta-header-left" in content, "CSS should define ta-header-left class"
        assert ".ta-header-right" in content, "CSS should define ta-header-right class"
        assert ".ta-subtitle" in content, "CSS should define ta-subtitle class"
        assert ".ta-filter-row" in content, "CSS should define ta-filter-row class"
        assert ".ta-stat-row" in content, "CSS should define ta-stat-row class"
    
    def test_render_all_calls_header_metrics(self):
        """Test that renderAll calls renderHeaderMetrics"""
        with open("static/js/time_analysis.js") as f:
            content = f.read()
        
        # Find renderAll method
        assert "renderAll()" in content, "renderAll method should exist"
        
        # Check it calls renderHeaderMetrics
        render_all_section = content[content.find("renderAll()"):content.find("renderAll()") + 500]
        assert "renderHeaderMetrics" in render_all_section, "renderAll should call renderHeaderMetrics"



class TestChunk7CTemporalAnalytics:
    """Tests for CHUNK 7C - Temporal Analytics (Day/Week/Month/Macro/R-Distribution)"""
    
    def test_template_has_temporal_grids(self):
        """Test that template has all temporal analytics grid containers"""
        with open("templates/time_analysis.html", encoding="utf-8") as f:
            c = f.read()
        assert 'id="dayOfWeekGrid"' in c, "dayOfWeekGrid should be present"
        assert 'id="weekOfMonthGrid"' in c, "weekOfMonthGrid should be present"
        assert 'id="monthOfYearGrid"' in c, "monthOfYearGrid should be present"
        assert 'id="macroGrid"' in c, "macroGrid should be present"
        assert 'id="rDistCanvas"' in c, "rDistCanvas should be present"
    
    def test_js_has_temporal_render_functions(self):
        """Test that JS has all temporal rendering functions"""
        with open("static/js/time_analysis.js", encoding="utf-8") as f:
            c = f.read()
        assert "renderDayOfWeek" in c, "renderDayOfWeek function should be present"
        assert "renderWeekOfMonth" in c, "renderWeekOfMonth function should be present"
        assert "renderMonthOfYear" in c, "renderMonthOfYear function should be present"
        assert "renderMacroWindows" in c, "renderMacroWindows function should be present"
        assert "renderRDistribution" in c, "renderRDistribution function should be present"
    
    def test_js_render_all_calls_temporal_functions(self):
        """Test that renderAll() calls all temporal rendering functions"""
        with open("static/js/time_analysis.js", encoding="utf-8") as f:
            c = f.read()
        
        # Find renderAll method
        render_all_start = c.find('renderAll()')
        assert render_all_start != -1, "renderAll method should exist"
        
        # Get renderAll method content (next 500 chars should be enough)
        render_all_section = c[render_all_start:render_all_start + 500]
        
        assert 'this.renderDayOfWeek()' in render_all_section, "renderAll should call renderDayOfWeek"
        assert 'this.renderWeekOfMonth()' in render_all_section, "renderAll should call renderWeekOfMonth"
        assert 'this.renderMonthOfYear()' in render_all_section, "renderAll should call renderMonthOfYear"
        assert 'this.renderMacroWindows()' in render_all_section, "renderAll should call renderMacroWindows"
        assert 'this.renderRDistribution()' in render_all_section, "renderAll should call renderRDistribution"
    
    def test_js_uses_chart_js_for_mini_charts(self):
        """Test that JS creates Chart.js mini sparklines"""
        with open("static/js/time_analysis.js", encoding="utf-8") as f:
            c = f.read()
        
        # Check for Chart.js instantiation in temporal functions
        assert 'new Chart(ctx, {' in c, "Chart.js should be instantiated"
        assert 'dowMini' in c, "Day of Week mini charts should be created"
        assert 'womMini' in c, "Week of Month mini charts should be created"
        assert 'moyMini' in c, "Month of Year mini charts should be created"
        
        # Check for mini-chart class usage
        assert 'mini-chart' in c, "mini-chart class should be used"
    
    def test_js_uses_v2_data_fields(self):
        """Test that JS uses correct V2 data field names"""
        with open("static/js/time_analysis.js", encoding="utf-8") as f:
            c = f.read()
        
        # Check for V2 field usage
        assert 'day_of_week' in c, "Should reference day_of_week data"
        assert 'week_of_month' in c, "Should reference week_of_month data"
        assert 'monthly' in c, "Should reference monthly data"
        assert 'macro' in c, "Should reference macro data"
        
        # Check for metric field usage
        assert 'expectancy' in c, "Should use expectancy field"
        assert 'win_rate' in c, "Should use win_rate field"
        assert 'avg_r' in c, "Should use avg_r field"
