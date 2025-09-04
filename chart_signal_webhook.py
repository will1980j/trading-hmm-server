#!/usr/bin/env python3
"""
Chart Signal Webhook - Minimal implementation for TradingView chart display
Connects your live signals dashboard with TradingView charts
"""

from flask import Flask, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/api/chart-signal', methods=['POST'])
def chart_signal_webhook():
    """Receive signals and format for TradingView chart display"""
    try:
        # Get raw data from TradingView alert
        raw_data = request.get_data(as_text=True)
        
        # Parse different alert formats
        if raw_data.startswith('SIGNAL:'):
            # Format: SIGNAL:BULLISH:15234.5:85
            parts = raw_data.split(':')
            if len(parts) >= 4:
                bias = parts[1]
                price = float(parts[2])
                strength = float(parts[3])
                
                # Create chart display signal
                chart_signal = {
                    'type': 'CHART_DISPLAY',
                    'symbol': 'NQ1!',
                    'bias': bias,
                    'price': price,
                    'strength': strength,
                    'timestamp': datetime.now().isoformat(),
                    'display_text': f"{bias} {strength}%"
                }
                
                print(f"✅ Chart Signal: {chart_signal}")
                return jsonify({"status": "success", "signal": chart_signal})
        
        # Try JSON format
        try:
            data = json.loads(raw_data)
            chart_signal = {
                'type': 'CHART_DISPLAY',
                'symbol': data.get('symbol', 'NQ1!'),
                'bias': data.get('bias', 'NEUTRAL'),
                'price': data.get('price', 0),
                'strength': data.get('strength', 50),
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"✅ JSON Chart Signal: {chart_signal}")
            return jsonify({"status": "success", "signal": chart_signal})
            
        except json.JSONDecodeError:
            pass
        
        # Default response
        return jsonify({"status": "received", "data": raw_data[:100]})
        
    except Exception as e:
        print(f"❌ Chart signal error: {e}")
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)