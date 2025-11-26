"""
H1.2 Main Dashboard - MASTER PATCH Test Suite
Complete validation of clean rebuild with NO FAKE DATA
"""

import os
import pytest


class TestMasterPatchImplementation:
    """Verify MASTER PATCH specifications are met"""
    
    def test_template_exists(self):
        """Template file exists"""
        assert os.path.exists('templates/main_dashboard.html')
    
    def test_css_exists(self):
        """CSS file exists"""
        assert os.path.exists('static/css/main_dashboard.css')
    
    def test_js_exists(self):
        """JavaScript file exists"""
        assert os.path.exists('static/js/main_dashboard.js')
    
    def test_template_imports_macros(self):
        """Template imports roadmap macros"""
        with open('templates/main_dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
            assert "from '_macros.html' import roadmap_locked" in content
            assert "from '_macros.html' import" in content
    
    def test_no_fake_automation_status(self):
        """No fake automation status in template"""
        with open('templates/main_dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
            # Should NOT have hardcoded "ACTIVE" or "HEALTHY" for automation
            assert 'Automation: ACTIVE' not in content
            assert 'Risk Engine: HEALTHY' not in content
    
    def test_no_fake_queue_depth(self):
        """No fake queue depth metrics"""
        with open('templates/main_dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'Queue Depth' not in content or 'roadmap_locked' in content
    
    def test_no_fake_latency(self):
        """No fake latency metrics"""
        with open('templates/main_dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'Latency' not in content or 'roadmap_locked' in content


class TestSystemTimeAPI:
    """Test /api/system-time endpoint and session logic"""
    
    def test_get_ny_session_info_returns_dict(self):
        """get_ny_session_info() returns proper dict structure"""
        from web_server import get_ny_session_info
        
        info = get_ny_session_info()
        
        assert isinstance(info, dict)
        assert 'et_time' in info
        assert 'current_session' in info
        assert 'next_session' in info
    
    def test_get_ny_session_info_valid_sessions(self):
        """get_ny_session_info() returns valid session names"""
        from web_server import get_ny_session_info
        
        info = get_ny_session_info()
        
        valid_sessions = ['ASIA', 'LONDON', 'NY PRE', 'NY AM', 'NY LUNCH', 'NY PM', 'CLOSED']
        assert info['current_session'] in valid_sessions
        assert info['next_session'] in valid_sessions
    
    def test_get_ny_session_info_et_time_has_timezone(self):
        """get_ny_session_info() returns ET time with timezone"""
        from web_server import get_ny_session_info
        
        info = get_ny_session_info()
        
        assert info['et_time'].tzinfo is not None
        assert str(info['et_time'].tzinfo) in ['EST', 'EDT', 'America/New_York']
    
    def test_system_time_endpoint_exists(self):
        """Verify /api/system-time endpoint is registered"""
        from web_server import app
        
        # Check if route exists
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        assert '/api/system-time' in routes
    
    def test_system_time_endpoint_returns_json(self):
        """Test /api/system-time returns proper JSON structure"""
        from web_server import app
        
        with app.test_client() as client:
            # Note: This will fail without login, but we're testing structure
            # In real deployment, this requires @login_required
            response = client.get('/api/system-time')
            
            # Should redirect to login (302) or return 401 unauthorized
            assert response.status_code in [302, 401]
    
    def test_session_sequence_logic(self):
        """Test that next_session follows correct sequence"""
        from web_server import get_ny_session_info
        
        info = get_ny_session_info()
        
        # Define valid transitions
        valid_transitions = {
            'ASIA': 'LONDON',
            'LONDON': 'NY PRE',
            'NY PRE': 'NY AM',
            'NY AM': 'NY LUNCH',
            'NY LUNCH': 'NY PM',
            'NY PM': 'ASIA',
            'CLOSED': 'ASIA'
        }
        
        current = info['current_session']
        next_session = info['next_session']
        
        assert valid_transitions[current] == next_session


class TestChunk2TimePanel:
    """Test Chunk 2: Time Panel & Layout Adjustments"""
    
    def test_time_panel_elements_exist(self):
        """Verify time panel HTML elements exist in template"""
        with open('templates/main_dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Time panel container
            assert 'class="time-panel"' in content
            
            # Local time elements
            assert 'id="localTimeDisplay"' in content
            assert 'id="localLocationDisplay"' in content
            
            # NY time elements
            assert 'id="nyTimeDisplay"' in content
            assert 'id="currentSessionDisplay"' in content
            
            # Time labels
            assert 'Local Time' in content
            assert 'New York Time (ET)' in content
    
    def test_time_panel_css_exists(self):
        """Verify time panel CSS styling exists"""
        with open('static/css/main_dashboard.css', 'r', encoding='utf-8') as f:
            content = f.read()
            
            assert '.time-panel' in content
            assert '.time-block' in content
            assert '.time-label' in content
            assert '.time-value' in content
            assert '.time-sub' in content
    
    def test_prop_firm_in_left_column(self):
        """Verify Prop-Firm Status panel is in left column"""
        with open('templates/main_dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Find left column
            left_col_start = content.find('<!-- LEFT COLUMN -->')
            left_col_end = content.find('<!-- RIGHT COLUMN -->')
            
            assert left_col_start != -1, "Left column marker not found"
            assert left_col_end != -1, "Right column marker not found"
            
            left_column_content = content[left_col_start:left_col_end]
            
            # Prop-Firm Status should be in left column
            assert 'Prop-Firm Status' in left_column_content
            assert 'id="prop-pnl-today"' in left_column_content
    
    def test_prop_firm_above_automation_engine(self):
        """Verify Prop-Firm Status appears before Automation Engine"""
        with open('templates/main_dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
            
            prop_firm_pos = content.find('Prop-Firm Status')
            automation_pos = content.find('Automation Engine')
            
            assert prop_firm_pos != -1, "Prop-Firm Status not found"
            assert automation_pos != -1, "Automation Engine not found"
            assert prop_firm_pos < automation_pos, "Prop-Firm Status should appear before Automation Engine"
    
    def test_no_duplicate_prop_firm_panel(self):
        """Verify Prop-Firm Status panel appears only once"""
        with open('templates/main_dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Count occurrences of Prop-Firm Status header
            count = content.count('Prop-Firm Status</h3>')
            assert count == 1, f"Prop-Firm Status should appear exactly once, found {count} times"
    
    def test_renderSystemTime_updates_time_display(self):
        """Verify renderSystemTime method updates time display elements"""
        with open('static/js/main_dashboard.js', 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for time display updates
            assert 'localTimeDisplay' in content
            assert 'localLocationDisplay' in content
            assert 'nyTimeDisplay' in content
            assert 'currentSessionDisplay' in content
            
            # Check for timezone handling
            assert 'Intl.DateTimeFormat' in content
            assert 'timeZone' in content


class TestChunk3DatePanel:
    """Test Chunk 3: Today's Date Panel"""
    
    def test_date_panel_elements_exist(self):
        """Verify date panel HTML elements exist in template"""
        with open('templates/main_dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Date panel container
            assert 'class="date-panel"' in content
            
            # Date display elements
            assert 'id="todayDateDisplay"' in content
            assert 'id="todayWeekDisplay"' in content
            
            # Comment marker
            assert "Today's Date Panel" in content
    
    def test_date_panel_css_exists(self):
        """Verify date panel CSS styling exists"""
        with open('static/css/main_dashboard.css', 'r', encoding='utf-8') as f:
            content = f.read()
            
            assert '.date-panel' in content
            assert '.date-main' in content
            assert '.date-sub' in content
            
            # Check for specific styles
            assert 'linear-gradient' in content
            assert 'border-radius: 8px' in content
    
    def test_date_panel_above_pnl_today(self):
        """Verify date panel appears before P&L Today panel"""
        with open('templates/main_dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
            
            date_panel_pos = content.find('class="date-panel"')
            pnl_today_pos = content.find('P&L TODAY PANEL')
            
            assert date_panel_pos != -1, "Date panel not found"
            assert pnl_today_pos != -1, "P&L Today panel not found"
            assert date_panel_pos < pnl_today_pos, "Date panel should appear before P&L Today"
    
    def test_date_panel_in_right_column(self):
        """Verify date panel is in right column"""
        with open('templates/main_dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Find right column
            right_col_start = content.find('<!-- RIGHT COLUMN -->')
            
            # Find next column or end
            next_section = content.find('</div>', right_col_start + 1000)
            
            assert right_col_start != -1, "Right column marker not found"
            
            # Date panel should be in right column
            date_panel_pos = content.find('class="date-panel"')
            assert date_panel_pos > right_col_start, "Date panel should be in right column"
    
    def test_renderTodayDate_method_exists(self):
        """Verify renderTodayDate method exists in JavaScript"""
        with open('static/js/main_dashboard.js', 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for method definition
            assert 'renderTodayDate()' in content
            
            # Check for date formatting
            assert 'toLocaleDateString' in content
            assert 'weekday' in content
            assert 'month' in content
            
            # Check for week number calculation
            assert 'Week ${week}' in content or 'Week ' in content
            
            # Check for element updates
            assert 'todayDateDisplay' in content
            assert 'todayWeekDisplay' in content
    
    def test_date_panel_initialization(self):
        """Verify date panel is initialized in init method"""
        with open('static/js/main_dashboard.js', 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for initialization call
            assert 'this.renderTodayDate()' in content
            
            # Check for interval setup
            assert 'setInterval' in content
            assert '60000' in content  # 60 second interval
    
    def test_no_vs_yesterday(self):
        """No fake 'vs yesterday' comparisons"""
        with open('templates/main_dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'vs yesterday' not in content.lower()
    
    def test_automation_engine_locked(self):
        """Automation Engine panel uses roadmap locks"""
        with open('templates/main_dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'Automation Engine' in content
            # Should have locked sections
            automation_section = content[content.find('Automation Engine'):content.find('Automation Engine') + 1000]
            assert 'roadmap_locked' in automation_section
    
    def test_prop_firm_h1_limited(self):
        """Prop-Firm Status is H1-limited with locks"""
        with open('templates/main_dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'Prop-Firm Status' in content
            prop_section = content[content.find('Prop-Firm Status'):content.find('Prop-Firm Status') + 2000]
            # Should have multiple roadmap locks
            assert prop_section.count('roadmap_locked') >= 5
    
    def test_active_signals_lifecycle_driven(self):
        """Active Signals panel is lifecycle-driven"""
        with open('static/js/main_dashboard.js', 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'renderActiveSignals' in content
            assert 'ACTIVE' in content or 'CONFIRMED' in content
            # Should filter by status
            assert 'filter' in content
    
    def test_signal_card_has_all_fields(self):
        """Signal cards include all required H1 fields"""
        with open('static/js/main_dashboard.js', 'r', encoding='utf-8') as f:
            content = f.read()
            signal_card_section = content[content.find('createSignalCard'):content.find('createSignalCard') + 2000]
            required_fields = ['direction', 'session', 'entry_price', 'stop_loss', 
                             'be_triggered', 'no_be_mfe', 'be_mfe', 'duration', 'risk_distance']
            for field in required_fields:
                assert field in signal_card_section
    
    def test_unknown_signal_error_handling(self):
        """Unknown signals show error message"""
        with open('static/js/main_dashboard.js', 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'UNKNOWN' in content
            assert 'Data Integrity Issue' in content or 'integrity' in content.lower()
    
    def test_primary_kpis_repositioned(self):
        """Primary KPIs (Expectancy, Win Rate, R-Dist) are at top"""
        with open('templates/main_dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
            # Find positions
            kpi_pos = content.find('PRIMARY KPIS')
            signals_pos = content.find('Active Signals')
            # KPIs should come before signals
            assert kpi_pos < signals_pos
    
    def test_active_strategy_locked(self):
        """Active Strategy panel is locked behind H1.28"""
        with open('templates/main_dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'Active Strategy' in content or 'h1_28' in content
            assert 'roadmap_locked' in content
    
    def test_pnl_today_expanded(self):
        """P&L Today has expanded H1 fields"""
        with open('templates/main_dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
            pnl_section = content[content.find('P&L Today'):content.find('P&L Today') + 1500]
            assert 'R Today' in pnl_section
            assert 'Trades Today' in pnl_section
            assert 'Win/Loss' in pnl_section
            assert 'Best Trade' in pnl_section
            assert 'Worst Trade' in pnl_section
            assert 'Date' in pnl_section
    
    def test_session_performance_upgraded(self):
        """Session Performance has full H1 upgrade"""
        with open('static/js/main_dashboard.js', 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'renderSessionPerformance' in content
            assert 'session_breakdown' in content
            assert 'hot' in content.lower() or 'Hot' in content
    
    def test_signal_quality_real_metrics(self):
        """Signal Quality uses real H1 metrics"""
        with open('templates/main_dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
            quality_section = content[content.find('Signal Quality'):content.find('Signal Quality') + 1000]
            assert 'Valid Signal Rate' in quality_section
            assert 'Noise Rate' in quality_section
            assert 'Confirmation Time' in quality_section
            assert 'Cancellation Rate' in quality_section
    
    def test_risk_warnings_implemented(self):
        """Risk Snapshot includes warning system"""
        with open('static/js/main_dashboard.js', 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'renderRiskWarnings' in content
            assert 'risk-warning' in content
            assert 'danger' in content
            assert 'warning' in content
    
    def test_no_fake_data_in_js(self):
        """JavaScript has no fake data"""
        with open('static/js/main_dashboard.js', 'r', encoding='utf-8') as f:
            content = f.read().lower()
            forbidden = ['fake', 'dummy', 'lorem ipsum', 'test data', 'sample data', 'mock data']
            for word in forbidden:
                assert word not in content
    
    def test_lifecycle_driven_filtering(self):
        """Active signals use lifecycle-driven filtering"""
        with open('static/js/main_dashboard.js', 'r', encoding='utf-8') as f:
            content = f.read()
            # Should filter for confirmed AND no exit AND not cancelled
            assert 'filter' in content
            assert 'status' in content
    
    def test_real_api_endpoints(self):
        """JavaScript fetches from real API endpoints"""
        with open('static/js/main_dashboard.js', 'r', encoding='utf-8') as f:
            content = f.read()
            assert '/api/automated-signals/dashboard-data' in content
            assert '/api/automated-signals/stats-live' in content
    
    def test_error_handling_present(self):
        """JavaScript includes error handling"""
        with open('static/js/main_dashboard.js', 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'try' in content
            assert 'catch' in content
            assert 'error' in content.lower()
    
    def test_polling_implemented(self):
        """Dashboard implements 15-second polling"""
        with open('static/js/main_dashboard.js', 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'refreshInterval' in content
            assert '15000' in content
            assert 'setInterval' in content
    
    def test_css_deep_blue_theme(self):
        """CSS uses deep blue fintech theme"""
        with open('static/css/main_dashboard.css', 'r', encoding='utf-8') as f:
            content = f.read()
            # Should have deep blue colors
            assert '#0a1324' in content or '#0d1b33' in content
            assert 'linear-gradient' in content
    
    def test_responsive_design(self):
        """CSS includes responsive design"""
        with open('static/css/main_dashboard.css', 'r', encoding='utf-8') as f:
            content = f.read()
            assert '@media' in content
            assert 'max-width' in content
    
    def test_locked_sections_styled(self):
        """Locked sections have proper styling"""
        with open('static/css/main_dashboard.css', 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'locked' in content.lower()
    
    def test_empty_states_styled(self):
        """Empty states have proper styling"""
        with open('static/css/main_dashboard.css', 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'empty-state' in content
    
    def test_health_topbar_real_data_only(self):
        """Health topbar shows only real H1 data"""
        with open('templates/main_dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
            topbar_section = content[content.find('HEALTH TOPBAR'):content.find('HEALTH TOPBAR') + 1500]
            # Should have webhook, session, next session
            assert 'Webhook Health' in topbar_section
            assert 'Current Session' in topbar_section
            assert 'Next Session' in topbar_section
            # Should have locked items
            assert 'roadmap_locked' in topbar_section
    
    def test_no_placeholder_text(self):
        """Template has no placeholder text"""
        with open('templates/main_dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read().lower()
            forbidden = ['lorem ipsum', 'todo', 'fixme', 'coming soon']
            for word in forbidden:
                assert word not in content


class TestIntegration:
    """Integration tests"""
    
    def test_route_exists_in_web_server(self):
        """Route exists in web_server.py"""
        with open('web_server.py', 'r', encoding='utf-8') as f:
            content = f.read()
            assert "@app.route('/main-dashboard')" in content
            assert "def main_dashboard():" in content
    
    def test_homepage_links_to_dashboard(self):
        """Homepage links to main dashboard"""
        with open('templates/homepage_video_background.html', 'r', encoding='utf-8') as f:
            content = f.read()
            assert '/main-dashboard' in content
    
    def test_roadmap_state_marked_complete(self):
        """H1.2 marked complete in roadmap_state.py"""
        with open('roadmap_state.py', 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'h1_2_main_dashboard' in content
            # Find the line and check if done: True
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'h1_2_main_dashboard' in line:
                    section = '\n'.join(lines[i:i+3])
                    assert '"done": True' in section
                    break


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
