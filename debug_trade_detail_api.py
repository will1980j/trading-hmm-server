"""Debug why trade-detail API returns empty events"""
import psycopg2
import os
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()

trade_id = "20251212_151200000_BEARISH"

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor(cursor_factory=RealDictCursor)

# Same query as API
cursor.execute("""
    SELECT 
        id, trade_id, event_type, direction, entry_price,
        stop_loss, session, bias, risk_distance,
        current_price, mfe, be_mfe, no_be_mfe,
        exit_price, final_mfe,
        signal_date, signal_time, timestamp
    FROM automated_signals
    WHERE trade_id = %s
    ORDER BY timestamp ASC
""", (trade_id,))

rows = cursor.fetchall()

print(f"Database query returned: {len(rows)} rows")
print()

if rows:
    events = []
    for row in rows:
        event = dict(row)
        events.append(event)
        print(f"Event: {event['event_type']}")
        print(f"   BE MFE: {event['be_mfe']}")
        print(f"   No-BE MFE: {event['no_be_mfe']}")
        print()
    
    # Now test build_trade_state
    print("=" * 80)
    print("Testing build_trade_state...")
    print("=" * 80)
    
    from automated_signals_state import build_trade_state
    
    trade_state = build_trade_state(events)
    
    if trade_state:
        print(f"Trade state built successfully")
        print(f"   Trade ID: {trade_state.get('trade_id')}")
        print(f"   Status: {trade_state.get('status')}")
        print(f"   Direction: {trade_state.get('direction')}")
        print(f"   Entry: {trade_state.get('entry_price')}")
        print(f"   Stop: {trade_state.get('stop_loss')}")
        print()
        
        # Check if events are in trade_state
        if 'events' in trade_state:
            print(f"   Events in trade_state: {len(trade_state['events'])}")
        else:
            print("   ⚠️ No 'events' key in trade_state!")
            print(f"   Keys in trade_state: {list(trade_state.keys())[:10]}")
    else:
        print("❌ build_trade_state returned None!")

cursor.close()
conn.close()
