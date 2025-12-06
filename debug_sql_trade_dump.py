import os
import psycopg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

load_dotenv()

def run():
    database_url = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(database_url)
    cur = conn.cursor(cursor_factory=DictCursor)
    trade_id = "20251205_075700000_BULLISH"  # change if needed
    # Check total count
    cur.execute("SELECT COUNT(*) FROM automated_signals;")
    print(f"Total rows in automated_signals: {cur.fetchone()[0]}")
    
    # List ALL trade_ids (most recent first)
    cur.execute("""
        SELECT DISTINCT trade_id, MIN(timestamp) as first_ts
        FROM automated_signals
        GROUP BY trade_id
        ORDER BY first_ts DESC
        LIMIT 15;
    """)
    print("\n=== ALL TRADE IDs (most recent) ===")
    for r in cur.fetchall():
        print(dict(r))
    
    print(f"\n=== EVENTS FOR TRADE: {trade_id} ===")
    cur.execute("""
        SELECT id, trade_id, event_type, timestamp, signal_time
        FROM automated_signals
        WHERE trade_id = %s
        ORDER BY timestamp ASC;
    """, (trade_id,))
    rows = cur.fetchall()
    if not rows:
        print("No events found for this trade_id")
    for r in rows:
        print(dict(r))
    cur.close()
    conn.close()

if __name__ == "__main__":
    run()
