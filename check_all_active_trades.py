"""
List all active trades to see what's actually active
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

print("=" * 80)
print("ALL ACTIVE TRADES")
print("=" * 80)
print()

# Get all trades without EXIT
cur.execute("""
    SELECT 
        e.trade_id,
        e.signal_date,
        e.signal_time,
        e.direction,
        e.entry_price,
        e.stop_loss,
        e.session,
        latest_mfe.be_mfe,
        latest_mfe.no_be_mfe,
        latest_mfe.timestamp as last_mfe_update
    FROM automated_signals e
    LEFT JOIN LATERAL (
        SELECT be_mfe, no_be_mfe, timestamp
        FROM automated_signals
        WHERE trade_id = e.trade_id
        AND event_type = 'MFE_UPDATE'
        ORDER BY timestamp DESC
        LIMIT 1
    ) latest_mfe ON true
    WHERE e.event_type = 'ENTRY'
    AND e.trade_id NOT IN (
        SELECT DISTINCT trade_id 
        FROM automated_signals 
        WHERE event_type LIKE 'EXIT_%'
    )
    ORDER BY e.signal_date DESC, e.signal_time DESC
""")

active_trades = cur.fetchall()

print(f"Total active trades (no EXIT event): {len(active_trades)}")
print()

if len(active_trades) > 0:
    print("List of active trades:")
    print()
    for i, trade in enumerate(active_trades, 1):
        print(f"{i}. {trade[0]}")
        print(f"   Date: {trade[1]} {trade[2]}")
        print(f"   Direction: {trade[3]}")
        print(f"   Entry: ${trade[4]}, Stop: ${trade[5]}")
        print(f"   Session: {trade[6]}")
        print(f"   BE MFE: {float(trade[7]) if trade[7] is not None else 'NULL'}")
        print(f"   No-BE MFE: {float(trade[8]) if trade[8] is not None else 'NULL'}")
        print(f"   Last MFE Update: {trade[9] if trade[9] else 'NEVER'}")
        print()

# Check if there are trades with EXIT that might be showing as active
print("=" * 80)
print("CHECKING FOR MISCLASSIFIED TRADES")
print("=" * 80)
print()

# Check if dashboard might be querying differently
cur.execute("""
    SELECT COUNT(DISTINCT trade_id)
    FROM automated_signals
    WHERE event_type = 'ENTRY'
""")

total_entry_events = cur.fetchone()[0]

cur.execute("""
    SELECT COUNT(DISTINCT trade_id)
    FROM automated_signals
    WHERE event_type LIKE 'EXIT_%'
""")

total_exit_events = cur.fetchone()[0]

print(f"Total ENTRY events: {total_entry_events}")
print(f"Total EXIT events: {total_exit_events}")
print(f"Active (ENTRY - EXIT): {total_entry_events - total_exit_events}")
print()

if total_entry_events - total_exit_events != len(active_trades):
    print("⚠️ Mismatch in counting logic!")
else:
    print("✅ Counting logic is consistent")

# Check what the dashboard API returns
print()
print("=" * 80)
print("DASHBOARD API SIMULATION")
print("=" * 80)
print()

# Simulate the dashboard active trades query
cur.execute("""
    SELECT 
        e.trade_id,
        e.entry_price,
        e.stop_loss,
        e.direction,
        e.session,
        e.signal_date,
        e.signal_time
    FROM automated_signals e
    WHERE e.event_type = 'ENTRY'
    AND e.trade_id NOT IN (
        SELECT DISTINCT trade_id FROM automated_signals WHERE event_type LIKE 'EXIT_%'
    )
    ORDER BY e.timestamp DESC
""")

dashboard_active = cur.fetchall()

print(f"Dashboard would show: {len(dashboard_active)} active trades")

cur.close()
conn.close()

print()
print("=" * 80)
print("CONCLUSION")
print("=" * 80)
print()

if len(active_trades) == 7:
    print("✅ There are exactly 7 active trades in the database")
    print()
    print("If you're seeing 'many more' somewhere, possible reasons:")
    print("1. You're looking at 'All Signals' tab (includes pending/cancelled)")
    print("2. You're looking at completed trades")
    print("3. You're counting MFE_UPDATE events (not unique trades)")
    print("4. Frontend is displaying duplicates")
    print("5. You're looking at a different dashboard")
    print()
    print("The calendar is showing the correct count: 7 active trades")
else:
    print(f"⚠️ Database shows {len(active_trades)} active trades")
    print("   But calendar shows 7")
    print("   Need to check calendar query logic")
