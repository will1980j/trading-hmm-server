"""
Match homepage navigation EXACTLY - no Home link
"""

import os
import re

DASHBOARD_FILES = [
    'ml_feature_dashboard.html',
    'signal_lab_dashboard.html',
    'signal_analysis_lab.html',
    'automated_signals_dashboard.html',
    'time_analysis.html',
    'strategy_optimizer.html',
    'strategy_comparison.html',
    'ai_business_dashboard.html',
    'prop_firm_management.html',
    'trade_manager.html',
    'financial_summary.html',
    'reporting_hub.html',
]

# EXACT navigation from homepage - NO HOME LINK
EXACT_NAV = '''    <!-- Navigation -->
    <nav class="nav-container">
        <a href="/ml-dashboard" class="nav-link">🤖 ML</a>
        <a href="/signal-lab-dashboard" class="nav-link">🏠 Dashboard</a>
        <a href="/signal-analysis-lab" class="nav-link">🧪 Signal Lab</a>
       