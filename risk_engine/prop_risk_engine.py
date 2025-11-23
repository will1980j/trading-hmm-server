"""Stage 13D - Prop Firm Risk Engine Implementation."""
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class RiskCheckResult:
    """Result of a risk check for a single firm and task."""
    firm_code: str
    status: str  # "APPROVED" or "REJECTED"
    rule: Optional[str] = None
    reason: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


def _check_max_contracts(
    firm_code: str,
    quantity: Optional[int],
    max_contracts: Optional[int],
) -> Optional[RiskCheckResult]:
    """Check if quantity exceeds max_contracts rule."""
    if max_contracts is None or quantity is None:
        return None
    
    if quantity <= max_contracts:
        return None
    
    return RiskCheckResult(
        firm_code=firm_code,
        status="REJECTED",
        rule="MAX_CONTRACTS",
        reason=f"Requested quantity {quantity} exceeds max_contracts {max_contracts} for firm {firm_code}.",
        details={
            "quantity": quantity,
            "max_contracts": max_contracts,
        },
    )


def _check_allowed_sessions(
    firm_code: str,
    session: Optional[str],
    allowed_sessions: Optional[list],
) -> Optional[RiskCheckResult]:
    """Check if session is in allowed_sessions list."""
    if not allowed_sessions:
        return None
    
    if session is None:
        return None
    
    if session in allowed_sessions:
        return None
    
    return RiskCheckResult(
        firm_code=firm_code,
        status="REJECTED",
        rule="ALLOWED_SESSIONS",
        reason=f"Session '{session}' is not allowed for firm {firm_code}.",
        details={
            "session": session,
            "allowed_sessions": allowed_sessions,
        },
    )


def _compute_stop_distance_points(
    direction: Optional[str],
    entry_price: Optional[float],
    stop_loss: Optional[float],
) -> Optional[float]:
    """Compute stop distance in points based on direction."""
    if direction is None or entry_price is None or stop_loss is None:
        return None
    
    try:
        direction_upper = direction.upper()
    except AttributeError:
        direction_upper = str(direction)
    
    if direction_upper == "LONG":
        return entry_price - stop_loss
    
    if direction_upper == "SHORT":
        return stop_loss - entry_price
    
    return None


def _check_min_stop_distance(
    firm_code: str,
    direction: Optional[str],
    entry_price: Optional[float],
    stop_loss: Optional[float],
    min_stop_distance_points: Optional[float],
) -> Optional[RiskCheckResult]:
    """Check if stop distance meets minimum requirement."""
    if min_stop_distance_points is None:
        return None
    
    distance = _compute_stop_distance_points(direction, entry_price, stop_loss)
    if distance is None:
        return None
    
    if distance >= min_stop_distance_points:
        return None
    
    return RiskCheckResult(
        firm_code=firm_code,
        status="REJECTED",
        rule="MIN_STOP_DISTANCE_POINTS",
        reason=(
            f"Stop distance {distance:.2f} is less than "
            f"min_stop_distance_points {min_stop_distance_points:.2f} for firm {firm_code}."
        ),
        details={
            "direction": direction,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "distance": distance,
            "min_stop_distance_points": min_stop_distance_points,
        },
    )


def evaluate_task_risk(
    firm_code: str,
    task_payload: Dict[str, Any],
    routing_meta: Dict[str, Any],
    firm_config: Dict[str, Any],
    firm_risk_rules: Dict[str, Any],
) -> RiskCheckResult:
    """Evaluate a single task for a single firm against configured risk rules.
    
    Returns:
        RiskCheckResult with status:
        - "APPROVED" if no rules are violated
        - "REJECTED" with rule/reason if any rule fails
    """
    # Extract normalized fields
    quantity = routing_meta.get("quantity")
    try:
        if quantity is not None:
            quantity = int(quantity)
    except (TypeError, ValueError):
        quantity = None
    
    session = task_payload.get("session")
    direction = task_payload.get("direction")
    entry_price = task_payload.get("entry_price")
    stop_loss = task_payload.get("stop_loss")
    
    max_contracts = firm_risk_rules.get("max_contracts")
    min_stop_distance_points = firm_risk_rules.get("min_stop_distance_points")
    allowed_sessions = firm_risk_rules.get("allowed_sessions")
    
    # 1) Max contracts rule
    result = _check_max_contracts(firm_code, quantity, max_contracts)
    if result is not None:
        return result
    
    # 2) Allowed sessions rule
    result = _check_allowed_sessions(firm_code, session, allowed_sessions)
    if result is not None:
        return result
    
    # 3) Minimum stop distance rule
    result = _check_min_stop_distance(
        firm_code,
        direction,
        entry_price,
        stop_loss,
        min_stop_distance_points,
    )
    if result is not None:
        return result
    
    # If we reach here, all active rules passed
    return RiskCheckResult(
        firm_code=firm_code,
        status="APPROVED",
        rule=None,
        reason=None,
        details=None,
    )
