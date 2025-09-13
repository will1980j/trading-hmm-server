#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.railway_db import RailwayDB

def debug_trades():
    db = RailwayDB()
    cursor = db.conn.cursor()
    
    # Check what's actually in the database
    cursor.execute("SELECT COUNT(*) as total FROM signal_lab_trades")
    total = cursor.fetchone()['total']
    print(f"Total trades: {total}")
    
    # Check active vs non-active
    cursor.execute("SELECT COUNT(*) as active FROM signal_lab_trades WHERE COALESCE(active_trade, false) = true")
    active = cursor.fetchone()['active']
    print(f"Active trades: {active}")
    
    cursor.execute("SELECT COUNT(*) as completed FROM signal_lab_trades WHERE COALESCE(active_trade, false) = false")
    completed = cursor.fetchone()['completed']
    print(f"Completed trades: {completed}")
    
    # Check what has MFE data
    cursor.execute("SELECT COUNT(*) as with_mfe FROM signal_lab_trades WHERE COALESCE(mfe_none, mfe, 0) != 0")
    with_mfe = cursor.fetchone()['with_mfe']
    print(f"Trades with MFE data: {with_mfe}")
    
    # Sample of actual data
    cursor.execute("""
        SELECT date, time, bias, session, signal_type, 
               COALESCE(mfe_none, mfe, 0) as mfe_value,
               COALESCE(active_trade, false) as is_active
        FROM signal_lab_trades 
        ORDER BY date DESC, time DESC 
        LIMIT 10
    """)
    
    trades = cursor.fetchall()
    print(f"\nSample trades:")
    for trade in trades:
        print(f"  {trade['date']} {trade['time']} {trade['bias']} MFE:{trade['mfe_value']} Active:{trade['is_active']}")

if __name__ == "__main__":
    debug_trades()