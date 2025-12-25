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


# Level 0 — Databento Foundation (Phase 0–1A) ✅ 4/5 COMPLETE
_add_phase(
    "0",
    level=0,
    name="Databento Foundation (Phase 0–1A)",
    description="Source of truth: Databento OHLCV-1m. TradingView: charting only.",
    modules={
        "databento_download": {
            "done": True,
            "desc": "✅ Databento dataset downloaded (MNQ OHLCV-1m)",
        },
        "schema_migration": {
            "done": True,
            "desc": "✅ DB schema migrated (market_bars_ohlcv_1m + data_ingest_runs)",
        },
        "ingestion_complete": {
            "done": True,
            "desc": "✅ Ingestion complete (2019–2025) — 2.34M bars (row_count 2338262)",
        },
        "stats_endpoint": {
            "done": True,
            "desc": "✅ Stats endpoint live (/api/market-data/mnq/ohlcv-1m/stats)",
        },
        "backfill_optional": {
            "done": False,
            "desc": "⬜ Optional backfill: 2010–2019",
        },
    },
)

# Level 1 — Indicator Parity (Phase 1B) ⬜ 0/3 PLANNED
_add_phase(
    "1",
    level=1,
    name="Indicator Parity (Phase 1B)",
    description="Python signal engine reproduces Pine outputs on Databento 1m bars.",
    modules={
        "python_signal_engine": {
            "done": False,
            "desc": "⬜ Python signal engine reproduces Pine outputs on 1m bars",
        },
        "bar_by_bar_parity": {
            "done": False,
            "desc": "⬜ Bar-by-bar parity tests pass",
        },
        "parity_dashboard": {
            "done": False,
            "desc": "⬜ Parity report visible on dashboard/homepage",
        },
    },
)

# Level 2 — Strategy Discovery (Phase 2) ⬜ 0/2 PLANNED
_add_phase(
    "2",
    level=2,
    name="Strategy Discovery (Phase 2)",
    description="Feature store + labeling (MFE/MAE, sessions, regimes) + candidate strategy selection.",
    modules={
        "feature_store": {
            "done": False,
            "desc": "⬜ Feature store + labeling (MFE/MAE, sessions, regimes)",
        },
        "candidate_strategy_selection": {
            "done": False,
            "desc": "⬜ Candidate strategy selection pipeline",
        },
    },
)

# Level 3 — Dashboards (Phase 2–3) ⬜ 0/3 PLANNED
_add_phase(
    "3",
    level=3,
    name="Dashboards (Phase 2–3)",
    description="Dashboards re-based on Databento truth layer.",
    modules={
        "automated_signals_dashboard_rebase": {
            "done": False,
            "desc": "⬜ Automated Signals Dashboard re-based on Databento truth layer",
        },
        "trades_mfe_mae_dashboards": {
            "done": False,
            "desc": "⬜ Trades / MFE / MAE dashboards re-based on Databento truth layer",
        },
        "data_quality_dashboard": {
            "done": False,
            "desc": "⬜ Data Quality dashboard updated for Databento pipeline",
        },
    },
)

# Level 4 — Automation & Execution (later) ⬜ 0/3 PLANNED
_add_phase(
    "4",
    level=4,
    name="Automation & Execution (later)",
    description="Live bars ingestion (Databento live) + execution router + prop firm scaling.",
    modules={
        "live_bars_ingestion": {
            "done": False,
            "desc": "⬜ Live bars ingestion (Databento live) using same schema",
        },
        "execution_router": {
            "done": False,
            "desc": "⬜ Execution router + prop firm scaling",
        },
        "copy_trading_framework": {
            "done": False,
            "desc": "⬜ Copy trading framework",
        },
    },
)

# Level 5 — Legacy / Optional (TradingView Alerts) ✅ 3/3 COMPLETE (DEPRECATED)
_add_phase(
    "5",
    level=5,
    name="Legacy / Optional (TradingView Alerts)",
    description="TradingView alert/webhook ingestion (deprecated for core analytics, kept as optional legacy).",
    modules={
        "tradingview_webhook_ingestion": {
            "done": True,
            "desc": "✅ TradingView webhook ingestion (legacy - optional)",
        },
        "hybrid_sync_system": {
            "done": True,
            "desc": "✅ Hybrid Signal Synchronization System (legacy - optional)",
        },
        "automated_signals_dashboard_legacy": {
            "done": True,
            "desc": "✅ Automated Signals Dashboard (legacy TradingView alerts)",
        },
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
