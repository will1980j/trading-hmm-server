#!/usr/bin/env python3
"""
TEST V2 ENDPOINTS LIVE
Test the existing V2 endpoints to verify functionality
"""

import requests
import json
from datetime import datetime

# Railway endpoint
RAILWAY_ENDPOINT = "https://web-production-cd33.up.railway.app"

def test_schema_deployment():
    """Test if we can deploy the dual schema"""
    try:
        print("🧪 Testing schema deployment...")
        
        response = requests.post(
            f"{RAILWAY_ENDPOINT}/api/deploy-dual-schema",
            json={},
            timeout=30
        )
        
        print(f"Schema deployment status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Schema deployment successful!")
            print(f"Tables: {result.get('tables_created', [])}")
            print(f"Functions: {result.get('functions_deployed', [])}")
            return True
        else:
            print(f"Schema deployment response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"Schema deployment error: {str(e)}")
        return False

def test_v2_signal_webhook():
    """Test the V2 signal webhook endpoint"""
    try:
        print("\n🧪 Testing V2 signal webhook...")
        
        # Create test signal data (Enhanced FVG format)
        test_signal = {
            "signal_type": "Bullish",
            "signal_candle": {
                "open": 20500.25,
                "high": 20502.75,
                "low": 20499.50,
                "close": 20501.00
            },
            "fvg_data": {
                "bias": "Bullish",
                "strength": 85.0
            },
            "htf_data": {
                "aligned": True,
                "bias_1h": "Bullish",
                "bias_15m": "Bullish",
                "bias_5m": "Bullish"
            },
            "session_data": {
                "current_session": "NY AM",
                "valid": True
            },
            "methodology_data": {
                "requires_confirmation": True,
                "stop_loss_buffer": 25,
                "confirmation_condition": "close_above_signal_high"
            },
            "market_context": {
                "volatility": "medium",
                "trend": "bullish"
            }
        }
        
        response = requests.post(
            f"{RAILWAY_ENDPOINT}/api/live-signals-v2",
            json=test_signal,
            timeout=15
        )
        
        print(f"V2 Signal webhook status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ V2 Signal webhook working!")
            print(f"Success: {result.get('success')}")
            print(f"Message: {result.get('message')}")
            if result.get('v2_automation'):
                print(f"V2 Automation: {result['v2_automation']}")
            return True
        else:
            print(f"V2 Signal webhook response: {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"V2 Signal webhook error: {str(e)}")
        return False

def test_realtime_price_webhook():
    """Test the real-time price webhook endpoint"""
    try:
        print("\n🧪 Testing real-time price webhook...")
        
        # Create test price data
        test_price = {
            "type": "realtime_price",
            "symbol": "NQ",
            "price": 20501.75,
            "timestamp": int(datetime.now().timestamp() * 1000),
            "session": "NY AM",
            "volume": 500,
            "change": 1.75
        }
        
        response = requests.post(
            f"{RAILWAY_ENDPOINT}/api/realtime-price",
            json=test_price,
            timeout=15
        )
        
        print(f"Real-time price webhook status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Real-time price webhook working!")
            print(f"Status: {result.get('status')}")
            print(f"Price: {result.get('price')}")
            return True
        else:
            print(f"Real-time price webhook response: {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"Real-time price webhook error: {str(e)}")
        return False

def test_existing_endpoints():
    """Test existing API endpoints"""
    try:
        print("\n🧪 Testing existing API endpoints...")
        
        # Test webhook stats
        response = requests.get(f"{RAILWAY_ENDPOINT}/api/webhook-stats")
        print(f"Webhook stats: {response.status_code}")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Webhook stats working - Total signals: {stats.get('total_signals', 0)}")
        
        # Test database status
        response = requests.get(f"{RAILWAY_ENDPOINT}/api/db-status")
        print(f"Database status: {response.status_code}")
        
        if response.status_code == 200:
            db_status = response.json()
            print(f"✅ Database status: {db_status.get('status')}")
            print(f"Signals last hour: {db_status.get('signals_last_hour', 0)}")
        
        return True
        
    except Exception as e:
        print(f"Existing endpoints test error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 TESTING V2 BACKEND SYSTEM")
    print("=" * 50)
    
    results = {
        "schema_deployment": test_schema_deployment(),
        "v2_signal_webhook": test_v2_signal_webhook(),
        "realtime_price_webhook": test_realtime_price_webhook(),
        "existing_endpoints": test_existing_endpoints()
    }
    
    print("\n📊 TEST RESULTS SUMMARY:")
    print("=" * 30)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\n🎯 OVERALL: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🚀 ALL SYSTEMS GO!")
        print("Your V2 dual indicator backend is ready for:")
        print("✅ Enhanced FVG signal processing")
        print("✅ Real-time price stream handling")
        print("✅ Automated MFE tracking")
        print("✅ Comprehensive data storage")
    else:
        print(f"\n⚠️ {total_tests - total_passed} tests failed")
        print("Some functionality may need attention")
    
    return total_passed == total_tests

if __name__ == "__main__":
    main()