#!/usr/bin/env python3
"""
Direct Fix for Signal Lab Dashboard Sync
Directly fixes the database to ensure processed trades appear in dashboard
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fix_signal_sync():
    """Fix the signal sync issue directly in the database"""
    
    print("DIRECT FIX: SIGNAL LAB <-> DASHBOARD SYNC")
    print("=" * 50)
    
    try:
        # Import database connection
        sys.path.append(os.path.dirname(__file__))
        from database.railway_db import RailwayDB
        
        db = RailwayDB()
        cursor = db.conn.cursor()
        
        print("1. Analyzing current state...")
        
        # Get total trades
        cursor.execute("SELECT COUNT(*) as total FROM signal_lab_trades")
        total_trades = cursor.fetchone()['total']
        
        # Get dashboard-visible trades (the filtering logic from web_server.py)
        cursor.execute("""
            SELECT COUNT(*) as dashboard_visible 
            FROM signal_lab_trades 
            WHERE COALESCE(mfe_none, mfe, 0) != 0
            AND COALESCE(active_trade, false) = false
        """)
        dashboard_visible = cursor.fetchone()['dashboard_visible']
        
        # Get trades with MFE but still marked as active
        cursor.execute("""
            SELECT COUNT(*) as needs_fix
            FROM signal_lab_trades 
            WHERE COALESCE(mfe_none, mfe, 0) != 0
            AND COALESCE(active_trade, false) = true
        """)
        needs_fix = cursor.fetchone()['needs_fix']
        
        print(f"   Total Signal Lab trades: {total_trades}")
        print(f"   Dashboard visible trades: {dashboard_visible}")
        print(f"   Trades needing fix: {needs_fix}")
        print(f"   Discrepancy: {total_trades - dashboard_visible}")
        
        if needs_fix > 0:
            print(f"\\n2. Applying fix...")
            print(f"   Marking {needs_fix} completed trades as non-active...")
            
            # Fix: Mark all trades with MFE data as completed (active_trade = false)
            cursor.execute("""
                UPDATE signal_lab_trades 
                SET active_trade = false 
                WHERE COALESCE(mfe_none, mfe, 0) != 0
                AND COALESCE(active_trade, false) = true
            """)
            
            fixed_count = cursor.rowcount
            db.conn.commit()
            
            print(f"   SUCCESS: Fixed {fixed_count} trades")
            
            # Verify the fix
            print(f"\\n3. Verifying fix...")
            
            cursor.execute("""
                SELECT COUNT(*) as dashboard_visible_after 
                FROM signal_lab_trades 
                WHERE COALESCE(mfe_none, mfe, 0) != 0
                AND COALESCE(active_trade, false) = false
            """)
            dashboard_visible_after = cursor.fetchone()['dashboard_visible_after']
            
            print(f"   Dashboard visible trades after fix: {dashboard_visible_after}")
            print(f"   Improvement: +{dashboard_visible_after - dashboard_visible} trades")
            
            if dashboard_visible_after > dashboard_visible:
                print(f"   ✅ SUCCESS: Signal Lab and Dashboard are now reconciled!")
                print(f"   ✅ All processed trades (with MFE data) now appear in both systems")
            else:
                print(f"   ⚠️  No improvement detected - there may be other issues")
        
        else:
            print(f"\\n   ✅ No fix needed - systems are already in sync!")
        
        # Show sample of remaining active trades (these should be incomplete/in-progress)
        cursor.execute("""
            SELECT id, date, time, bias, 
                   COALESCE(mfe_none, mfe, 0) as mfe_value,
                   COALESCE(active_trade, false) as is_active
            FROM signal_lab_trades 
            WHERE COALESCE(active_trade, false) = true
            ORDER BY created_at DESC
            LIMIT 5
        """)
        
        active_trades = cursor.fetchall()
        
        if active_trades:
            print(f"\\n4. Remaining active trades (should be incomplete):")
            for trade in active_trades:
                print(f"   ID {trade['id']}: {trade['date']} {trade['time']} {trade['bias']} (MFE: {trade['mfe_value']})")
        else:
            print(f"\\n4. No active trades remaining")
        
        print(f"\\nFIX COMPLETE!")
        print(f"Signal Lab and Dashboard should now show the same processed trades.")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_signal_sync()