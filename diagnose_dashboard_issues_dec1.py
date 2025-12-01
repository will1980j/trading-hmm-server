#!/usr/bin/env python3
"""Diagnose the 3 dashboard issues:
1. Trade showing COMPLETED when it should be ACTIVE
2. Time only on one trade, and increasing per minute
3. Age showing 11 hours for one, nothing for other
"""

import os
from dotenv import load_dotenv
import psycopg2
from datetime import datetime
import pytz

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')

def diagnose():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Get all events for today's trades
    print("=" * 80)
    print("ALL EVENTS FOR TODAY'S TRADES")
    print("=" * 80)
    
    cur.execute("""
        SELECT trade_id, event_type, direction, signal_time, signal_date, 
               entry_price, stop_loss, be_mfe, no_be_mfe, timestamp,
               created_at
        FROM automated_signals 
        WHERE DATE(created_at) = CURRENT_DATE
        ORDER BY trade_id, created_at
    """)
    
    rows = cur.fetchall()
    
    trades = {}
    for row in rows:
        trade_id = row[0]
        if trade_id not in trades:
            trades[trade_id] = []
        trades[trade_id].append({
            'event_type': row[1],
            'direction': row[2],
            'signal_time': row[3],
            'signal_date': row[4],
            'entry_price': row[5],
            'stop_loss': row[6],
            'be_mfe': row[7],
            'no_be_mfe': row[8],
            'timestamp': row[9],
            'created_at': row[10]
        })
    
    for trade_id, events in trades.items():
        print(f"\n{'='*60}")
        print(f"TRADE: {trade_id}")
        print(f"{'='*60}")
        
        for e in events:
            print(f"  Event: {e['event_type']}")
            print(f"    signal_time: {e['signal_time']}")
            print(f"    signal_date: {e['signal_date']}")
            print(f"    timestamp: {e['timestamp']}")
            print(f"    created_at: {e['created_at']}")
            print(f"    direction: {e['direction']}")
            print(f"    entry: {e['entry_price']}, stop: {e['stop_loss']}")
            print(f"    be_mfe: {e['be_mfe']}, no_be_mfe: {e['no_be_mfe']}")
            print()
        
        # Check for completion events
        event_types = [e['event_type'] for e in events]
        print(f"  Event types present: {event_types}")
        
        has_entry = 'ENTRY' in event_types
        has_exit = any(et in event_types for et in ['EXIT_SL', 'EXIT_BE', 'BE_TRIGGERED'])
        
        print(f"  Has ENTRY: {has_entry}")
        print(f"  Has EXIT event: {has_exit}")
        print(f"  Should be: {'COMPLETED' if has_exit else 'ACTIVE'}")
    
    # Now check what the dashboard query returns
    print("\n" + "=" * 80)
    print("DASHBOARD QUERY RESULT (what the API returns)")
    print("=" * 80)
    
    # This is the query from the dashboard API
    cur.execute("""
        WITH latest_events AS (
            SELECT DISTINCT ON (trade_id) 
                trade_id, event_type, direction, entry_price, stop_loss,
                be_mfe, no_be_mfe, session, signal_time, signal_date, timestamp
            FROM automated_signals
            ORDER BY trade_id, created_at DESC
        ),
        trade_status AS (
            SELECT trade_id,
                   CASE WHEN EXISTS (
                       SELECT 1 FROM automated_signals a2 
                       WHERE a2.trade_id = latest_events.trade_id 
                       AND a2.event_type IN ('EXIT_SL', 'EXIT_BE', 'BE_TRIGGERED')
                   ) THEN 'COMPLETED' ELSE 'ACTIVE' END as status
            FROM latest_events
        )
        SELECT le.trade_id, ts.status, le.event_type, le.direction, 
               le.signal_time, le.signal_date, le.timestamp,
               le.entry_price, le.stop_loss, le.be_mfe, le.no_be_mfe
        FROM latest_events le
        JOIN trade_status ts ON le.trade_id = ts.trade_id
        WHERE DATE(le.timestamp) >= CURRENT_DATE - INTERVAL '1 day'
        ORDER BY le.timestamp DESC
    """)
    
    rows = cur.fetchall()
    for row in rows:
        print(f"\nTrade: {row[0]}")
        print(f"  Status: {row[1]}")
        print(f"  Latest event_type: {row[2]}")
        print(f"  Direction: {row[3]}")
        print(f"  signal_time: {row[4]}")
        print(f"  signal_date: {row[5]}")
        print(f"  timestamp: {row[6]}")
        print(f"  entry: {row[7]}, stop: {row[8]}")
        print(f"  be_mfe: {row[9]}, no_be_mfe: {row[10]}")
    
    # Check the trade_id format - is it using correct timezone?
    print("\n" + "=" * 80)
    print("TRADE ID ANALYSIS")
    print("=" * 80)
    
    for trade_id in trades.keys():
        # Parse trade_id: YYYYMMDD_HHMMSS_DIRECTION
        parts = trade_id.split('_')
        if len(parts) >= 2:
            date_part = parts[0]
            time_part = parts[1]
            print(f"\nTrade ID: {trade_id}")
            print(f"  Date from ID: {date_part[:4]}-{date_part[4:6]}-{date_part[6:8]}")
            print(f"  Time from ID: {time_part[:2]}:{time_part[2:4]}:{time_part[4:6]}")
            
            # Compare with signal_time in database
            first_event = trades[trade_id][0]
            print(f"  signal_time in DB: {first_event['signal_time']}")
            print(f"  signal_date in DB: {first_event['signal_date']}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    diagnose()
