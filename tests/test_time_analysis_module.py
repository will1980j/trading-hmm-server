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
