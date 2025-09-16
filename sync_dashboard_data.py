#!/usr/bin/env python3
"""
Direct fix for dashboard sync issue
Makes main dashboard use same data as signal lab
"""

from database.railway_db import RailwayDB

def sync_dashboard_data():
    try:
        db = RailwayDB()
        cursor = db.conn.cursor()
        
        # Mark all completed trades as non-active so they show in dashboard
        cursor.execute("""
            UPDATE signal_lab_trades 
            SET active_trade = false 
            WHERE COALESCE(mfe_none, mfe, 0) != 0
            AND COALESCE(active_trade, true) = true
        """)
        
        updated_count = cursor.rowcount
        db.conn.commit()
        
        print(f"SUCCESS: Updated {updated_count} trades to show in dashboard")
        print("Main dashboard and signal lab should now show the same data")
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    sync_dashboard_data()