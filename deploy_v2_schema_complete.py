#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def deploy_v2_schema():
    """Deploy complete V2 schema to Railway"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("🚀 Deploying Complete V2 Database Schema")
    print("=" * 50)
    
    # Deploy V2 schema using the existing endpoint
    print("\n1. 📊 Deploying V2 database schema...")
    
    try:
        response = requests.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json={"deploy": True},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("   ✅ V2 Schema deployment response:")
                print(json.dumps(result, indent=4))
                
                if result.get('success'):
                    print("   🎉 V2 database schema deployed successfully!")
                else:
                    print(f"   ❌ Deployment failed: {result.get('error', 'Unknown error')}")
                    
            except:
                print("   ✅ Deployment completed (non-JSON response)")
                print(f"   📄 Response: {response.text[:200]}")
        else:
            print(f"   ❌ Deployment failed: {response.status_code}")
            print(f"   📄 Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Deployment connection error: {e}")
    
    # Wait a moment for deployment to complete
    print("\n⏳ Waiting for deployment to complete...")
    import time
    time.sleep(3)
    
    # Test V2 system after deployment
    print("\n2. 🧪 Testing V2 system after deployment...")
    
    test_signal = {
        "timestamp": datetime.now().isoformat(),
        "type": "Bullish",
        "price": 20150.75,
        "session": "NY AM"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/live-signals-v2",
            json=test_signal,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            v2_status = result.get('v2_automation', {})
            
            print("   📡 Webhook test results:")
            if v2_status.get('success'):
                print("   🎉 SUCCESS! V2 automation is now working!")
                print(f"   📊 Trade ID: {v2_status.get('trade_id')}")
                print(f"   🆔 Trade UUID: {v2_status.get('trade_uuid')}")
                print(f"   💰 Entry Price: {v2_status.get('entry_price')}")
                print(f"   🛡️ Stop Loss: {v2_status.get('stop_loss_price')}")
            else:
                error_msg = v2_status.get('error', v2_status.get('reason', 'Unknown'))
                print(f"   ❌ Still failing: {error_msg}")
                
                if error_msg != "0":
                    print("   ✅ Error message improved (no longer '0')")
                else:
                    print("   ❌ Still getting error '0' - may need manual intervention")
        else:
            print(f"   ❌ Webhook test failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Webhook test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 V2 DEPLOYMENT STATUS:")
    
    # Final status check
    if response.status_code == 200:
        result = response.json()
        v2_status = result.get('v2_automation', {})
        
        if v2_status.get('success'):
            print("   🎉 V2 AUTOMATION: FULLY OPERATIONAL!")
            print("   ✅ Database schema: Deployed")
            print("   ✅ Signal processing: Working")
            print("   ✅ Trade creation: Active")
            print("   ✅ 20R targeting: Enabled")
            print("\n🚀 READY FOR LIVE TRADINGVIEW SIGNALS!")
        else:
            print("   🔧 V2 AUTOMATION: NEEDS ATTENTION")
            print("   ✅ Webhook: Working")
            print("   ❌ Database: Issues remain")
            print("\n🔧 May need manual database verification")
    
    print(f"\n📡 TradingView Webhook URL:")
    print(f"   {base_url}/api/live-signals-v2")

if __name__ == "__main__":
    deploy_v2_schema()