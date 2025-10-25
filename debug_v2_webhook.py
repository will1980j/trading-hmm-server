#!/usr/bin/env python3
"""
Debug V2 webhook to see exact error
"""

import requests
import json

def debug_v2_webhook():
    """Debug V2 webhook to see what's failing"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("🔧 DEBUGGING V2 WEBHOOK")
    print("=" * 40)
    
    webhook_data = {
        "type": "Bullish",
        "price": 20000,
        "session": "NY PM"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/live-signals-v2",
            json=webhook_data,
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Full response:")
            print(json.dumps(data, indent=2))
            
            v2_auto = data.get('v2_automation', {})
            if not v2_auto.get('success'):
                print(f"\nV2 Error: {v2_auto.get('error', 'Unknown')}")
                print(f"V2 Reason: {v2_auto.get('reason', 'Unknown')}")
                
        else:
            print(f"Failed: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_v2_webhook()