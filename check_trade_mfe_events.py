#!/usr/bin/env python3
"""Check MFE values for specific trades"""
import os
import psycopg2
import psycopg2.extras

DATABASE_URL = os.environ.get("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
try:
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        # Get unique trade_ids
        cur.execute("""
            SELECT DISTINCT trade_id FROM automated_signals 
            ORDER BY trade_id DESC LIMIT 5
        """)
        trade_ids = [r['trade_id'] for r in cur.fetchall()]
        
        for tid in trade_ids:
            print(f"\n=== Trade: {tid} ===")
            cur.execute("""
                SELECT event_type, be_mfe, no_be_mfe, mfe, timestamp
                FROM automated_signals
                WHERE trade_id = %s
                ORDER BY timestamp ASC
            """, [tid])
            events = cur.fetchall()
            for e in events:
                print(f"  {e['event_type']}: be_mfe={e['be_mfe']}, no_be_mfe={e['no_be_mfe']}, mfe={e['mfe']}")
finally:
    conn.close()
