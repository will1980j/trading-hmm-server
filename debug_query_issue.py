import psycopg2
import os

DATABASE_URL = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

print("=" * 80)
print("DEBUGGING QUERY ISSUE")
print("=" * 80)

# Test the EXACT query from the API
query = """
    SELECT 
        e.id,
        e.trade_id,
        e.direction as bias,
        CAST(e.entry_price AS FLOAT) as entry_price,
        CAST(e.stop_loss AS FLOAT) as stop_loss_price,
        CAST(COALESCE(m.be_mfe, e.be_mfe, 0) AS FLOAT) as be_mfe,
        CAST(COALESCE(m.no_be_mfe, e.no_be_mfe, m.mfe, e.mfe, 0) AS FLOAT) as no_be_mfe,
        e.session,
        e.signal_date, e.signal_time,
        e.timestamp as created_at,
        'ACTIVE' as trade_status
    FROM automated_signals e
    LEFT JOIN LATERAL (
        SELECT be_mfe, no_be_mfe, mfe, current_price
        FROM automated_signals
        WHERE trade_id = e.trade_id
        AND event_type = 'MFE_UPDATE'
        ORDER BY timestamp DESC
        LIMIT 1
    ) m ON true
    WHERE e.event_type = 'ENTRY'
    AND e.trade_id NOT IN (
        SELECT trade_id FROM automated_signals 
        WHERE event_type LIKE 'EXIT_%'
    )
    ORDER BY e.timestamp DESC
    LIMIT 10;
"""

print("\nRunning active trades query...")
cur.execute(query)
results = cur.fetchall()

print(f"\nFound {len(results)} active trades")

if results:
    print("\nMost Recent 3:")
    for i, row in enumerate(results[:3]):
        print(f"\n{i+1}. Trade ID: {row[1]}")
        print(f"   Signal Time: {row[9]}")
        print(f"   Entry: {row[3]}")
        print(f"   Timestamp: {row[10]}")

# Now check what the LATEST ENTRY event actually is
print("\n" + "=" * 80)
print("LATEST ENTRY EVENTS (should show 22:31)")
print("=" * 80)

cur.execute("""
    SELECT trade_id, signal_time, entry_price, timestamp
    FROM automated_signals
    WHERE event_type = 'ENTRY'
    ORDER BY timestamp DESC
    LIMIT 5
""")

results = cur.fetchall()
for row in results:
    print(f"\nTrade ID: {row[0]}")
    print(f"  Signal Time: {row[1]}")
    print(f"  Entry: {row[2]}")
    print(f"  Timestamp: {row[3]}")

# Check if those trades have EXIT events
print("\n" + "=" * 80)
print("CHECKING IF RECENT TRADES HAVE EXIT EVENTS")
print("=" * 80)

cur.execute("""
    SELECT DISTINCT trade_id
    FROM automated_signals
    WHERE event_type LIKE 'EXIT_%'
    AND timestamp > NOW() - INTERVAL '3 hours'
    ORDER BY trade_id DESC
    LIMIT 10
""")

exit_trades = [row[0] for row in cur.fetchall()]
print(f"\nTrades with EXIT events in last 3 hours: {len(exit_trades)}")
for trade_id in exit_trades[:5]:
    print(f"  - {trade_id}")

cur.close()
conn.close()
