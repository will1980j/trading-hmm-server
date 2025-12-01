#!/usr/bin/env python3
"""Check what trades remain in the database"""
import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

print("=== ALL ENTRY EVENTS ===")
cur.execute("""
    SELECT trade_id, timestamp, direction, session
    FROM automated_signals
    WHERE event_type = 'ENTRY'
    ORDER BY timestamp DESC
""")
entries = cur.fetchall()
print(f"Total ENTRY events: {len(entries)}")
for row in entries[:15]:
    print(f"  {row[0]} | {row[1]} | {row[2]} | {row[3]}")

print("\n=== ALL EXIT EVENTS ===")
cur.execute("""
    SELECT trade_id, event_type, timestamp
    FROM automated_signals
    WHERE event_type LIKE 'EXIT_%'
    ORDER BY timestamp DESC
""")
exits = cur.fetchall()
print(f"Total EXIT events: {len(exits)}")
for row in exits[:15]:
    print(f"  {row[0]} | {row[1]} | {row[2]}")

print("\n=== EVENT TYPE COUNTS ===")
cur.execute("""
    SELECT event_type, COUNT(*) 
    FROM automated_signals 
    GROUP BY event_type
    ORDER BY COUNT(*) DESC
""")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

conn.close()
