#!/usr/bin/env python3
"""
Ultimate OpenAI Trading Integration
Maximum AI assistance for trading decisions
"""

from flask import Flask, request, jsonify
import openai
import os
from datetime import datetime, time
import json

app = Flask(__name__)
openai.api_key = os.getenv('OPENAI_API_KEY')

# Market context for AI
MARKET_CONTEXT = {
    "current_session": None,
    "recent_signals": [],
    "market_structure": {},
    "key_levels": {}
}

@app.route('/api/ai-trading-webhook', methods=['POST'])
def ai_trading_webhook():
    """Ultimate AI-powered trading webhook"""
    try:
        data = request.get_json()
        
        # Enhanced data from TradingView
        trading_data = {
            'symbol': data.get('symbol', 'NQ1!'),
            'price': float(data.get('price', 0)),
            'action': data.get('action', 'ANALYZE'),
            'timeframe': data.get('timeframe', '5m'),
            'volume': data.get('volume', 0),
            'rsi': data.get('rsi', 50),
            'macd': data.get('macd', 0),
            'session': get_current_session(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Get comprehensive AI analysis
        ai_analysis = get_comprehensive_ai_analysis(trading_data)
        
        # Update market context
        update_market_context(trading_data, ai_analysis)
        
        # Generate trading decision
        trading_decision = generate_trading_decision(ai_analysis)
        
        result = {
            'timestamp': trading_data['timestamp'],
            'market_data': trading_data,
            'ai_analysis': ai_analysis,
            'trading_decision': trading_decision,
            'confidence': ai_analysis.get('confidence', 0.5)
        }
        
        print(f"🤖 Ultimate AI Analysis: {json.dumps(result, indent=2)}")
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def get_comprehensive_ai_analysis(data):
    """Get deep AI analysis with maximum context"""
    
    # Build comprehensive prompt with all available context
    prompt = f"""
    You are an expert ICT (Inner Circle Trader) analyst with deep market structure knowledge.
    
    CURRENT MARKET DATA:
    Symbol: {data['symbol']}
    Price: ${data['price']}
    Session: {data['session']}
    Timeframe: {data['timeframe']}
    Volume: {data['volume']}
    RSI: {data['rsi']}
    MACD: {data['macd']}
    Time: {datetime.now().strftime('%H:%M:%S EST')}
    
    RECENT CONTEXT:
    {get_recent_context()}
    
    ANALYSIS REQUIRED:
    1. Market Structure Analysis (HH, HL, LH, LL)
    2. Liquidity Analysis (where are stops likely?)
    3. Fair Value Gap identification
    4. Order Block analysis
    5. Session bias and institutional flow
    6. Risk/Reward assessment
    7. Entry timing and confluence
    
    Provide comprehensive analysis in JSON:
    {{
        "market_structure": {{
            "trend": "BULLISH/BEARISH/RANGING",
            "key_levels": ["support_levels", "resistance_levels"],
            "liquidity_zones": ["buy_stops", "sell_stops"]
        }},
        "ict_analysis": {{
            "fvg_present": true/false,
            "fvg_quality": 0.0-1.0,
            "order_blocks": ["bullish_ob", "bearish_ob"],
            "imbalances": ["price_levels"],
            "session_bias": "LONG/SHORT/NEUTRAL"
        }},
        "entry_analysis": {{
            "signal_strength": 0.0-1.0,
            "confluence_factors": ["list_of_confluences"],
            "entry_price": number,
            "stop_loss": number,
            "take_profit_1": number,
            "take_profit_2": number,
            "risk_reward": number
        }},
        "market_psychology": {{
            "institutional_flow": "BUYING/SELLING/NEUTRAL",
            "retail_sentiment": "BULLISH/BEARISH/MIXED",
            "smart_money_direction": "LONG/SHORT/SIDEWAYS"
        }},
        "timing_analysis": {{
            "session_context": "analysis of current session",
            "macro_window": "upcoming key times",
            "volatility_expectation": "HIGH/MEDIUM/LOW"
        }},
        "recommendation": {{
            "action": "BUY/SELL/WAIT",
            "confidence": 0.0-1.0,
            "reasoning": "detailed explanation",
            "risk_level": "LOW/MEDIUM/HIGH",
            "position_size": "percentage of account"
        }}
    }}
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert ICT trader with 20+ years experience. Provide detailed, actionable analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=2000
        )
        
        analysis = json.loads(response.choices[0].message.content)
        return analysis
        
    except Exception as e:
        return {
            "error": str(e),
            "recommendation": {"action": "WAIT", "confidence": 0.1}
        }

def get_recent_context():
    """Get recent market context for AI"""
    context = f"""
    Recent Signals: {len(MARKET_CONTEXT['recent_signals'])} in last hour
    Current Session: {MARKET_CONTEXT['current_session']}
    Key Levels: {MARKET_CONTEXT.get('key_levels', {})}
    Market Structure: {MARKET_CONTEXT.get('market_structure', {})}
    """
    return context

def update_market_context(data, analysis):
    """Update global market context"""
    MARKET_CONTEXT['current_session'] = data['session']
    MARKET_CONTEXT['recent_signals'].append({
        'timestamp': data['timestamp'],
        'price': data['price'],
        'analysis': analysis.get('recommendation', {})
    })
    
    # Keep only last 10 signals
    MARKET_CONTEXT['recent_signals'] = MARKET_CONTEXT['recent_signals'][-10:]
    
    # Update key levels from AI analysis
    if 'market_structure' in analysis:
        MARKET_CONTEXT['key_levels'] = analysis['market_structure'].get('key_levels', [])
        MARKET_CONTEXT['market_structure'] = analysis['market_structure']

def generate_trading_decision(analysis):
    """Generate final trading decision with AI reasoning"""
    try:
        decision_prompt = f"""
        Based on this comprehensive analysis:
        {json.dumps(analysis, indent=2)}
        
        Generate final trading decision:
        {{
            "trade": true/false,
            "direction": "LONG/SHORT",
            "entry_method": "MARKET/LIMIT/STOP",
            "position_size": "1-3 contracts",
            "stop_placement": "exact price",
            "profit_targets": ["tp1", "tp2"],
            "trade_management": "how to manage the trade",
            "exit_strategy": "when to exit",
            "notes": "key points to remember"
        }}
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": decision_prompt}],
            temperature=0.1
        )
        
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        return {"trade": False, "notes": f"Decision error: {str(e)}"}

def get_current_session():
    """Determine current trading session"""
    now = datetime.now().time()
    
    if time(2, 0) <= now < time(8, 0):
        return "ASIA"
    elif time(8, 0) <= now < time(13, 0):
        return "LONDON"
    elif time(13, 0) <= now < time(17, 0):
        return "NY_OVERLAP"
    elif time(17, 0) <= now < time(20, 0):
        return "NY_PM"
    else:
        return "AFTER_HOURS"

@app.route('/api/ai-market-summary', methods=['GET'])
def ai_market_summary():
    """Get AI-powered market summary"""
    summary_prompt = f"""
    Provide current market summary based on:
    
    Recent Context: {get_recent_context()}
    Current Session: {get_current_session()}
    
    Generate market summary:
    {{
        "session_outlook": "what to expect this session",
        "key_levels_to_watch": ["important price levels"],
        "market_bias": "overall direction",
        "trading_opportunities": ["potential setups"],
        "risk_factors": ["what could go wrong"],
        "recommended_approach": "how to trade today"
    }}
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": summary_prompt}],
            temperature=0.3
        )
        
        summary = json.loads(response.choices[0].message.content)
        return jsonify(summary)
        
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    print("🤖 Ultimate OpenAI Trading System Starting...")
    app.run(host='0.0.0.0', port=8080, debug=True)