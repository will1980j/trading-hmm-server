"""
AI Business Advisor for Prop Trading Operations
Provides strategic guidance on scaling, risk management, and profit optimization
"""

BUSINESS_ADVISOR_PROMPT = """You are an elite prop trading business advisor with expertise in:
- Futures trading operations and scaling
- Multi-account prop firm management (FTMO, Apex, MyForexFunds, etc.)
- Risk management across portfolios
- Trade copier optimization and automation
- Business growth strategies and capital allocation
- Profit maximization and wealth building

Your role is to analyze the trader's current operation and provide actionable strategic advice on:
1. **Scaling Strategy** - When and how to add more prop accounts
2. **Capital Allocation** - Optimal distribution across accounts
3. **Risk Optimization** - Balancing growth vs. safety
4. **Profit Extraction** - Payout timing and reinvestment strategy
5. **Business Efficiency** - Automation and process improvements
6. **Growth Roadmap** - 30/60/90 day action plans

Always provide:
- Specific numbers and targets
- Risk-adjusted recommendations
- Timeline for implementation
- Expected ROI/impact
- Potential pitfalls to avoid

Be direct, data-driven, and focused on maximizing long-term wealth."""

def get_business_context(db):
    """Gather comprehensive business metrics"""
    cursor = db.conn.cursor()
    
    # Trading performance
    cursor.execute("""
        SELECT 
            COUNT(*) as total_trades,
            AVG(CASE WHEN mfe_none > 0 THEN mfe_none ELSE 0 END) as avg_winner,
            COUNT(CASE WHEN mfe_none > 0 THEN 1 END)::float / NULLIF(COUNT(*), 0) as win_rate,
            session,
            COUNT(*) as session_trades
        FROM signal_lab_trades
        WHERE date > CURRENT_DATE - INTERVAL '30 days'
        GROUP BY session
    """)
    session_stats = cursor.fetchall()
    
    # Recent performance trend
    cursor.execute("""
        SELECT date, SUM(mfe_none) as daily_r
        FROM signal_lab_trades
        WHERE date > CURRENT_DATE - INTERVAL '7 days'
        GROUP BY date
        ORDER BY date DESC
    """)
    recent_performance = cursor.fetchall()
    
    # ML prediction accuracy
    try:
        cursor.execute("""
            SELECT 
                AVG(CASE WHEN ml_prediction IS NOT NULL THEN 1 ELSE 0 END) as ml_coverage,
                COUNT(*) as signals_with_ml
            FROM live_signals
            WHERE timestamp > NOW() - INTERVAL '7 days'
        """)
        ml_stats = cursor.fetchone()
    except:
        ml_stats = {'ml_coverage': 0, 'signals_with_ml': 0}
    
    return {
        'session_performance': [dict(row) for row in session_stats],
        'recent_trend': [dict(row) for row in recent_performance],
        'ml_integration': dict(ml_stats) if ml_stats else {},
        'total_trades_30d': sum(s['total_trades'] for s in session_stats) if session_stats else 0
    }

def analyze_business_health(context):
    """Calculate business health score"""
    total_trades = context.get('total_trades_30d', 0)
    
    # Scoring factors
    volume_score = min(100, (total_trades / 100) * 100)  # 100 trades/month = 100%
    consistency_score = 100 if len(context.get('recent_trend', [])) >= 5 else 50
    ml_score = context.get('ml_integration', {}).get('ml_coverage', 0) * 100
    
    overall_score = (volume_score * 0.4 + consistency_score * 0.3 + ml_score * 0.3)
    
    return {
        'overall_score': round(overall_score, 1),
        'volume_score': round(volume_score, 1),
        'consistency_score': consistency_score,
        'ml_integration_score': round(ml_score, 1)
    }
