#!/usr/bin/env python3
"""
Signal Contract V1 Wave 1 - One-Time Backfill
Populates Wave 1 fields for existing rows in automated_signals
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv
import argparse
import time

load_dotenv()

parser = argparse.ArgumentParser(description='Backfill Signal Contract V1 Wave 1 fields')
parser.add_argument('--limit', type=int, default=10000, help='Max rows to backfill (default: 10000)')
parser.add_argument('--dry-run', action='store_true', help='Show what would be updated without committing')
parser.add_argument('--since-id', type=int, help='Only backfill rows with id >= this value')
args = parser.parse_args()

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set")
    sys.exit(1)

print("Signal Contract V1 Wave 1 - Backfill")
print("=" * 80)
print(f"Limit: {args.limit}")
print(f"Dry run: {args.dry_run}")
if args.since_id:
    print(f"Since ID: {args.since_id}")
print("=" * 80)

start_time = time.time()

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Build WHERE clause
where_clause = "WHERE symbol IS NULL OR status IS NULL"
if args.since_id:
    where_clause += f" AND id >= {args.since_id}"

# Count rows to update
print("\nCounting rows to update...")
cursor.execute(f"""
    SELECT COUNT(*) FROM (
        SELECT id FROM automated_signals
        {where_clause}
        ORDER BY id DESC
        LIMIT {args.limit}
    ) t
""")
rows_to_update = cursor.fetchone()[0]
print(f"Rows to update: {rows_to_update}")

if rows_to_update == 0:
    print("No rows need updating")
    cursor.close()
    conn.close()
    sys.exit(0)

if args.dry_run:
    print("\n[DRY RUN] Would update the following:")
    cursor.execute(f"""
        SELECT id, trade_id, event_type, direction, symbol, status
        FROM automated_signals
        {where_clause}
        ORDER BY id DESC
        LIMIT 20
    """)
    for row in cursor.fetchall():
        print(f"  ID {row[0]}: {row[1]} {row[2]} direction={row[3]} symbol={row[4]} status={row[5]}")
    cursor.close()
    conn.close()
    sys.exit(0)

print("\nExecuting backfill...")

# Update in single transaction with CTEs
update_sql = f"""
WITH target_rows AS (
    SELECT id
    FROM automated_signals
    ORDER BY id DESC
    LIMIT {args.limit}
),
rows_with_data AS (
    SELECT 
        a.id,
        a.trade_id,
        a.event_type,
        a.direction,
        a.timestamp,
        a.confirmation_time
    FROM automated_signals a
    INNER JOIN target_rows t ON a.id = t.id
),
direction_inferred AS (
    SELECT 
        id,
        trade_id,
        event_type,
        COALESCE(
            direction,
            CASE 
                WHEN trade_id LIKE '%_BULLISH%' THEN 'Bullish'
                WHEN trade_id LIKE '%_BEARISH%' THEN 'Bearish'
                ELSE NULL
            END
        ) AS normalized_direction,
        timestamp,
        confirmation_time
    FROM rows_with_data
),
direction_carried AS (
    SELECT 
        id,
        trade_id,
        event_type,
        COALESCE(
            normalized_direction,
            FIRST_VALUE(normalized_direction) OVER (PARTITION BY trade_id ORDER BY id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
        ) AS final_direction,
        timestamp,
        confirmation_time
    FROM direction_inferred
),
be_triggered_flags AS (
    SELECT 
        trade_id,
        MIN(id) AS first_be_id
    FROM rows_with_data
    WHERE event_type = 'BE_TRIGGERED'
    GROUP BY trade_id
)
UPDATE automated_signals a
SET
    symbol = COALESCE(a.symbol, 'GLBX.MDP3:NQ'),
    status = CASE 
        WHEN a.status IS NOT NULL THEN a.status
        WHEN a.event_type = 'SIGNAL_CREATED' THEN 'PENDING'
        WHEN a.event_type = 'ENTRY' THEN 'CONFIRMED'
        WHEN a.event_type IN ('EXIT_SL', 'EXIT_BE', 'EXIT_TP') THEN 'EXITED'
        WHEN a.event_type = 'CANCELLED' THEN 'CANCELLED'
        WHEN a.event_type IN ('MFE_UPDATE', 'BE_TRIGGERED') THEN 'ACTIVE'
        ELSE NULL
    END,
    direction = COALESCE(a.direction, dc.final_direction),
    signal_bar_open_ts = CASE 
        WHEN a.signal_bar_open_ts IS NULL AND a.event_type = 'SIGNAL_CREATED' 
        THEN date_trunc('minute', a.timestamp AT TIME ZONE 'UTC')
        ELSE a.signal_bar_open_ts
    END,
    signal_bar_close_ts = CASE 
        WHEN a.signal_bar_close_ts IS NULL AND a.event_type = 'SIGNAL_CREATED' 
        THEN date_trunc('minute', a.timestamp AT TIME ZONE 'UTC') + interval '1 minute'
        ELSE a.signal_bar_close_ts
    END,
    entry_bar_open_ts = CASE 
        WHEN a.entry_bar_open_ts IS NULL AND a.event_type = 'ENTRY' 
        THEN date_trunc('minute', a.timestamp AT TIME ZONE 'UTC')
        ELSE a.entry_bar_open_ts
    END,
    entry_bar_close_ts = CASE 
        WHEN a.entry_bar_close_ts IS NULL AND a.event_type = 'ENTRY' 
        THEN date_trunc('minute', a.timestamp AT TIME ZONE 'UTC') + interval '1 minute'
        ELSE a.entry_bar_close_ts
    END,
    confirmation_bar_open_ts = CASE 
        WHEN a.confirmation_bar_open_ts IS NULL AND a.confirmation_time IS NOT NULL 
        THEN date_trunc('minute', a.confirmation_time AT TIME ZONE 'UTC')
        ELSE a.confirmation_bar_open_ts
    END,
    confirmation_bar_close_ts = CASE 
        WHEN a.confirmation_bar_close_ts IS NULL AND a.confirmation_time IS NOT NULL 
        THEN date_trunc('minute', a.confirmation_time AT TIME ZONE 'UTC') + interval '1 minute'
        ELSE a.confirmation_bar_close_ts
    END,
    exit_bar_open_ts = CASE 
        WHEN a.exit_bar_open_ts IS NULL AND a.event_type IN ('EXIT_SL', 'EXIT_BE', 'EXIT_TP') 
        THEN date_trunc('minute', a.timestamp AT TIME ZONE 'UTC')
        ELSE a.exit_bar_open_ts
    END,
    exit_bar_close_ts = CASE 
        WHEN a.exit_bar_close_ts IS NULL AND a.event_type IN ('EXIT_SL', 'EXIT_BE', 'EXIT_TP') 
        THEN date_trunc('minute', a.timestamp AT TIME ZONE 'UTC') + interval '1 minute'
        ELSE a.exit_bar_close_ts
    END,
    be_enabled = COALESCE(a.be_enabled, true),
    be_trigger_R = COALESCE(a.be_trigger_R, 1.0),
    be_offset_points = COALESCE(a.be_offset_points, 0.0),
    be_triggered = CASE 
        WHEN a.be_triggered IS NOT NULL THEN a.be_triggered
        WHEN a.event_type = 'BE_TRIGGERED' THEN true
        WHEN btf.first_be_id IS NOT NULL AND a.id >= btf.first_be_id THEN true
        ELSE false
    END,
    be_trigger_bar_open_ts = CASE 
        WHEN a.be_trigger_bar_open_ts IS NULL AND a.event_type = 'BE_TRIGGERED' 
        THEN date_trunc('minute', a.timestamp AT TIME ZONE 'UTC')
        ELSE a.be_trigger_bar_open_ts
    END,
    be_trigger_bar_close_ts = CASE 
        WHEN a.be_trigger_bar_close_ts IS NULL AND a.event_type = 'BE_TRIGGERED' 
        THEN date_trunc('minute', a.timestamp AT TIME ZONE 'UTC') + interval '1 minute'
        ELSE a.be_trigger_bar_close_ts
    END
FROM direction_carried dc
LEFT JOIN be_triggered_flags btf ON dc.trade_id = btf.trade_id
WHERE a.id = dc.id
"""

cursor.execute(update_sql)
rows_updated = cursor.rowcount

if not args.dry_run:
    conn.commit()
    print(f"\n✅ Updated {rows_updated} rows")
else:
    conn.rollback()
    print(f"\n[DRY RUN] Would update {rows_updated} rows")

# Print statistics
print("\nField population statistics:")
cursor.execute(f"""
    SELECT 
        COUNT(*) FILTER (WHERE symbol IS NOT NULL) AS symbol_populated,
        COUNT(*) FILTER (WHERE status IS NOT NULL) AS status_populated,
        COUNT(*) FILTER (WHERE signal_bar_open_ts IS NOT NULL) AS signal_ts_populated,
        COUNT(*) FILTER (WHERE entry_bar_open_ts IS NOT NULL) AS entry_ts_populated,
        COUNT(*) FILTER (WHERE exit_bar_open_ts IS NOT NULL) AS exit_ts_populated,
        COUNT(*) FILTER (WHERE be_enabled IS NOT NULL) AS be_enabled_populated,
        COUNT(*) FILTER (WHERE be_triggered = true) AS be_triggered_count,
        COUNT(*) AS total_rows
    FROM (
        SELECT * FROM automated_signals
        ORDER BY id DESC
        LIMIT {args.limit}
    ) t
""")

stats = cursor.fetchone()
print(f"  symbol:           {stats[0]}/{stats[7]} ({100*stats[0]/stats[7]:.1f}%)")
print(f"  status:           {stats[1]}/{stats[7]} ({100*stats[1]/stats[7]:.1f}%)")
print(f"  signal_bar_open:  {stats[2]}/{stats[7]} ({100*stats[2]/stats[7]:.1f}%)")
print(f"  entry_bar_open:   {stats[3]}/{stats[7]} ({100*stats[3]/stats[7]:.1f}%)")
print(f"  exit_bar_open:    {stats[4]}/{stats[7]} ({100*stats[4]/stats[7]:.1f}%)")
print(f"  be_enabled:       {stats[5]}/{stats[7]} ({100*stats[5]/stats[7]:.1f}%)")
print(f"  be_triggered:     {stats[6]} rows")

duration = time.time() - start_time
print(f"\nDuration: {duration:.2f} seconds")

cursor.close()
conn.close()

print("=" * 80)
print("✅ Backfill complete")
print("\nVerify with:")
print("  curl http://localhost:5000/api/signals/v1/debug/last?limit=5")
