import requests
import psycopg2
import os

# Direct database query to see ALL events
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/trading')

print("=" * 80)
print("CHECKING ALL DATABASE EVENTS")
print("=" * 80)

try:
    # Try to connect to Railway database
    conn = psycopg2.connect("postgresql://postgres:CtqxqPxqJqPPqJJJJJJJJJJJJJJJJJJJ@postgres.railway.internal:5432/railway")
    cursor = conn.cursor()
    
    # Get all event types
    cursor.execute("""
        SELECT event_type, COUNT(*) as count
        FROM automated_signals
        GROUP BY event_type
        ORDER BY count DESC
    """)
    
    print("\nEvent Types in Database:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} events")
    
    # Get sample of each event type
    cursor.execute("""
        SELECT DISTINCT event_type FROM automated_signals
    """)
    
    event_types = [row[0] for row in cursor.fetchall()]
    
    for event_type in event_types:
        print(f"\n--- Sample {event_type} Event ---")
        cursor.execute(f"""
            SELECT trade_id, mfe, final_mfe, current_price, timestamp
            FROM automated_signals
            WHERE event_type = '{event_type}'
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        row = cursor.fetchone()
        if row:
            print(f"  Trade ID: {row[0]}")
            print(f"  MFE: {row[1]}")
            print(f"  Final MFE: {row[2]}")
            print(f"  Current Price: {row[3]}")
            print(f"  Timestamp: {row[4]}")
    
    conn.close()
    
except Exception as e:
    print(f"Direct DB connection failed: {e}")
    print("\nTrying via API...")
    
    # Fall back to checking via webhook test
    print("\nSend me ONE of the alert messages from TradingView Alert Log")
    print("Copy the JSON payload and I'll tell you what's wrong")

print("\n" + "=" * 80)
