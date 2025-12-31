#!/usr/bin/env python3
"""
Run Phase E HTF Bias Series Migration
Creates bias_series_1m_v1 table for HTF bias timeline persistence
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
with open('database/phase_e_htf_bias_series_schema.sql', 'r') as f:
    schema_sql = f.read()

print("Executing migration...")
cursor.execute(schema_sql)
conn.commit()

print("Verifying table creation...")
cursor.execute("""
    SELECT COUNT(*) FROM information_schema.tables 
    WHERE table_name = 'bias_series_1m_v1'
""")
count = cursor.fetchone()[0]

if count == 1:
    print("✅ Table bias_series_1m_v1 created successfully")
    
    # Check row count
    cursor.execute("SELECT COUNT(*) FROM bias_series_1m_v1")
    row_count = cursor.fetchone()[0]
    print(f"   Current rows: {row_count}")
else:
    print("❌ Table creation failed")

cursor.close()
conn.close()

print("\nMigration complete")
