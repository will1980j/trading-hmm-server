"""
AI Proactive Alerts Module
"""

def get_all_alerts(db):
    """Get all proactive alerts"""
    return {
        'performance': [
            {
                'type': 'data_analysis',
                'message': 'Raw signal data ready for optimization',
                'priority': 'medium'
            }
        ],
        'system': [
            {
                'type': 'platform_status',
                'message': 'All systems operational',
                'priority': 'low'
            }
        ],
        'opportunities': [
            {
                'type': 'optimization',
                'message': 'Use Signal Lab to filter best setups',
                'priority': 'medium'
            }
        ]
    }
