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
        "h1_1_homepage_command_center": {"done": True, "desc": "H1.1 Homepage Command Center ⭐ H1"},
        "h1_2_main_dashboard": {"done": True, "desc": "H1.2 Main Dashboard ⭐ H1"},
        "h1_3_time_analysis": {"done": False, "desc": "H1.3 Time Analysis ⭐ H1"},
        "h1_4_ml_intelligence_hub": {"done": False, "desc": "H1.4 ML Intelligence Hub ⭐ H1"},
        "h1_5_financial_summary": {"done": False, "desc": "H1.5 Financial Summary ⭐ H1"},
        "h1_6_reporting_center": {"done": False, "desc": "H1.6 Reporting Center ⭐ H1"},
        "h2_1_secure_auth_system": {"done": False, "desc": "H2.1 Secure Authentication System ⭐ H2"},
        "h2_2_navigation_framework": {"done": False, "desc": "H2.2 Navigation Framework ⭐ H2"},
        "h2_3_user_session_manager": {"done": False, "desc": "H2.3 User/Session Manager ⭐ H2"},
        "h2_4_user_roles_permissions": {"done": False, "desc": "H2.4 User Roles & Permissions ⭐ H2"},
        "h2_5_multi_factor_auth": {"done": False, "desc": "H2.5 Multi-Factor Authentication (MFA) ⭐ H2"},
        "h3_1_unified_navigation_system": {"done": False, "desc": "H3.1 Unified Navigation System (role-aware) ⭐ H3"},
        "h3_2_audit_trail_logging": {"done": False, "desc": "H3.2 Audit Trail & Activity Logging (expanded) ⭐ H3"},
    },
)

# Level 2 — Automated Signals Engine (2A–2C)
_add_phase(
    "2",
    level=2,
    name="Automated Signals Engine",
    description="Signal ingestion, lifecycle, MFE and automation-ready state.",
    modules={
        "h1_7_signal_noise_filter": {"done": False, "desc": "H1.7 Signal Noise Filter (Pre-Validation Filter) ⭐ H1"},
        "h1_8_webhook_ingestion": {"done": False, "desc": "H1.8 Webhook Ingestion ⭐ H1"},
        "h1_9_timestamp_normalization": {"done": False, "desc": "H1.9 Timestamp Normalization ⭐ H1"},
        "h2_6_duplicate_filtering": {"done": False, "desc": "H2.6 Duplicate Filtering ⭐ H2"},
        "h2_7_session_tagging": {"done": False, "desc": "H2.7 Session Tagging ⭐ H2"},
        "h1_10_validation_rules": {"done": False, "desc": "H1.10 Validation Rules ⭐ H1"},
        "h1_11_outlier_detection": {"done": False, "desc": "H1.11 Outlier Detection ⭐ H1"},
        "h2_8_guardrails": {"done": False, "desc": "H2.8 Guardrails ⭐ H2"},
        "h2_9_missing_field_repair": {"done": False, "desc": "H2.9 Missing-Field Repair ⭐ H2"},
        "h1_12_signal_lifecycle_model": {"done": False, "desc": "H1.12 Signal Lifecycle Model ⭐ H1"},
        "h1_13_mfe_engine_dual": {"done": False, "desc": "H1.13 MFE Engine (Dual) ⭐ H1"},
        "h1_14_be_logic": {"done": False, "desc": "H1.14 BE Logic ⭐ H1"},
        "h1_15_exit_consolidation": {"done": False, "desc": "H1.15 Exit Consolidation ⭐ H1"},
        "h2_10_multi_event_reconciliation": {"done": False, "desc": "H2.10 Multi-Event Reconciliation ⭐ H2"},
        "h2_11_data_accumulation_window": {"done": False, "desc": "H2.11 Data Accumulation Window ⭐ H2"},
        "h2_12_signal_schema_governance": {"done": False, "desc": "H2.12 Signal Schema Governance ⭐ H2"},
        "h3_3_data_integrity_watchdog": {"done": False, "desc": "H3.3 Data Integrity Watchdog ⭐ H3"},
        "h3_4_signal_replay_engine": {"done": False, "desc": "H3.4 Signal Replay Engine ⭐ H3"},
    },
)

_add_phase(
    "2.5",
    level=2,
    name="Prop Guardrails & Evaluation",
    description="Evaluation rules, consistency windows and prop-firm readiness.",
    modules={
        "h1_16_drawdown_limits": {"done": False, "desc": "H1.16 Drawdown Limits ⭐ H1"},
        "h1_17_daily_loss_limits": {"done": False, "desc": "H1.17 Daily Loss Limits ⭐ H1"},
        "h2_13_consistency_metrics": {"done": False, "desc": "H2.13 Consistency Metrics ⭐ H2"},
        "h2_14_evaluation_reporting": {"done": False, "desc": "H2.14 Evaluation Reporting ⭐ H2"},
    },
)

# Level 3 — Real-Time Data Layer
_add_phase(
    "3",
    level=3,
    name="Real-Time Data Layer",
    description="Streaming market data, tick/bar synthesis and session metrics.",
    modules={
        "h1_18_realtime_price_stream": {"done": False, "desc": "H1.18 Real-Time Price Stream ⭐ H1"},
        "h1_19_atr_volatility_model": {"done": False, "desc": "H1.19 ATR/Volatility Model ⭐ H1"},
        "h1_20_tick_to_bar_converter": {"done": False, "desc": "H1.20 Tick-to-Bar Converter ⭐ H1"},
        "h2_15_session_heatmaps": {"done": False, "desc": "H2.15 Session Heatmaps ⭐ H2"},
        "h2_16_regime_classifier": {"done": False, "desc": "H2.16 Regime Classifier ⭐ H2"},
        "h2_17_bar_aggregation": {"done": False, "desc": "H2.17 Bar Aggregation ⭐ H2"},
        "h2_18_session_metrics": {"done": False, "desc": "H2.18 Session Metrics ⭐ H2"},
        "h3_5_tick_data_warehouse": {"done": False, "desc": "H3.5 Tick Data Warehouse ⭐ H3"},
        "h3_6_market_replay_engine": {"done": False, "desc": "H3.6 Market Replay Engine ⭐ H3"},
        "h3_7_dom_orderbook_capture": {"done": False, "desc": "H3.7 DOM / Orderbook Capture Layer ⭐ H3"},
        "h3_8_latency_monitoring": {"done": False, "desc": "H3.8 Latency Monitoring ⭐ H3"},
    },
)

# Level 4 — Execution & Automation Engine
_add_phase(
    "4",
    level=4,
    name="Execution & Automation Engine",
    description="Multi-account routing, pre-trade checks and auto-execution.",
    modules={
        "h1_21_multi_account_router": {"done": False, "desc": "H1.21 Multi-Account Router ⭐ H1"},
        "h1_22_order_queue": {"done": False, "desc": "H1.22 Order Queue ⭐ H1"},
        "h1_23_dry_run_mode": {"done": False, "desc": "H1.23 Dry-Run Mode ⭐ H1"},
        "h1_24_state_reconciliation": {"done": False, "desc": "H1.24 State Reconciliation ⭐ H1"},
        "h2_19_program_sizing": {"done": False, "desc": "H2.19 Program Sizing ⭐ H2"},
        "h2_20_risk_engine_integration": {"done": False, "desc": "H2.20 Risk Engine Integration ⭐ H2"},
        "h2_21_account_state_manager": {"done": False, "desc": "H2.21 Account State Manager ⭐ H2"},
        "h2_22_position_state_manager": {"done": False, "desc": "H2.22 Position State Manager ⭐ H2"},
        "h3_9_execution_safety_sandbox": {"done": False, "desc": "H3.9 Execution Safety Sandbox ⭐ H3"},
        "h3_10_circuit_breakers": {"done": False, "desc": "H3.10 Circuit Breakers ⭐ H3"},
        "h3_11_execution_decision_engine": {"done": False, "desc": "H3.11 Execution Decision Engine (ML → action logic) ⭐ H3"},
        "h3_12_pre_trade_checks": {"done": False, "desc": "H3.12 Pre-Trade Checks ⭐ H3"},
        "h1_25_automated_entry_logic": {"done": False, "desc": "H1.25 Automated Entry Logic ⭐ H1"},
        "h1_26_automated_exit_logic": {"done": False, "desc": "H1.26 Automated Exit Logic ⭐ H1"},
        "h1_27_position_sizing_automation": {"done": False, "desc": "H1.27 Position Sizing Automation ⭐ H1"},
        "h2_23_strategy_signal_compatibility": {"done": False, "desc": "H2.23 Strategy–Signal Compatibility Engine ⭐ H2"},
    },
)

# Level 5 — ML Intelligence Layer
_add_phase(
    "5",
    level=5,
    name="ML Intelligence",
    description="Predictive models, feature engineering, regime detection.",
    modules={
        "h1_28_early_stage_strategy_discovery": {"done": False, "desc": "H1.28 Early-Stage Strategy Discovery Engine ⭐ H1"},
        "h1_29_ml_dataset_builder": {"done": False, "desc": "H1.29 ML Dataset Builder ⭐ H1"},
        "h1_30_feature_engineering": {"done": False, "desc": "H1.30 Feature Engineering ⭐ H1"},
        "h1_31_expectancy_model": {"done": False, "desc": "H1.31 Expectancy Model ⭐ H1"},
        "h1_32_r_multiple_predictor": {"done": False, "desc": "H1.32 R-Multiple Distribution Predictor ⭐ H1"},
        "h2_24_regime_classifier": {"done": False, "desc": "H2.24 Regime Classifier ⭐ H2"},
        "h2_25_ml_dashboard": {"done": False, "desc": "H2.25 ML Dashboard (Module 20 baseline) ⭐ H2"},
        "h3_13_feature_store": {"done": False, "desc": "H3.13 Feature Store ⭐ H3"},
        "h3_14_model_registry": {"done": False, "desc": "H3.14 Model Registry ⭐ H3"},
        "h3_15_model_drift_detection": {"done": False, "desc": "H3.15 Model Drift Detection ⭐ H3"},
    },
)

# Level 6 — Strategy Research & Analytics
_add_phase(
    "6",
    level=6,
    name="Strategy Research & Analytics",
    description="Optimisation, comparison and research tooling.",
    modules={
        "h1_33_signal_strategy_attribution": {"done": False, "desc": "H1.33 Signal–Strategy Attribution Engine ⭐ H1"},
        "h1_34_strategy_optimizer": {"done": False, "desc": "H1.34 Strategy Optimizer (Module 18) ⭐ H1"},
        "h1_35_strategy_compare": {"done": False, "desc": "H1.35 Strategy Compare (Module 19) ⭐ H1"},
        "h1_36_expectancy_analysis": {"done": False, "desc": "H1.36 Expectancy Analysis ⭐ H1"},
        "h2_26_session_analytics": {"done": False, "desc": "H2.26 Session Analytics ⭐ H2"},
        "h2_27_multi_strategy_portfolio": {"done": False, "desc": "H2.27 Multi-Strategy Portfolio Analysis ⭐ H2"},
        "h2_28_what_if_scenarios": {"done": False, "desc": "H2.28 What-If Scenarios ⭐ H2"},
        "h2_29_backtesting_engine": {"done": False, "desc": "H2.29 Backtesting Engine (institutional-grade) ⭐ H2"},
        "h2_30_strategy_library": {"done": False, "desc": "H2.30 Strategy Library ⭐ H2"},
        "h2_31_r_multiple_expectation_designer": {"done": False, "desc": "H2.31 R-Multiple Expectation Designer ⭐ H2"},
        "h3_16_automated_reporting_engine": {"done": False, "desc": "H3.16 Automated Reporting Engine ⭐ H3"},
        "h3_17_slide_document_generation": {"done": False, "desc": "H3.17 Slide/Document Generation Layer (vendor-agnostic) ⭐ H3"},
        "h3_18_report_scheduler_delivery": {"done": False, "desc": "H3.18 Report Scheduler & Delivery System ⭐ H3"},
        "h3_19_narrative_ai_summarization": {"done": False, "desc": "H3.19 Narrative AI Summarization Engine ⭐ H3"},
    },
)

# Level 7 — Signal Quality & Integrity
_add_phase(
    "7",
    level=7,
    name="Signal Quality & Integrity",
    description="Telemetry, validation, anomaly detection and data hygiene.",
    modules={
        "h1_37_signal_integrity_api": {"done": False, "desc": "H1.37 Signal Integrity API ⭐ H1"},
        "h1_38_telemetry_pipeline": {"done": False, "desc": "H1.38 Telemetry Pipeline (PATCH 7A–7M) ⭐ H1"},
        "h1_39_validation_checks": {"done": False, "desc": "H1.39 Validation Checks ⭐ H1"},
        "h2_32_signal_validator": {"done": False, "desc": "H2.32 Signal Validator ⭐ H2"},
        "h2_33_anomaly_detection": {"done": False, "desc": "H2.33 Anomaly Detection ⭐ H2"},
        "h2_34_repair_engine": {"done": False, "desc": "H2.34 Repair Engine ⭐ H2"},
        "h3_20_integrity_dashboard": {"done": False, "desc": "H3.20 Integrity Dashboard ⭐ H3"},
        "h3_21_statistical_integrity_engine": {"done": False, "desc": "H3.21 Statistical Integrity Engine ⭐ H3"},
        "h3_22_quality_scoring_engine": {"done": False, "desc": "H3.22 Quality Scoring Engine ⭐ H3"},
        "h3_23_alerting_engine": {"done": False, "desc": "H3.23 Alerting Engine ⭐ H3"},
    },
)

# Level 8 — Prop Portfolio & Compliance
_add_phase(
    "8",
    level=8,
    name="Prop Portfolio & Compliance",
    description="Prop account registry, rule tracking and payout governance.",
    modules={
        "h1_40_prop_firm_challenge_simulator": {"done": False, "desc": "H1.40 Prop Firm Challenge Simulator ⭐ H1"},
        "h1_41_drawdown_stress_tester": {"done": False, "desc": "H1.41 Drawdown Stress Tester (Risk-Only Simulator) ⭐ H1"},
        "h1_42_prop_portfolio_management": {"done": False, "desc": "H1.42 Prop Portfolio Management ⭐ H1"},
        "h1_43_prop_account_registry": {"done": False, "desc": "H1.43 Prop Account Registry ⭐ H1"},
        "h2_35_risk_rule_logic": {"done": False, "desc": "H2.35 Risk Rule Logic ⭐ H2"},
        "h2_36_rule_library": {"done": False, "desc": "H2.36 Rule Library ⭐ H2"},
        "h2_37_violation_detection": {"done": False, "desc": "H2.37 Violation Detection ⭐ H2"},
        "h2_38_account_breach_detection": {"done": False, "desc": "H2.38 Account Breach Detection ⭐ H2"},
        "h2_39_payout_schedule": {"done": False, "desc": "H2.39 Payout Schedule ⭐ H2"},
        "h2_40_programme_sizing": {"done": False, "desc": "H2.40 Programme Sizing ⭐ H2"},
        "h3_24_payout_engine": {"done": False, "desc": "H3.24 Payout Engine ⭐ H3"},
        "h3_25_compliance_dashboard": {"done": False, "desc": "H3.25 Compliance Dashboard ⭐ H3"},
        "h3_26_scaling_ladder": {"done": False, "desc": "H3.26 Scaling Ladder ⭐ H3"},
        "h3_27_exposure_monitoring": {"done": False, "desc": "H3.27 Exposure Monitoring ⭐ H3"},
    },
)

# Level 9 — Infrastructure & Scaling
_add_phase(
    "9",
    level=9,
    name="Infrastructure & Scaling",
    description="Resilience, scaling, monitoring and deployment automation.",
    modules={
        "h2_41_worker_scaling": {"done": False, "desc": "H2.41 Worker Scaling ⭐ H2"},
        "h2_42_db_scaling": {"done": False, "desc": "H2.42 DB Scaling ⭐ H2"},
        "h2_43_multi_region_support": {"done": False, "desc": "H2.43 Multi-Region Support ⭐ H2"},
        "h2_44_load_balancing": {"done": False, "desc": "H2.44 Load Balancing ⭐ H2"},
        "h2_45_caching_layer": {"done": False, "desc": "H2.45 Caching Layer ⭐ H2"},
        "h2_46_performance_tuning": {"done": False, "desc": "H2.46 Performance Tuning ⭐ H2"},
        "h3_28_observability_stack": {"done": False, "desc": "H3.28 Observability Stack ⭐ H3"},
        "h3_29_observability_layer": {"done": False, "desc": "H3.29 Observability Layer (metrics/logs/traces) ⭐ H3"},
        "h3_30_distributed_worker_queue": {"done": False, "desc": "H3.30 Distributed Worker Queue ⭐ H3"},
        "h3_31_disaster_recovery": {"done": False, "desc": "H3.31 Disaster Recovery ⭐ H3"},
    },
)

# Level 10 — Autonomous Trader Engine
_add_phase(
    "10",
    level=10,
    name="Autonomous Trader Engine",
    description="Self-optimising AI trader, including AI Business Advisor.",
    modules={
        "h2_47_automated_challenge_planner": {"done": False, "desc": "H2.47 Automated Challenge Execution Planner ⭐ H2"},
        "h2_48_strategy_selector": {"done": False, "desc": "H2.48 Strategy Selector ⭐ H2"},
        "h2_49_autonomous_executor": {"done": False, "desc": "H2.49 Autonomous Executor ⭐ H2"},
        "h2_50_auto_risk_manager": {"done": False, "desc": "H2.50 Auto Risk Manager ⭐ H2"},
        "h2_51_ai_business_advisor": {"done": False, "desc": "H2.51 AI Business Advisor ⭐ H2"},
        "h2_52_auto_tilt_detection": {"done": False, "desc": "H2.52 Auto Tilt Detection ⭐ H2"},
        "h2_53_regime_aware_execution": {"done": False, "desc": "H2.53 Regime-Aware Execution ⭐ H2"},
        "h2_54_auto_scale_up_down": {"done": False, "desc": "H2.54 Auto Scale Up/Down ⭐ H2"},
        "h3_32_safety_aware_strategy_selector": {"done": False, "desc": "H3.32 Safety-Aware Strategy Selector ⭐ H3"},
        "h3_33_autonomous_execution_simulator": {"done": False, "desc": "H3.33 Autonomous Execution Simulator (shadow mode) ⭐ H3"},
        "h3_34_fund_automation_bridge": {"done": False, "desc": "H3.34 Fund Automation Bridge ⭐ H3"},
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
