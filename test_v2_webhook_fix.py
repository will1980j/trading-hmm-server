#!/usr/bin/env python3

import requests
import json
import time

def test_v2_webhook_fix():
    """Test the V2 webhook after fixing the database schema issues"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("🔧 TESTING V2 WEBHOOK FIXES")
    print("=" * 50)
    
    # Test with different signal formats
    test_signals = [
        {
            "name": "Standard format",
            "data": {
                "signal": "bullish",
                "price": 20500.75,
                "timestamp": int(time.time() * 1000),
                "session": "NY AM",
                "symbol": "NQ"
            }
        },
        {
            "name": "Type format",
            "data": {
                "type": "Bullish",
                "price": 20501.25,
                "timestamp": int(time.time() * 1000),
                "session": "NY AM",
                "symbol": "NQ"
            }
        },
        {
            "name": "Signal_type format",
            "data": {
                "signal_type": "bearish",
                "price": 20499.50,
                "timestamp": int(time.time() * 1000),
                "session": "NY PM",
                "symbol": "NQ"
            }
        }
    ]
    
    for test in test_signals:
        print(f"📡 Testing {test['name']}...")
        try:
            response = requests.post(
                f"{base_url}/api/live-signals-v2",
                json=test['data'],
                timeout=10
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                v2_automation = data.get("v2_automation", {})
                
                if v2_automation.get("success"):
                    print("   ✅ SUCCESS! Signal processed and trade created")
                    print(f"   Trade ID: {v2_automation.get('trade_id')}")
                    print(f"   Trade UUID: {v2_automation.get('trade_uuid')}")
                else:
                    print("   ❌ FAILED - V2 automation unsuccessful")
                    print(f"   Reason: {v2_automation.get('reason', 'Unknown')}")
                    if 'error' in v2_automation:
                        print(f"   Error: {v2_automation['error']}")
            else:
                print(f"   ❌ HTTP Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        print()
    
    # Now test if stats endpoint works
    print("📊 Testing V2 stats after webhook fixes...")
    try:
        response = requests.get(f"{base_url}/api/v2/stats", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "error" in data and "Database query failed" in str(data.get("error")):
                print("   ❌ Stats still failing - database query error")
            else:
                print("   ✅ Stats working!")
                print(f"   Total signals: {data.get('total_signals', 0)}")
                print(f"   Active trades: {data.get('active_trades', 0)}")
        else:
            print(f"   ❌ Stats error: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Stats exception: {e}")
    
    print()
    print("=" * 50)
    print("🎯 WEBHOOK FIX TEST COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    test_v2_webhook_fix()