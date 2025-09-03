import requests
import json
from datetime import datetime

def test_webhook_direct():
    """Test webhook endpoint directly"""
    url = "https://web-production-cd33.up.railway.app/api/live-signals"
    
    # Test with minimal signal data
    test_signals = [
        {
            "symbol": "NQ1!",
            "timeframe": "1m",
            "signal_type": "BULLISH_FVG", 
            "bias": "Bullish",
            "price": 20150.25,
            "strength": 85.0,
            "volume": 1250,
            "timestamp": datetime.now().isoformat()
        },
        {
            "symbol": "ES1!",
            "timeframe": "1m",
            "signal_type": "BEARISH_FVG",
            "bias": "Bearish", 
            "price": 5125.75,
            "strength": 72.0,
            "volume": 980,
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    print("Testing webhook endpoint...")
    
    for i, signal in enumerate(test_signals):
        try:
            print(f"\nSending signal {i+1}: {signal['symbol']} {signal['signal_type']}")
            
            response = requests.post(url, json=signal, timeout=10)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("✅ Signal sent successfully!")
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    # Test getting signals back
    print("\n" + "="*50)
    print("Testing signal retrieval...")
    
    try:
        get_response = requests.get(f"{url}?timeframe=1m", timeout=10)
        print(f"GET Status: {get_response.status_code}")
        
        if get_response.status_code == 200:
            data = get_response.json()
            signals = data.get('signals', [])
            print(f"Retrieved {len(signals)} signals from database")
            
            if signals:
                latest = signals[0]
                print(f"Latest signal: {latest.get('symbol')} {latest.get('signal_type')} at {latest.get('price')}")
            else:
                print("No signals found in database")
        else:
            print(f"GET Error: {get_response.text}")
            
    except Exception as e:
        print(f"❌ GET request failed: {e}")

if __name__ == "__main__":
    test_webhook_direct()