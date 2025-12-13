"""
Check for trades with 0.00 MFE values and NULL entry/SL
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

print("=" * 80)
print("CHECKING FOR 0.00 MFE AND NULL ENTRY/SL VALUES")
print("=" * 80)
print()

# Check 1: Trades with 0.00 MFE values
print("1. TRADES WITH 0.00 MFE VALUES:")
cur.execute("""
    SELECT 
        e.trade_id,
        e.entry_price,
        e.stop_loss,
        e.direction,
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
    AND (latest_mfe.be_mfe = 0.0 OR latest_mfe.no_be_mfe = 0.0 OR latest_mfe.be_mfe IS NULL)
    ORDER BY e.timestamp DESC
    LIMIT 10
""")

zero_mfe_trades = cur.fetchall()

if zero_mfe_trades:
    print(f"   Found {len(zero_mfe_trades)} trades with 0.00 or NULL MFE:")
    for trade in zero_mfe_trades:
        print(f"\n   Trade: {trade[0]}")
        print(f"      Entry: ${trade[1] if trade[1] else 'NULL'}")
        print(f"      Stop: ${trade[2] if trade[2] else 'NULL'}")
        print(f"      Direction: {trade[3]}")
        print(f"      BE MFE: {float(trade[4]) if trade[4] is not None else 'NULL'}")
        print(f"      No-BE MFE: {float(trade[5]) if trade[5] is not None else 'NULL'}")
        print(f"      Last MFE Update: {trade[6] if trade[6] else 'NEVER'}")
else:
    print("   ✅ No trades with 0.00 MFE found")

print()
print("=" * 80)

# Check 2: Trades with NULL entry_price or stop_loss
print("2. TRADES WITH NULL ENTRY OR STOP LOSS:")
cur.execute("""
    SELECT 
        trade_id,
        entry_price,
        stop_loss,
        direction,
        session,
        timestamp
    FROM automated_signals
    WHERE event_type = 'ENTRY'
    AND (entry_price IS NULL OR stop_loss IS NULL)
    ORDER BY timestamp DESC
""")

null_trades = cur.fetchall()

if null_trades:
    print(f"   Found {len(null_trades)} trades with NULL entry/SL:")
    for trade in null_trades:
        print(f"\n   Trade: {trade[0]}")
        print(f"      Entry: {trade[1] if trade[1] else 'NULL'}")
        print(f"      Stop: {trade[2] if trade[2] else 'NULL'}")
        print(f"      Direction: {trade[3]}")
        print(f"      Session: {trade[4]}")
        print(f"      Timestamp: {trade[5]}")
else:
    print("   ✅ No trades with NULL entry/SL found")

print()
print("=" * 80)

# Check 3: Check if these are test signals or real signals
print("3. IDENTIFYING TEST VS REAL SIGNALS:")
cur.execute("""
    SELECT 
        trade_id,
        entry_price,
        stop_loss,
        signal_date,
        CASE 
            WHEN trade_id LIKE '%TEST%' THEN 'TEST'
            WHEN signal_date >= '2025-12-13' THEN 'TEST (Weekend)'
            ELSE 'REAL'
        END as signal_type
    FROM automated_signals
    WHERE event_type = 'ENTRY'
    AND (entry_price IS NULL OR stop_loss IS NULL OR 
         trade_id IN (
             SELECT e.trade_id FROM automated_signals e
             LEFT JOIN LATERAL (
                 SELECT be_mfe FROM automated_signals
                 WHERE trade_id = e.trade_id AND event_type = 'MFE_UPDATE'
                 ORDER BY timestamp DESC LIMIT 1
             ) m ON true
             WHERE e.event_type = 'ENTRY'
             AND (m.be_mfe = 0.0 OR m.be_mfe IS NULL)
         ))
    ORDER BY timestamp DESC
""")

signals = cur.fetchall()

test_count = sum(1 for s in signals if s[4] in ['TEST', 'TEST (Weekend)'])
real_count = sum(1 for s in signals if s[4] == 'REAL')

print(f"   Test signals with issues: {test_count}")
print(f"   Real signals with issues: {real_count}")

if real_count > 0:
    print(f"\n   Real signals with issues:")
    for signal in signals:
        if signal[4] == 'REAL':
            print(f"      {signal[0]} | Entry: {signal[1]} | Stop: {signal[2]} | Date: {signal[3]}")

cur.close()
conn.close()

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()
print("Issues found:")
print(f"   - Trades with 0.00 MFE: {len(zero_mfe_trades)}")
print(f"   - Trades with NULL entry/SL: {len(null_trades)}")
print(f"   - Test signals: {test_count}")
print(f"   - Real signals: {real_count}")
print()

if real_count > 0:
    print("⚠️ REAL signals have data issues - needs investigation")
elif test_count > 0:
    print("ℹ️ Only TEST signals have issues - this is expected")
    print("   Real signals from Monday will have complete data")
else:
    print("✅ No data issues found")
