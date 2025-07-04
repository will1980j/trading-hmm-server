#!/usr/bin/env python3
"""
Clean Trading Dashboard Server
"""

import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import logging
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingHMM:
    def __init__(self):
        self.model = GaussianMixture(n_components=4, covariance_type="full", max_iter=200, random_state=42)
        self.states = ['Ranging', 'Accumulation', 'Markup', 'Distribution']
        self.is_trained = False
        self.observation_history = []
        self.scaler = None
        self.feature_importance = np.zeros(14)
        self.training_score = 0.0
        self.validation_score = 0.0
        
    def prepare_features(self, data):
        try:
            features = np.array([
                data.get('volume_ratio', 1.0),
                data.get('price_momentum', 0.0),
                data.get('time_of_day', 12) / 24.0,
                data.get('day_of_week', 3) / 7.0,
                data.get('trend_strength', 0.0) / 100.0,
                data.get('support_distance', 5.0) / 100.0,
                data.get('resistance_distance', 5.0) / 100.0,
                data.get('pattern_sequence_score', 1.0),
                data.get('market_regime_score', 0.0),
                data.get('volatility_percentile', 50.0) / 100.0,
                data.get('volume_profile', 1.0),
                data.get('price_position', 0.5),
                data.get('momentum_divergence', 0.0),
                data.get('atr_value', 1.0) / data.get('current_price', 1.0) * 1000
            ]).reshape(1, -1)
            return features
        except Exception as e:
            logger.error(f"Feature preparation error: {e}")
            return np.array([[1.0, 0.0, 0.5, 0.4, 0.0, 0.05, 0.05, 1.0, 0.0, 0.5, 1.0, 0.5, 0.0, 0.001]])
    
    def train_model(self, historical_data):
        try:
            if len(historical_data) < 10:
                logger.warning("Not enough data for training")
                return False
                
            features = []
            for data_point in historical_data:
                feat = self.prepare_features(data_point).flatten()
                features.append(feat)
            
            X = np.array(features)
            self.model.fit(X)
            self.is_trained = True
            logger.info(f"HMM trained on {len(historical_data)} observations")
            return True
            
        except Exception as e:
            logger.error(f"Training error: {e}")
            return False
    
    def predict_state(self, current_data):
        try:
            X = self.prepare_features(current_data)
            
            if not self.is_trained:
                pattern_strength = current_data.get('pattern_strength', 0.5)
                volume_ratio = current_data.get('volume_ratio', 1.0)
                
                if volume_ratio > 1.5 and pattern_strength > 0.7:
                    state = 2
                    confidence = 0.75
                elif volume_ratio > 1.2 and pattern_strength > 0.6:
                    state = 1
                    confidence = 0.65
                elif pattern_strength < 0.4:
                    state = 0
                    confidence = 0.6
                else:
                    state = 3
                    confidence = 0.55
                    
                probabilities = [0.25, 0.25, 0.25, 0.25]
                probabilities[state] = confidence
                
            else:
                if self.scaler is not None:
                    X = self.scaler.transform(X)
                
                state_probs = self.model.predict_proba(X)
                predicted_states = self.model.predict(X)
                
                state = int(predicted_states[0])
                confidence = float(np.max(state_probs[0]))
                probabilities = state_probs[0].tolist()
            
            self.observation_history.append(current_data)
            if len(self.observation_history) > 1000:
                self.observation_history = self.observation_history[-500:]
            
            return {
                'state': state,
                'state_name': self.states[state],
                'confidence': round(confidence, 3),
                'probabilities': [round(p, 3) for p in probabilities],
                'is_trained': self.is_trained,
                'observations_count': len(self.observation_history)
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {
                'state': 0,
                'state_name': 'Ranging',
                'confidence': 0.5,
                'probabilities': [0.25, 0.25, 0.25, 0.25],
                'is_trained': False,
                'error': str(e)
            }

# Initialize Flask app and HMM
app = Flask(__name__)
CORS(app)
hmm_engine = TradingHMM()

# Trade Logging System
trade_log = []
signal_log = []
performance_stats = {
    'total_trades': 0,
    'winning_trades': 0,
    'losing_trades': 0,
    'total_pnl': 0.0,
    'best_patterns': {},
    'confidence_accuracy': {},
    'pending_signals': 0
}

@app.route('/', methods=['GET'])
def dashboard():
    """Clean trading dashboard"""
    total_trades = performance_stats['total_trades']
    win_rate = (performance_stats['winning_trades'] / total_trades * 100) if total_trades > 0 else 0
    avg_rr = sum([t.get('actual_rr', 0) for t in trade_log]) / len(trade_log) if trade_log else 0
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Trading System Dashboard</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
            * {{ box-sizing: border-box; }}
            body {{ font-family: 'Inter', sans-serif; margin: 0; background: #0f172a; color: #cbd5e1; min-height: 100vh; }}
            .container {{ max-width: 1400px; margin: 0 auto; padding: 24px; }}
            .header {{ text-align: center; margin-bottom: 32px; border-bottom: 1px solid #334155; padding-bottom: 24px; }}
            .header h1 {{ font-size: 2em; font-weight: 300; color: #f8fafc; margin: 0; }}
            .section {{ background: #1e293b; padding: 24px; margin: 20px 0; border-radius: 8px; border: 1px solid #334155; }}
            .section h2 {{ color: #f1f5f9; margin: 0 0 20px 0; font-size: 1.1em; font-weight: 500; text-transform: uppercase; }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }}
            .stat-box {{ background: #0f172a; padding: 20px; border-radius: 6px; text-align: center; border: 1px solid #334155; }}
            .stat-box h3 {{ color: #94a3b8; margin: 0 0 10px 0; font-size: 0.8em; text-transform: uppercase; }}
            .stat-box p {{ font-size: 1.8em; font-weight: 600; margin: 0; color: #f8fafc; }}
            .success {{ color: #10b981; }}
            .warning {{ color: #f59e0b; }}
            .error {{ color: #ef4444; }}
            button {{ background: #334155; color: #f1f5f9; padding: 12px 20px; border: 1px solid #475569; border-radius: 6px; cursor: pointer; font-weight: 500; font-family: inherit; transition: all 0.2s ease; }}
            button:hover {{ background: #475569; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>TRADING SYSTEM DASHBOARD</h1>
                <p style="color: #64748b; margin: 5px 0;">Performance Analytics & Signal Management</p>
            </div>
            
            <div class="section">
                <h2>System Status</h2>
                <div class="stats">
                    <div class="stat-box">
                        <h3>Model Status</h3>
                        <p class="success">{'TRAINED' if hmm_engine.is_trained else 'LEARNING'}</p>
                    </div>
                    <div class="stat-box">
                        <h3>Total Trades</h3>
                        <p>{total_trades}</p>
                    </div>
                    <div class="stat-box">
                        <h3>Win Rate</h3>
                        <p class="{'success' if win_rate > 60 else 'warning' if win_rate > 40 else 'error'}">{win_rate:.1f}%</p>
                    </div>
                    <div class="stat-box">
                        <h3>Avg R:R</h3>
                        <p class="{'success' if avg_rr > 2 else 'warning' if avg_rr > 1 else 'error'}">{avg_rr:.2f}</p>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>Signal Management</h2>
                <div>No pending signals</div>
                <button onclick="location.reload()">REFRESH DATA</button>
            </div>
        </div>
    </body>
    </html>
    '''
    return html

@app.route('/predict', methods=['POST'])
def predict():
    """Main prediction endpoint"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        result = hmm_engine.predict_state(data)
        logger.info(f"Prediction: {result['state_name']} ({result['confidence']})")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Prediction endpoint error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'HMM Server Running',
        'is_trained': hmm_engine.is_trained,
        'observations': len(hmm_engine.observation_history)
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Starting Trading Dashboard Server...")
    app.run(host='0.0.0.0', port=port, debug=False)