"""
Price Snapshot Processor - Backend MFE/MAE Calculation
Processes OHLC snapshots to update trade metrics without Pine dependency
"""
import psycopg2
from datetime import datetime
from typing import Dict, List, Optional
import os

DATABASE_URL = os.getenv('DATABASE_URL')

def process_price_snapshot(snapshot: Dict) -> Dict:
    """
    Process a single price snapshot and update all active trades
    """
    symbol = snapshot['symbol']
    bar_ts = snapshot['bar_ts']
    high = float(snapshot['high'])
    low = float(snapshot['low'])
    open_price = float(snapshot['open'])
    close = float(snapshot['close'])
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    try:
        # Check for duplicate
        cur.execute("""
            SELECT 1 FROM price_snapshots 
            WHERE symbol = %s AND bar_ts = %s
        """, (symbol, bar_ts))
        if cur.fetchone():
            conn.close()
            return {"status": "duplicate", "updated": 0}
        
        # Store snapshot
        cur.execute("""
            INSERT INTO price_snapshots (symbol, timeframe, bar_ts, open, high, low, close)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (symbol, snapshot.get('timeframe', '1m'), bar_ts, open_price, high, low, close))
        
        # Update indicator health
        try:
            from services.indicator_health_updater import update_indicator_health_from_snapshot
            update_indicator_health_from_snapshot(symbol)
        except:
            pass  # Non-critical
        
        # Get all active trades for this symbol
        cur.execute("""
            SELECT trade_id, direction, entry_price, stop_price, risk_r,
                   no_be_mfe, be_mfe, mae, be_triggered
            FROM confirmed_signals_ledger
            WHERE symbol = %s AND completed = false
        """, (symbol,))
        
        active_trades = cur.fetchall()
        updated_count = 0
        
        for trade in active_trades:
            trade_id, direction, entry, stop, risk_r, curr_no_be_mfe, curr_be_mfe, curr_mae, be_triggered = trade
            
            if not entry or not stop or not risk_r or risk_r == 0:
                continue
            
            # Calculate MFE/MAE candidates
            if direction in ['Bullish', 'LONG']:
                mfe_candidate = (high - entry) / risk_r
                mae_candidate = (low - entry) / risk_r
                stop_hit = low <= stop
            else:  # Bearish/SHORT
                mfe_candidate = (entry - low) / risk_r
                mae_candidate = (entry - high) / risk_r
                stop_hit = high >= stop
            
            # Update values
            new_no_be_mfe = max(curr_no_be_mfe or 0.0, mfe_candidate)
            new_mae = min(curr_mae or 0.0, mae_candidate, 0.0)
            
            # BE logic
            new_be_triggered = be_triggered
            if not be_triggered and new_no_be_mfe >= 1.0:
                new_be_triggered = True
            
            # BE MFE continues tracking until completion
            new_be_mfe = max(curr_be_mfe or 0.0, mfe_candidate)
            # BE MFE cannot exceed no_be_mfe
            new_be_mfe = min(new_be_mfe, new_no_be_mfe)
            
            # Check completion
            if stop_hit:
                cur.execute("""
                    UPDATE confirmed_signals_ledger
                    SET no_be_mfe = %s, be_mfe = %s, mae = %s,
                        be_triggered = %s, completed = true,
                        completed_at = %s, updated_at = NOW()
                    WHERE trade_id = %s
                """, (new_no_be_mfe, new_be_mfe, new_mae, new_be_triggered,
                      datetime.fromtimestamp(bar_ts / 1000), trade_id))
            else:
                cur.execute("""
                    UPDATE confirmed_signals_ledger
                    SET no_be_mfe = %s, be_mfe = %s, mae = %s,
                        be_triggered = %s, updated_at = NOW()
                    WHERE trade_id = %s
                """, (new_no_be_mfe, new_be_mfe, new_mae, new_be_triggered, trade_id))
            
            updated_count += 1
        
        conn.commit()
        return {"status": "success", "updated": updated_count}
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


def validate_snapshot(data: Dict) -> Optional[str]:
    """
    Validate price snapshot payload
    Returns error message or None if valid
    """
    if 'symbol' not in data:
        return "symbol required"
    if 'bar_ts' not in data:
        return "bar_ts required"
    
    try:
        high = float(data.get('high', 0))
        low = float(data.get('low', 0))
        if high < low:
            return "high must be >= low"
    except (ValueError, TypeError):
        return "numeric fields required"
    
    return None
