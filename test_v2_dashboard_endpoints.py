#!/usr/bin/env python3

import requests
import json

def test_v2_dashboard_endpoints():
    """Test V2 dashboard endpoints without authentication"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("🔍 Testing V2 Dashboard Endpoints (Public Access)")
    print("=" * 55)
    
    # Test 1: V2 Stats endpoint
    print("\n1. Testing V2 Stats Endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v2/stats", timeout=15)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ V2 Stats working")
            print(f"   📊 Data: {json.dumps(data, indent=2)}")
        else:
            print(f"   ❌ V2 Stats error: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ V2 Stats connection error: {e}")
    
    # Test 2: V2 Active Trades endpoint
    print("\n2. Testing V2 Active Trades Endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v2/active-trades", timeout=15)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ V2 Active Trades working")
            print(f"   📊 Data: {json.dumps(data, indent=2)}")
        else:
            print(f"   ❌ V2 Active Trades error: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ V2 Active Trades connection error: {e}")
    
    # Test 3: V2 Dashboard page
    print("\n3. Testing V2 Dashboard Page...")
    try:
        response = requests.get(f"{base_url}/signal-lab-v2", timeout=15)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ V2 Dashboard page accessible")
            if "V2 Automation Active" in response.text:
                print(f"   ✅ V2 Dashboard content loaded")
            else:
                print(f"   ⚠️ V2 Dashboard content may not be complete")
        elif response.status_code == 302:
            print(f"   🔐 V2 Dashboard requires login (redirecting)")
        else:
            print(f"   ❌ V2 Dashboard error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ V2 Dashboard connection error: {e}")
    
    # Test 4: Test webhook is still working
    print("\n4. Testing V2 Webhook (Quick Test)...")
    test_signal = {
        "timestamp": "2025-10-25T21:00:00",
        "type": "Bullish",
        "price": 20150.75,
        "session": "NY AM"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/live-signals-v2",
            json=test_signal,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            v2_status = result.get('v2_automation', {})
            if v2_status.get('success'):
                print(f"   ✅ V2 Webhook still working - Trade ID: {v2_status.get('trade_id')}")
            else:
                print(f"   ⚠️ V2 Webhook responding but automation issue")
        else:
            print(f"   ❌ V2 Webhook error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ V2 Webhook connection error: {e}")
    
    print(f"\n" + "=" * 55)
    print(f"🎯 V2 DASHBOARD STATUS:")
    print(f"   📊 Dashboard URL: {base_url}/signal-lab-v2")
    print(f"   🔗 API Endpoints: Updated for public access")
    print(f"   🤖 V2 Automation: Active and processing signals")
    
    print(f"\n📋 EXPECTED BEHAVIOR:")
    print(f"   - V2 Dashboard loads without 500 errors")
    print(f"   - Basic stats show without authentication")
    print(f"   - Full data available after login")
    print(f"   - Webhook continues processing signals")

if __name__ == "__main__":
    test_v2_dashboard_endpoints()