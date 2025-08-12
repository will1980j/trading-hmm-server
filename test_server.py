from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import OpenAI
from os import environ
from dotenv import load_dotenv
from datetime import datetime
from extended_market_data import ExtendedMarketData

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize OpenAI and Market Data
client = OpenAI(api_key=environ.get('OPENAI_API_KEY')) if environ.get('OPENAI_API_KEY') else None
market_provider = ExtendedMarketData()

@app.route('/api/test')
def test():
    print("✅ TEST ENDPOINT CALLED")
    return jsonify({"message": "WORKING"})

# Store current bias from indicator
current_indicator_bias = {'bias': 'Unknown', 'timestamp': 0}

@app.route('/api/update-bias', methods=['POST'])
def update_bias():
    global current_indicator_bias
    try:
        data = request.get_json()
        current_indicator_bias = {
            'bias': data.get('bias', 'Unknown'),
            'source': data.get('source', ''),
            'timestamp': data.get('timestamp', 0)
        }
        print(f"📊 Indicator bias updated: {current_indicator_bias['bias']} from '{current_indicator_bias['source']}'")
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"❌ Bias update error: {e}")
        return jsonify({'status': 'error'})

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
        # Get real market data - NO FALLBACK
        market_data = market_provider.get_nq_data()
        if not market_data:
            return jsonify({
                'symbol': symbol,
                'session': session,
                'bias': 'NO DATA ❌',
                'fvgQuality': 0.0,
                'entryConfidence': 0.0,
                'marketCondition': 'MARKET DATA UNAVAILABLE',
                'recommendation': 'WAIT - NO DATA'
            })
        
        # Simple market structure for extended data
        market_structure = {
            'h1_bias': market_data.get('h1_bias', 'Neutral'),
            'sweep_potential_high': abs(market_data['price'] - market_data['session_high']) < 10,
            'sweep_potential_low': abs(market_data['price'] - market_data['session_low']) < 10
        }
        
        # Session info
        session_info = {
            'liquidity': 'EXTENDED' if market_provider.get_market_hours_status() == 'EXTENDED_HOURS' else 'HIGH',
            'typical_range': '20-60 points',
            'bias_tendency': 'CONTINUATION'
        }
        
        # Build enhanced prompt with ONLY real data
        real_price = market_data.get('price', float(price))
        session_high = market_data.get('session_high', real_price + 50)
        session_low = market_data.get('session_low', real_price - 50)
        trend = market_structure.get('h1_bias', 'UNKNOWN')
        position_in_range = 50
            
        prompt = f"""NQ Futures ICT LIQUIDITY GRAB Analysis:
            
            TRADER'S EXACT STRATEGY (from chart example):
            - Uses FVG Multi-Timeframe Bias Indicator (1H bias currently: {market_data.get('h1_bias', 'UNKNOWN')})
            - Waits for price to sweep 1-minute pivot highs/lows (liquidity grab)
            - Enters ONLY on FVG or IFVG formation after the sweep
            - Risk management: SL below/above FVG base, move to 1:1 breakeven, test R-targets
            - Chart shows: Blue FVG boxes, pivot levels, clear sweep then reversal entry
            
            CURRENT MARKET STATE:
            - NQ Price: {real_price}
            - 1H FVG BIAS: {market_data.get('h1_bias', 'UNKNOWN')} (from your indicator at bottom of chart)
            - This bias is determined by your Multi-Instrument FVG Scanner indicator
            - Current indicator reading: {market_data.get('h1_bias', 'UNKNOWN')} bias on 1H timeframe
            - Session High: {session_high} (LIQUIDITY POOL)
            - Session Low: {session_low} (LIQUIDITY POOL) 
            - 1min Pivot Levels: Near session extremes
            - Sweep Setup: {market_structure.get('sweep_potential_high', False)} (high) | {market_structure.get('sweep_potential_low', False)} (low)
            
            SESSION: {session} ({session_info['liquidity']} liquidity) - {market_provider.get_market_hours_status()}
            
            PRECISE ENTRY ANALYSIS (Based on your indicator):
            1. INDICATOR BIAS: Your FVG Scanner shows {market_data.get('h1_bias', 'UNKNOWN')} on 1H timeframe
            2. BIAS CONFIRMATION: Is this {market_data.get('h1_bias', 'UNKNOWN')} bias aligned across multiple timeframes?
            3. LIQUIDITY SWEEP: Based on {market_data.get('h1_bias', 'UNKNOWN')} bias, which sweep direction to watch?
            4. FVG FORMATION: After sweep, rate the gap formation potential
            5. ENTRY EXECUTION: 1min timing for FVG entry matching {market_data.get('h1_bias', 'UNKNOWN')} direction
            
            CRITICAL: Your indicator at bottom shows {market_data.get('h1_bias', 'UNKNOWN')} bias - AI must acknowledge this specific reading
            Reference the indicator: Based on your FVG Scanner indicator showing {market_data.get('h1_bias', 'UNKNOWN')} bias"""
        # Build prompt with real data
        prompt = f"""NQ Futures ICT Analysis - MUST ACKNOWLEDGE INDICATOR:
        
        CRITICAL: Your FVG Multi-Instrument Scanner indicator at bottom of chart shows: {market_data.get('h1_bias', 'UNKNOWN')} bias on 1H timeframe
        
        Current Market Data:
        - NQ Price: {market_data.get('price', 'Unknown')}
        - Session High: {market_data.get('session_high', 'Unknown')}
        - Session Low: {market_data.get('session_low', 'Unknown')}
        - 1H Bias from YOUR indicator: {market_data.get('h1_bias', 'UNKNOWN')}
        
        MANDATORY: Start your response with "I can see your FVG Scanner indicator shows {market_data.get('h1_bias', 'UNKNOWN')} bias on the 1H timeframe."
        
        Then provide ICT analysis based on this {market_data.get('h1_bias', 'UNKNOWN')} bias from your indicator."""
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
        
        # Parse AI response but FORCE alignment with FVG bias
        response_lower = ai_response.lower()
        
        # Get FVG bias from your indicator
        fvg_bias = market_data.get('h1_bias', 'Neutral') if market_data else 'Neutral'
        print(f"📈 Using FVG bias from your indicator: {fvg_bias}")
        
        # Parse AI response for FVG formation after sweep
        has_fvg_setup = any(word in response_lower for word in ['fvg', 'gap', 'formation', 'entry'])
        has_sweep = any(word in response_lower for word in ['sweep', 'pivot', 'liquidity'])
        
        # CORRECT LOGIC: Bias determines direction, look for ANY pivot sweep + FVG
        if fvg_bias == 'Bullish':
            # Bullish bias = look for ANY sweep then BUY on FVG
            if has_sweep and has_fvg_setup:
                bias = 'LONG 📈'
                recommendation = 'BUY FVG ENTRY'
            elif has_sweep:
                bias = 'LONG 📈'
                recommendation = 'WAIT FOR FVG'
            else:
                bias = 'LONG 📈'
                recommendation = 'WAIT FOR SWEEP'
        elif fvg_bias == 'Bearish':
            # Bearish bias = look for ANY sweep then SELL on FVG
            if has_sweep and has_fvg_setup:
                bias = 'SHORT 📉'
                recommendation = 'SELL FVG ENTRY'
            elif has_sweep:
                bias = 'SHORT 📉'
                recommendation = 'WAIT FOR FVG'
            else:
                bias = 'SHORT 📉'
                recommendation = 'WAIT FOR SWEEP'
        else:
            bias = 'NEUTRAL ⏸️'
            recommendation = 'NO BIAS - WAIT'
        
        # Extract confidence with real data context
        confidence_words = ['high', 'strong', 'excellent', 'very', 'good']
        medium_words = ['medium', 'moderate', 'fair', 'decent']
        
        if any(word in response_lower for word in confidence_words):
            fvg_quality = 0.85
            entry_confidence = 0.9
        elif any(word in response_lower for word in medium_words):
            fvg_quality = 0.65
            entry_confidence = 0.7
        else:
            fvg_quality = 0.45
            entry_confidence = 0.5
            
        # Enhanced market condition with real data
        if market_data:
            trend_info = market_structure.get('trend', 'UNKNOWN')
            market_condition = f'{session} | {trend_info}'
        else:
            market_condition = f'{session} ACTIVE'
        
        return jsonify({
            'symbol': symbol,
            'session': session,
            'bias': f"{fvg_bias} (from indicator)",
            'fvgQuality': fvg_quality,
            'entryConfidence': entry_confidence,
            'marketCondition': f"{market_condition} | Indicator: {fvg_bias}",
            'recommendation': recommendation,
            'aiAnalysis': ai_response
        })
        
    except Exception as e:
        print(f"❌ OpenAI Error: {e}")
        return jsonify({
            'symbol': symbol,
            'session': session,
            'fvgQuality': 0.3,
            'entryConfidence': 0.2,
            'marketCondition': 'AI ERROR',
            'recommendation': 'CHECK LOGS'
        })

if __name__ == '__main__':
    print("Starting test server with OpenAI...")
    app.run(host='127.0.0.1', port=8080, debug=True)