import requests
import json

# Test webhook endpoint
def test_live_signal():
    url = "https://web-production-cd33.up.railway.app/api/live-signals"
    
    test_signal = {
        "symbol": "NQ1!",
        "timeframe": "1m", 
        "signal_type": "BULLISH_FVG",
        "bias": "Bullish",
        "price": 20150.25,
        "strength": 85.5,
        "volume": 1250,
        "ath": 20200.0,
        "atl": 20100.0,
        "fvg_high": 20155.0,
        "fvg_low": 20145.0,
        "timestamp": "1703123456789"
    }
    
    response = requests.post(url, json=test_signal)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    test_live_signal()