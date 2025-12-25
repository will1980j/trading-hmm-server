"""
Feature Flag System for Second Skies Trading Platform

This module provides a centralized feature flag system to gate unfinished features.
Flags can be overridden via environment variables: FEATURE_<FLAGNAME>=true/false

Usage:
    from config.feature_flags import is_enabled, get_all_flags
    
    if is_enabled('DATABENTO_FOUNDATION'):
        # Show Databento features
    else:
        # Show placeholder
"""

import os
from typing import Dict, List


# ============================================================================
# FEATURE FLAGS - Default values (False unless explicitly enabled)
# ============================================================================

FEATURE_FLAGS: Dict[str, bool] = {
    # PHASE 0 - Databento Foundation
    "DATABENTO_FOUNDATION": True,  # Enabled once stats endpoint healthy
    "DATABENTO_BACKFILL": False,   # Optional 2010-2019 backfill
    
    # PHASE 1 - Market Data Layer
    "MARKET_DATA_BROWSER": False,  # Query bars by date range UI
    "DATA_QUALITY_DASHBOARD": False,  # Gap detection, integrity checks
    "TIMEZONE_NORMALIZATION": False,  # Session/timezone policy enforcement
    
    # PHASE 2 - Indicator Parity
    "INDICATOR_PARITY_ENGINE": False,  # Python signal engine
    "PARITY_TESTS": False,  # Bar-by-bar comparison tests
    "PARITY_DASHBOARD": False,  # Parity results visualization
    
    # PHASE 3 - Automated Signals (Historical)
    "AUTOMATED_SIGNALS_HISTORICAL": False,  # Historical signal generation
    "SIGNALS_V3_SCHEMA": False,  # New signals_v3 database schema
    "AUTOMATED_SIGNALS_DASHBOARD_V3": False,  # Databento-based dashboard
    "MFE_MAE_COMPUTATION": False,  # MFE/MAE from Databento bars
    
    # PHASE 4 - Strategy Discovery
    "FEATURE_STORE": False,  # Feature engineering pipeline
    "STRATEGY_DISCOVERY": False,  # Candidate strategy generator
    "WALK_FORWARD_VALIDATION": False,  # Walk-forward testing framework
    "STRATEGY_SCORING": False,  # Strategy selection dashboard
    
    # PHASE 5 - Regime/Temporal Analysis
    "REGIME_DETECTION": False,  # Volatility/trend regime detection
    "REGIME_ANALYSIS": False,  # Regime analysis dashboard
    "TEMPORAL_FILTERS": False,  # Session/time-of-day filters
    "TRADE_GATING_RULES": False,  # "When not to trade" rules
    
    # PHASE 6 - Backtesting & Portfolio
    "PORTFOLIO_BACKTEST": False,  # Portfolio simulation engine
    "RISK_CONTROLS": False,  # Max DD, daily loss limits
    "RISK_DASHBOARD": False,  # Risk monitoring dashboard
    "SCENARIO_TESTING": False,  # What-if scenario analysis
    
    # PHASE 7 - Live Market Data
    "DATABENTO_LIVE_SUBSCRIPTION": False,  # Live data subscription
    "LIVE_BAR_INGESTION": False,  # Real-time bar ingestion
    "AUTOMATED_SIGNALS_LIVE": False,  # Live signal generation
    "STREAM_HEALTH_MONITOR": False,  # Stream health dashboard
    
    # PHASE 8 - Execution & Prop Firm
    "EXECUTION_ROUTER": False,  # Multi-account execution
    "PROP_FIRM_RULES": False,  # Prop firm rules engine
    "KILL_SWITCH": False,  # Emergency stop system
    "PAPER_TRADING": False,  # Paper trading mode
    
    # PHASE 9 - Copy Trading & Ops
    "COPY_TRADING": False,  # Copy allocation engine
    "ACCOUNT_STATE_MANAGER": False,  # Account state tracking
    "OPERATOR_DASHBOARD": False,  # Operations monitoring
    "AUDIT_TRAILS": False,  # Comprehensive audit logging
    
    # PHASE 10 - MLOps (Advanced)
    "ML_LABELING": False,  # Automated ML labeling
    "ML_TRAINING": False,  # Training pipeline
    "ML_INFERENCE": False,  # Inference service
    "ML_DRIFT_DETECTION": False,  # Model drift monitoring
    "MODEL_REGISTRY": False,  # Model versioning system
    
    # LEGACY SYSTEMS
    "LEGACY_TV_INGESTION": False,  # TradingView webhook ingestion (deprecated)
    "LEGACY_HYBRID_SYNC": False,  # Hybrid sync system (deprecated)
    
    # OBSERVABILITY
    "OBSERVABILITY": False,  # Advanced monitoring/tracing
    "PERFORMANCE_PROFILING": False,  # Performance profiling tools
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_enabled(flag_name: str) -> bool:
    """
    Check if a feature flag is enabled.
    
    Priority:
    1. Environment variable: FEATURE_<FLAGNAME>=true/false
    2. Default value from FEATURE_FLAGS dict
    
    Args:
        flag_name: Feature flag name (e.g., 'DATABENTO_FOUNDATION')
    
    Returns:
        bool: True if feature is enabled, False otherwise
    
    Examples:
        >>> is_enabled('DATABENTO_FOUNDATION')
        True
        >>> is_enabled('MARKET_DATA_BROWSER')
        False
    """
    # Check environment variable override
    env_key = f"FEATURE_{flag_name.upper()}"
    env_value = os.environ.get(env_key)
    
    if env_value is not None:
        return env_value.lower() in ('true', '1', 'yes', 'on')
    
    # Fall back to default value
    return FEATURE_FLAGS.get(flag_name, False)


def get_all_flags() -> Dict[str, bool]:
    """
    Get all feature flags with their current values (including env overrides).
    
    Returns:
        dict: All feature flags with resolved values
    """
    return {
        flag_name: is_enabled(flag_name)
        for flag_name in FEATURE_FLAGS.keys()
    }


def get_enabled_flags() -> List[str]:
    """
    Get list of all enabled feature flags.
    
    Returns:
        list: Names of enabled flags
    """
    return [
        flag_name
        for flag_name, enabled in get_all_flags().items()
        if enabled
    ]


def get_disabled_flags() -> List[str]:
    """
    Get list of all disabled feature flags.
    
    Returns:
        list: Names of disabled flags
    """
    return [
        flag_name
        for flag_name, enabled in get_all_flags().items()
        if not enabled
    ]


def set_flag(flag_name: str, enabled: bool) -> None:
    """
    Programmatically set a feature flag (runtime only, not persisted).
    
    Args:
        flag_name: Feature flag name
        enabled: True to enable, False to disable
    
    Note:
        This only affects the current process. Use environment variables
        for persistent configuration.
    """
    FEATURE_FLAGS[flag_name] = enabled


def get_phase_flags(phase_id: str) -> Dict[str, bool]:
    """
    Get all feature flags for a specific phase.
    
    Args:
        phase_id: Phase identifier (e.g., 'phase_0', 'phase_1')
    
    Returns:
        dict: Feature flags relevant to the phase
    """
    phase_flag_mapping = {
        'phase_0': ['DATABENTO_FOUNDATION', 'DATABENTO_BACKFILL'],
        'phase_1': ['MARKET_DATA_BROWSER', 'DATA_QUALITY_DASHBOARD', 'TIMEZONE_NORMALIZATION'],
        'phase_2': ['INDICATOR_PARITY_ENGINE', 'PARITY_TESTS', 'PARITY_DASHBOARD'],
        'phase_3': ['AUTOMATED_SIGNALS_HISTORICAL', 'SIGNALS_V3_SCHEMA', 'AUTOMATED_SIGNALS_DASHBOARD_V3', 'MFE_MAE_COMPUTATION'],
        'phase_4': ['FEATURE_STORE', 'STRATEGY_DISCOVERY', 'WALK_FORWARD_VALIDATION', 'STRATEGY_SCORING'],
        'phase_5': ['REGIME_DETECTION', 'REGIME_ANALYSIS', 'TEMPORAL_FILTERS', 'TRADE_GATING_RULES'],
        'phase_6': ['PORTFOLIO_BACKTEST', 'RISK_CONTROLS', 'RISK_DASHBOARD', 'SCENARIO_TESTING'],
        'phase_7': ['DATABENTO_LIVE_SUBSCRIPTION', 'LIVE_BAR_INGESTION', 'AUTOMATED_SIGNALS_LIVE', 'STREAM_HEALTH_MONITOR'],
        'phase_8': ['EXECUTION_ROUTER', 'PROP_FIRM_RULES', 'KILL_SWITCH', 'PAPER_TRADING'],
        'phase_9': ['COPY_TRADING', 'ACCOUNT_STATE_MANAGER', 'OPERATOR_DASHBOARD', 'AUDIT_TRAILS'],
        'phase_10': ['ML_LABELING', 'ML_TRAINING', 'ML_INFERENCE', 'ML_DRIFT_DETECTION', 'MODEL_REGISTRY'],
    }
    
    flag_names = phase_flag_mapping.get(phase_id, [])
    return {
        flag_name: is_enabled(flag_name)
        for flag_name in flag_names
    }


# ============================================================================
# FEATURE FLAG METADATA
# ============================================================================

FEATURE_METADATA = {
    "DATABENTO_FOUNDATION": {
        "phase": "phase_0",
        "title": "Databento Foundation",
        "description": "Historical OHLCV-1m data ingestion and stats endpoint",
    },
    "MARKET_DATA_BROWSER": {
        "phase": "phase_1",
        "title": "Market Data Browser",
        "description": "UI to query and visualize historical bars",
    },
    "AUTOMATED_SIGNALS_HISTORICAL": {
        "phase": "phase_3",
        "title": "Historical Automated Signals",
        "description": "Generate signals from historical Databento bars",
    },
    "AUTOMATED_SIGNALS_LIVE": {
        "phase": "phase_7",
        "title": "Live Automated Signals",
        "description": "Real-time signal generation from live Databento stream",
    },
    # Add more metadata as needed
}


def get_flag_metadata(flag_name: str) -> Dict[str, str]:
    """
    Get metadata for a feature flag.
    
    Args:
        flag_name: Feature flag name
    
    Returns:
        dict: Metadata including phase, title, description
    """
    return FEATURE_METADATA.get(flag_name, {
        "phase": "unknown",
        "title": flag_name,
        "description": "No description available",
    })
