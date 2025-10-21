"""Advanced Feature Engineering & Importance Analysis"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from scipy.stats import chi2_contingency
from typing import Dict, List, Tuple
import json

class AdvancedFeatureAnalyzer:
    def __init__(self, db):
        self.db = db
        
    def get_feature_data(self) -> Tuple[np.ndarray, np.ndarray, Dict]:
        """Extract and engineer features from trading data"""
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT 
                session,
                bias,
                COALESCE(mfe_none, mfe, 0) as mfe,
                CASE WHEN COALESCE(mfe_none, mfe, 0) >= 1 THEN 1 ELSE 0 END as success,
                EXTRACT(HOUR FROM time::time) as hour,
                EXTRACT(DOW FROM date) as day_of_week
            FROM signal_lab_trades
            WHERE COALESCE(mfe_none, mfe, 0) IS NOT NULL
            AND active_trade = false
            LIMIT 1898
        """)
        
        data = cursor.fetchall()
        
        # Feature engineering
        features = []
        labels = []
        feature_names = ['session_encoded', 'bias_encoded', 'hour', 'day_of_week', 
                        'is_ny_am', 'is_bullish', 'is_morning']
        
        for row in data:
            session_map = {'NY AM': 1, 'NY PM': 2, 'London': 3, 'Asia': 4}
            session_encoded = session_map.get(row['session'], 0)
            bias_encoded = 1 if row['bias'] == 'Bullish' else 0
            hour = row['hour'] if row['hour'] else 12
            dow = row['day_of_week'] if row['day_of_week'] else 3
            
            features.append([
                session_encoded,
                bias_encoded,
                hour,
                dow,
                1 if row['session'] == 'NY AM' else 0,
                bias_encoded,
                1 if hour < 12 else 0
            ])
            labels.append(row['success'])
        
        return np.array(features), np.array(labels), {'feature_names': feature_names}
    
    def calculate_permutation_importance(self) -> Dict:
        """Calculate permutation importance with statistical significance"""
        X, y, meta = self.get_feature_data()
        
        if len(X) < 50:
            return {'error': 'Insufficient data'}
        
        # Train model
        model = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=5)
        model.fit(X, y)
        
        # Permutation importance
        perm_importance = permutation_importance(model, X, y, n_repeats=10, random_state=42)
        
        results = []
        for i, name in enumerate(meta['feature_names']):
            results.append({
                'feature': name,
                'importance': float(perm_importance.importances_mean[i]),
                'std': float(perm_importance.importances_std[i]),
                'significance': 'High' if perm_importance.importances_mean[i] > 0.01 else 'Low'
            })
        
        return {
            'permutation_importance': sorted(results, key=lambda x: x['importance'], reverse=True),
            'model_score': float(model.score(X, y))
        }
    
    def detect_feature_interactions(self) -> List[Dict]:
        """Detect which feature combinations work best"""
        cursor = self.db.conn.cursor()
        
        # Session + Bias interaction
        cursor.execute("""
            SELECT 
                session,
                bias,
                COUNT(*) as total,
                AVG(CASE WHEN COALESCE(mfe_none, mfe, 0) >= 1 THEN 1 ELSE 0 END) as success_rate,
                AVG(COALESCE(mfe_none, mfe, 0)) as avg_mfe
            FROM signal_lab_trades
            WHERE COALESCE(mfe_none, mfe, 0) IS NOT NULL
            AND active_trade = false
            GROUP BY session, bias
            HAVING COUNT(*) >= 10
            ORDER BY success_rate DESC
        """)
        
        interactions = []
        for row in cursor.fetchall():
            interactions.append({
                'combination': f"{row['session']} + {row['bias']}",
                'success_rate': float(row['success_rate']),
                'avg_mfe': float(row['avg_mfe']),
                'sample_size': row['total'],
                'effectiveness': 'High' if row['success_rate'] > 0.6 else 'Medium' if row['success_rate'] > 0.4 else 'Low'
            })
        
        return interactions
    
    def analyze_target_specific_features(self) -> Dict:
        """Analyze what predicts 1R vs 2R vs 3R"""
        cursor = self.db.conn.cursor()
        
        results = {}
        for target in [1, 2, 3]:
            cursor.execute("""
                SELECT 
                    session,
                    bias,
                    COUNT(*) as total,
                    AVG(CASE WHEN COALESCE(mfe_none, mfe, 0) >= %s THEN 1 ELSE 0 END) as hit_rate
                FROM signal_lab_trades
                WHERE COALESCE(mfe_none, mfe, 0) IS NOT NULL
                AND active_trade = false
                GROUP BY session, bias
                HAVING COUNT(*) >= 10
                ORDER BY hit_rate DESC
                LIMIT 5
            """, (target,))
            
            top_features = []
            for row in cursor.fetchall():
                top_features.append({
                    'session': row['session'],
                    'bias': row['bias'],
                    'hit_rate': float(row['hit_rate']),
                    'sample_size': row['total']
                })
            
            results[f'{target}R'] = top_features
        
        return results
    
    def calculate_feature_stability(self) -> Dict:
        """Calculate how consistent each feature is over time"""
        cursor = self.db.conn.cursor()
        
        # Session stability over time windows
        cursor.execute("""
            WITH time_windows AS (
                SELECT 
                    session,
                    DATE_TRUNC('week', created_at) as week,
                    AVG(CASE WHEN COALESCE(mfe_none, mfe, 0) >= 1 THEN 1 ELSE 0 END) as success_rate
                FROM signal_lab_trades
                WHERE COALESCE(mfe_none, mfe, 0) IS NOT NULL
                AND active_trade = false
                AND created_at > NOW() - INTERVAL '90 days'
                GROUP BY session, DATE_TRUNC('week', created_at)
                HAVING COUNT(*) >= 5
            )
            SELECT 
                session,
                AVG(success_rate) as avg_rate,
                STDDEV(success_rate) as std_rate,
                COUNT(*) as weeks
            FROM time_windows
            GROUP BY session
        """)
        
        stability = []
        for row in cursor.fetchall():
            std = row['std_rate'] if row['std_rate'] else 0
            stability_score = 1 - min(std * 2, 1)  # Lower std = higher stability
            
            stability.append({
                'feature': row['session'],
                'stability_score': float(stability_score),
                'avg_performance': float(row['avg_rate']),
                'consistency': 'High' if stability_score > 0.7 else 'Medium' if stability_score > 0.4 else 'Low'
            })
        
        return {'feature_stability': stability}
    
    def get_feature_recommendations(self) -> List[Dict]:
        """Generate automated feature engineering recommendations"""
        recommendations = []
        
        # Get interaction analysis
        interactions = self.detect_feature_interactions()
        top_combo = interactions[0] if interactions else None
        
        if top_combo and top_combo['success_rate'] > 0.6:
            recommendations.append({
                'type': 'high_value_combination',
                'priority': 'High',
                'message': f"Focus on {top_combo['combination']} - {top_combo['success_rate']*100:.1f}% success rate",
                'action': 'Increase allocation to this combination'
            })
        
        # Check for redundant features
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT 
                bias,
                AVG(CASE WHEN COALESCE(mfe_none, mfe, 0) >= 1 THEN 1 ELSE 0 END) as bullish_rate
            FROM signal_lab_trades
            WHERE bias = 'Bullish'
            AND COALESCE(mfe_none, mfe, 0) IS NOT NULL
            AND active_trade = false
            GROUP BY bias
        """)
        bullish_data = cursor.fetchone()
        
        cursor.execute("""
            SELECT 
                bias,
                AVG(CASE WHEN COALESCE(mfe_none, mfe, 0) >= 1 THEN 1 ELSE 0 END) as bearish_rate
            FROM signal_lab_trades
            WHERE bias = 'Bearish'
            AND COALESCE(mfe_none, mfe, 0) IS NOT NULL
            AND active_trade = false
            GROUP BY bias
        """)
        bearish_data = cursor.fetchone()
        
        if bullish_data and bearish_data:
            diff = abs(bullish_data['bullish_rate'] - bearish_data['bearish_rate'])
            if diff < 0.05:
                recommendations.append({
                    'type': 'low_discriminative_power',
                    'priority': 'Medium',
                    'message': 'Bias feature shows similar performance - consider additional context',
                    'action': 'Add time-of-day or volatility features'
                })
        
        return recommendations
    
    def get_comprehensive_analysis(self) -> Dict:
        """Get all advanced feature analysis"""
        try:
            perm_importance = self.calculate_permutation_importance()
            interactions = self.detect_feature_interactions()
            target_analysis = self.analyze_target_specific_features()
            stability = self.calculate_feature_stability()
            recommendations = self.get_feature_recommendations()
            
            return {
                'permutation_importance': perm_importance.get('permutation_importance', []),
                'model_accuracy': perm_importance.get('model_score', 0),
                'feature_interactions': interactions,
                'target_specific': target_analysis,
                'feature_stability': stability.get('feature_stability', []),
                'recommendations': recommendations,
                'status': 'success'
            }
        except Exception as e:
            return {
                'error': str(e),
                'status': 'error'
            }
