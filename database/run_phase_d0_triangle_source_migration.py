#!/usr/bin/env python3
"""
Run Phase D.0 Triangle Source Tracking Migration
Adds source_table and logic_version columns to triangle_events_v1
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set")
    exit(1)

print("Connecting to database...")
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

print("Reading schema file...")
with open('database/phase_d0_triangle_source_tracking.sql', 'r') as f:
    schema_sql = f.read()

print("Executing migration...")
cursor.execute(schema_sql)
conn.commit()

print("Verifying columns added...")
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'triangle_events_v1' 
    AND column_name IN ('source_table', 'logic_version')
    ORDER BY column_name
""")

columns = cursor.fetchall()
if len(columns) == 2:
    print("✅ Columns added successfully:")
    for col in columns:
        print(f"     {col[0]}: {col[1]}")
else:
    print(f"❌ Column addition failed (found {len(columns)}/2 columns)")

cursor.close()
conn.close()

print("\nMigration complete")
