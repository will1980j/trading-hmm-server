#!/usr/bin/env python3
"""
Enhanced TradingView Webhook + OpenAI Integration
Better than Chrome extension scraping
"""

from flask import Flask, request, jsonify
import openai
import os
from datetime import datetime

app = Flask(__name__)
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/api/tradingview-webhook', methods=['POST'])
def tradingview_webhook():
    """Receive TradingView alerts and analyze with OpenAI"""
    try:
        data = request.get_json()
        
        # TradingView sends: {"symbol": "NQ1!", "price": 15234.5, "action": "BUY", "message": "FVG detected"}
        symbol = data.get('symbol', 'NQ1!')
        price = data.get('price', 0)
        action = data.get('action', 'ANALYZE')
        message = data.get('message', '')
        
        # Get OpenAI analysis
        analysis = get_openai_analysis(symbol, price, action, message)
        
        # Store and return
        result = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'price': price,
            'tradingview_signal': action,
            'ai_analysis': analysis,
            'confidence': analysis.get('confidence', 0.5)
        }
        
        print(f"✅ TradingView + OpenAI: {result}")
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def get_openai_analysis(symbol, price, action, message):
    """Get OpenAI analysis of TradingView signal"""
    try:
        prompt = f"""
        Analyze this TradingView signal for {symbol}:
        
        Current Price: ${price}
        Signal: {action}
        Message: {message}
        Time: {datetime.now().strftime('%H:%M EST')}
        
        Provide analysis in JSON format:
        {{
            "bias": "LONG/SHORT/NEUTRAL",
            "confidence": 0.0-1.0,
            "entry_price": number,
            "stop_loss": number,
            "take_profit": number,
            "risk_reward": number,
            "reasoning": "explanation",
            "session_context": "market session analysis"
        }}
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        import json
        analysis = json.loads(response.choices[0].message.content)
        return analysis
        
    except Exception as e:
        return {
            "bias": "NEUTRAL",
            "confidence": 0.3,
            "reasoning": f"Analysis error: {str(e)}"
        }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)