from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import OpenAI
from os import environ
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize OpenAI
client = OpenAI(api_key=environ.get('OPENAI_API_KEY')) if environ.get('OPENAI_API_KEY') else None

@app.route('/api/test')
def test():
    print("✅ TEST ENDPOINT CALLED")
    return jsonify({"message": "WORKING"})

@app.route('/api/ai-chart-analysis')
def ai_analysis():
    print("✅ AI ENDPOINT CALLED - USING REAL OPENAI")
    symbol = request.args.get('symbol', 'NQ1')
    session = request.args.get('session', 'LONDON')
    price = request.args.get('price', '15000')
    
    if not client:
        return jsonify({
            'symbol': symbol,
            'session': session,
            'fvgQuality': 0.5,
            'entryConfidence': 0.3,
            'marketCondition': 'NO OPENAI KEY',
            'recommendation': 'ADD API KEY'
        })
    
    try:
        # Simple prompt without complex market data
        prompt = f"""NQ Futures ICT Analysis:
        
        TRADER'S STRATEGY:
        - Uses FVG bias indicator for direction
        - Waits for 1min pivot sweeps (any pivot level)
        - Enters on FVG/IFVG formation after sweep
        - SL at FVG base, 1:1 breakeven, test R-targets
        
        CURRENT CONDITIONS:
        - Symbol: {symbol}
        - Price: {price}
        - Session: {session}
        - Time: {datetime.now().strftime('%H:%M UTC')}
        
        Based on {session} session characteristics:
        1. What should the FVG bias be? (Bullish/Bearish/Neutral)
        2. Are there likely pivot sweep opportunities?
        3. What's the FVG formation potential? (0-1 scale)
        4. Entry confidence for this session? (0-1 scale)
        5. Specific recommendation: BUY/SELL/WAIT
        
        Provide concise ICT-focused analysis."""
        
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {"role": "system", "content": "You are an expert NQ futures trader using ICT methodology. Provide concise, actionable analysis."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.4
        )
        
        ai_response = response.choices[0].message.content
        print(f"🤖 OpenAI Response: {ai_response[:100]}...")
        
        # Parse AI response
        response_lower = ai_response.lower()
        
        # Extract bias and signals
        if any(word in response_lower for word in ['bullish', 'long', 'buy']):
            bias = 'LONG 📈'
            recommendation = 'BUY SETUP'
        elif any(word in response_lower for word in ['bearish', 'short', 'sell']):
            bias = 'SHORT 📉'
            recommendation = 'SELL SETUP'
        else:
            bias = 'NEUTRAL ⏸️'
            recommendation = 'WAIT'
        
        # Extract confidence
        if any(word in response_lower for word in ['high', 'strong', 'excellent']):
            fvg_quality = 0.8
            entry_confidence = 0.85
        elif any(word in response_lower for word in ['medium', 'moderate']):
            fvg_quality = 0.6
            entry_confidence = 0.65
        else:
            fvg_quality = 0.4
            entry_confidence = 0.45
        
        return jsonify({
            'symbol': symbol,
            'session': session,
            'bias': bias,
            'fvgQuality': fvg_quality,
            'entryConfidence': entry_confidence,
            'marketCondition': f'{session} ACTIVE',
            'recommendation': recommendation,
            'aiAnalysis': ai_response
        })
        
    except Exception as e:
        print(f"❌ OpenAI Error: {e}")
        return jsonify({
            'symbol': symbol,
            'session': session,
            'bias': 'ERROR ❌',
            'fvgQuality': 0.3,
            'entryConfidence': 0.2,
            'marketCondition': 'AI ERROR',
            'recommendation': 'CHECK LOGS'
        })

if __name__ == '__main__':
    print("🚀 Starting simple AI server...")
    app.run(host='127.0.0.1', port=8080, debug=True)