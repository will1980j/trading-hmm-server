import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def quick_recover():
    conn = None
    try:
        print("Connecting to database...")
        database_url = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(database_url, connect_timeout=10)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        print("Connected successfully")
        
        print("Querying for missed signals...")
        cursor.execute("""
            SELECT date(timestamp AT TIME ZONE 'America/New_York') as date,
                   to_char(timestamp AT TIME ZONE 'America/New_York', 'HH24:MI:SS') as time,
                   bias, session, signal_type, price, htf_aligned
            FROM live_signals 
            WHERE symbol = 'NQ1!' 
            AND htf_aligned = true
            AND timestamp > '2024-09-11 12:20:00'
            AND signal_type NOT LIKE '%DIVERGENCE%'
            AND signal_type NOT LIKE '%CORRELATION%'
            AND signal_type NOT LIKE '%INVERSE%'
            ORDER BY timestamp
            LIMIT 10
        """)
        
        signals = cursor.fetchall()
        print(f"Found {len(signals)} signals")
        
        for signal in signals:
            print(f"Signal: {signal['date']} {signal['time']} {signal['bias']} {signal['signal_type']}")
            
            # Insert into signal_lab_trades
            cursor.execute("""
                INSERT INTO signal_lab_trades 
                (date, time, bias, session, signal_type, entry_price, htf_aligned)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (date, time, signal_type) DO NOTHING
            """, (
                signal['date'], signal['time'], signal['bias'], 
                signal['session'], signal['signal_type'], signal['price'],
                signal['htf_aligned']
            ))
        
        conn.commit()
        print("Recovery completed")
        
    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    quick_recover()