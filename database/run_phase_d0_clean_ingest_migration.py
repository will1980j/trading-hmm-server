#!/usr/bin/env python3
"""
Run Phase D.0 Clean Ingest Runs Migration
Creates clean_ingest_runs table for ingestion audit trail
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
with open('database/phase_d0_clean_ingest_runs_schema.sql', 'r') as f:
    schema_sql = f.read()

print("Executing migration...")
cursor.execute(schema_sql)
conn.commit()

print("Verifying table creation...")
cursor.execute("""
    SELECT COUNT(*) FROM information_schema.tables 
    WHERE table_name = 'clean_ingest_runs'
""")
count = cursor.fetchone()[0]

if count == 1:
    print("✅ Table clean_ingest_runs created successfully")
    
    # Check row count
    cursor.execute("SELECT COUNT(*) FROM clean_ingest_runs")
    row_count = cursor.fetchone()[0]
    print(f"   Current runs: {row_count}")
else:
    print("❌ Table creation failed")

cursor.close()
conn.close()

print("\nMigration complete")
