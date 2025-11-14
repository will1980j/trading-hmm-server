"""
Test webhook with the EXACT payload from TradingView alerts
"""
import requests
import json

def test_exact_tradingview_payload():
    """Test with exact payload format from the screenshot"""
    print("=" * 80)
    print("TESTING WITH EXACT TRADINGVIEW PAYLOAD")
    print("=" * 80)
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    # This is the EXACT format from your screenshot
    payload = {
        "type": "ENTRY",
        "signal_id": "20251114_041600000_BEARISH",
        "date": "2025-11-14",
        "time": "05:15:00",
        "bias": "Bearish",
        "session": "LONDON",
        "entry_price": 24968,
        "sl_price": 24986.75,
        "be_price": 24968,
        "target_1r": 24949.25,
        "target_2r": 24930.5,
        "target_3r": 24911.75,
        "target_5r": 24874.25,
        "target_10r": 24780.5,
        "target_20r": 24593,
        "lowest_low": 24954,
        "highest_high": 24979.75,
        "status": "active",
        "timestamp": 1763115840000
    }
    
    print("\n📤 Sending payload:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(
            f"{base_url}/api/automated-signals/webhook",
            json=payload,
            timeout=10
        )
        
        print(f"\n📥 Response:")
        print(f"Status: {response.status_code}")
        print(f"Body: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('success'):
                print("\n✅ Webhook accepted!")
                
                # Check if stored
                print("\n🔍 Checking database...")
                stats = requests.get(f"{base_url}/api/automated-signals/stats-live", timeout=10)
                if stats.status_code == 200:
                    data = stats.json()
                    print(f"Total signals: {data.get('total_signals', 0)}")
                    
                    if data.get('total_signals', 0) > 0:
                        print("\n🎉 SUCCESS! Signal was stored!")
                        
                        # Get the actual signal
                        dashboard = requests.get(f"{base_url}/api/automated-signals/dashboard-data", timeout=10)
                        if dashboard.status_code == 200:
                            dash_data = dashboard.json()
                            active = dash_data.get('active_trades', [])
                            if active:
                                print(f"\n📊 Active trade found:")
                                print(json.dumps(active[0], indent=2))
                    else:
                        print("\n❌ Signal NOT stored despite success response!")
                        print("\nThis means the INSERT is failing silently.")
                        print("Check Railway logs for the actual error.")
            else:
                print(f"\n❌ Webhook returned error: {response_data.get('error')}")
        else:
            print(f"\n❌ HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ Request failed: {e}")

def main():
    test_exact_tradingview_payload()
    
    print("\n" + "=" * 80)
    print("DIAGNOSIS")
    print("=" * 80)
    print("\nIf webhook returns success but signal not stored:")
    print("  → INSERT is failing but error is being caught")
    print("  → Check Railway deployment logs")
    print("  → Likely issue: Missing column or data type mismatch")

if __name__ == '__main__':
    main()
