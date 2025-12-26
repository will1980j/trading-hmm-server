#!/usr/bin/env python3
import os, psycopg2
from dotenv import load_dotenv

load_dotenv()
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("❌ DATABASE_URL not set")
    exit(1)

with open('database/phase_a_active_versions_migration.sql', 'r') as f:
    sql = f.read()

conn = psycopg2.connect(database_url)
cursor = conn.cursor()
cursor.execute(sql)
conn.commit()
cursor.close()
conn.close()

print("✅ Phase A active versions migration complete")
print("   - Created active_dataset_versions table")
print("   - Seeded NQ and MNQ mappings")
