#!/usr/bin/env python3
"""
Fix Calendar Discrepancy Between Signal Lab and Dashboard

The issue: Signal Lab calendar shows trades on Sunday, Monday, Tuesday
while Dashboard calendar shows no activity on those days.

Root cause: Different filtering logic between the two systems.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.railway_db import RailwayDB
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_calendar_discrepancy():
    """Analyze the discrepancy between Signal Lab and Dashboard calendars"""
    try:
        db = RailwayDB()
        cursor = db.conn.cursor()
        
        print("ANALYZING CALENDAR DISCREPANCY")
        print("=" * 50)
        
        # 1. Get ALL trades (Signal Lab view)
        cursor.execute("""
            SELECT date, COUNT(*) as trade_count,
                   COUNT(CASE WHEN COALESCE(mfe_none, mfe, 0) != 0 THEN 1 END) as with_mfe,
                   COUNT(CASE WHEN COALESCE(active_trade, false) = true THEN 1 END) as active_trades,
                   COUNT(CASE WHEN COALESCE(active_trade, false) = false THEN 1 END) as completed_trades
            FROM signal_lab_trades 
            WHERE date >= '2024-09-01' AND date <= '2024-09-30'
            GROUP BY date 
            ORDER BY date
        """)
        
        all_trades_by_date = cursor.fetchall()
        
        # 2. Get Dashboard-visible trades (analysis_only=true logic)
        cursor.execute("""
            SELECT date, COUNT(*) as trade_count
            FROM signal_lab_trades 
            WHERE COALESCE(mfe_none, mfe, 0) != 0
            AND COALESCE(active_trade, false) = false
            AND date >= '2024-09-01' AND date <= '2024-09-30'
            GROUP BY date 
            ORDER BY date
        """)
        
        dashboard_trades_by_date = cursor.fetchall()
        
        # Convert to dictionaries for easy comparison
        all_trades_dict = {str(row['date']): row for row in all_trades_by_date}
        dashboard_trades_dict = {str(row['date']): row for row in dashboard_trades_by_date}
        
        print("\nSIGNAL LAB CALENDAR (All Trades):")
        print("Date       | Total | With MFE | Active | Completed")
        print("-" * 50)
        for date_str, data in all_trades_dict.items():
            print(f"{date_str} | {data['trade_count']:5d} | {data['with_mfe']:8d} | {data['active_trades']:6d} | {data['completed_trades']:9d}")
        
        print("\nDASHBOARD CALENDAR (Processed Trades Only):")
        print("Date       | Visible")
        print("-" * 20)
        for date_str, data in dashboard_trades_dict.items():
            print(f"{date_str} | {data['trade_count']:7d}")
        
        print("\nDISCREPANCY ANALYSIS:")
        print("Date       | Signal Lab | Dashboard | Missing | Reason")
        print("-" * 60)
        
        discrepancies_found = []
        
        for date_str in all_trades_dict.keys():
            signal_lab_count = all_trades_dict[date_str]['trade_count']
            dashboard_count = dashboard_trades_dict.get(date_str, {'trade_count': 0})['trade_count']
            missing = signal_lab_count - dashboard_count
            
            if missing > 0:
                # Analyze why trades are missing
                data = all_trades_dict[date_str]
                if data['with_mfe'] == 0:
                    reason = "No MFE data"
                elif data['active_trades'] > 0:
                    reason = "Active trades"
                else:
                    reason = "Unknown"
                
                discrepancies_found.append({
                    'date': date_str,
                    'signal_lab': signal_lab_count,
                    'dashboard': dashboard_count,
                    'missing': missing,
                    'reason': reason
                })
                
                print(f"{date_str} | {signal_lab_count:10d} | {dashboard_count:9d} | {missing:7d} | {reason}")
        
        if not discrepancies_found:
            print("No discrepancies found - calendars are in sync!")
            return True
        
        print(f"\nFound {len(discrepancies_found)} dates with discrepancies")
        
        # 3. Detailed analysis of problematic dates
        print("\nDETAILED ANALYSIS OF PROBLEMATIC DATES:")
        for disc in discrepancies_found[:5]:  # Show first 5
            date_str = disc['date']
            print(f"\n{date_str}:")
            
            cursor.execute("""
                SELECT time, bias, session, signal_type,
                       COALESCE(mfe_none, mfe, 0) as mfe_value,
                       COALESCE(active_trade, false) as is_active
                FROM signal_lab_trades 
                WHERE date = %s
                ORDER BY time
            """, (date_str,))
            
            trades = cursor.fetchall()
            
            print("  Time     | Bias     | Session | MFE   | Active | Visible in Dashboard")
            print("  " + "-" * 65)
            
            for trade in trades:
                has_mfe = trade['mfe_value'] != 0
                is_active = trade['is_active']
                visible = has_mfe and not is_active
                
                print(f"  {trade['time']} | {trade['bias']:8s} | {trade['session']:7s} | {trade['mfe_value']:5.2f} | {str(is_active):6s} | {str(visible):6s}")
        
        return False
        
    except Exception as e:
        logger.error(f"Error analyzing calendar discrepancy: {str(e)}")
        return False

def fix_calendar_discrepancy():
    """Fix the calendar discrepancy by updating trade statuses"""
    try:
        db = RailwayDB()
        cursor = db.conn.cursor()
        
        print("\nFIXING CALENDAR DISCREPANCY")
        print("=" * 40)
        
        # Strategy 1: Mark all trades with MFE data as completed (non-active)
        cursor.execute("""
            UPDATE signal_lab_trades 
            SET active_trade = false 
            WHERE COALESCE(mfe_none, mfe, 0) != 0
            AND COALESCE(active_trade, false) = true
        """)
        
        fixed_count = cursor.rowcount
        print(f"Marked {fixed_count} trades with MFE data as completed")
        
        # Strategy 2: Mark historical trades (older than today) as completed
        cursor.execute("""
            UPDATE signal_lab_trades 
            SET active_trade = false 
            WHERE date < CURRENT_DATE
            AND COALESCE(active_trade, false) = true
        """)
        
        historical_fixed = cursor.rowcount
        print(f"Marked {historical_fixed} historical trades as completed")
        
        db.conn.commit()
        
        print(f"\nTOTAL FIXES APPLIED: {fixed_count + historical_fixed} trades")
        print("Calendar discrepancy should now be resolved!")
        
        return True
        
    except Exception as e:
        logger.error(f"Error fixing calendar discrepancy: {str(e)}")
        if hasattr(db, 'conn') and db.conn:
            db.conn.rollback()
        return False

def main():
    """Main function to analyze and fix calendar discrepancy"""
    print("CALENDAR DISCREPANCY DIAGNOSTIC TOOL")
    print("=" * 50)
    
    # Step 1: Analyze the discrepancy
    analysis_success = analyze_calendar_discrepancy()
    
    if not analysis_success:
        print("\nAnalysis failed - cannot proceed with fix")
        return
    
    # Step 2: Ask user if they want to apply the fix
    print("\n" + "=" * 50)
    response = input("Apply fix to resolve calendar discrepancy? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        fix_success = fix_calendar_discrepancy()
        
        if fix_success:
            print("\nCalendar discrepancy fixed successfully!")
            print("Please refresh both Signal Lab and Dashboard to see the changes")
        else:
            print("\nFix failed - please check the logs")
    else:
        print("\nFix skipped - discrepancy analysis complete")

if __name__ == "__main__":
    main()