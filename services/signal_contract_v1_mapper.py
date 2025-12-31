"""
Signal Contract V1 - Wave 1 Field Mapper
Maps webhook payloads to Signal Contract V1 fields
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import subprocess

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

def derive_bar_close_ts(bar_open_ts):
    """Derive bar close timestamp from bar open (add 1 minute)"""
    if bar_open_ts is None:
        return None
    return bar_open_ts + timedelta(minutes=1)

def map_wave1_fields(payload, event_type):
    """
    Map webhook payload to Wave 1 contract fields
    
    Returns dict with Wave 1 fields to be inserted
    """
    fields = {}
    
    # Identity
    fields['symbol'] = payload.get('symbol', 'UNKNOWN')
    fields['logic_version'] = get_logic_version()
    fields['source'] = 'tradingview_webhook'
    
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
    
    # Timestamps - convert from milliseconds
    event_ts_ms = payload.get('event_timestamp') or payload.get('timestamp')
    
    if event_type == 'SIGNAL_CREATED':
        # Signal bar timestamps
        signal_bar_open_ts = ms_to_timestamptz(event_ts_ms)
        fields['signal_bar_open_ts'] = signal_bar_open_ts
        fields['signal_bar_close_ts'] = derive_bar_close_ts(signal_bar_open_ts)
        
        # Signal candle OHLC (if provided)
        fields['signal_candle_high'] = payload.get('signal_candle_high')
        fields['signal_candle_low'] = payload.get('signal_candle_low')
    
    elif event_type == 'ENTRY':
        # Entry bar timestamps
        entry_bar_open_ts = ms_to_timestamptz(event_ts_ms)
        fields['entry_bar_open_ts'] = entry_bar_open_ts
        fields['entry_bar_close_ts'] = derive_bar_close_ts(entry_bar_open_ts)
        
        # Confirmation timestamps (entry bar - 1 minute)
        if entry_bar_open_ts:
            confirmation_bar_close_ts = entry_bar_open_ts - timedelta(minutes=1)
            fields['confirmation_bar_close_ts'] = confirmation_bar_close_ts
            fields['confirmation_bar_open_ts'] = confirmation_bar_close_ts - timedelta(seconds=59)
    
    elif event_type == 'BE_TRIGGERED':
        # BE trigger timestamps
        be_trigger_bar_open_ts = ms_to_timestamptz(event_ts_ms)
        fields['be_trigger_bar_open_ts'] = be_trigger_bar_open_ts
        fields['be_trigger_bar_close_ts'] = derive_bar_close_ts(be_trigger_bar_open_ts)
        fields['be_triggered'] = True
    
    elif event_type in ['EXIT_SL', 'EXIT_BE', 'EXIT_TP']:
        # Exit bar timestamps
        exit_bar_open_ts = ms_to_timestamptz(event_ts_ms)
        fields['exit_bar_open_ts'] = exit_bar_open_ts
        fields['exit_bar_close_ts'] = derive_bar_close_ts(exit_bar_open_ts)
    
    elif event_type == 'CANCELLED':
        # Cancellation happens at signal bar
        cancel_bar_open_ts = ms_to_timestamptz(event_ts_ms)
        fields['signal_bar_open_ts'] = cancel_bar_open_ts
        fields['signal_bar_close_ts'] = derive_bar_close_ts(cancel_bar_open_ts)
    
    # Breakeven fields (defaults)
    if event_type == 'ENTRY':
        fields['be_enabled'] = True
        fields['be_trigger_R'] = 1.0
        fields['be_offset_points'] = 0.0
        fields['be_triggered'] = False
    
    # Extremes (from MFE_UPDATE payload)
    if event_type == 'MFE_UPDATE':
        fields['highest_high'] = payload.get('highest_high')
        fields['lowest_low'] = payload.get('lowest_low')
        extremes_bar_open_ts = ms_to_timestamptz(event_ts_ms)
        fields['extremes_last_updated_bar_open_ts'] = extremes_bar_open_ts
    
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
