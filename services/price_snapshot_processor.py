"""
Price Snapshot Processor - Backend MFE/MAE Calculation
Processes OHLC snapshots to update trade metrics without Pine dependency
"""
import psycopg2
from datetime import datetime
from typing import Dict, List, Optional, Set
from decimal import Decimal
import os

DATABASE_URL = os.getenv('DATABASE_URL')

def f(x):
    """Convert Decimal/numeric to float for arithmetic"""
    if x is None:
        return None
    if isinstance(x, Decimal):
        return float(x)
    return float(x)

def canonical_symbol(sym: str) -> str:
    """Normalize symbol for consistent matching"""
    if not sym:
        return ''
    sym = sym.strip()
    if ':' in sym:
        return sym.split(':')[-1]
    return sym

def get_confirmed_ledger_columns(cur) -> Set[str]:
    """Get actual column names from confirmed_signals_ledger"""
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'public'
        AND table_name = 'confirmed_signals_ledger'
    """)
    return {row[0] for row in cur.fetchall()}

def process_price_snapshot(snapshot: Dict) -> Dict:
    """
    Process a single price snapshot and update all active trades
    """
    symbol = canonical_symbol(snapshot['symbol'])
    bar_ts = snapshot['bar_ts']
    high = f(snapshot['high'])
    low = f(snapshot['low'])
    open_price = f(snapshot['open'])
    close = f(snapshot['close'])
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    try:
        # Upsert snapshot (update if exists)
        cur.execute("""
            INSERT INTO price_snapshots (symbol, timeframe, bar_ts, open, high, low, close, received_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (symbol, bar_ts) DO UPDATE SET
                open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                received_at = NOW()
        """, (symbol, snapshot.get('timeframe', '1m'), bar_ts, open_price, high, low, close))
        
        # Update indicator health
        try:
            from services.indicator_health_updater import update_indicator_health_from_snapshot
            update_indicator_health_from_snapshot(symbol)
        except:
            pass  # Non-critical
        
        # Introspect schema
        cols = get_confirmed_ledger_columns(cur)
        
        # Determine symbol column
        symbol_col = None
        for candidate in ['symbol', 'exchange', 'ticker', 'instrument', 'contract']:
            if candidate in cols:
                symbol_col = candidate
                break
        
        # If no symbol column exists, cannot safely map trades
        if not symbol_col:
            conn.commit()
            return {"status": "ignored", "reason": "confirmed_signals_ledger has no symbol column", "updated": 0}
        
        # Determine other column names
        entry_col = 'entry' if 'entry' in cols else 'entry_price'
        stop_col = 'stop' if 'stop' in cols else 'stop_price'
        
        risk_col = None
        if 'risk_r' in cols:
            risk_col = 'risk_r'
        elif 'risk_R' in cols:
            risk_col = 'risk_R'
        elif 'risk' in cols:
            risk_col = 'risk'
        
        mae_col = None
        if 'mae' in cols:
            mae_col = 'mae'
        elif 'mae_global_r' in cols:
            mae_col = 'mae_global_r'
        
        has_be_triggered = 'be_triggered' in cols
        has_completed = 'completed' in cols
        
        # Build SELECT
        select_parts = [
            'trade_id',
            'direction',
            entry_col,
            stop_col,
            f'{risk_col}' if risk_col else 'NULL as risk',
            'no_be_mfe',
            'be_mfe',
            f'{mae_col}' if mae_col else 'NULL as mae'
        ]
        if has_be_triggered:
            select_parts.append('be_triggered')
        else:
            select_parts.append('NULL as be_triggered')
        
        select_sql = ', '.join(select_parts)
        
        # Build WHERE clause
        where_parts = [f"{symbol_col} = %s"]
        query_params = [symbol]
        
        if has_completed:
            where_parts.append("completed = false")
        
        where_clause = ' AND '.join(where_parts) if where_parts else '1=1'
        
        # Get all active trades
        cur.execute(f"""
            SELECT {select_sql}
            FROM confirmed_signals_ledger
            WHERE {where_clause}
        """, query_params)
        
        active_trades = cur.fetchall()
        col_names = [desc[0] for desc in cur.description]
        updated_count = 0
        
        for row in active_trades:
            trade_dict = dict(zip(col_names, row))
            
            trade_id = trade_dict['trade_id']
            direction = trade_dict['direction']
            entry = f(trade_dict.get(entry_col))
            stop = f(trade_dict.get(stop_col))
            risk_r = f(trade_dict.get('risk') or trade_dict.get(risk_col)) if risk_col else None
            curr_no_be_mfe = f(trade_dict.get('no_be_mfe')) or 0.0
            curr_be_mfe = f(trade_dict.get('be_mfe')) or 0.0
            curr_mae = f(trade_dict.get('mae')) or 0.0
            be_triggered = trade_dict.get('be_triggered') or False
            
            # Compute risk if not stored
            if not risk_r and entry and stop:
                risk_r = abs(entry - stop)
            
            if not entry or not stop or not risk_r or risk_r == 0:
                continue
            
            # Calculate MFE/MAE candidates
            try:
                if direction in ['Bullish', 'LONG']:
                    mfe_candidate = (high - entry) / risk_r
                    mae_candidate = (low - entry) / risk_r
                    stop_hit = low <= stop
                else:  # Bearish/SHORT
                    mfe_candidate = (entry - low) / risk_r
                    mae_candidate = (entry - high) / risk_r
                    stop_hit = high >= stop
            except TypeError as e:
                logger.error(f"[PRICE_SNAPSHOT] Type error in MFE calc: entry={type(entry)}, stop={type(stop)}, high={type(high)}, low={type(low)}, risk_r={type(risk_r)}")
                continue
            
            # Update values
            new_no_be_mfe = max(curr_no_be_mfe, mfe_candidate)
            new_mae = min(curr_mae, mae_candidate, 0.0)
            
            # BE logic
            new_be_triggered = be_triggered
            if not be_triggered and new_no_be_mfe >= 1.0:
                new_be_triggered = True
            
            # BE MFE continues tracking
            new_be_mfe = max(curr_be_mfe, mfe_candidate)
            new_be_mfe = min(new_be_mfe, new_no_be_mfe)
            
            # Build UPDATE
            update_parts = ['no_be_mfe = %s', 'be_mfe = %s']
            params = [new_no_be_mfe, new_be_mfe]
            
            if mae_col:
                update_parts.append(f'{mae_col} = %s')
                params.append(new_mae)
            
            if has_be_triggered:
                update_parts.append('be_triggered = %s')
                params.append(new_be_triggered)
            
            update_parts.append('updated_at = NOW()')
            
            if stop_hit and has_completed:
                update_parts.append('completed = true')
                update_parts.append('completed_at = %s')
                params.append(datetime.fromtimestamp(bar_ts / 1000))
            
            params.append(trade_id)
            
            update_sql = ', '.join(update_parts)
            cur.execute(f"""
                UPDATE confirmed_signals_ledger
                SET {update_sql}
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
