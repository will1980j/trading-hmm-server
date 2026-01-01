"""
Signal Contract V1 - Wave 1 Field Mapper
Maps webhook payloads to Signal Contract V1 fields
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import subprocess
import os

def get_logic_version():
    """Get git hash for logic_version"""
    try:
        return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], 
                                      stderr=subprocess.DEVNULL).decode().strip()
    except:
        return 'unknown'

def ms_to_timestamptz(ms_timestamp):
    """Convert milliseconds timestamp to timestamptz"""
    if ms_timestamp is None:
        return None
    return datetime.fromtimestamp(ms_timestamp / 1000.0, tz=ZoneInfo('UTC'))

def floor_to_minute(dt):
    """Floor datetime to minute boundary (bar OPEN time)"""
    if dt is None:
        return None
    return dt.replace(second=0, microsecond=0)

def derive_bar_close_ts(bar_open_ts):
    """Derive bar close timestamp from bar open (add 1 minute)"""
    if bar_open_ts is None:
        return None
    return bar_open_ts + timedelta(minutes=1)

def normalize_direction(payload, event_type, trade_id):
    """Normalize direction from various sources"""
    # Try payload.direction first
    direction = payload.get('direction')
    if direction:
        # Normalize to Bullish/Bearish
        if direction.upper() in ['LONG', 'BULLISH', 'BULL']:
            return 'Bullish'
        elif direction.upper() in ['SHORT', 'BEARISH', 'BEAR']:
            return 'Bearish'
    
    # Try to infer from trade_id suffix
    if trade_id and '_BULLISH' in trade_id.upper():
        return 'Bullish'
    elif trade_id and '_BEARISH' in trade_id.upper():
        return 'Bearish'
    
    return None

def map_wave1_fields(payload, event_type, trade_id=None, prior_event=None):
    """
    Map webhook payload to Wave 1 contract fields
    
    Args:
        payload: Webhook payload dict
        event_type: Event type string
        trade_id: Trade ID (for direction inference)
        prior_event: Most recent event for this trade_id (for carry-forward)
    
    Returns dict with Wave 1 fields to be inserted
    """
    fields = {}
    
    # Identity - with fallbacks
    fields['symbol'] = payload.get('symbol') or (prior_event.get('symbol') if prior_event else None) or os.environ.get('DEFAULT_SYMBOL', 'GLBX.MDP3:NQ')
    fields['logic_version'] = get_logic_version()
    fields['source'] = 'tradingview_webhook'
    
    # Direction - normalize and carry forward
    direction = normalize_direction(payload, event_type, trade_id)
    if not direction and prior_event:
        direction = prior_event.get('direction')
    fields['direction'] = direction
    
    # Status (inferred from event_type)
    if event_type == 'SIGNAL_CREATED':
        fields['status'] = 'PENDING'
    elif event_type == 'ENTRY':
        fields['status'] = 'CONFIRMED'
    elif event_type in ['EXIT_SL', 'EXIT_BE', 'EXIT_TP']:
        fields['status'] = 'EXITED'
    elif event_type == 'CANCELLED':
        fields['status'] = 'CANCELLED'
    else:
        fields['status'] = 'ACTIVE'
    
    # Timestamps - convert from milliseconds and floor to minute
    event_ts_ms = payload.get('event_timestamp') or payload.get('timestamp')
    event_ts = ms_to_timestamptz(event_ts_ms)
    bar_open_ts = floor_to_minute(event_ts) if event_ts else None
    bar_close_ts = derive_bar_close_ts(bar_open_ts)
    
    if event_type == 'SIGNAL_CREATED':
        # Signal bar timestamps
        fields['signal_bar_open_ts'] = bar_open_ts
        fields['signal_bar_close_ts'] = bar_close_ts
        
        # Signal candle OHLC (if provided)
        fields['signal_candle_high'] = payload.get('signal_candle_high')
        fields['signal_candle_low'] = payload.get('signal_candle_low')
    
    elif event_type == 'ENTRY':
        # Entry bar timestamps
        fields['entry_bar_open_ts'] = bar_open_ts
        fields['entry_bar_close_ts'] = bar_close_ts
        
        # Confirmation timestamps (entry bar - 1 minute)
        if bar_open_ts:
            confirmation_bar_close_ts = bar_open_ts - timedelta(minutes=1)
            fields['confirmation_bar_close_ts'] = confirmation_bar_close_ts
            fields['confirmation_bar_open_ts'] = floor_to_minute(confirmation_bar_close_ts)
        
        # Breakeven defaults for new trade
        fields['be_enabled'] = True
        fields['be_trigger_R'] = 1.0
        fields['be_offset_points'] = 0.0
        fields['be_triggered'] = False
    
    elif event_type == 'BE_TRIGGERED':
        # BE trigger timestamps
        fields['be_trigger_bar_open_ts'] = bar_open_ts
        fields['be_trigger_bar_close_ts'] = bar_close_ts
        fields['be_triggered'] = True
    
    elif event_type in ['EXIT_SL', 'EXIT_BE', 'EXIT_TP']:
        # Exit bar timestamps
        fields['exit_bar_open_ts'] = bar_open_ts
        fields['exit_bar_close_ts'] = bar_close_ts
        
        # Carry forward from prior event if missing
        if prior_event:
            if not direction:
                fields['direction'] = prior_event.get('direction')
            if not fields.get('symbol'):
                fields['symbol'] = prior_event.get('symbol')
    
    elif event_type == 'CANCELLED':
        # Cancellation happens at signal bar
        fields['signal_bar_open_ts'] = bar_open_ts
        fields['signal_bar_close_ts'] = bar_close_ts
    
    elif event_type == 'MFE_UPDATE':
        # Extremes (from MFE_UPDATE payload)
        fields['highest_high'] = payload.get('highest_high')
        fields['lowest_low'] = payload.get('lowest_low')
        fields['extremes_last_updated_bar_open_ts'] = bar_open_ts
    
    return fields

def build_wave1_insert_columns():
    """Return list of Wave 1 column names for INSERT"""
    return [
        'symbol', 'logic_version', 'source', 'status',
        'signal_bar_open_ts', 'signal_bar_close_ts',
        'confirmation_bar_open_ts', 'confirmation_bar_close_ts',
        'entry_bar_open_ts', 'entry_bar_close_ts',
        'exit_bar_open_ts', 'exit_bar_close_ts',
        'signal_candle_high', 'signal_candle_low',
        'be_enabled', 'be_trigger_R', 'be_offset_points', 'be_triggered',
        'be_trigger_bar_open_ts', 'be_trigger_bar_close_ts',
        'highest_high', 'lowest_low', 'extremes_last_updated_bar_open_ts'
    ]

def build_wave1_insert_values(wave1_fields):
    """Return tuple of values for INSERT in correct order"""
    cols = build_wave1_insert_columns()
    return tuple(wave1_fields.get(col) for col in cols)

def get_prior_event(trade_id, conn):
    """Get most recent event for trade_id to carry forward fields"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT symbol, direction, session, bias, entry_price, stop_loss
        FROM automated_signals
        WHERE trade_id = %s
        ORDER BY id DESC
        LIMIT 1
    """, (trade_id,))
    row = cursor.fetchone()
    cursor.close()
    
    if row:
        return {
            'symbol': row[0],
            'direction': row[1],
            'session': row[2],
            'bias': row[3],
            'entry_price': row[4],
            'stop_loss': row[5]
        }
    return None
