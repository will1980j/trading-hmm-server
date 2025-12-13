"""
Check if trades are being counted correctly for dual strategy (BE=1 and No-BE)
A trade is ACTIVE if either strategy is still running
A trade is COMPLETE only when BOTH strategies have exited
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

print("=" * 80)
print("DUAL STRATEGY STATUS CHECK")
print("=" * 80)
print()

# Check trades with EXIT_BE (BE strategy stopped, but No-BE might still be running)
print("1. Trades with EXIT_BE (BE stopped, No-BE might still be active):")
cur.execute("""
    SELECT 
        e.trade_id,
        e.entry_price,
        e.stop_loss,
        e.direction,
        EXISTS(SELECT 1 FROM automated_signals WHERE trade_id = e.trade_id AND event_type = 'EXIT_BE') as has_exit_be,
        EXISTS(SELECT 1 FROM automated_signals WHERE trade_id = e.trade_id AND event_type = 'EXIT_SL') as has_exit_sl
    FROM automated_signals e
    WHERE e.event_type = 'ENTRY'
    ORDER BY e.timestamp DESC
    LIMIT 20
""")

trades = cur.fetchall()

active_be_only = []  # BE exited, No-BE still active
active_both = []     # Both still active
complete_both = []   # Both exited

for trade in trades:
    trade_id = trade[0]
    has_exit_be = trade[4]
    has_exit_sl = trade[5]
    
    if has_exit_be and has_exit_sl:
        complete_both.append(trade_id)  # Both exited
    elif has_exit_be and not has_exit_sl:
        active_be_only.append(trade_id)  # BE exited, No-BE still active
    elif not has_exit_be and not has_exit_sl:
        active_both.append(trade_id)  # Both still active

print(f"   Trades where BE exited but No-BE still active: {len(active_be_only)}")
print(f"   Trades where both strategies still active: {len(active_both)}")
print(f"   Trades where both strategies exited: {len(complete_both)}")
print()

if active_be_only:
    print("   Trades with BE exited but No-BE active:")
    for trade_id in active_be_only[:5]:
        print(f"      {trade_id}")

print()
print("=" * 80)
print("CURRENT QUERY LOGIC")
print("=" * 80)
print()

# Current query: Excludes ANY trade with ANY EXIT event
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

current_count = cur.fetchone()[0]
print(f"Current query counts: {current_count} active trades")
print("   Logic: Excludes trades with ANY EXIT event")
print()

# Correct query: Only exclude trades with BOTH EXIT events
cur.execute("""
    SELECT COUNT(DISTINCT e.trade_id)
    FROM automated_signals e
    WHERE e.event_type = 'ENTRY'
    AND e.trade_id NOT IN (
        -- Only exclude if BOTH strategies have exited
        SELECT trade_id
        FROM automated_signals
        WHERE event_type = 'EXIT_SL'
        -- EXIT_SL means No-BE strategy stopped (original stop hit)
        -- This is the final exit for both strategies
    )
""")

correct_count = cur.fetchone()[0]
print(f"Correct query should count: {correct_count} active trades")
print("   Logic: Only excludes trades with EXIT_SL (both strategies stopped)")
print()

print("=" * 80)
print("EXPLANATION")
print("=" * 80)
print()
print("Dual Strategy Exit Logic:")
print()
print("EXIT_BE:")
print("   - BE=1 strategy stops at entry (break even)")
print("   - No-BE strategy CONTINUES tracking")
print("   - Trade is still ACTIVE (No-BE running)")
print()
print("EXIT_SL:")
print("   - Original stop loss hit")
print("   - BOTH strategies stop")
print("   - Trade is COMPLETE")
print()
print("Therefore:")
print("   Active = No EXIT_SL (regardless of EXIT_BE)")
print("   Complete = Has EXIT_SL")

cur.close()
conn.close()

print()
print("=" * 80)
print("RECOMMENDATION")
print("=" * 80)
print()
print("Change active trades query from:")
print("   WHERE trade_id NOT IN (SELECT ... WHERE event_type LIKE 'EXIT_%')")
print()
print("To:")
print("   WHERE trade_id NOT IN (SELECT ... WHERE event_type = 'EXIT_SL')")
print()
print("This will correctly show trades where No-BE strategy is still active")
print("even if BE strategy has exited.")
