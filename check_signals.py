#!/usr/bin/env python3
"""
Quick signal check - minimal memory usage
"""
import os
from dotenv import load_dotenv
load_dotenv()

try:
    from psycopg2 import connect
    from psycopg2.extras import RealDictCursor
    
    # Quick connection
    db_url = os.getenv('DATABASE_URL')
    conn = connect(db_url, cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    
    print("🔍 QUICK SIGNAL CHECK")
    print("=" * 30)
    
    # Check last 5 signals only
    cursor.execute("""
        SELECT symbol, bias, htf_aligned, timestamp
        FROM live_signals 
        ORDER BY timestamp DESC 
        LIMIT 5
    """)
    
    signals = cursor.fetchall()
    print(f"\nLast 5 signals:")
    for s in signals:
        auto = "✅ WOULD AUTO-POP" if (s['symbol'] == 'NQ1!' and s['htf_aligned']) else "❌ SKIPPED"
        print(f"  {s['symbol']} | {s['bias']} | HTF:{s['htf_aligned']} | {auto}")
    
    # Check symbols
    cursor.execute("""
        SELECT DISTINCT symbol 
        FROM live_signals 
        WHERE timestamp > NOW() - INTERVAL '6 hours'
    """)
    
    symbols = cursor.fetchall()
    print(f"\nSymbols (last 6h): {[s['symbol'] for s in symbols]}")
    
    # Check auto-pop count
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM signal_lab_trades 
        WHERE created_at > NOW() - INTERVAL '6 hours'
        AND htf_aligned = true
    """)
    
    auto_count = cursor.fetchone()
    print(f"Auto-populated trades (6h): {auto_count['count']}")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {str(e)}")