"""
Test Robust Automated Signals Solution
Comprehensive testing of all components
"""

import requests
import time
import json

BASE_URL = 'https://web-production-cd33.up.railway.app'

def test_api_endpoints():
    """Test all API endpoints"""
    print("=" * 80)
    print("TEST 1: API ENDPOINTS")
    print("=" * 80)
    
    endpoints = [
        '/api/automated-signals/dashboard-data',
        '/api/automated-signals/stats',
        '/api/automated-signals/active',
        '/api/automated-signals/completed'
    ]
    
    results = []
    for endpoint in endpoints:
        try:
            response = requests.get(f'{BASE_URL}{endpoint}', timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                print(f"✓ {endpoint}")
                print(f"  Status: {response.status_code}")
                print(f"  Keys: {list(data.keys())}")
            else:
                print(f"✗ {endpoint}")
                print(f"  Status: {response.status_code}")
                print(f"  Error: {response.text[:100]}")
            
            results.append(success)
            
        except Exception as e:
            print(f"✗ {endpoint}")
            print(f"  Exception: {e}")
            results.append(False)
    
    return all(results)

def test_dashboard_page():
    """Test dashboard page loads"""
    print("\n" + "=" * 80)
    print("TEST 2: DASHBOARD PAGE")
    print("=" * 80)
    
    try:
        response = requests.get(f'{BASE_URL}/automated-signals', timeout=10)
        success = response.status_code == 200
        
        if success:
            print("✓ Dashboard page loads")
            print(f"  Status: {response.status_code}")
            print(f"  Content length: {len(response.text)} bytes")
            
            # Check for robust WebSocket client
            if 'RobustWebSocketClient' in response.text:
                print("✓ Robust WebSocket client included")
            else:
                print("✗ Robust WebSocket client NOT found")
                success = False
                
        else:
            print("✗ Dashboard page failed")
            print(f"  Status: {response.status_code}")
        
        return success
        
    except Exception as e:
        print(f"✗ Dashboard page error: {e}")
        return False

def test_static_files():
    """Test static files are accessible"""
    print("\n" + "=" * 80)
    print("TEST 3: STATIC FILES")
    print("=" * 80)
    
    try:
        response = requests.get(f'{BASE_URL}/static/websocket_client_robust.js', timeout=10)
        success = response.status_code == 200
        
        if success:
            print("✓ Robust WebSocket client accessible")
            print(f"  Status: {response.status_code}")
            print(f"  Size: {len(response.text)} bytes")
            
            # Check for key functions
            if 'RobustWebSocketClient' in response.text:
                print("✓ RobustWebSocketClient class found")
            else:
                print("✗ RobustWebSocketClient class NOT found")
                success = False
                
        else:
            print("✗ Static file not accessible")
            print(f"  Status: {response.status_code}")
        
        return success
        
    except Exception as e:
        print(f"✗ Static file error: {e}")
        return False

def test_data_structure():
    """Test API returns proper data structure"""
    print("\n" + "=" * 80)
    print("TEST 4: DATA STRUCTURE")
    print("=" * 80)
    
    try:
        response = requests.get(f'{BASE_URL}/api/automated-signals/dashboard-data', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            required_keys = ['success', 'active_trades', 'completed_trades', 'stats', 
                           'hourly_distribution', 'session_breakdown', 'timestamp']
            
            missing_keys = [key for key in required_keys if key not in data]
            
            if not missing_keys:
                print("✓ All required keys present")
                print(f"  Active trades: {len(data['active_trades'])}")
                print(f"  Completed trades: {len(data['completed_trades'])}")
                print(f"  Stats: {data['stats']}")
                
                if 'debug_info' in data:
                    print(f"  Debug info: {data['debug_info']}")
                
                return True
            else:
                print(f"✗ Missing keys: {missing_keys}")
                return False
        else:
            print(f"✗ API request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Data structure test error: {e}")
        return False

def print_summary(results):
    """Print test summary"""
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    test_names = [
        "API Endpoints",
        "Dashboard Page",
        "Static Files",
        "Data Structure"
    ]
    
    for name, result in zip(test_names, results):
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(results)
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print("Robust solution is working correctly!")
    else:
        print("✗ SOME TESTS FAILED")
        print("Review failures above and check deployment")
    print("=" * 80)
    
    return all_passed

if __name__ == "__main__":
    print("ROBUST AUTOMATED SIGNALS SOLUTION - COMPREHENSIVE TEST")
    print("Testing production deployment at:", BASE_URL)
    print()
    
    results = []
    
    # Run all tests
    results.append(test_api_endpoints())
    results.append(test_dashboard_page())
    results.append(test_static_files())
    results.append(test_data_structure())
    
    # Print summary
    all_passed = print_summary(results)
    
    # Exit code
    exit(0 if all_passed else 1)
