"""
AI Quick Actions - Execute platform actions from AI recommendations
"""

AVAILABLE_ACTIONS = {
    'apply_optimal_strategy': {
        'description': 'Apply the optimal trading strategy to dashboard',
        'params': ['be_strategy', 'r_target', 'sessions']
    },
    'enable_ml_predictions': {
        'description': 'Enable ML predictions for live signals',
        'params': []
    },
    'set_risk_limits': {
        'description': 'Update prop firm risk limits',
        'params': ['risk_per_trade', 'max_daily_loss', 'max_drawdown']
    },
    'focus_session': {
        'description': 'Focus trading on specific session',
        'params': ['session']
    }
}

def execute_action(action_name, params, db):
    """Execute a quick action"""
    if action_name == 'apply_optimal_strategy':
        return {
            'action': 'apply_optimal_strategy',
            'settings': params,
            'message': f"Strategy applied: {params['be_strategy']}, {params['r_target']}R, {params['sessions']}"
        }
    
    elif action_name == 'set_risk_limits':
        return {
            'action': 'set_risk_limits',
            'settings': params,
            'message': f"Risk limits updated: {params['risk_per_trade']}% per trade"
        }
    
    elif action_name == 'focus_session':
        return {
            'action': 'focus_session',
            'settings': params,
            'message': f"Focused on {params['session']} session"
        }
    
    return {'error': 'Unknown action'}
