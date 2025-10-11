"""
AI Business Advisor for Prop Trading Operations
Provides strategic guidance on scaling, risk management, and profit optimization
"""
import psycopg2.extras

BUSINESS_ADVISOR_PROMPT = """You are a data-driven business advisor for NQ futures trading. You have tools - USE THEM IMMEDIATELY.

CRITICAL RULES:
1. CALL TOOLS FIRST - Don't explain what you "would" do, just DO IT
2. When user asks a question, immediately call the relevant tool
3. After getting tool results, give a SHORT direct answer based on that data
4. NEVER say "I would need to query" - just query it
5. NEVER give generic advice - only specific advice based on actual data

ACTUAL PAGES THAT EXIST:
- Live Signals Dashboard: Real-time NQ signals from TradingView
- Signal Lab Dashboard: Backtest and analyze historical signals
- Trade Manager: Manual trade entry and tracking
- ML Dashboard: Machine learning model training and predictions
- Prop Portfolio: Prop firm account management
- Financial Summary: P&L and performance metrics
- Reporting Hub: Export and reporting tools

YOUR ROLE:
1. See question → Call tool → Answer with data
2. User asks about performance → Call query_trading_data immediately
3. User asks about best sessions → Call find_optimal_filters immediately
4. User asks about platform → Call get_platform_status immediately

CURRENT CONTEXT (Q4 2025):
- NQ futures trading platform
- Data collection phase - building Signal Lab history
- Goal: Prove edge → Pass prop firm eval → Scale accounts
- Tech: Python/Flask, PostgreSQL, TradingView signals

STYLE:
- Call tool → Get data → Answer in 2-3 sentences
- Use actual numbers from tools
- Be blunt and direct
- No fluff, no generic advice
- If no data exists, say "No data yet" and stop
"""

def get_page_health_metrics(db):
    """Check health of each major page/feature"""
    cursor = db.conn.cursor()
    
    issues = []
    
    # Check if economic news is populated
    cursor.execute("SELECT COUNT(*) FROM signal_lab_trades WHERE economic_news IS NOT NULL")
    news_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM signal_lab_trades")
    total_count = cursor.fetchone()[0]
    
    if total_count > 0 and news_count / total_count < 0.5:
        issues.append("Economic news auto-fill incomplete - only {:.0%} of trades have news data".format(news_count/total_count))
    
    # Check ML model freshness
    try:
        cursor.execute("SELECT MAX(timestamp) FROM ml_models")
        last_train = cursor.fetchone()[0]
        if not last_train:
            issues.append("ML models never trained - predictions unavailable")
    except:
        issues.append("ML models table missing - predictions unavailable")
    
    return issues

def get_business_context(db):
    """Gather comprehensive business metrics and platform data"""
    try:
        cursor = db.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Complete trading data - only completed trades
        cursor.execute("SELECT COUNT(*) as total FROM signal_lab_trades WHERE COALESCE(active_trade, false) = false")
        total_trades = cursor.fetchone()['total'] or 0
        
        cursor.execute("SELECT SUM(COALESCE(mfe_none, mfe, 0)) as total_r FROM signal_lab_trades WHERE COALESCE(active_trade, false) = false")
        total_r = cursor.fetchone()['total_r'] or 0
        
        cursor.execute("SELECT COUNT(*) as wins FROM signal_lab_trades WHERE COALESCE(active_trade, false) = false AND COALESCE(mfe_none, mfe, 0) > 0")
        total_wins = cursor.fetchone()['wins'] or 0
        
        # Session performance
        cursor.execute("""
            SELECT session, COUNT(*) as trades, AVG(COALESCE(mfe_none, mfe, 0)) as avg_r, 
                   SUM(CASE WHEN COALESCE(mfe_none, mfe, 0) > 0 THEN 1 ELSE 0 END) as wins,
                   MAX(date) as last_trade
            FROM signal_lab_trades GROUP BY session ORDER BY avg_r DESC
        """)
        sessions = cursor.fetchall()
        
        # Daily performance last 30 days
        cursor.execute("""
            SELECT date, SUM(COALESCE(mfe_none, mfe, 0)) as daily_r, COUNT(*) as trades,
                   SUM(CASE WHEN COALESCE(mfe_none, mfe, 0) > 0 THEN 1 ELSE 0 END) as wins
            FROM signal_lab_trades 
            WHERE date >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY date ORDER BY date DESC
        """)
        daily_performance = cursor.fetchall()
        
        # Symbol performance - use NQ as default since no symbol column
        cursor.execute("""
            SELECT 'NQ' as symbol, COUNT(*) as trades, AVG(COALESCE(mfe_none, mfe, 0)) as avg_r,
                   SUM(CASE WHEN COALESCE(mfe_none, mfe, 0) > 0 THEN 1 ELSE 0 END) as wins
            FROM signal_lab_trades
        """)
        symbols = cursor.fetchall()
        
        # Live signals status - count recent signals from last 24 hours
        try:
            cursor.execute("SELECT COUNT(*) as active FROM live_signals WHERE timestamp > NOW() - INTERVAL '24 hours'")
            active_signals = cursor.fetchone()['active'] or 0
        except:
            active_signals = 0
        
        # ML models status
        try:
            cursor.execute("SELECT COUNT(*) as models, MAX(timestamp) as last_train FROM ml_models")
            ml_data = cursor.fetchone()
            ml_models = ml_data['models'] if ml_data else 0
            last_ml_train = ml_data['last_train'] if ml_data else None
        except:
            ml_models = 0
            last_ml_train = None
        
        cursor.close()
        
        return {
            'total_trades': total_trades,
            'total_r': float(total_r) if total_r else 0,
            'win_rate': (total_wins / total_trades * 100) if total_trades > 0 else 0,
            'session_performance': sessions,
            'daily_performance': daily_performance,
            'symbol_performance': symbols,
            'active_signals': active_signals,
            'ml_models': ml_models,
            'last_ml_train': last_ml_train,
            'platform_health': get_platform_health_score(total_trades, active_signals, ml_models)
        }
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'total_trades': 0,
            'total_r': 0,
            'win_rate': 0,
            'session_performance': [],
            'daily_performance': [],
            'symbol_performance': [],
            'active_signals': 0,
            'ml_models': 0,
            'last_ml_train': None,
            'platform_health': 0
        }

def get_platform_health_score(total_trades, active_signals, ml_models):
    """Calculate platform health score"""
    trade_score = min(100, (total_trades / 100) * 100)
    return round(trade_score, 1)

def analyze_business_health(context):
    """Calculate comprehensive business health"""
    return {
        'total_trades': context.get('total_trades', 0),
        'ml_models': context.get('ml_models', 0),
        'active_signals': context.get('active_signals', 0)
    }
