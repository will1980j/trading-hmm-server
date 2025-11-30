#!/usr/bin/env python3
"""Check trades that have MFE values"""
import os
import psycopg2
import psycopg2.extras

DATABASE_URL = os.environ.get("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
try:
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        # Find trades that have MFE_UPDATE events with actual values
        cur.execute("""
            SELECT DISTINCT trade_id FROM automated_signals 
            WHERE be_mfe IS NOT NULL OR no_be_mfe IS NOT NULL
            ORDER BY trade_id DESC LIMIT 5
        """)
        trade_ids = [r['trade_id'] for r in cur.fetchall()]
        
        print(f"Found {len(trade_ids)} trades with MFE values")
        
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
                print(f"  {e['event_type']}: be_mfe={e['be_mfe']}, no_be_mfe={e['no_be_mfe']}")
finally:
    conn.close()
