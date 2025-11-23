"""
Stage 13G - Account State Manager

Centralized in-memory store for account metrics per (firm_code, program_id).
Maintains account state and provides safe environment variable fallback.
Never fabricates data - returns empty dict if no data available.
"""

import os
import time
from threading import Lock
from typing import Any, Dict, Tuple


class AccountStateManager:
    """
    Stage 13G - Central in-memory store for account metrics.
    
    Stores account state keyed by (firm_code, program_id). Metrics are
    intended to represent real account values coming from upstream systems
    or environment variables. This manager never fabricates values; if no
    data is available, it returns an empty dict.
    """
    
    def __init__(self) -> None:
        self._state: Dict[Tuple[str, int], Dict[str, Any]] = {}
        self._lock = Lock()
    
    def _make_key(self, firm_code: str, program_id: int) -> Tuple[str, int]:
        return (str(firm_code or "").upper(), int(program_id))
    
    def update_account_state(
        self,
        firm_code: str,
        program_id: int,
        metrics: Dict[str, Any],
    ) -> None:
        """
        Merge the provided metrics into existing state for this firm/program.
        
        If metrics do not contain a 'last_update' field, one is added based
        on the current time.
        """
        if metrics is None:
            return
        
        key = self._make_key(firm_code, program_id)
        with self._lock:
            existing = self._state.get(key, {})
            merged = dict(existing)
            merged.update(metrics)
            if "last_update" not in merged:
                merged["last_update"] = time.time()
            self._state[key] = merged
    
    def get_account_state(
        self,
        firm_code: str,
        program_id: int,
    ) -> Dict[str, Any]:
        """
        Return a shallow copy of the current metrics for this firm/program.
        
        If no state exists, returns {}. This method never raises.
        """
        key = self._make_key(firm_code, program_id)
        with self._lock:
            data = self._state.get(key)
            return dict(data) if data else {}
    
    def load_from_env(
        self,
        firm_code: str,
        program_id: int,
    ) -> Dict[str, Any]:
        """
        Load account metrics for a given firm/program from environment variables.
        
        Expected optional variables (per firm/program):
            {FIRM}_{PROGRAM}_EQUITY
            {FIRM}_{PROGRAM}_BALANCE
            {FIRM}_{PROGRAM}_DAY_PL
            {FIRM}_{PROGRAM}_TOTAL_PL
            {FIRM}_{PROGRAM}_DRAWDOWN
        
        All values are optional. Only non-empty, parseable float values are used.
        If no usable values are found, returns {} and does not update state.
        """
        prefix = f"{str(firm_code or '').upper()}_{int(program_id)}_"
        
        def _env_float(name: str):
            value = os.getenv(prefix + name)
            if value is None or value == "":
                return None
            try:
                return float(value)
            except (TypeError, ValueError):
                return None
        
        metrics = {
            "equity": _env_float("EQUITY"),
            "balance": _env_float("BALANCE"),
            "day_pl": _env_float("DAY_PL"),
            "total_pl": _env_float("TOTAL_PL"),
            "drawdown": _env_float("DRAWDOWN"),
        }
        
        # Remove keys with None values
        metrics = {k: v for k, v in metrics.items() if v is not None}
        
        if not metrics:
            return {}
        
        metrics["source"] = "ENV"
        metrics["last_update"] = time.time()
        self.update_account_state(firm_code, program_id, metrics)
        return metrics

    
    def update_flag(
        self,
        firm_code: str,
        program_id: int,
        key: str,
        value: Any,
    ) -> None:
        """Stage 13H:
        Safely update a single flag/field in the account state.
        
        Args:
            firm_code: Firm identifier
            program_id: Program identifier
            key: Field name to update (e.g., "paused")
            value: Value to set
        
        This is a convenience method for updating individual fields
        without replacing the entire state dict.
        """
        state_key = self._make_key(firm_code, program_id)
        with self._lock:
            if state_key not in self._state:
                self._state[state_key] = {}
            self._state[state_key][key] = value
            self._state[state_key]["last_update"] = time.time()
