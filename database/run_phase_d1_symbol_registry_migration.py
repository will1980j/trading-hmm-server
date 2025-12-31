#!/usr/bin/env python3
"""
Run Phase D.1 Symbol Registry Generalization Migration
Adds optional metadata columns for diverse asset class support
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
with open('database/phase_d1_symbol_registry_generalization.sql', 'r') as f:
    schema_sql = f.read()

print("Executing migration...")
cursor.execute(schema_sql)
conn.commit()

print("Verifying columns added...")
cursor.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'symbol_registry' 
    AND column_name IN ('vendor_dataset', 'schema_name', 'venue', 'asset_class', 'timezone', 'session_profile')
    ORDER BY column_name
""")

columns = cursor.fetchall()
if len(columns) == 6:
    print("✅ Columns added successfully:")
    for col in columns:
        nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
        print(f"     {col[0]:<20} {col[1]:<15} {nullable}")
else:
    print(f"❌ Column addition failed (found {len(columns)}/6 columns)")

print("\nVerifying existing symbols updated...")
cursor.execute("""
    SELECT internal_symbol, vendor_dataset, schema_name, venue, asset_class, timezone
    FROM symbol_registry
    ORDER BY internal_symbol
""")

print("\n   Registered symbols with metadata:")
for row in cursor.fetchall():
    print(f"     {row[0]:<20} dataset={row[1]:<12} venue={row[3] or 'NULL':<6} class={row[4] or 'NULL'}")

cursor.close()
conn.close()

print("\nMigration complete")
