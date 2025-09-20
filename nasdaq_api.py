from flask import Flask, jsonify, request
from nasdaq_ml_predictor import NasdaqMLPredictor
import json
from datetime import datetime

app = Flask(__name__)
predictor = NasdaqMLPredictor()

@app.route('/api/nasdaq-train', methods=['POST'])
def train_nasdaq_model():
    try:
        data = request.get_json() or {}
        symbol = data.get('symbol', 'QQQ')
        
        results = predictor.train(symbol)
        
        return jsonify({
            'status': 'success',
            'symbol': symbol,
            'training_results': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/nasdaq-predict', methods=['POST'])
def predict_nasdaq():
    try:
        data = request.get_json() or {}
        symbol = data.get('symbol', 'QQQ')
        
        if not predictor.is_trained:
            predictor.train(symbol)
        
        prediction = predictor.predict_with_confidence(symbol)
        
        return jsonify({
            'status': 'success',
            'symbol': symbol,
            'prediction': prediction,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/nasdaq-status', methods=['GET'])
def nasdaq_status():
    return jsonify({
        'is_trained': predictor.is_trained,
        'models': list(predictor.models.keys()),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)