import psycopg2
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:vZxqxqPPqPPqPPqPPqPPqPPqPPqPPqPP@autorack.proxy.rlwy.net:12345/railway')

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Check for MFE_UPDATE events
cursor.execute("""
    SELECT COUNT(*) 
    FROM automated_signals 
    WHERE event_type = 'MFE_UPDATE'
""")
mfe_count = cursor.fetchone()[0]
print(f"Total MFE_UPDATE events: {mfe_count}")

# Check sample MFE_UPDATE event
cursor.execute("""
    SELECT trade_id, event_type, be_mfe, no_be_mfe, timestamp
    FROM automated_signals 
    WHERE event_type = 'MFE_UPDATE'
    ORDER BY timestamp DESC
    LIMIT 5
""")
print("\nSample MFE_UPDATE events:")
for row in cursor.fetchall():
    print(f"  {row}")

# Check for one specific active trade
cursor.execute("""
    SELECT trade_id, event_type, be_mfe, no_be_mfe, timestamp
    FROM automated_signals 
    WHERE trade_id = '20251114_141700000_BEARISH'
    ORDER BY timestamp DESC
""")
print("\nEvents for trade 20251114_141700000_BEARISH:")
for row in cursor.fetchall():
    print(f"  {row}")

conn.close()
