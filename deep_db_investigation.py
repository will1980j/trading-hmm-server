#!/usr/bin/env python3
"""Deep investigation of database state"""
import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:rlVgkSLbFWUYvxdBXhKPLMrCDqWOctJE@junction.proxy.rlwy.net:57782/railway')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Check all tables that might contain signals
print("=== ALL TABLES IN DATABASE ===")
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name
""")
for row in cur.fetchall():
    print(f"  {row[0]}")

# Check the max ID in automated_signals
print("\n=== AUTOMATED_SIGNALS TABLE STATS ===")
cur.execute("SELECT MAX(id), MIN(id), COUNT(*) FROM automated_signals")
row = cur.fetchone()
print(f"  Max ID: {row[0]}, Min ID: {row[1]}, Total rows: {row[2]}")

# Check if there's a sequence issue
print("\n=== SEQUENCE STATUS ===")
cur.execute("SELECT last_value FROM automated_signals_id_seq")
print(f"  Sequence last_value: {cur.fetchone()[0]}")

# Check for any records with ID > 10513 (the last known ID)
print("\n=== RECORDS WITH ID > 10513 ===")
cur.execute("SELECT id, trade_id, event_type, timestamp FROM automated_signals WHERE id > 10513 ORDER BY id")
rows = cur.fetchall()
print(f"  Found {len(rows)} records")
for row in rows:
    print(f"    ID={row[0]}, trade={row[1]}, type={row[2]}, ts={row[3]}")

# Check if there's a different automated_signals table in another schema
print("\n=== CHECKING FOR DUPLICATE TABLES ===")
cur.execute("""
    SELECT table_schema, table_name 
    FROM information_schema.tables 
    WHERE table_name LIKE '%automated%' OR table_name LIKE '%signal%'
    ORDER BY table_schema, table_name
""")
for row in cur.fetchall():
    print(f"  {row[0]}.{row[1]}")

# Try to insert directly and see what happens
print("\n=== DIRECT INSERT TEST ===")
try:
    cur.execute("""
        INSERT INTO automated_signals (trade_id, event_type, direction, entry_price, stop_loss, risk_distance, session, timestamp)
        VALUES ('DIRECT_TEST_123', 'ENTRY', 'LONG', 25000.00, 24980.00, 20.00, 'TEST', NOW())
        RETURNING id
    """)
    new_id = cur.fetchone()[0]
    print(f"  Direct insert succeeded! New ID: {new_id}")
    conn.commit()
    
    # Verify it exists
    cur.execute("SELECT * FROM automated_signals WHERE trade_id = 'DIRECT_TEST_123'")
    row = cur.fetchone()
    if row:
        print(f"  Verified: Record exists with ID {row[0]}")
    else:
        print("  ERROR: Record not found after insert!")
    
    # Clean up
    cur.execute("DELETE FROM automated_signals WHERE trade_id = 'DIRECT_TEST_123'")
    conn.commit()
    print("  Cleaned up test record")
    
except Exception as e:
    print(f"  Direct insert failed: {e}")
    conn.rollback()

cur.close()
conn.close()
