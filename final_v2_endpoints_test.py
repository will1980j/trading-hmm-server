#!/usr/bin/env python3

import requests
import json
import time

def final_v2_endpoints_test():
    """Final comprehensive test of all V2 endpoints after fixes"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("🎯 FINAL V2 ENDPOINTS TEST")
    print("=" * 50)
    print(f"Testing at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {}
    
    # Test 1: V2 Stats Endpoint
    print("📊 Testing /api/v2/stats...")
    try:
        response = requests.get(f"{base_url}/api/v2/stats", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "Database query failed: 0" in str(data.get("error", "")):
                print("   ❌ STILL FAILING - Old database error")
                results["stats"] = "FAIL - Old error"
            elif data.get("status") == "success" or data.get("public_access"):
                print("   ✅ SUCCESS - Stats working!")
                print(f"   Total signals: {data.get('total_signals', 0)}")
                print(f"   Active trades: {data.get('active_trades', 0)}")
                results["stats"] = "PASS"
            else:
                print("   ⚠️  PARTIAL - Unexpected response")
                results["stats"] = "PARTIAL"
        else:
            print(f"   ❌ HTTP ERROR - {response.status_code}")
            results["stats"] = f"FAIL - {response.status_code}"
            
    except Exception as e:
        print(f"   ❌ EXCEPTION - {e}")
        results["stats"] = f"ERROR - {e}"
    
    print()
    
    # Test 2: V2 Price Current Endpoint
    print("💰 Testing /api/v2/price/current...")
    try:
        response = requests.get(f"{base_url}/api/v2/price/current", timeout=10)
        
        if response.status_code == 404:
            data = response.json()
            if "No real-time price data available" in str(data.get("error", "")):
                print("   ✅ SUCCESS - Proper 404 for no data!")
                print(f"   Session: {data.get('session', 'N/A')}")
                results["price"] = "PASS"
            else:
                print("   ⚠️  PARTIAL - 404 but unexpected message")
                results["price"] = "PARTIAL"
        elif response.status_code == 500:
            data = response.json()
            if data.get("message") == "0":
                print("   ❌ STILL FAILING - Old database error")
                results["price"] = "FAIL - Old error"
            else:
                print("   ❌ NEW 500 ERROR")
                results["price"] = "FAIL - New error"
        elif response.status_code == 200:
            print("   ✅ SUCCESS - Real data available!")
            results["price"] = "PASS"
        else:
            print(f"   ❌ UNEXPECTED STATUS - {response.status_code}")
            results["price"] = f"FAIL - {response.status_code}"
            
    except Exception as e:
        print(f"   ❌ EXCEPTION - {e}")
        results["price"] = f"ERROR - {e}"
    
    print()
    
    # Test 3: V2 Webhook (should still work)
    print("🔗 Testing /api/live-signals-v2 webhook...")
    try:
        test_signal = {
            "type": "Bullish",
            "price": 20500.75,
            "timestamp": int(time.time() * 1000),
            "session": "NY AM",
            "symbol": "NQ"
        }
        
        response = requests.post(f"{base_url}/api/live-signals-v2", json=test_signal, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            v2_automation = data.get("v2_automation", {})
            
            if v2_automation.get("success"):
                print("   ✅ SUCCESS - Webhook creating trades!")
                print(f"   Trade ID: {v2_automation.get('trade_id')}")
                results["webhook"] = "PASS"
            else:
                print("   ⚠️  PARTIAL - Webhook responds but no trade created")
                results["webhook"] = "PARTIAL"
        else:
            print(f"   ❌ HTTP ERROR - {response.status_code}")
            results["webhook"] = f"FAIL - {response.status_code}"
            
    except Exception as e:
        print(f"   ❌ EXCEPTION - {e}")
        results["webhook"] = f"ERROR - {e}"
    
    print()
    
    # Test 4: Signal Lab V2 Dashboard Page
    print("🧪 Testing /signal-lab-v2 dashboard...")
    try:
        response = requests.get(f"{base_url}/signal-lab-v2", timeout=10)
        
        if response.status_code == 200:
            print("   ✅ SUCCESS - Dashboard accessible!")
            results["dashboard"] = "PASS"
        elif response.status_code == 302:
            print("   🔐 REDIRECT - Authentication required (expected)")
            results["dashboard"] = "PASS - Auth required"
        else:
            print(f"   ❌ HTTP ERROR - {response.status_code}")
            results["dashboard"] = f"FAIL - {response.status_code}"
            
    except Exception as e:
        print(f"   ❌ EXCEPTION - {e}")
        results["dashboard"] = f"ERROR - {e}"
    
    print()
    print("=" * 50)
    print("🎯 FINAL TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        if "PASS" in result:
            icon = "✅"
            passed += 1
        elif "PARTIAL" in result:
            icon = "⚠️"
        else:
            icon = "❌"
        
        print(f"{icon} {test_name.upper()}: {result}")
    
    print()
    print(f"🎯 OVERALL: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! V2 system fully operational!")
        print("   Your browser errors should be resolved.")
    elif passed >= total * 0.75:
        print("⚠️  MOSTLY WORKING - Minor issues remain")
    else:
        print("❌ SIGNIFICANT ISSUES - More work needed")
    
    return passed == total

if __name__ == "__main__":
    print("🚀 FINAL V2 ENDPOINTS TEST")
    print("=" * 50)
    print()
    print("This test will verify all V2 endpoints after deployment.")
    print("Run this after committing and pushing your changes.")
    print()
    
    input("Press Enter to start testing...")
    print()
    
    success = final_v2_endpoints_test()
    
    if success:
        print()
        print("🎊 SUCCESS! Your Signal Lab V2 dashboard should now work perfectly!")
        print("   Refresh your browser and the console errors should be gone.")
    else:
        print()
        print("🔧 Some issues remain. Check the results above for details.")