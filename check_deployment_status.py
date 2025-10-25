#!/usr/bin/env python3
"""
Check Deployment Status - See if V2 endpoints are deployed
"""

import requests
import time

def check_deployment_status():
    """Check if V2 endpoints are deployed to Railway"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("🔍 CHECKING V2 DEPLOYMENT STATUS")
    print("=" * 50)
    
    # Test the new V2 webhook endpoint (no auth required)
    print("📡 Testing V2 webhook endpoint...")
    
    test_data = {
        "type": "Bullish",
        "price": 20000,
        "session": "Test"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/live-signals-v2",
            json=test_data,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ V2 ENDPOINTS ARE DEPLOYED!")
            result = response.json()
            print(f"Response: {result.get('message', 'No message')}")
            
            v2_auto = result.get('v2_automation', {})
            if v2_auto.get('success'):
                print(f"🎉 V2 AUTOMATION WORKING!")
                print(f"   Trade ID: {v2_auto.get('trade_id')}")
                print(f"   Entry: ${v2_auto.get('entry_price')}")
                print(f"   20R Target: ${v2_auto.get('r_targets', {}).get('20R')}")
            
        elif response.status_code == 404:
            print("⏳ V2 endpoints not deployed yet")
            print("   Railway is still deploying the changes...")
            
        elif response.status_code == 405:
            print("⏳ V2 endpoints not deployed yet")
            print("   Method not allowed - old endpoint still active")
            
        else:
            print(f"❓ Unexpected status: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Check if we can access the original webhook
    print(f"\n📡 Testing original webhook endpoint...")
    
    try:
        response = requests.post(
            f"{base_url}/api/live-signals",
            json=test_data,
            timeout=10
        )
        
        print(f"Original webhook status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Original webhook still working")
        
    except Exception as e:
        print(f"❌ Original webhook test failed: {e}")

def wait_for_deployment():
    """Wait for Railway deployment to complete"""
    
    print("\n⏳ WAITING FOR RAILWAY DEPLOYMENT...")
    print("=" * 50)
    
    max_attempts = 12  # 2 minutes max
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        print(f"Attempt {attempt}/{max_attempts}...")
        
        try:
            response = requests.post(
                "https://web-production-cd33.up.railway.app/api/live-signals-v2",
                json={"type": "Test", "price": 20000},
                timeout=5
            )
            
            if response.status_code == 200:
                print("🎉 DEPLOYMENT COMPLETE!")
                print("✅ V2 endpoints are now live!")
                return True
                
        except:
            pass
        
        if attempt < max_attempts:
            print("   Still deploying... waiting 10 seconds")
            time.sleep(10)
    
    print("⏰ Deployment taking longer than expected")
    print("   Check Railway dashboard for deployment status")
    return False

if __name__ == "__main__":
    check_deployment_status()
    
    # If not deployed, wait for it
    print("\n" + "="*50)
    wait_for_deployment()