#!/usr/bin/env python3
"""Check MFE values directly in the database"""
import os
import psycopg2
import psycopg2.extras

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("DATABASE_URL not set")
    exit(1)

conn = psycopg2.connect(DATABASE_URL)
try:
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        # Check recent trades with MFE values
        cur.execute("""
            SELECT trade_id, event_type, be_mfe, no_be_mfe, mfe, timestamp
            FROM automated_signals
            ORDER BY timestamp DESC
            LIMIT 20
        """)
        rows = cur.fetchall()
        
        print(f"Last 20 events in automated_signals:")
        for r in rows:
            print(f"  {r['trade_id']} | {r['event_type']} | be_mfe={r['be_mfe']} | no_be_mfe={r['no_be_mfe']} | mfe={r['mfe']}")
        
        # Count how many have MFE values
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(be_mfe) as with_be_mfe,
                COUNT(no_be_mfe) as with_no_be_mfe,
                COUNT(mfe) as with_mfe
            FROM automated_signals
        """)
        stats = cur.fetchone()
        print(f"\nMFE Statistics:")
        print(f"  Total rows: {stats['total']}")
        print(f"  With be_mfe: {stats['with_be_mfe']}")
        print(f"  With no_be_mfe: {stats['with_no_be_mfe']}")
        print(f"  With mfe: {stats['with_mfe']}")
finally:
    conn.close()
