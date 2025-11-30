#!/usr/bin/env python3
import os
import psycopg2

database_url = os.environ.get('DATABASE_URL')
if database_url:
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'automated_signals' 
        ORDER BY ordinal_position
    """)
    cols = [r[0] for r in cursor.fetchall()]
    print('Columns in automated_signals table:')
    for c in cols:
        print(f'  - {c}')
    conn.close()
else:
    print('No DATABASE_URL')
