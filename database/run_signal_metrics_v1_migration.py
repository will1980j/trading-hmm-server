#!/usr/bin/env python3
import os, psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
cursor = conn.cursor()

with open('database/signal_metrics_v1_schema.sql', 'r') as f:
    cursor.execute(f.read())
conn.commit()

cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'signal_metrics_v1'")
print("✅ signal_metrics_v1 created" if cursor.fetchone()[0] == 1 else "❌ Failed")
cursor.close()
conn.close()
