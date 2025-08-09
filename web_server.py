from flask import Flask, render_template_string, send_from_directory, request, jsonify
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client only if API key is available
api_key = os.getenv('OPENAI_API_KEY')
try:
    client = OpenAI(api_key=api_key) if api_key else None
except Exception:
    client = None

app = Flask(__name__)

# Read HTML files and serve them
def read_html_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"<h1>File {filename} not found</h1>"

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
    return read_html_file('tradingview_integration.html')

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
        print(f"API Key exists: {bool(os.getenv('OPENAI_API_KEY'))}")
        print(f"Client exists: {bool(client)}")
        
        if not client:
            return jsonify({
                "error": "OpenAI client not initialized",
                "status": "error"
            }), 500
            
        data = request.get_json()
        prompt = data.get('prompt', 'How can I trade better?')
        
        print(f"Sending request to OpenAI...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional ICT trading analyst. Provide concise, actionable trading advice."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        print(f"OpenAI response received")
        return jsonify({
            "insight": response.choices[0].message.content,
            "status": "success"
        })
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)