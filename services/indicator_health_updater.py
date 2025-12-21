"""
Indicator Health Updater
Updates indicator health status based on price snapshot activity
"""
import psycopg2
import os
from datetime import datetime, timedelta

DATABASE_URL = os.getenv('DATABASE_URL')

def update_indicator_health_from_snapshot(symbol: str):
    """
    Update indicator health status when price snapshot received
    Price snapshots count as indicator activity
    """
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    try:
        # Update or insert indicator health record
        cur.execute("""
            INSERT INTO indicator_health (symbol, last_activity, status, updated_at)
            VALUES (%s, NOW(), 'GREEN', NOW())
            ON CONFLICT (symbol) 
            DO UPDATE SET 
                last_activity = NOW(),
                status = 'GREEN',
                updated_at = NOW()
        """, (symbol,))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        # Non-critical - don't fail snapshot processing
        pass
    finally:
        cur.close()
        conn.close()


def check_indicator_health():
    """
    Check indicator health for all symbols
    Returns status based on last activity
    """
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    try:
        # Get all active trades with their symbols
        cur.execute("""
            SELECT DISTINCT symbol 
            FROM confirmed_signals_ledger 
            WHERE completed = false
        """)
        
        active_symbols = [row[0] for row in cur.fetchall()]
        
        health_status = {}
        for symbol in active_symbols:
            # Check last price snapshot or MFE update
            cur.execute("""
                SELECT 
                    COALESCE(
                        (SELECT MAX(created_at) FROM price_snapshots WHERE symbol = %s),
                        (SELECT MAX(updated_at) FROM confirmed_signals_ledger WHERE symbol = %s)
                    ) as last_activity
            """, (symbol, symbol))
            
            result = cur.fetchone()
            if result and result[0]:
                last_activity = result[0]
                age_minutes = (datetime.now() - last_activity).total_seconds() / 60
                
                if age_minutes < 5:
                    status = 'GREEN'
                elif age_minutes < 15:
                    status = 'YELLOW'
                else:
                    status = 'RED'
                
                health_status[symbol] = {
                    'status': status,
                    'last_activity': last_activity.isoformat(),
                    'age_minutes': int(age_minutes)
                }
            else:
                health_status[symbol] = {
                    'status': 'UNKNOWN',
                    'last_activity': None,
                    'age_minutes': None
                }
        
        return health_status
        
    finally:
        cur.close()
        conn.close()
