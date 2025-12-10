import psycopg2
import os
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Check for recent MFE_UPDATE events (last 5 minutes)
cutoff = datetime.utcnow() - timedelta(minutes=5)

cur.execute("""
    SELECT trade_id, timestamp, be_mfe, no_be_mfe, mae_global_r, current_price
    FROM automated_signals
    WHERE event_type = 'MFE_UPDATE'
    AND timestamp > %s
    ORDER BY timestamp DESC
    LIMIT 30
""", (cutoff,))

rows = cur.fetchall()
print(f"MFE_UPDATE events in last 5 minutes: {len(rows)}")
print("=" * 80)

if len(rows) == 0:
    print("⚠️ NO MFE_UPDATE EVENTS IN LAST 5 MINUTES!")
    print("This means batch updates are NOT being received or processed.")
else:
    # Group by minute to see batch pattern
    by_minute = {}
    for row in rows:
        trade_id, ts, be_mfe, no_be_mfe, mae, price = row
        minute_key = ts.strftime('%H:%M')
        if minute_key not in by_minute:
            by_minute[minute_key] = []
        by_minute[minute_key].append({
            'trade_id': trade_id,
            'be_mfe': float(be_mfe) if be_mfe else 0,
            'no_be_mfe': float(no_be_mfe) if no_be_mfe else 0,
            'mae': float(mae) if mae else 0
        })
    
    print("Updates by minute (batch pattern):")
    for minute in sorted(by_minute.keys(), reverse=True):
        signals = by_minute[minute]
        print(f"\n{minute} - {len(signals)} signals updated:")
        for s in signals[:5]:  # Show first 5
            print(f"  {s['trade_id'][-20:]}: BE={s['be_mfe']:.2f}R, NoBE={s['no_be_mfe']:.2f}R, MAE={s['mae']:.2f}R")

# Check most recent update time
cur.execute("""
    SELECT MAX(timestamp) 
    FROM automated_signals 
    WHERE event_type = 'MFE_UPDATE'
""")
last_update = cur.fetchone()[0]
print(f"\n{'='*80}")
print(f"Last MFE_UPDATE received: {last_update}")
if last_update:
    minutes_ago = (datetime.utcnow() - last_update.replace(tzinfo=None)).total_seconds() / 60
    print(f"Time since last update: {minutes_ago:.1f} minutes ago")
    if minutes_ago > 2:
        print("⚠️ WARNING: No updates in over 2 minutes - batch system may not be working!")

cur.close()
conn.close()
