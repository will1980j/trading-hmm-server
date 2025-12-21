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
        
        # Introspect schema to determine column names
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'confirmed_signals_ledger'
            AND column_name IN ('entry', 'entry_price', 'stop', 'stop_price', 'risk_r', 'risk_R', 'risk', 'mae', 'mae_global_r', 'be_triggered')
        """)
        existing_cols = {row[0] for row in cur.fetchall()}
        
        # Determine column names
        entry_col = 'entry' if 'entry' in existing_cols else 'entry_price'
        stop_col = 'stop' if 'stop' in existing_cols else 'stop_price'
        risk_col = 'risk_r' if 'risk_r' in existing_cols else ('risk_R' if 'risk_R' in existing_cols else 'risk')
        mae_col = 'mae' if 'mae' in existing_cols else 'mae_global_r'
        has_be_triggered = 'be_triggered' in existing_cols
        
        # Build dynamic query
        select_cols = f"""
            trade_id, direction, {entry_col}, {stop_col}, 
            {risk_col}, no_be_mfe, be_mfe, {mae_col}
        """
        if has_be_triggered:
            select_cols += ", be_triggered"
        
        # Get all active trades for this symbol
        cur.execute(f"""
            SELECT {select_cols}
            FROM confirmed_signals_ledger
            WHERE symbol = %s AND completed = false
        """, (symbol,))
        
        active_trades = cur.fetchall()
        updated_count = 0
        
        for trade in active_trades:
            if has_be_triggered:
                trade_id, direction, entry, stop, risk_r, curr_no_be_mfe, curr_be_mfe, curr_mae, be_triggered = trade
            else:
                trade_id, direction, entry, stop, risk_r, curr_no_be_mfe, curr_be_mfe, curr_mae = trade
                be_triggered = False
            
            # Compute risk_r if not stored
            if not risk_r and entry and stop:
                risk_r = abs(entry - stop)
            
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
            
            # Build UPDATE statement
            update_cols = f"no_be_mfe = %s, be_mfe = %s, {mae_col} = %s"
            if has_be_triggered:
                update_cols += ", be_triggered = %s"
            update_cols += ", updated_at = NOW()"
            
            # Check completion
            if stop_hit:
                update_cols += ", completed = true, completed_at = %s"
                params = [new_no_be_mfe, new_be_mfe, new_mae]
                if has_be_triggered:
                    params.append(new_be_triggered)
                params.extend([datetime.fromtimestamp(bar_ts / 1000), trade_id])
                
                cur.execute(f"""
                    UPDATE confirmed_signals_ledger
                    SET {update_cols}
                    WHERE trade_id = %s
                """, params)
            else:
                params = [new_no_be_mfe, new_be_mfe, new_mae]
                if has_be_triggered:
                    params.append(new_be_triggered)
                params.append(trade_id)
                
                cur.execute(f"""
                    UPDATE confirmed_signals_ledger
                    SET {update_cols}
                    WHERE trade_id = %s
                """, params)
            
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
