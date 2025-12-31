#!/usr/bin/env python3
"""
Run Phase D.0 Symbol Registry Migration
Creates symbol_registry table for multi-symbol support
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
with open('database/phase_d0_symbol_registry_schema.sql', 'r') as f:
    schema_sql = f.read()

print("Executing migration...")
cursor.execute(schema_sql)
conn.commit()

print("Verifying table creation...")
cursor.execute("""
    SELECT COUNT(*) FROM information_schema.tables 
    WHERE table_name = 'symbol_registry'
""")
count = cursor.fetchone()[0]

if count == 1:
    print("✅ Table symbol_registry created successfully")
    
    # Check row count
    cursor.execute("SELECT COUNT(*) FROM symbol_registry")
    row_count = cursor.fetchone()[0]
    print(f"   Registered symbols: {row_count}")
    
    # Show registered symbols
    cursor.execute("SELECT internal_symbol, root, roll_rule, is_active FROM symbol_registry ORDER BY internal_symbol")
    print("\n   Registered symbols:")
    for row in cursor.fetchall():
        status = "ACTIVE" if row[3] else "INACTIVE"
        print(f"     {row[0]:<20} root={row[1]:<4} roll={row[2]} [{status}]")
else:
    print("❌ Table creation failed")

cursor.close()
conn.close()

print("\nMigration complete")
