#!/usr/bin/env python3

import requests
import json
import time

def test_dashboard_exactly():
    """Test exactly what the dashboard sees, not just the API"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("🔍 TESTING EXACTLY WHAT THE DASHBOARD SEES")
    print("=" * 50)
    
    # Test the exact sequence the dashboard uses
    print("1. Testing dashboard price loading sequence...")
    
    # Step 1: Try /api/v2/price/current (what dashboard tries first)
    print("   Step 1: /api/v2/price/current")
    try:
        response = requests.get(f"{base_url}/api/v2/price/current", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ SUCCESS - Dashboard should show this data:")
            print(f"   Price: ${data.get('price')}")
            print(f"   Session: {data.get('session')}")
            print(f"   Timestamp: {data.get('timestamp')}")
            current_price_works = True
        elif response.status_code == 404:
            print("   ❌ 404 - Dashboard will try fallback")
            current_price_works = False
        else:
            print(f"   ❌ Error {response.status_code} - Dashboard will try fallback")
            current_price_works = False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        current_price_works = False
    
    print()
    
    # Step 2: Try /api/v2/price/stream?limit=1 (dashboard fallback)
    if not current_price_works:
        print("   Step 2: /api/v2/price/stream?limit=1 (fallback)")
        try:
            response = requests.get(f"{base_url}/api/v2/price/stream?limit=1", timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('prices') and len(data['prices']) > 0:
                    price_data = data['prices'][0]
                    print("   ✅ SUCCESS - Dashboard should show this fallback data:")
                    print(f"   Price: ${price_data.get('price')}")
                    print(f"   Session: {price_data.get('session')}")
                    print(f"   Timestamp: {price_data.get('timestamp')}")
                else:
                    print("   ❌ No price data in response")
            elif response.status_code == 404:
                print("   ❌ 404 - Dashboard will show 'Market Closed'")
            else:
                print(f"   ❌ Error {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print()
    
    # Test what happens when dashboard can't get price data
    print("2. If both endpoints fail, dashboard should show:")
    print("   Price: ---.--")
    print("   Session: Market Closed") 
    print("   Last Update: No Data")
    print("   Updates/Min: 0")
    
    print()
    
    # Check browser cache issues
    print("3. Potential browser cache issues:")
    print("   - Dashboard might be showing cached data")
    print("   - Try hard refresh: Ctrl+F5 or Cmd+Shift+R")
    print("   - Try incognito/private mode")
    print("   - Check browser developer tools Network tab")
    
    print()
    
    # Check if realtime price handler is actually running
    print("4. Testing if realtime price handler is running...")
    
    # Send a test price update
    test_price = {
        "type": "realtime_price",
        "symbol": "NQ",
        "price": 99999.99,  # Obvious test value
        "timestamp": int(time.time() * 1000),
        "session": "TEST_SESSION",
        "volume": 999,
        "change": 999.99,
        "bid": 99999.50,
        "ask": 100000.50
    }
    
    try:
        # Send test data
        response = requests.post(f"{base_url}/api/realtime-price", json=test_price, timeout=10)
        print(f"   Test price sent: {response.status_code}")
        
        if response.status_code == 200:
            # Wait a moment
            time.sleep(2)
            
            # Check if it appears in current price
            response = requests.get(f"{base_url}/api/v2/price/current", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('price') == 99999.99:
                    print("   ✅ Realtime price handler is working!")
                    print("   Dashboard should update within 10 seconds")
                else:
                    print(f"   ⚠️  Handler not updating - still shows: ${data.get('price')}")
            else:
                print("   ❌ Current price endpoint not working")
        else:
            print("   ❌ Test price send failed")
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
    
    print()
    print("=" * 50)
    print("🎯 WHAT YOU SHOULD SEE ON DASHBOARD")
    print("=" * 50)
    
    print("If APIs are working but dashboard shows old data:")
    print("- Browser cache issue - try hard refresh")
    print("- Dashboard JavaScript error - check console")
    print("- Realtime handler not running - price not updating")
    print()
    print("If dashboard shows 'Market Closed' or '---.--':")
    print("- Both price endpoints are returning 404")
    print("- Realtime price handler has no data")
    print("- TradingView alerts not sending data")

if __name__ == "__main__":
    test_dashboard_exactly()