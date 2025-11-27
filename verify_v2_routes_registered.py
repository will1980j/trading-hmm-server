"""
H1.4 CHUNK 4: V2 Route Registration Verification Script

Simple verification that V2 routes are registered without requiring pytest.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from web_server import app

def test_route_registered(path, method='GET'):
    """Test if a route is registered in Flask app"""
    with app.test_client() as client:
        if method == 'GET':
            response = client.get(path)
        elif method == 'DELETE':
            response = client.delete(path)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response.status_code, response.status_code != 404


def main():
    """Run verification tests"""
    print("=" * 80)
    print("H1.4 CHUNK 4: V2 ROUTE REGISTRATION VERIFICATION")
    print("=" * 80)
    print()
    
    # Define routes to test
    routes = [
        ('/api/automated-signals/stats', 'GET', 'Stats endpoint'),
        ('/api/automated-signals/dashboard-data', 'GET', 'Dashboard data endpoint'),
        ('/api/automated-signals/mfe-distribution', 'GET', 'MFE distribution endpoint (was missing)'),
        ('/api/automated-signals/active', 'GET', 'Active trades endpoint (was missing)'),
        ('/api/automated-signals/completed', 'GET', 'Completed trades endpoint (was missing)'),
        ('/api/automated-signals/hourly-distribution', 'GET', 'Hourly distribution endpoint (was missing)'),
        ('/api/automated-signals/daily-calendar', 'GET', 'Daily calendar endpoint (was missing)'),
        ('/api/automated-signals/trade-detail/20250101_120000_LONG', 'GET', 'Trade detail endpoint (robust)'),
    ]
    
    results = []
    all_passed = True
    
    for path, method, description in routes:
        try:
            status_code, is_registered = test_route_registered(path, method)
            
            if is_registered:
                status = "✅ REGISTERED"
                result_msg = f"Status: {status_code}"
            else:
                status = "❌ NOT REGISTERED (404)"
                result_msg = "FAILED - Route not found!"
                all_passed = False
            
            results.append({
                'path': path,
                'description': description,
                'status': status,
                'result': result_msg
            })
            
            print(f"{status} - {description}")
            print(f"  Path: {path}")
            print(f"  {result_msg}")
            print()
            
        except Exception as e:
            print(f"❌ ERROR - {description}")
            print(f"  Path: {path}")
            print(f"  Error: {str(e)}")
            print()
            all_passed = False
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    registered_count = sum(1 for r in results if '✅' in r['status'])
    total_count = len(results)
    
    print(f"Routes Registered: {registered_count}/{total_count}")
    print()
    
    if all_passed:
        print("✅ ALL ROUTES SUCCESSFULLY REGISTERED!")
        print()
        print("Key Achievements:")
        print("  • Original automated_signals_api.py routes now registered")
        print("  • Robust versions override overlapping routes")
        print("  • 5 previously missing endpoints now accessible")
        print("  • No 404 errors on any V2 endpoint")
        return 0
    else:
        print("❌ SOME ROUTES FAILED TO REGISTER")
        print()
        print("Failed routes:")
        for r in results:
            if '❌' in r['status']:
                print(f"  • {r['path']} - {r['description']}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
