#!/usr/bin/env python3
"""
Run Signal Contract V1 Wave 1 Migration
Extends automated_signals table with timestamp semantics, signal candle, breakeven, and extremes fields
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set")
    exit(1)

print("Signal Contract V1 - Wave 1 Migration")
print("=" * 80)
print("Connecting to database...")
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

print("Reading migration file...")
with open('database/signal_contract_v1_wave1_migration.sql', 'r') as f:
    migration_sql = f.read()

print("Executing migration...")
cursor.execute(migration_sql)
conn.commit()

print("\nVerifying columns added...")
cursor.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'automated_signals' 
    AND column_name IN (
        'symbol', 'logic_version', 'source', 'status',
        'signal_bar_open_ts', 'signal_bar_close_ts',
        'confirmation_bar_open_ts', 'confirmation_bar_close_ts',
        'entry_bar_open_ts', 'entry_bar_close_ts',
        'exit_bar_open_ts', 'exit_bar_close_ts',
        'signal_candle_high', 'signal_candle_low',
        'be_enabled', 'be_trigger_R', 'be_offset_points', 'be_triggered',
        'be_trigger_bar_open_ts', 'be_trigger_bar_close_ts',
        'highest_high', 'lowest_low', 'extremes_last_updated_bar_open_ts'
    )
    ORDER BY column_name
""")

columns = cursor.fetchall()
print(f"\n✅ Added {len(columns)} columns:")
for col in columns:
    nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
    print(f"   {col[0]:<35} {col[1]:<20} {nullable}")

print("\nVerifying indexes...")
cursor.execute("""
    SELECT indexname 
    FROM pg_indexes 
    WHERE tablename = 'automated_signals'
    AND indexname LIKE '%signal_bar%' OR indexname LIKE '%entry_bar%' OR indexname LIKE '%exit_bar%'
    OR indexname LIKE '%status%' OR indexname LIKE '%symbol%'
    ORDER BY indexname
""")

indexes = cursor.fetchall()
print(f"\n✅ Indexes created: {len(indexes)}")
for idx in indexes:
    print(f"   {idx[0]}")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("✅ Wave 1 migration complete")
print("\nNext steps:")
print("1. Update webhook handlers to populate new columns")
print("2. Test with live events")
print("3. Verify via debug endpoints")
