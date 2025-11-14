"""
Test both webhook URLs to see which one works
"""
import requests
import json

def test_webhook_url(url, name):
    """Test a webhook URL"""
    print(f"\n{'='*80}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print('='*80)
    
    # Test with sample payload
    test_payload = {
        "type": "SIGNAL_CREATED",
        "signal_id": "TEST_20251114_120000_Bullish",
        "direction": "Bullish",
        "entry_price": 16000.0,
        "stop_loss": 15950.0,
        "risk_distance": 50.0,
        "num_contracts": 1,
        "session": "NY AM",
        "htf_bias": "Bullish",
        "timestamp": 1700000000000
    }
    
    try:
        # Try POST (what TradingView sends)
        print("\n1. Testing POST request...")
        response = requests.post(url, json=test_payload, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
        if response.status_code == 200:
            print(f"   ✅ {name} WORKS!")
            return True
        else:
            print(f"   ❌ {name} returned error")
            return False
            
    except Exception as e:
        print(f"   ❌ {name} failed: {e}")
        return False

def main():
    print("\n🔍 TESTING BOTH WEBHOOK URLS\n")
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    # Test URL 1
    url1 = f"{base_url}/api/automated-signals/webhook"
    works1 = test_webhook_url(url1, "URL 1: /api/automated-signals/webhook")
    
    # Test URL 2
    url2 = f"{base_url}/api/automated-signals"
    works2 = test_webhook_url(url2, "URL 2: /api/automated-signals")
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print('='*80)
    
    if works1:
        print(f"\n✅ USE THIS URL:")
        print(f"   {url1}")
    elif works2:
        print(f"\n✅ USE THIS URL:")
        print(f"   {url2}")
    else:
        print("\n❌ NEITHER URL WORKS!")
        print("\nPossible issues:")
        print("  1. Backend not deployed")
        print("  2. Endpoint not configured")
        print("  3. Railway service down")
    
    print()

if __name__ == '__main__':
    main()
