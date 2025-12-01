#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
cur = conn.cursor()

# Get schema
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'automated_signals'")
print('Columns:', [r[0] for r in cur.fetchall()])

# Get all data
print("\n\nALL DATA:")
cur.execute("SELECT * FROM automated_signals ORDER BY timestamp DESC LIMIT 20")
cols = [desc[0] for desc in cur.description]
print("Columns:", cols)
for row in cur.fetchall():
    print(dict(zip(cols, row)))
    print()

cur.close()
conn.close()
