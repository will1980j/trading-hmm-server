from flask import Flask, render_template_string, send_from_directory, request, jsonify, session, redirect, url_for
from os import environ, path
from json import loads, dumps
from dotenv import load_dotenv
from openai import OpenAI
from werkzeug.utils import secure_filename
from html import escape
from logging import basicConfig, getLogger, INFO
from csrf_protection import csrf, csrf_protect
from ai_prompts import get_ai_system_prompt
from auth import login_required, authenticate
import math

# Constants
NEWLINE_CHAR = '\n'
CARRIAGE_RETURN_CHAR = '\r'

# Setup logging first
basicConfig(level=INFO)
logger = getLogger(__name__)

# Load environment variables
load_dotenv()

# Database integration
try:
    from database.railway_db import RailwayDB
    db = RailwayDB()
    db_enabled = True
    logger.info("Database connected successfully")
except (ImportError, ConnectionError, Exception) as e:
    logger.error(f"Database connection failed: {str(e).replace(NEWLINE_CHAR, '').replace(CARRIAGE_RETURN_CHAR, '')}")
    db = None
    db_enabled = False

# Initialize OpenAI client only if API key is available
api_key = environ.get('OPENAI_API_KEY')
client = None
if api_key:
    try:
        client = OpenAI(api_key=api_key)
        logger.info("OpenAI client initialized successfully")
    except (ValueError, ConnectionError, Exception) as e:
        logger.error(f"OpenAI client initialization failed: {str(e).replace(NEWLINE_CHAR, '').replace(CARRIAGE_RETURN_CHAR, '')}")
        client = None

app = Flask(__name__)
app.secret_key = environ.get('SECRET_KEY', 'dev-key-change-in-production')
csrf.init_app(app)

# Read HTML files and serve them
def read_html_file(filename):
    try:
        # Secure filename to prevent path traversal
        secure_name = secure_filename(filename)
        if not secure_name or secure_name != filename:
            logger.warning(f"Invalid filename rejected: {filename.replace(NEWLINE_CHAR, '').replace(CARRIAGE_RETURN_CHAR, '')}")
            return "<h1>Trading Dashboard</h1><p>Invalid file request.</p><a href='/health'>Health Check</a>"
        
        # Use relative path for better portability
        file_path = path.join(path.dirname(__file__), secure_name)
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except (FileNotFoundError, IOError) as e:
        logger.warning(f"File access error for {filename}: {str(e).replace(NEWLINE_CHAR, '').replace(CARRIAGE_RETURN_CHAR, '')}")
        return "<h1>Trading Dashboard</h1><p>File not found. Server is running.</p><a href='/health'>Health Check</a>"
    except Exception as e:
        logger.error(f"Unexpected error reading file {filename}: {str(e).replace(NEWLINE_CHAR, '').replace(CARRIAGE_RETURN_CHAR, '')}")
        return "<h1>Trading Dashboard</h1><p>Server error. Please try again.</p><a href='/health'>Health Check</a>"

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate(username, password):
            session['authenticated'] = True
            return redirect('/')
        return render_template_string(read_html_file('login.html'), error='Invalid credentials')
    return render_template_string(read_html_file('login.html'))

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect('/login')

# Main routes - now protected
@app.route('/')
@login_required
def dashboard():
    return read_html_file('advanced_trading_dashboard.html')

@app.route('/dashboard')
@login_required
def advanced_dashboard():
    return read_html_file('advanced_trading_dashboard.html')

@app.route('/trade-manager')
@login_required
def trade_manager():
    return read_html_file('trade_manager.html')

@app.route('/prop-portfolio')
@login_required
def prop_portfolio():
    return read_html_file('prop_firms_v2.html')

@app.route('/financial-summary')
@login_required
def financial_summary():
    return read_html_file('financial_summary.html')

@app.route('/reporting-hub')
@login_required
def reporting_hub():
    return read_html_file('reporting_hub.html')

@app.route('/tradingview')
@login_required
def tradingview():
    return read_html_file('trading_dashboard.html')

@app.route('/trading-dashboard')
@login_required
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

@app.route('/notification_system.js')
def notification_system_js():
    return send_from_directory('.', 'notification_system.js', mimetype='application/javascript')

# Serve images from root
@app.route('/style_preview.html')
def style_preview():
    return read_html_file('style_preview.html')

@app.route('/style_preview2.html')
def style_preview2():
    return read_html_file('style_preview2.html')

@app.route('/style_preview3.html')
def style_preview3():
    return read_html_file('style_preview3.html')

@app.route('/styles')
@login_required
def style_selector():
    return read_html_file('style_selector.html')

@app.route('/style_switcher.js')
def style_switcher_js():
    return send_from_directory('.', 'style_switcher.js', mimetype='application/javascript')

@app.route('/professional_styles.js')
def professional_styles_js():
    return send_from_directory('.', 'professional_styles.js', mimetype='application/javascript')

@app.route('/nighthawk_terminal.html')
@login_required
def nighthawk_terminal():
    return read_html_file('nighthawk_terminal.html')

@app.route('/emerald_mainframe.html')
@login_required
def emerald_mainframe():
    return read_html_file('emerald_mainframe.html')

@app.route('/amber_oracle.html')
@login_required
def amber_oracle():
    return read_html_file('amber_oracle.html')

@app.route('/<path:filename>')
def serve_files(filename):
    if filename.endswith(('.jpg', '.png', '.gif', '.ico', '.pdf')):
        return send_from_directory('.', filename)
    return "File not found", 404

# API endpoint for trading data
@app.route('/api/trading-data')
@login_required
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
@login_required
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
        logger.info(f"AI insights request: {prompt[:50].replace(NEWLINE_CHAR, '').replace(CARRIAGE_RETURN_CHAR, '')}...")
        logger.debug(f"Has trading data: {bool(trading_data)}")
        
        # Get centralized system prompt for better maintainability
        system_prompt = get_ai_system_prompt()
        
        # Add trading context if available
        context_info = ""
        if trading_data.get('summary'):
            summary = trading_data['summary']
            context_info = f"\n\nTrader's Current Stats:\n- Total Trades: {summary.get('totalTrades', 'N/A')}\n- Win Rate: {summary.get('winRate', 'N/A')}\n- Funded Accounts: {summary.get('fundedAccounts', 'N/A')}"
        
        if trading_data.get('recentTrades'):
            recent = trading_data['recentTrades'][-3:]  # Last 3 trades
            context_info += f"\n\nRecent Trades: {len(recent)} trades with outcomes: {[t.get('outcome', 'unknown') for t in recent]}"
        
        model_name = environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt + context_info},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.8
        )
        
        logger.info("OpenAI API call successful")
        return jsonify({
            "insight": response.choices[0].message.content,
            "status": "success"
        })
    except Exception as e:
        logger.error(f"Error in ai_insights: {str(e)}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

# Webhook for storing trading data
@app.route('/webhook', methods=['GET', 'POST'])
@login_required
@csrf_protect
def webhook():
    if request.method == 'GET':
        return jsonify({
            "message": "Webhook endpoint ready",
            "database": "connected" if db_enabled else "offline",
            "usage": "Send POST with JSON data"
        })
    try:
        # Handle different content types
        if request.is_json:
            data = request.get_json()
        else:
            # Try to parse as JSON from raw data
            raw_data = request.get_data(as_text=True)
            data = loads(raw_data) if raw_data else None
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Sanitize log input to prevent log injection
        data_type = str(type(data).__name__).replace(NEWLINE_CHAR, '').replace(CARRIAGE_RETURN_CHAR, '')
        logger.info(f"Webhook received data: {data_type}")
        
        if db_enabled and db:
            # Store market data if provided
            if 'current_price' in data:
                db.store_market_data(data.get('symbol', 'NQ1!'), {
                    'close': data['current_price'],
                    'timestamp': data.get('timestamp')
                })
            
            # Store trading signal if provided
            if 'signal_type' in data:
                db.store_signal({
                    'symbol': data.get('symbol', 'NQ1!'),
                    'type': data.get('signal_type'),
                    'entry': data.get('entry_price', 0),
                    'confidence': data.get('confidence', 0.8),
                    'reason': data.get('reason', 'Manual entry')
                })
            
            # Store ICT levels if provided
            for level_type in ['fvgs', 'order_blocks', 'liquidity_levels']:
                for level in data.get(level_type, []):
                    db.store_ict_level({
                        'symbol': data.get('symbol', 'NQ1!'),
                        'type': level_type.upper(),
                        'top': level.get('top', 0),
                        'bottom': level.get('bottom', 0),
                        'strength': level.get('strength', 0.5),
                        'active': level.get('active', True)
                    })
        
        return jsonify({"status": "success", "database": "stored" if db_enabled else "offline"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Bulk trade upload
@app.route('/upload-trades', methods=['POST'])
@login_required
@csrf_protect
def upload_trades():
    try:
        data = request.get_json()
        trades = data.get('trades', [])
        
        if not db_enabled or not db:
            return jsonify({"error": "Database not available"}), 500
        
        stored_count = 0
        for trade in trades:
            try:
                db.store_signal({
                    'symbol': 'NQ1!',
                    'type': trade.get('bias', 'LONG'),
                    'entry': trade.get('entryPrice', 0),
                    'confidence': abs(trade.get('rScore', 0)) / 10,
                    'reason': f"{trade.get('session', 'UNKNOWN')} - {trade.get('rScore', 0)}R - {trade.get('date', '')}"
                })
                stored_count += 1
            except Exception as e:
                logger.error(f"Failed to store trade: {str(e).replace(NEWLINE_CHAR, '').replace(CARRIAGE_RETURN_CHAR, '')}")
        
        return jsonify({
            "status": "success",
            "uploaded": stored_count,
            "total": len(trades)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get trades from database
@app.route('/api/trades')
def get_trades():
    try:
        if not db_enabled or not db:
            return jsonify({"trades": [], "error": "Database not available"})
        
        try:
            cursor = db.conn.cursor()
            cursor.execute("""
                SELECT id, symbol, signal_type, entry_price, confidence, reason, 
                       timestamp, created_at
                FROM trading_signals 
                ORDER BY created_at DESC 
                LIMIT 100
            """)
        except Exception as e:
            db.conn.rollback()
            error_msg = str(e).replace(NEWLINE_CHAR, ' ').replace(CARRIAGE_RETURN_CHAR, ' ')
            logger.error(f"Database query error: {error_msg}")
            raise e
        
        trades = [{
            'id': row['id'],
            'symbol': row['symbol'],
            'bias': row['signal_type'],
            'entry': row['entry_price'],
            'confidence': row['confidence'],
            'reason': row['reason'],
            'timestamp': str(row['timestamp']),
            'created_at': str(row['created_at'])
        } for row in cursor.fetchall()]
        
        return jsonify({"trades": trades, "count": len(trades)})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Manual signal entry
@app.route('/add-signal', methods=['POST'])
@login_required
@csrf_protect
def add_signal():
    try:
        data = request.get_json() or request.form.to_dict()
        
        if db_enabled and db:
            try:
                # Validate and convert numeric inputs with NaN protection
                entry_price_str = str(data.get('entry_price', 0)).lower()
                confidence_str = str(data.get('confidence', 0.8)).lower()
                
                # Check for NaN, infinity, or invalid values
                if any(invalid in entry_price_str for invalid in ['nan', 'inf', '-inf']):
                    return jsonify({"error": "Invalid entry price value"}), 400
                if any(invalid in confidence_str for invalid in ['nan', 'inf', '-inf']):
                    return jsonify({"error": "Invalid confidence value"}), 400
                    
                entry_price = float(data.get('entry_price', 0))
                confidence = float(data.get('confidence', 0.8))
                
                # Additional validation for finite numbers
                if not (math.isfinite(entry_price) and math.isfinite(confidence)):
                    return jsonify({"error": "Numeric values must be finite"}), 400
                
                # Validate inputs
                if entry_price < 0:
                    return jsonify({"error": "Entry price cannot be negative"}), 400
                if not 0 <= confidence <= 1:
                    return jsonify({"error": "Confidence must be between 0 and 1"}), 400
                    
                result = db.store_signal({
                    'symbol': data.get('symbol', 'NQ1!'),
                    'type': data.get('signal_type', 'LONG'),
                    'entry': entry_price,
                    'confidence': confidence,
                    'reason': data.get('reason', 'Manual entry')
                })
            except (ValueError, TypeError) as e:
                logger.error(f"Invalid input data: {e}")
                return jsonify({"error": "Invalid numeric input"}), 400
            
            return jsonify({
                "status": "success", 
                "message": "Signal stored successfully",
                "data": data
            })
        else:
            return jsonify({"error": "Database not available"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get recent signals
@app.route('/api/signals')
def get_signals():
    try:
        if db_enabled and db:
            try:
                cursor = db.conn.cursor()
                cursor.execute("""
                    SELECT id, symbol, signal_type, entry_price, confidence, reason, timestamp, created_at 
                    FROM trading_signals 
                    ORDER BY created_at DESC 
                    LIMIT 20
                """)
                signals = cursor.fetchall()
                
                return jsonify({
                    "signals": [dict(signal) for signal in signals],
                    "count": len(signals)
                })
            except (ConnectionError, Exception) as e:
                logger.error(f"Database query error: {str(e).replace(NEWLINE_CHAR, '').replace(CARRIAGE_RETURN_CHAR, '')}")
                return jsonify({"error": "Database query failed"}), 500
        else:
            return jsonify({"error": "Database not available"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy", 
        "message": "Trading server running",
        "database": "connected" if db_enabled else "offline",
        "csrf_token": csrf.generate_csrf_token()
    })

# Prop firm endpoints
@app.route('/api/prop-firms')
def get_prop_firms():
    try:
        month_year = request.args.get('month', '2024-08')
        if not db_enabled or not db:
            return jsonify({"firms": []})
        
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT firm_name, status, account_size, monthly_profit 
            FROM prop_firms WHERE month_year = %s
        """, (month_year,))
        
        firms = []
        for row in cursor.fetchall():
            firms.append({
                'firmName': row[0],
                'status': row[1], 
                'accountSize': float(row[2]) if row[2] else 0,
                'monthlyProfit': float(row[3]) if row[3] else 0
            })
        
        return jsonify({"firms": firms})
    except (ConnectionError, ValueError, Exception) as e:
        error_msg = str(e).replace(NEWLINE_CHAR, ' ').replace(CARRIAGE_RETURN_CHAR, ' ')
        logger.error(f"Prop firms query error: {error_msg}")
        return jsonify({"firms": []})

@app.route('/api/scrape-propfirms')
def scrape_propfirms():
    try:
        from propfirm_scraper import run_daily_scraper
        firms_found = run_daily_scraper()
        return jsonify({
            "status": "success",
            "firms_found": firms_found,
            "message": f"Scraped {firms_found} prop firms"
        })
    except (ImportError, AttributeError, Exception) as e:
        logger.error(f"Scraper error: {str(e).replace(NEWLINE_CHAR, '').replace(CARRIAGE_RETURN_CHAR, '')}")
        return jsonify({"error": "Scraper unavailable"}), 500

if __name__ == '__main__':
    port = int(environ.get('PORT', 5000))
    debug_mode = environ.get('DEBUG', 'False').lower() == 'true'
    logger.info(f"Starting server on port {port}, debug={debug_mode}")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)