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

@app.route('/webhook', methods=['POST'])
def webhook_receiver():
    """Enhanced webhook receiver for multiple alert types"""
    try:
        if request.is_json:
            data = request.json
        else:
            alert_message = request.form.get('message', '')
            if 'Market Data:' in alert_message:
                json_str = alert_message.split('Market Data: ')[1]
                data = json.loads(json_str)
            elif 'HMM Training Data:' in alert_message:
                json_str = alert_message.split('HMM Training Data: ')[1]
                training_data = json.loads(json_str)
                hmm_engine.observation_history.append(training_data)
                return jsonify({'status': 'training_data_received'})
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
                return jsonify({'status': 'signal_logged', 'signal_id': signal_entry['signal_id']})
            else:
                return jsonify({'error': 'Unknown alert format'}), 400
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        result = hmm_engine.predict_state(data)
        logger.info(f"Webhook processed: {result['state_name']}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

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
        
        return jsonify({'status': 'success', 'trade_id': len(trade_log)})
        
    except Exception as e:
        logger.error(f"Trade logging error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/performance', methods=['GET'])
def get_performance():
    """Get trading performance statistics"""
    try:
        win_rate = (performance_stats['winning_trades'] / performance_stats['total_trades'] * 100) if performance_stats['total_trades'] > 0 else 0
        recent_trades = trade_log[-10:] if len(trade_log) > 10 else trade_log
        
        result = {
            'summary': {
                'total_trades': performance_stats['total_trades'],
                'win_rate': round(win_rate, 2),
                'total_pnl': round(performance_stats['total_pnl'], 2),
                'avg_pnl_per_trade': round(performance_stats['total_pnl'] / performance_stats['total_trades'], 2) if performance_stats['total_trades'] > 0 else 0
            },
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

@app.route('/mixed_bias_analysis', methods=['POST'])
def mixed_bias_analysis():
    """Analyze mixed bias days using ML"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
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
        
        result = {
            'recommendation': recommendation,
            'confidence': round(confidence, 3),
            'bull_ml_score': round(bull_ml_score, 3),
            'bear_ml_score': round(bear_ml_score, 3),
            'analysis_method': 'ML_Enhanced_Pattern_Weighting',
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
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
        
        daily_bias = data.get('daily_bias', 'NEUTRAL')
        bias_score = data.get('bias_score', 50.0)
        current_price = data.get('current_price', 0.0)
        volume_ratio = data.get('volume_ratio', 1.0)
        price_momentum = data.get('price_momentum', 0.0)
        
        entry_signal = "NO_ENTRY"
        confidence = 0.0
        
        if daily_bias == "BULLISH" and bias_score >= 65:
            if volume_ratio > 1.2 and price_momentum > 0.1:
                entry_signal = "ENTER_LONG"
                confidence = min(bias_score / 100 * (1 + volume_ratio * 0.2), 0.95)
        elif daily_bias == "BEARISH" and bias_score <= -65:
            if volume_ratio > 1.2 and price_momentum < -0.1:
                entry_signal = "ENTER_SHORT"
                confidence = min(abs(bias_score) / 100 * (1 + volume_ratio * 0.2), 0.95)
        
        result = {
            'entry_signal': entry_signal,
            'confidence': round(confidence, 3),
            'current_price': current_price,
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
        
        # Generate recommendations
        if len(insights['best_performing_patterns']) > 0:
            best_pattern = max(insights['best_performing_patterns'], key=lambda x: x['success_rate'])
            insights['recommendations'].append(f"Focus on {best_pattern['pattern']} patterns - {best_pattern['success_rate']}% success rate")
        
        return jsonify(insights)
        
    except Exception as e:
        logger.error(f"Model insights error: {e}")
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