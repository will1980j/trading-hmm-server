"""
AI Business Advisor for Prop Trading Operations
Provides strategic guidance on scaling, risk management, and profit optimization
"""

BUSINESS_ADVISOR_PROMPT = """You're a helpful trading advisor. Be supportive, encouraging, and practical.

CRITICAL: Answer their SPECIFIC QUESTION directly.

YOU KNOW EVERYTHING ABOUT THEIR PLATFORM:
- Prop trading business for NQ futures (E-mini Nasdaq-100)
- Building data-driven platform to scale from 1 to multiple prop accounts
- Platform: ML predictions, live signals, analytics, signal lab, trade manager, financials
- Database: signal_lab_trades (1M trades with MFE), live_signals, ml_models, economic_news
- Goal: Find optimal strategies, pass prop challenges, scale to 6-figure monthly income
- Uses Amazon Q Developer for coding

You understand:
- Session performance (Asia, London, NY Pre/AM/Lunch/PM)
- Win rates, expectancy, R-multiples
- Recent trends
- What works and what needs improvement

Your job:
1. Answer their question directly using their actual data
2. Be encouraging but honest
3. Give specific, actionable advice
4. For code changes: "FOR AMAZON Q: File: X, Function: Y, Change: Z, Reason: W"

Be friendly, supportive, helpful. No condescension."""

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
    """Gather comprehensive business metrics"""
    try:
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                session,
                COUNT(*) as session_trades,
                AVG(mfe_none) as avg_mfe,
                SUM(CASE WHEN mfe_none > 0 THEN 1 ELSE 0 END) as wins
            FROM signal_lab_trades
            WHERE date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY session
        """)
        session_stats = cursor.fetchall()
        
        cursor.execute("""
            SELECT date, SUM(mfe_none) as daily_r, COUNT(*) as trades
            FROM signal_lab_trades
            WHERE date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY date
            ORDER BY date DESC
        """)
        recent_performance = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) as total FROM signal_lab_trades WHERE date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)")
        total_result = cursor.fetchone()
        total_trades = total_result['total'] if total_result else 0
        
        cursor.close()
        
        return {
            'session_performance': session_stats,
            'recent_trend': recent_performance,
            'ml_integration': {'ml_coverage': 0, 'signals_with_ml': 0},
            'total_trades_30d': total_trades
        }
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'session_performance': [],
            'recent_trend': [],
            'ml_integration': {},
            'total_trades_30d': 0
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
