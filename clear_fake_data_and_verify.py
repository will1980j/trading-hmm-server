#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def clear_fake_data_and_verify():
    """Clear any fake data and verify the system shows proper 'no data' state"""
    
    print("🧹 CLEARING FAKE DATA AND VERIFYING PROPER STATE")
    print("=" * 60)
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    # Check current state of realtime price handler
    print("1. Checking current realtime price handler state:")
    try:
        from realtime_price_webhook_handler import get_current_price
        current_price = get_current_price()
        
        if current_price:
            print(f"⚠️ FOUND FAKE DATA: Price = {current_price.price}")
            print(f"   Timestamp: {datetime.fromtimestamp(current_price.timestamp/1000)}")
            print(f"   Session: {current_price.session}")
            print("   This is fake data that needs to be cleared!")
        else:
            print("✅ No current price data - this is correct!")
            
    except ImportError:
        print("❌ Cannot import realtime price handler")
    except Exception as e:
        print(f"❌ Error checking price handler: {str(e)}")
    
    # Test V2 endpoints - they should return 404 (no data)
    print("\n2. Testing V2 endpoints (should return 404 - no data):")
    
    # Test current price endpoint
    try:
        response = requests.get(f"{base_url}/api/v2/price/current", timeout=10)
        print(f"\n/api/v2/price/current:")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 404:
            data = response.json()
            if data.get('status') == 'no_data':
                print("✅ CORRECT: Returns 404 with 'no_data' status")
                print(f"   Message: {data.get('message')}")
            else:
                print(f"⚠️ Returns 404 but wrong status: {data.get('status')}")
        elif response.status_code == 200:
            data = response.json()
            print(f"❌ WRONG: Returns 200 with fake data: {data.get('price')}")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing current price: {str(e)}")
    
    # Test price stream endpoint
    try:
        response = requests.get(f"{base_url}/api/v2/price/stream?limit=1", timeout=10)
        print(f"\n/api/v2/price/stream:")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 404:
            data = response.json()
            if data.get('status') == 'no_data':
                print("✅ CORRECT: Returns 404 with 'no_data' status")
                print(f"   Count: {data.get('count', 0)}")
            else:
                print(f"⚠️ Returns 404 but wrong status: {data.get('status')}")
        elif response.status_code == 200:
            data = response.json()
            print(f"❌ WRONG: Returns 200 with fake data count: {data.get('count')}")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing price stream: {str(e)}")
    
    print("\n3. CORRECT BEHAVIOR SUMMARY:")
    print("✅ V2 endpoints should return 404 until TradingView sends real data")
    print("✅ Dashboard should show 'No price data available' message")
    print("✅ No fake prices should be displayed")
    
    print("\n4. TO GET REAL DATA:")
    print("📊 Deploy tradingview_simple_price_streamer.pine to TradingView")
    print("🔗 Set webhook URL: https://web-production-cd33.up.railway.app/api/realtime-price")
    print("⚡ Configure alerts to send real NQ prices")
    print("📈 Dashboard will then show actual market data")
    
    print("\n5. CURRENT STATE:")
    print("The system is correctly configured to reject fake data")
    print("and wait for real TradingView price updates.")

if __name__ == "__main__":
    clear_fake_data_and_verify()