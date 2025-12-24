"""
Test the new fingerprint debug endpoint.
Verifies we can identify which alert source is sending fake OHLC data.
"""
import requests
import json

BASE_URL = "https://web-production-f8c3.up.railway.app"

def test_fingerprint_endpoint():
    """Test the /api/indicator-export/debug/latest-fingerprint endpoint"""
    
    print("=" * 80)
    print("FINGERPRINT DEBUG TEST")
    print("=" * 80)
    
    url = f"{BASE_URL}/api/indicator-export/debug/latest-fingerprint"
    
    print(f"\n📡 Fetching: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"\n✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n" + "=" * 80)
            print("FINGERPRINT RESULTS")
            print("=" * 80)
            
            print(f"\n📦 Batch ID: {data.get('id')}")
            print(f"⏰ Received At: {data.get('received_at')}")
            print(f"🎯 Symbol: {data.get('symbol')}")
            print(f"📊 Bar Timestamp: {data.get('bar_ts')}")
            
            print(f"\n🔑 Payload Keys: {data.get('payload_keys')}")
            print(f"🔐 SHA256 Hash: {data.get('payload_sha256')}")
            
            print(f"\n🐛 Has debug_payload_version: {data.get('has_debug_payload_version')}")
            print(f"🐛 Debug Version: {data.get('debug_payload_version')}")
            
            ohlc = data.get('ohlc', {})
            print(f"\n📈 OHLC Data:")
            print(f"   Open:  {ohlc.get('o')}")
            print(f"   High:  {ohlc.get('h')}")
            print(f"   Low:   {ohlc.get('l')}")
            print(f"   Close: {ohlc.get('c')}")
            
            is_fake = data.get('is_fake_ohlc', False)
            print(f"\n⚠️  Is Fake OHLC (1/2/0.5/1.5): {is_fake}")
            
            if is_fake:
                print("\n" + "🚨" * 40)
                print("FAKE OHLC DETECTED!")
                print("This alert is sending dummy data (1/2/0.5/1.5)")
                print("Check TradingView alert configuration!")
                print("🚨" * 40)
            else:
                print("\n✅ OHLC looks legitimate (not the fake 1/2/0.5/1.5 pattern)")
            
            print(f"\n🕐 Server Time: {data.get('server_now')}")
            
            # Pretty print full response
            print("\n" + "=" * 80)
            print("FULL JSON RESPONSE")
            print("=" * 80)
            print(json.dumps(data, indent=2))
            
        elif response.status_code == 404:
            print("\n⚠️  No UNIFIED_SNAPSHOT_V1 batches found in database")
            print("Wait for the next alert to fire from TradingView")
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.Timeout:
        print("\n❌ Request timed out")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_fingerprint_endpoint()
