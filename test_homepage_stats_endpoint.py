"""
Test script for /api/homepage-stats endpoint
Verifies the unified homepage statistics endpoint
"""

import requests
import json
from datetime import datetime

def test_homepage_stats():
    """Test the homepage stats endpoint"""
    
    # Test against production
    base_url = "https://web-production-cd33.up.railway.app"
    endpoint = f"{base_url}/api/homepage-stats"
    
    print("=" * 80)
    print("TESTING /api/homepage-stats ENDPOINT")
    print("=" * 80)
    print(f"\nEndpoint: {endpoint}")
    print(f"Time: {datetime.now().isoformat()}\n")
    
    try:
        response = requests.get(endpoint, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response.elapsed.total_seconds():.2f}s\n")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ SUCCESS - Response received\n")
            print("Response Data:")
            print(json.dumps(data, indent=2))
            
            # Validate required fields
            print("\n" + "=" * 80)
            print("FIELD VALIDATION")
            print("=" * 80)
            
            required_fields = [
                'current_session',
                'signals_today',
                'last_signal_time',
                'webhook_health',
                'server_time_ny'
            ]
            
            all_present = True
            for field in required_fields:
                present = field in data
                status = "✅" if present else "❌"
                value = data.get(field, "MISSING")
                print(f"{status} {field}: {value}")
                if not present:
                    all_present = False
            
            # Validate session value
            print("\n" + "=" * 80)
            print("SESSION VALIDATION")
            print("=" * 80)
            
            valid_sessions = ["ASIA", "LONDON", "NY PRE", "NY AM", "NY LUNCH", "NY PM", "CLOSED"]
            session = data.get('current_session')
            if session in valid_sessions:
                print(f"✅ Valid session: {session}")
            else:
                print(f"❌ Invalid session: {session}")
                print(f"   Expected one of: {', '.join(valid_sessions)}")
            
            # Validate webhook health
            print("\n" + "=" * 80)
            print("WEBHOOK HEALTH VALIDATION")
            print("=" * 80)
            
            valid_health = ["OK", "WARNING", "CRITICAL", "NO_DATA"]
            health = data.get('webhook_health')
            if health in valid_health:
                print(f"✅ Valid webhook health: {health}")
            else:
                print(f"❌ Invalid webhook health: {health}")
                print(f"   Expected one of: {', '.join(valid_health)}")
            
            # Validate signals today
            print("\n" + "=" * 80)
            print("SIGNALS TODAY VALIDATION")
            print("=" * 80)
            
            signals = data.get('signals_today')
            if isinstance(signals, int) and signals >= 0:
                print(f"✅ Valid signals count: {signals}")
            else:
                print(f"❌ Invalid signals count: {signals}")
            
            # Summary
            print("\n" + "=" * 80)
            print("TEST SUMMARY")
            print("=" * 80)
            
            if all_present and session in valid_sessions and health in valid_health:
                print("✅ ALL TESTS PASSED")
                print("\nEndpoint is ready for production use!")
            else:
                print("❌ SOME TESTS FAILED")
                print("\nPlease review the validation errors above.")
            
        else:
            print(f"❌ ERROR - Status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ ERROR - Request timed out after 10 seconds")
    except requests.exceptions.ConnectionError:
        print("❌ ERROR - Could not connect to server")
    except Exception as e:
        print(f"❌ ERROR - {str(e)}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_homepage_stats()
