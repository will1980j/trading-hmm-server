#!/usr/bin/env python3
"""
Cleanup orphaned/stale trades that never received EXIT events.
These are trades from days ago that are still showing as "ACTIVE".
"""
import os
import psycopg2
from datetime import datetime, timedelta
import pytz

DATABASE_URL = os.environ.get('DATABASE_URL')

def analyze_orphaned_trades():
    """Analyze trades that are stuck as ACTIVE"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    eastern = pytz.timezone('US/Eastern')
    now = datetime.now(eastern)
    today = now.date()
    
    print(f"Current date (Eastern): {today}")
    print("=" * 70)
    
    # Find ENTRY events without corresponding EXIT events
    cur.execute("""
        SELECT e.trade_id, e.timestamp, e.direction, e.session
        FROM automated_signals e
        WHERE e.event_type = 'ENTRY'
        AND NOT EXISTS (
            SELECT 1 FROM automated_signals ex
            WHERE ex.trade_id = e.trade_id
            AND ex.event_type LIKE 'EXIT_%'
        )
        ORDER BY e.timestamp DESC
    """)
    
    orphaned = cur.fetchall()
    print(f"\nFound {len(orphaned)} orphaned trades (ENTRY without EXIT):\n")
    
    old_trades = []
    today_trades = []
    
    for row in orphaned:
        trade_id, timestamp, direction, session = row
        trade_date = timestamp.date() if timestamp else None
        
        # Extract date from trade_id as backup
        try:
            date_str = trade_id.split('_')[0]
            trade_id_date = datetime.strptime(date_str, '%Y%m%d').date()
        except:
            trade_id_date = None
        
        age_days = (today - trade_date).days if trade_date else "?"
        
        if trade_date and trade_date < today:
            old_trades.append(trade_id)
            print(f"  ❌ OLD ({age_days}d): {trade_id[:40]}... | {direction} | {session}")
        else:
            today_trades.append(trade_id)
            print(f"  ✅ TODAY: {trade_id[:40]}... | {direction} | {session}")
    
    print(f"\n" + "=" * 70)
    print(f"Summary:")
    print(f"  - Old orphaned trades (should be purged): {len(old_trades)}")
    print(f"  - Today's active trades: {len(today_trades)}")
    
    conn.close()
    return old_trades

def purge_old_trades(trade_ids):
    """Delete all events for the specified trade_ids"""
    if not trade_ids:
        print("No trades to purge.")
        return
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print(f"\nPurging {len(trade_ids)} old orphaned trades...")
    
    cur.execute("""
        DELETE FROM automated_signals
        WHERE trade_id = ANY(%s)
    """, (trade_ids,))
    
    deleted = cur.rowcount
    conn.commit()
    conn.close()
    
    print(f"✅ Deleted {deleted} events for {len(trade_ids)} trades")

if __name__ == '__main__':
    import sys
    
    old_trades = analyze_orphaned_trades()
    
    if old_trades and len(sys.argv) > 1 and sys.argv[1] == '--purge':
        confirm = input(f"\nPurge {len(old_trades)} old trades? (yes/no): ")
        if confirm.lower() == 'yes':
            purge_old_trades(old_trades)
        else:
            print("Aborted.")
    elif old_trades:
        print(f"\nTo purge these old trades, run: python cleanup_orphaned_trades.py --purge")
