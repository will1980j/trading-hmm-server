import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def recover_missed_signals():
    """Recover missed NQ HTF aligned signals from live_signals table"""
    try:
        # Connect to Railway PostgreSQL
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("DATABASE_URL not found in environment")
            return
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        print("Connected to PostgreSQL database")
        
        # Find NQ1! HTF aligned signals after 12:20pm Sep 11th that should have been auto-populated
        cursor.execute("""
            SELECT date(timestamp AT TIME ZONE 'America/New_York') as date,
                   to_char(timestamp AT TIME ZONE 'America/New_York', 'HH24:MI:SS') as time,
                   bias, session, signal_type, price, htf_aligned, timestamp
            FROM live_signals 
            WHERE symbol = 'NQ1!' 
            AND htf_aligned = true
            AND timestamp > '2024-09-11 12:20:00'
            AND signal_type NOT LIKE '%DIVERGENCE%'
            AND signal_type NOT LIKE '%CORRELATION%'
            AND signal_type NOT LIKE '%INVERSE%'
            ORDER BY timestamp
        """)
        
        missed_signals = cursor.fetchall()
        print(f"Found {len(missed_signals)} NQ HTF aligned signals after 12:20pm Sep 11th")
        
        if not missed_signals:
            print("No missed signals found")
            return
        
        populated_count = 0
        
        for signal in missed_signals:
            # Check if already exists in signal_lab_trades
            cursor.execute("""
                SELECT COUNT(*) FROM signal_lab_trades 
                WHERE date = %s AND time = %s AND signal_type = %s
            """, (signal['date'], signal['time'], signal['signal_type']))
            
            if cursor.fetchone()['count'] > 0:
                print(f"Already exists: {signal['date']} {signal['time']} {signal['signal_type']}")
                continue
            
            # Insert into signal_lab_trades
            cursor.execute("""
                INSERT INTO signal_lab_trades 
                (date, time, bias, session, signal_type, entry_price, htf_aligned)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                signal['date'], signal['time'], signal['bias'], 
                signal['session'], signal['signal_type'], signal['price'],
                signal['htf_aligned']
            ))
            
            populated_count += 1
            print(f"Populated: {signal['date']} {signal['time']} {signal['bias']} {signal['session']} @ {signal['price']}")
        
        conn.commit()
        print(f"\nSuccessfully populated {populated_count} missed NQ HTF aligned signals")
        
    except Exception as e:
        print(f"Error: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    recover_missed_signals()