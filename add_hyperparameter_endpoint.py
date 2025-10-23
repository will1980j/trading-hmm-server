"""
Add this code to web_server.py after the /api/ml-optimization endpoint (around line 4895)
"""

# Add this endpoint after @app.route('/api/ml-optimization')
"""
@app.route('/api/hyperparameter-status', methods=['GET'])
@login_required
def get_hyperparameter_status():
    '''Get hyperparameter optimization status and history'''
    try:
        if not db_enabled or not db:
            return jsonify({
                'status': 'not_available',
                'message': 'Database not available'
            }), 200
        
        from hyperparameter_status import HyperparameterStatus
        status_tracker = HyperparameterStatus(db)
        
        status = status_tracker.get_optimization_status()
        history = status_tracker.get_optimization_history(limit=5)
        
        return jsonify({
            'status': status,
            'history': history,
            'auto_optimizer_active': True,  # ml_auto_optimizer.py runs hourly
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f'Hyperparameter status error: {str(e)}')
        return jsonify({
            'status': {'status': 'error', 'message': str(e)},
            'history': {'history': [], 'total_runs': 0},
            'auto_optimizer_active': True
        }), 200
"""
