#!/usr/bin/env python3
"""
Check Signal Flow - Direct webhook test to diagnose Signal Lab population
"""

import requests
import json
from datetime import datetime

RAILWAY_URL = "https://web-production-cd33.up.railway.app"

def test_signal_flow():
    """Test the complete signal flow"""
    print("Testing Signal Flow to 1m Signal Lab")
    print("=" * 40)
    
    # Test 1: Send a test NQ HTF aligned signal
    test_signal = {
        "bias": "Bullish",
        "price": 20150.25,
        "strength": 75,
        "symbol": "NQ1!",
        "htf_aligned": True,
        "htf_status": "ALIGNED", 
        "timeframe": "1m",
        "signal_type": "BIAS_BULLISH"
    }
    
    print("\\n1. Sending test NQ HTF aligned signal...")
    try:
        response = requests.post(
            f"{RAILWAY_URL}/api/live-signals",
            json=test_signal,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data.get('status', 'unknown')}")
            print(f"   Message: {data.get('message', 'no message')[:100]}")
            
            # Check if it mentions Signal Lab auto-population
            message = data.get('message', '')
            if 'Signal Lab' in message or 'auto-populated' in message:
                print("   ✓ Signal Lab auto-population mentioned")
            else:
                print("   ✗ No Signal Lab auto-population mentioned")
                
        else:
            print(f"   Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Send signal with different contract (should not populate)
    test_signal_wrong_contract = {
        "bias": "Bearish", 
        "price": 5500.75,
        "strength": 80,
        "symbol": "ES1!",  # Different contract
        "htf_aligned": True,
        "timeframe": "1m"
    }
    
    print("\\n2. Sending ES signal (should not populate NQ Signal Lab)...")
    try:
        response = requests.post(
            f"{RAILWAY_URL}/api/live-signals",
            json=test_signal_wrong_contract,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            message = data.get('message', '')
            if 'Signal Lab' in message:
                print("   ✗ Incorrectly populated Signal Lab")
            else:
                print("   ✓ Correctly did not populate Signal Lab")
                
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Send NQ signal without HTF alignment (should not populate)
    test_signal_no_htf = {
        "bias": "Bullish",
        "price": 20155.50, 
        "strength": 60,
        "symbol": "NQ1!",
        "htf_aligned": False,  # Not HTF aligned
        "timeframe": "1m"
    }
    
    print("\\n3. Sending NQ signal without HTF alignment (should not populate)...")
    try:
        response = requests.post(
            f"{RAILWAY_URL}/api/live-signals",
            json=test_signal_no_htf,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            message = data.get('message', '')
            if 'Signal Lab' in message:
                print("   ✗ Incorrectly populated Signal Lab (no HTF alignment)")
            else:
                print("   ✓ Correctly did not populate Signal Lab (no HTF alignment)")
                
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Check webhook endpoint format
    print("\\n4. Testing TradingView webhook format...")
    
    # Simulate TradingView alert message format
    tv_alert = 'SIGNAL:Bullish:20160.25:85:ALIGNED:ALIGNED:' + datetime.now().isoformat()
    
    try:
        response = requests.post(
            f"{RAILWAY_URL}/api/live-signals",
            data=tv_alert,
            headers={'Content-Type': 'text/plain'},
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            message = data.get('message', '')
            print(f"   Message: {message[:100]}")
            
    except Exception as e:
        print(f"   Error: {e}")

def check_webhook_url():
    """Provide webhook setup instructions"""
    print("\\n" + "=" * 50)
    print("WEBHOOK SETUP INSTRUCTIONS")
    print("=" * 50)
    print("\\nIn TradingView Pine Script alert:")
    print("1. Webhook URL: https://web-production-cd33.up.railway.app/api/live-signals")
    print("\\n2. Message format (JSON):")
    print('{')
    print('  "bias": "{{strategy.position_size > 0 ? \\"Bullish\\" : \\"Bearish\\"}}",')
    print('  "price": {{close}},')
    print('  "strength": 75,')
    print('  "symbol": "{{syminfo.ticker}}",')
    print('  "htf_aligned": true,')
    print('  "timeframe": "1m"')
    print('}')
    print("\\n3. Or simple format:")
    print('SIGNAL:{{strategy.position_size > 0 ? "Bullish" : "Bearish"}}:{{close}}:75:ALIGNED:ALIGNED:{{time}}')
    
    print("\\nFor Signal Lab auto-population, ensure:")
    print("- Symbol is NQ1! (or current NQ contract)")
    print("- htf_aligned is true")
    print("- Pine Script only sends HTF aligned signals")

if __name__ == "__main__":
    test_signal_flow()
    check_webhook_url()