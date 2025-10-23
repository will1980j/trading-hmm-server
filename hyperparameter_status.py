"""Hyperparameter Optimization Status Tracker"""
from datetime import datetime
from typing import Dict, Optional
import json

class HyperparameterStatus:
    def __init__(self, db):
        self.db = db
        
    def get_optimization_status(self) -> Dict:
        """Get current hyperparameter optimization status"""
        try:
            cursor = self.db.conn.cursor()
            
            # Check if optimization results table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'hyperparameter_optimization_results'
                ) as exists
            """)
            
            result = cursor.fetchone()
            table_exists = result['exists'] if result else False
            
            if not table_exists:
                return {
                    'status': 'not_run',
                    'message': 'Hyperparameter optimization has not been run yet',
                    'current_params': self._get_default_params(),
                    'last_run': None
                }
            
            # Get latest optimization results
            cursor.execute("""
                SELECT 
                    optimization_timestamp,
                    rf_params,
                    gb_params,
                    baseline_accuracy,
                    optimized_accuracy,
                    improvement_pct,
                    optimization_duration_seconds
                FROM hyperparameter_optimization_results
                ORDER BY optimization_timestamp DESC
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            
            if not result:
                return {
                    'status': 'not_run',
                    'message': 'Hyperparameter optimization has not been run yet',
                    'current_params': self._get_default_params(),
                    'last_run': None
                }
            
            return {
                'status': 'optimized',
                'last_run': result['optimization_timestamp'].isoformat(),
                'current_params': {
                    'random_forest': json.loads(result['rf_params']) if isinstance(result['rf_params'], str) else result['rf_params'],
                    'gradient_boosting': json.loads(result['gb_params']) if isinstance(result['gb_params'], str) else result['gb_params']
                },
                'performance': {
                    'baseline_accuracy': float(result['baseline_accuracy']),
                    'optimized_accuracy': float(result['optimized_accuracy']),
                    'improvement': float(result['improvement_pct'])
                },
                'duration_seconds': float(result['optimization_duration_seconds'])
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error retrieving optimization status: {str(e)}',
                'current_params': self._get_default_params(),
                'last_run': None
            }
    
    def _get_default_params(self) -> Dict:
        """Get default hyperparameters"""
        return {
            'random_forest': {
                'n_estimators': 100,
                'max_depth': 5,
                'min_samples_split': 2,
                'min_samples_leaf': 1,
                'max_features': 'sqrt'
            },
            'gradient_boosting': {
                'n_estimators': 100,
                'max_depth': 5,
                'learning_rate': 0.1,
                'subsample': 1.0,
                'min_samples_split': 2
            }
        }
    
    def get_optimization_history(self, limit: int = 10) -> Dict:
        """Get hyperparameter optimization history"""
        try:
            cursor = self.db.conn.cursor()
            
            cursor.execute("""
                SELECT 
                    optimization_timestamp,
                    baseline_accuracy,
                    optimized_accuracy,
                    improvement_pct,
                    optimization_duration_seconds
                FROM hyperparameter_optimization_results
                ORDER BY optimization_timestamp DESC
                LIMIT %s
            """, (limit,))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    'timestamp': row['optimization_timestamp'].isoformat(),
                    'baseline_accuracy': float(row['baseline_accuracy']),
                    'optimized_accuracy': float(row['optimized_accuracy']),
                    'improvement': float(row['improvement_pct']),
                    'duration_seconds': float(row['optimization_duration_seconds'])
                })
            
            return {
                'history': history,
                'total_runs': len(history)
            }
            
        except Exception as e:
            return {
                'history': [],
                'total_runs': 0,
                'error': str(e)
            }
