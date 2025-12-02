"""
Test what the calendar API is actually returning
"""
import requests

BASE_URL = "https://web-production-f8c3.up.railway.app"

print("Testing calendar API data...")

try:
    resp = requests.get(f"{BASE_URL}/api/automated-signals/daily-calendar", timeout=10)
    data = resp.json()
    
    if data.get('success'):
        daily_data = data.get('daily_data', {})
        print(f"\n✅ Calendar API returned {len(daily_data)} days")
        
        # Show recent days
        dates = sorted(daily_data.keys())[-5:]
        print(f"\nRecent days:")
        for date in dates:
            day_data = daily_data[date]
            print(f"  {date}:")
            print(f"    Completed: {day_data.get('completed_count', 0)}")
            print(f"    Active: {day_data.get('active_count', 0)}")
            print(f"    Total: {day_data.get('trade_count', 0)}")
    else:
        print(f"❌ API error: {data}")
        
except Exception as e:
    print(f"❌ Error: {e}")
