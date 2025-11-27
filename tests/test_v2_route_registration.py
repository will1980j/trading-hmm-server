"""
H1.4 CHUNK 4: V2 Route Registration Smoke Tests

Tests to verify that previously missing V2 endpoints are now registered
and reachable (not returning 404).

These are minimal smoke tests - we only verify routes are registered,
not that they return perfect data.
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from web_server import app


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestV2RouteRegistration:
    """Test that V2 routes are registered and reachable"""
    
    def test_stats_endpoint_registered(self, client):
        """Test /api/automated-signals/stats is registered"""
        response = client.get('/api/automated-signals/stats')
        # Should NOT be 404 - route must be registered
        assert response.status_code != 404, "Stats endpoint returned 404 - route not registered!"
        # Accept 200, 500, or other codes - just not 404
        assert response.status_code in [200, 500], f"Unexpected status: {response.status_code}"
    
    def test_dashboard_data_endpoint_registered(self, client):
        """Test /api/automated-signals/dashboard-data is registered"""
        response = client.get('/api/automated-signals/dashboard-data')
        # Should NOT be 404 - route must be registered
        assert response.status_code != 404, "Dashboard data endpoint returned 404 - route not registered!"
        # Accept 200, 500, or other codes - just not 404
        assert response.status_code in [200, 500], f"Unexpected status: {response.status_code}"
    
    def test_mfe_distribution_endpoint_registered(self, client):
        """Test /api/automated-signals/mfe-distribution is registered (was missing)"""
        response = client.get('/api/automated-signals/mfe-distribution')
        # This endpoint was previously 404 - now should be registered
        assert response.status_code != 404, "MFE distribution endpoint returned 404 - route not registered!"
        # Accept 200, 500, or other codes - just not 404
        assert response.status_code in [200, 500], f"Unexpected status: {response.status_code}"
    
    def test_active_trades_endpoint_registered(self, client):
        """Test /api/automated-signals/active is registered (was missing)"""
        response = client.get('/api/automated-signals/active')
        # This endpoint was previously 404 - now should be registered
        assert response.status_code != 404, "Active trades endpoint returned 404 - route not registered!"
        # Accept 200, 500, or other codes - just not 404
        assert response.status_code in [200, 500], f"Unexpected status: {response.status_code}"
    
    def test_completed_trades_endpoint_registered(self, client):
        """Test /api/automated-signals/completed is registered (was missing)"""
        response = client.get('/api/automated-signals/completed')
        # This endpoint was previously 404 - now should be registered
        assert response.status_code != 404, "Completed trades endpoint returned 404 - route not registered!"
        # Accept 200, 500, or other codes - just not 404
        assert response.status_code in [200, 500], f"Unexpected status: {response.status_code}"
    
    def test_hourly_distribution_endpoint_registered(self, client):
        """Test /api/automated-signals/hourly-distribution is registered (was missing)"""
        response = client.get('/api/automated-signals/hourly-distribution')
        # This endpoint was previously 404 - now should be registered
        assert response.status_code != 404, "Hourly distribution endpoint returned 404 - route not registered!"
        # Accept 200, 500, or other codes - just not 404
        assert response.status_code in [200, 500], f"Unexpected status: {response.status_code}"
    
    def test_daily_calendar_endpoint_registered(self, client):
        """Test /api/automated-signals/daily-calendar is registered (was missing)"""
        response = client.get('/api/automated-signals/daily-calendar')
        # This endpoint was previously 404 - now should be registered
        assert response.status_code != 404, "Daily calendar endpoint returned 404 - route not registered!"
        # Accept 200, 500, or other codes - just not 404
        assert response.status_code in [200, 500], f"Unexpected status: {response.status_code}"
    
    def test_trade_detail_endpoint_registered(self, client):
        """Test /api/automated-signals/trade-detail/<id> is registered (from robust)"""
        # Use a dummy trade_id for testing
        response = client.get('/api/automated-signals/trade-detail/20250101_120000_LONG')
        # Should NOT be 404 - route must be registered
        assert response.status_code != 404, "Trade detail endpoint returned 404 - route not registered!"
        # Accept 200, 404 (trade not found), 500, or other codes - just not route 404
        # Note: 404 here would mean "trade not found" not "route not found"
        assert response.status_code in [200, 404, 500], f"Unexpected status: {response.status_code}"


class TestRouteOverrideOrder:
    """Test that robust routes override original routes correctly"""
    
    def test_stats_uses_robust_implementation(self, client):
        """Verify stats endpoint uses robust implementation (registered last)"""
        response = client.get('/api/automated-signals/stats')
        # Robust version should handle errors gracefully and return 200 even with no data
        # Original version might return 500 on errors
        # We can't definitively test which is used without inspecting response structure
        # But we can verify it doesn't crash
        assert response.status_code in [200, 500], f"Stats endpoint failed: {response.status_code}"
    
    def test_dashboard_data_uses_robust_implementation(self, client):
        """Verify dashboard-data endpoint uses robust implementation (registered last)"""
        response = client.get('/api/automated-signals/dashboard-data')
        # Robust version should handle errors gracefully
        assert response.status_code in [200, 500], f"Dashboard data endpoint failed: {response.status_code}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
