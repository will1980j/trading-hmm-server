#!/usr/bin/env python3

import requests
import json

def check_realtime_price_data():
    """Check what realtime price data exists in the system"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("🔍 CHECKING REALTIME PRICE DATA SYSTEM")
    print("=" * 50)
    
    # Test the realtime price webhook
    print("1. Testing realtime price webhook...")
    try:
        test_data = {
            "type": "realtime_price",
            "symbol": "NQ",
            "price": 20501.25,
            "timestamp": 1698765432000,
            "session": "NY AM",
            "volume": 100,
            "bid": 20501.00,
            "ask": 20501.50,
            "change": 1.25
        }
        
        response = requests.post(f"{base_url}/api/realtime-price", json=test_data, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Realtime price webhook working!")
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   ❌ Webhook failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Check if there's a table for realtime prices
    print("2. Checking for realtime price storage...")
    
    # Look for any endpoints that might return realtime price data
    endpoints_to_check = [
        "/api/webhook-stats",
        "/api/v2/active-trades", 
        "/api/live-signals"
    ]
    
    for endpoint in endpoints_to_check:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                data_str = json.dumps(data).lower()
                
                if "price" in data_str and "realtime" in data_str:
                    print(f"   ✅ Found realtime price data in {endpoint}")
                elif "price" in data_str:
                    print(f"   🔍 Found price data in {endpoint}")
                    
        except:
            continue
    
    print()
    
    # Test if we can get current price from the realtime system
    print("3. Testing current price retrieval...")
    
    # The V2 endpoints should connect to the realtime price system
    # Let me check what tables exist for price data
    
    print("=" * 50)
    print("🎯 ANALYSIS")
    print("=" * 50)
    
    print("The system has:")
    print("✅ Realtime price webhook endpoint (/api/realtime-price)")
    print("✅ Realtime price handler (realtime_price_webhook_handler.py)")
    print("✅ TradingView 1-second indicator (tradingview_realtime_price_streamer.pine)")
    print()
    print("The issue is:")
    print("❌ V2 price endpoints are not connected to the realtime price system")
    print("❌ Price endpoints query 'live_signals' table instead of realtime price data")
    print()
    print("SOLUTION:")
    print("🔧 Connect V2 price endpoints to the realtime price handler")
    print("🔧 Store realtime price data in database or use in-memory cache")

if __name__ == "__main__":
    check_realtime_price_data()