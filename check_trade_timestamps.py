"""Check trade timestamps via production API"""
import requests
from datetime import datetime

BASE_URL = "https://web-production-f8c3.up.railway.app"

r = requests.get(f"{BASE_URL}/api/automated-signals/dashboard-data")
if r.status_code == 200:
    data = r.json()
    
    print("=== ACTIVE TRADES WITH TIMESTAMPS ===")
    for trade in data.get('active_trades', []):
        trade_id = trade.get('trade_id', 'unknown')
        be_mfe = trade.get('be_mfe', 0)
        timestamp = trade.get('timestamp', 'N/A')
        signal_time = trade.get('signal_time', 'N/A')
        
        # Parse trade_id to get creation time
        parts = trade_id.split('_')
        if len(parts) >= 2:
            date_part = parts[0]  # YYYYMMDD
            time_part = parts[1]  # HHMMSS000
            created = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]} {time_part[:2]}:{time_part[2:4]}:{time_part[4:6]}"
        else:
            created = "unknown"
        
        has_mfe = "✓ MFE updating" if be_mfe > 0 else "✗ NO MFE updates"
        print(f"  {trade_id}")
        print(f"    Created: {created}")
        print(f"    Signal Time: {signal_time}")
        print(f"    MFE: {be_mfe}R - {has_mfe}")
        print()
