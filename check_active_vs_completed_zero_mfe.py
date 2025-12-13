"""
Check if 0.00 MFE trades are active or completed
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

print("=" * 80)
print("ACTIVE VS COMPLETED TRADES WITH 0.00 MFE")
print("=" * 80)
print()

# Get trades with 0.00 or NULL MFE
cur.execute("""
    SELECT 
        e.trade_id,
        e.entry_price,
        e.stop_loss,
        e.direction,
        e.signal_date,
        latest_mfe.be_mfe,
        latest_mfe.no_be_mfe,
        EXISTS(
            SELECT 1 FROM automated_signals ex
            WHERE ex.trade_id = e.trade_id
            AND ex.event_type LIKE 'EXIT_%'
        ) as has_exit
    FROM automated_signals e
    LEFT JOIN LATERAL (
        SELECT be_mfe, no_be_mfe
        FROM automated_signals
        WHERE trade_id = e.trade_id
        AND event_type = 'MFE_UPDATE'
        ORDER BY timestamp DESC
        LIMIT 1
    ) latest_mfe ON true
    WHERE e.event_type = 'ENTRY'
    AND (latest_mfe.be_mfe = 0.0 OR latest_mfe.no_be_mfe = 0.0 OR latest_mfe.be_mfe IS NULL)
    ORDER BY e.timestamp DESC
""")

trades = cur.fetchall()

active_trades = [t for t in trades if not t[7]]
completed_trades = [t for t in trades if t[7]]

print(f"Total trades with 0.00/NULL MFE: {len(trades)}")
print(f"   Active (no EXIT): {len(active_trades)}")
print(f"   Completed (has EXIT): {len(completed_trades)}")
print()

if active_trades:
    print("ACTIVE TRADES (Should have MFE updates):")
    for trade in active_trades[:5]:
        print(f"   {trade[0]}")
        print(f"      Entry: ${trade[1]}, Stop: ${trade[2]}")
        print(f"      Date: {trade[4]}")
        print(f"      BE MFE: {float(trade[5]) if trade[5] is not None else 'NULL'}")
        print(f"      Status: ACTIVE (no EXIT event)")
        print()

if completed_trades:
    print("COMPLETED TRADES (Should have final MFE from EXIT):")
    for trade in completed_trades[:5]:
        print(f"   {trade[0]}")
        print(f"      Entry: ${trade[1]}, Stop: ${trade[2]}")
        print(f"      Date: {trade[4]}")
        print(f"      BE MFE: {float(trade[5]) if trade[5] is not None else 'NULL'}")
        print(f"      Status: COMPLETED (has EXIT event)")
        print()

# Check if completed trades have MFE in EXIT event
if completed_trades:
    print("Checking EXIT events for MFE values...")
    
    for trade in completed_trades[:3]:
        cur.execute("""
            SELECT event_type, be_mfe, no_be_mfe, exit_price
            FROM automated_signals
            WHERE trade_id = %s
            AND event_type LIKE 'EXIT_%'
        """, (trade[0],))
        
        exit_event = cur.fetchone()
        if exit_event:
            print(f"\n   {trade[0]}:")
            print(f"      EXIT event: {exit_event[0]}")
            print(f"      EXIT BE MFE: {float(exit_event[1]) if exit_event[1] is not None else 'NULL'}")
            print(f"      EXIT No-BE MFE: {float(exit_event[2]) if exit_event[2] is not None else 'NULL'}")
            print(f"      Exit Price: ${exit_event[3] if exit_event[3] else 'NULL'}")

cur.close()
conn.close()

print()
print("=" * 80)
print("DIAGNOSIS")
print("=" * 80)
print()

if len(active_trades) > 0:
    print(f"⚠️ {len(active_trades)} ACTIVE trades have no MFE updates")
    print("   Possible causes:")
    print("   1. Indicator stopped tracking them (restart)")
    print("   2. MFE_UPDATE webhooks not being sent")
    print("   3. Batch system not including them")
    print()
    print("   Solution: Hybrid Sync should fill these with calculated MFE")

if len(completed_trades) > 0:
    print(f"⚠️ {len(completed_trades)} COMPLETED trades showing 0.00 MFE")
    print("   Possible causes:")
    print("   1. EXIT event has 0.00 MFE (indicator issue)")
    print("   2. Dashboard querying MFE_UPDATE instead of EXIT")
    print("   3. No MFE_UPDATE events before EXIT")
    print()
    print("   Solution: Dashboard should use EXIT event MFE for completed trades")
