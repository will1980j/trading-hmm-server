"""
Complete ML Insights Endpoint
Fixes the truncated endpoint in web_server.py
"""

def get_ml_insights_response(ml_available, db_enabled, db):
    """Generate complete ML insights response"""
    from flask import jsonify
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        if not ml_available:
            return jsonify({
                'performance': {'is_trained': False, 'training_samples': 0, 'success_accuracy': 0, 'last_training': None},
                'best_sessions': {},
                'optimal_targets': {},
                'bias_performance': {},
                'key_recommendations': [],
                'status': 'dependencies_missing'
            }), 200
        
        if not db_enabled or not db:
            return jsonify({
                'performance': {'is_trained': False, 'training_samples': 0, 'success_accuracy': 0, 'last_training': None},
                'best_sessions': {},
                'optimal_targets': {},
                'bias_performance': {},
                'key_recommendations': [],
                'status': 'database_offline'
            }), 200
        
        # Get unified ML instance
        from unified_ml_intelligence import get_unified_ml
        ml_engine = get_unified_ml(db)
        
        # Train if not trained
        if not ml_engine.is_trained:
            logger.info("ML not trained, training now...")
            train_result = ml_engine.train_on_all_data()
            if 'error' in train_result:
                logger.error(f"Training failed: {train_result['error']}")
        
        # Get fundamental insights
        insights = ml_engine.get_fundamental_insights()
        
        if 'error' in insights:
            return jsonify({
                'performance': {
                    'is_trained': ml_engine.is_trained,
                    'training_samples': ml_engine.training_data_count,
                    'success_accuracy': 0,
                    'last_training': ml_engine.last_training.isoformat() if ml_engine.last_training else None
                },
                'best_sessions': {},
                'optimal_targets': {},
                'bias_performance': {},
                'key_recommendations': [],
                'status': 'error'
            }), 200
        
        # Build complete response
        response = {
            'performance': {
                'is_trained': ml_engine.is_trained,
                'training_samples': ml_engine.training_data_count,
                'success_accuracy': 0,
                'last_training': ml_engine.last_training.isoformat() if ml_engine.last_training else None
            },
            'best_sessions': insights.get('best_sessions', {}),
            'optimal_targets': insights.get('optimal_targets', {}),
            'bias_performance': insights.get('bias_performance', {}),
            'key_recommendations': insights.get('key_recommendations', []),
            'total_trades': insights.get('total_trades', 0),
            'trades_with_outcomes': insights.get('trades_with_outcomes', 0),
            'status': 'success'
        }
        
        logger.info(f"✅ ML Insights: {response['total_trades']} trades, {len(response['key_recommendations'])} recommendations")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"ML insights error: {str(e)}")
        return jsonify({
            'performance': {'is_trained': False, 'training_samples': 0, 'success_accuracy': 0, 'last_training': None},
            'best_sessions': {},
            'optimal_targets': {},
            'bias_performance': {},
            'key_recommendations': [],
            'status': 'error'
        }), 200
