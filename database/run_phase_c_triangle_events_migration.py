#!/usr/bin/env python3
"""Run Phase C triangle events migration"""

import os, psycopg2
from dotenv import load_dotenv

load_dotenv()
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("ERROR: DATABASE_URL not set")
    exit(1)

with open('database/phase_c_triangle_events_schema.sql', 'r') as f:
    sql = f.read()

conn = psycopg2.connect(database_url)
cursor = conn.cursor()
cursor.execute(sql)
conn.commit()
cursor.close()
conn.close()

print("[OK] Phase C triangle events migration complete")
print("     - Created triangle_events_v1 table")
print("     - Created indexes")
