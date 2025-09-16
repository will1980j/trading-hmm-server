#!/usr/bin/env python3
"""
Simple Signal Lab Population Test
"""

import requests
import json
from datetime import datetime

RAILWAY_URL = "https://web-production-cd33.up.railway.app"

def send_test_signal():
    """Send a test signal that should populate Signal Lab"""
    
    # Perfect test signal for Signal Lab auto-population
    test_signal = {
        "bias": "Bullish",
        "price": 20150.25,
        "strength": 85,
        "symbol": "NQ1!",
        "htf_aligned": True,
        "htf_status": "ALIGNED",
        "timeframe": "1m",
        "signal_type": "BIAS_BULLISH"
    }
    
    print("Sending test NQ HTF aligned signal...")
    print(f"Signal: {json.dumps(test_signal, indent=2)}")
    
    try:
        response = requests.post(
            f"{RAILWAY_URL}/api/live-signals",
            json=test_signal,
            timeout=10
        )
        
        print(f"\\nWebhook Response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"Message: {data.get('message')}")
            
            # Check if Signal Lab was mentioned
            message = data.get('message', '')
            if 'Signal Lab' in message or 'auto-populated' in message:
                print("SUCCESS: Signal Lab auto-population mentioned!")
                return True
            else:
                print("WARNING: No Signal Lab auto-population mentioned")
                print("This suggests the auto-population logic may not be working")
                return False
        else:
            print(f"ERROR: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def check_current_setup():
    """Check what might be preventing Signal Lab population"""
    
    print("\\n" + "="*50)
    print("SIGNAL LAB AUTO-POPULATION REQUIREMENTS")
    print("="*50)
    
    print("\\nFor signals to auto-populate 1m Signal Lab:")
    print("1. Symbol must be NQ1! (or current active NQ contract)")
    print("2. htf_aligned must be true")
    print("3. Webhook must reach: /api/live-signals")
    
    print("\\nCommon issues:")
    print("- TradingView not sending htf_aligned: true")
    print("- Pine Script filtering out signals before sending")
    print("- Contract rollover (NQ1! vs NQZ24, etc.)")
    print("- Database connection issues")
    
    print("\\nTo debug:")
    print("1. Check TradingView alert history")
    print("2. Verify Pine Script HTF filter logic")
    print("3. Check server logs for auto-population messages")

if __name__ == "__main__":
    print("Signal Lab Population Test")
    print("="*30)
    
    success = send_test_signal()
    
    if success:
        print("\\nTest signal sent successfully!")
        print("Check your Signal Lab dashboard to see if it populated.")
    else:
        print("\\nTest signal failed or didn't mention Signal Lab.")
        
    check_current_setup()