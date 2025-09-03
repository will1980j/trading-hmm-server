import requests
import json
from datetime import datetime

def check_recent_signals():
    """Check what signals are in the database"""
    try:
        response = requests.get('https://web-production-cd33.up.railway.app/api/live-signals?timeframe=1m')
        print(f"API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            signals = data.get('signals', [])
            print(f"Total signals in DB: {len(signals)}")
            
            if signals:
                print("\nRecent signals:")
                for i, signal in enumerate(signals[:5]):
                    print(f"{i+1}. {signal.get('symbol', 'N/A')} - {signal.get('signal_type', 'N/A')} - {signal.get('timestamp', 'N/A')}")
            else:
                print("No signals found in database")
        else:
            print(f"API Error: {response.text}")
            
    except Exception as e:
        print(f"Error checking signals: {e}")

def test_webhook_simple():
    """Test webhook with simple signal"""
    url = "https://web-production-cd33.up.railway.app/api/live-signals"
    
    test_signal = {
        "symbol": "NQ1!",
        "timeframe": "1m", 
        "signal_type": "TEST_SIGNAL",
        "bias": "Bullish",
        "price": 20150.25,
        "strength": 75.0,
        "volume": 1000,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(url, json=test_signal)
        print(f"Webhook Status: {response.status_code}")
        print(f"Webhook Response: {response.json()}")
    except Exception as e:
        print(f"Webhook Error: {e}")

if __name__ == "__main__":
    print("=== Checking Recent Signals ===")
    check_recent_signals()
    
    print("\n=== Testing Webhook ===")
    test_webhook_simple()
    
    print("\n=== Checking Again After Test ===")
    check_recent_signals()