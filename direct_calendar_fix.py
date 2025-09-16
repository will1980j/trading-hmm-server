#!/usr/bin/env python3
"""
Direct Calendar Fix - Resolve discrepancy between Signal Lab and Dashboard calendars
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.railway_db import RailwayDB
from datetime import datetime

def fix_calendar_discrepancy():
    """Fix the calendar discrepancy by updating trade statuses"""
    try:
        db = RailwayDB()
        cursor = db.conn.cursor()
        
        print("FIXING CALENDAR DISCREPANCY")
        print("=" * 40)
        
        # Get current state
        cursor.execute("SELECT COUNT(*) as total FROM signal_lab_trades")
        total_trades = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as active FROM signal_lab_trades WHERE COALESCE(active_trade, false) = true")
        active_trades = cursor.fetchone()['active']
        
        cursor.execute("SELECT COUNT(*) as with_mfe FROM signal_lab_trades WHERE COALESCE(mfe_none, mfe, 0) != 0")
        trades_with_mfe = cursor.fetchone()['with_mfe']
        
        print(f"Current state: {total_trades} total trades, {active_trades} active, {trades_with_mfe} with MFE data")
        
        # Fix 1: Mark all trades with MFE data as completed (non-active)
        cursor.execute("""
            UPDATE signal_lab_trades 
            SET active_trade = false 
            WHERE COALESCE(mfe_none, mfe, 0) != 0
            AND COALESCE(active_trade, false) = true
        """)
        
        fixed_mfe_count = cursor.rowcount
        print(f"Fixed {fixed_mfe_count} trades with MFE data - marked as completed")
        
        # Fix 2: Mark all historical trades (before today) as completed
        cursor.execute("""
            UPDATE signal_lab_trades 
            SET active_trade = false 
            WHERE date < CURRENT_DATE
            AND COALESCE(active_trade, false) = true
        """)
        
        fixed_historical_count = cursor.rowcount
        print(f"Fixed {fixed_historical_count} historical trades - marked as completed")
        
        # Fix 3: Ensure all September 1-3 trades are visible in dashboard
        cursor.execute("""
            UPDATE signal_lab_trades 
            SET active_trade = false 
            WHERE date IN ('2024-09-01', '2024-09-02', '2024-09-03')
            AND COALESCE(active_trade, false) = true
        """)
        
        fixed_sept_count = cursor.rowcount
        print(f"Fixed {fixed_sept_count} September 1-3 trades - marked as completed")
        
        db.conn.commit()
        
        # Verify the fix
        cursor.execute("""
            SELECT date, COUNT(*) as total_trades,
                   COUNT(CASE WHEN COALESCE(mfe_none, mfe, 0) != 0 AND COALESCE(active_trade, false) = false THEN 1 END) as dashboard_visible
            FROM signal_lab_trades 
            WHERE date IN ('2024-09-01', '2024-09-02', '2024-09-03')
            GROUP BY date 
            ORDER BY date
        """)
        
        verification = cursor.fetchall()
        
        print("\nVerification - September 1-3 trades:")
        print("Date       | Total | Dashboard Visible")
        print("-" * 35)
        for row in verification:
            print(f"{row['date']} | {row['total_trades']:5d} | {row['dashboard_visible']:15d}")
        
        total_fixed = fixed_mfe_count + fixed_historical_count + fixed_sept_count
        print(f"\nTOTAL FIXES APPLIED: {total_fixed} trades")
        print("Calendar discrepancy should now be resolved!")
        
        return True
        
    except Exception as e:
        print(f"Error fixing calendar discrepancy: {str(e)}")
        if hasattr(db, 'conn') and db.conn:
            db.conn.rollback()
        return False

if __name__ == "__main__":
    fix_calendar_discrepancy()