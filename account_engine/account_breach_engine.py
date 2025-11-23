"""Stage 13F - Account Breach Engine Implementation."""
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class AccountBreachResult:
    """Result of account-level breach evaluation for a single firm/program."""
    firm_code: str
    program_id: Optional[int]
    status: str  # "APPROVED" or "REJECTED"
    rule: Optional[str] = None
    reason: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


def _check_max_daily_loss(
    firm_code: str,
    program_id: Optional[int],
    account_metrics: Dict[str, Any],
    max_daily_loss: Optional[float],
) -> Optional[AccountBreachResult]:
    """Check if daily loss exceeds maximum allowed."""
    if max_daily_loss is None:
        return None
    
    day_pl = account_metrics.get("day_pl")
    if day_pl is None:
        return None
    
    # day_pl is PnL relative to start of day; negative = loss
    try:
        day_pl_value = float(day_pl)
    except (TypeError, ValueError):
        return None
    
    if day_pl_value >= -max_daily_loss:
        return None
    
    return AccountBreachResult(
        firm_code=firm_code,
        program_id=program_id,
        status="REJECTED",
        rule="MAX_DAILY_LOSS",
        reason=f"Daily loss {day_pl_value} exceeds max_daily_loss {max_daily_loss}.",
        details={
            "day_pl": day_pl_value,
            "max_daily_loss": max_daily_loss,
        },
    )


def _check_max_total_loss(
    firm_code: str,
    program_id: Optional[int],
    account_metrics: Dict[str, Any],
    max_total_loss: Optional[float],
) -> Optional[AccountBreachResult]:
    """Check if total loss exceeds maximum allowed."""
    if max_total_loss is None:
        return None
    
    total_pl = account_metrics.get("total_pl")
    if total_pl is None:
        return None
    
    try:
        total_pl_value = float(total_pl)
    except (TypeError, ValueError):
        return None
    
    if total_pl_value >= -max_total_loss:
        return None
    
    return AccountBreachResult(
        firm_code=firm_code,
        program_id=program_id,
        status="REJECTED",
        rule="MAX_TOTAL_LOSS",
        reason=f"Total loss {total_pl_value} exceeds max_total_loss {max_total_loss}.",
        details={
            "total_pl": total_pl_value,
            "max_total_loss": max_total_loss,
        },
    )


def _check_max_drawdown(
    firm_code: str,
    program_id: Optional[int],
    account_metrics: Dict[str, Any],
    max_drawdown: Optional[float],
) -> Optional[AccountBreachResult]:
    """Check if drawdown exceeds maximum allowed."""
    if max_drawdown is None:
        return None
    
    drawdown = account_metrics.get("drawdown")
    if drawdown is None:
        return None
    
    try:
        dd_value = float(drawdown)
    except (TypeError, ValueError):
        return None
    
    if dd_value >= -max_drawdown:
        return None
    
    return AccountBreachResult(
        firm_code=firm_code,
        program_id=program_id,
        status="REJECTED",
        rule="MAX_DRAWDOWN",
        reason=f"Drawdown {dd_value} exceeds max_drawdown {max_drawdown}.",
        details={
            "drawdown": dd_value,
            "max_drawdown": max_drawdown,
        },
    )


def evaluate_account_breach(
    firm_code: str,
    program_id: Optional[int],
    account_metrics: Dict[str, Any],
    breach_rules: Dict[str, Any],
) -> AccountBreachResult:
    """Evaluate account breach rules for a single firm/program.
    
    account_metrics:
        {"day_pl": float or str,
         "total_pl": float or str,
         "drawdown": float or str,
         ... (optional extensions)}
    
    breach_rules:
        {"max_daily_loss": float or None,
         "max_total_loss": float or None,
         "max_drawdown": float or None,}
    
    If no rules are configured or metrics missing, returns APPROVED with
    a details.reason explaining why enforcement is effectively disabled.
    """
    max_daily_loss = breach_rules.get("max_daily_loss")
    max_total_loss = breach_rules.get("max_total_loss")
    max_drawdown = breach_rules.get("max_drawdown")
    
    # 1) Max daily loss
    result = _check_max_daily_loss(firm_code, program_id, account_metrics, max_daily_loss)
    if result is not None:
        return result
    
    # 2) Max total loss
    result = _check_max_total_loss(firm_code, program_id, account_metrics, max_total_loss)
    if result is not None:
        return result
    
    # 3) Max drawdown
    result = _check_max_drawdown(firm_code, program_id, account_metrics, max_drawdown)
    if result is not None:
        return result
    
    # If no rules or no metrics triggered, approve
    return AccountBreachResult(
        firm_code=firm_code,
        program_id=program_id,
        status="APPROVED",
        rule=None,
        reason=None,
        details=None,
    )



def check_order_enforcement(
    firm_code: str,
    program_id: int,
    program_metadata: Dict[str, Any],
    account_state: Dict[str, Any],
    order_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Stage 13H:
    Comprehensive order enforcement checks before routing.
    
    Performs all enforcement validations in sequence:
    1. Paused check
    2. Session validation
    3. Max contracts validation
    4. Risk-per-trade validation
    5. Daily loss validation
    6. Trailing drawdown validation
    
    Args:
        firm_code: Firm identifier
        program_id: Program identifier
        program_metadata: Unified program metadata dict
        account_state: Current account state dict
        order_data: Order details (entry_price, stop_loss, contracts, session)
    
    Returns:
        {
            "allowed": True/False,
            "reason": "string",
            "breach_type": "paused | session | contracts | risk | daily_loss | drawdown"
        }
    
    Never raises - returns blocked result on any error.
    """
    try:
        # 1. Paused check
        if account_state.get("paused") is True:
            return {
                "allowed": False,
                "reason": f"Account {firm_code}/{program_id} is paused",
                "breach_type": "paused"
            }
        
        # 2. Session validation
        session = order_data.get("session")
        allowed_sessions = program_metadata.get("allowed_sessions")
        if allowed_sessions is not None and session is not None:
            if session not in allowed_sessions:
                return {
                    "allowed": False,
                    "reason": f"Session '{session}' not in allowed sessions {allowed_sessions}",
                    "breach_type": "session"
                }
        
        # 3. Max contracts validation
        contracts = order_data.get("contracts")
        max_contracts = program_metadata.get("max_contracts")
        if max_contracts is not None and contracts is not None:
            if contracts > max_contracts:
                return {
                    "allowed": False,
                    "reason": f"Contracts {contracts} exceeds max_contracts {max_contracts}",
                    "breach_type": "contracts"
                }
        
        # 4. Risk-per-trade validation
        entry_price = order_data.get("entry_price")
        stop_loss = order_data.get("stop_loss")
        max_risk_pct = program_metadata.get("max_risk_per_trade_pct")
        equity = account_state.get("equity")
        
        if (max_risk_pct is not None and entry_price is not None and 
            stop_loss is not None and contracts is not None and equity is not None):
            
            # Assume tick_value = 5.0 for NQ (could be made configurable)
            tick_value = 5.0
            risk_value = abs(float(entry_price) - float(stop_loss)) * tick_value * int(contracts)
            allowed_risk = float(equity) * float(max_risk_pct)
            
            if risk_value > allowed_risk:
                return {
                    "allowed": False,
                    "reason": f"Risk value ${risk_value:.2f} exceeds allowed risk ${allowed_risk:.2f} ({max_risk_pct*100:.1f}% of equity)",
                    "breach_type": "risk"
                }
        
        # 5. Daily loss validation
        daily_loss_limit = program_metadata.get("daily_loss_limit")
        starting_balance = account_state.get("starting_balance")
        
        if daily_loss_limit is not None and equity is not None and starting_balance is not None:
            min_allowed_equity = float(starting_balance) - float(daily_loss_limit)
            if float(equity) <= min_allowed_equity:
                return {
                    "allowed": False,
                    "reason": f"Equity ${equity:.2f} at/below daily loss limit (${starting_balance:.2f} - ${daily_loss_limit:.2f} = ${min_allowed_equity:.2f})",
                    "breach_type": "daily_loss"
                }
        
        # 6. Trailing drawdown validation
        max_drawdown = program_metadata.get("max_drawdown")
        peak_equity = account_state.get("peak_equity")
        
        if max_drawdown is not None and equity is not None and peak_equity is not None:
            min_allowed_equity = float(peak_equity) - float(max_drawdown)
            if float(equity) <= min_allowed_equity:
                return {
                    "allowed": False,
                    "reason": f"Equity ${equity:.2f} at/below drawdown limit (${peak_equity:.2f} - ${max_drawdown:.2f} = ${min_allowed_equity:.2f})",
                    "breach_type": "drawdown"
                }
        
        # All checks passed
        return {
            "allowed": True,
            "reason": "All enforcement checks passed",
            "breach_type": None
        }
        
    except Exception as e:
        # Any error blocks the order for safety
        return {
            "allowed": False,
            "reason": f"Enforcement check error: {str(e)}",
            "breach_type": "error"
        }
