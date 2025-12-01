#!/usr/bin/env python3
"""Quick diagnostic to check what fields the dashboard API returns"""
import requests
import json

BASE_URL = "https://web-production-f8c3.up.railway.app"

print("=" * 70)
print("DASHBOARD API FIELD DIAGNOSTIC")
print("=" * 70)

# 1. Check dashboard-data endpoint
print("\n1. Checking /api/automated-signals/dashboard-data...")
try:
    resp = requests.get(f"{BASE_URL}/api/automated-signals/dashboard-data", timeout=30)
    data = resp.json()
    
    print(f"   Status: {resp.status_code}")
    print(f"   Active trades: {len(data.get('active_trades', []))}")
    print(f"   Completed trades: {len(data.get('completed_trades', []))}")
    
    # Check first active trade fields
    if data.get('active_trades'):
        trade = data['active_trades'][0]
        print(f"\n   Sample ACTIVE trade fields:")
        print(f"   - trade_id: {trade.get('trade_id')}")
        print(f"   - direction: {trade.get('direction')}")
        print(f"   - mfe: {trade.get('mfe')}")
        print(f"   - be_mfe: {trade.get('be_mfe')}")
        print(f"   - no_be_mfe: {trade.get('no_be_mfe')}")
        print(f"   - be_mfe_R: {trade.get('be_mfe_R')}")
        print(f"   - no_be_mfe_R: {trade.get('no_be_mfe_R')}")
        print(f"   - timestamp: {trade.get('timestamp')}")
    
    # Check first completed trade fields
    if data.get('completed_trades'):
        trade = data['completed_trades'][0]
        print(f"\n   Sample COMPLETED trade fields:")
        print(f"   - trade_id: {trade.get('trade_id')}")
        print(f"   - direction: {trade.get('direction')}")
        print(f"   - mfe: {trade.get('mfe')}")
        print(f"   - be_mfe: {trade.get('be_mfe')}")
        print(f"   - no_be_mfe: {trade.get('no_be_mfe')}")
        print(f"   - final_mfe: {trade.get('final_mfe')}")
        print(f"   - timestamp: {trade.get('timestamp')}")
        
except Exception as e:
    print(f"   ERROR: {e}")

# 2. Check daily-calendar endpoint
print("\n2. Checking /api/automated-signals/daily-calendar...")
try:
    resp = requests.get(f"{BASE_URL}/api/automated-signals/daily-calendar", timeout=30)
    data = resp.json()
    
    print(f"   Status: {resp.status_code}")
    print(f"   Success: {data.get('success')}")
    
    daily_data = data.get('daily_data', {})
    print(f"   Days with data: {len(daily_data)}")
    
    # Show today's data if available
    from datetime import datetime
    import pytz
    ny_tz = pytz.timezone('America/New_York')
    today_str = datetime.now(ny_tz).strftime('%Y-%m-%d')
    
    if today_str in daily_data:
        today_data = daily_data[today_str]
        print(f"\n   Today ({today_str}) data:")
        print(f"   - completed_count: {today_data.get('completed_count')}")
        print(f"   - active_count: {today_data.get('active_count')}")
        print(f"   - trade_count: {today_data.get('trade_count')}")
    else:
        print(f"\n   No data for today ({today_str})")
        # Show most recent day
        if daily_data:
            recent_date = sorted(daily_data.keys())[-1]
            print(f"   Most recent day ({recent_date}):")
            print(f"   - {daily_data[recent_date]}")
            
except Exception as e:
    print(f"   ERROR: {e}")

# 3. Check a specific trade detail if we have one
print("\n3. Checking trade detail endpoint...")
try:
    # First get a trade_id from dashboard
    resp = requests.get(f"{BASE_URL}/api/automated-signals/dashboard-data", timeout=30)
    data = resp.json()
    
    trade_id = None
    if data.get('active_trades'):
        trade_id = data['active_trades'][0].get('trade_id')
    elif data.get('completed_trades'):
        trade_id = data['completed_trades'][0].get('trade_id')
    
    if trade_id:
        print(f"   Testing with trade_id: {trade_id}")
        # Note: This endpoint requires auth, so it may fail
        detail_resp = requests.get(f"{BASE_URL}/api/automated-signals/trade/{trade_id}", timeout=30)
        print(f"   Status: {detail_resp.status_code}")
        if detail_resp.status_code == 200:
            detail = detail_resp.json()
            print(f"   - be_mfe_R: {detail.get('be_mfe_R')}")
            print(f"   - no_be_mfe_R: {detail.get('no_be_mfe_R')}")
            print(f"   - final_mfe_R: {detail.get('final_mfe_R')}")
            print(f"   - events count: {len(detail.get('events', []))}")
    else:
        print("   No trades available to test")
        
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
