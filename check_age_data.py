import requests
from datetime import datetime
import pytz

r = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data')
data = r.json()

trades = data.get('active_trades', []) + data.get('completed_trades', [])

eastern = pytz.timezone('US/Eastern')
now_eastern = datetime.now(eastern)
print(f"Current Eastern Time: {now_eastern.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print()

for t in trades[:5]:
    print(f"trade_id: {t.get('trade_id')}")
    print(f"  signal_date: {t.get('signal_date')}")
    print(f"  signal_time: {t.get('signal_time')}")
    print(f"  status: {t.get('status')}")
    print(f"  exit_timestamp: {t.get('exit_timestamp')}")
    print(f"  duration_seconds: {t.get('duration_seconds')}")
    
    # Calculate expected age
    if t.get('signal_date') and t.get('signal_time'):
        signal_dt_str = f"{t.get('signal_date')} {t.get('signal_time')}"
        signal_dt = eastern.localize(datetime.strptime(signal_dt_str, '%Y-%m-%d %H:%M:%S'))
        age_seconds = (now_eastern - signal_dt).total_seconds()
        hours = int(age_seconds // 3600)
        mins = int((age_seconds % 3600) // 60)
        print(f"  Expected age: {hours}h {mins}m ({age_seconds:.0f} seconds)")
    print()
