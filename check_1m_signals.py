from database.railway_db import RailwayDB
from datetime import datetime, timedelta

db = RailwayDB()
cursor = db.conn.cursor()

# Check 1M signals
cursor.execute("""
    SELECT symbol, timeframe, bias, price, strength, htf_aligned, 
           timestamp, signal_type
    FROM live_signals 
    WHERE timeframe = '1m' 
    ORDER BY timestamp DESC 
    LIMIT 20
""")

rows = cursor.fetchall()

print(f"\n{'='*80}")
print(f"CHECKING 1M SIGNALS - Total found: {len(rows)}")
print(f"{'='*80}\n")

if not rows:
    print("❌ NO 1M SIGNALS FOUND IN DATABASE")
    print("\nThis means:")
    print("1. TradingView webhook is not sending 1M signals")
    print("2. Or the signals are being filtered out")
    print("3. Or the timeframe is not being set correctly")
else:
    # Check if signals are recent (within last 24 hours)
    now = datetime.now()
    recent_count = 0
    old_count = 0
    
    for row in rows:
        age = now - row['timestamp'].replace(tzinfo=None)
        is_recent = age < timedelta(hours=24)
        
        if is_recent:
            recent_count += 1
            status = "✅ RECENT"
        else:
            old_count += 1
            status = "⚠️ OLD"
        
        print(f"{status} | {row['timestamp']} | {row['symbol']} | {row['bias']} | "
              f"${row['price']:,.2f} | {row['strength']}% | HTF:{row['htf_aligned']} | {row['signal_type']}")
    
    print(f"\n{'='*80}")
    print(f"SUMMARY:")
    print(f"  Recent signals (< 24h): {recent_count}")
    print(f"  Old signals (> 24h): {old_count}")
    print(f"{'='*80}\n")
    
    if recent_count == 0:
        print("⚠️ WARNING: All signals are OLD (> 24 hours)")
        print("This suggests TradingView is NOT sending live 1M signals currently")
    else:
        print("✅ GOOD: Recent 1M signals detected")

# Check if there are ANY recent signals (any timeframe)
cursor.execute("""
    SELECT COUNT(*) as count 
    FROM live_signals 
    WHERE timestamp > NOW() - INTERVAL '1 hour'
""")
recent_any = cursor.fetchone()['count']

print(f"\nRecent signals (any timeframe, last 1 hour): {recent_any}")

if recent_any == 0:
    print("❌ NO RECENT SIGNALS AT ALL - TradingView webhook may be down")
else:
    print("✅ TradingView webhook is working (receiving signals)")

db.conn.close()
