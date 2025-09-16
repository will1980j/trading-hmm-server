#!/usr/bin/env python3
"""
Debug script to check what signals are being received and why they're not auto-populating
"""

import os
import sys
from dotenv import load_dotenv
load_dotenv()

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.railway_db import RailwayDB

def debug_signals():
    """Debug recent signals and auto-population logic"""
    try:
        db = RailwayDB()
        cursor = db.conn.cursor()
        
        print("🔍 SIGNAL DEBUG ANALYSIS")
        print("=" * 50)
        
        # 1. Check recent live signals
        print("\n1. RECENT LIVE SIGNALS (Last 10):")
        cursor.execute("""
            SELECT symbol, bias, price, htf_aligned, htf_status, session, 
                   signal_type, timestamp, strength
            FROM live_signals 
            ORDER BY timestamp DESC 
            LIMIT 10
        """)
        
        recent_signals = cursor.fetchall()
        if recent_signals:
            for signal in recent_signals:
                htf_status = "✅ HTF ALIGNED" if signal['htf_aligned'] else "❌ NOT HTF ALIGNED"
                auto_pop = "🎯 WOULD AUTO-POP" if (signal['symbol'] == 'NQ1!' and signal['htf_aligned']) else "⚠️ SKIPPED"
                
                print(f"  {signal['symbol']} | {signal['bias']} | ${signal['price']:,.2f} | {htf_status} | {auto_pop}")
                print(f"    Session: {signal['session']} | Type: {signal['signal_type']} | Strength: {signal['strength']}%")
                print(f"    Time: {signal['timestamp']}")
                print()
        else:
            print("  No recent live signals found")
        
        # 2. Check signal lab auto-populated trades
        print("\n2. RECENT AUTO-POPULATED TRADES (Last 5):")
        cursor.execute("""
            SELECT date, time, bias, session, signal_type, entry_price, 
                   COALESCE(active_trade, false) as is_active, htf_aligned
            FROM signal_lab_trades 
            WHERE htf_aligned = true
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        auto_trades = cursor.fetchall()
        if auto_trades:
            for trade in auto_trades:
                status = "🔴 ACTIVE" if trade['is_active'] else "✅ COMPLETED"
                print(f"  {trade['date']} {trade['time']} | {trade['bias']} | ${trade['entry_price']:,.2f} | {status}")
                print(f"    Session: {trade['session']} | Type: {trade['signal_type']}")
                print()
        else:
            print("  No auto-populated trades found")
        
        # 3. Check symbol distribution
        print("\n3. SYMBOL DISTRIBUTION (Last 24 hours):")
        cursor.execute("""
            SELECT symbol, COUNT(*) as count, 
                   SUM(CASE WHEN htf_aligned THEN 1 ELSE 0 END) as htf_aligned_count
            FROM live_signals 
            WHERE timestamp > NOW() - INTERVAL '24 hours'
            GROUP BY symbol 
            ORDER BY count DESC
        """)
        
        symbols = cursor.fetchall()
        if symbols:
            for sym in symbols:
                print(f"  {sym['symbol']}: {sym['count']} total, {sym['htf_aligned_count']} HTF aligned")
        else:
            print("  No signals in last 24 hours")
        
        # 4. Check HTF alignment distribution
        print("\n4. HTF ALIGNMENT STATUS (Last 24 hours):")
        cursor.execute("""
            SELECT htf_aligned, htf_status, COUNT(*) as count
            FROM live_signals 
            WHERE timestamp > NOW() - INTERVAL '24 hours'
            GROUP BY htf_aligned, htf_status 
            ORDER BY count DESC
        """)
        
        htf_stats = cursor.fetchall()
        if htf_stats:
            for stat in htf_stats:
                print(f"  HTF Aligned: {stat['htf_aligned']} | Status: {stat['htf_status']} | Count: {stat['count']}")
        else:
            print("  No HTF data available")
        
        # 5. Check auto-population criteria
        print("\n5. AUTO-POPULATION ANALYSIS:")
        cursor.execute("""
            SELECT COUNT(*) as total_nq_signals,
                   SUM(CASE WHEN htf_aligned THEN 1 ELSE 0 END) as htf_aligned_nq,
                   SUM(CASE WHEN htf_aligned AND symbol = 'NQ1!' THEN 1 ELSE 0 END) as should_auto_pop
            FROM live_signals 
            WHERE symbol LIKE '%NQ%' 
            AND timestamp > NOW() - INTERVAL '24 hours'
        """)
        
        auto_analysis = cursor.fetchone()
        if auto_analysis:
            print(f"  Total NQ signals: {auto_analysis['total_nq_signals']}")
            print(f"  HTF aligned NQ: {auto_analysis['htf_aligned_nq']}")
            print(f"  Should auto-populate: {auto_analysis['should_auto_pop']}")
            
            if auto_analysis['should_auto_pop'] == 0:
                print("  ⚠️ ISSUE: No signals meet auto-population criteria!")
                if auto_analysis['htf_aligned_nq'] == 0:
                    print("     - No HTF aligned NQ signals received")
                else:
                    print("     - HTF aligned signals exist but symbol != 'NQ1!'")
        
        # 6. Recent contract rollover check
        print("\n6. CONTRACT ROLLOVER CHECK:")
        cursor.execute("""
            SELECT DISTINCT symbol 
            FROM live_signals 
            WHERE symbol LIKE '%NQ%' 
            AND timestamp > NOW() - INTERVAL '7 days'
            ORDER BY symbol
        """)
        
        nq_symbols = cursor.fetchall()
        if nq_symbols:
            print("  NQ-related symbols received:")
            for sym in nq_symbols:
                print(f"    - {sym['symbol']}")
                
            if len(nq_symbols) > 1:
                print("  🚨 MULTIPLE NQ SYMBOLS DETECTED - Possible contract rollover!")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_signals()