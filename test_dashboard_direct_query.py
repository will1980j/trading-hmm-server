import os
import psycopg2
from psycopg2.extras import RealDictCursor

database_url = os.environ.get('DATABASE_URL')
print(f"Connecting to database...")

try:
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Test the exact query from the robust API
    print("\nTesting ENTRY query...")
    query = """
        SELECT 
            e.id,
            e.trade_id,
            e.direction as bias,
            CAST(e.entry_price AS FLOAT) as entry_price,
            CAST(e.stop_loss AS FLOAT) as stop_loss_price,
            CAST(COALESCE(m.mfe, e.mfe, 0) AS FLOAT) as current_mfe,
            e.session,
            e.signal_date, e.signal_time,
            e.timestamp as created_at,
            'ACTIVE' as trade_status
        FROM automated_signals e
        LEFT JOIN LATERAL (
            SELECT mfe, current_price
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
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    print(f"✅ Query succeeded! Found {len(rows)} active trades")
    
    if rows:
        print("\nFirst trade:")
        for key, value in dict(rows[0]).items():
            print(f"  {key}: {value}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Query failed: {e}")
    import traceback
    traceback.print_exc()
