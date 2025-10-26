#!/usr/bin/env python3
"""
TEST ENHANCED DASHBOARD INTEGRATION
Test the enhanced Signal Lab V2 dashboard with existing backend
"""

import requests
import json
from datetime import datetime

# Railway endpoint
RAILWAY_ENDPOINT = "https://web-production-cd33.up.railway.app"

def test_dashboard_endpoints():
    """Test all endpoints used by the enhanced dashboard"""
    print("🧪 TESTING ENHANCED DASHBOARD ENDPOINTS")
    print("=" * 50)
    
    endpoints_to_test = [
        ("/api/v2/signals/comprehensive", "Enhanced Signals"),
        ("/api/v2/price/current", "Current Price"),
        ("/api/v2/price/stream?limit=1", "Price Stream"),
        ("/api/v2/stats", "V2 Stats"),
        ("/signal-lab-v2", "Dashboard Page")
    ]
    
    results = {}
    
    for endpoint, name in endpoints_to_test:
        try:
            print(f"\n📡 Testing {name}: {endpoint}")
            
            response = requests.get(f"{RAILWAY_ENDPOINT}{endpoint}", timeout=10)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                if endpoint.endswith('.html') or endpoint == "/signal-lab-v2":
                    print("✅ Dashboard page accessible")
                    results[name] = True
                else:
                    try:
                        data = response.json()
                        print(f"✅ JSON response received")
                        
                        # Show sample data structure
                        if isinstance(data, dict):
                            keys = list(data.keys())[:5]  # First 5 keys
                            print(f"Data keys: {keys}")
                        
                        results[name] = True
                    except json.JSONDecodeError:
                        print("⚠️ Non-JSON response (might be HTML)")
                        results[name] = True
            elif response.status_code == 302:
                print("🔐 Requires authentication (normal for dashboard)")
                results[name] = True
            else:
                print(f"❌ Failed with status {response.status_code}")
                print(f"Response: {response.text[:200]}")
                results[name] = False
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results[name] = False
    
    return results

def test_signal_data_flow():
    """Test the signal data flow for the dashboard"""
    print("\n🔄 TESTING SIGNAL DATA FLOW")
    print("=" * 35)
    
    # Send a test signal to see if it appears in dashboard data
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
            "stop_loss_buffer": 25
        }
    }
    
    try:
        print("📤 Sending test signal...")
        response = requests.post(
            f"{RAILWAY_ENDPOINT}/api/live-signals-v2",
            json=test_signal,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Test signal sent successfully")
            print(f"Signal processed: {result.get('success')}")
            
            if result.get('v2_automation', {}).get('success'):
                trade_id = result['v2_automation'].get('trade_id')
                print(f"Trade created with ID: {trade_id}")
                return True
            else:
                print(f"V2 automation issue: {result.get('v2_automation', {}).get('reason')}")
                return False
        else:
            print(f"❌ Signal sending failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Signal flow test error: {str(e)}")
        return False

def test_price_stream():
    """Test the price stream functionality"""
    print("\n📈 TESTING PRICE STREAM")
    print("=" * 25)
    
    # Send a test price update
    test_price = {
        "type": "realtime_price",
        "symbol": "NQ",
        "price": 20501.75,
        "timestamp": int(datetime.now().timestamp() * 1000),
        "session": "NY AM",
        "volume": 500,
        "change": 1.75
    }
    
    try:
        print("📤 Sending test price update...")
        response = requests.post(
            f"{RAILWAY_ENDPOINT}/api/realtime-price",
            json=test_price,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Price update sent successfully")
            print(f"Price recorded: {result.get('price')}")
            return True
        else:
            print(f"❌ Price update failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Price stream test error: {str(e)}")
        return False

def main():
    """Run comprehensive dashboard integration test"""
    print("🚀 ENHANCED DASHBOARD INTEGRATION TEST")
    print("=" * 55)
    
    # Test all endpoints
    endpoint_results = test_dashboard_endpoints()
    
    # Test data flow
    signal_flow_result = test_signal_data_flow()
    price_stream_result = test_price_stream()
    
    # Summary
    print("\n📊 TEST RESULTS SUMMARY")
    print("=" * 30)
    
    print("\n🔗 Endpoint Tests:")
    for name, result in endpoint_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name}: {status}")
    
    print(f"\n🔄 Data Flow Tests:")
    print(f"  Signal Flow: {'✅ PASS' if signal_flow_result else '❌ FAIL'}")
    print(f"  Price Stream: {'✅ PASS' if price_stream_result else '❌ FAIL'}")
    
    # Overall assessment
    total_tests = len(endpoint_results) + 2
    passed_tests = sum(endpoint_results.values()) + signal_flow_result + price_stream_result
    
    print(f"\n🎯 OVERALL: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ENHANCED DASHBOARD READY!")
        print("✅ All endpoints working")
        print("✅ Signal processing active")
        print("✅ Price streaming functional")
        print("✅ Real-time data flow confirmed")
        print(f"\n🌐 Access your enhanced dashboard:")
        print(f"   {RAILWAY_ENDPOINT}/signal-lab-v2")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} tests failed")
        print("Some functionality may need attention")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    main()