#!/usr/bin/env python3
"""
Proper Hidden Markov Model Server for Trading
Receives pattern data from Pine Script and returns HMM state predictions
"""

import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from hmmlearn.hmm import GaussianHMM
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingHMM:
    def __init__(self):
        # 4 Hidden States: 0=Ranging, 1=Accumulation, 2=Markup, 3=Distribution
        self.model = GaussianHMM(n_components=4, covariance_type="full", n_iter=200, random_state=42)
        self.states = ['Ranging', 'Accumulation', 'Markup', 'Distribution']
        self.is_trained = False
        self.observation_history = []
        self.scaler = None
        self.feature_importance = np.zeros(14)
        self.training_score = 0.0
        self.validation_score = 0.0
        
    def prepare_features(self, data):
        """Convert trading data to comprehensive HMM observation features"""
        try:
            # Extract 12 comprehensive features
            features = np.array([
                data.get('volume_ratio', 1.0),              # Volume strength
                data.get('price_momentum', 0.0),            # Price momentum
                data.get('time_of_day', 12) / 24.0,         # Session timing (0-1)
                data.get('day_of_week', 3) / 7.0,           # Weekly patterns (0-1)
                data.get('trend_strength', 0.0) / 100.0,    # Trend context (-1 to 1)
                data.get('support_distance', 5.0) / 100.0,  # Distance to support
                data.get('resistance_distance', 5.0) / 100.0, # Distance to resistance
                data.get('pattern_sequence_score', 1.0),    # Pattern sequence multiplier
                data.get('market_regime_score', 0.0),       # Regime (-1, 0, 1)
                data.get('volatility_percentile', 50.0) / 100.0, # Volatility rank
                data.get('volume_profile', 1.0),            # Volume profile
                data.get('price_position', 0.5),            # Position in range (0-1)
                data.get('momentum_divergence', 0.0),       # Momentum divergence
                data.get('atr_value', 1.0) / data.get('current_price', 1.0) * 1000  # Normalized ATR
            ]).reshape(1, -1)
            
            return features
        except Exception as e:
            logger.error(f"Feature preparation error: {e}")
            return np.array([[1.0, 0.0, 0.5, 0.4, 0.0, 0.05, 0.05, 1.0, 0.0, 0.5, 1.0, 0.5, 0.0, 0.001]])
    
    def train_model(self, historical_data):
        """Train HMM on historical observations"""
        try:
            if len(historical_data) < 10:
                logger.warning("Not enough data for training")
                return False
                
            # Prepare feature matrix
            features = []
            for data_point in historical_data:
                feat = self.prepare_features(data_point).flatten()
                features.append(feat)
            
            X = np.array(features)
            
            # Train HMM
            self.model.fit(X)
            self.is_trained = True
            logger.info(f"HMM trained on {len(historical_data)} observations")
            return True
            # Prepare feature matrix
            features = []
            for data_point in historical_data:
                feat = self.prepare_features(data_point).flatten()
                features.append(feat)
            
            X = np.array(features)
            
            # Feature scaling
            from sklearn.preprocessing import StandardScaler
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Train-validation split (80-20)
            split_idx = int(len(X_scaled) * 0.8)
            X_train = X_scaled[:split_idx]
            X_val = X_scaled[split_idx:]
            
            # Train HMM
            self.model.fit(X_train)
            
            # Calculate scores
            self.training_score = self.model.score(X_train)
            self.validation_score = self.model.score(X_val) if len(X_val) > 0 else self.training_score
            
            # Feature importance (variance of each feature across states)
            state_means = self.model.means_
            self.feature_importance = np.var(state_means, axis=0)
            
            self.is_trained = True
            logger.info(f"HMM trained: {len(historical_data)} obs, train_score: {self.training_score:.3f}, val_score: {self.validation_score:.3f}")
            logger.info(f"Top features: {np.argsort(self.feature_importance)[-3:][::-1]}")
            return True
            
        except Exception as e:
            logger.error(f"Training error: {e}")
            return False
    
    def predict_state(self, current_data):
        """Predict current market state using HMM"""
        try:
            # Prepare current observation
            X = self.prepare_features(current_data)
            
            if not self.is_trained:
                # Use simple heuristics if not trained
                pattern_strength = current_data.get('pattern_strength', 0.5)
                volume_ratio = current_data.get('volume_ratio', 1.0)
                
                if volume_ratio > 1.5 and pattern_strength > 0.7:
                    state = 2  # Markup
                    confidence = 0.75
                elif volume_ratio > 1.2 and pattern_strength > 0.6:
                    state = 1  # Accumulation
                    confidence = 0.65
                elif pattern_strength < 0.4:
                    state = 0  # Ranging
                    confidence = 0.6
                else:
                    state = 3  # Distribution
                    confidence = 0.55
                    
                probabilities = [0.25, 0.25, 0.25, 0.25]
                probabilities[state] = confidence
                
            else:
                # Scale features using trained scaler
                if self.scaler is not None:
                    X = self.scaler.transform(X)
                
                # Use trained HMM
                state_probs = self.model.predict_proba(X)
                predicted_states = self.model.predict(X)
                
                state = int(predicted_states[0])
                confidence = float(np.max(state_probs[0]))
                probabilities = state_probs[0].tolist()
                
                # Enhanced confidence with entropy
                entropy = -np.sum(state_probs[0] * np.log(state_probs[0] + 1e-10))
                normalized_confidence = confidence * (1 - entropy / np.log(4))  # 4 states
            
            # Store observation for future training
            self.observation_history.append(current_data)
            if len(self.observation_history) > 1000:
                self.observation_history = self.observation_history[-500:]  # Keep recent data
            
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
CORS(app)  # Allow cross-origin requests
hmm_engine = TradingHMM()

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint with model performance"""
    return jsonify({
        'status': 'HMM Server Running',
        'is_trained': hmm_engine.is_trained,
        'observations': len(hmm_engine.observation_history),
        'training_score': round(hmm_engine.training_score, 4) if hmm_engine.is_trained else 0,
        'validation_score': round(hmm_engine.validation_score, 4) if hmm_engine.is_trained else 0,
        'top_features': np.argsort(hmm_engine.feature_importance)[-3:][::-1].tolist() if hmm_engine.is_trained else []
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Main prediction endpoint for Pine Script"""
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

@app.route('/market_structure', methods=['POST'])
def market_structure():
    """Analyze current market structure for entry timing"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract market structure data
        highs = data.get('recent_highs', [])
        lows = data.get('recent_lows', [])
        volumes = data.get('recent_volumes', [])
        
        structure_analysis = {
            'trend_strength': 0.0,
            'support_level': 0.0,
            'resistance_level': 0.0,
            'breakout_probability': 0.0,
            'optimal_entry_zone': [0.0, 0.0]
        }
        
        if len(highs) >= 3 and len(lows) >= 3:
            # Calculate trend strength
            recent_highs = highs[-3:]
            recent_lows = lows[-3:]
            
            higher_highs = sum(1 for i in range(1, len(recent_highs)) if recent_highs[i] > recent_highs[i-1])
            higher_lows = sum(1 for i in range(1, len(recent_lows)) if recent_lows[i] > recent_lows[i-1])
            
            structure_analysis['trend_strength'] = (higher_highs + higher_lows) / 4.0
            structure_analysis['support_level'] = min(recent_lows)
            structure_analysis['resistance_level'] = max(recent_highs)
            
            # Volume analysis
            if len(volumes) >= 3:
                avg_volume = sum(volumes[-3:]) / 3
                current_volume = volumes[-1] if volumes else 1.0
                volume_strength = current_volume / avg_volume if avg_volume > 0 else 1.0
                
                structure_analysis['breakout_probability'] = min(volume_strength * structure_analysis['trend_strength'], 1.0)
            
            # Optimal entry zone (between support and resistance)
            support = structure_analysis['support_level']
            resistance = structure_analysis['resistance_level']
            zone_size = (resistance - support) * 0.2  # 20% of range
            
            if structure_analysis['trend_strength'] > 0.5:  # Bullish
                structure_analysis['optimal_entry_zone'] = [support, support + zone_size]
            else:  # Bearish
                structure_analysis['optimal_entry_zone'] = [resistance - zone_size, resistance]
        
        return jsonify(structure_analysis)
        
    except Exception as e:
        logger.error(f"Market structure analysis error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/train', methods=['POST'])
def train():
    """Training endpoint for historical data"""
    try:
        data = request.json
        if not data or 'historical_data' not in data:
            return jsonify({'error': 'No historical data provided'}), 400
        
        success = hmm_engine.train_model(data['historical_data'])
        
        return jsonify({
            'status': 'success' if success else 'failed',
            'is_trained': hmm_engine.is_trained,
            'message': 'HMM training completed' if success else 'Training failed'
        })
        
    except Exception as e:
        logger.error(f"Training endpoint error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/retrain', methods=['POST'])
def retrain():
    """Retrain HMM on accumulated observations"""
    try:
        if len(hmm_engine.observation_history) < 20:
            return jsonify({
                'status': 'insufficient_data',
                'message': f'Need at least 20 observations, have {len(hmm_engine.observation_history)}'
            })
        
        success = hmm_engine.train_model(hmm_engine.observation_history)
        
        return jsonify({
            'status': 'success' if success else 'failed',
            'is_trained': hmm_engine.is_trained,
            'observations_used': len(hmm_engine.observation_history)
        })
        
    except Exception as e:
        logger.error(f"Retrain endpoint error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook_receiver():
    """Receive webhook data from TradingView Pine Script"""
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.json
        else:
            # Parse alert message from TradingView webhook
            alert_message = request.form.get('message', '')
            if 'Python Server Data:' in alert_message:
                json_str = alert_message.split('Python Server Data: ')[1]
                data = json.loads(json_str)
            elif 'HMM Training Data:' in alert_message:
                json_str = alert_message.split('HMM Training Data: ')[1]
                training_data = json.loads(json_str)
                hmm_engine.observation_history.append(training_data)
                return jsonify({'status': 'training_data_received'})
            else:
                return jsonify({'error': 'Unknown alert format'}), 400
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Process entry signal prediction
        result = predict_entry_signal(data)
        logger.info(f"Webhook processed: {result['entry_signal']}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

def predict_entry_signal(data):
    """Process entry signal from webhook data"""
    try:
        # Extract data
        current_price = data.get('current_price', 0.0)
        volume_ratio = data.get('volume_ratio', 1.0)
        price_momentum = data.get('price_momentum', 0.0)
        daily_bias = data.get('daily_bias', 'NEUTRAL')
        bias_score = data.get('bias_score', 50.0)
        pullback_level = data.get('pullback_level', current_price)
        resistance_level = data.get('resistance_level', current_price * 1.01)
        support_level = data.get('support_level', current_price * 0.99)
        
        # Get HMM prediction
        hmm_result = hmm_engine.predict_state({
            'pattern_strength': abs(bias_score) / 100,
            'volume_ratio': volume_ratio,
            'price_momentum': price_momentum,
            'volatility_ratio': 1.0,
            'rsi_momentum': 0.5
        })
        
        # Entry signal logic
        entry_signal = "NO_ENTRY"
        confidence = 0.0
        
        if daily_bias == "BULLISH" and bias_score >= 65 and hmm_result['state'] in [1, 2]:  # Accumulation or Markup
            if volume_ratio > 1.2 and price_momentum > 0.1:
                entry_signal = "ENTER_LONG"
                confidence = min(0.8 * hmm_result['confidence'], 0.95)
        elif daily_bias == "BEARISH" and bias_score <= -65 and hmm_result['state'] in [1, 3]:  # Accumulation or Distribution
            if volume_ratio > 1.2 and price_momentum < -0.1:
                entry_signal = "ENTER_SHORT"
                confidence = min(0.8 * hmm_result['confidence'], 0.95)
        
        return {
            'entry_signal': entry_signal,
            'confidence': round(confidence, 3),
            'hmm_state': hmm_result['state_name'],
            'hmm_confidence': hmm_result['confidence'],
            'current_price': current_price,
            'volume_ratio': volume_ratio,
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Entry signal prediction error: {e}")
        return {'entry_signal': 'ERROR', 'error': str(e)}

@app.route('/predict_entry', methods=['POST'])
def predict_entry():
    """Real-time 1M entry signal prediction"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract 1M data
        daily_bias = data.get('daily_bias', 'NEUTRAL')
        bias_score = data.get('bias_score', 50.0)
        current_price = data.get('current_price', 0.0)
        volume_ratio = data.get('volume_ratio', 1.0)
        price_momentum = data.get('price_momentum', 0.0)
        pullback_level = data.get('pullback_level', 0.0)
        resistance_level = data.get('resistance_level', 0.0)
        support_level = data.get('support_level', 0.0)
        
        # Calculate entry signal strength
        entry_signal = "NO_ENTRY"
        confidence = 0.0
        target_price = 0.0
        stop_price = 0.0
        
        # Entry Logic for BULLISH bias
        if daily_bias == "BULLISH" and bias_score >= 65:
            # Check for pullback completion
            pullback_complete = current_price <= pullback_level and volume_ratio < 0.8
            momentum_building = price_momentum > 0.1 and volume_ratio > 1.2
            
            if pullback_complete and momentum_building:
                entry_signal = "ENTER_LONG"
                confidence = min(bias_score / 100 * (1 + volume_ratio * 0.2), 0.95)
                target_price = resistance_level if resistance_level > 0 else current_price * 1.002
                stop_price = support_level if support_level > 0 else current_price * 0.998
                
            elif momentum_building and current_price > pullback_level:
                entry_signal = "MOMENTUM_LONG"
                confidence = min(bias_score / 100 * 0.8, 0.85)
                target_price = resistance_level if resistance_level > 0 else current_price * 1.0015
                stop_price = pullback_level if pullback_level > 0 else current_price * 0.9995
        
        # Entry Logic for BEARISH bias
        elif daily_bias == "BEARISH" and bias_score <= -65:
            # Check for rally completion
            rally_complete = current_price >= pullback_level and volume_ratio < 0.8
            momentum_building = price_momentum < -0.1 and volume_ratio > 1.2
            
            if rally_complete and momentum_building:
                entry_signal = "ENTER_SHORT"
                confidence = min(abs(bias_score) / 100 * (1 + volume_ratio * 0.2), 0.95)
                target_price = support_level if support_level > 0 else current_price * 0.998
                stop_price = resistance_level if resistance_level > 0 else current_price * 1.002
                
            elif momentum_building and current_price < pullback_level:
                entry_signal = "MOMENTUM_SHORT"
                confidence = min(abs(bias_score) / 100 * 0.8, 0.85)
                target_price = support_level if support_level > 0 else current_price * 0.9985
                stop_price = pullback_level if pullback_level > 0 else current_price * 1.0005
        
        # Risk/Reward calculation
        risk_reward = 0.0
        if stop_price != 0 and target_price != 0:
            risk = abs(current_price - stop_price)
            reward = abs(target_price - current_price)
            risk_reward = reward / risk if risk > 0 else 0
        
        result = {
            'entry_signal': entry_signal,
            'confidence': round(confidence, 3),
            'current_price': current_price,
            'target_price': round(target_price, 2),
            'stop_price': round(stop_price, 2),
            'risk_reward': round(risk_reward, 2),
            'volume_ratio': volume_ratio,
            'price_momentum': price_momentum,
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        logger.info(f"Entry Signal: {entry_signal} - Confidence: {confidence:.3f}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Entry prediction error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    
    print("🚀 Starting HMM Server...")
    print(f"📊 Server will be available on port: {port}")
    print("⚡ Ready to receive Pine Script data!")
    
    app.run(host='0.0.0.0', port=port, debug=False)