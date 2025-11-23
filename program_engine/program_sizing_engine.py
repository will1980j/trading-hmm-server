"""Stage 13E - Program Sizing Engine Implementation."""
from dataclasses import dataclass
from typing import Any, Dict, Optional
import math


@dataclass
class SizingResult:
    """Result of program-aware auto-sizing."""
    firm_code: str
    program_id: Optional[int]
    status: str  # "APPROVED" or "REJECTED"
    rule: Optional[str] = None
    reason: Optional[str] = None
    computed_quantity: Optional[int] = None
    details: Optional[Dict[str, Any]] = None


def compute_contract_size_for_program(
    *,
    firm_code: str,
    program: Dict[str, Any],
    scaling_rules: Dict[str, Any],
    entry_price: Optional[float],
    stop_loss: Optional[float],
    user_quantity: Optional[int],
    risk_percent: Optional[float],
) -> SizingResult:
    """Stage 13E:
    Determine the correct contract quantity based on:
    - program account size
    - risk_percent (if provided)
    - stop distance
    - min/max constraints from program + scaling rules
    
    If user manually provides quantity AND it is safe, approve it.
    If auto-size is needed, compute quantity.
    If quantity violates rules, reject it.
    
    program dict MUST contain:
    - account_size (float)
    
    scaling_rules may contain:
    - max_contracts
    - min_contracts
    - max_risk_percent
    
    Always return SizingResult.
    """
    # Extract core values
    try:
        account_size = float(program.get("account_size"))
    except Exception:
        account_size = None
    
    # If we cannot determine account size, APPROVE user's quantity
    if account_size is None:
        return SizingResult(
            firm_code=firm_code,
            program_id=program.get("id"),
            status="APPROVED",
            computed_quantity=user_quantity,
            details={"reason": "Missing account_size; auto-sizing skipped"},
        )
    
    # Compute stop distance
    stop_distance = None
    if entry_price is not None and stop_loss is not None:
        if program.get("direction", "").upper() == "LONG":
            stop_distance = entry_price - stop_loss
        elif program.get("direction", "").upper() == "SHORT":
            stop_distance = stop_loss - entry_price
        else:
            # fallback for programs that do not include direction
            try:
                stop_distance = abs(entry_price - stop_loss)
            except Exception:
                stop_distance = None
    
    # Risk percent override rules
    max_risk_percent = scaling_rules.get("max_risk_percent")
    if risk_percent is not None and max_risk_percent is not None:
        if risk_percent > max_risk_percent:
            return SizingResult(
                firm_code=firm_code,
                program_id=program.get("id"),
                status="REJECTED",
                rule="MAX_RISK_PERCENT",
                reason=f"risk_percent {risk_percent} exceeds max_risk_percent {max_risk_percent}.",
            )
    
    # If user provided quantity AND stop_distance is usable, check min/max constraints
    if user_quantity is not None:
        max_contracts = scaling_rules.get("max_contracts")
        min_contracts = scaling_rules.get("min_contracts")
        
        if max_contracts is not None and user_quantity > max_contracts:
            return SizingResult(
                firm_code=firm_code,
                program_id=program.get("id"),
                status="REJECTED",
                rule="MAX_CONTRACTS",
                reason=f"User quantity {user_quantity} exceeds max_contracts {max_contracts}.",
            )
        
        if min_contracts is not None and user_quantity < min_contracts:
            return SizingResult(
                firm_code=firm_code,
                program_id=program.get("id"),
                status="REJECTED",
                rule="MIN_CONTRACTS",
                reason=f"User quantity {user_quantity} is below min_contracts {min_contracts}.",
            )
        
        return SizingResult(
            firm_code=firm_code,
            program_id=program.get("id"),
            status="APPROVED",
            computed_quantity=user_quantity,
            details={"reason": "User quantity approved"},
        )
    
    # AUTO-SIZING: Only if user did not supply quantity
    if risk_percent is None or stop_distance is None or stop_distance <= 0:
        # Cannot compute auto-size; approve zero or missing quantity
        return SizingResult(
            firm_code=firm_code,
            program_id=program.get("id"),
            status="APPROVED",
            computed_quantity=user_quantity,
            details={"reason": "Insufficient data for auto-sizing"},
        )
    
    # contracts = floor( (account_size * risk_percent) / (stop_distance * contract_value) )
    # For NQ, assume $2 per point unless scaling_rules provide a multiplier
    multiplier = scaling_rules.get("point_value") or 2.0
    
    try:
        raw_contracts = (account_size * risk_percent) / (stop_distance * multiplier)
        quantity = int(math.floor(raw_contracts))
    except Exception:
        quantity = None
    
    if quantity is None or quantity <= 0:
        return SizingResult(
            firm_code=firm_code,
            program_id=program.get("id"),
            status="REJECTED",
            rule="AUTO_SIZE_INVALID",
            reason="Auto-sized quantity <= 0 or invalid.",
        )
    
    max_contracts = scaling_rules.get("max_contracts")
    if max_contracts is not None and quantity > max_contracts:
        quantity = max_contracts
    
    min_contracts = scaling_rules.get("min_contracts")
    if min_contracts is not None and quantity < min_contracts:
        return SizingResult(
            firm_code=firm_code,
            program_id=program.get("id"),
            status="REJECTED",
            rule="AUTO_SIZE_TOO_SMALL",
            reason=f"Auto-sized quantity {quantity} below min_contracts {min_contracts}.",
        )
    
    return SizingResult(
        firm_code=firm_code,
        program_id=program.get("id"),
        status="APPROVED",
        computed_quantity=quantity,
        details={
            "account_size": account_size,
            "risk_percent": risk_percent,
            "stop_distance": stop_distance,
            "multiplier": multiplier,
        },
    )
