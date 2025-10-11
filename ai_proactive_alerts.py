"""
AI Proactive Alerts Module
"""

def get_all_alerts(db):
    """Get all proactive alerts"""
    try:
        # Basic implementation - can be enhanced later
        alerts = []
        
        if db and db.conn:
            cursor = db.conn.cursor()
            
            # Check for low activity
            cursor.execute("SELECT COUNT(*) FROM signal_lab_trades WHERE date >= CURRENT_DATE - INTERVAL '7 days'")
            recent_trades = cursor.fetchone()[0]
            
            if recent_trades < 10:
                alerts.append({
                    'type': 'low_activity',
                    'message': f'Only {recent_trades} trades in the last 7 days - consider increasing trading frequency',
                    'priority': 'medium'
                })
            
            # Check for poor performance
            cursor.execute("""
                SELECT AVG(mfe_none) as avg_mfe FROM signal_lab_trades 
                WHERE date >= CURRENT_DATE - INTERVAL '30 days' AND mfe_none IS NOT NULL
            """)
            result = cursor.fetchone()
            avg_mfe = result[0] if result and result[0] else 0
            
            if avg_mfe < 0:
                alerts.append({
                    'type': 'poor_performance',
                    'message': f'Average MFE is {avg_mfe:.2f}R over last 30 days - review strategy',
                    'priority': 'high'
                })
            
            cursor.close()
        
        return alerts
        
    except Exception as e:
        return [{'type': 'error', 'message': f'Alert system error: {str(e)}', 'priority': 'low'}]
