#!/usr/bin/env python3

import requests
from datetime import datetime

def check_deployment():
    """Check what's currently deployed"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("🔍 Checking Current Deployment")
    print("=" * 40)
    
    # Test with exact TradingView format
    tradingview_signal = {
        "timestamp": datetime.now().isoformat(),
        "type": "Bullish",  # Exact capitalization
        "price": 20150.75,
        "session": "NY AM"
    }
    
    print("\n📡 Testing exact TradingView format...")
    try:
        response = requests.post(
            f"{base_url}/api/live-signals-v2",
            json=tradingview_signal,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Full response: {json.dumps(result, indent=2)}")
            
            v2_status = result.get('v2_automation', {})
            if v2_status.get('success'):
                print("✅ V2 AUTOMATION WORKING!")
            else:
                print(f"❌ V2 Issue: {v2_status}")
        else:
            print(f"❌ HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 40)

if __name__ == "__main__":
    import json
    check_deployment()