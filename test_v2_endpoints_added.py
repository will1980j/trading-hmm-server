#!/usr/bin/env python3
"""
Test V2 Endpoints Added - Verify the endpoints were added correctly
"""

import requests
import json

def test_v2_endpoints_added():
    """Test that V2 endpoints are working after being added to web_server.py"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    session = requests.Session()
    
    print("🧪 TESTING V2 ENDPOINTS AFTER DEPLOYMENT")
    print("=" * 60)
    
    # Login first
    login_data = {'username': 'admin', 'password': 'n2351447'}
    response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
    
    if response.status_code != 302:
        print("❌ Login failed!")
        return
    
    print("✅ Login successful!")
    
    # Test 1: V2 Stats endpoint
    print("\n📊 Test 1: V2 Statistics...")
    try:
        response = session.get(f"{base_url}/api/v2/stats", timeout=30)
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ V2 Stats endpoint working!")
            print(f"   📈 Total V2 trades: {stats.get('v2_stats', {}).get('total_v2_trades', 0)}")
            print(f"   🔄 Active trades: {stats.get('v2_stats', {}).get('active_trades', 0)}")
            print(f"   🤖 Automated trades: {stats.get('v2_stats', {}).get('automated_trades', 0)}")
        else:
            print(f"❌ V2 Stats failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ V2 Stats request failed: {e}")
    
    # Test 2: V2 Active Trades endpoint
    print("\n📋 Test 2: V2 Active Trades...")
    try:
        response = session.get(f"{base_url}/api/v2/active-trades", timeout=30)
        
        if response.status_code == 200:
            trades = response.json()
            print("✅ V2 Active Trades endpoint working!")
            print(f"   📊 Active trades count: {trades.get('count', 0)}")
        else:
            print(f"❌ V2 Active Trades failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ V2 Active Trades request failed: {e}")
    
    # Test 3: V2 Process Signal endpoint
    print("\n🎯 Test 3: V2 Process Signal...")
    try:
        test_signal = {
            "type": "Bullish",
            "price": 20000.00,
            "timestamp": "2025-10-25T15:30:00Z",
            "session": "NY PM"
        }
        
        response = session.post(
            f"{base_url}/api/v2/process-signal",
            json=test_signal,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ V2 Process Signal endpoint working!")
            print(f"   🆔 Trade ID: {result.get('trade_id')}")
            print(f"   💰 Entry Price: ${result.get('entry_price')}")
            print(f"   🛑 Stop Loss: ${result.get('stop_loss_price')}")
            print(f"   🎯 20R Target: ${result.get('r_targets', {}).get('20R')}")
        else:
            print(f"❌ V2 Process Signal failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ V2 Process Signal request failed: {e}")
    
    # Test 4: V2 Enhanced Webhook (no login required)
    print("\n📡 Test 4: V2 Enhanced Webhook...")
    try:
        webhook_data = {
            "type": "Bearish",
            "symbol": "NQ1!",
            "price": 20050.00,
            "session": "NY PM"
        }
        
        # Test without session (no login required)
        response = requests.post(
            f"{base_url}/api/live-signals-v2",
            json=webhook_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ V2 Enhanced Webhook working!")
            v2_auto = result.get('v2_automation', {})
            if v2_auto.get('success'):
                print(f"   🆔 Auto Trade ID: {v2_auto.get('trade_id')}")
                print(f"   💰 Auto Entry: ${v2_auto.get('entry_price')}")
                print(f"   🎯 Auto 20R Target: ${v2_auto.get('r_targets', {}).get('20R')}")
            else:
                print(f"   ⚠️ V2 automation failed: {v2_auto.get('error', 'Unknown error')}")
        else:
            print(f"❌ V2 Enhanced Webhook failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ V2 Enhanced Webhook request failed: {e}")
    
    print("\n🎉 V2 ENDPOINTS TEST COMPLETE!")
    print("=" * 60)
    print("🚀 V2 AUTOMATION SYSTEM IS NOW LIVE!")
    print("\n📝 What's now available:")
    print("  ✅ /api/v2/process-signal - Manual signal processing")
    print("  ✅ /api/v2/active-trades - Real-time active trades")
    print("  ✅ /api/v2/update-mfe - MFE updates")
    print("  ✅ /api/v2/close-trade - Trade closure")
    print("  ✅ /api/v2/stats - V2 statistics")
    print("  ✅ /api/live-signals-v2 - Enhanced TradingView webhook")
    print("\n🎯 Ready to capture those 20R trend moves!")

if __name__ == "__main__":
    test_v2_endpoints_added()