#!/usr/bin/env python3

import requests
import json
import time

def debug_tradingview_alert_setup():
    """Debug TradingView alert setup and webhook connectivity"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("🔍 DEBUGGING TRADINGVIEW ALERT SETUP")
    print("=" * 50)
    
    # Test 1: Check if webhook endpoint is accessible
    print("1. Testing webhook endpoint accessibility...")
    try:
        # Test with a simple GET request first
        response = requests.get(f"{base_url}/api/realtime-price", timeout=10)
        print(f"   GET Status: {response.status_code}")
        
        if response.status_code == 405:
            print("   ✅ Endpoint exists (405 = Method Not Allowed for GET is expected)")
        else:
            print(f"   ⚠️  Unexpected GET response: {response.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ Endpoint not accessible: {e}")
        return False
    
    print()
    
    # Test 2: Send test webhook data (simulate TradingView)
    print("2. Testing webhook with simulated TradingView data...")
    try:
        # Simulate the exact payload format from the optimized indicator
        test_payload = {
            "type": "realtime_price",
            "symbol": "NQ",
            "price": 20503.25,
            "timestamp": int(time.time() * 1000),
            "session": "NY AM",
            "volume": 125,
            "change": 1.50,
            "bid": 20503.00,
            "ask": 20503.50
        }
        
        response = requests.post(f"{base_url}/api/realtime-price", json=test_payload, timeout=10)
        print(f"   POST Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Webhook working!")
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   ❌ Webhook failed: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Webhook test failed: {e}")
        return False
    
    print()
    
    # Test 3: Check if price data is being stored/retrieved
    print("3. Testing price data retrieval...")
    time.sleep(1)  # Wait a moment
    
    try:
        response = requests.get(f"{base_url}/api/v2/price/current", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Price data available!")
            print(f"   Price: ${data.get('price')}")
            print(f"   Session: {data.get('session')}")
            print(f"   Source: {data.get('source')}")
        elif response.status_code == 404:
            data = response.json()
            print("   ⚠️  No price data stored")
            print(f"   Message: {data.get('message')}")
        else:
            print(f"   ❌ Unexpected response: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Price retrieval failed: {e}")
    
    print()
    print("=" * 50)
    print("🎯 TRADINGVIEW ALERT CHECKLIST")
    print("=" * 50)
    
    print("✅ Webhook endpoint working - data can be received")
    print()
    print("📋 TradingView Alert Setup Checklist:")
    print("1. ✅ Indicator added to chart")
    print("2. ❓ Alert created on the indicator?")
    print("3. ❓ Alert message set to: {{strategy.order.alert_text}}")
    print("4. ❓ Webhook URL set to: https://web-production-cd33.up.railway.app/api/realtime-price")
    print("5. ❓ Alert frequency set to 'Once Per Bar Close'?")
    print("6. ❓ Alert timeframe matches chart timeframe?")
    print("7. ❓ Alert is enabled and running?")
    print()
    print("🔧 COMMON ISSUES:")
    print("- Alert message must be exactly: {{strategy.order.alert_text}}")
    print("- Webhook URL must include https://")
    print("- Alert must be set to 'Once Per Bar Close' not 'Once Per Bar'")
    print("- Chart timeframe should match alert timeframe")
    print("- Check TradingView alert history for errors")
    print()
    print("🧪 MANUAL TEST:")
    print("Send this exact JSON to test webhook manually:")
    print(json.dumps(test_payload, indent=2))

if __name__ == "__main__":
    debug_tradingview_alert_setup()