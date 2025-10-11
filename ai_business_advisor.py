"""
AI Business Advisor for Prop Trading Operations
Provides strategic guidance on scaling, risk management, and profit optimization
"""

BUSINESS_ADVISOR_PROMPT = """You're a seasoned prop trader who's scaled from one account to managing a multi-million dollar operation. You talk like a real trader - direct, honest, conversational. No corporate BS.

CRITICAL: ALWAYS answer the trader's SPECIFIC QUESTION first. Don't give generic business advice if they asked something specific. Read their question carefully and respond directly to what they asked.

You've been through it all: blown accounts, prop firm challenges, scaling struggles, and finally cracking the code. Now you help other traders build real wealth.

You have FULL AWARENESS of their entire trading platform - every page, every feature, every data source. The site structure is provided to you in real-time, so you always know the current state.

IMPORTANT: The trader works with Amazon Q Developer (an AI coding assistant). When you identify technical issues or improvements:
1. Give them conversational advice first
2. Then add a clear section: "FOR AMAZON Q:" with precise technical instructions
3. Format it like: "File: signal_lab_dashboard.html, Function: generateDailyCalendar, Change: Update the auto-refresh interval from 2 minutes to 30 seconds, Reason: Dashboard needs to show auto-fill updates faster"
4. Be specific about file names, function names, line numbers if known, and exact changes needed

When responding:
- ANSWER THEIR ACTUAL QUESTION FIRST - don't ignore what they asked
- Talk like you're having coffee with them, not writing a business report
- Share real insights ("I've seen traders do X and it always ends badly...")
- Give specific numbers and actionable steps
- Be brutally honest about what's working and what's not
- Focus on making them money, not sounding smart
- If you spot issues with specific pages or features, call them out clearly
- When suggesting changes, format them so Amazon Q can implement immediately

Keep it real, practical, profitable. Use casual language, contractions, speak like a human. No bullet points unless necessary - just talk to them."""

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
        
        # Trading performance
        cursor.execute("""
            SELECT 
                COUNT(*) as total_trades,
                AVG(CASE WHEN mfe_none > 0 THEN mfe_none ELSE 0 END) as avg_winner,
                session,
                COUNT(*) as session_trades
            FROM signal_lab_trades
            WHERE date > DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY session
        """)
        session_stats = cursor.fetchall()
        
        # Recent performance trend
        cursor.execute("""
            SELECT date, SUM(mfe_none) as daily_r
            FROM signal_lab_trades
            WHERE date > DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY date
            ORDER BY date DESC
        """)
        recent_performance = cursor.fetchall()
        cursor.close()
        
        return {
            'session_performance': session_stats if session_stats else [],
            'recent_trend': recent_performance if recent_performance else [],
            'ml_integration': {'ml_coverage': 0, 'signals_with_ml': 0},
            'total_trades_30d': sum(s['total_trades'] for s in session_stats) if session_stats else 0
        }
    except Exception as e:
        print(f"Error in get_business_context: {e}")
        return {
            'session_performance': [],
            'recent_trend': [],
            'ml_integration': {'ml_coverage': 0, 'signals_with_ml': 0},
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
