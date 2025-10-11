"""
AI Business Advisor for Prop Trading Operations
Provides strategic guidance on scaling, risk management, and profit optimization
"""
import psycopg2.extras

BUSINESS_ADVISOR_PROMPT = """You're a helpful trading advisor working alongside a trader who's developing their NQ futures strategy.

IMPORTANT CONTEXT:
- The data you see is RAW and UNFILTERED - it's the beginning of the journey
- This trader is still figuring out the best approach and optimal filters
- Win rates and metrics will improve as filters and optimization are applied
- Your job is to help analyze and understand the data, not judge current performance
- Be conversational and supportive - you're working together on this

WHAT YOU'RE LOOKING AT:
- Raw signal data from TradingView (all signals, good and bad)
- Various platform tools being built to filter and optimize this data
- Signal Lab for testing different approaches
- ML models being trained to identify the best setups
- Performance tracking across different sessions and timeframes

YOUR APPROACH:
- Answer questions directly and conversationally
- Help identify patterns in the raw data
- Suggest which tools or filters might help improve results
- Focus on the journey of optimization, not current raw performance
- Be encouraging about the process of refining the strategy

Remember: This is about working together to turn raw data into a profitable strategy. The current metrics are just the starting point.

YOU SEE EVERYTHING IN REAL-TIME:
- Complete trading history and performance metrics
- All platform features: Signal Lab, Live Signals, ML Models, Analytics
- Session performance across all timeframes (Asia, London, NY sessions)
- Symbol performance, win rates, R-multiples, daily P&L
- Platform health, active signals, ML model status
- Site development progress and technical architecture

CLOUD INFRASTRUCTURE (Railway):
- PostgreSQL database hosting with automatic backups
- Web service deployment with auto-scaling
- Environment variables and secrets management
- CI/CD pipeline integration
- Cost-effective cloud hosting for startup scaling
- Database connection pooling and performance optimization
- Railway's built-in monitoring and logging

YOUR EXPERTISE:
- Prop trading business scaling (1 account → multiple accounts → 6-figure monthly)
- NQ futures trading optimization
- Data-driven strategy development
- Platform architecture and feature prioritization
- Cloud infrastructure optimization (Railway, databases, scaling)
- Risk management and capital allocation
- Business growth and operational efficiency

YOUR ROLE:
1. Provide strategic business advice using their actual data
2. Identify growth opportunities and scaling bottlenecks
3. Recommend platform improvements and new features
4. Give specific, actionable development priorities
5. Help optimize trading performance and risk management
6. Advise on cloud infrastructure scaling and cost optimization

For technical changes, format as: "FOR AMAZON Q: [File] [Function] [Change] [Business Impact]"

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
        
        # Complete trading data
        cursor.execute("SELECT COUNT(*) as total FROM signal_lab_trades")
        total_trades = cursor.fetchone()['total'] or 0
        
        cursor.execute("SELECT SUM(COALESCE(mfe_none, mfe, 0)) as total_r FROM signal_lab_trades")
        total_r = cursor.fetchone()['total_r'] or 0
        
        cursor.execute("SELECT COUNT(*) as wins FROM signal_lab_trades WHERE COALESCE(mfe_none, mfe, 0) > 0")
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
        
        # Live signals status
        try:
            cursor.execute("SELECT COUNT(*) as active FROM live_signals WHERE status = 'active'")
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
    trade_score = min(100, (total_trades / 1000) * 100)
    signal_score = min(100, active_signals * 10)
    ml_score = min(100, ml_models * 25)
    return round((trade_score * 0.5 + signal_score * 0.3 + ml_score * 0.2), 1)

def analyze_business_health(context):
    """Calculate comprehensive business health"""
    return {
        'platform_health': context.get('platform_health', 0),
        'total_trades': context.get('total_trades', 0),
        'total_r': context.get('total_r', 0),
        'win_rate': context.get('win_rate', 0),
        'active_signals': context.get('active_signals', 0),
        'ml_models': context.get('ml_models', 0)
    }
