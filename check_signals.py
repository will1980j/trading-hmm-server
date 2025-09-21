#!/usr/bin/env python3
"""Quick script to check signals in database"""

try:
    from database.railway_db import RailwayDB
    
    db = RailwayDB()
    if db.conn:
        cursor = db.conn.cursor()
        
        # Check live signals
        cursor.execute("SELECT COUNT(*) as count FROM live_signals")
        live_count = cursor.fetchone()['count']
        print(f"Live signals: {live_count}")
        
        # Check recent signals
        cursor.execute("SELECT symbol, bias, timestamp FROM live_signals ORDER BY timestamp DESC LIMIT 5")
        recent = cursor.fetchall()
        print("\nRecent signals:")
        for signal in recent:
            print(f"- {signal['symbol']} {signal['bias']} at {signal['timestamp']}")
            
        # Check signal lab trades
        cursor.execute("SELECT COUNT(*) as count FROM signal_lab_trades")
        lab_count = cursor.fetchone()['count']
        print(f"\nSignal lab trades: {lab_count}")
        
    else:
        print("No database connection")
        
except Exception as e:
    print(f"Error: {e}")