"""
AI Proactive Alerts Module
"""

def get_all_alerts(db):
    """Get all proactive alerts"""
    try:
        performance = []
        system = []
        opportunities = []
        
        if db and db.conn:
            cursor = db.conn.cursor()
            
            # Check for low activity
            cursor.execute("SELECT COUNT(*) FROM signal_lab_trades WHERE date >= CURRENT_DATE - INTERVAL '7 days'")
            result = cursor.fetchone()
            recent_trades = result[0] if result else 0
            
            if recent_trades < 10:
                performance.append({
                    'type': 'low_activity',
                    'message': f'Only {recent_trades} trades in the last 7 days - consider increasing trading frequency',
                    'priority': 'medium'
                })
            
            # Check for poor performance
            cursor.execute("""
                SELECT AVG(COALESCE(mfe_none, mfe, 0)) as avg_mfe FROM signal_lab_trades 
                WHERE date >= CURRENT_DATE - INTERVAL '30 days'
            """)
            result = cursor.fetchone()
            avg_mfe = result[0] if result and result[0] else 0
            
            if avg_mfe < 0:
                performance.append({
                    'type': 'poor_performance',
                    'message': f'Average MFE is {avg_mfe:.2f}R over last 30 days - review strategy',
                    'priority': 'high'
                })
            
            cursor.close()
        
        return {
            'performance': performance,
            'system': system,
            'opportunities': opportunities
        }
        
    except Exception as e:
        return {
            'performance': [{'type': 'error', 'message': f'Alert system error: {str(e)}', 'priority': 'low'}],
            'system': [],
            'opportunities': []
        }
