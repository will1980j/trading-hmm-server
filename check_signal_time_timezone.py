import requests
import json
from datetime import datetime
import pytz

# Get the latest signal from the API
url = "https://web-production-cd33.up.railway.app/api/automated-signals/dashboard-data"
response = requests.get(url)
data = response.json()

if data.get('success') and data.get('active_trades'):
    # Get the most recent signal
    latest = data['active_trades'][0]
    
    print("="*60)
    print("LATEST SIGNAL TIMEZONE ANALYSIS")
    print("="*60)
    
    print(f"\nTrade ID: {latest['trade_id']}")
    print(f"Signal Date: {latest['signal_date']}")
    print(f"Signal Time: {latest['signal_time']}")
    print(f"Created At: {latest['created_at']}")
    
    # Parse the times
    signal_time_str = f"{latest['signal_date']}T{latest['signal_time']}"
    created_at_str = latest['created_at']
    
    print(f"\n📅 SIGNAL TIME ANALYSIS:")
    print(f"  Raw signal_time: {latest['signal_time']}")
    print(f"  Raw signal_date: {latest['signal_date']}")
    print(f"  Combined: {signal_time_str}")
    
    print(f"\n🕐 CREATED_AT ANALYSIS:")
    print(f"  Raw created_at: {created_at_str}")
    
    # Parse created_at (has timezone)
    created_dt = datetime.fromisoformat(created_at_str)
    print(f"  Parsed: {created_dt}")
    print(f"  Timezone: {created_dt.tzinfo}")
    print(f"  UTC: {created_dt.astimezone(pytz.UTC)}")
    print(f"  Eastern: {created_dt.astimezone(pytz.timezone('US/Eastern'))}")
    
    # Compare times
    print(f"\n⏰ TIME COMPARISON:")
    print(f"  Signal time says: {latest['signal_time']}")
    print(f"  Created_at Eastern: {created_dt.astimezone(pytz.timezone('US/Eastern')).strftime('%H:%M:%S')}")
    print(f"  Created_at UTC: {created_dt.astimezone(pytz.UTC).strftime('%H:%M:%S')}")
    
    # Check if there's a 1-hour difference
    signal_hour = int(latest['signal_time'].split(':')[0])
    created_hour = created_dt.astimezone(pytz.timezone('US/Eastern')).hour
    
    print(f"\n🔍 HOUR COMPARISON:")
    print(f"  Signal time hour: {signal_hour}")
    print(f"  Created_at hour (ET): {created_hour}")
    print(f"  Difference: {abs(signal_hour - created_hour)} hours")
    
    if abs(signal_hour - created_hour) == 1:
        print(f"\n⚠️  TIMEZONE ISSUE DETECTED!")
        print(f"  There's a 1-hour difference between signal_time and created_at")
        print(f"  This suggests DST handling issue or timezone mismatch")
    
else:
    print("No active trades found")
