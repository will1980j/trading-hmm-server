"""
Check when the Dec 8th trade's stop was actually hit
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

trade_id = "20251208_093900000_BEARISH"

print("=" * 80)
print(f"WHEN WAS STOP HIT: {trade_id}")
print("=" * 80)
print()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Get entry and stop
cur.execute("""
    SELECT entry_price, stop_loss, direction
    FROM automated_signals
    WHERE trade_id = %s
    AND event_type = 'ENTRY'
""", (trade_id,))

entry_data = cur.fetchone()

if not entry_data:
    print("❌ No ENTRY event found")
    exit(1)

entry_price = float(entry_data[0])
stop_loss = float(entry_data[1])
direction = entry_data[2]

print(f"Trade Details:")
print(f"   Entry: ${entry_price}")
print(f"   Stop: ${stop_loss}")
print(f"   Direction: {direction} (SHORT)")
print()
print(f"For a SHORT trade, stop is hit when price >= ${stop_loss}")
print()

# Check all MFE_UPDATE events to find when stop was hit
cur.execute("""
    SELECT 
        timestamp,
        current_price,
        be_mfe,
        no_be_mfe
    FROM automated_signals
    WHERE trade_id = %s
    AND event_type = 'MFE_UPDATE'
    ORDER BY timestamp ASC
""", (trade_id,))

mfe_updates = cur.fetchall()

print(f"Total MFE_UPDATE events: {len(mfe_updates)}")
print()

# Find when stop was hit
stop_hit_events = []
for update in mfe_updates:
    timestamp = update[0]
    current_price = float(update[1])
    
    # For SHORT: stop is hit when price >= stop_loss
    if current_price >= stop_loss:
        stop_hit_events.append({
            'timestamp': timestamp,
            'price': current_price,
            'be_mfe': float(update[2]) if update[2] else None,
            'no_be_mfe': float(update[3]) if update[3] else None
        })

if stop_hit_events:
    print(f"🚨 STOP WAS HIT {len(stop_hit_events)} times!")
    print()
    print("First time stop was hit:")
    first_hit = stop_hit_events[0]
    print(f"   Date: {first_hit['timestamp'].strftime('%Y-%m-%d')}")
    print(f"   Time: {first_hit['timestamp'].strftime('%H:%M:%S')}")
    print(f"   Price: ${first_hit['price']}")
    print(f"   Stop: ${stop_loss}")
    print(f"   BE MFE at stop: {first_hit['be_mfe']}R")
    print(f"   No-BE MFE at stop: {first_hit['no_be_mfe']}R")
    print()
    
    if len(stop_hit_events) > 1:
        print(f"Stop was hit {len(stop_hit_events)} times total")
        print(f"Last time: {stop_hit_events[-1]['timestamp']}")
    
    print()
    print("=" * 80)
    print("DIAGNOSIS")
    print("=" * 80)
    print()
    print("❌ INDICATOR BUG: Stop loss was hit but EXIT event was never sent!")
    print()
    print("Possible causes:")
    print("1. Indicator's stop detection logic is broken")
    print("2. Indicator is checking wrong price (close vs high)")
    print("3. Indicator lost tracking before stop was hit")
    print("4. EXIT webhook failed to send")
    print()
    print("Solution:")
    print("1. Fix indicator stop detection logic")
    print("2. Hybrid Sync should detect missed exits and insert EXIT_SL")
    print("3. Add 'stale trade cleanup' (auto-close trades >3 days old)")
    
else:
    print("✅ Stop was NEVER hit according to MFE_UPDATE prices")
    print()
    print("   This means:")
    print("   - Price never went above $25,835.00")
    print("   - Trade is legitimately still active")
    print("   - Indicator is tracking correctly")
    print()
    print("   But you said it should have been stopped out on Dec 10th...")
    print("   Let me check prices around Dec 10th:")
    
    # Check prices around Dec 10th
    cur.execute("""
        SELECT 
            timestamp,
            current_price
        FROM automated_signals
        WHERE trade_id = %s
        AND event_type = 'MFE_UPDATE'
        AND timestamp >= '2025-12-10 00:00:00'
        AND timestamp <= '2025-12-10 23:59:59'
        ORDER BY timestamp ASC
    """, (trade_id,))
    
    dec10_prices = cur.fetchall()
    
    if dec10_prices:
        print(f"\n   Prices on Dec 10th:")
        max_price = max(float(p[1]) for p in dec10_prices)
        print(f"      Highest price: ${max_price}")
        print(f"      Stop loss: ${stop_loss}")
        print(f"      Difference: ${stop_loss - max_price}")
        
        if max_price >= stop_loss:
            print(f"\n      🚨 STOP WAS HIT on Dec 10th at ${max_price}!")
        else:
            print(f"\n      ✅ Stop was NOT hit on Dec 10th (max ${max_price} < stop ${stop_loss})")

cur.close()
conn.close()
