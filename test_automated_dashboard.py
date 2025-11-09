"""
Test the automated signals dashboard deployment
"""
import requests
import time

BASE_URL = "https://web-production-cd33.up.railway.app"

def test_dashboard_route():
    """Test if the dashboard route is accessible"""
    print("🧪 Testing dashboard route...")
    
    try:
        response = requests.get(f"{BASE_URL}/automated-signals", allow_redirects=False)
        
        if response.status_code == 302:
            print("✅ Dashboard route exists (redirects to login as expected)")
            return True
        elif response.status_code == 200:
            print("✅ Dashboard route accessible")
            return True
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing dashboard route: {e}")
        return False

def test_api_endpoint():
    """Test if the API endpoint exists"""
    print("\n🧪 Testing API endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/automated-signals/recent")
        
        if response.status_code == 401:
            print("✅ API endpoint exists (requires authentication)")
            return True
        elif response.status_code == 200:
            print("✅ API endpoint accessible")
            data = response.json()
            print(f"   Signals returned: {data.get('count', 0)}")
            return True
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API endpoint: {e}")
        return False

def test_webhook_endpoint():
    """Test if the webhook endpoint still works"""
    print("\n🧪 Testing webhook endpoint...")
    
    try:
        test_payload = {
            "event": "entry",
            "direction": "Bullish",
            "entry_price": 16500.00,
            "stop_loss": 16475.00,
            "session": "NY AM",
            "bias": "Bullish",
            "timestamp": int(time.time() * 1000)
        }
        
        response = requests.post(
            f"{BASE_URL}/api/automated-signals",
            json=test_payload
        )
        
        if response.status_code == 200:
            print("✅ Webhook endpoint working")
            return True
        else:
            print(f"⚠️  Webhook returned status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 AUTOMATED SIGNALS DASHBOARD - DEPLOYMENT TEST")
    print("=" * 60)
    print(f"\nTesting: {BASE_URL}")
    print()
    
    results = []
    
    # Run tests
    results.append(("Dashboard Route", test_dashboard_route()))
    results.append(("API Endpoint", test_api_endpoint()))
    results.append(("Webhook Endpoint", test_webhook_endpoint()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\n📍 Dashboard URL:")
        print(f"   {BASE_URL}/automated-signals")
        print("\n📍 API Endpoint:")
        print(f"   {BASE_URL}/api/automated-signals/recent")
    else:
        print("⚠️  SOME TESTS FAILED - Check deployment")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())
