#!/usr/bin/env python3

import requests
import time
import json

def test_v2_system():
    """Test the V2 system comprehensively"""
    base_url = 'https://web-production-cd33.up.railway.app'
    
    print("🧪 Testing V2 System Comprehensively")
    print("=" * 50)
    
    # Test 1: Send a signal to V2 webhook
    print("\n1. Testing V2 Webhook...")
    test_signal = {
        'signal_type': 'Bullish',
        'price': 4155.50,
        'session': 'NY AM',
        'timestamp': str(int(time.time() * 1000))
    }
    
    try:
        response = requests.post(f'{base_url}/api/live-signals-v2', 
                                json=test_signal, timeout=10)
        if response.status_code == 200:
            data = response.json()
            trade_id = data.get('v2_automation', {}).get('trade_id', 'N/A')
            print(f"✅ V2 Webhook working - Trade ID: {trade_id}")
        else:
            print(f"❌ V2 Webhook failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ V2 Webhook error: {e}")
        return False
    
    # Test 2: Check V2 Stats
    print("\n2. Testing V2 Stats...")
    try:
        response = requests.get(f'{base_url}/api/v2/stats', timeout=10)
        if response.status_code == 200:
            data = response.json()
            total = data.get('total_signals', 0)
            print(f"✅ V2 Stats working - Total signals: {total}")
        else:
            print(f"❌ V2 Stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ V2 Stats error: {e}")
    
    # Test 3: Check V2 Active Trades
    print("\n3. Testing V2 Active Trades...")
    try:
        response = requests.get(f'{base_url}/api/v2/active-trades', timeout=10)
        if response.status_code == 200:
            data = response.json()
            trades = data.get('trades', [])
            print(f"✅ V2 Active Trades working - Found {len(trades)} trades")
            
            if trades:
                print("   Recent trades:")
                for i, trade in enumerate(trades[:3]):  # Show first 3
                    trade_id = trade.get('id', 'N/A')
                    bias = trade.get('bias', 'N/A')
                    status = trade.get('trade_status', 'N/A')
                    print(f"     Trade {trade_id}: {bias} - {status}")
                return True
            else:
                print("   No trades found - this indicates the fix is needed")
                return False
        else:
            print(f"❌ V2 Active Trades failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ V2 Active Trades error: {e}")
        return False

def check_deployment_needed():
    """Check if deployment is needed"""
    print("\n🔍 Checking if deployment is needed...")
    
    # The fix is needed if we can create trades but can't see them
    result = test_v2_system()
    
    if not result:
        print("\n🚨 DEPLOYMENT NEEDED!")
        print("The V2 system can create trades but can't display them.")
        print("This means the active-trades endpoint fix needs to be deployed.")
        print("\n📋 DEPLOYMENT INSTRUCTIONS:")
        print("1. Open GitHub Desktop")
        print("2. You'll see web_server.py has been modified")
        print("3. Commit with message: 'Fix V2 dashboard: Show all V2 trades, not just active ones'")
        print("4. Push to main branch")
        print("5. Wait 2-3 minutes for Railway deployment")
        print("6. Run this script again to verify the fix")
        return True
    else:
        print("\n✅ V2 system is working correctly!")
        print("No deployment needed.")
        return False

if __name__ == '__main__':
    check_deployment_needed()