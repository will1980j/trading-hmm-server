#!/usr/bin/env python3
"""
Fix Active Trades Data Recovery Script
Restores missing trades that were incorrectly marked as active or excluded
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.railway_db import RailwayDB
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_active_trades():
    """Fix active trades data and restore missing trades"""
    try:
        db = RailwayDB()
        cursor = db.conn.cursor()
        
        # 1. Check current state
        cursor.execute("SELECT COUNT(*) as total FROM signal_lab_trades")
        total_trades = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as active FROM signal_lab_trades WHERE COALESCE(active_trade, false) = true")
        active_trades = cursor.fetchone()['active']
        
        cursor.execute("SELECT COUNT(*) as completed FROM signal_lab_trades WHERE COALESCE(active_trade, false) = false")
        completed_trades = cursor.fetchone()['completed']
        
        logger.info(f"Current state: {total_trades} total, {active_trades} active, {completed_trades} completed")
        
        # 2. Find trades that should NOT be active (have MFE data but marked as active)
        cursor.execute("""
            SELECT id, date, time, bias, session, signal_type, 
                   COALESCE(mfe_none, mfe, 0) as mfe_value,
                   COALESCE(active_trade, false) as is_active
            FROM signal_lab_trades 
            WHERE COALESCE(active_trade, false) = true
            AND COALESCE(mfe_none, mfe, 0) != 0
            ORDER BY date DESC, time DESC
        """)
        
        incorrectly_active = cursor.fetchall()
        logger.info(f"Found {len(incorrectly_active)} trades marked as active but have MFE data")
        
        # 3. Mark these trades as completed (not active)
        if incorrectly_active:
            trade_ids = [trade['id'] for trade in incorrectly_active]
            placeholders = ','.join(['%s'] * len(trade_ids))
            
            cursor.execute(f"""
                UPDATE signal_lab_trades 
                SET active_trade = false 
                WHERE id IN ({placeholders})
            """, trade_ids)
            
            rows_updated = cursor.rowcount
            logger.info(f"Marked {rows_updated} trades as completed (not active)")
        
        # 4. Check for trades with invalid dates that might be causing issues
        cursor.execute("""
            SELECT COUNT(*) as invalid_dates
            FROM signal_lab_trades 
            WHERE date IS NULL OR time IS NULL OR date::text = 'Invalid Date'
        """)
        
        invalid_dates = cursor.fetchone()['invalid_dates']
        if invalid_dates > 0:
            logger.warning(f"Found {invalid_dates} trades with invalid dates")
            
            # Delete trades with invalid dates
            cursor.execute("""
                DELETE FROM signal_lab_trades 
                WHERE date IS NULL OR time IS NULL OR date::text = 'Invalid Date'
            """)
            
            deleted_invalid = cursor.rowcount
            logger.info(f"Deleted {deleted_invalid} trades with invalid dates")
        
        # 5. Ensure all trades from before today are marked as completed
        cursor.execute("""
            UPDATE signal_lab_trades 
            SET active_trade = false 
            WHERE date < CURRENT_DATE
            AND COALESCE(active_trade, false) = true
        """)
        
        historical_updated = cursor.rowcount
        if historical_updated > 0:
            logger.info(f"Marked {historical_updated} historical trades as completed")
        
        # 6. Check final state
        cursor.execute("SELECT COUNT(*) as total FROM signal_lab_trades")
        final_total = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as active FROM signal_lab_trades WHERE COALESCE(active_trade, false) = true")
        final_active = cursor.fetchone()['active']
        
        cursor.execute("SELECT COUNT(*) as completed FROM signal_lab_trades WHERE COALESCE(active_trade, false) = false")
        final_completed = cursor.fetchone()['completed']
        
        # 7. Get sample of recent completed trades to verify
        cursor.execute("""
            SELECT date, time, bias, session, signal_type, 
                   COALESCE(mfe_none, mfe, 0) as mfe_value
            FROM signal_lab_trades 
            WHERE COALESCE(active_trade, false) = false
            AND COALESCE(mfe_none, mfe, 0) != 0
            ORDER BY date DESC, time DESC
            LIMIT 10
        """)
        
        sample_trades = cursor.fetchall()
        
        db.conn.commit()
        
        logger.info(f"Final state: {final_total} total, {final_active} active, {final_completed} completed")
        logger.info("Sample of restored trades:")
        for trade in sample_trades:
            logger.info(f"  {trade['date']} {trade['time']} {trade['bias']} {trade['session']} MFE: {trade['mfe_value']:.2f}R")
        
        return {
            'status': 'success',
            'before': {'total': total_trades, 'active': active_trades, 'completed': completed_trades},
            'after': {'total': final_total, 'active': final_active, 'completed': final_completed},
            'changes': {
                'incorrectly_active_fixed': len(incorrectly_active),
                'invalid_dates_deleted': invalid_dates,
                'historical_completed': historical_updated
            }
        }
        
    except Exception as e:
        logger.error(f"Error fixing active trades: {str(e)}")
        if 'db' in locals() and hasattr(db, 'conn'):
            db.conn.rollback()
        return {'status': 'error', 'message': str(e)}

if __name__ == "__main__":
    result = fix_active_trades()
    print(f"Fix result: {result}")