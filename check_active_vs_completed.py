"""Check which trades should be active vs completed"""
import os
import psycopg2

database_url = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(database_url)
cursor = conn.cursor()

# Get all ENTRY events
cursor.execute("""
SELECT trade_id, timestamp
FROM automated_signals
WHERE event_type = 'ENTRY'
ORDER BY timestamp DESC
LIMIT 20
""")

entries = cursor.fetchall()

print(f"\n📊 Checking {len(entries)} recent ENTRY events:\n")

for trade_id, entry_time in entries:
    # Check if this trade has an EXIT event
    cursor.execute("""
    SELECT event_type, timestamp
    FROM automated_signals
    WHERE trade_id = %s
    AND event_type LIKE 'EXIT_%%'
    ORDER BY timestamp DESC
    LIMIT 1
    """, (trade_id,))
    
    exit_event = cursor.fetchone()
    
    if exit_event:
        exit_type, exit_time = exit_event
        print(f"✅ {trade_id}")
        print(f"   Entry: {entry_time}")
        print(f"   Exit: {exit_time} ({exit_type})")
        print(f"   Status: COMPLETED")
    else:
        print(f"❌ {trade_id}")
        print(f"   Entry: {entry_time}")
        print(f"   Exit: NONE")
        print(f"   Status: ACTIVE (should show as ACTIVE)")
    print()

# Count totals
cursor.execute("""
SELECT COUNT(DISTINCT trade_id)
FROM automated_signals
WHERE event_type = 'ENTRY'
""")
total_entries = cursor.fetchone()[0]

cursor.execute("""
SELECT COUNT(DISTINCT trade_id)
FROM automated_signals
WHERE event_type LIKE 'EXIT_%'
""")
total_exits = cursor.fetchone()[0]

print(f"\n📈 Summary:")
print(f"  Total ENTRY events: {total_entries}")
print(f"  Total EXIT events: {total_exits}")
print(f"  Active trades (no exit): {total_entries - total_exits}")

conn.close()
