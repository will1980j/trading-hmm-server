"""
Check the test trade we just created
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Use the trade_id from the last test
trade_id = "20251213_140727000_BULLISH"  # From previous test

print(f"Checking trade: {trade_id}")
print("=" * 80)

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Get all events
cur.execute("""
    SELECT 
        event_type,
        timestamp,
        entry_price,
        stop_loss,
        be_mfe,
        no_be_mfe,
        current_price,
        exit_price
    FROM automated_signals
    WHERE trade_id = %s
    ORDER BY timestamp ASC
""", (trade_id,))

events = cur.fetchall()

print(f"Total events: {len(events)}")
print()

for i, event in enumerate(events, 1):
    print(f"{i}. {event[0]}")
    print(f"   Timestamp: {event[1]}")
    if event[2]:
        print(f"   Entry: ${event[2]}")
    if event[3]:
        print(f"   Stop: ${event[3]}")
    if event[4] is not None:
        print(f"   BE MFE: {float(event[4]):.2f}R")
    if event[5] is not None:
        print(f"   No-BE MFE: {float(event[5]):.2f}R")
    if event[6]:
        print(f"   Current Price: ${event[6]}")
    if event[7]:
        print(f"   Exit Price: ${event[7]}")
    print()

# Check if ENTRY exists
has_entry = any(e[0] == 'ENTRY' for e in events)
print(f"Has ENTRY: {has_entry}")

if has_entry:
    print("✅ ENTRY exists - lifecycle enforcement should allow MFE_UPDATE")
else:
    print("❌ ENTRY missing - this explains why MFE_UPDATE was rejected")

cur.close()
conn.close()
