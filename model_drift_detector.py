"""Model Drift Detection System for Trading ML"""
import numpy as np
from scipy import stats
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json

class ModelDriftDetector:
    def __init__(self, db):
        self.db = db
        self.psi_threshold = 0.2
        self.ks_threshold = 0.05
        
    def calculate_psi(self, expected: np.ndarray, actual: np.ndarray, bins=10) -> float:
        """Calculate Population Stability Index"""
        expected_percents = np.histogram(expected, bins=bins)[0] / len(expected)
        actual_percents = np.histogram(actual, bins=bins)[0] / len(actual)
        
        expected_percents = np.where(expected_percents == 0, 0.0001, expected_percents)
        actual_percents = np.where(actual_percents == 0, 0.0001, actual_percents)
        
        psi = np.sum((actual_percents - expected_percents) * np.log(actual_percents / expected_percents))
        return psi
    
    def detect_feature_drift(self, baseline_data: Dict, current_data: Dict) -> Dict:
        """Detect drift in feature distributions"""
        drift_results = {}
        
        for feature in baseline_data.keys():
            if feature not in current_data:
                continue
                
            baseline = np.array(baseline_data[feature])
            current = np.array(current_data[feature])
            
            # PSI calculation
            psi = self.calculate_psi(baseline, current)
            
            # KS test
            ks_stat, ks_pval = stats.ks_2samp(baseline, current)
            
            # Determine severity
            if psi > 0.25 or ks_pval < 0.01:
                severity = 'Critical'
            elif psi > 0.2 or ks_pval < 0.05:
                severity = 'High'
            elif psi > 0.1:
                severity = 'Medium'
            else:
                severity = 'Low'
            
            drift_results[feature] = {
                'psi': float(psi),
                'ks_statistic': float(ks_stat),
                'ks_pvalue': float(ks_pval),
                'severity': severity,
                'drift_detected': psi > self.psi_threshold or ks_pval < self.ks_threshold
            }
        
        return drift_results
    
    def calculate_performance_drift(self, window_days: int = 30) -> Dict:
        """Monitor model performance degradation"""
        cursor = self.db.conn.cursor()
        
        # Get recent predictions vs actuals
        cursor.execute("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as total,
                AVG(CASE WHEN mfe_none > 0 THEN 1 ELSE 0 END) as success_rate,
                AVG(mfe_none) as avg_mfe
            FROM signal_lab_trades
            WHERE created_at > NOW() - INTERVAL '%s days'
            AND mfe_none IS NOT NULL
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """, (window_days,))
        
        results = cursor.fetchall()
        
        if len(results) < 7:
            return {'status': 'insufficient_data'}
        
        # Calculate trend
        dates = [r['date'] for r in results]
        success_rates = [r['success_rate'] for r in results]
        
        # Linear regression for trend
        x = np.arange(len(success_rates))
        slope, intercept = np.polyfit(x, success_rates, 1)
        
        # Performance degradation detected if negative slope
        degradation = slope < -0.01
        
        return {
            'window_days': window_days,
            'current_accuracy': float(success_rates[0]) if success_rates else 0,
            'avg_accuracy': float(np.mean(success_rates)),
            'trend_slope': float(slope),
            'degradation_detected': degradation,
            'severity': 'High' if slope < -0.02 else 'Medium' if degradation else 'Low',
            'data_points': len(results)
        }
    
    def get_model_health_score(self) -> Dict:
        """Calculate composite model health score"""
        try:
            # Get baseline data (first 30 days)
            cursor = self.db.conn.cursor()
            cursor.execute("""
                SELECT 
                    CASE WHEN bias = 'Bullish' THEN 1 ELSE 0 END as bias_encoded,
                    CASE 
                        WHEN session = 'NY AM' THEN 1
                        WHEN session = 'NY PM' THEN 2
                        WHEN session = 'London' THEN 3
                        ELSE 0
                    END as session_encoded
                FROM signal_lab_trades
                WHERE created_at < NOW() - INTERVAL '30 days'
                LIMIT 500
            """)
            baseline = cursor.fetchall()
            
            # Get current data (last 7 days)
            cursor.execute("""
                SELECT 
                    CASE WHEN bias = 'Bullish' THEN 1 ELSE 0 END as bias_encoded,
                    CASE 
                        WHEN session = 'NY AM' THEN 1
                        WHEN session = 'NY PM' THEN 2
                        WHEN session = 'London' THEN 3
                        ELSE 0
                    END as session_encoded
                FROM signal_lab_trades
                WHERE created_at > NOW() - INTERVAL '7 days'
            """)
            current = cursor.fetchall()
            
            if len(baseline) < 50 or len(current) < 10:
                return {
                    'health_score': 75,
                    'status': 'Insufficient Data',
                    'recommendation': 'Collect more data'
                }
            
            # Feature drift
            baseline_data = {
                'bias': [r['bias_encoded'] for r in baseline],
                'session': [r['session_encoded'] for r in baseline]
            }
            current_data = {
                'bias': [r['bias_encoded'] for r in current],
                'session': [r['session_encoded'] for r in current]
            }
            
            drift_results = self.detect_feature_drift(baseline_data, current_data)
            
            # Performance drift
            perf_drift = self.calculate_performance_drift(30)
            
            # Calculate health score (0-100)
            health_score = 100
            
            # Deduct for feature drift
            for feature, result in drift_results.items():
                if result['severity'] == 'Critical':
                    health_score -= 20
                elif result['severity'] == 'High':
                    health_score -= 10
                elif result['severity'] == 'Medium':
                    health_score -= 5
            
            # Deduct for performance drift
            if perf_drift.get('degradation_detected'):
                if perf_drift['severity'] == 'High':
                    health_score -= 15
                else:
                    health_score -= 8
            
            health_score = max(0, health_score)
            
            # Determine status
            if health_score >= 80:
                status = 'Healthy'
                recommendation = 'Continue monitoring'
            elif health_score >= 60:
                status = 'Warning'
                recommendation = 'Review model performance'
            else:
                status = 'Critical'
                recommendation = 'Retrain model immediately'
            
            return {
                'health_score': health_score,
                'status': status,
                'recommendation': recommendation,
                'feature_drift': drift_results,
                'performance_drift': perf_drift,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'health_score': 50,
                'status': 'Error',
                'recommendation': f'Error calculating health: {str(e)}'
            }
    
    def get_drift_alerts(self) -> List[Dict]:
        """Get active drift alerts"""
        health = self.get_model_health_score()
        alerts = []
        
        # Feature drift alerts
        if 'feature_drift' in health:
            for feature, result in health['feature_drift'].items():
                if result['drift_detected']:
                    alerts.append({
                        'type': 'feature_drift',
                        'feature': feature,
                        'severity': result['severity'],
                        'message': f"{feature} distribution has drifted (PSI: {result['psi']:.3f})",
                        'timestamp': datetime.now().isoformat()
                    })
        
        # Performance drift alerts
        if 'performance_drift' in health and health['performance_drift'].get('degradation_detected'):
            alerts.append({
                'type': 'performance_drift',
                'severity': health['performance_drift']['severity'],
                'message': f"Model accuracy declining (trend: {health['performance_drift']['trend_slope']:.4f})",
                'timestamp': datetime.now().isoformat()
            })
        
        # Health score alerts
        if health['health_score'] < 60:
            alerts.append({
                'type': 'health_score',
                'severity': 'Critical' if health['health_score'] < 40 else 'High',
                'message': f"Model health score: {health['health_score']}/100 - {health['recommendation']}",
                'timestamp': datetime.now().isoformat()
            })
        
        return alerts
