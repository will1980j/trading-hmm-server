"""Intelligent Prediction Confidence & Model Uncertainty"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.calibration import calibration_curve
from typing import Dict, List, Tuple
import json

class IntelligentPredictor:
    def __init__(self, db):
        self.db = db
        self.rf_model = None
        self.gb_model = None
        self.is_trained = False
        
    def train_models(self):
        """Train ensemble models"""
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT 
                session,
                bias,
                COALESCE(mfe_none, mfe, 0) as mfe,
                CASE WHEN COALESCE(mfe_none, mfe, 0) >= 1 THEN 1 ELSE 0 END as success
            FROM signal_lab_trades
            WHERE COALESCE(mfe_none, mfe, 0) IS NOT NULL
            AND active_trade = false
            LIMIT 1500
        """)
        
        data = cursor.fetchall()
        if len(data) < 50:
            return False
        
        # Feature engineering
        X = []
        y = []
        session_map = {'NY AM': 1, 'NY PM': 2, 'London': 3, 'Asia': 4}
        
        for row in data:
            X.append([
                session_map.get(row['session'], 0),
                1 if row['bias'] == 'Bullish' else 0
            ])
            y.append(row['success'])
        
        X = np.array(X)
        y = np.array(y)
        
        # Train models
        self.rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.gb_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        
        self.rf_model.fit(X, y)
        self.gb_model.fit(X, y)
        self.is_trained = True
        
        return True
    
    def predict_with_confidence(self, signal: Dict) -> Dict:
        """Generate prediction with confidence and uncertainty"""
        if not self.is_trained:
            self.train_models()
        
        if not self.is_trained:
            return {'error': 'Insufficient training data'}
        
        # Encode features
        session_map = {'NY AM': 1, 'NY PM': 2, 'London': 3, 'Asia': 4}
        features = np.array([[
            session_map.get(signal.get('session', 'NY AM'), 1),
            1 if signal.get('bias', 'Bullish') == 'Bullish' else 0
        ]])
        
        # Get predictions from both models
        rf_proba = self.rf_model.predict_proba(features)[0]
        gb_proba = self.gb_model.predict_proba(features)[0]
        
        # Ensemble prediction (average)
        ensemble_proba = (rf_proba + gb_proba) / 2
        
        # Calculate confidence (agreement between models)
        model_agreement = 1 - abs(rf_proba[1] - gb_proba[1])
        
        # Uncertainty quantification
        prediction_uncertainty = np.std([rf_proba[1], gb_proba[1]])
        
        # Confidence score (0-100)
        confidence = int(model_agreement * 100)
        
        # Position sizing recommendation
        if confidence >= 80:
            position_size = 'Full'
            risk_level = 'Low'
        elif confidence >= 60:
            position_size = 'Half'
            risk_level = 'Medium'
        else:
            position_size = 'Quarter'
            risk_level = 'High'
        
        return {
            'prediction': 'Success' if ensemble_proba[1] > 0.5 else 'Failure',
            'success_probability': float(ensemble_proba[1]),
            'confidence': confidence,
            'uncertainty': float(prediction_uncertainty),
            'rf_probability': float(rf_proba[1]),
            'gb_probability': float(gb_proba[1]),
            'model_agreement': float(model_agreement),
            'position_size_recommendation': position_size,
            'risk_level': risk_level,
            'ensemble_vote': {
                'random_forest': 'Success' if rf_proba[1] > 0.5 else 'Failure',
                'gradient_boosting': 'Success' if gb_proba[1] > 0.5 else 'Failure'
            }
        }
    
    def predict_multi_target(self, signal: Dict) -> Dict:
        """Predict probabilities for 1R, 2R, 3R targets"""
        predictions = {}
        
        for target in [1, 2, 3]:
            cursor = self.db.conn.cursor()
            cursor.execute("""
                SELECT 
                    session,
                    bias,
                    CASE WHEN COALESCE(mfe_none, mfe, 0) >= %s THEN 1 ELSE 0 END as hit_target
                FROM signal_lab_trades
                WHERE COALESCE(mfe_none, mfe, 0) IS NOT NULL
                AND active_trade = false
                LIMIT 1000
            """, (target,))
            
            data = cursor.fetchall()
            if len(data) < 30:
                predictions[f'{target}R'] = {'probability': 0.5, 'confidence': 0}
                continue
            
            # Quick model for this target
            session_map = {'NY AM': 1, 'NY PM': 2, 'London': 3, 'Asia': 4}
            X = np.array([[
                session_map.get(row['session'], 0),
                1 if row['bias'] == 'Bullish' else 0
            ] for row in data])
            y = np.array([row['hit_target'] for row in data])
            
            model = RandomForestClassifier(n_estimators=50, random_state=42)
            model.fit(X, y)
            
            # Predict
            features = np.array([[
                session_map.get(signal.get('session', 'NY AM'), 1),
                1 if signal.get('bias', 'Bullish') == 'Bullish' else 0
            ]])
            
            proba = model.predict_proba(features)[0][1]
            
            predictions[f'{target}R'] = {
                'probability': float(proba),
                'confidence': int(model.score(X, y) * 100)
            }
        
        return predictions
    
    def get_prediction_calibration(self) -> Dict:
        """Check if predictions are well-calibrated"""
        if not self.is_trained:
            self.train_models()
        
        if not self.is_trained:
            return {'error': 'Insufficient data'}
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT 
                session,
                bias,
                CASE WHEN COALESCE(mfe_none, mfe, 0) >= 1 THEN 1 ELSE 0 END as success
            FROM signal_lab_trades
            WHERE COALESCE(mfe_none, mfe, 0) IS NOT NULL
            AND active_trade = false
            LIMIT 500
        """)
        
        data = cursor.fetchall()
        session_map = {'NY AM': 1, 'NY PM': 2, 'London': 3, 'Asia': 4}
        
        X = np.array([[
            session_map.get(row['session'], 0),
            1 if row['bias'] == 'Bullish' else 0
        ] for row in data])
        y = np.array([row['success'] for row in data])
        
        # Get predictions
        y_pred_proba = self.rf_model.predict_proba(X)[:, 1]
        
        # Calculate calibration
        try:
            fraction_of_positives, mean_predicted_value = calibration_curve(
                y, y_pred_proba, n_bins=5
            )
            
            calibration_data = []
            for i in range(len(fraction_of_positives)):
                calibration_data.append({
                    'predicted': float(mean_predicted_value[i]),
                    'actual': float(fraction_of_positives[i])
                })
            
            return {'calibration': calibration_data}
        except:
            return {'calibration': []}
    
    def get_live_prediction(self) -> Dict:
        """Get prediction for most recent signal"""
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT session, bias, created_at
            FROM signal_lab_trades
            WHERE active_trade = true
            ORDER BY created_at DESC
            LIMIT 1
        """)
        
        signal = cursor.fetchone()
        if not signal:
            return {'status': 'no_active_signal'}
        
        # Get prediction
        prediction = self.predict_with_confidence({
            'session': signal['session'],
            'bias': signal['bias']
        })
        
        # Get multi-target predictions
        multi_target = self.predict_multi_target({
            'session': signal['session'],
            'bias': signal['bias']
        })
        
        return {
            'signal': {
                'session': signal['session'],
                'bias': signal['bias'],
                'timestamp': signal['created_at'].isoformat()
            },
            'prediction': prediction,
            'multi_target': multi_target,
            'status': 'success'
        }
