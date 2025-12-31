#!/usr/bin/env python3
"""
Phase E: Verify Bias Series Window
Display HTF bias timeline for a specific time window
"""

import os, sys, psycopg2
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

if len(sys.argv) < 4:
    print("Usage: python scripts/phase_e_verify_bias_series_window.py SYMBOL START_TS END_TS")
    print("Example: python scripts/phase_e_verify_bias_series_window.py GLBX.MDP3:NQ 2025-12-02T00:10:00Z 2025-12-02T00:30:00Z")
    sys.exit(1)

load_dotenv()

symbol = sys.argv[1]
start_ts_str = sys.argv[2]
end_ts_str = sys.argv[3]

# Parse timestamps
start_ts = datetime.fromisoformat(start_ts_str.replace('Z', '+00:00'))
end_ts = datetime.fromisoformat(end_ts_str.replace('Z', '+00:00'))

# Connect to database
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("ERROR: DATABASE_URL not set")
    sys.exit(1)

conn = psycopg2.connect(database_url)
cursor = conn.cursor()

# Query bias series
cursor.execute("""
    SELECT ts, bias_1m, bias_5m, bias_15m, bias_1h, bias_4h, bias_1d
    FROM bias_series_1m_v1
    WHERE symbol = %s AND ts >= %s AND ts <= %s
    ORDER BY ts ASC
""", (symbol, start_ts, end_ts))

rows = cursor.fetchall()

print(f"Bias Series Window: {symbol}")
print(f"Range: {start_ts} to {end_ts}")
print("-" * 100)
print(f"{'TS (UTC)':<20} {'1m':<10} {'5m':<10} {'15m':<10} {'1h':<10} {'4h':<10} {'1d':<10}")
print("-" * 100)

for row in rows:
    print(f"{row[0].isoformat():<20} {row[1]:<10} {row[2]:<10} {row[3]:<10} {row[4]:<10} {row[5]:<10} {row[6]:<10}")

print("-" * 100)
print(f"Rows found: {len(rows)}")
if rows:
    print(f"Min ts: {rows[0][0]}")
    print(f"Max ts: {rows[-1][0]}")

cursor.close()
conn.close()
