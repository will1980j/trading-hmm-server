import sqlite3
from datetime import datetime

def populate_missed_signals():
    conn = sqlite3.connect('trading_data.db')
    cursor = conn.cursor()
    
    # Get NQ1! HTF aligned signals from this week that aren't divergence signals
    cursor.execute('''
        SELECT date, time, symbol, signal_type, bias, session, htf_aligned, open_price, entry_price, stop_loss
        FROM live_signals 
        WHERE date >= '2025-09-09' AND date <= '2025-09-13'
        AND symbol = 'NQ1!' 
        AND htf_aligned = 1
        AND signal_type NOT LIKE '%DIVERGENCE%'
        AND signal_type NOT LIKE '%CORRELATION%'
        AND signal_type NOT LIKE '%INVERSE%'
        ORDER BY date, time
    ''')
    
    missed_signals = cursor.fetchall()
    
    if not missed_signals:
        print("No missed signals found to populate.")
        conn.close()
        return
    
    print(f"Found {len(missed_signals)} missed signals to populate:")
    
    populated_count = 0
    for signal in missed_signals:
        date, time, symbol, signal_type, bias, session, htf_aligned, open_price, entry_price, stop_loss = signal
        
        # Check if this signal already exists in signal_lab_trades
        cursor.execute('''
            SELECT COUNT(*) FROM signal_lab_trades 
            WHERE date = ? AND time = ? AND signal_type = ?
        ''', (date, time, signal_type))
        
        if cursor.fetchone()[0] > 0:
            print(f"Signal already exists: {date} {time} {signal_type}")
            continue
        
        # Insert into signal_lab_trades
        cursor.execute('''
            INSERT INTO signal_lab_trades 
            (date, time, bias, session, signal_type, open_price, entry_price, stop_loss, htf_aligned)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date, time, bias, session, signal_type, open_price, entry_price, stop_loss, htf_aligned))
        
        populated_count += 1
        print(f"Populated: {date} {time} {signal_type} ({bias} {session})")
    
    conn.commit()
    conn.close()
    
    print(f"\nSuccessfully populated {populated_count} missed signals to Signal Lab.")

if __name__ == "__main__":
    populate_missed_signals()