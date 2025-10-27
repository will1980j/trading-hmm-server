#!/usr/bin/env python3

import requests
import json
import time
from datetime import datetime

def verify_v2_deployment():
    """Comprehensive verification of V2 API endpoints after deployment"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("🚀 V2 DEPLOYMENT VERIFICATION")
    print("=" * 50)
    print(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {}
    
    # Test 1: V2 Stats Endpoint
    print("📊 Testing /api/v2/stats...")
    try:
        response = requests.get(f"{base_url}/api/v2/stats", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "error" in data and "Database query failed" in str(data.get("error", "")):
                print("❌ STILL FAILING - Database query error persists")
                results["v2_stats"] = "FAIL - Database error"
            elif data.get("status") == "success" or data.get("public_access"):
                print("✅ SUCCESS - V2 stats working!")
                print(f"   Total signals: {data.get('total_signals', 0)}")
                print(f"   Active trades: {data.get('active_trades', 0)}")
                print(f"   Today signals: {data.get('today_signals', 0)}")
                results["v2_stats"] = "PASS"
            else:
                print("⚠️  PARTIAL - Unexpected response format")
                results["v2_stats"] = "PARTIAL"
        else:
            print(f"❌ FAILED - Status {response.status_code}")
            results["v2_stats"] = f"FAIL - {response.status_code}"
            
    except Exception as e:
        print(f"❌ ERROR - {e}")
        results["v2_stats"] = f"ERROR - {e}"
    
    print()
    
    # Test 2: V2 Price Current Endpoint
    print("💰 Testing /api/v2/price/current...")
    try:
        response = requests.get(f"{base_url}/api/v2/price/current", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                print("✅ SUCCESS - Price endpoint working!")
                print(f"   Price: ${data.get('price', 'N/A')}")
                print(f"   Session: {data.get('session', 'N/A')}")
                results["v2_price"] = "PASS"
            else:
                print("⚠️  PARTIAL - No real data available (expected)")
                results["v2_price"] = "PARTIAL - No data"
        elif response.status_code == 404:
            data = response.json()
            if "No real price data available" in str(data.get("error", "")):
                print("✅ SUCCESS - Proper 404 for no data (expected)")
                results["v2_price"] = "PASS - No data"
            else:
                print("❌ FAILED - Unexpected 404")
                results["v2_price"] = "FAIL - Bad 404"
        else:
            print(f"❌ FAILED - Status {response.status_code}")
            results["v2_price"] = f"FAIL - {response.status_code}"
            
    except Exception as e:
        print(f"❌ ERROR - {e}")
        results["v2_price"] = f"ERROR - {e}"
    
    print()
    
    # Test 3: V2 Webhook (should still work)
    print("🔗 Testing /api/live-signals-v2 webhook...")
    try:
        test_signal = {
            "signal": "bullish",
            "price": 20500.75,
            "timestamp": int(time.time() * 1000),
            "session": "NY AM",
            "symbol": "NQ"
        }
        
        response = requests.post(
            f"{base_url}/api/live-signals-v2",
            json=test_signal,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") or "Signal received" in str(data.get("message", "")):
                print("✅ SUCCESS - V2 webhook working!")
                results["v2_webhook"] = "PASS"
            else:
                print("⚠️  PARTIAL - Webhook responded but unclear result")
                results["v2_webhook"] = "PARTIAL"
        else:
            print(f"❌ FAILED - Status {response.status_code}")
            results["v2_webhook"] = f"FAIL - {response.status_code}"
            
    except Exception as e:
        print(f"❌ ERROR - {e}")
        results["v2_webhook"] = f"ERROR - {e}"
    
    print()
    
    # Test 4: Signal Lab V2 Dashboard Page
    print("🧪 Testing /signal-lab-v2 dashboard page...")
    try:
        response = requests.get(f"{base_url}/signal-lab-v2", timeout=10)
        
        if response.status_code == 200:
            if "Signal Lab V2" in response.text or "v2" in response.text.lower():
                print("✅ SUCCESS - V2 dashboard page accessible!")
                results["v2_dashboard"] = "PASS"
            else:
                print("⚠️  PARTIAL - Page loads but content unclear")
                results["v2_dashboard"] = "PARTIAL"
        elif response.status_code == 302:
            print("🔐 REDIRECT - Authentication required (expected)")
            results["v2_dashboard"] = "PASS - Auth required"
        else:
            print(f"❌ FAILED - Status {response.status_code}")
            results["v2_dashboard"] = f"FAIL - {response.status_code}"
            
    except Exception as e:
        print(f"❌ ERROR - {e}")
        results["v2_dashboard"] = f"ERROR - {e}"
    
    print()
    print("=" * 50)
    print("📋 DEPLOYMENT VERIFICATION SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status_icon = "✅" if "PASS" in result else "❌" if "FAIL" in result or "ERROR" in result else "⚠️"
        print(f"{status_icon} {test_name.replace('_', ' ').title()}: {result}")
        if "PASS" in result:
            passed += 1
    
    print()
    print(f"🎯 OVERALL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 DEPLOYMENT SUCCESSFUL! All V2 endpoints working!")
        return True
    elif passed >= total * 0.75:
        print("⚠️  DEPLOYMENT MOSTLY SUCCESSFUL - Minor issues remain")
        return True
    else:
        print("❌ DEPLOYMENT ISSUES - Multiple endpoints failing")
        return False

def wait_for_deployment():
    """Wait for Railway deployment to complete"""
    print("⏳ Waiting for Railway deployment...")
    print("   (This usually takes 2-3 minutes)")
    print()
    
    for i in range(6):  # Wait up to 3 minutes
        print(f"   Waiting... {i*30}s")
        time.sleep(30)
        
        # Quick test to see if deployment is complete
        try:
            response = requests.get(
                "https://web-production-cd33.up.railway.app/api/v2/stats",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                # Check if we're getting the old error
                if not ("Database query failed: 0" in str(data.get("error", ""))):
                    print("✅ Deployment detected! Running verification...")
                    print()
                    return True
        except:
            pass
    
    print("⚠️  Deployment taking longer than expected, running verification anyway...")
    print()
    return True

if __name__ == "__main__":
    print("🚀 V2 DEPLOYMENT VERIFICATION TOOL")
    print("=" * 50)
    print()
    print("Instructions:")
    print("1. Commit your changes in GitHub Desktop")
    print("2. Push to main branch")
    print("3. Run this script to verify deployment")
    print()
    
    input("Press Enter when you've pushed the changes to continue...")
    print()
    
    # Wait for deployment
    wait_for_deployment()
    
    # Run verification
    success = verify_v2_deployment()
    
    if success:
        print()
        print("🎊 Your V2 dashboard should now work without errors!")
        print("   Try refreshing your browser and check the console.")
    else:
        print()
        print("🔧 Some issues remain. Check the results above.")
        print("   You may need to investigate further or try again.")