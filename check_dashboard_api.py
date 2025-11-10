"""
Check the automated signals dashboard API
"""
import requests

# Test the API endpoint
url = "https://web-production-cd33.up.railway.app/api/automated-signals/recent"

print("🔍 Checking Automated Signals API...\n")

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text[:500]}")  # First 500 chars
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"\n✅ API Response:")
            print(f"Success: {data.get('success')}")
            
            signals = data.get('signals', [])
            print(f"\n📊 Found {len(signals)} signals:\n")
            
            for signal in signals:
                print(f"Trade ID: {signal.get('trade_id')}")
                print(f"  Event: {signal.get('event_type')}")
                print(f"  Direction: {signal.get('direction')}")
                print(f"  Entry: {signal.get('entry_price')}")
                print(f"  Stop Loss: {signal.get('stop_loss')}")
                print(f"  MFE: {signal.get('mfe')}")
                print(f"  Status: {signal.get('status')}")
                print(f"  Timestamp: {signal.get('timestamp')}")
                print()
        except:
            print("\n⚠️ Response is not JSON (probably login redirect)")
    else:
        print(f"\n❌ Error Response:")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n🌐 Dashboard URL:")
print("https://web-production-cd33.up.railway.app/automated-signals-dashboard")
