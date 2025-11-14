"""
Diagnose why MFE_UPDATE and EXIT webhooks aren't firing
"""

import requests
from datetime import datetime

# Check if backend is receiving ENTRY webhooks
print("=" * 80)
print("WEBHOOK DIAGNOSTIC")
print("=" * 80)
print()

# Check recent database entries
print("1. Checking recent database entries...")
try:
    response = requests.get('https://web-production-cd33.up.railway.app/api/automated-signals/dashboard-data')
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Backend responding")
        print(f"   Active trades: {len(data.get('active_trades', []))}")
        print(f"   Completed trades: {len(data.get('completed_trades', []))}")
        
        if data.get('active_trades'):
            print("\n   Active Trades:")
            for trade in data['active_trades'][:3]:
                print(f"   - {trade.get('trade_id')}: {trade.get('direction')} @ {trade.get('entry_price')}")
                print(f"     BE MFE: {trade.get('be_mfe')}, No BE MFE: {trade.get('no_be_mfe')}")
    else:
        print(f"❌ Backend error: {response.status_code}")
except Exception as e:
    print(f"❌ Cannot reach backend: {e}")

print()
print("2. Checking webhook stats...")
try:
    response = requests.get('https://web-production-cd33.up.railway.app/api/automated-signals/stats-live')
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ Stats retrieved")
        print(f"   Total signals: {stats.get('total_signals', 0)}")
        print(f"   Active: {stats.get('active_count', 0)}")
        print(f"   Completed: {stats.get('completed_count', 0)}")
    else:
        print(f"❌ Stats error: {response.status_code}")
except Exception as e:
    print(f"❌ Cannot get stats: {e}")

print()
print("=" * 80)
print("DIAGNOSIS")
print("=" * 80)
print()
print("If ENTRY webhooks are working but dashboard shows no data:")
print("- Backend is not receiving webhooks (check Railway logs)")
print("- Webhook URL is wrong in TradingView alert")
print("- Backend is receiving but not processing (check error logs)")
print()
print("If dashboard shows data but no MFE updates:")
print("- active_signal_ids array not being populated")
print("- MFE_UPDATE webhook condition not being met")
print("- Check TradingView alert log for MFE_UPDATE alerts")
print()
print("Next steps:")
print("1. Check TradingView alert log - do you see MFE_UPDATE alerts?")
print("2. Check Railway logs - are webhooks being received?")
print("3. If no MFE_UPDATE alerts in TradingView, the indicator logic is broken")
print("4. If MFE_UPDATE alerts exist but dashboard doesn't update, backend issue")
