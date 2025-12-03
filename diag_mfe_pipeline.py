"""
Comprehensive MFE Pipeline Diagnostics
Traces MFE values through entire system to find failure point
"""
from dotenv import load_dotenv
load_dotenv()

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import json

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

BASE_URL = "https://web-production-f8c3.up.railway.app"

print("=" * 80)
print("MFE PIPELINE DIAGNOSTICS")
print("=" * 80)

# 1. Query last 20 MFE_UPDATE rows
print("\n1. LAST 20 MFE_UPDATE ROWS IN DATABASE:")
print("-" * 80)

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor(cursor_factory=RealDictCursor)

cursor.execute("""
    SELECT trade_id, be_mfe, no_be_mfe, current_price, timestamp
    FROM automated_signals
    WHERE event_type = 'MFE_UPDATE'
    ORDER BY timestamp DESC
    LIMIT 20
""")

mfe_rows = cursor.fetchall()
trade_ids = set()

for row in mfe_rows:
    trade_ids.add(row['trade_id'])
    print(f"{row['timestamp']} | {row['trade_id'][:30]}...")
    print(f"  BE MFE: {row['be_mfe']}, No BE MFE: {row['no_be_mfe']}, Price: {row['current_price']}")

# 2. Event progression for each trade
print("\n2. EVENT PROGRESSION BY TRADE:")
print("-" * 80)

for trade_id in list(trade_ids)[:5]:  # Limit to 5 trades
    print(f"\nTrade: {trade_id}")
    cursor.execute("""
        SELECT event_type, be_mfe, no_be_mfe, timestamp
        FROM automated_signals
        WHERE trade_id = %s
        ORDER BY timestamp ASC
    """, (trade_id,))
    
    events = cursor.fetchall()
    for event in events:
        print(f"  {event['timestamp']} | {event['event_type']:15} | BE={event['be_mfe']}, No BE={event['no_be_mfe']}")

# 3. Validate normalization (check telemetry log)
print("\n3. NORMALIZATION VALIDATION:")
print("-" * 80)

try:
    cursor.execute("""
        SELECT raw_payload, fused_event
        FROM telemetry_automated_signals_log
        WHERE fused_event->>'event_type' = 'MFE_UPDATE'
        ORDER BY received_at DESC
        LIMIT 5
    """)
    
    telemetry_rows = cursor.fetchall()
    for i, row in enumerate(telemetry_rows, 1):
        raw = row['raw_payload']
        fused = row['fused_event']
        print(f"\nEvent {i}:")
        print(f"  Raw mfe_R: {raw.get('mfe_R')}")
        print(f"  Raw mae_R: {raw.get('mae_R')}")
        print(f"  Fused mfe_R: {fused.get('mfe_R')}")
        print(f"  Fused mae_R: {fused.get('mae_R')}")
except Exception as e:
    print(f"  Telemetry log check failed: {e}")

# 4. Dashboard query validation
print("\n4. DASHBOARD QUERY VALIDATION:")
print("-" * 80)

cursor.execute("""
    WITH latest_mfe AS (
        SELECT
            trade_id,
            MAX(timestamp) FILTER (WHERE event_type = 'MFE_UPDATE') AS last_mfe_ts,
            MAX(be_mfe) FILTER (WHERE event_type = 'MFE_UPDATE') AS latest_be_mfe,
            MAX(no_be_mfe) FILTER (WHERE event_type = 'MFE_UPDATE') AS latest_no_be_mfe,
            MAX(current_price) FILTER (WHERE event_type = 'MFE_UPDATE') AS latest_current_price
        FROM automated_signals
        GROUP BY trade_id
    )
    SELECT 
        e.trade_id,
        e.be_mfe as entry_be_mfe,
        e.no_be_mfe as entry_no_be_mfe,
        COALESCE(m.latest_be_mfe, e.be_mfe, 0.0) AS dashboard_be_mfe,
        COALESCE(m.latest_no_be_mfe, e.no_be_mfe, 0.0) AS dashboard_no_be_mfe,
        m.latest_current_price
    FROM automated_signals e
    LEFT JOIN latest_mfe m ON m.trade_id = e.trade_id
    WHERE e.event_type = 'ENTRY'
    AND NOT EXISTS (
        SELECT 1 FROM automated_signals ex
        WHERE ex.trade_id = e.trade_id
        AND ex.event_type LIKE 'EXIT_%'
    )
    ORDER BY e.timestamp DESC
    LIMIT 10
""")

dashboard_rows = cursor.fetchall()
print("Dashboard sees these MFE values:")
for row in dashboard_rows:
    print(f"\n{row['trade_id'][:30]}...")
    print(f"  ENTRY row: BE={row['entry_be_mfe']}, No BE={row['entry_no_be_mfe']}")
    print(f"  Dashboard: BE={row['dashboard_be_mfe']}, No BE={row['dashboard_no_be_mfe']}")
    print(f"  Current Price: {row['latest_current_price']}")

cursor.close()
conn.close()

# 5. API endpoint check
print("\n5. API ENDPOINT CHECK:")
print("-" * 80)

r = requests.get(f"{BASE_URL}/api/automated-signals/dashboard-data")
api_data = r.json()

if api_data.get('active_trades'):
    print(f"API returns {len(api_data['active_trades'])} active trades")
    for trade in api_data['active_trades'][:3]:
        print(f"\n{trade['trade_id'][:30]}...")
        print(f"  BE MFE: {trade.get('be_mfe')}")
        print(f"  No BE MFE: {trade.get('no_be_mfe')}")

# 6. Final verdict
print("\n" + "=" * 80)
print("FINAL VERDICT:")
print("=" * 80)

# Check each stage
has_mfe_updates = len(mfe_rows) > 0
mfe_values_nonzero = any(row['be_mfe'] != 0 or row['no_be_mfe'] != 0 for row in mfe_rows)
dashboard_query_works = any(row['dashboard_be_mfe'] != 0 or row['dashboard_no_be_mfe'] != 0 for row in dashboard_rows)
api_returns_nonzero = any(t.get('be_mfe', 0) != 0 or t.get('no_be_mfe', 0) != 0 for t in api_data.get('active_trades', []))

if not has_mfe_updates:
    print("❌ FAILURE LOCATION: MFE_UPDATE webhooks not being stored")
elif not mfe_values_nonzero:
    print("❌ FAILURE LOCATION: DB Update Handler (storing 0.0 values)")
elif not dashboard_query_works:
    print("❌ FAILURE LOCATION: Dashboard Query (CTE not aggregating)")
elif not api_returns_nonzero:
    print("❌ FAILURE LOCATION: API Endpoint (not using dashboard query)")
else:
    print("✅ BACKEND WORKING - Issue is frontend caching/display")
    print("   API returns correct values but dashboard shows 0.00R")
    print("   Solution: Hard refresh browser or deploy cache-busting fix")

print("=" * 80)
