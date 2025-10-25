#!/usr/bin/env python3
"""
Test Single Endpoint - Quick test of one V2 endpoint
"""

import requests

def test_single_endpoint():
    """Test just one V2 endpoint quickly"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("🧪 QUICK V2 ENDPOINT TEST")
    print("=" * 30)
    
    # Test the webhook endpoint (no auth required)
    webhook_data = {
        "type": "Bullish",
        "price": 20000
    }
    
    try:
        print("📡 Testing V2 webhook...")
        response = requests.post(
            f"{base_url}/api/live-signals-v2",
            json=webhook_data,
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Webhook working!")
            
            v2_auto = data.get('v2_automation', {})
            if v2_auto.get('success'):
                print(f"🎉 V2 AUTOMATION SUCCESS!")
                print(f"Trade ID: {v2_auto.get('trade_id')}")
            else:
                print(f"❌ V2 automation error: {v2_auto.get('error')}")
        else:
            print(f"❌ Failed: {response.text[:100]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_single_endpoint()