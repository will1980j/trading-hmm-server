from flask import Flask, render_template_string, send_from_directory, request, jsonify
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client only if API key is available
api_key = os.getenv('OPENAI_API_KEY')
client = None
if api_key:
    try:
        client = OpenAI(api_key=api_key)
        print(f"OpenAI client initialized successfully")
    except Exception as e:
        print(f"OpenAI client initialization failed: {e}")
        client = None

app = Flask(__name__)

# Read HTML files and serve them
def read_html_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: File {filename} not found")
        return f"<h1>Trading Dashboard</h1><p>File {filename} not found. Server is running.</p><a href='/health'>Health Check</a>"

# Main routes
@app.route('/')
def dashboard():
    return read_html_file('advanced_trading_dashboard.html')

@app.route('/dashboard')
def advanced_dashboard():
    return read_html_file('advanced_trading_dashboard.html')

@app.route('/trade-manager')
def trade_manager():
    return read_html_file('trade_manager.html')

@app.route('/prop-portfolio')
def prop_portfolio():
    return read_html_file('prop_firms_v2.html')

@app.route('/financial-summary')
def financial_summary():
    return read_html_file('financial_summary.html')

@app.route('/reporting-hub')
def reporting_hub():
    return read_html_file('reporting_hub.html')

@app.route('/tradingview')
def tradingview():
    return read_html_file('trading_dashboard.html')

@app.route('/trading-dashboard')
def trading_dashboard():
    return read_html_file('trading_dashboard.html')

# Serve static files (CSS, JS, images)
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# Serve JavaScript files from root
@app.route('/api_integration.js')
def api_integration_js():
    return send_from_directory('.', 'api_integration.js', mimetype='application/javascript')

@app.route('/chatbot.js')
def chatbot_js():
    return send_from_directory('.', 'chatbot.js', mimetype='application/javascript')

@app.route('/trading_empire_kb.js')
def trading_empire_kb_js():
    return send_from_directory('.', 'trading_empire_kb.js', mimetype='application/javascript')

# Serve images from root
@app.route('/<path:filename>')
def serve_files(filename):
    if filename.endswith(('.jpg', '.png', '.gif', '.ico', '.pdf')):
        return send_from_directory('.', filename)
    return "File not found", 404

# API endpoint for trading data
@app.route('/api/trading-data')
def api_trading_data():
    format_type = request.args.get('format', 'json')
    
    sample_data = {
        "trades": [
            {"date": "2024-01-15", "symbol": "EURUSD", "outcome": "win", "rTarget": 2, "profit": 200},
            {"date": "2024-01-16", "symbol": "GBPUSD", "outcome": "loss", "rTarget": 1, "profit": -100}
        ],
        "summary": {
            "totalTrades": 2,
            "winRate": "50%",
            "totalProfit": 100
        }
    }
    
    if format_type == 'gamma':
        return jsonify({
            "title": "Trading Performance Dashboard",
            "summary": sample_data["summary"],
            "timestamp": "2024-01-15T14:23:47Z"
        })
    
    return jsonify(sample_data)

# OpenAI API endpoint for trading insights
@app.route('/api/ai-insights', methods=['POST'])
def ai_insights():
    try:
        print("AI insights endpoint called")
        if not client:
            print("Client not available")
            return jsonify({
                "error": "OpenAI client not initialized",
                "status": "error"
            }), 500
            
        data = request.get_json()
        prompt = data.get('prompt', 'How can I trade better?')
        trading_data = data.get('data', {})
        trading_data = data.get('data', {})
        print(f"Prompt: {prompt[:50]}...")
        print(f"Has trading data: {bool(trading_data)}")
        
        print("Making OpenAI API call...")
        # Enhanced system prompt with trading context
        system_prompt = """
You are the ultimate Trading Empire Advisor - a multi-disciplinary expert combining:

🎯 TRADING MASTERY:
- ICT concepts (Fair Value Gaps, Order Blocks, Liquidity Sweeps, Market Structure)
- Futures markets (ES, NQ, YM, RTY) and Forex (majors, minors, exotics)
- TradingView platform expertise (indicators, Pine Script, alerts, strategies)
- Prop firm optimization (FTMO, MyForexFunds, The5ers, etc.)
- Risk management and systematic trading approaches

💼 BUSINESS & FINANCE:
- Trading business structure and scaling strategies
- Australian tax optimization for traders (CGT, business deductions, structures)
- Cash flow management and profit allocation systems
- Technology stack development and platform integration
- Performance analytics and business intelligence

🏠 WEALTH CREATION & PROPERTY:
- Property investment using trading profits (residential, commercial, REIT)
- Australian property market analysis and financing strategies
- Portfolio diversification beyond trading (stocks, bonds, alternatives)
- Wealth preservation and generational planning
- Investment property tax strategies and depreciation

🚀 STRATEGIC GROWTH:
- Platform development and feature enhancement
- Revenue stream diversification (signals, education, managed accounts)
- Team building and operational systems
- Market expansion and competitive positioning
- Exit strategies and business valuation

Provide specific, actionable advice with Australian context. Think like a CFO, CTO, and wealth advisor combined.
"""
        
        # Add trading context if available
        context_info = ""
        if trading_data.get('summary'):
            summary = trading_data['summary']
            context_info = f"\n\nTrader's Current Stats:\n- Total Trades: {summary.get('totalTrades', 'N/A')}\n- Win Rate: {summary.get('winRate', 'N/A')}\n- Funded Accounts: {summary.get('fundedAccounts', 'N/A')}"
        
        if trading_data.get('recentTrades'):
            recent = trading_data['recentTrades'][-3:]  # Last 3 trades
            context_info += f"\n\nRecent Trades: {len(recent)} trades with outcomes: {[t.get('outcome', 'unknown') for t in recent]}"
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt + context_info},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.8
        )
        
        print("OpenAI API call successful")
        return jsonify({
            "insight": response.choices[0].message.content,
            "status": "success"
        })
    except Exception as e:
        print(f"Error in ai_insights: {str(e)}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "message": "Trading server running"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)