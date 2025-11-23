"""
Signal State Builder (Phase 2A)
Unified view model builder for signal lifecycle
NO DATABASE WRITES - view model only
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def build_signal_state(rows_for_trade_id: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Build unified signal state from multiple event rows
    
    Args:
        rows_for_trade_id: List of database rows for a single trade_id
        
    Returns:
        Unified signal state dict or None if invalid
    """
    if not rows_for_trade_id:
        return None
    
    try:
        # Sort by timestamp to get chronological order
        sorted_rows = sorted(rows_for_trade_id, key=lambda r: r.get('timestamp', 0) or 0)
        
        # Get base info from first row (ENTRY event)
        first_row = sorted_rows[0]
        
        # Build lifecycle events
        lifecycle = []
        for row in sorted_rows:
            event = {
                'event_type': row.get('event_type'),
                'timestamp': row.get('timestamp'),
                'mfe': _safe_float(row.get('mfe')),
                'be_mfe': _safe_float(row.get('be_mfe')),
                'no_be_mfe': _safe_float(row.get('no_be_mfe')),
                'current_price': _safe_float(row.get('current_price'))
            }
            lifecycle.append(event)
        
        # Determine current status
        last_row = sorted_rows[-1]
        status = _determine_status(sorted_rows)
        
        # Get latest MFE values
        mfe = _get_latest_mfe(sorted_rows)
        be_mfe = _get_latest_be_mfe(sorted_rows)
        no_be_mfe = _get_latest_no_be_mfe(sorted_rows)
        
        # Calculate R-multiple (use final_mfe if completed, else current mfe)
        r_multiple = None
        if status == 'COMPLETED':
            r_multiple = _safe_float(last_row.get('final_mfe'))
        if r_multiple is None:
            r_multiple = mfe
        
        # Calculate AE (adverse excursion) - not yet implemented in data
        ae = None  # TODO: Implement when AE tracking is added
        
        # Build unified state
        state = {
            'trade_id': first_row.get('trade_id'),
            'direction': first_row.get('direction'),
            'entry_price': _safe_float(first_row.get('entry_price')),
            'stop_loss': _safe_float(first_row.get('stop_loss')),
            'session': first_row.get('session'),
            'bias': first_row.get('bias'),
            'status': status,
            'timestamp': first_row.get('timestamp'),
            'created_at': first_row.get('created_at'),
            'mfe': mfe,
            'be_mfe': be_mfe,
            'no_be_mfe': no_be_mfe,
            'ae': ae,
            'r_multiple': r_multiple,
            'final_mfe': _safe_float(last_row.get('final_mfe')),
            'exit_price': _safe_float(last_row.get('exit_price')),
            'current_price': _safe_float(last_row.get('current_price')),
            'risk_distance': _safe_float(first_row.get('risk_distance')),
            'lifecycle': lifecycle,
            'event_count': len(sorted_rows),
            'last_event_type': last_row.get('event_type'),
            'be_triggered': _check_be_triggered(sorted_rows)
        }
        
        # Add targets if present
        if first_row.get('targets'):
            state['targets'] = first_row['targets']
        
        # Add telemetry from last row if present
        if last_row.get('telemetry'):
            state['telemetry'] = last_row['telemetry']
        
        # Add signal date/time if present
        if first_row.get('signal_date'):
            state['signal_date'] = first_row['signal_date']
        if first_row.get('signal_time'):
            state['signal_time'] = first_row['signal_time']
        
        return state
        
    except Exception as e:
        logger.error(f"Error building signal state: {e}", exc_info=True)
        return None


def _determine_status(rows: List[Dict[str, Any]]) -> str:
    """Determine current status from event sequence"""
    if not rows:
        return 'UNKNOWN'
    
    # Check last event
    last_event = rows[-1].get('event_type', '')
    
    if 'EXIT' in last_event:
        return 'COMPLETED'
    elif last_event == 'INVALIDATED':
        return 'CANCELLED'
    elif last_event == 'ENTRY' or last_event == 'SIGNAL_CREATED':
        return 'ACTIVE'
    elif last_event in ['MFE_UPDATE', 'BE_TRIGGERED']:
        return 'ACTIVE'
    
    # Check lifecycle_state if available
    lifecycle_state = rows[-1].get('lifecycle_state')
    if lifecycle_state:
        if 'COMPLETE' in lifecycle_state or 'EXIT' in lifecycle_state:
            return 'COMPLETED'
        elif 'CANCEL' in lifecycle_state or 'INVALID' in lifecycle_state:
            return 'CANCELLED'
        elif 'ACTIVE' in lifecycle_state or 'RUNNING' in lifecycle_state:
            return 'ACTIVE'
        elif 'PENDING' in lifecycle_state or 'CONFIRMED' in lifecycle_state:
            return 'PENDING'
    
    return 'ACTIVE'  # Default


def _get_latest_mfe(rows: List[Dict[str, Any]]) -> Optional[float]:
    """Get latest MFE value from rows"""
    for row in reversed(rows):
        mfe = _safe_float(row.get('mfe'))
        if mfe is not None:
            return mfe
    return None


def _get_latest_be_mfe(rows: List[Dict[str, Any]]) -> Optional[float]:
    """Get latest BE MFE value from rows"""
    for row in reversed(rows):
        be_mfe = _safe_float(row.get('be_mfe'))
        if be_mfe is not None:
            return be_mfe
    return None


def _get_latest_no_be_mfe(rows: List[Dict[str, Any]]) -> Optional[float]:
    """Get latest No BE MFE value from rows"""
    for row in reversed(rows):
        no_be_mfe = _safe_float(row.get('no_be_mfe'))
        if no_be_mfe is not None:
            return no_be_mfe
    return None


def _check_be_triggered(rows: List[Dict[str, Any]]) -> bool:
    """Check if BE was triggered in lifecycle"""
    for row in rows:
        if row.get('event_type') == 'BE_TRIGGERED':
            return True
    return False


def _safe_float(value: Any) -> Optional[float]:
    """Safely convert value to float"""
    if value is None or value == '':
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def build_multiple_signal_states(grouped_rows: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Build signal states for multiple trade_ids
    
    Args:
        grouped_rows: Dict mapping trade_id to list of rows
        
    Returns:
        List of unified signal states
    """
    states = []
    
    for trade_id, rows in grouped_rows.items():
        state = build_signal_state(rows)
        if state:
            states.append(state)
    
    return states


def filter_by_status(states: List[Dict[str, Any]], status: str) -> List[Dict[str, Any]]:
    """Filter signal states by status"""
    return [s for s in states if s.get('status') == status]


def filter_active_signals(states: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Get only active/pending signals"""
    return [s for s in states if s.get('status') in ['ACTIVE', 'PENDING', 'CONFIRMED']]


def filter_completed_signals(states: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Get only completed signals"""
    return [s for s in states if s.get('status') == 'COMPLETED']
