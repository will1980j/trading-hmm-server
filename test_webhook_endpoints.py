"""
Test both webhook endpoints to verify they work
"""
import requests
import json
from datetime import datetime

def test_webhook_endpoints():
    """Test both webhook URLs"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    # Test payload matching indicator format
    test_payload = {
        "type": "ENTRY",
        "signal_id": f"TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}_BULLISH",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "bias": "Bullish",
        "session": "NY AM",
        "entry_price": 4500.0,
        "sl_price": 4475.0,
        "risk_distance": 25.0,
        "be_price": 4500.0,
        "target_1r": 4525.0,
        "target_2r": 4550.0,
        "target_3r": 4575.0,
        "be_hit": False,
        "be_mfe": 0.0,
        "no_be_mfe": 0.0,
        "status": "active",
        "timestamp": int(datetime.now().timestamp() * 1000)
    }
    
    endpoints = [
        "/api/automated-signals",
        "/api/automated-signals/webhook"
    ]
    
    print("\n" + "="*80)
    print("TESTING WEBHOOK ENDPOINTS")
    print("="*80)
    
    for endpoint in endpoints:
        url = base_url + endpoint
        print(f"\nTesting: {url}")
        print("-"*80)
        
        try:
            response = requests.post(
                url,
                json=test_payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✓ SUCCESS - Endpoint is working!")
                try:
                    result = response.json()
                    print(f"Response: {json.dumps(result, indent=2)}")
                except:
                    print(f"Response: {response.text}")
            elif response.status_code == 405:
                print("❌ FAIL - Method Not Allowed (endpoint doesn't exist)")
                print("This endpoint needs to be added to web_server.py")
            elif response.status_code == 401:
                print("⚠️  AUTHENTICATION REQUIRED")
                print("Endpoint exists but requires login")
                print("This is OK for testing - TradingView webhooks don't need auth")
            else:
                print(f"⚠️  Unexpected status: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print("❌ TIMEOUT - Server took too long to respond")
        except requests.exceptions.ConnectionError:
            print("❌ CONNECTION ERROR - Could not reach server")
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    print("\nExpected Results:")
    print("  - Both endpoints should return 200 OK")
    print("  - Both should accept the test payload")
    print("  - Both should insert data into database")
    print("\nIf one returns 405, that endpoint doesn't exist yet.")
    print("Deploy the fix to add the missing endpoint.")

if __name__ == "__main__":
    test_webhook_endpoints()
