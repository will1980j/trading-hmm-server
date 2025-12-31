#!/usr/bin/env python3
"""
Phase C Stage 1: Check Triangle Counts
Verify triangle events in database for a date range
"""

import os, sys, psycopg2
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

if len(sys.argv) < 4:
    print("Usage: python scripts/phase_c_check_triangle_counts.py SYMBOL START_DATE END_DATE")
    print("Example: python scripts/phase_c_check_triangle_counts.py GLBX.MDP3:NQ 2025-12-02 2025-12-02")
    sys.exit(1)

load_dotenv()

symbol = sys.argv[1]
start_date = sys.argv[2]
end_date = sys.argv[3]

# Parse dates
utc_tz = ZoneInfo('UTC')

if 'T' in start_date:
    start_ts = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
else:
    start_ts = datetime.fromisoformat(start_date).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=utc_tz)

if 'T' in end_date:
    end_ts = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
else:
    end_ts = datetime.fromisoformat(end_date).replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=utc_tz)

database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("ERROR: DATABASE_URL not set")
    sys.exit(1)

conn = psycopg2.connect(database_url)
cursor = conn.cursor()

# Get counts
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(*) FILTER (WHERE direction = 'BULL') as bull_count,
        COUNT(*) FILTER (WHERE direction = 'BEAR') as bear_count,
        MIN(ts) as min_ts,
        MAX(ts) as max_ts
    FROM triangle_events_v1
    WHERE symbol = %s AND ts >= %s AND ts <= %s
""", (symbol, start_ts, end_ts))

result = cursor.fetchone()
cursor.close()
conn.close()

print(f"Triangle Events for {symbol}")
print(f"Date range: {start_date} to {end_date}")
print("-" * 80)

if result and result[0] > 0:
    print(f"Total rows: {result[0]}")
    print(f"Bull count: {result[1]}")
    print(f"Bear count: {result[2]}")
    print(f"First triangle: {result[3].isoformat() if result[3] else 'N/A'}")
    print(f"Last triangle: {result[4].isoformat() if result[4] else 'N/A'}")
else:
    print("No triangle events found")

print("-" * 80)
