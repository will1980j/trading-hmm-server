#!/usr/bin/env python3
"""Diagnose all dashboard issues"""
import requests
import os

BASE_URL = 'https://web-production-f8c3.up.railway.app'
DATABASE_URL = os.environ.get('DATABASE_URL')

# Check raw database
print("=== RAW DATABASE CHECK ===")
if DATABASE_URL:
    import psycopg2
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Check what columns exist
    cur.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'automated_signals' 
        ORDER BY ordinal_position
    """)
    cols = [r[0] for r in cur.fetchall()]
    print(f"Columns in automated_signals: {cols}")
    
    # Check recent events
    cur.execute("""
        SELECT trade_id, event_type, signal_date, signal_time, session, mfe, be_mfe, no_be_mfe, timestamp
        FROM automated_signals 
        ORDER BY timestamp DESC 
        LIMIT 10
    """)
    print("\nRecent events:")
    for row in cur.fetchall():
        print(f"  {row[0][:20]}... | {row[1]:15} | date={row[2]} | time={row[3]} | session={row[4]} | mfe={row[5]} | be_mfe={row[6]} | no_be_mfe={row[7]}")
    
    # Check MFE_UPDATE events specifically
    cur.execute("""
        SELECT COUNT(*) FROM automated_signals WHERE event_type = 'MFE_UPDATE'
    """)
    mfe_count = cur.fetchone()[0]
    print(f"\nTotal MFE_UPDATE events: {mfe_count}")
    
    # Check what event types exist
    cur.execute("""
        SELECT event_type, COUNT(*) FROM automated_signals GROUP BY event_type
    """)
    print("\nEvent type counts:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")
    
    conn.close()
else:
    print("No DATABASE_URL - checking via API only")

# Check what the indicator is sending
print("\n=== WEBHOOK STATS ===")
resp = requests.get(f'{BASE_URL}/api/webhook-stats', timeout=30)
if resp.status_code == 200:
    stats = resp.json()
    print(f"Total webhooks: {stats.get('total_webhooks', 'N/A')}")
    print(f"Recent: {stats.get('recent_webhooks', [])[:3]}")
