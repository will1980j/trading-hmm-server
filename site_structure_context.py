"""
Complete site structure and context for AI Business Advisor
This gives the AI full awareness of the entire platform
"""

SITE_STRUCTURE = {
    "base_url": "https://web-production-cd33.up.railway.app",
    
    "pages": {
        "/ml-dashboard": {
            "name": "ML Dashboard",
            "purpose": "Machine learning model training and predictions",
            "features": ["Model training", "Prediction accuracy", "Feature importance"],
            "data_sources": ["signal_lab_trades", "live_signals"]
        },
        "/live-signals-dashboard": {
            "name": "Live Signals Dashboard",
            "purpose": "Real-time trading signals from TradingView",
            "features": ["Live feed", "Signal filtering", "Session analysis"],
            "data_sources": ["live_signals"]
        },
        "/signal-lab-dashboard": {
            "name": "Signal Lab Dashboard",
            "purpose": "Performance analytics and strategy optimization",
            "features": ["Performance calendar", "Time analysis", "Session analytics", "AI optimization"],
            "data_sources": ["signal_lab_trades"]
        },
        "/signal-analysis-lab": {
            "name": "Signal Analysis Lab",
            "purpose": "Detailed signal analysis and backtesting",
            "features": ["Trade-by-trade analysis", "BE strategy testing", "R-target optimization", "Economic news integration"],
            "data_sources": ["signal_lab_trades", "economic_news"]
        },
        "/ai-business-advisor": {
            "name": "AI Business Advisor",
            "purpose": "Strategic business guidance and optimization",
            "features": ["Business health analysis", "Scaling recommendations", "Growth strategies"],
            "data_sources": ["All trading data", "ML metrics", "Performance trends"]
        },
        "/prop-portfolio": {
            "name": "Prop Portfolio Manager",
            "purpose": "Multi-account prop firm management",
            "features": ["Account tracking", "Risk management", "Payout tracking"],
            "data_sources": ["prop_firms", "prop_accounts"]
        },
        "/trade-manager": {
            "name": "Trade Manager",
            "purpose": "Manual trade entry and management",
            "features": ["Trade logging", "Performance tracking", "Trade editing"],
            "data_sources": ["signal_lab_trades"]
        },
        "/financial-summary": {
            "name": "Financial Summary",
            "purpose": "Overall financial performance and metrics",
            "features": ["P&L tracking", "Monthly summaries", "Account balances"],
            "data_sources": ["signal_lab_trades", "prop_accounts"]
        },
        "/reporting-hub": {
            "name": "Reporting Hub",
            "purpose": "Comprehensive reports and analytics",
            "features": ["Custom reports", "Export functionality", "Historical analysis"],
            "data_sources": ["All tables"]
        }
    },
    
    "database_tables": {
        "signal_lab_trades": "Main trading data with MFE, BE levels, sessions",
        "live_signals": "Real-time signals from TradingView webhooks",
        "economic_news": "Economic calendar events",
        "prop_firms": "Prop firm account information",
        "ml_models": "Trained ML models and predictions"
    },
    
    "key_features": {
        "auto_fill": "Automatically populates economic news for trades",
        "ml_predictions": "AI-powered trade outcome predictions",
        "session_analysis": "Performance breakdown by trading session",
        "calendar_sync": "Synchronized performance calendars across pages",
        "be_strategies": "Breakeven strategy testing (BE=1R, BE=2R)",
        "r_target_optimization": "Find optimal profit targets"
    },
    
    "common_issues": {
        "calendar_sync": "Dashboard and analysis lab calendars need to stay in sync",
        "economic_news": "Auto-fill process updates database, dashboard needs refresh",
        "ml_training": "Models need retraining when new data added",
        "session_filtering": "Multiple session combinations in time analysis"
    }
}

def get_site_context_for_ai():
    """Generate comprehensive site context for AI advisor - dynamically reads current structure"""
    import os
    
    # Dynamically scan HTML files
    html_files = [f for f in os.listdir('.') if f.endswith('.html')]
    py_files = [f for f in os.listdir('.') if f.endswith('.py') and not f.startswith('test_')]
    
    context = f"""
COMPLETE SITE STRUCTURE (LIVE - SCANNED AUTOMATICALLY):

HTML PAGES AVAILABLE: {len(html_files)}
{chr(10).join(['- ' + f for f in sorted(html_files)[:20]])}

PYTHON MODULES: {len(py_files)}
{chr(10).join(['- ' + f for f in sorted(py_files)[:15]])}

COMPLETE SITE STRUCTURE:

BASE URL: {SITE_STRUCTURE['base_url']}

AVAILABLE PAGES:
"""
    for route, info in SITE_STRUCTURE['pages'].items():
        context += f"\n{route} - {info['name']}"
        context += f"\n  Purpose: {info['purpose']}"
        context += f"\n  Features: {', '.join(info['features'])}"
        context += f"\n  Data: {', '.join(info['data_sources'])}"
    
    context += "\n\nDATABASE TABLES:\n"
    for table, desc in SITE_STRUCTURE['database_tables'].items():
        context += f"- {table}: {desc}\n"
    
    context += "\nKEY FEATURES:\n"
    for feature, desc in SITE_STRUCTURE['key_features'].items():
        context += f"- {feature}: {desc}\n"
    
    context += "\nKNOWN ISSUES TO WATCH:\n"
    for issue, desc in SITE_STRUCTURE['common_issues'].items():
        context += f"- {issue}: {desc}\n"
    
    return context
