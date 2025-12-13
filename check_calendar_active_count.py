"""
Check calendar active trades count vs actual active trades
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

print("=" * 80)
print("CALENDAR ACTIVE TRADES COUNT CHECK")
print("=" * 80)
print()

# Method 1: Count active trades (no EXIT event)
print("METHOD 1: Trades without EXIT event")
cur.execute("""
    SELECT COUNT(DISTINCT e.trade_id)
    FROM automated_signals e
    WHERE e.event_type = 'ENTRY'
    AND e.trade_id NOT IN (
        SELECT DISTINCT trade_id 
        FROM automated_signals 
        WHERE event_type LIKE 'EXIT_%'
    )
""")

active_no_exit = cur.fetchone()[0]
print(f"   Active trades (no EXIT): {active_no_exit}")

# Method 2: What the calendar API might be using
print("\nMETHOD 2: Calendar API query")
cur.execute("""
    SELECT COUNT(DISTINCT e.trade_id)
    FROM automated_signals e
    WHERE e.event_type = 'ENTRY'
    AND e.signal_date >= CURRENT_DATE - INTERVAL '7 days'
    AND e.trade_id NOT IN (
        SELECT DISTINCT trade_id 
        FROM automated_signals 
        WHERE event_type LIKE 'EXIT_%'
    )
""")

active_last_7_days = cur.fetchone()[0]
print(f"   Active trades (last 7 days): {active_last_7_days}")

# Method 3: Check what calendar endpoint actually returns
print("\nMETHOD 3: Checking actual calendar data...")

# List all active trades
cur.execute("""
    SELECT 
        e.trade_id,
        e.signal_date,
        e.signal_time,
        e.direction,
        e.entry_price,
        e.stop_loss,
        EXTRACT(DAY FROM (CURRENT_DATE - e.signal_date)) as days_old
    FROM automated_signals e
    WHERE e.event_type = 'ENTRY'
    AND e.trade_id NOT IN (
        SELECT DISTINCT trade_id 
        FROM automated_signals 
        WHERE event_type LIKE 'EXIT_%'
    )
    ORDER BY e.signal_date DESC, e.signal_time DESC
""")

all_active = cur.fetchall()

print(f"\nAll active trades: {len(all_active)}")
print()

# Group by date
from collections import defaultdict
by_date = defaultdict(list)

for trade in all_active:
    date = str(trade[1])
    by_date[date].append(trade)

print("Active trades by date:")
for date in sorted(by_date.keys(), reverse=True):
    trades = by_date[date]
    print(f"\n   {date}: {len(trades)} trades")
    for trade in trades[:3]:  # Show first 3
        print(f"      {trade[0][:30]}... | {trade[3]} | Entry: ${trade[4]} | {int(trade[6])} days old")
    if len(trades) > 3:
        print(f"      ... and {len(trades) - 3} more")

# Check if calendar is filtering by date range
print()
print("=" * 80)
print("CALENDAR FILTER ANALYSIS")
print("=" * 80)
print()

# Check different date ranges
date_ranges = [
    ("Today", "CURRENT_DATE"),
    ("Last 3 days", "CURRENT_DATE - INTERVAL '3 days'"),
    ("Last 7 days", "CURRENT_DATE - INTERVAL '7 days'"),
    ("Last 14 days", "CURRENT_DATE - INTERVAL '14 days'"),
    ("Last 30 days", "CURRENT_DATE - INTERVAL '30 days'"),
]

for label, date_filter in date_ranges:
    cur.execute(f"""
        SELECT COUNT(DISTINCT e.trade_id)
        FROM automated_signals e
        WHERE e.event_type = 'ENTRY'
        AND e.signal_date >= {date_filter}
        AND e.trade_id NOT IN (
            SELECT DISTINCT trade_id 
            FROM automated_signals 
            WHERE event_type LIKE 'EXIT_%'
        )
    """)
    
    count = cur.fetchone()[0]
    print(f"   {label}: {count} active trades")

print()
print("=" * 80)
print("DIAGNOSIS")
print("=" * 80)
print()

if active_last_7_days == 7:
    print("✅ Calendar is showing 'Last 7 days' active trades")
    print(f"   This matches the 7 trades you mentioned")
    print()
    print(f"   But there are actually {active_no_exit} total active trades")
    print(f"   The calendar is filtering out trades older than 7 days")
    print()
    print("   Solution: Remove or extend the date filter in calendar query")
else:
    print(f"⚠️ Calendar shows 7 trades, but query shows {active_last_7_days}")
    print("   Need to check the actual calendar API endpoint")

cur.close()
conn.close()
