#!/usr/bin/env python3

import requests
import json

def check_v2_table():
    """Check if the signal_lab_v2_trades table exists and has data"""
    base_url = 'https://web-production-cd33.up.railway.app'
    
    print("🔍 Checking V2 Table Status")
    print("=" * 50)
    
    # Test the webhook to see if it can create trades
    print("\n1. Testing V2 Webhook (creates records in signal_lab_v2_trades)...")
    test_signal = {
        'signal_type': 'Bullish',
        'price': 4160.25,
        'session': 'NY AM',
        'timestamp': '1698765432000'
    }
    
    try:
        response = requests.post(f'{base_url}/api/live-signals-v2', 
                                json=test_signal, timeout=10)
        if response.status_code == 200:
            data = response.json()
            trade_id = data.get('v2_automation', {}).get('trade_id')
            print(f"✅ V2 Webhook working - Created trade ID: {trade_id}")
            print("   This confirms signal_lab_v2_trades table exists and is writable")
        else:
            print(f"❌ V2 Webhook failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ V2 Webhook error: {e}")
    
    # Test the active trades endpoint (reads from signal_lab_v2_trades)
    print("\n2. Testing V2 Active Trades (reads from signal_lab_v2_trades)...")
    try:
        response = requests.get(f'{base_url}/api/v2/active-trades', timeout=10)
        if response.status_code == 200:
            data = response.json()
            trades = data.get('trades', [])
            print(f"✅ V2 Active Trades working - Found {len(trades)} trades")
            if trades:
                print("   This confirms the table is readable and has data")
            else:
                print("   Table is readable but may be empty or filtered")
        else:
            print(f"❌ V2 Active Trades failed: {response.status_code}")
    except Exception as e:
        print(f"❌ V2 Active Trades error: {e}")
    
    # Test the stats endpoint (also reads from signal_lab_v2_trades)
    print("\n3. Testing V2 Stats (reads from signal_lab_v2_trades)...")
    try:
        response = requests.get(f'{base_url}/api/v2/stats', timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('error') == 'Database connection issue':
                print("❌ V2 Stats has database connection issue")
                print("   This suggests a problem with the stats query specifically")
            else:
                print("✅ V2 Stats working properly")
                print(f"   Total signals: {data.get('total_signals', 'N/A')}")
        else:
            print(f"❌ V2 Stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ V2 Stats error: {e}")
    
    print("\n📊 Analysis:")
    print("If webhook works but stats fails, the issue is likely:")
    print("1. Different database connection handling in stats endpoint")
    print("2. Query syntax error in stats endpoint")
    print("3. Authentication/session issue in stats endpoint")

if __name__ == '__main__':
    check_v2_table()