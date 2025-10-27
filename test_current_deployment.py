#!/usr/bin/env python3

import requests
import json

def test_current_deployment():
    """Test the current deployment status"""
    base_url = 'https://web-production-cd33.up.railway.app'
    
    print("🔍 Testing Current Deployment Status")
    print("=" * 60)
    
    # Test 1: Create a new trade
    print("\n1. Creating a new V2 trade...")
    test_signal = {
        'signal_type': 'Bearish',
        'price': 4145.75,
        'session': 'NY PM',
        'timestamp': '1698765432000'
    }
    
    try:
        response = requests.post(f'{base_url}/api/live-signals-v2', 
                                json=test_signal, timeout=10)
        if response.status_code == 200:
            data = response.json()
            trade_id = data.get('v2_automation', {}).get('trade_id')
            print(f"✅ Created trade ID: {trade_id}")
        else:
            print(f"❌ Failed to create trade: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error creating trade: {e}")
        return
    
    # Test 2: Check if we can see the trade
    print("\n2. Checking if trade appears in active trades...")
    try:
        response = requests.get(f'{base_url}/api/v2/active-trades', timeout=10)
        if response.status_code == 200:
            data = response.json()
            trades = data.get('trades', [])
            print(f"   Found {len(trades)} trades")
            
            if len(trades) > 0:
                print("✅ DEPLOYMENT IS WORKING!")
                print("   Recent trades:")
                for trade in trades[:3]:
                    print(f"     ID: {trade.get('id')}, Bias: {trade.get('bias')}, Status: {trade.get('trade_status')}")
            else:
                print("❌ DEPLOYMENT NEEDED!")
                print("   Trades are being created but not displayed")
        else:
            print(f"❌ Active trades endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking active trades: {e}")
    
    # Test 3: Check stats
    print("\n3. Checking V2 stats...")
    try:
        response = requests.get(f'{base_url}/api/v2/stats', timeout=10)
        if response.status_code == 200:
            data = response.json()
            total = data.get('total_signals', 0)
            error = data.get('error', 'None')
            print(f"   Total signals: {total}")
            print(f"   Error: {error}")
            
            if total > 0:
                print("✅ Stats are working correctly")
            else:
                print("❌ Stats show 0 signals despite trades being created")
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking stats: {e}")
    
    # Test 4: Check price endpoint
    print("\n4. Checking V2 price endpoint...")
    try:
        response = requests.get(f'{base_url}/api/v2/price/current', timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response keys: {list(data.keys())}")
            print("✅ Price endpoint working")
        elif response.status_code == 404:
            print("❌ Price endpoint not found (404)")
        else:
            print(f"❌ Price endpoint error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking price: {e}")
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("If trades are created but not displayed, deployment is needed.")
    print("If all endpoints work, the V2 dashboard should be functional.")

if __name__ == '__main__':
    test_current_deployment()