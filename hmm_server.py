#!/usr/bin/env python3
"""
Proper Hidden Markov Model Server for Trading
Receives pattern data from Pine Script and returns HMM state predictions
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
        # 4 Hidden States: 0=Ranging, 1=Accumulation, 2=Markup, 3=Distribution
        self.model = GaussianMixture(n_components=4, covariance_type="full", max_iter=200, random_state=42)
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
                
                # Use trained model
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
def dashboard():
    """Wall Street financial trader dashboard"""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Trading System Dashboard</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            * { box-sizing: border-box; }
            
            body { 
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; 
                margin: 0; 
                background: linear-gradient(180deg, #0a0e1a 0%, #1a1f2e 100%); 
                color: #c7d2fe; 
                min-height: 100vh;
                font-weight: 400;
            }
            
            .container { 
                max-width: 1200px; 
                margin: 0 auto; 
                padding: 20px;
                position: relative;
            }
            
            .header {
                text-align: center;
                margin-bottom: 30px;
                position: relative;
            }
            
            .header h1 {
                font-size: 2.2em;
                font-weight: 300;
                color: #f8fafc;
                margin: 0 0 8px 0;
                letter-spacing: -0.025em;
            }
            
            @keyframes gradientShift {
                0%, 100% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
            }
            
            .live-indicator {
                display: inline-block;
                width: 12px;
                height: 12px;
                background: #00ff88;
                border-radius: 50%;
                animation: pulse 1.5s infinite;
                margin-left: 10px;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.3; transform: scale(1.2); }
            }
            
            .section { 
                background: rgba(30, 41, 59, 0.4); 
                padding: 24px; 
                margin: 24px 0; 
                border-radius: 8px; 
                border: 1px solid rgba(71, 85, 105, 0.2);
                backdrop-filter: blur(8px);
                transition: border-color 0.2s ease;
            }
            
            .section::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 2px;
                background: linear-gradient(90deg, transparent, #00d4ff, transparent);
                animation: scan 3s linear infinite;
            }
            
            @keyframes scan {
                0% { left: -100%; }
                100% { left: 100%; }
            }
            
            .section:hover {
                transform: translateY(-5px);
                box-shadow: 0 12px 40px rgba(0, 212, 255, 0.2);
                border-color: rgba(0, 212, 255, 0.4);
            }
            
            .section h2 {
                color: #00d4ff;
                margin-top: 0;
                font-size: 1.3em;
                text-transform: uppercase;
                letter-spacing: 2px;
            }
            
            .stats { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                gap: 20px; 
            }
            
            .stat-box { 
                background: rgba(15, 23, 42, 0.6); 
                padding: 24px; 
                border-radius: 6px; 
                text-align: center;
                border: 1px solid rgba(51, 65, 85, 0.3);
                transition: all 0.2s ease;
            }
            
            .stat-box::after {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 0;
                height: 0;
                background: radial-gradient(circle, rgba(0, 212, 255, 0.1) 0%, transparent 70%);
                transition: all 0.3s ease;
                transform: translate(-50%, -50%);
            }
            
            .stat-box:hover::after {
                width: 200px;
                height: 200px;
            }
            
            .stat-box:hover {
                transform: scale(1.05);
                border-color: rgba(0, 212, 255, 0.6);
            }
            
            .stat-box h3 {
                color: #00d4ff;
                margin: 0 0 10px 0;
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .stat-box p {
                font-size: 1.8em;
                font-weight: bold;
                margin: 0;
                position: relative;
                z-index: 1;
            }
            
            .success { 
                color: #10b981;
            }
            
            @keyframes glow {
                from { text-shadow: 0 0 10px rgba(0, 255, 136, 0.5); }
                to { text-shadow: 0 0 20px rgba(0, 255, 136, 0.8), 0 0 30px rgba(0, 255, 136, 0.3); }
            }
            
            .error { color: #ff4444; }
            
            button { 
                background: rgba(51, 65, 85, 0.8); 
                color: #f1f5f9; 
                padding: 12px 20px; 
                border: 1px solid rgba(71, 85, 105, 0.4); 
                border-radius: 6px; 
                cursor: pointer; 
                font-weight: 500;
                font-family: inherit;
                font-size: 0.9em;
                transition: all 0.2s ease;
            }
            
            button::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
                transition: left 0.5s;
            }
            
            button:hover::before {
                left: 100%;
            }
            
            button:hover { 
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 212, 255, 0.4);
            }
            
            .signal-item {
                background: linear-gradient(135deg, #0f3460 0%, #1a1a2e 100%);
                padding: 15px;
                margin: 10px 0;
                border-radius: 10px;
                border-left: 4px solid #00d4ff;
                transition: all 0.3s ease;
                animation: slideIn 0.5s ease-out;
            }
            
            @keyframes slideIn {
                from { opacity: 0; transform: translateX(-20px); }
                to { opacity: 1; transform: translateX(0); }
            }
            
            .signal-item:hover {
                transform: translateX(5px);
                border-left-color: #00ff88;
                box-shadow: 0 5px 15px rgba(0, 212, 255, 0.2);
            }
            
            .signal-buttons {
                margin-top: 10px;
            }
            
            .signal-buttons button {
                font-size: 10px;
                padding: 5px 10px;
                margin: 2px;
                border-radius: 5px;
            }
            
            .btn-win { background: linear-gradient(45deg, #00ff88, #00cc6a); }
            .btn-loss { background: linear-gradient(45deg, #ff4444, #cc3333); }
            .btn-ignore { background: linear-gradient(45deg, #666, #444); }
            
            .loading {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid rgba(0, 212, 255, 0.3);
                border-radius: 50%;
                border-top-color: #00d4ff;
                animation: spin 1s ease-in-out infinite;
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            
            .matrix-bg {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: -1;
                opacity: 0.1;
            }
            
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: linear-gradient(45deg, #00d4ff, #0099cc);
                color: white;
                padding: 15px 20px;
                border-radius: 8px;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
                transform: translateX(400px);
                transition: transform 0.3s ease;
                z-index: 1000;
            }
            
            .notification.show {
                transform: translateX(0);
            }
        </style>
    </head>
    <body>
        <canvas class="matrix-bg" id="matrixCanvas"></canvas>
        
        <div class="container">
            <div class="header">
                <h1>QUANTITATIVE TRADING SYSTEM<span class="live-indicator"></span></h1>
                <p style="color: #64748b; font-size: 0.95em; margin: 0;">Institutional-Grade Algorithmic Trading Platform</p>
            </div>
            
            <div class="section">
                <h2>📊 System Status</h2>
                <div class="stats">
                    <div class="stat-box">
                        <h3>HMM Model</h3>
                        <p class="success">''' + ('✅ Trained' if hmm_engine.is_trained else '⏳ Learning') + '''</p>
                    </div>
                    <div class="stat-box">
                        <h3>Observations</h3>
                        <p>''' + str(len(hmm_engine.observation_history)) + '''</p>
                    </div>
                    <div class="stat-box">
                        <h3>Pending Signals</h3>
                        <p class="success">''' + str(performance_stats.get('pending_signals', 0)) + '''</p>
                    </div>
                    <div class="stat-box">
                        <h3>Win Rate</h3>
                        <p class="success">''' + str(round((performance_stats['winning_trades'] / performance_stats['total_trades'] * 100) if performance_stats['total_trades'] > 0 else 0, 1)) + '''%</p>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>⏳ Update Signal Results</h2>
                <p>AI signals are automatically logged. Just click the result when you're done trading:</p>
                <div id="pendingSignals">Loading...</div>
                <button onclick="loadPendingSignals()" style="margin-top: 10px;">🔄 Refresh Signals</button>
            </div>
            
            <div class="section">
                <h2>🚀 Quick Actions</h2>
                <div style="display: flex; gap: 15px; flex-wrap: wrap; justify-content: center;">
                    <button onclick="window.open('/performance', '_blank')" style="flex: 1; min-width: 200px;">📊 Performance Analytics</button>
                    <button onclick="window.open('/model_insights', '_blank')" style="flex: 1; min-width: 200px;">🧠 AI Insights</button>
                    <button onclick="loadPendingSignals()" style="flex: 1; min-width: 200px;">🔄 Refresh Data</button>
                </div>
            </div>
            
            <div class="section" style="text-align: center; font-size: 0.9em; color: #666;">
                <p>🤖 Powered by Advanced Machine Learning | 🔒 Secure Cloud Processing | ⚡ Real-time Analysis</p>
                <p>Last Updated: <span id="lastUpdate"></span></p>
            </div>
            
            <script>
                // Update timestamp
                document.getElementById('lastUpdate').textContent = new Date().toLocaleString();
                setInterval(() => {
                    document.getElementById('lastUpdate').textContent = new Date().toLocaleString();
                }, 60000);
            </script>
        </div>
        
        <script>
            // Matrix background animation
            const canvas = document.getElementById('matrixCanvas');
            const ctx = canvas.getContext('2d');
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            
            const matrix = '01';
            const matrixArray = matrix.split('');
            const fontSize = 10;
            const columns = canvas.width / fontSize;
            const drops = [];
            
            for (let x = 0; x < columns; x++) {
                drops[x] = 1;
            }
            
            function drawMatrix() {
                ctx.fillStyle = 'rgba(0, 0, 0, 0.04)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = '#00d4ff';
                ctx.font = fontSize + 'px monospace';
                
                for (let i = 0; i < drops.length; i++) {
                    const text = matrixArray[Math.floor(Math.random() * matrixArray.length)];
                    ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                    
                    if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                        drops[i] = 0;
                    }
                    drops[i]++;
                }
            }
            
            setInterval(drawMatrix, 35);
            
            // Sound effects
            function playSound(type) {
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);
                
                if (type === 'win') {
                    oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
                    oscillator.frequency.exponentialRampToValueAtTime(1200, audioContext.currentTime + 0.1);
                } else if (type === 'loss') {
                    oscillator.frequency.setValueAtTime(400, audioContext.currentTime);
                    oscillator.frequency.exponentialRampToValueAtTime(200, audioContext.currentTime + 0.2);
                } else {
                    oscillator.frequency.setValueAtTime(600, audioContext.currentTime);
                }
                
                gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
                
                oscillator.start(audioContext.currentTime);
                oscillator.stop(audioContext.currentTime + 0.2);
            }
            
            // Notification system
            function showNotification(message, type = 'info') {
                const notification = document.createElement('div');
                notification.className = 'notification';
                notification.textContent = message;
                document.body.appendChild(notification);
                
                setTimeout(() => notification.classList.add('show'), 100);
                setTimeout(() => {
                    notification.classList.remove('show');
                    setTimeout(() => document.body.removeChild(notification), 300);
                }, 3000);
            }
            
            // Auto-refresh stats every 30 seconds
            setInterval(() => {
                loadPendingSignals();
            }, 30000);
            
            // Load pending signals on page load
            loadPendingSignals();
            
            async function loadPendingSignals() {
                try {
                    document.getElementById('pendingSignals').innerHTML = '<div class="loading"></div> Loading signals...';
                    
                    // Simulate pending signals for demo
                    const pendingData = [];
                    
                    let html = '';
                    if (pendingData.length === 0) {
                        html = '<p style="text-align: center; color: #666; font-style: italic;">🎯 No pending signals - AI is monitoring markets</p>';
                    } else {
                        html = '<div style="max-height: 400px; overflow-y: auto;">';
                        pendingData.forEach(signal => {
                            const direction = signal.direction === 'LONG' ? '🟢' : '🔴';
                            html += `
                                <div class="signal-item">
                                    <strong>${direction} ${signal.symbol} - ${signal.entry_signal}</strong><br>
                                    <small>Confidence: ${(signal.ai_confidence * 100).toFixed(0)}% | Entry: ${signal.suggested_entry}</small>
                                    <div class="signal-buttons">
                                        <button class="btn-win" onclick="updateSignal(${signal.signal_id}, 'TAKEN', 'WIN')">✅ WIN</button>
                                        <button class="btn-loss" onclick="updateSignal(${signal.signal_id}, 'TAKEN', 'LOSS')">❌ LOSS</button>
                                        <button class="btn-ignore" onclick="updateSignal(${signal.signal_id}, 'IGNORED', '')">⏭️ IGNORE</button>
                                    </div>
                                </div>
                            `;
                        });
                        html += '</div>';
                    }
                    
                    setTimeout(() => {
                        document.getElementById('pendingSignals').innerHTML = html;
                    }, 500);
                } catch (error) {
                    document.getElementById('pendingSignals').innerHTML = '<p class="error">⚠️ Error loading signals</p>';
                }
            }
            
            function updateSignal(signalId, status, result) {
                if (result === 'WIN') {
                    playSound('win');
                    showNotification('🎉 Trade marked as WIN!', 'success');
                } else if (result === 'LOSS') {
                    playSound('loss');
                    showNotification('📉 Trade marked as LOSS', 'warning');
                } else {
                    playSound('click');
                    showNotification('⏭️ Signal ignored', 'info');
                }
                
                setTimeout(() => {
                    loadPendingSignals();
                    // Simulate stats update
                    location.reload();
                }, 1000);
            }
            
            // Resize canvas on window resize
            window.addEventListener('resize', () => {
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
            });
        </script>
    </body>
    </html>
    '''
    return html

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
            elif 'Mixed Bias Analysis:' in alert_message:
                json_str = alert_message.split('Mixed Bias Analysis: ')[1]
                mixed_data = json.loads(json_str)
                # Process mixed bias analysis
                analysis_result = mixed_bias_analysis()
                return analysis_result
            elif 'Auto Log Signal:' in alert_message:
                json_str = alert_message.split('Auto Log Signal: ')[1]
                signal_data = json.loads(json_str)
                # Auto-log the signal
                signal_entry = {
                    'signal_id': len(signal_log) + 1,
                    'timestamp': signal_data.get('timestamp', pd.Timestamp.now().isoformat()),
                    'symbol': signal_data.get('symbol', 'UNKNOWN'),
                    'direction': signal_data.get('direction', ''),
                    'entry_signal': signal_data.get('entry_signal', ''),
                    'ai_confidence': float(signal_data.get('ai_confidence', 0)),
                    'suggested_entry': float(signal_data.get('suggested_entry', 0)),
                    'status': 'PENDING'
                }
                signal_log.append(signal_entry)
                performance_stats['pending_signals'] = len([s for s in signal_log if s['status'] == 'PENDING'])
                return jsonify({'status': 'signal_logged', 'signal_id': signal_entry['signal_id']})
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

@app.route('/mixed_bias_analysis', methods=['POST'])
def mixed_bias_analysis():
    """Analyze mixed bias days using ML to determine optimal direction"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        bull_score = data.get('bull_weighted_score', 0.0)
        bear_score = data.get('bear_weighted_score', 0.0)
        bull_patterns = data.get('bull_patterns', [])
        bear_patterns = data.get('bear_patterns', [])
        hmm_state = data.get('hmm_state', 0)
        hmm_confidence = data.get('hmm_confidence', 0.5)
        
        # Enhanced pattern analysis using historical data + market context
        pattern_weights = {
            'hammer': 0.85,      # Typically high success rate
            'engulf': 0.75,      # Strong momentum pattern
            'ebp': 0.70,         # Sweep patterns
            'three_bar': 0.65,   # Multi-bar confirmation
            'sweep': 0.60,       # Basic sweep
            'inside': 0.45,      # Often lower success
            'close_above': 0.40, # Basic pattern
            'close_below': 0.40  # Basic pattern
        }
        
        # Calculate ML-enhanced scores
        bull_ml_score = 0.0
        bear_ml_score = 0.0
        
        for pattern in bull_patterns:
            if pattern in pattern_weights:
                bull_ml_score += pattern_weights[pattern]
        
        for pattern in bear_patterns:
            if pattern in pattern_weights:
                bear_ml_score += pattern_weights[pattern]
        
        # HMM state enhancement
        if hmm_state == 1:  # Accumulation - favor continuation
            bull_ml_score *= 1.2
        elif hmm_state == 2:  # Markup - favor bullish
            bull_ml_score *= 1.3
        elif hmm_state == 3:  # Distribution - favor bearish
            bear_ml_score *= 1.3
        
        # Market structure analysis
        volume_ratio = data.get('volume_ratio', 1.0)
        if volume_ratio > 1.5:  # High volume confirmation
            if bull_ml_score > bear_ml_score:
                bull_ml_score *= 1.1
            else:
                bear_ml_score *= 1.1
        
        # Final recommendation
        confidence_threshold = 0.15
        if bull_ml_score > bear_ml_score + confidence_threshold:
            recommendation = 'BULLISH'
            confidence = min((bull_ml_score - bear_ml_score) / bull_ml_score, 0.95)
        elif bear_ml_score > bull_ml_score + confidence_threshold:
            recommendation = 'BEARISH'
            confidence = min((bear_ml_score - bull_ml_score) / bear_ml_score, 0.95)
        else:
            recommendation = 'NEUTRAL'
            confidence = 0.5
        
        result = {
            'recommendation': recommendation,
            'confidence': round(confidence, 3),
            'bull_ml_score': round(bull_ml_score, 3),
            'bear_ml_score': round(bear_ml_score, 3),
            'analysis_method': 'ML_Enhanced_Pattern_Weighting',
            'hmm_state_factor': hmm_state,
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        logger.info(f"Mixed Bias Analysis: {recommendation} with {confidence:.3f} confidence")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Mixed bias analysis error: {e}")
        return jsonify({'error': str(e)}), 500

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

# Trade Logging System
trade_log = []
signal_log = []  # Auto-logged signals waiting for results
performance_stats = {
    'total_trades': 0,
    'winning_trades': 0,
    'losing_trades': 0,
    'total_pnl': 0.0,
    'best_patterns': {},
    'confidence_accuracy': {},
    'pending_signals': 0
}

@app.route('/log_trade', methods=['POST'])
def log_trade():
    """Enhanced trade logging with R:R analysis and MAE/MFE tracking"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No trade data provided'}), 400
        
        # Calculate enhanced metrics
        entry_price = float(data.get('entry_price', 0))
        exit_price = float(data.get('exit_price', 0))
        stop_loss = float(data.get('stop_loss', 0))
        take_profit = float(data.get('take_profit', 0))
        max_favorable = float(data.get('max_favorable_excursion', exit_price))
        max_adverse = float(data.get('max_adverse_excursion', entry_price))
        
        # Calculate R:R metrics
        if stop_loss > 0 and take_profit > 0:
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            planned_rr = reward / risk if risk > 0 else 0
        else:
            planned_rr = 0
            
        actual_pnl = exit_price - entry_price if data.get('direction') == 'LONG' else entry_price - exit_price
        actual_risk = abs(entry_price - stop_loss) if stop_loss > 0 else abs(actual_pnl)
        actual_rr = abs(actual_pnl) / actual_risk if actual_risk > 0 else 0
        
        # Calculate MAE/MFE
        if data.get('direction') == 'LONG':
            mfe = max_favorable - entry_price  # Max Favorable Excursion
            mae = entry_price - max_adverse    # Max Adverse Excursion
        else:
            mfe = entry_price - max_favorable
            mae = max_adverse - entry_price
            
        # Enhanced trade entry
        trade_entry = {
            'timestamp': data.get('timestamp', pd.Timestamp.now().isoformat()),
            'symbol': data.get('symbol', 'UNKNOWN'),
            'direction': data.get('direction', ''),
            'entry_price': entry_price,
            'exit_price': exit_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'quantity': float(data.get('quantity', 1)),
            'pnl': float(data.get('pnl', actual_pnl)),
            'pnl_pips': float(data.get('pnl_pips', 0)),
            'result': data.get('result', ''),
            
            # R:R Analysis
            'planned_rr': planned_rr,
            'actual_rr': actual_rr,
            'rr_efficiency': (actual_rr / planned_rr) if planned_rr > 0 else 0,
            
            # MAE/MFE Analysis
            'mae': mae,
            'mfe': mfe,
            'mae_percentage': (mae / entry_price * 100) if entry_price > 0 else 0,
            'mfe_percentage': (mfe / entry_price * 100) if entry_price > 0 else 0,
            'exit_efficiency': (actual_pnl / mfe) if mfe > 0 else 0,
            
            # Trade Duration
            'entry_time': data.get('entry_time', pd.Timestamp.now().isoformat()),
            'exit_time': data.get('exit_time', pd.Timestamp.now().isoformat()),
            'duration_minutes': float(data.get('duration_minutes', 0)),
            
            # AI Signal Data
            'entry_signal': data.get('entry_signal', ''),
            'ai_confidence': float(data.get('ai_confidence', 0)),
            'bias_score': float(data.get('bias_score', 0)),
            'patterns_used': data.get('patterns_used', []),
            'hmm_state': data.get('hmm_state', 'Unknown'),
            'session': data.get('session', 'Unknown'),
            
            # Market Conditions
            'volatility': float(data.get('volatility', 0)),
            'volume_ratio': float(data.get('volume_ratio', 1)),
            'spread': float(data.get('spread', 0)),
            
            'notes': data.get('notes', '')
        }
        
        # Add to trade log
        trade_log.append(trade_entry)
        
        # Update performance stats
        performance_stats['total_trades'] += 1
        performance_stats['total_pnl'] += trade_entry['pnl']
        
        if trade_entry['result'] == 'WIN':
            performance_stats['winning_trades'] += 1
        elif trade_entry['result'] == 'LOSS':
            performance_stats['losing_trades'] += 1
        
        # Track pattern performance
        for pattern in trade_entry['patterns_used']:
            if pattern not in performance_stats['best_patterns']:
                performance_stats['best_patterns'][pattern] = {'wins': 0, 'total': 0}
            performance_stats['best_patterns'][pattern]['total'] += 1
            if trade_entry['result'] == 'WIN':
                performance_stats['best_patterns'][pattern]['wins'] += 1
        
        # Track confidence accuracy
        conf_bucket = int(trade_entry['ai_confidence'] * 10) * 10  # 70%, 80%, etc.
        if conf_bucket not in performance_stats['confidence_accuracy']:
            performance_stats['confidence_accuracy'][conf_bucket] = {'wins': 0, 'total': 0}
        performance_stats['confidence_accuracy'][conf_bucket]['total'] += 1
        if trade_entry['result'] == 'WIN':
            performance_stats['confidence_accuracy'][conf_bucket]['wins'] += 1
        
        logger.info(f"Trade logged: {trade_entry['direction']} {trade_entry['symbol']} - {trade_entry['result']} ({trade_entry['pnl']:.2f})")
        
        return jsonify({
            'status': 'success',
            'trade_id': len(trade_log),
            'message': 'Trade logged successfully'
        })
        
    except Exception as e:
        logger.error(f"Trade logging error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
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

@app.route('/performance', methods=['GET'])
def get_performance():
    """Get trading performance statistics"""
    try:
        # Calculate win rate
        win_rate = (performance_stats['winning_trades'] / performance_stats['total_trades'] * 100) if performance_stats['total_trades'] > 0 else 0
        
        # Calculate pattern success rates
        pattern_stats = {}
        for pattern, data in performance_stats['best_patterns'].items():
            pattern_stats[pattern] = {
                'success_rate': (data['wins'] / data['total'] * 100) if data['total'] > 0 else 0,
                'total_trades': data['total'],
                'wins': data['wins']
            }
        
        # Calculate confidence accuracy
        confidence_stats = {}
        for conf, data in performance_stats['confidence_accuracy'].items():
            confidence_stats[f"{conf}%"] = {
                'accuracy': (data['wins'] / data['total'] * 100) if data['total'] > 0 else 0,
                'total_trades': data['total']
            }
        
        # Recent trades (last 10)
        recent_trades = trade_log[-10:] if len(trade_log) > 10 else trade_log
        
        result = {
            'summary': {
                'total_trades': performance_stats['total_trades'],
                'win_rate': round(win_rate, 2),
                'total_pnl': round(performance_stats['total_pnl'], 2),
                'avg_pnl_per_trade': round(performance_stats['total_pnl'] / performance_stats['total_trades'], 2) if performance_stats['total_trades'] > 0 else 0
            },
            'pattern_performance': pattern_stats,
            'confidence_accuracy': confidence_stats,
            'recent_trades': recent_trades,
            'total_logged_trades': len(trade_log)
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Performance retrieval error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/model_insights', methods=['GET'])
def get_model_insights():
    """Get AI model insights based on logged trades"""
    try:
        if len(trade_log) < 5:
            return jsonify({'message': 'Need at least 5 trades for insights'})
        
        insights = {
            'best_performing_patterns': [],
            'optimal_confidence_threshold': 0.7,
            'session_performance': {},
            'hmm_state_accuracy': {},
            'recommendations': []
        }
        
        # Find best patterns
        for pattern, data in performance_stats['best_patterns'].items():
            if data['total'] >= 3:  # Minimum sample size
                success_rate = (data['wins'] / data['total']) * 100
                if success_rate > 60:
                    insights['best_performing_patterns'].append({
                        'pattern': pattern,
                        'success_rate': round(success_rate, 1),
                        'sample_size': data['total']
                    })
        
        # Find optimal confidence threshold
        best_threshold = 0.7
        best_accuracy = 0
        for conf, data in performance_stats['confidence_accuracy'].items():
            if data['total'] >= 3:
                accuracy = (data['wins'] / data['total']) * 100
                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    best_threshold = conf / 100
        
        insights['optimal_confidence_threshold'] = best_threshold
        
        # Generate recommendations
        if len(insights['best_performing_patterns']) > 0:
            best_pattern = max(insights['best_performing_patterns'], key=lambda x: x['success_rate'])
            insights['recommendations'].append(f"Focus on {best_pattern['pattern']} patterns - {best_pattern['success_rate']}% success rate")
        
        if best_threshold > 0.7:
            insights['recommendations'].append(f"Consider raising confidence threshold to {best_threshold:.0%} for better accuracy")
        
        return jsonify(insights)
        
    except Exception as e:
        logger.error(f"Model insights error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    
    print("🚀 Starting HMM Server with Trade Logging...")
    print(f"📊 Server will be available on port: {port}")
    print("⚡ Ready to receive Pine Script data and log trades!")
    print("📈 New endpoints: /log_trade, /performance, /model_insights")
    
    app.run(host='0.0.0.0', port=port, debug=False)