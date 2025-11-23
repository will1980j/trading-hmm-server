"""Stage 13D - Prop Firm Risk Engine

Provides helper functions to evaluate execution tasks against
per-firm risk rules before connector routing.
"""
from .prop_risk_engine import (
    RiskCheckResult,
    evaluate_task_risk,
)
