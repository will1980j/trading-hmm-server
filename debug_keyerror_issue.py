#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def debug_keyerror():
    """Debug the specific KeyError in V2 webhook"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("🔍 Debugging KeyError in V2 Webhook")
    print("=" * 45)
    
    # Test with minimal required fields
    minimal_signal = {
        "timestamp": datetime.now().isoformat(),
        "type": "Bullish",
        "price": 20150.75
    }
    
    print(f"\n1. Testing minimal signal (no session)...")
    print(f"   Signal: {minimal_signal}")
    
    try:
        response = requests.post(
            f"{base_url}/api/live-signals-v2",
            json=minimal_signal,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            v2_status = result.get('v2_automation', {})
            
            print(f"   Status: {response.status_code}")
            print(f"   V2 Success: {v2_status.get('success')}")
            print(f"   Error: {v2_status.get('error')}")
            print(f"   Error Type: {v2_status.get('error_type')}")
            
    except Exception as e:
        print(f"   Connection Error: {e}")
    
    # Test with all fields
    complete_signal = {
        "timestamp": datetime.now().isoformat(),
        "type": "Bullish",
        "price": 20150.75,
        "session": "NY AM",
        "timeframe": "1m",
        "source": "TradingView"
    }
    
    print(f"\n2. Testing complete signal...")
    print(f"   Signal: {complete_signal}")
    
    try:
        response = requests.post(
            f"{base_url}/api/live-signals-v2",
            json=complete_signal,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            v2_status = result.get('v2_automation', {})
            
            print(f"   Status: {response.status_code}")
            print(f"   V2 Success: {v2_status.get('success')}")
            print(f"   Error: {v2_status.get('error')}")
            print(f"   Error Type: {v2_status.get('error_type')}")
            
    except Exception as e:
        print(f"   Connection Error: {e}")
    
    # Test with different signal types
    bearish_signal = {
        "timestamp": datetime.now().isoformat(),
        "type": "Bearish",
        "price": 20150.75,
        "session": "NY AM"
    }
    
    print(f"\n3. Testing bearish signal...")
    print(f"   Signal: {bearish_signal}")
    
    try:
        response = requests.post(
            f"{base_url}/api/live-signals-v2",
            json=bearish_signal,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            v2_status = result.get('v2_automation', {})
            
            print(f"   Status: {response.status_code}")
            print(f"   V2 Success: {v2_status.get('success')}")
            print(f"   Error: {v2_status.get('error')}")
            print(f"   Error Type: {v2_status.get('error_type')}")
            
    except Exception as e:
        print(f"   Connection Error: {e}")
    
    print(f"\n" + "=" * 45)
    print(f"🎯 KEYERROR ANALYSIS:")
    print(f"   The KeyError suggests missing dictionary key")
    print(f"   Likely candidates:")
    print(f"   - targets['1R'], targets['2R'], etc.")
    print(f"   - signal_result['session']")
    print(f"   - Missing field in database insert")
    
    print(f"\n🔧 NEXT STEPS:")
    print(f"   1. Check targets dictionary initialization")
    print(f"   2. Verify signal_result field access")
    print(f"   3. Check database insert parameter mapping")

if __name__ == "__main__":
    debug_keyerror()