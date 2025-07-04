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
import pickle
import os
from datetime import datetime
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
            # Input validation and sanitization
            volume_ratio = max(0.1, min(10.0, float(data.get('volume_ratio', 1.0))))
            price_momentum = max(-1.0, min(1.0, float(data.get('price_momentum', 0.0))))
            current_price = max(0.001, float(data.get('current_price', 1.0)))
            atr_value = max(0.0001, float(data.get('atr_value', 1.0)))
            
            features = np.array([
                volume_ratio,
                price_momentum,
                max(0, min(24, data.get('time_of_day', 12))) / 24.0,
                max(0, min(7, data.get('day_of_week', 3))) / 7.0,
                max(-100, min(100, data.get('trend_strength', 0.0))) / 100.0,
                max(0, min(100, data.get('support_distance', 5.0))) / 100.0,
                max(0, min(100, data.get('resistance_distance', 5.0))) / 100.0,
                max(0, min(5, data.get('pattern_sequence_score', 1.0))),
                max(-1, min(1, data.get('market_regime_score', 0.0))),
                max(0, min(100, data.get('volatility_percentile', 50.0))) / 100.0,
                max(0.1, min(10, data.get('volume_profile', 1.0))),
                max(0, min(1, data.get('price_position', 0.5))),
                max(-1, min(1, data.get('momentum_divergence', 0.0))),
                (atr_value / current_price) * 1000
            ]).reshape(1, -1)
            
            # Check for NaN or infinite values
            if np.any(np.isnan(features)) or np.any(np.isinf(features)):
                logger.warning("Invalid feature values detected, using defaults")
                return np.array([[1.0, 0.0, 0.5, 0.4, 0.0, 0.05, 0.05, 1.0, 0.0, 0.5, 1.0, 0.5, 0.0, 0.001]])
            
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
            
            # Feature scaling
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
            
            # Log learning event
            learning_stats['learning_events'].append({
                'timestamp': datetime.now().isoformat(),
                'observation_count': len(self.observation_history),
                'state_predicted': self.states[state],
                'confidence': confidence
            })
            
            # Keep only recent learning events
            if len(learning_stats['learning_events']) > 100:
                learning_stats['learning_events'] = learning_stats['learning_events'][-50:]
            
            # Check for auto-retrain
            check_auto_retrain()
            
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

# Data persistence functions
def save_data():
    """Save trading data to files"""
    try:
        data = {
            'trade_log': trade_log,
            'signal_log': signal_log,
            'performance_stats': performance_stats,
            'hmm_observations': hmm_engine.observation_history,
            'learning_stats': learning_stats
        }
        with open('trading_data.pkl', 'wb') as f:
            pickle.dump(data, f)
    except Exception as e:
        logger.error(f"Data save error: {e}")

def load_data():
    """Load trading data from files"""
    global trade_log, signal_log, performance_stats
    try:
        if os.path.exists('trading_data.pkl'):
            with open('trading_data.pkl', 'rb') as f:
                data = pickle.load(f)
            trade_log = data.get('trade_log', [])
            signal_log = data.get('signal_log', [])
            performance_stats.update(data.get('performance_stats', {}))
            hmm_engine.observation_history = data.get('hmm_observations', [])
            learning_stats.update(data.get('learning_stats', {}))
            logger.info(f"Loaded {len(trade_log)} trades from storage")
    except Exception as e:
        logger.error(f"Data load error: {e}")

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

# Load existing data on startup
load_data()

# Learning monitoring system
learning_stats = {
    'last_retrain': None,
    'retrain_count': 0,
    'learning_events': [],
    'model_improvements': []
}

def check_auto_retrain():
    """Check if model should be retrained automatically"""
    obs_count = len(hmm_engine.observation_history)
    
    # Auto-retrain every 100 observations or when significant data accumulated
    should_retrain = False
    if obs_count >= 100 and obs_count % 50 == 0:  # Every 50 new observations after 100
        should_retrain = True
    
    if should_retrain:
        old_score = hmm_engine.validation_score if hmm_engine.is_trained else 0
        success = hmm_engine.train_model(hmm_engine.observation_history)
        
        if success:
            new_score = hmm_engine.validation_score
            improvement = new_score - old_score
            
            learning_stats['last_retrain'] = datetime.now().isoformat()
            learning_stats['retrain_count'] += 1
            learning_stats['model_improvements'].append({
                'timestamp': datetime.now().isoformat(),
                'old_score': round(old_score, 4),
                'new_score': round(new_score, 4),
                'improvement': round(improvement, 4),
                'observations_used': obs_count
            })
            
            logger.info(f"Auto-retrain completed: {improvement:+.4f} improvement")
            save_data()
            return True
    return False

@app.route('/', methods=['GET'])
def dashboard():
    """Enhanced dashboard with auto-refresh and performance graphs"""
    total_trades = performance_stats['total_trades']
    win_rate = (performance_stats['winning_trades'] / total_trades * 100) if total_trades > 0 else 0
    avg_rr = sum([t.get('actual_rr', 0) for t in trade_log]) / len(trade_log) if trade_log else 0
    avg_mae = sum([t.get('mae_percentage', 0) for t in trade_log]) / len(trade_log) if trade_log else 0
    avg_mfe = sum([t.get('mfe_percentage', 0) for t in trade_log]) / len(trade_log) if trade_log else 0
    
    # Prepare chart data
    recent_trades = trade_log[-20:] if len(trade_log) > 20 else trade_log
    pnl_data = [t.get('pnl', 0) for t in recent_trades]
    rr_data = [t.get('actual_rr', 0) for t in recent_trades]
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Trading System Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
            .chart-container {{ background: #0f172a; padding: 20px; border-radius: 6px; margin: 20px 0; height: 300px; }}
            .charts-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
            .auto-refresh {{ position: fixed; top: 20px; right: 20px; background: #10b981; color: white; padding: 8px 16px; border-radius: 20px; font-size: 0.8em; }}
        </style>
    </head>
    <body>
        <div class="auto-refresh">AUTO-REFRESH: ON</div>
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
                    <div class="stat-box">
                        <h3>Avg MAE</h3>
                        <p class="error">{avg_mae:.2f}%</p>
                    </div>
                    <div class="stat-box">
                        <h3>Avg MFE</h3>
                        <p class="success">{avg_mfe:.2f}%</p>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>Performance Charts</h2>
                <div class="charts-grid">
                    <div class="chart-container">
                        <canvas id="pnlChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <canvas id="rrChart"></canvas>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>Signal Management</h2>
                <div id="signalList">No pending signals</div>
                <button onclick="refreshData()">REFRESH DATA</button>
            </div>
        </div>
        
        <script>
            // Chart setup
            const pnlCtx = document.getElementById('pnlChart').getContext('2d');
            const rrCtx = document.getElementById('rrChart').getContext('2d');
            
            const pnlChart = new Chart(pnlCtx, {{
                type: 'line',
                data: {{
                    labels: {list(range(1, len(pnl_data) + 1))},
                    datasets: [{{
                        label: 'P&L per Trade',
                        data: {pnl_data},
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.4
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ labels: {{ color: '#cbd5e1' }} }}
                    }},
                    scales: {{
                        x: {{ ticks: {{ color: '#94a3b8' }} }},
                        y: {{ ticks: {{ color: '#94a3b8' }} }}
                    }}
                }}
            }});
            
            const rrChart = new Chart(rrCtx, {{
                type: 'bar',
                data: {{
                    labels: {list(range(1, len(rr_data) + 1))},
                    datasets: [{{
                        label: 'Risk:Reward Ratio',
                        data: {rr_data},
                        backgroundColor: 'rgba(59, 130, 246, 0.8)',
                        borderColor: '#3b82f6'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ labels: {{ color: '#cbd5e1' }} }}
                    }},
                    scales: {{
                        x: {{ ticks: {{ color: '#94a3b8' }} }},
                        y: {{ ticks: {{ color: '#94a3b8' }} }}
                    }}
                }}
            }});
            
            function refreshData() {{
                location.reload();
            }}
            
            // Auto-refresh every 30 seconds
            setInterval(() => {{
                location.reload();
            }}, 30000);
        </script>
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

# Global webhook counter for debugging
webhook_counter = 0
webhook_log = []

@app.route('/webhook', methods=['POST'])
def webhook_receiver():
    """Enhanced webhook receiver with comprehensive logging"""
    global webhook_counter
    webhook_counter += 1
    
    try:
        # Log EVERYTHING for debugging
        logger.info(f"=== WEBHOOK #{webhook_counter} RECEIVED ===")
        logger.info(f"Method: {request.method}")
        logger.info(f"URL: {request.url}")
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"Content-Length: {request.content_length}")
        
        # Log raw data
        raw_data = request.get_data(as_text=True)
        logger.info(f"Raw Data: {raw_data[:500]}...")  # First 500 chars
        
        # Store webhook log entry
        webhook_entry = {
            'id': webhook_counter,
            'timestamp': datetime.now().isoformat(),
            'method': request.method,
            'content_type': request.content_type,
            'raw_data': raw_data[:200],  # First 200 chars
            'processed': False
        }
        webhook_log.append(webhook_entry)
        
        # Keep only last 50 webhook logs
        if len(webhook_log) > 50:
            webhook_log[:] = webhook_log[-25:]
        
        if request.is_json:
            data = request.json
            logger.info(f"JSON Data: {data}")
            webhook_entry['data_type'] = 'JSON'
            webhook_entry['processed'] = True
            
            # Process direct JSON data as market data
            result = hmm_engine.predict_state(data)
            logger.info(f"Direct JSON processed: {result['state_name']} (confidence: {result['confidence']})")
            logger.info(f"Total observations now: {len(hmm_engine.observation_history)}")
            
            result['webhook_id'] = webhook_counter
            return jsonify(result)
        else:
            # Try form data first
            alert_message = request.form.get('message', '')
            
            # If no form data, get raw text data
            if not alert_message:
                alert_message = raw_data
                webhook_entry['data_type'] = 'RAW_TEXT'
                logger.info(f"Raw Text Message: {alert_message[:200]}...")
            else:
                webhook_entry['data_type'] = 'FORM'
                logger.info(f"Form Message: {alert_message[:200]}...")
            
            if 'Market Data:' in alert_message:
                try:
                    json_str = alert_message.split('Market Data: ')[1].strip()
                    # Handle potential truncation by trying to fix incomplete JSON
                    if not json_str.endswith('}'):
                        logger.warning(f"JSON appears truncated: {json_str}")
                        # Try to find the last complete field
                        last_comma = json_str.rfind(',')
                        if last_comma > 0:
                            json_str = json_str[:last_comma] + '}'
                            logger.info(f"Attempting to fix JSON: {json_str}")
                    
                    data = json.loads(json_str)
                    logger.info(f"Successfully parsed Market Data: {data}")
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parsing failed: {e}")
                    logger.error(f"Raw JSON string: {json_str}")
                    return jsonify({'error': f'Invalid JSON: {str(e)}', 'webhook_id': webhook_counter}), 400
            elif 'HMM Training Data:' in alert_message:
                json_str = alert_message.split('HMM Training Data: ')[1]
                training_data = json.loads(json_str)
                hmm_engine.observation_history.append(training_data)
                logger.info(f"Training data added. Total observations: {len(hmm_engine.observation_history)}")
                webhook_entry['processed'] = True
                return jsonify({'status': 'training_data_received', 'webhook_id': webhook_counter})
            elif 'Mixed Bias Analysis:' in alert_message:
                json_str = alert_message.split('Mixed Bias Analysis: ')[1]
                mixed_data = json.loads(json_str)
                result = mixed_bias_analysis_internal(mixed_data)
                webhook_entry['processed'] = True
                return jsonify(result)
            elif 'Auto Log Signal:' in alert_message:
                json_str = alert_message.split('Auto Log Signal: ')[1]
                signal_data = json.loads(json_str)
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
                webhook_entry['processed'] = True
                return jsonify({'status': 'signal_logged', 'signal_id': signal_entry['signal_id'], 'webhook_id': webhook_counter})
            else:
                logger.warning(f"Unknown alert format: {alert_message[:100]}...")
                return jsonify({'error': 'Unknown alert format', 'webhook_id': webhook_counter}), 400
        
        # This should only be reached for form data processing
        if not data:
            logger.error("No data provided in webhook")
            return jsonify({'error': 'No data provided', 'webhook_id': webhook_counter}), 400
        
        result = hmm_engine.predict_state(data)
        logger.info(f"Form data processed: {result['state_name']} (confidence: {result['confidence']})")
        logger.info(f"Total observations now: {len(hmm_engine.observation_history)}")
        
        webhook_entry['processed'] = True
        result['webhook_id'] = webhook_counter
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Webhook #{webhook_counter} error: {e}")
        return jsonify({'error': str(e), 'webhook_id': webhook_counter}), 500

@app.route('/log_trade', methods=['POST'])
def log_trade():
    """Enhanced trade logging with MAE/MFE analysis"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No trade data provided'}), 400
        
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
            mfe = max_favorable - entry_price
            mae = entry_price - max_adverse
        else:
            mfe = entry_price - max_favorable
            mae = max_adverse - entry_price
            
        trade_entry = {
            'timestamp': data.get('timestamp', pd.Timestamp.now().isoformat()),
            'symbol': data.get('symbol', 'UNKNOWN'),
            'direction': data.get('direction', ''),
            'entry_price': entry_price,
            'exit_price': exit_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'pnl': float(data.get('pnl', actual_pnl)),
            'result': data.get('result', ''),
            'planned_rr': planned_rr,
            'actual_rr': actual_rr,
            'rr_efficiency': (actual_rr / planned_rr) if planned_rr > 0 else 0,
            'mae': mae,
            'mfe': mfe,
            'mae_percentage': (mae / entry_price * 100) if entry_price > 0 else 0,
            'mfe_percentage': (mfe / entry_price * 100) if entry_price > 0 else 0,
            'exit_efficiency': (actual_pnl / mfe) if mfe > 0 else 0,
            'duration_minutes': float(data.get('duration_minutes', 0)),
            'ai_confidence': float(data.get('ai_confidence', 0)),
            'patterns_used': data.get('patterns_used', []),
            'session': data.get('session', 'Unknown')
        }
        
        trade_log.append(trade_entry)
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
        
        # Save data after each trade
        save_data()
        
        return jsonify({'status': 'success', 'trade_id': len(trade_log)})
        
    except Exception as e:
        logger.error(f"Trade logging error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/performance', methods=['GET'])
def get_performance():
    """Enhanced trading performance statistics"""
    try:
        win_rate = (performance_stats['winning_trades'] / performance_stats['total_trades'] * 100) if performance_stats['total_trades'] > 0 else 0
        recent_trades = trade_log[-10:] if len(trade_log) > 10 else trade_log
        
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
        
        # Calculate profit factor and drawdown metrics
        winning_pnl = sum([t.get('pnl', 0) for t in trade_log if t.get('pnl', 0) > 0])
        losing_pnl = abs(sum([t.get('pnl', 0) for t in trade_log if t.get('pnl', 0) < 0]))
        profit_factor = winning_pnl / losing_pnl if losing_pnl > 0 else 0
        
        # Calculate maximum drawdown
        cumulative_pnl = 0
        peak = 0
        max_drawdown = 0
        for trade in trade_log:
            cumulative_pnl += trade.get('pnl', 0)
            if cumulative_pnl > peak:
                peak = cumulative_pnl
            drawdown = peak - cumulative_pnl
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        result = {
            'summary': {
                'total_trades': performance_stats['total_trades'],
                'win_rate': round(win_rate, 2),
                'total_pnl': round(performance_stats['total_pnl'], 2),
                'avg_pnl_per_trade': round(performance_stats['total_pnl'] / performance_stats['total_trades'], 2) if performance_stats['total_trades'] > 0 else 0,
                'profit_factor': round(profit_factor, 2),
                'best_trade': max([t.get('pnl', 0) for t in trade_log]) if trade_log else 0,
                'worst_trade': min([t.get('pnl', 0) for t in trade_log]) if trade_log else 0,
                'max_drawdown': round(max_drawdown, 2)
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

@app.route('/market_structure', methods=['POST'])
def market_structure():
    """Analyze current market structure for entry timing"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
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
            recent_highs = highs[-3:]
            recent_lows = lows[-3:]
            
            higher_highs = sum(1 for i in range(1, len(recent_highs)) if recent_highs[i] > recent_highs[i-1])
            higher_lows = sum(1 for i in range(1, len(recent_lows)) if recent_lows[i] > recent_lows[i-1])
            
            structure_analysis['trend_strength'] = (higher_highs + higher_lows) / 4.0
            structure_analysis['support_level'] = min(recent_lows)
            structure_analysis['resistance_level'] = max(recent_highs)
            
            if len(volumes) >= 3:
                avg_volume = sum(volumes[-3:]) / 3
                current_volume = volumes[-1] if volumes else 1.0
                volume_strength = current_volume / avg_volume if avg_volume > 0 else 1.0
                structure_analysis['breakout_probability'] = min(volume_strength * structure_analysis['trend_strength'], 1.0)
            
            support = structure_analysis['support_level']
            resistance = structure_analysis['resistance_level']
            zone_size = (resistance - support) * 0.2
            
            if structure_analysis['trend_strength'] > 0.5:
                structure_analysis['optimal_entry_zone'] = [support, support + zone_size]
            else:
                structure_analysis['optimal_entry_zone'] = [resistance - zone_size, resistance]
        
        return jsonify(structure_analysis)
        
    except Exception as e:
        logger.error(f"Market structure analysis error: {e}")
        return jsonify({'error': str(e)}), 500

def mixed_bias_analysis_internal(data):
    """Internal mixed bias analysis function"""
    bull_score = data.get('bull_weighted_score', 0.0)
    bear_score = data.get('bear_weighted_score', 0.0)
    bull_patterns = data.get('bull_patterns', [])
    bear_patterns = data.get('bear_patterns', [])
    hmm_state = data.get('hmm_state', 0)
    
    pattern_weights = {
        'hammer': 0.85, 'engulf': 0.75, 'ebp': 0.70, 'three_bar': 0.65,
        'sweep': 0.60, 'inside': 0.45, 'close_above': 0.40, 'close_below': 0.40
    }
    
    bull_ml_score = sum(pattern_weights.get(p, 0.5) for p in bull_patterns)
    bear_ml_score = sum(pattern_weights.get(p, 0.5) for p in bear_patterns)
    
    if hmm_state == 1:
        bull_ml_score *= 1.2
    elif hmm_state == 2:
        bull_ml_score *= 1.3
    elif hmm_state == 3:
        bear_ml_score *= 1.3
    
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
    
    return {
        'recommendation': recommendation,
        'confidence': round(confidence, 3),
        'bull_ml_score': round(bull_ml_score, 3),
        'bear_ml_score': round(bear_ml_score, 3),
        'analysis_method': 'ML_Enhanced_Pattern_Weighting',
        'timestamp': pd.Timestamp.now().isoformat()
    }

@app.route('/mixed_bias_analysis', methods=['POST'])
def mixed_bias_analysis():
    """Analyze mixed bias days using ML"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        result = mixed_bias_analysis_internal(data)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Mixed bias analysis error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/predict_entry', methods=['POST'])
def predict_entry():
    """Real-time 1M entry signal prediction with HMM state alignment"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        daily_bias = data.get('daily_bias', 'NEUTRAL')
        bias_score = data.get('bias_score', 50.0)
        current_price = data.get('current_price', 0.0)
        volume_ratio = data.get('volume_ratio', 1.0)
        price_momentum = data.get('price_momentum', 0.0)
        pullback_level = data.get('pullback_level', 0.0)
        resistance_level = data.get('resistance_level', 0.0)
        support_level = data.get('support_level', 0.0)
        
        # Get HMM state prediction
        hmm_result = hmm_engine.predict_state({
            'pattern_strength': abs(bias_score) / 100,
            'volume_ratio': volume_ratio,
            'price_momentum': price_momentum,
            'volatility_ratio': 1.0,
            'rsi_momentum': 0.5
        })
        
        entry_signal = "NO_ENTRY"
        confidence = 0.0
        target_price = 0.0
        stop_price = 0.0
        
        # LONG entries with HMM state alignment
        if daily_bias == "BULLISH" and bias_score >= 65 and hmm_result['state'] in [1, 2]:  # Accumulation or Markup
            if volume_ratio > 1.2 and price_momentum > 0.1:
                entry_signal = "ENTER_LONG"
                confidence = min(bias_score / 100 * (1 + volume_ratio * 0.2) * hmm_result['confidence'], 0.95)
                target_price = resistance_level if resistance_level > 0 else current_price * 1.002
                stop_price = support_level if support_level > 0 else current_price * 0.998
        
        # SHORT entries with HMM state alignment  
        elif daily_bias == "BEARISH" and bias_score <= -65 and hmm_result['state'] in [1, 3]:  # Accumulation or Distribution
            if volume_ratio > 1.2 and price_momentum < -0.1:
                entry_signal = "ENTER_SHORT"
                confidence = min(abs(bias_score) / 100 * (1 + volume_ratio * 0.2) * hmm_result['confidence'], 0.95)
                target_price = support_level if support_level > 0 else current_price * 0.998
                stop_price = resistance_level if resistance_level > 0 else current_price * 1.002
        
        # Calculate risk/reward ratio
        risk_reward = 0.0
        if stop_price != 0 and target_price != 0:
            risk = abs(current_price - stop_price)
            reward = abs(target_price - current_price)
            risk_reward = reward / risk if risk > 0 else 0
        
        result = {
            'entry_signal': entry_signal,
            'confidence': round(confidence, 3),
            'current_price': current_price,
            'target_price': round(target_price, 5),
            'stop_price': round(stop_price, 5),
            'risk_reward': round(risk_reward, 2),
            'hmm_state': hmm_result['state_name'],
            'hmm_confidence': hmm_result['confidence'],
            'volume_ratio': volume_ratio,
            'price_momentum': price_momentum,
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Entry prediction error: {e}")
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
            'recommendations': []
        }
        
        # Find best patterns
        for pattern, data in performance_stats['best_patterns'].items():
            if data['total'] >= 3:
                success_rate = (data['wins'] / data['total']) * 100
                if success_rate > 60:
                    insights['best_performing_patterns'].append({
                        'pattern': pattern,
                        'success_rate': round(success_rate, 1),
                        'sample_size': data['total']
                    })
        
        # Calculate session performance
        london_trades = [t for t in trade_log if t.get('session') == 'London']
        ny_trades = [t for t in trade_log if t.get('session') == 'NY']
        
        if london_trades:
            london_wins = len([t for t in london_trades if t.get('result') == 'WIN'])
            insights['session_performance']['London'] = {
                'total_trades': len(london_trades),
                'win_rate': round((london_wins / len(london_trades)) * 100, 1),
                'avg_pnl': round(sum([t.get('pnl', 0) for t in london_trades]) / len(london_trades), 2)
            }
        
        if ny_trades:
            ny_wins = len([t for t in ny_trades if t.get('result') == 'WIN'])
            insights['session_performance']['NY'] = {
                'total_trades': len(ny_trades),
                'win_rate': round((ny_wins / len(ny_trades)) * 100, 1),
                'avg_pnl': round(sum([t.get('pnl', 0) for t in ny_trades]) / len(ny_trades), 2)
            }
        
        # Generate recommendations
        if len(insights['best_performing_patterns']) > 0:
            best_pattern = max(insights['best_performing_patterns'], key=lambda x: x['success_rate'])
            insights['recommendations'].append(f"Focus on {best_pattern['pattern']} patterns - {best_pattern['success_rate']}% success rate")
        
        # Session recommendations
        if 'London' in insights['session_performance'] and 'NY' in insights['session_performance']:
            london_wr = insights['session_performance']['London']['win_rate']
            ny_wr = insights['session_performance']['NY']['win_rate']
            if london_wr > ny_wr + 10:
                insights['recommendations'].append(f"London session performing better ({london_wr}% vs {ny_wr}% win rate)")
            elif ny_wr > london_wr + 10:
                insights['recommendations'].append(f"NY session performing better ({ny_wr}% vs {london_wr}% win rate)")
        
        return jsonify(insights)
        
    except Exception as e:
        logger.error(f"Model insights error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/learning_status', methods=['GET'])
def learning_status():
    """Monitor AI learning progress and improvements"""
    try:
        # Calculate learning velocity (observations per hour)
        recent_events = [e for e in learning_stats.get('learning_events', []) 
                        if (datetime.now() - datetime.fromisoformat(e['timestamp'])).total_seconds() < 3600]
        learning_velocity = len(recent_events)
        
        # Get latest model improvement
        latest_improvement = None
        if learning_stats.get('model_improvements'):
            latest_improvement = learning_stats['model_improvements'][-1]
        
        return jsonify({
            'learning_active': len(hmm_engine.observation_history) > 0,
            'total_observations': len(hmm_engine.observation_history),
            'learning_velocity_per_hour': learning_velocity,
            'retrain_count': learning_stats.get('retrain_count', 0),
            'last_retrain': learning_stats.get('last_retrain'),
            'latest_improvement': latest_improvement,
            'model_trained': hmm_engine.is_trained,
            'training_score': round(hmm_engine.training_score, 4) if hmm_engine.is_trained else 0,
            'validation_score': round(hmm_engine.validation_score, 4) if hmm_engine.is_trained else 0,
            'next_retrain_at': f"{((len(hmm_engine.observation_history) // 50 + 1) * 50)} observations",
            'learning_progress': min(100, (len(hmm_engine.observation_history) / 100) * 100)
        })
    except Exception as e:
        logger.error(f"Learning status error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook_debug', methods=['GET'])
def webhook_debug():
    """Debug webhook reception issues"""
    try:
        return jsonify({
            'total_webhooks_received': webhook_counter,
            'recent_webhooks': webhook_log[-10:] if webhook_log else [],
            'observations_count': len(hmm_engine.observation_history),
            'model_trained': hmm_engine.is_trained,
            'last_webhook': webhook_log[-1] if webhook_log else None,
            'server_time': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/webhook_test', methods=['GET', 'POST'])
def webhook_test():
    """Test webhook connectivity and log all incoming requests"""
    try:
        if request.method == 'GET':
            return jsonify({
                'status': 'Webhook endpoint active',
                'url': request.url,
                'method': 'GET',
                'timestamp': datetime.now().isoformat(),
                'message': 'Send POST request with JSON data to test webhook'
            })
        
        # Log all POST data for debugging
        logger.info(f"Webhook test received: {request.method}")
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"Content-Type: {request.content_type}")
        
        if request.is_json:
            data = request.json
            logger.info(f"JSON data: {data}")
        else:
            form_data = request.form.to_dict()
            raw_data = request.get_data(as_text=True)
            logger.info(f"Form data: {form_data}")
            logger.info(f"Raw data: {raw_data}")
        
        return jsonify({
            'status': 'Webhook test successful',
            'received_data': True,
            'content_type': request.content_type,
            'method': request.method,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Webhook test error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Enhanced health check with system metrics"""
    try:
        # System health metrics
        memory_usage = 0
        try:
            import psutil
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        except:
            pass
        
        return jsonify({
            'status': 'HMM Server Running',
            'is_trained': hmm_engine.is_trained,
            'observations': len(hmm_engine.observation_history),
            'total_trades': len(trade_log),
            'memory_usage_mb': round(memory_usage, 2),
            'uptime': datetime.now().isoformat(),
            'training_score': round(hmm_engine.training_score, 4) if hmm_engine.is_trained else 0,
            'validation_score': round(hmm_engine.validation_score, 4) if hmm_engine.is_trained else 0
        })
    except Exception as e:
        return jsonify({'status': 'Error', 'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Starting Trading Dashboard Server...")
    app.run(host='0.0.0.0', port=port, debug=False)