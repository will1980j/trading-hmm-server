"""
Check Signal Lab data and diagnose calendar display issues
"""

import os
import psycopg2
from datetime import datetime

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL')

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("=" * 80)
    print("SIGNAL LAB DATA CHECK")
    print("=" * 80)
    
    # Check signal_lab_trades table
    cur.execute("""
        SELECT COUNT(*) FROM signal_lab_trades
    """)
    total_count = cur.fetchone()[0]
    print(f"\n📊 Total Signal Lab Trades: {total_count}")
    
    if total_count > 0:
        # Check date range
        cur.execute("""
            SELECT 
                MIN(date) as earliest_date,
                MAX(date) as latest_date
            FROM signal_lab_trades
        """)
        date_range = cur.fetchone()
        print(f"📅 Date Range: {date_range[0]} to {date_range[1]}")
        
        # Check recent trades
        cur.execute("""
            SELECT 
                date,
                session,
                bias,
                mfe,
                outcome
            FROM signal_lab_trades
            ORDER BY date DESC, time DESC
            LIMIT 10
        """)
        recent = cur.fetchall()
        print(f"\n🔍 Recent 10 Trades:")
        for trade in recent:
            print(f"  {trade[0]} | {trade[1]} | {trade[2]} | MFE: {trade[3]}R | {trade[4]}")
        
        # Check trades by date
        cur.execute("""
            SELECT 
                date,
                COUNT(*) as trade_count,
                AVG(mfe) as avg_mfe
            FROM signal_lab_trades
            GROUP BY date
            ORDER BY date DESC
            LIMIT 10
        """)
        by_date = cur.fetchall()
        print(f"\n📆 Trades by Date (Last 10 days):")
        for day in by_date:
            print(f"  {day[0]}: {day[1]} trades, Avg MFE: {day[2]:.2f}R")
        
        # Check for NULL dates
        cur.execute("""
            SELECT COUNT(*) FROM signal_lab_trades WHERE date IS NULL
        """)
        null_dates = cur.fetchone()[0]
        if null_dates > 0:
            print(f"\n⚠️ WARNING: {null_dates} trades have NULL dates!")
        
        # Check date format
        cur.execute("""
            SELECT DISTINCT date 
            FROM signal_lab_trades 
            ORDER BY date DESC 
            LIMIT 5
        """)
        sample_dates = cur.fetchall()
        print(f"\n📋 Sample Date Formats:")
        for d in sample_dates:
            print(f"  {d[0]} (type: {type(d[0])})")
    
    else:
        print("\n❌ No trades found in signal_lab_trades table!")
        print("\nPossible issues:")
        print("  1. No data has been entered into Signal Lab")
        print("  2. Data is in a different table")
        print("  3. Database connection issue")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("✅ Check complete!")
    print("=" * 80)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
