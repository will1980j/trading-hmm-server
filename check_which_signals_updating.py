"""Check which signals are being updated by the batch"""

import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

database_url = os.getenv('DATABASE_URL')
conn = psycopg2.connect(database_url)
cur = conn.cursor()

# Get signals updated in last 5 minutes
cur.execute("""
    SELECT DISTINCT trade_id, MAX(timestamp) as last_update
    FROM automated_signals
    WHERE event_type = 'MFE_UPDATE'
    AND timestamp > NOW() - INTERVAL '5 minutes'
    GROUP BY trade_id
    ORDER BY last_update DESC
""")

recent_signals = cur.fetchall()

print(f"Signals updated in last 5 minutes: {len(recent_signals)}")
print()
for trade_id, last_update in recent_signals:
    print(f"  {trade_id}: {last_update}")

print()
print("=" * 80)

# Check if these are the same signals or rotating
cur.execute("""
    SELECT 
        DATE_TRUNC('minute', timestamp) as minute,
        array_agg(DISTINCT trade_id ORDER BY trade_id) as trade_ids
    FROM automated_signals
    WHERE event_type = 'MFE_UPDATE'
    AND timestamp > NOW() - INTERVAL '5 minutes'
    GROUP BY DATE_TRUNC('minute', timestamp)
    ORDER BY minute DESC
""")

batches = cur.fetchall()
print("Signals per batch (checking for rotation):")
print()

if len(batches) >= 2:
    batch1_ids = set(batches[0][1])
    batch2_ids = set(batches[1][1])
    
    same = batch1_ids == batch2_ids
    overlap = len(batch1_ids & batch2_ids)
    
    print(f"Latest batch: {len(batch1_ids)} signals")
    print(f"Previous batch: {len(batch2_ids)} signals")
    print(f"Overlap: {overlap} signals")
    print()
    
    if same:
        print("❌ SAME 14 SIGNALS - Not rotating!")
    else:
        print(f"✅ ROTATING - {len(batch1_ids - batch2_ids)} new signals in latest batch")

cur.close()
conn.close()
