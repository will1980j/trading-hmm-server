import requests

r = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data')
data = r.json()

active = data.get('active_trades', [])
if active:
    signal = active[0]
    print(f"First active signal:")
    print(f"  trade_id: {signal.get('trade_id')}")
    print(f"  event_ts: {signal.get('event_ts')}")
    print(f"  entry_ts: {signal.get('entry_ts')}")
    print(f"  timestamp: {signal.get('timestamp')}")
    print(f"  signal_date: {signal.get('signal_date')}")
    print(f"  signal_time: {signal.get('signal_time')}")
    
    # Test formatSignalDateTime logic
    trade_id = signal.get('trade_id')
    if trade_id:
        parts = trade_id.split('_')
        if len(parts) >= 2:
            date_str = parts[0]
            time_str = parts[1][:6]
            print(f"\nParsed from trade_id:")
            print(f"  Date: {date_str}")
            print(f"  Time: {time_str}")
            print(f"  Should display: {time_str[:2]}:{time_str[2:4]}")
