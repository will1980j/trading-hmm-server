"""Centralised roadmap state for Second Skies Trading.

This module encodes the development roadmap as data, not prose.
It is the single source of truth for:
- Levels (0–10)
- Phases
- Modules within each phase
- Boolean completion flags per module

Higher-level systems (UI, APIs, CLI tools) should READ from this
structure and derive progress, rather than hard-coding numbers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class ModuleStatus:
    name: str
    completed: bool = False
    description: str | None = None


@dataclass
class Phase:
    id: str
    level: int
    name: str
    description: str
    modules: Dict[str, ModuleStatus] = field(default_factory=dict)

    @property
    def module_count(self) -> int:
        return len(self.modules)

    @property
    def completed_count(self) -> int:
        return sum(1 for m in self.modules.values() if m.completed)

    @property
    def percent_complete(self) -> int:
        if not self.modules:
            return 0
        return int((self.completed_count / self.module_count) * 100)


# -------------------------------------------------------------------
# ROADMAP DATA
# Boolean completion flags based on current project state.
# This is v1; adjust flags as reality changes.
# -------------------------------------------------------------------

ROADMAP: Dict[str, Phase] = {}


def _add_phase(
    pid: str, level: int, name: str, description: str, modules: Dict[str, dict]
):
    ROADMAP[pid] = Phase(
        id=pid,
        level=level,
        name=name,
        description=description,
        modules={
            key: ModuleStatus(
                name=key, completed=meta.get("done", False), description=meta.get("desc")
            )
            for key, meta in modules.items()
        },
    )


# Level 0 — Foundations
_add_phase(
    "0",
    level=0,
    name="Foundations",
    description="Core platform infrastructure, methodology and strict-mode pipeline.",
    modules={
        "architecture_foundation": {
            "done": True,
            "desc": "Core system architecture and deployment to Railway.",
        },
        "trading_methodology": {
            "done": True,
            "desc": "NQ strategy definition and constraints.",
        },
        "strict_mode_tooling": {
            "done": True,
            "desc": "Kiro + strict patch workflow, repo guardrails.",
        },
    },
)

# Level 1 — Core Platform & Authentication
_add_phase(
    "1",
    level=1,
    name="Core Platform",
    description="Main UX shell, login, dashboards and core analytics modules.",
    modules={
        "homepage_command_center": {"done": True},
        "main_dashboard": {"done": False},
        "login_basic": {"done": False},
        "secure_auth_hardening": {"done": False},
        "time_analysis_module": {"done": False},
        "financial_summary_module": {"done": False},
        "reporting_hub_module": {"done": False},
        "trade_manager_module": {"done": False},
    },
)

# Level 2 — Automated Signals Engine (2A–2C)
_add_phase(
    "2",
    level=2,
    name="Automated Signals Engine",
    description="Signal ingestion, lifecycle, MFE and automation-ready state.",
    modules={
        "webhook_ingest_v2": {"done": False},
        "event_normalisation": {"done": False},
        "lifecycle_builder": {"done": False},
        "mfe_engine_dual": {"done": False},
        "exit_consolidation": {"done": False},
        "signal_state_api": {"done": False},
        "validation_and_guardrails": {"done": False},
        "live_signal_stats": {"done": False},
    },
)

_add_phase(
    "2.5",
    level=2,
    name="Prop Guardrails & Evaluation",
    description="Evaluation rules, consistency windows and prop-firm readiness.",
    modules={
        "drawdown_limits": {"done": False},
        "daily_loss_limits": {"done": False},
        "consistency_metrics": {"done": False},
        "evaluation_reporting": {"done": False},
    },
)

# Level 3 — Real-Time Data Layer
_add_phase(
    "3",
    level=3,
    name="Real-Time Data Layer",
    description="Streaming market data, tick/bar synthesis and session metrics.",
    modules={
        "realtime_price_stream": {"done": False},
        "bar_aggregation": {"done": False},
        "session_metrics": {"done": False},
        "latency_monitoring": {"done": False},
        "volatility_model": {"done": False},
    },
)

# Level 4 — Execution & Automation Engine
_add_phase(
    "4",
    level=4,
    name="Execution & Automation Engine",
    description="Multi-account routing, pre-trade checks and auto-execution.",
    modules={
        "execution_router": {"done": False},
        "order_queue": {"done": False},
        "position_state_manager": {"done": False},
        "risk_engine_core": {"done": False},
        "auto_entry_logic": {"done": False},
        "auto_exit_logic": {"done": False},
        "pre_trade_checks": {"done": False},
    },
)

# Level 5 — ML Intelligence Layer
_add_phase(
    "5",
    level=5,
    name="ML Intelligence",
    description="Predictive models, feature engineering, regime detection.",
    modules={
        "ml_dataset_builder": {"done": False},
        "feature_engineering": {"done": False},
        "r_multiple_model": {"done": False},
        "regime_classifier": {"done": False},
        "ml_dashboard": {"done": False},
    },
)

# Level 6 — Strategy Research & Analytics
_add_phase(
    "6",
    level=6,
    name="Strategy Research & Analytics",
    description="Optimisation, comparison and research tooling.",
    modules={
        "strategy_optimizer": {"done": False},
        "strategy_compare": {"done": False},
        "expectancy_analysis": {"done": False},
        "session_analytics": {"done": False},
        "multi_strategy_portfolio_analysis": {"done": False},
        "what_if_scenarios": {"done": False},
    },
)

# Level 7 — Signal Quality & Integrity
_add_phase(
    "7",
    level=7,
    name="Signal Quality & Integrity",
    description="Telemetry, validation, anomaly detection and data hygiene.",
    modules={
        "telemetry_pipeline": {"done": False},
        "signal_validator": {"done": False},
        "anomaly_detection": {"done": False},
        "integrity_dashboard": {"done": False},
    },
)

# Level 8 — Prop Portfolio & Compliance
_add_phase(
    "8",
    level=8,
    name="Prop Portfolio & Compliance",
    description="Prop account registry, rule tracking and payout governance.",
    modules={
        "prop_account_registry": {"done": False},
        "rule_library": {"done": False},
        "violation_detection": {"done": False},
        "payout_schedule": {"done": False},
        "programme_sizing": {"done": False},
        "exposure_monitoring": {"done": False},
    },
)

# Level 9 — Infrastructure & Scaling
_add_phase(
    "9",
    level=9,
    name="Infrastructure & Scaling",
    description="Resilience, scaling, monitoring and deployment automation.",
    modules={
        "worker_scaling": {"done": False},
        "db_scaling": {"done": False},
        "observability_stack": {"done": False},
        "disaster_recovery": {"done": False},
    },
)

# Level 10 — Autonomous Trader Engine
_add_phase(
    "10",
    level=10,
    name="Autonomous Trader Engine",
    description="Self-optimising AI trader, including AI Business Advisor.",
    modules={
        "strategy_selector": {"done": False},
        "auto_risk_manager": {"done": False},
        "ai_business_advisor": {"done": False},
        "auto_tilt_detection": {"done": False},
        "regime_aware_execution": {"done": False},
        "auto_scale_up_down": {"done": False},
        "fund_automation_bridge": {"done": False},
    },
)


# -------------------------------------------------------------------
# PUBLIC API
# -------------------------------------------------------------------


def get_phase(phase_id: str) -> Phase | None:
    """Return a Phase by id, or None if not found."""
    return ROADMAP.get(phase_id)


def all_phases() -> Dict[str, Phase]:
    """Return all phases as a dict keyed by phase id."""
    return ROADMAP


def phase_progress_snapshot() -> Dict[str, dict]:
    """Return a lightweight dict of phase progress for UI / APIs.

    Example:
        {
            "0": {"name": "Foundations", "modules": 3, "completed": 3, "percent": 100},
            ...
        }
    """
    return {
        pid: {
            "id": phase.id,
            "level": phase.level,
            "name": phase.name,
            "description": phase.description,
            "modules": phase.module_count,
            "completed": phase.completed_count,
            "percent": phase.percent_complete,
        }
        for pid, phase in ROADMAP.items()
    }
