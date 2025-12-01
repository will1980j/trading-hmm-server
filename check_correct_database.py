#!/usr/bin/env python3
"""Check the CORRECT database that Railway is using"""
import psycopg2

# The CORRECT URL from .env
CORRECT_URL = 'postgresql://postgres:hvJnnhbUsRppEDPlGAVrEeVLijYXJntS@caboose.proxy.rlwy.net:17437/railway'

conn = psycopg2.connect(CORRECT_URL)
cur = conn.cursor()

print("=== CORRECT DATABASE STATS ===")
cur.execute("SELECT MAX(id), MIN(id), COUNT(*) FROM automated_signals")
row = cur.fetchone()
print(f"  Max ID: {row[0]}, Min ID: {row[1]}, Total rows: {row[2]}")

print("\n=== MOST RECENT ENTRIES ===")
cur.execute("""
    SELECT id, trade_id, event_type, direction, entry_price, timestamp
    FROM automated_signals 
    ORDER BY id DESC
    LIMIT 10
""")
for row in cur.fetchall():
    print(f"  ID={row[0]}, trade={row[1]}, type={row[2]}, dir={row[3]}, entry={row[4]}, ts={row[5]}")

print("\n=== TODAY'S DATA (Dec 1) ===")
cur.execute("""
    SELECT COUNT(*) FROM automated_signals 
    WHERE timestamp >= '2025-12-01 00:00:00'
""")
print(f"  Events from Dec 1: {cur.fetchone()[0]}")

print("\n=== EVENT TYPES TODAY ===")
cur.execute("""
    SELECT event_type, COUNT(*) 
    FROM automated_signals 
    WHERE timestamp >= '2025-12-01 00:00:00'
    GROUP BY event_type
    ORDER BY COUNT(*) DESC
""")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

print("\n=== UNIQUE TRADE IDS TODAY ===")
cur.execute("""
    SELECT DISTINCT trade_id 
    FROM automated_signals 
    WHERE timestamp >= '2025-12-01 00:00:00'
    ORDER BY trade_id
""")
trade_ids = [row[0] for row in cur.fetchall()]
print(f"  Found {len(trade_ids)} unique trade IDs today")
for tid in trade_ids[:10]:
    print(f"    {tid}")

# Clean up test data
print("\n=== CLEANING UP TEST DATA ===")
cur.execute("DELETE FROM automated_signals WHERE trade_id LIKE 'TEST_%' OR trade_id LIKE 'RAILWAY_TEST_%'")
deleted = cur.rowcount
conn.commit()
print(f"  Deleted {deleted} test records")

cur.close()
conn.close()
