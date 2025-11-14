"""
Fix the automated_signals table schema
"""
import requests

def fix_schema():
    """Call the fix-schema endpoint"""
    print("=" * 80)
    print("FIXING AUTOMATED_SIGNALS TABLE SCHEMA")
    print("=" * 80)
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("\n📝 Adding missing columns to automated_signals table...")
    print("   - be_mfe")
    print("   - no_be_mfe")
    
    try:
        response = requests.post(f"{base_url}/api/automated-signals/fix-schema", timeout=30)
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ Schema fixed successfully!")
            
            # Test with a signal now
            print("\n🧪 Testing with a signal...")
            test_payload = {
                "type": "ENTRY",
                "signal_id": "TEST_20251114_142000_BULLISH",
                "direction": "Bullish",
                "entry_price": 25000.0,
                "stop_loss": 24975.0,
                "risk_distance": 25.0,
                "num_contracts": 1,
                "session": "NY AM",
                "htf_bias": "Bullish",
                "timestamp": 1731585600000
            }
            
            test_response = requests.post(
                f"{base_url}/api/automated-signals/webhook",
                json=test_payload,
                timeout=10
            )
            
            print(f"Test webhook status: {test_response.status_code}")
            
            if test_response.status_code == 200:
                # Check if it was stored
                stats_response = requests.get(f"{base_url}/api/automated-signals/stats-live", timeout=10)
                if stats_response.status_code == 200:
                    data = stats_response.json()
                    print(f"Total signals in database: {data.get('total_signals', 0)}")
                    
                    if data.get('total_signals', 0) > 0:
                        print("\n🎉 SUCCESS! Signals are now being stored!")
                        print("\n✅ Your TradingView alerts should now work!")
                    else:
                        print("\n⚠️  Still not storing... checking further...")
        else:
            print(f"\n❌ Schema fix failed: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

def main():
    fix_schema()

if __name__ == '__main__':
    main()
