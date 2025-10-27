#!/usr/bin/env python3

import requests
import time

def verify_v2_deployment():
    """Verify that the V2 dashboard fix has been deployed successfully"""
    base_url = 'https://web-production-cd33.up.railway.app'
    
    print("🔍 Verifying V2 Dashboard Deployment")
    print("=" * 60)
    
    # Test all V2 endpoints
    endpoints_to_test = [
        ('/api/v2/stats', 'V2 Stats'),
        ('/api/v2/active-trades', 'V2 Active Trades'),
        ('/api/v2/price/current', 'V2 Price Current')
    ]
    
    all_working = True
    
    for endpoint, name in endpoints_to_test:
        try:
            response = requests.get(f'{base_url}{endpoint}', timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {name}: Working (200)")
                
                # Check specific data for each endpoint
                data = response.json()
                
                if endpoint == '/api/v2/stats':
                    total = data.get('total_signals', 0)
                    error = data.get('error', 'None')
                    if total > 0:
                        print(f"   📊 Total signals: {total} (GOOD - shows real data)")
                    else:
                        print(f"   ⚠️  Total signals: {total}, Error: {error}")
                        if 'Database' in str(error):
                            all_working = False
                
                elif endpoint == '/api/v2/active-trades':
                    trades = data.get('trades', [])
                    count = len(trades)
                    if count > 0:
                        print(f"   📋 Active trades: {count} (EXCELLENT - fix deployed!)")
                        # Show first few trades
                        for i, trade in enumerate(trades[:3]):
                            trade_id = trade.get('id', 'N/A')
                            bias = trade.get('bias', 'N/A')
                            status = trade.get('trade_status', 'N/A')
                            print(f"      Trade {trade_id}: {bias} - {status}")
                    else:
                        print(f"   ❌ Active trades: {count} (fix not deployed yet)")
                        all_working = False
                
                elif endpoint == '/api/v2/price/current':
                    price = data.get('price', 'N/A')
                    session = data.get('session', 'N/A')
                    print(f"   💰 Price: {price}, Session: {session}")
                    
            else:
                print(f"❌ {name}: Failed ({response.status_code})")
                all_working = False
                
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            all_working = False
    
    print("\n" + "=" * 60)
    
    if all_working:
        print("🎉 DEPLOYMENT SUCCESSFUL!")
        print("✅ All V2 endpoints are working correctly")
        print("✅ V2 dashboard should now display real data")
        print("✅ Browser errors should be resolved")
        print("\n🌐 Check your V2 dashboard:")
        print("   https://web-production-cd33.up.railway.app/signal-lab-v2")
    else:
        print("⚠️  DEPLOYMENT INCOMPLETE")
        print("❌ Some endpoints are still not working correctly")
        print("💡 This usually means:")
        print("   1. Deployment is still in progress (wait 1-2 more minutes)")
        print("   2. Changes haven't been pushed to Railway yet")
        print("   3. Browser cache needs to be cleared")
        print("\n🔄 Try running this script again in 2 minutes")
    
    return all_working

if __name__ == '__main__':
    verify_v2_deployment()