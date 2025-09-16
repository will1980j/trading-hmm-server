#!/usr/bin/env python3
"""
Fix dashboard synchronization by ensuring all trades with MFE data are marked as completed
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.railway_db import RailwayDB
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_dashboard_sync():
    """Fix the dashboard synchronization issue"""
    try:
        db = RailwayDB()
        cursor = db.conn.cursor()
        
        # 1. Check current state
        cursor.execute("SELECT COUNT(*) as total FROM signal_lab_trades")
        total_trades = cursor.fetchone()['total']
        
        cursor.execute("""
            SELECT COUNT(*) as with_mfe 
            FROM signal_lab_trades 
            WHERE COALESCE(mfe_none, mfe, 0) > 0
        """)
        trades_with_mfe = cursor.fetchone()['with_mfe']
        
        cursor.execute("""
            SELECT COUNT(*) as dashboard_visible 
            FROM signal_lab_trades 
            WHERE COALESCE(mfe_none, mfe, 0) > 0 
            AND COALESCE(active_trade, false) = false
        """)
        dashboard_visible = cursor.fetchone()['dashboard_visible']
        
        logger.info(f"Current state: {total_trades} total, {trades_with_mfe} with MFE, {dashboard_visible} dashboard visible")
        
        # 2. Fix: Mark all trades with MFE data as completed (not active)
        cursor.execute("""
            UPDATE signal_lab_trades 
            SET active_trade = false 
            WHERE COALESCE(mfe_none, mfe, 0) > 0
            AND COALESCE(active_trade, false) = true
        """)
        
        fixed_count = cursor.rowcount
        db.conn.commit()
        
        # 3. Verify fix
        cursor.execute("""
            SELECT COUNT(*) as dashboard_visible_after 
            FROM signal_lab_trades 
            WHERE COALESCE(mfe_none, mfe, 0) > 0 
            AND COALESCE(active_trade, false) = false
        """)
        dashboard_visible_after = cursor.fetchone()['dashboard_visible_after']
        
        logger.info(f"FIXED: {fixed_count} trades marked as completed")
        logger.info(f"Result: {dashboard_visible_after} trades now visible in both dashboards")
        
        # 4. Sample verification
        cursor.execute("""
            SELECT date, time, bias, session, 
                   COALESCE(mfe_none, mfe, 0) as mfe_value,
                   COALESCE(active_trade, false) as is_active
            FROM signal_lab_trades 
            WHERE COALESCE(mfe_none, mfe, 0) > 0
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        sample_trades = cursor.fetchall()
        logger.info("Sample of fixed trades:")
        for trade in sample_trades:
            logger.info(f"  {trade['date']} {trade['time']} {trade['bias']} - MFE: {trade['mfe_value']:.2f}R, Active: {trade['is_active']}")
        
        return {
            'status': 'success',
            'total_trades': total_trades,
            'trades_with_mfe': trades_with_mfe,
            'dashboard_visible_before': dashboard_visible,
            'dashboard_visible_after': dashboard_visible_after,
            'fixed_count': fixed_count
        }
        
    except Exception as e:
        logger.error(f"Error fixing dashboard sync: {str(e)}")
        return {'status': 'error', 'error': str(e)}

if __name__ == "__main__":
    result = fix_dashboard_sync()
    print(f"Dashboard sync fix result: {result}")