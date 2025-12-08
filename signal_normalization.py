"""
Signal Normalization Layer (Phase 2A)
Pure transformation layer for TradingView webhook payloads
NO DATABASE WRITES - transformation only
"""

from datetime import datetime
from typing import Dict, Any, Optional
import pytz
import logging

logger = logging.getLogger(__name__)

# Session mapping constants
SESSION_MAPPINGS = {
    'ASIA': 'ASIA',
    'LONDON': 'LONDON', 
    'NY PRE': 'NY_PRE',
    'NY_PRE': 'NY_PRE',
    'NY AM': 'NY_AM',
    'NY_AM': 'NY_AM',
    'NY LUNCH': 'NY_LUNCH',
    'NY_LUNCH': 'NY_LUNCH',
    'NY PM': 'NY_PM',
    'NY_PM': 'NY_PM'
}

# Event type mappings
EVENT_TYPE_MAPPINGS = {
    'ENTRY': 'ACTIVE',
    'SIGNAL_CREATED': 'ACTIVE',
    'MFE_UPDATE': 'LIFECYCLE_EVENT',
    'BE_TRIGGERED': 'LIFECYCLE_EVENT',
    'EXIT_SL': 'COMPLETED',
    'EXIT_TARGET': 'COMPLETED',
    'INVALIDATED': 'CANCELLED'
}


def normalize_signal_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize TradingView webhook payload to standardized format
    
    Args:
        payload: Raw webhook payload from TradingView
        
    Returns:
        Normalized payload with standardized fields
        
    Raises:
        ValueError: If required fields are missing or invalid
    """
    try:
        # Store raw payload for traceability
        normalized = {
            'raw_payload': payload.copy(),
            'normalized_at': datetime.now(pytz.UTC).isoformat()
        }
        
        # Normalize direction
        direction = payload.get('direction', payload.get('type', '')).upper()
        if 'BULL' in direction or direction == 'LONG':
            normalized['direction'] = 'LONG'
        elif 'BEAR' in direction or direction == 'SHORT':
            normalized['direction'] = 'SHORT'
        else:
            # Default to raw value if can't determine
            normalized['direction'] = direction
        
        # Normalize numeric fields (convert strings to floats)
        normalized['entry_price'] = _safe_float(payload.get('entry_price', payload.get('price')))
        normalized['stop_loss'] = _safe_float(payload.get('stop_loss', payload.get('stop_price')))
        normalized['current_price'] = _safe_float(payload.get('current_price'))
        normalized['exit_price'] = _safe_float(payload.get('exit_price'))
        
        # Validate required fields
        if normalized['entry_price'] is None:
            logger.warning("Missing entry_price in payload")
        if normalized['stop_loss'] is None:
            logger.warning("Missing stop_loss in payload")
        
        # Normalize session
        raw_session = payload.get('session', '')
        normalized['session'] = _normalize_session(raw_session)
        
        # Normalize event type
        raw_event_type = payload.get('event_type', 'ENTRY')
        normalized['event_type'] = raw_event_type  # Keep original
        normalized['status'] = EVENT_TYPE_MAPPINGS.get(raw_event_type, 'ACTIVE')
        
        # Normalize timestamp
        normalized['timestamp'] = _normalize_timestamp(payload.get('timestamp'))
        
        # Pass through other fields
        normalized['trade_id'] = payload.get('trade_id', '')
        normalized['bias'] = payload.get('bias', '')
        
        # Local MFE / MAE from TradingView
        mfe_R = payload.get("mfe_R")
        mae_R = payload.get("mae_R")
        
        # Global MAE (maximum adverse excursion over the life of the trade, in R)
        # Support both mae_global_R and mae_R_global, and be robust to missing/invalid values.
        mae_global_R = payload.get("mae_global_R")
        if mae_global_R is None:
            mae_global_R = payload.get("mae_R_global")
        if mae_global_R is not None:
            try:
                mae_global_R = float(mae_global_R)
            except Exception:
                mae_global_R = None
        
        # Convert to floats using safe conversion
        mfe_r = _safe_float(mfe_R)
        mae_r = _safe_float(mae_R)
        
        normalized['be_mfe'] = mfe_r
        normalized['no_be_mfe'] = mae_r
        normalized['mae_global_R'] = mae_global_R
        logger.info(f"[NORMALIZER] MFE be={mfe_r}, no_be={mae_r}, mae_global={mae_global_R}")
        
        # Legacy mfe field for backward compatibility
        normalized['mfe'] = _safe_float(payload.get('mfe')) or mfe_r
        normalized['final_mfe'] = _safe_float(payload.get('final_mfe')) or _safe_float(payload.get('final_mfe_R')) or mfe_r
        
        # Calculate risk_distance if not provided (from entry_price and stop_loss)
        risk_distance = _safe_float(payload.get('risk_distance'))
        if not risk_distance:
            entry_price = _safe_float(normalized.get('entry_price'))
            stop_loss = _safe_float(normalized.get('stop_loss'))
            if entry_price and stop_loss:
                risk_distance = abs(entry_price - stop_loss)
        normalized['risk_distance'] = risk_distance
        
        # Pass through target fields
        for target in ['target_1r', 'target_2r', 'target_3r', 'target_5r', 'target_10r', 'target_20r']:
            normalized[target] = _safe_float(payload.get(target))
        
        # Pass through account/risk fields
        normalized['account_size'] = _safe_float(payload.get('account_size'))
        normalized['risk_percent'] = _safe_float(payload.get('risk_percent'))
        normalized['contracts'] = _safe_int(payload.get('contracts'))
        normalized['risk_amount'] = _safe_float(payload.get('risk_amount'))
        
        # Pass through telemetry if present
        if 'telemetry' in payload:
            normalized['telemetry'] = payload['telemetry']
        
        # Pass through targets JSONB if present
        if 'targets' in payload:
            normalized['targets'] = payload['targets']
        
        # Pass through lifecycle fields
        normalized['lifecycle_state'] = payload.get('lifecycle_state')
        normalized['lifecycle_seq'] = _safe_int(payload.get('lifecycle_seq'))
        
        logger.info(f"Normalized payload: event={raw_event_type}, direction={normalized['direction']}, session={normalized['session']}")
        
        return normalized
        
    except Exception as e:
        logger.error(f"Normalization error: {e}", exc_info=True)
        # Return payload with error flag
        return {
            'raw_payload': payload.copy(),
            'normalized_at': datetime.now(pytz.UTC).isoformat(),
            'normalization_error': str(e),
            'normalization_failed': True
        }


def _safe_float(value: Any) -> Optional[float]:
    """Safely convert value to float"""
    if value is None or value == '':
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _safe_int(value: Any) -> Optional[int]:
    """Safely convert value to int"""
    if value is None or value == '':
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _normalize_session(session: str) -> str:
    """Normalize session name to standard format"""
    if not session:
        return ''
    
    session_upper = session.upper().strip()
    return SESSION_MAPPINGS.get(session_upper, session)


def _normalize_timestamp(timestamp: Any) -> Optional[int]:
    """
    Normalize timestamp to consistent format (Unix timestamp in milliseconds)
    
    Args:
        timestamp: Can be int, float, string ISO format, or None
        
    Returns:
        Unix timestamp in milliseconds or None
    """
    if timestamp is None:
        return None
    
    try:
        # If already a number, assume it's Unix timestamp
        if isinstance(timestamp, (int, float)):
            # If it looks like seconds (< year 3000 in seconds), convert to ms
            if timestamp < 32503680000:  # Jan 1, 3000 in seconds
                return int(timestamp * 1000)
            return int(timestamp)
        
        # If string, try to parse as ISO format
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return int(dt.timestamp() * 1000)
        
        return None
        
    except Exception as e:
        logger.warning(f"Could not normalize timestamp {timestamp}: {e}")
        return None


def validate_normalized_payload(normalized: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate that normalized payload has required fields
    
    Returns:
        (is_valid, error_message)
    """
    if normalized.get('normalization_failed'):
        return False, normalized.get('normalization_error', 'Normalization failed')
    
    # Check required fields
    if not normalized.get('direction'):
        return False, "Missing direction"
    
    if not normalized.get('event_type'):
        return False, "Missing event_type"
    
    # Entry events must have entry_price and stop_loss
    if normalized.get('event_type') == 'ENTRY':
        if normalized.get('entry_price') is None:
            return False, "ENTRY event missing entry_price"
        if normalized.get('stop_loss') is None:
            return False, "ENTRY event missing stop_loss"
    
    return True, None
