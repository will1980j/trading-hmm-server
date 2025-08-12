#!/usr/bin/env python3
"""
Cloud-based AI Trading System with Machine Learning
Deployed on Railway/Vercel - No local dependencies
"""

from flask import Flask, request, jsonify
import openai
import os
import json
from datetime import datetime
import sqlite3
from threading import Lock
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle

app = Flask(__name__)
openai.api_key = os.getenv('OPENAI_API_KEY')

# Thread-safe database operations
db_lock = Lock()

# ML Model for signal quality prediction
signal_model = None
model_features = ['rsi', 'macd', 'volume_ratio', 'atr', 'session_score', 'fvg_quality']

def init_database():
    """Initialize cloud database for signal tracking"""
    with db_lock:
        conn = sqlite3.connect('trading_signals.db')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                symbol TEXT,
                price REAL,
                signal_type TEXT,
                confidence REAL,
                rsi REAL,
                macd REAL,
                volume_ratio REAL,
                atr REAL,
                session TEXT,
                fvg_quality REAL,
                outcome TEXT,
                profit_loss REAL,
                ai_reasoning TEXT
            )
        ''')
        conn.commit()
        conn.close()

def load_ml_model():
    """Load or create ML model for signal prediction"""
    global signal_model
    try:
        with open('signal_model.pkl', 'rb') as f:
            signal_model = pickle.load(f)
    except:
        signal_model = RandomForestClassifier(n_estimators=100, random_state=42)

@app.route('/api/ai-signal-analysis', methods=['POST'])
def ai_signal_analysis():
    """Main endpoint for TradingView indicator"""
    try:
        data = request.get_json()
        
        # Extract comprehensive market data
        market_data = {
            'symbol': data.get('symbol', 'NQ1!'),
            'price': float(data.get('price', 0)),
            'rsi': float(data.get('rsi', 50)),
            'macd': float(data.get('macd', 0)),
            'volume': float(data.get('volume', 0)),
            'volume_sma': float(data.get('volume_sma', 1)),
            'atr': float(data.get('atr', 10)),
            'session': data.get('session', 'NY'),
            'fvg_up': data.get('fvg_up', False),
            'fvg_down': data.get('fvg_down', False),
            'order_block': data.get('order_block', False),
            'liquidity_sweep': data.get('liquidity_sweep', False),
            'timestamp': datetime.now().isoformat()
        }
        
        # Calculate derived features
        market_data['volume_ratio'] = market_data['volume'] / max(market_data['volume_sma'], 1)
        market_data['session_score'] = get_session_score(market_data['session'])
        market_data['fvg_quality'] = calculate_fvg_quality(market_data)
        
        # Get AI analysis
        ai_analysis = get_advanced_ai_analysis(market_data)
        
        # Get ML prediction
        ml_prediction = get_ml_signal_prediction(market_data)
        
        # Combine AI + ML for final signal
        final_signal = combine_ai_ml_signals(ai_analysis, ml_prediction, market_data)
        
        # Store signal for learning
        store_signal_for_learning(market_data, final_signal, ai_analysis)
        
        # Return to TradingView indicator
        response = {
            'signal_strength': final_signal['strength'],
            'signal_type': final_signal['type'],
            'confidence': final_signal['confidence'],
            'entry_price': final_signal['entry_price'],
            'stop_loss': final_signal['stop_loss'],
            'take_profit': final_signal['take_profit'],
            'ai_reasoning': ai_analysis['reasoning'],
            'ml_score': ml_prediction['score'],
            'risk_level': final_signal['risk_level'],
            'timestamp': market_data['timestamp']
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e), 'signal_strength': 0}), 400

def get_advanced_ai_analysis(data):
    """Advanced AI analysis with your trading strategy"""
    
    prompt = f"""
    You are an expert ICT trader analyzing NQ futures for high-probability setups.
    
    MARKET DATA:
    Price: ${data['price']}
    RSI: {data['rsi']}
    MACD: {data['macd']}
    Volume Ratio: {data['volume_ratio']:.2f}
    ATR: {data['atr']}
    Session: {data['session']}
    FVG Present: {data['fvg_up'] or data['fvg_down']}
    Order Block: {data['order_block']}
    Liquidity Sweep: {data['liquidity_sweep']}
    
    STRATEGY FOCUS:
    - Fair Value Gaps (FVG) with institutional confirmation
    - Order blocks at key levels
    - Liquidity sweeps and reversals
    - Session-based bias
    - Multi-timeframe confluence
    
    Analyze for ROCK SOLID signals only (80%+ win rate potential):
    
    {{
        "signal_present": true/false,
        "signal_type": "LONG/SHORT/NONE",
        "strength": 0.0-1.0,
        "confluence_factors": ["list of confluences"],
        "entry_price": number,
        "stop_loss": number,
        "take_profit": number,
        "risk_reward": number,
        "reasoning": "detailed explanation of why this is rock solid",
        "session_context": "how session affects this setup",
        "institutional_bias": "what smart money is likely doing",
        "failure_scenarios": ["what could invalidate this setup"]
    }}
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a master ICT trader. Only identify the highest probability setups. Be extremely selective."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        return {
            "signal_present": False,
            "signal_type": "NONE",
            "strength": 0.0,
            "reasoning": f"Analysis error: {str(e)}"
        }

def get_ml_signal_prediction(data):
    """ML prediction based on historical signal performance"""
    global signal_model
    
    try:
        # Prepare features for ML model
        features = np.array([[
            data['rsi'],
            data['macd'],
            data['volume_ratio'],
            data['atr'],
            data['session_score'],
            data['fvg_quality']
        ]])
        
        if signal_model and hasattr(signal_model, 'predict_proba'):
            # Get probability of successful signal
            prob = signal_model.predict_proba(features)[0]
            success_prob = prob[1] if len(prob) > 1 else 0.5
            
            return {
                'score': float(success_prob),
                'prediction': 'STRONG' if success_prob > 0.8 else 'WEAK',
                'model_confidence': float(max(prob))
            }
        else:
            return {'score': 0.5, 'prediction': 'NEUTRAL', 'model_confidence': 0.5}
            
    except Exception as e:
        return {'score': 0.3, 'prediction': 'ERROR', 'model_confidence': 0.1}

def combine_ai_ml_signals(ai_analysis, ml_prediction, market_data):
    """Combine AI and ML for final trading signal"""
    
    # Only proceed if AI identifies a signal
    if not ai_analysis.get('signal_present', False):
        return {
            'type': 'NONE',
            'strength': 0.0,
            'confidence': 0.0,
            'entry_price': market_data['price'],
            'stop_loss': market_data['price'],
            'take_profit': market_data['price'],
            'risk_level': 'NONE'
        }
    
    # Combine AI confidence with ML score
    ai_strength = ai_analysis.get('strength', 0.0)
    ml_score = ml_prediction.get('score', 0.5)
    
    # Weighted combination (70% AI, 30% ML)
    combined_confidence = (ai_strength * 0.7) + (ml_score * 0.3)
    
    # Only return signals with high combined confidence
    if combined_confidence < 0.75:
        return {
            'type': 'WAIT',
            'strength': combined_confidence,
            'confidence': combined_confidence,
            'entry_price': market_data['price'],
            'stop_loss': market_data['price'],
            'take_profit': market_data['price'],
            'risk_level': 'HIGH'
        }
    
    return {
        'type': ai_analysis.get('signal_type', 'NONE'),
        'strength': combined_confidence,
        'confidence': combined_confidence,
        'entry_price': ai_analysis.get('entry_price', market_data['price']),
        'stop_loss': ai_analysis.get('stop_loss', market_data['price']),
        'take_profit': ai_analysis.get('take_profit', market_data['price']),
        'risk_level': 'LOW' if combined_confidence > 0.9 else 'MEDIUM'
    }

def store_signal_for_learning(market_data, signal, ai_analysis):
    """Store signal data for ML learning"""
    with db_lock:
        try:
            conn = sqlite3.connect('trading_signals.db')
            conn.execute('''
                INSERT INTO signals (
                    timestamp, symbol, price, signal_type, confidence,
                    rsi, macd, volume_ratio, atr, session, fvg_quality,
                    ai_reasoning
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                market_data['timestamp'],
                market_data['symbol'],
                market_data['price'],
                signal['type'],
                signal['confidence'],
                market_data['rsi'],
                market_data['macd'],
                market_data['volume_ratio'],
                market_data['atr'],
                market_data['session'],
                market_data['fvg_quality'],
                ai_analysis.get('reasoning', '')
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Database error: {e}")

@app.route('/api/update-signal-outcome', methods=['POST'])
def update_signal_outcome():
    """Update signal outcome for ML learning"""
    try:
        data = request.get_json()
        signal_id = data.get('signal_id')
        outcome = data.get('outcome')  # 'WIN' or 'LOSS'
        profit_loss = float(data.get('profit_loss', 0))
        
        with db_lock:
            conn = sqlite3.connect('trading_signals.db')
            conn.execute('''
                UPDATE signals 
                SET outcome = ?, profit_loss = ?
                WHERE id = ?
            ''', (outcome, profit_loss, signal_id))
            conn.commit()
            conn.close()
        
        # Retrain model with new data
        retrain_model()
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def retrain_model():
    """Retrain ML model with latest signal outcomes"""
    global signal_model
    
    try:
        with db_lock:
            conn = sqlite3.connect('trading_signals.db')
            cursor = conn.execute('''
                SELECT rsi, macd, volume_ratio, atr, session, fvg_quality, outcome
                FROM signals 
                WHERE outcome IS NOT NULL
            ''')
            
            data = cursor.fetchall()
            conn.close()
        
        if len(data) < 10:  # Need minimum data
            return
        
        # Prepare training data
        X = []
        y = []
        
        for row in data:
            session_score = get_session_score(row[4])
            X.append([row[0], row[1], row[2], row[3], session_score, row[5]])
            y.append(1 if row[6] == 'WIN' else 0)
        
        X = np.array(X)
        y = np.array(y)
        
        # Train model
        signal_model.fit(X, y)
        
        # Save model
        with open('signal_model.pkl', 'wb') as f:
            pickle.dump(signal_model, f)
            
        print(f"Model retrained with {len(data)} signals")
        
    except Exception as e:
        print(f"Model training error: {e}")

def get_session_score(session):
    """Convert session to numerical score"""
    scores = {'ASIA': 0.3, 'LONDON': 0.8, 'NY': 0.9, 'NY_PM': 0.6}
    return scores.get(session, 0.5)

def calculate_fvg_quality(data):
    """Calculate FVG quality score"""
    if not (data['fvg_up'] or data['fvg_down']):
        return 0.0
    
    # Quality based on volume, ATR, and session
    volume_factor = min(data['volume_ratio'], 2.0) / 2.0
    session_factor = get_session_score(data['session'])
    
    return (volume_factor + session_factor) / 2.0

# Initialize on startup
init_database()
load_ml_model()

if __name__ == '__main__':
    print("🚀 Cloud AI Trading System Starting...")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))