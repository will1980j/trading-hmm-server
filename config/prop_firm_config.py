"""Prop firm configuration loader."""
import os
from typing import Any, Dict, List, Optional, Tuple, Union


def _env_bool(key: str, default: bool = False) -> bool:
    """Parse environment variable as boolean."""
    value = os.getenv(key, str(default)).lower()
    return value in ('1', 'true', 'yes', 'on')


def _env_int(name: str, default: Optional[int] = None) -> Optional[int]:
    """Parse environment variable as integer."""
    value = os.getenv(name)
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _env_float(name: str, default: Optional[float] = None) -> Optional[float]:
    """Parse environment variable as float."""
    value = os.getenv(name)
    if value is None or value == "":
        return default
    try:
        return float(value)
    except ValueError:
        return default


def get_firm_config(firm_code: str) -> Dict[str, Any]:
    """Get configuration for a specific prop firm.
    
    Never raises exceptions - returns disabled config if missing.
    """
    try:
        if firm_code == "FTMO":
            return {
                'enabled': _env_bool('FTMO_ENABLED', False),
                'api_key': os.getenv('FTMO_API_KEY'),
                'base_url': os.getenv('FTMO_BASE_URL'),
                'supported_symbols': ['NQ', 'ES', 'YM', 'RTY'],
                'max_position_size': 10,
                'timeout': 30
            }
        elif firm_code == "APEX":
            return {
                'enabled': _env_bool('APEX_ENABLED', False),
                'api_key': os.getenv('APEX_API_KEY'),
                'base_url': os.getenv('APEX_BASE_URL'),
                'supported_symbols': ['NQ', 'ES', 'YM', 'RTY'],
                'max_position_size': 10,
                'timeout': 30
            }
        else:
            return {
                'enabled': False,
                'error': f'Unknown firm code: {firm_code}'
            }
    except Exception:
        return {
            'enabled': False,
            'error': f'Configuration error for {firm_code}'
        }


def get_routing_rules_for_task(payload: Dict[str, Any]) -> Tuple[List[str], Dict[str, Any]]:
    """Get routing rules for a task payload.
    
    Returns:
        Tuple of (firm_codes, routing_metadata)
    """
    try:
        firm_codes = payload.get('firm_codes', [])
        
        if not firm_codes:
            potential_firms = ['FTMO', 'APEX']
            firm_codes = []
            
            for firm in potential_firms:
                config = get_firm_config(firm)
                if config.get('enabled', False):
                    firm_codes.append(firm)
        
        routing_meta = {
            'program_ids': payload.get('program_ids', []),
            'quantity': payload.get('quantity', 1),
            'risk_percent': payload.get('risk_percent', 0.01),
            'symbol': payload.get('symbol', 'NQ'),
            'session': payload.get('session', 'NY AM'),
            'bias': payload.get('bias', payload.get('direction', 'LONG'))
        }
        
        return firm_codes, routing_meta
    
    except Exception:
        return [], {}


def get_firm_risk_rules(firm_code: str) -> Dict[str, Any]:
    """Stage 13D: Return per-firm risk rule configuration.
    
    All values are optional. If a value is None, that rule is considered
    disabled and will not be enforced.
    
    Rules:
        max_contracts: maximum allowed quantity per order
        min_stop_distance_points: minimum stop distance in points
        allowed_sessions: list of allowed session strings (e.g. "NY AM")
    
    All values come from environment variables, with safe defaults.
    """
    code = (firm_code or "").upper()
    
    if code == "FTMO":
        return {
            "max_contracts": _env_int("FTMO_MAX_CONTRACTS"),
            "min_stop_distance_points": _env_float("FTMO_MIN_STOP_DISTANCE_POINTS"),
            "allowed_sessions": (
                os.getenv("FTMO_ALLOWED_SESSIONS") or 
                "ASIA,LONDON,NY PRE,NY AM,NY LUNCH,NY PM"
            ).split(","),
        }
    
    if code == "APEX":
        return {
            "max_contracts": _env_int("APEX_MAX_CONTRACTS"),
            "min_stop_distance_points": _env_float("APEX_MIN_STOP_DISTANCE_POINTS"),
            "allowed_sessions": (
                os.getenv("APEX_ALLOWED_SESSIONS") or 
                "ASIA,LONDON,NY PRE,NY AM,NY LUNCH,NY PM"
            ).split(","),
        }
    
    # Unknown firm: no rules enforced
    return {
        "max_contracts": None,
        "min_stop_distance_points": None,
        "allowed_sessions": None,
    }


def get_program_scaling_rules(firm_code: str, program_id: int) -> Dict[str, Any]:
    """Stage 13E:
    Load program-level scaling rules from environment variables.
    
    Rules are optional and disabled if missing.
    """
    return {
        "max_contracts": _env_int(f"{firm_code.upper()}_{program_id}_MAX_CONTRACTS"),
        "min_contracts": _env_int(f"{firm_code.upper()}_{program_id}_MIN_CONTRACTS"),
        "max_risk_percent": _env_float(f"{firm_code.upper()}_{program_id}_MAX_RISK_PERCENT"),
        "point_value": _env_float(f"{firm_code.upper()}_{program_id}_POINT_VALUE"),
    }


def get_account_breach_rules(firm_code: str, program_id: int) -> Dict[str, Any]:
    """Stage 13F:
    Load account-level breach rules for a given firm and program.
    
    Values are optional; if None, that rule is disabled.
    
    Env variables example:
        FTMO_1_MAX_DAILY_LOSS
        FTMO_1_MAX_TOTAL_LOSS
        FTMO_1_MAX_DRAWDOWN
    """
    prefix = f"{firm_code.upper()}_{program_id}_"
    return {
        "max_daily_loss": _env_float(prefix + "MAX_DAILY_LOSS"),
        "max_total_loss": _env_float(prefix + "MAX_TOTAL_LOSS"),
        "max_drawdown": _env_float(prefix + "MAX_DRAWDOWN"),
    }


def get_unified_program_metadata(
    firm_code: str,
    program_id: int,
    db_conn=None,
) -> Dict[str, Any]:
    """Stage 13H:
    Assemble unified program metadata from multiple sources.
    
    Sources (in priority order):
    1. Environment variables (highest priority)
    2. Database prop_firms table (fallback)
    3. Safe defaults (if nothing available)
    
    Returns unified dict with:
        daily_loss_limit: float
        max_drawdown: float
        max_contracts: int
        max_risk_per_trade_pct: float
        allowed_sessions: list[str]
    
    Never raises - returns safe defaults if data unavailable.
    """
    metadata = {}
    
    # 1. Try database first (if connection provided)
    if db_conn is not None:
        try:
            from psycopg2.extras import RealDictCursor
            cur = db_conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(
                """
                SELECT daily_loss_limit, max_drawdown, contract_cap
                FROM prop_firms
                WHERE UPPER(name) = UPPER(%s)
                LIMIT 1
                """,
                (firm_code,)
            )
            row = cur.fetchone()
            if row:
                metadata["daily_loss_limit"] = float(row["daily_loss_limit"]) if row.get("daily_loss_limit") else None
                metadata["max_drawdown"] = float(row["max_drawdown"]) if row.get("max_drawdown") else None
                metadata["max_contracts"] = int(row["contract_cap"]) if row.get("contract_cap") else None
        except Exception:
            pass  # Graceful fallback to env
    
    # 2. Environment variables override database
    prefix_firm = f"{firm_code.upper()}_"
    prefix_program = f"{firm_code.upper()}_{program_id}_"
    
    # Daily loss limit (program-level override, then firm-level)
    daily_loss = _env_float(prefix_program + "DAILY_LOSS_LIMIT")
    if daily_loss is None:
        daily_loss = _env_float(prefix_firm + "DAILY_LOSS_LIMIT")
    if daily_loss is not None:
        metadata["daily_loss_limit"] = daily_loss
    
    # Max drawdown (program-level override, then firm-level)
    max_dd = _env_float(prefix_program + "MAX_DRAWDOWN")
    if max_dd is None:
        max_dd = _env_float(prefix_firm + "MAX_DRAWDOWN")
    if max_dd is not None:
        metadata["max_drawdown"] = max_dd
    
    # Max contracts (program-level override, then firm-level)
    max_contracts = _env_int(prefix_program + "MAX_CONTRACTS")
    if max_contracts is None:
        max_contracts = _env_int(prefix_firm + "MAX_CONTRACTS")
    if max_contracts is not None:
        metadata["max_contracts"] = max_contracts
    
    # Max risk per trade percent (program-level only)
    max_risk_pct = _env_float(prefix_program + "MAX_RISK_PERCENT")
    if max_risk_pct is not None:
        metadata["max_risk_per_trade_pct"] = max_risk_pct
    
    # Allowed sessions (firm-level only, split by comma and trim)
    allowed_sessions_str = os.getenv(prefix_firm + "ALLOWED_SESSIONS")
    if allowed_sessions_str:
        metadata["allowed_sessions"] = [s.strip() for s in allowed_sessions_str.split(",") if s.strip()]
    
    # 3. Safe defaults for missing values
    if "daily_loss_limit" not in metadata:
        metadata["daily_loss_limit"] = None
    if "max_drawdown" not in metadata:
        metadata["max_drawdown"] = None
    if "max_contracts" not in metadata:
        metadata["max_contracts"] = None
    if "max_risk_per_trade_pct" not in metadata:
        metadata["max_risk_per_trade_pct"] = None
    if "allowed_sessions" not in metadata:
        metadata["allowed_sessions"] = None
    
    return metadata
