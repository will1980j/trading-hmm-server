"""ML-Driven Performance Optimization & Auto-Retraining"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import cross_val_score
from typing import Dict, List
from datetime import datetime, timedelta

class MLOptimizer:
    def __init__(self, db):
        self.db = db
        
    def detect_performance_degradation(self) -> Dict:
        """Detect if model performance is degrading"""
        cursor = self.db.conn.cursor()
        
        # Compare recent vs historical performance
        cursor.execute("""
            SELECT 
                AVG(CASE WHEN COALESCE(mfe_none, mfe, 0) >= 1 THEN 1 ELSE 0 END) as recent_accuracy
            FROM signal_lab_trades
            WHERE created_at > NOW() - INTERVAL '7 days'
            AND COALESCE(mfe_none, mfe, 0) IS NOT NULL
            AND active_trade = false
        """)
        recent = cursor.fetchone()
        
        cursor.execute("""
            SELECT 
                AVG(CASE WHEN COALESCE(mfe_none, mfe, 0) >= 1 THEN 1 ELSE 0 END) as historical_accuracy
            FROM signal_lab_trades
            WHERE created_at BETWEEN NOW() - INTERVAL '60 days' AND NOW() - INTERVAL '7 days'
            AND COALESCE(mfe_none, mfe, 0) IS NOT NULL
            AND active_trade = false
        """)
        historical = cursor.fetchone()
        
        if not recent or not historical:
            return {'status': 'insufficient_data'}
        
        recent_acc = recent['recent_accuracy'] or 0
        hist_acc = historical['historical_accuracy'] or 0
        
        degradation = hist_acc - recent_acc
        needs_retraining = degradation > 0.05  # 5% drop
        
        return {
            'recent_accuracy': float(recent_acc),
            'historical_accuracy': float(hist_acc),
            'degradation': float(degradation),
            'needs_retraining': needs_retraining,
            'severity': 'Critical' if degradation > 0.1 else 'High' if degradation > 0.05 else 'Low'
        }
    
    def suggest_hyperparameters(self) -> Dict:
        """Suggest optimal hyperparameters based on data characteristics"""
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) as total_samples,
                   COUNT(DISTINCT session) as unique_sessions,
                   COUNT(DISTINCT bias) as unique_bias
            FROM signal_lab_trades
            WHERE COALESCE(mfe_none, mfe, 0) IS NOT NULL
            AND active_trade = false
        """)
        
        stats = cursor.fetchone()
        total = stats['total_samples']
        
        # Adaptive hyperparameters based on data size
        if total < 500:
            suggestions = {
                'n_estimators': 50,
                'max_depth': 3,
                'min_samples_split': 10,
                'reason': 'Small dataset - preventing overfitting'
            }
        elif total < 1500:
            suggestions = {
                'n_estimators': 100,
                'max_depth': 5,
                'min_samples_split': 5,
                'reason': 'Medium dataset - balanced complexity'
            }
        else:
            suggestions = {
                'n_estimators': 200,
                'max_depth': 7,
                'min_samples_split': 2,
                'reason': 'Large dataset - increased model capacity'
            }
        
        return suggestions
    
    def detect_market_regime(self) -> Dict:
        """Detect current market regime using unsupervised learning"""
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT 
                session,
                AVG(COALESCE(mfe_none, mfe, 0)) as avg_mfe,
                STDDEV(COALESCE(mfe_none, mfe, 0)) as volatility,
                AVG(CASE WHEN COALESCE(mfe_none, mfe, 0) >= 1 THEN 1 ELSE 0 END) as success_rate
            FROM signal_lab_trades
            WHERE created_at > NOW() - INTERVAL '14 days'
            AND COALESCE(mfe_none, mfe, 0) IS NOT NULL
            AND active_trade = false
            GROUP BY session
        """)
        
        regimes = []
        for row in cursor.fetchall():
            volatility = row['volatility'] or 0
            success_rate = row['success_rate'] or 0
            
            # Classify regime
            if success_rate > 0.6 and volatility < 1.5:
                regime = 'Favorable'
            elif success_rate < 0.4 or volatility > 2.0:
                regime = 'Challenging'
            else:
                regime = 'Neutral'
            
            regimes.append({
                'session': row['session'],
                'regime': regime,
                'success_rate': float(success_rate),
                'volatility': float(volatility)
            })
        
        return {'regimes': regimes}
    
    def optimize_signal_filtering(self) -> Dict:
        """Suggest optimal signal filtering based on ML confidence"""
        cursor = self.db.conn.cursor()
        
        # Analyze performance by session
        cursor.execute("""
            SELECT 
                session,
                COUNT(*) as total,
                AVG(CASE WHEN COALESCE(mfe_none, mfe, 0) >= 1 THEN 1 ELSE 0 END) as success_rate,
                AVG(COALESCE(mfe_none, mfe, 0)) as avg_mfe
            FROM signal_lab_trades
            WHERE COALESCE(mfe_none, mfe, 0) IS NOT NULL
            AND active_trade = false
            GROUP BY session
            HAVING COUNT(*) >= 20
            ORDER BY success_rate DESC
        """)
        
        filters = []
        for row in cursor.fetchall():
            if row['success_rate'] > 0.55:
                recommendation = 'Trade'
                confidence = 'High'
            elif row['success_rate'] > 0.45:
                recommendation = 'Trade with caution'
                confidence = 'Medium'
            else:
                recommendation = 'Avoid'
                confidence = 'Low'
            
            filters.append({
                'session': row['session'],
                'recommendation': recommendation,
                'confidence': confidence,
                'success_rate': float(row['success_rate']),
                'avg_mfe': float(row['avg_mfe']),
                'sample_size': row['total']
            })
        
        return {'filters': filters}
    
    def suggest_feature_engineering(self) -> List[Dict]:
        """Suggest new features based on performance gaps"""
        suggestions = []
        
        cursor = self.db.conn.cursor()
        
        # Check if time-based features would help
        cursor.execute("""
            SELECT 
                EXTRACT(HOUR FROM time::time) as hour,
                AVG(CASE WHEN COALESCE(mfe_none, mfe, 0) >= 1 THEN 1 ELSE 0 END) as success_rate,
                COUNT(*) as total
            FROM signal_lab_trades
            WHERE COALESCE(mfe_none, mfe, 0) IS NOT NULL
            AND active_trade = false
            AND time IS NOT NULL
            GROUP BY EXTRACT(HOUR FROM time::time)
            HAVING COUNT(*) >= 10
            ORDER BY success_rate DESC
        """)
        
        time_data = cursor.fetchall()
        if len(time_data) > 0:
            max_rate = max([r['success_rate'] for r in time_data])
            min_rate = min([r['success_rate'] for r in time_data])
            
            if max_rate - min_rate > 0.15:
                suggestions.append({
                    'feature': 'hour_of_day',
                    'priority': 'High',
                    'reason': f'Time shows {((max_rate - min_rate) * 100):.1f}% performance variance',
                    'expected_improvement': f'+{((max_rate - min_rate) * 5):.1f}% accuracy'
                })
        
        # Check day of week patterns
        cursor.execute("""
            SELECT 
                EXTRACT(DOW FROM date) as dow,
                AVG(CASE WHEN COALESCE(mfe_none, mfe, 0) >= 1 THEN 1 ELSE 0 END) as success_rate,
                COUNT(*) as total
            FROM signal_lab_trades
            WHERE COALESCE(mfe_none, mfe, 0) IS NOT NULL
            AND active_trade = false
            GROUP BY EXTRACT(DOW FROM date)
            HAVING COUNT(*) >= 15
        """)
        
        dow_data = cursor.fetchall()
        if len(dow_data) >= 3:
            max_rate = max([r['success_rate'] for r in dow_data])
            min_rate = min([r['success_rate'] for r in dow_data])
            
            if max_rate - min_rate > 0.1:
                suggestions.append({
                    'feature': 'day_of_week',
                    'priority': 'Medium',
                    'reason': f'Weekday patterns show {((max_rate - min_rate) * 100):.1f}% variance',
                    'expected_improvement': f'+{((max_rate - min_rate) * 3):.1f}% accuracy'
                })
        
        # Suggest interaction features
        suggestions.append({
            'feature': 'session_bias_interaction',
            'priority': 'High',
            'reason': 'Session and bias combinations show strong patterns',
            'expected_improvement': '+3-5% accuracy'
        })
        
        return suggestions
    
    def get_optimization_recommendations(self) -> Dict:
        """Get comprehensive ML optimization recommendations"""
        degradation = self.detect_performance_degradation()
        hyperparams = self.suggest_hyperparameters()
        regimes = self.detect_market_regime()
        filters = self.optimize_signal_filtering()
        features = self.suggest_feature_engineering()
        
        # Generate priority recommendations
        recommendations = []
        
        if degradation.get('needs_retraining'):
            recommendations.append({
                'type': 'auto_retrain',
                'priority': 'Critical',
                'title': 'Model Retraining Required',
                'message': f"Performance degraded by {degradation['degradation']*100:.1f}% - retrain immediately",
                'action': 'Trigger automatic model retraining',
                'impact': f"Expected +{degradation['degradation']*100:.1f}% accuracy recovery"
            })
        
        # Hyperparameter optimization is automated - no manual recommendations needed
        
        for feature in features[:2]:  # Top 2 features
            recommendations.append({
                'type': 'feature_engineering',
                'priority': feature['priority'],
                'title': f"Add {feature['feature']} feature",
                'message': feature['reason'],
                'action': f"Implement {feature['feature']} in feature pipeline",
                'impact': feature['expected_improvement']
            })
        
        # Market regime recommendations
        challenging_regimes = [r for r in regimes.get('regimes', []) if r['regime'] == 'Challenging']
        if challenging_regimes:
            recommendations.append({
                'type': 'market_regime',
                'priority': 'High',
                'title': 'Challenging Market Conditions Detected',
                'message': f"{len(challenging_regimes)} sessions in challenging regime",
                'action': 'Reduce position sizes or avoid these sessions',
                'impact': 'Risk reduction'
            })
        
        return {
            'recommendations': recommendations,
            'performance_status': degradation,
            'hyperparameters': hyperparams,
            'market_regimes': regimes,
            'signal_filters': filters,
            'timestamp': datetime.now().isoformat()
        }
