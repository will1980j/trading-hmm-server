from flask import Flask, render_template_string, send_from_directory, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from os import environ, path
from json import loads, dumps
from dotenv import load_dotenv
from openai import OpenAI
from werkzeug.utils import secure_filename
from html import escape
from logging import basicConfig, getLogger, INFO
from markupsafe import escape as markup_escape, Markup
from csrf_protection import csrf, csrf_protect
from ai_prompts import get_ai_system_prompt, get_chart_analysis_prompt, get_strategy_summary_prompt, get_risk_assessment_prompt
from news_api import NewsAPI, get_market_sentiment, extract_key_levels
from datetime import datetime
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
except (ImportError, ConnectionError) as e:
    safe_error = escape(str(e)[:200]).replace(NEWLINE_CHAR, '').replace(CARRIAGE_RETURN_CHAR, '')
    logger.error(f"Database connection failed: {safe_error}")
    db = None
    db_enabled = False
except Exception as e:
    safe_error = escape(str(e)[:200]).replace(NEWLINE_CHAR, '').replace(CARRIAGE_RETURN_CHAR, '')
    logger.error(f"Unexpected database error: {safe_error}")
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
CORS(app, origins=['chrome-extension://abndgpgodnhhkchaoiiopnondcpmnanc', 'https://www.tradingview.com'], supports_credentials=True)
csrf.init_app(app)

# Read HTML files and serve them
def read_html_file(filename):
    try:
        # Secure filename to prevent path traversal
        secure_name = secure_filename(filename)
        if not secure_name or secure_name != filename:
            safe_filename = escape(str(filename)[:100]).replace(NEWLINE_CHAR, '').replace(CARRIAGE_RETURN_CHAR, '')
            logger.warning(f"Invalid filename rejected: {safe_filename}")
            return "<h1>Trading Dashboard</h1><p>Invalid file request.</p><a href='/health'>Health Check</a>"
        
        # Use relative path for better portability
        file_path = path.join(path.dirname(__file__), secure_name)
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except (FileNotFoundError, IOError) as e:
        safe_filename = escape(str(filename)[:100]).replace(NEWLINE_CHAR, '').replace(CARRIAGE_RETURN_CHAR, '')
        safe_error = escape(str(e)[:200]).replace(NEWLINE_CHAR, '').replace(CARRIAGE_RETURN_CHAR, '')
        logger.warning(f"File access error for {safe_filename}: {safe_error}")
        return "<h1>Trading Dashboard</h1><p>File not found. Server is running.</p><a href='/health'>Health Check</a>"
    except Exception as e:
        safe_filename = escape(str(filename)[:100]).replace(NEWLINE_CHAR, '').replace(CARRIAGE_RETURN_CHAR, '')
        safe_error = escape(str(e)[:200]).replace(NEWLINE_CHAR, '').replace(CARRIAGE_RETURN_CHAR, '')
        logger.error(f"Unexpected error reading file {safe_filename}: {safe_error}")
        return "<h1>Trading Dashboard</h1><p>Server error. Please try again.</p><a href='/health'>Health Check</a>"

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            error_msg = markup_escape('Username and password are required')
            return render_template_string(read_html_file('login.html'), error=error_msg)
            
        if authenticate(username, password):
            session['authenticated'] = True
            return redirect('/')
            
        error_msg = markup_escape('Invalid credentials')
        return render_template_string(read_html_file('login.html'), error=error_msg)
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

@app.route('/signal-analysis-lab')
@login_required
def signal_analysis_lab():
    return read_html_file('signal_analysis_lab.html')

@app.route('/chart-extractor')
@login_required
def chart_extractor():
    return read_html_file('chart_data_extractor.html')

@app.route('/recover-signal-lab')
@login_required
def recover_signal_lab():
    return read_html_file('recover_signal_lab_data.html')

@app.route('/migrate-signal-lab')
@login_required
def migrate_signal_lab_page():
    return read_html_file('recover_signal_lab_data.html')

@app.route('/check-localstorage')
@login_required
def check_localstorage():
    return read_html_file('check_localStorage.html')

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
@login_required
def api_integration_js():
    return send_from_directory('.', 'api_integration.js', mimetype='application/javascript')

@app.route('/chatbot.js')
@login_required
def chatbot_js():
    return send_from_directory('.', 'chatbot.js', mimetype='application/javascript')

@app.route('/trading_empire_kb.js')
@login_required
def trading_empire_kb_js():
    return send_from_directory('.', 'trading_empire_kb.js', mimetype='application/javascript')

@app.route('/notification_system.js')
@login_required
def notification_system_js():
    return send_from_directory('.', 'notification_system.js', mimetype='application/javascript')

@app.route('/d3_charts.js')
@login_required
def d3_charts_js():
    return send_from_directory('.', 'd3_charts.js', mimetype='application/javascript')

@app.route('/ai_chat.js')
@login_required
def ai_chat_js():
    return send_from_directory('.', 'ai_chat.js', mimetype='application/javascript')

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
@login_required
def style_switcher_js():
    return send_from_directory('.', 'style_switcher.js', mimetype='application/javascript')

@app.route('/professional_styles.js')
@login_required
def professional_styles_js():
    return send_from_directory('.', 'professional_styles.js', mimetype='application/javascript')

@app.route('/style_preload.css')
@login_required
def style_preload_css():
    return send_from_directory('.', 'style_preload.css', mimetype='text/css')

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
    try:
        if filename.endswith(('.jpg', '.png', '.gif', '.ico', '.pdf')):
            return send_from_directory('.', filename)
        return "File not found", 404
    except (IOError, OSError) as e:
        logger.error(f"File access error: {str(e)}")
        return "File access error", 500

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
        safe_prompt = escape(str(prompt)[:50]).replace(NEWLINE_CHAR, '').replace(CARRIAGE_RETURN_CHAR, '')
        logger.info(f"AI insights request: {safe_prompt}...")
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

# Dynamic AI analysis endpoints
    try:
        if not client:
            return jsonify({"analysis": "AI analysis temporarily unavailable. Please check your API configuration."}), 200
            
        data = request.get_json()
        chart_type = data.get('chart_type', 'equity')
        trades_data = data.get('trades', [])
        metrics = data.get('metrics', {})
        
        # Build concise context
        context = build_concise_context(trades_data, metrics)
        
        # Simplified, positive prompts
        chart_insights = {
            'equity': f"Equity Performance: {context}. Highlight 2-3 key strengths and growth opportunities.",
            'daily': f"Daily Patterns: {context}. Identify best performing patterns and optimization opportunities.",
            'weekly': f"Weekly Trends: {context}. Show momentum strengths and scaling opportunities.",
            'monthly': f"Monthly Analysis: {context}. Highlight seasonal advantages and growth potential.",
            'rscore': f"R-Score Distribution: {context}. Show target optimization and profit maximization opportunities.",
            'dayofweek': f"Day Performance: {context}. Identify optimal trading days and schedule optimization.",
            'seasonality': f"Seasonal Patterns: {context}. Highlight cyclical advantages and timing opportunities.",
            'rolling': f"30-Day Performance: {context}. Show momentum strengths and consistency improvements.",
            'session': f"Session Analysis: {context}. Identify best sessions and allocation optimization."
        }
        
        prompt = chart_insights.get(chart_type, chart_insights['equity'])
        
        response = client.chat.completions.create(
            model=environ.get('OPENAI_MODEL', 'gpt-4o'),
            messages=[
                {"role": "system", "content": get_chart_analysis_prompt()},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.6
        )
        
        return jsonify({
            "analysis": response.choices[0].message.content,
            "chart_type": chart_type,
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Error in ai_chart_analysis: {str(e)}")
        return jsonify({"analysis": "Chart analysis temporarily unavailable. System is optimizing for better performance."}), 200

@app.route('/api/ai-strategy-summary', methods=['POST'])
@login_required
def ai_strategy_summary():
    try:
        if not client:
            return jsonify({
                "summary": "🚀 Your trading system shows strong potential. Focus on consistency and scaling opportunities.",
                "system_health": "Optimizing (70+)",
                "adaptation_score": "Growing (65+)",
                "next_action": "Scale Gradually",
                "recommendation": "Continue building on current strengths while optimizing risk management.",
                "status": "success"
            }), 200
            
        data = request.get_json()
        trades_data = data.get('trades', [])
        metrics = data.get('metrics', {})
        
        context = build_strategic_context(trades_data, metrics)
        
        prompt = f"""Strategic Analysis Request:
        
        {context}
        
        Provide a comprehensive but positive strategic overview:
        
        **Current Strengths:** What's working well in the system
        **Growth Opportunities:** Specific areas for expansion and improvement  
        **Strategic Recommendations:** 3-4 actionable next steps
        **Business Development:** How to scale and optimize operations
        
        Maintain an encouraging, growth-focused tone throughout."""
        
        response = client.chat.completions.create(
            model=environ.get('OPENAI_MODEL', 'gpt-4o'),
            messages=[
                {"role": "system", "content": get_strategy_summary_prompt()},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.5
        )
        
        ai_response = response.choices[0].message.content
        
        return jsonify({
            "summary": ai_response,
            "system_health": extract_positive_health_score(ai_response),
            "adaptation_score": extract_positive_adaptation_score(ai_response),
            "next_action": extract_positive_next_action(ai_response),
            "recommendation": extract_positive_recommendation(ai_response),
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Error in ai_strategy_summary: {str(e)}")
        return jsonify({
            "summary": "🎯 Strategic analysis optimizing. Your trading system demonstrates solid fundamentals with clear growth potential.",
            "system_health": "Strong Foundation (75+)",
            "adaptation_score": "Evolving (70+)",
            "next_action": "Optimize & Scale",
            "recommendation": "Focus on consistency while exploring scaling opportunities.",
            "status": "success"
        }), 200

# News and Market Analysis Endpoints
@app.route('/api/market-news')
@login_required
def get_market_news():
    try:
        news_api = NewsAPI()
        news = news_api.get_market_news(limit=15)
        futures = news_api.get_futures_data()
        
        return jsonify({
            'news': news,
            'futures': futures,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Error fetching market news: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/economic-news', methods=['GET', 'POST'])
@login_required
def economic_news_data():
    if request.method == 'POST':
        # Save economic news data to database
        try:
            if not db_enabled or not db:
                return jsonify({'error': 'Database not available'}), 500
            
            data = request.get_json()
            news_data = data.get('news_data', {})
            
            cursor = db.conn.cursor()
            cursor.execute("""
                INSERT INTO economic_news_cache (news_data, created_at) 
                VALUES (%s, NOW())
                ON CONFLICT (id) DO UPDATE SET 
                news_data = EXCLUDED.news_data, 
                created_at = EXCLUDED.created_at
            """, (dumps(news_data),))
            
            db.conn.commit()
            return jsonify({'status': 'success', 'message': 'Economic news saved'})
            
        except Exception as e:
            if hasattr(db, 'conn') and db.conn:
                db.conn.rollback()
            logger.error(f"Error saving economic news: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    else:
        # Get economic news data from database
        try:
            if not db_enabled or not db:
                # Fallback to API call
                news_api = NewsAPI()
                economic_news = news_api.get_economic_news(limit=10)
                return jsonify({
                    'economic_news': economic_news,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success'
                })
            
            cursor = db.conn.cursor()
            cursor.execute("""
                SELECT news_data FROM economic_news_cache 
                ORDER BY created_at DESC LIMIT 1
            """)
            
            result = cursor.fetchone()
            if result:
                news_data = loads(result['news_data']) if isinstance(result['news_data'], str) else result['news_data']
                return jsonify({
                    'news_data': news_data,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success'
                })
            else:
                # No cached data, try API
                news_api = NewsAPI()
                economic_news = news_api.get_economic_news(limit=10)
                return jsonify({
                    'economic_news': economic_news,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success'
                })
                
        except Exception as e:
            logger.error(f"Error fetching economic news: {str(e)}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/economic-calendar')
@login_required
def get_economic_calendar():
    try:
        import requests
        
        response = requests.get('https://nfs.faireconomy.media/ff_calendar_thisweek.json', timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            events = []
            for event in data:
                if event.get('impact') in ['High', 'RED', 'high']:
                    events.append({
                        'date': event.get('date'),
                        'title': event.get('title', event.get('name', 'Economic Event')),
                        'impact': 'HIGH'
                    })
            
            logger.info(f"Fetched {len(events)} high-impact economic events")
            return jsonify({'events': events, 'status': 'success'})
        else:
            logger.error(f"ForexFactory API returned status {response.status_code}")
            return jsonify({'events': [], 'error': 'API unavailable', 'status': 'error'}), 500
        
    except Exception as e:
        logger.error(f"Error fetching economic calendar: {str(e)}")
        return jsonify({'events': [], 'error': str(e), 'status': 'error'}), 500

@app.route('/api/ai-economic-analysis', methods=['POST'])
@login_required
def ai_economic_analysis():
    try:
        if not client:
            return jsonify({
                'analysis': 'Economic analysis optimizing. Monitoring key economic indicators for NQ trading impact.',
                'impact': 'NEUTRAL',
                'key_events': ['Fed policy monitoring', 'Inflation data tracking', 'Employment trends'],
                'status': 'success'
            }), 200
            
        data = request.get_json()
        economic_news = data.get('economic_news', [])
        futures_data = data.get('futures', {})
        
        # Build economic analysis prompt
        news_summary = '\n'.join([f"- {item.get('title', '')[:150]}" for item in economic_news[:5]])
        
        prompt = f"""Economic Impact Analysis for NQ Futures Trading:
        
        TODAY'S ECONOMIC NEWS:
        {news_summary}
        
        CURRENT NQ PRICE: {futures_data.get('NQ', {}).get('price', 'N/A')}
        
        Provide concise economic analysis:
        1. MARKET IMPACT: How these events affect NQ futures specifically
        2. VOLATILITY OUTLOOK: Expected volatility changes for today/this week
        3. KEY LEVELS: Economic-driven support/resistance levels
        4. TRADING BIAS: Bullish/Bearish/Neutral based on economic data
        5. RISK FACTORS: Main economic risks to monitor
        
        Focus on actionable insights for NQ scalping strategy."""
        
        response = client.chat.completions.create(
            model=environ.get('OPENAI_MODEL', 'gpt-4o'),
            messages=[
                {"role": "system", "content": "You are an expert economic analyst providing real-time market intelligence for futures traders. Focus on actionable insights."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250,
            temperature=0.4
        )
        
        ai_response = response.choices[0].message.content
        
        # Parse response for structured data
        impact = 'NEUTRAL'
        if 'bullish' in ai_response.lower():
            impact = 'BULLISH'
        elif 'bearish' in ai_response.lower():
            impact = 'BEARISH'
        
        # Extract key events
        key_events = []
        for item in economic_news[:3]:
            title = item.get('title', '')[:50]
            if title:
                key_events.append(title + '...')
        
        return jsonify({
            'analysis': ai_response,
            'impact': impact,
            'key_events': key_events,
            'confidence': '78%',
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error in ai_economic_analysis: {str(e)}")
        return jsonify({
            'analysis': 'Economic intelligence processing. Monitoring Fed policy, inflation data, and employment trends for NQ impact.',
            'impact': 'NEUTRAL',
            'key_events': ['Economic data monitoring...'],
            'status': 'success'
        }), 200

@app.route('/api/ai-market-analysis', methods=['POST'])
@login_required
def ai_market_analysis():
    try:
        if not client:
            return jsonify({
                'analysis': '📊 Market analysis optimizing. Monitoring key levels and sentiment for NQ trading opportunities.',
                'bias': 'NEUTRAL',
                'key_levels': {'support': [15200], 'resistance': [15300]},
                'alerts': ['AI analysis connecting...'],
                'status': 'success'
            }), 200
            
        data = request.get_json()
        news_items = data.get('news', [])
        futures_data = data.get('futures', {})
        user_trades = data.get('trades', [])
        
        # Build context about user's trading strategy
        trading_context = build_user_trading_context(user_trades)
        
        # Create market analysis prompt
        news_summary = '\n'.join([f"- {item.get('title', '')[:100]}" for item in news_items[:5]])
        
        prompt = f"""ICT Market Analysis for NQ Liquidity Grab Scalper:
        
        TRADER PROFILE:
        {trading_context}
        
        CURRENT MARKET CONDITIONS:
        NQ Price: {futures_data.get('NQ', {}).get('price', 'N/A')}
        Market Sentiment: {get_market_sentiment()}
        Session Context: Analyze current session for liquidity opportunities
        
        RECENT NEWS IMPACT:
        {news_summary}
        
        Provide ICT-focused analysis:
        1. 1H BIAS: BULLISH/BEARISH based on FVG/IFVG context
        2. LIQUIDITY LEVELS: Session highs/lows and pivot areas for sweeps
        3. FVG OPPORTUNITIES: Potential gap formations for entries
        4. SESSION TIMING: Optimal periods for liquidity grab setups
        5. NEWS IMPACT: How news affects liquidity and volatility for scalping
        
        Focus on 1min execution opportunities within current 1H bias context."""
        
        response = client.chat.completions.create(
            model=environ.get('OPENAI_MODEL', 'gpt-4o'),
            messages=[
                {"role": "system", "content": "You are an expert NQ futures analyst providing real-time market intelligence. Focus on actionable insights for systematic traders."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.4
        )
        
        ai_response = response.choices[0].message.content
        
        # Parse AI response for structured data
        parsed_response = parse_market_analysis(ai_response)
        
        return jsonify({
            'analysis': ai_response,
            'bias': parsed_response.get('bias', 'NEUTRAL'),
            'key_levels': extract_key_levels()['NQ'],
            'alerts': parsed_response.get('alerts', []),
            'confidence': parsed_response.get('confidence', '75%'),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error in ai_market_analysis: {str(e)}")
        return jsonify({
            'analysis': '🎯 Market intelligence processing. Monitoring NQ for optimal entry opportunities based on your trading style.',
            'bias': 'NEUTRAL',
            'key_levels': {'support': [15200, 15150], 'resistance': [15300, 15350]},
            'alerts': ['Market analysis optimizing...'],
            'status': 'success'
        }), 200

@app.route('/api/ai-risk-assessment', methods=['POST'])
@login_required
def ai_risk_assessment():
    try:
        if not client:
            return jsonify({
                "risk_assessment": "🛡️ Risk management systems are optimizing. Current protective measures are maintaining account stability with growth potential.",
                "status": "success"
            }), 200
            
        data = request.get_json()
        trades_data = data.get('trades', [])
        metrics = data.get('metrics', {})
        
        risk_context = build_opportunity_context(trades_data, metrics)
        
        prompt = f"""Opportunity Optimization Analysis:
        
        {risk_context}
        
        Frame this as opportunity optimization rather than risk limitation:
        
        • **Protective Strengths:** Current risk management working well
        • **Growth Enablers:** How current protection supports scaling
        • **Optimization Opportunities:** Specific improvements for better protection
        • **Scaling Safeguards:** Risk management for growth phases
        
        Focus on how smart risk management enables greater opportunities."""
        
        response = client.chat.completions.create(
            model=environ.get('OPENAI_MODEL', 'gpt-4o'),
            messages=[
                {"role": "system", "content": get_risk_assessment_prompt()},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250,
            temperature=0.4
        )
        
        return jsonify({
            "risk_assessment": response.choices[0].message.content,
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Error in ai_risk_assessment: {str(e)}")
        return jsonify({
            "risk_assessment": "🎯 Opportunity optimization in progress. Your protective systems are enabling sustainable growth with measured risk exposure.",
            "status": "success"
        }), 200

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

# AI Signal Analysis endpoints
@app.route('/api/ai-signal-analysis', methods=['POST'])
@login_required
def ai_signal_analysis():
    try:
        if not client:
            return jsonify({"error": "OpenAI client not available"}), 500
            
        data = request.get_json()
        signals = data.get('signals', [])
        
        if len(signals) < 5:
            return jsonify({"error": "Need at least 5 signals for meaningful AI analysis"}), 400
        
        # Build analysis context
        context = build_signal_context(signals)
        
        prompt = f"""Analyze this NQ futures trading signal data comprehensively:
        
        {context}
        
        Provide your complete analysis - look for patterns, correlations, inefficiencies, opportunities, and insights I might not have considered. Don't limit yourself to obvious metrics. What does this data really tell you about the trading approach?"""
        
        response = client.chat.completions.create(
            model=environ.get('OPENAI_MODEL', 'gpt-4o'),
            messages=[
                {"role": "system", "content": "You are a world-class quantitative trading analyst. Analyze this data with fresh eyes - find patterns, correlations, and insights the trader might not see. Be thorough and unrestrained in your analysis."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.4
        )
        
        return jsonify({
            "analysis": response.choices[0].message.content,
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Error in ai_signal_analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/ai-signal-recommendations', methods=['POST'])
@login_required
def ai_signal_recommendations():
    try:
        if not client:
            return jsonify({"error": "OpenAI client not available"}), 500
            
        data = request.get_json()
        signals = data.get('signals', [])
        focus_area = data.get('focus', 'overall')
        
        context = build_focused_context(signals, focus_area)
        
        prompt = f"""Analyze this trading data and provide comprehensive recommendations:
        
        {context}
        
        Focus: {focus_area}
        
        What improvements, optimizations, or completely different approaches would you recommend? Think beyond conventional wisdom - what does the data suggest that might surprise me?"""
        
        response = client.chat.completions.create(
            model=environ.get('OPENAI_MODEL', 'gpt-4o'),
            messages=[
                {"role": "system", "content": "You are an innovative trading strategist. Challenge assumptions, find hidden patterns, and suggest improvements the trader hasn't considered. Be creative and thorough."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.5
        )
        
        # Parse recommendations into list
        recommendations = [line.strip('• -') for line in response.choices[0].message.content.split('\n') if line.strip() and ('•' in line or '-' in line)]
        
        return jsonify({
            "recommendations": recommendations[:5],
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Error in ai_signal_recommendations: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Get trades from database
@app.route('/api/trades')
@login_required
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
            if hasattr(db, 'conn') and db.conn:
                db.conn.rollback()
            error_msg = escape(str(e)[:200]).replace(NEWLINE_CHAR, ' ').replace(CARRIAGE_RETURN_CHAR, ' ')
            logger.error(f"Database query error: {error_msg}")
            return jsonify({"trades": [], "error": "Database query failed"}), 500
        
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
@login_required
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

# Signal Lab API endpoints
@app.route('/api/signal-lab-trades', methods=['GET'])
@login_required
def get_signal_lab_trades():
    try:
        if not db_enabled or not db:
            logger.info("Database not available - returning empty array for local development")
            return jsonify([]), 200
        
        # Clear any aborted transactions
        try:
            db.conn.rollback()
        except:
            pass
            
        cursor = db.conn.cursor()
        
        # Simple query with error handling
        try:
            cursor.execute("""
                SELECT id, date, time, bias, session, signal_type, open_price, entry_price, 
                       stop_loss, take_profit, 
                       COALESCE(mfe_none, mfe, 0) as mfe_none,
                       COALESCE(be1_level, 1) as be1_level,
                       COALESCE(be1_hit, false) as be1_hit,
                       COALESCE(mfe1, 0) as mfe1,
                       COALESCE(be2_level, 2) as be2_level,
                       COALESCE(be2_hit, false) as be2_hit,
                       COALESCE(mfe2, 0) as mfe2,
                       position_size, commission, news_proximity, news_event, screenshot, 
                       analysis_data, created_at
                FROM signal_lab_trades 
                ORDER BY created_at DESC
            """)
        except Exception as e:
            # Fallback to old schema
            cursor.execute("""
                SELECT id, date, time, bias, session, signal_type, open_price, entry_price, 
                       stop_loss, take_profit, 
                       COALESCE(mfe, 0) as mfe_none, 1 as be1_level, false as be1_hit, 0 as mfe1,
                       2 as be2_level, false as be2_hit, 0 as mfe2,
                       position_size, commission, news_proximity, news_event, screenshot, 
                       NULL as analysis_data, created_at
                FROM signal_lab_trades 
                ORDER BY created_at DESC
            """)
        
        rows = cursor.fetchall()
        logger.info(f"Query returned {len(rows)} rows")
        
        if len(rows) == 0:
            # Check if table exists and has data
            cursor.execute("SELECT COUNT(*) FROM signal_lab_trades")
            total_count = cursor.fetchone()[0]
            logger.info(f"Total records in signal_lab_trades table: {total_count}")
        
        trades = []
        for row in rows:
            trade = {
                'id': row['id'],
                'date': str(row['date']) if row['date'] else None,
                'time': str(row['time']) if row['time'] else None,
                'bias': row['bias'],
                'session': row['session'],
                'signal_type': row['signal_type'],
                'open_price': float(row['open_price']) if row['open_price'] else 0,
                'entry_price': float(row['entry_price']) if row['entry_price'] else 0,
                'stop_loss': float(row['stop_loss']) if row['stop_loss'] else 0,
                'take_profit': float(row['take_profit']) if row['take_profit'] else 0,
                'mfe_none': float(row['mfe_none']) if row['mfe_none'] is not None else 0,
                'be1_level': float(row['be1_level']) if row['be1_level'] is not None else 1,
                'be1_hit': bool(row['be1_hit']) if row['be1_hit'] is not None else False,
                'mfe1': float(row['mfe1']) if row['mfe1'] is not None else 0,
                'be2_level': float(row['be2_level']) if row['be2_level'] is not None else 2,
                'be2_hit': bool(row['be2_hit']) if row['be2_hit'] is not None else False,
                'mfe2': float(row['mfe2']) if row['mfe2'] is not None else 0,
                'position_size': int(row['position_size']) if row['position_size'] else 1,
                'commission': float(row['commission']) if row['commission'] else 0,
                'news_proximity': row['news_proximity'],

            }
            trades.append(trade)
            logger.debug(f"Processed trade ID {trade['id']}: {trade['date']} {trade['signal_type']}")
        
        logger.info(f"Returning {len(trades)} trades to client")
        return jsonify(trades)
        
    except Exception as e:
        import traceback
        error_details = f"{str(e)} | Traceback: {traceback.format_exc()}"
        logger.error(f"Error getting signal lab trades: {error_details}")
        # Return empty array instead of error for better UX
        return jsonify([]), 200

@app.route('/api/signal-lab-trades', methods=['POST'])
@login_required
def create_signal_lab_trade():
    try:
        logger.info("POST /api/signal-lab-trades called")
        
        if not db_enabled or not db:
            logger.error("Database not available")
            return jsonify({"error": "Database not available"}), 500
        
        data = request.get_json()
        logger.info(f"Received data: {data}")
        
        if not data:
            logger.error("No JSON data received")
            return jsonify({"error": "No data provided"}), 400
        
        cursor = db.conn.cursor()
        logger.info("Executing INSERT query")
        

        
        cursor.execute("""
            INSERT INTO signal_lab_trades 
            (date, time, bias, session, signal_type, open_price, entry_price, stop_loss, 
             take_profit, mfe_none, be1_level, be1_hit, mfe1, be2_level, be2_hit, mfe2, 
             position_size, commission, news_proximity, news_event, screenshot, analysis_data)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data.get('date'),
            data.get('time'),
            data.get('bias'),
            data.get('session'),
            data.get('signal_type'),
            data.get('open_price', 0),
            data.get('entry_price', 0),
            data.get('stop_loss', 0),
            data.get('take_profit', 0),
            data.get('mfe_none', 0),
            data.get('be1_level', 1),
            data.get('be1_hit', False),
            data.get('mfe1', 0),
            data.get('be2_level', 2),
            data.get('be2_hit', False),
            data.get('mfe2', 0),
            data.get('position_size', 1),
            data.get('commission', 0),
            data.get('news_proximity', 'None'),
            data.get('news_event', 'None'),
            data.get('screenshot'),
            None
        ))
        
        result = cursor.fetchone()
        if result:
            trade_id = result['id']  # Use dict key instead of index
        else:
            raise Exception("INSERT failed - no ID returned")
        db.conn.commit()
        logger.info(f"Successfully created trade with ID: {trade_id}")
        
        return jsonify({"id": trade_id, "status": "success"})
        
    except Exception as e:
        if hasattr(db, 'conn') and db.conn:
            db.conn.rollback()
        error_msg = str(e)
        logger.error(f"Error creating signal lab trade: {error_msg}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": error_msg, "details": traceback.format_exc()}), 500

@app.route('/api/signal-lab-trades/<int:trade_id>', methods=['PUT'])
@login_required
def update_signal_lab_trade(trade_id):
    try:
        if not db_enabled or not db:
            return jsonify({"error": "Database not available"}), 500
        
        data = request.get_json()
        logger.info(f"Updating trade {trade_id} with data: {data}")
        
        # First check if the trade exists
        cursor = db.conn.cursor()
        cursor.execute("SELECT id FROM signal_lab_trades WHERE id = %s", (trade_id,))
        if not cursor.fetchone():
            return jsonify({"error": f"Trade with ID {trade_id} not found"}), 404
        
        # Perform the update
        # Check if screenshot analysis is requested for update
        screenshot_data = data.get('screenshot')
        analysis_result = None
        
        if screenshot_data and screenshot_data.startswith('data:image'):
            try:
                from screenshot_analyzer import analyze_trading_screenshot
                analysis_result = analyze_trading_screenshot(screenshot_data)
                logger.info(f"Screenshot analysis completed for update: {analysis_result.get('status')}")
            except Exception as e:
                logger.warning(f"Screenshot analysis failed for update: {str(e)}")
        
        cursor.execute("""
            UPDATE signal_lab_trades SET
                news_proximity = %s, news_event = %s
            WHERE id = %s
        """, (
            data.get('news_proximity', 'None'),
            data.get('news_event', 'None'),
            trade_id
        ))
        
        rows_affected = cursor.rowcount
        logger.info(f"Update affected {rows_affected} rows")
        
        db.conn.commit()
        logger.info(f"Successfully updated trade {trade_id}")
        
        return jsonify({"status": "success", "rows_affected": rows_affected})
        
    except Exception as e:
        if hasattr(db, 'conn') and db.conn:
            db.conn.rollback()
        import traceback
        error_details = f"{str(e)} | Traceback: {traceback.format_exc()}"
        logger.error(f"Error updating signal lab trade {trade_id}: {error_details}")
        return jsonify({"error": str(e), "details": error_details}), 500

@app.route('/api/signal-lab-trades/<int:trade_id>', methods=['DELETE'])
@login_required
def delete_signal_lab_trade(trade_id):
    try:
        if not db_enabled or not db:
            return jsonify({"error": "Database not available"}), 500
        
        cursor = db.conn.cursor()
        cursor.execute("DELETE FROM signal_lab_trades WHERE id = %s", (trade_id,))
        db.conn.commit()
        
        return jsonify({"status": "success"})
        
    except Exception as e:
        if hasattr(db, 'conn') and db.conn:
            db.conn.rollback()
        logger.error(f"Error deleting signal lab trade: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/signal-lab-migrate', methods=['POST'])
@login_required
def migrate_signal_lab_data():
    """Migrate localStorage data to database"""
    try:
        if not db_enabled or not db:
            return jsonify({"error": "Database not available"}), 500
        
        data = request.get_json()
        trades = data.get('trades', [])
        
        if not trades:
            return jsonify({"error": "No trades provided"}), 400
        
        success_count = 0
        error_count = 0
        errors = []
        
        for trade in trades:
            try:
                cursor = db.conn.cursor()
                cursor.execute("""
                    INSERT INTO signal_lab_trades 
                    (date, time, bias, session, signal_type, open_price, entry_price, stop_loss, 
                     take_profit, be_achieved, breakeven, mfe, position_size, commission, 
                     news_proximity, news_event, screenshot)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    trade.get('date'),
                    trade.get('time'),
                    trade.get('bias'),
                    trade.get('session'),
                    trade.get('signalType'),
                    trade.get('openPrice', 0),
                    trade.get('entryPrice', 0),
                    trade.get('stopLoss', 0),
                    trade.get('takeProfit', 0),
                    trade.get('beAchieved', False),
                    trade.get('breakeven', 0),
                    trade.get('mfe', 0),
                    trade.get('positionSize', 1),
                    trade.get('commission', 0),
                    trade.get('newsProximity', 'None'),
                    trade.get('newsEvent', 'None'),
                    trade.get('screenshot')
                ))
                
                db.conn.commit()
                success_count += 1
                
            except Exception as e:
                if hasattr(db, 'conn') and db.conn:
                    db.conn.rollback()
                error_count += 1
                errors.append(str(e))
                logger.error(f"Error migrating trade: {str(e)}")
        
        return jsonify({
            "status": "completed",
            "success_count": success_count,
            "error_count": error_count,
            "total_trades": len(trades),
            "errors": errors[:5]  # Return first 5 errors only
        })
        
    except Exception as e:
        logger.error(f"Error in migration endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/check-localStorage')
@login_required
def check_localStorage():
    """Endpoint to check if localStorage migration is needed"""
    return jsonify({
        "message": "Check localStorage on client side",
        "database_available": db_enabled,
        "migration_endpoint": "/api/signal-lab-migrate"
    })

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy", 
        "message": "Trading server running",
        "database": "connected" if db_enabled else "offline",
        "csrf_token": csrf.generate_csrf_token()
    })

@app.route('/api/health')
def api_health_check():
    response = jsonify({
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "ai_enabled": client is not None,
        "database": "connected" if db_enabled else "offline"
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/test')
def test_endpoint():
    print("✅ TEST endpoint called")
    response = jsonify({"message": "Extension test working"})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/simple-test')
def simple_test():
    print("✅ SIMPLE TEST endpoint called")
    return "WORKING"

@app.route('/api/ai-analysis')
def ai_analysis_simple():
    print("✅ AI ANALYSIS endpoint called")
    return jsonify({"message": "AI endpoint working"})

@app.route('/api/ai-chart-analysis', methods=['GET', 'POST'])
def ai_chart_analysis_extension():
    print(f"✅ Extension endpoint called with method: {request.method}")
    try:
        # Handle both GET and POST requests
        if request.method == 'POST':
            data = request.get_json() or {}
            symbol = data.get('symbol', 'NQ1!')
            price = float(data.get('price', 0))
            session = data.get('session', 'LONDON')
        else:
            symbol = request.args.get('symbol', 'NQ1!')
            price = float(request.args.get('price', 0))
            session = request.args.get('session', 'LONDON')
        
        # Get current market data for context
        news_api = NewsAPI()
        futures_data = news_api.get_futures_data()
        current_time = datetime.now()
        
        # Session-based FVG quality scoring
        session_multipliers = {
            'ASIA': 0.3,
            'LONDON': 0.9,
            'NEW YORK AM': 0.8,
            'NEW YORK PM': 0.6,
            'NY LUNCH': 0.2,
            'NY PRE MARKET': 0.4
        }
        
        base_fvg_quality = 0.7
        session_multiplier = session_multipliers.get(session, 0.5)
        fvg_quality = min(0.95, base_fvg_quality * session_multiplier)
        
        # Entry confidence based on session and price action
        entry_confidence = 0.75 if session in ['LONDON', 'NEW YORK AM'] else 0.4
        if price > 0:
            entry_confidence = min(0.9, entry_confidence + 0.1)
        
        # Market condition analysis
        hour = current_time.hour
        if 8 <= hour <= 12:  # London session
            market_condition = "HIGH LIQUIDITY"
        elif 13 <= hour <= 16:  # NY AM
            market_condition = "TRENDING"
        else:
            market_condition = "LOW LIQUIDITY"
        
        # Generate recommendation
        if entry_confidence > 0.7 and fvg_quality > 0.6:
            recommendation = "STRONG SETUP"
        elif entry_confidence > 0.5:
            recommendation = "MODERATE SETUP"
        else:
            recommendation = "WAIT"
        
        response = jsonify({
            'symbol': symbol,
            'session': session,
            'fvgQuality': round(fvg_quality, 2),
            'entryConfidence': round(entry_confidence, 2),
            'marketCondition': market_condition,
            'sessionQuality': session_multiplier,
            'recommendation': recommendation,
            'timestamp': current_time.isoformat(),
            'analysis': f"Session: {session} | FVG Quality: {fvg_quality:.0%} | Entry Confidence: {entry_confidence:.0%} | Market: {market_condition}"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
        
    except Exception as e:
        logger.error(f"AI chart analysis error: {str(e)}")
        response = jsonify({
            'error': True,
            'message': str(e),
            'fvgQuality': 0.5,
            'entryConfidence': 0.3,
            'marketCondition': 'ANALYZING',
            'recommendation': 'WAIT'
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 200

# Prop firm endpoints
@app.route('/api/prop-firms')
@login_required
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
@login_required
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

# Level tracking endpoints
@app.route('/api/level-tracking/capture', methods=['POST'])
@login_required
def capture_daily_levels():
    try:
        from level_tracker import LevelTracker
        tracker = LevelTracker()
        
        data = request.get_json() or {}
        ai_analysis = data.get('ai_analysis')
        
        if ai_analysis:
            # Parse AI analysis for levels
            parsed_levels = tracker.parse_ai_levels(ai_analysis)
            levels = tracker.capture_daily_levels(parsed_levels)
            message = "AI-generated levels captured"
        else:
            # Use basic technical levels
            levels = tracker.capture_daily_levels()
            message = "Technical levels captured"
        
        return jsonify({
            "status": "success",
            "levels": levels,
            "message": message
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/level-tracking/accuracy')
@login_required
def get_level_accuracy():
    try:
        from level_tracker import LevelTracker
        tracker = LevelTracker()
        accuracy_data = tracker.get_accuracy_report()
        
        return jsonify({
            "accuracy_data": [{
                "level_type": row[1],
                "total_predictions": row[2],
                "total_hits": row[3],
                "accuracy_percentage": float(row[4]),
                "confidence_score": float(row[5])
            } for row in accuracy_data]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/level-tracking/analyze', methods=['POST'])
@login_required
def analyze_level_performance():
    try:
        if not client:
            return jsonify({"error": "OpenAI client not available"}), 500
            
        from level_tracker import LevelTracker
        tracker = LevelTracker()
        accuracy_data = tracker.get_accuracy_report()
        
        # Build context for GPT-4 analysis
        context = "NQ Level Accuracy Analysis:\n\n"
        for row in accuracy_data:
            level_type, total, hits, accuracy, confidence = row[1], row[2], row[3], float(row[4]), float(row[5])
            context += f"{level_type.upper()}: {hits}/{total} hits ({accuracy:.1f}% accuracy, {confidence:.1f}% confidence)\n"
        
        prompt = f"""{context}
        
Analyze this NQ level tracking data and provide:
        1. Which level types are most reliable for trading
        2. Confidence assessment for each level type
        3. Trading recommendations based on accuracy patterns
        4. Areas for improvement in level prediction
        
        Focus on actionable insights for ICT liquidity grab strategy."""
        
        response = client.chat.completions.create(
            model=environ.get('OPENAI_MODEL', 'gpt-4o'),
            messages=[
                {"role": "system", "content": "You are an expert quantitative analyst specializing in futures level analysis and ICT trading concepts."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.3
        )
        
        return jsonify({
            "analysis": response.choices[0].message.content,
            "accuracy_data": accuracy_data,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Add economic news cache table creation
try:
    if db_enabled and db:
        cursor = db.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS economic_news_cache (
                id SERIAL PRIMARY KEY,
                news_data JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        db.conn.commit()
        logger.info("Economic news cache table ready")
except Exception as e:
    logger.error(f"Error creating economic news cache table: {str(e)}")

# Signal lab table is created in railway_db.py setup_tables()

# Helper functions for AI context building
def build_concise_context(trades_data, metrics):
    """Build concise, positive trading context for AI analysis"""
    if not trades_data:
        return "Building trading history - early stage with growth potential"
    
    win_rate = calculate_win_rate(trades_data)
    recent_trend = determine_positive_trend(trades_data)
    
    context = f"""Performance Snapshot:
    • Trades Executed: {len(trades_data)}
    • Success Rate: {win_rate:.1f}%
    • Recent Momentum: {recent_trend}
    • System Status: {get_system_status(metrics)}
    """
    
    return context

def build_strategic_context(trades_data, metrics):
    """Build strategic context for comprehensive analysis"""
    if not trades_data:
        return "Strategic foundation being established - excellent growth potential ahead"
    
    performance_summary = analyze_performance_strengths(trades_data)
    growth_indicators = identify_growth_opportunities(trades_data, metrics)
    
    context = f"""Strategic Performance Overview:
    
    **Foundation Metrics:**
    • Trading Volume: {len(trades_data)} executions
    • Performance Trend: {performance_summary}
    • System Consistency: {metrics.get('consistency', 'Building')}
    • Growth Indicators: {growth_indicators}
    
    **Operational Strengths:**
    • Execution Quality: {assess_execution_quality(trades_data)}
    • Risk Management: {assess_risk_management(trades_data)}
    • Scaling Readiness: {assess_scaling_readiness(metrics)}
    """
    
    return context

def build_opportunity_context(trades_data, metrics):
    """Build opportunity-focused context for risk analysis"""
    if not trades_data:
        return "Opportunity framework initializing - protective systems ready for growth"
    
    protection_strengths = analyze_protection_strengths(trades_data)
    growth_enablers = identify_growth_enablers(trades_data, metrics)
    
    context = f"""Opportunity Optimization Framework:
    
    **Protective Strengths:**
    • Current Safeguards: {protection_strengths}
    • Account Stability: {assess_account_stability(trades_data)}
    • Recovery Patterns: {analyze_recovery_patterns(trades_data)}
    
    **Growth Enablers:**
    • Scaling Capacity: {growth_enablers}
    • Risk-Reward Balance: {assess_risk_reward_balance(trades_data)}
    • Expansion Readiness: {assess_expansion_readiness(metrics)}
    """
    
    return context

def build_comprehensive_context(trades_data, metrics):
    """Build detailed context for strategy analysis"""
    if not trades_data:
        return "Insufficient trading data for analysis"
    
    # Calculate additional metrics
    win_rate = calculate_win_rate(trades_data)
    avg_win_loss = calculate_avg_win_loss(trades_data)
    session_performance = analyze_session_performance(trades_data)
    
    context = f"""Comprehensive Trading Analysis:
    
    Performance Metrics:
    - Total Trades: {len(trades_data)}
    - Win Rate: {win_rate:.1f}%
    - Average Win/Loss Ratio: {avg_win_loss:.2f}
    - Best Session: {session_performance}
    - Expectancy: {metrics.get('expectancy', 'N/A')}
    - Sharpe Ratio: {metrics.get('sharpeRatio', 'N/A')}
    - Maximum Drawdown: {metrics.get('maxDrawdown', 'N/A')}
    
    Recent Patterns:
    - Last 20 trades trend: {determine_trend(trades_data[-20:])}
    - Consecutive performance: {analyze_streaks(trades_data)}
    - Risk patterns: {identify_risk_patterns(trades_data)}
    """
    
    return context

def build_risk_context(trades_data, metrics):
    """Build risk-focused context for analysis"""
    if not trades_data:
        return "No data for risk analysis"
    
    # Risk-specific calculations
    drawdown_analysis = analyze_drawdowns(trades_data)
    volatility = calculate_volatility_metrics(trades_data)
    risk_metrics = calculate_risk_metrics(trades_data)
    
    context = f"""Risk Assessment Data:
    
    Drawdown Analysis:
    - Maximum Drawdown: {metrics.get('maxDrawdown', 'N/A')}
    - Current Drawdown: {drawdown_analysis.get('current', 0):.2f}R
    - Recovery Time: {drawdown_analysis.get('avg_recovery', 'N/A')} days
    
    Volatility Metrics:
    - Return Volatility: {volatility.get('returns', 0):.3f}
    - Recent vs Historical: {volatility.get('comparison', 'stable')}
    
    Risk Indicators:
    - Consecutive Losses: {risk_metrics.get('max_consecutive_losses', 0)}
    - Risk-Adjusted Return: {metrics.get('sharpeRatio', 'N/A')}
    - Value at Risk (95%): {metrics.get('var95', 'N/A')}
    
    Position Sizing:
    - Current approach: {risk_metrics.get('sizing_analysis', 'standard')}
    - Kelly Criterion: {metrics.get('kellyPercent', 'N/A')}
    """
    
    return context

# Helper analysis functions
def analyze_recent_trades(recent_trades):
    """Analyze recent trading performance"""
    if not recent_trades:
        return "No recent trades"
    
    wins = sum(1 for trade in recent_trades if trade.get('rScore', 0) > 0)
    return f"{wins}/{len(recent_trades)} wins ({wins/len(recent_trades)*100:.0f}%)"

def determine_trend(trades):
    """Determine current performance trend"""
    if len(trades) < 5:
        return "insufficient data"
    
    recent_performance = sum(trade.get('rScore', 0) for trade in trades[-5:])
    return "positive" if recent_performance > 0 else "negative" if recent_performance < 0 else "neutral"

def calculate_win_rate(trades):
    """Calculate win rate from trades"""
    if not trades:
        return 0
    wins = sum(1 for trade in trades if trade.get('rScore', 0) > 0 or trade.get('breakeven', False))
    return (wins / len(trades)) * 100

def calculate_avg_win_loss(trades):
    """Calculate average win/loss ratio"""
    wins = [trade.get('rScore', 0) for trade in trades if trade.get('rScore', 0) > 0]
    losses = [abs(trade.get('rScore', 0)) for trade in trades if trade.get('rScore', 0) < 0]
    
    if not wins or not losses:
        return 0
    
    avg_win = sum(wins) / len(wins)
    avg_loss = sum(losses) / len(losses)
    
    return avg_win / avg_loss if avg_loss > 0 else 0

def analyze_session_performance(trades):
    """Analyze performance by trading session"""
    session_stats = {}
    for trade in trades:
        session = trade.get('session', 'Unknown')
        if session not in session_stats:
            session_stats[session] = {'wins': 0, 'total': 0}
        
        session_stats[session]['total'] += 1
        if trade.get('rScore', 0) > 0 or trade.get('breakeven', False):
            session_stats[session]['wins'] += 1
    
    best_session = max(session_stats.items(), 
                      key=lambda x: x[1]['wins']/x[1]['total'] if x[1]['total'] > 0 else 0,
                      default=('Unknown', {'wins': 0, 'total': 1}))
    
    return f"{best_session[0]} ({best_session[1]['wins']}/{best_session[1]['total']})"

def analyze_streaks(trades):
    """Analyze winning/losing streaks"""
    if len(trades) < 3:
        return "insufficient data"
    
    current_streak = 0
    streak_type = None
    
    for trade in trades[-5:]:
        result = trade.get('rScore', 0)
        if result > 0:
            if streak_type == 'win':
                current_streak += 1
            else:
                current_streak = 1
                streak_type = 'win'
        elif result < 0:
            if streak_type == 'loss':
                current_streak += 1
            else:
                current_streak = 1
                streak_type = 'loss'
        else:
            current_streak = 0
            streak_type = None
    
    return f"{current_streak} {streak_type} streak" if streak_type else "no streak"

def identify_risk_patterns(trades):
    """Identify risk patterns in trading"""
    if len(trades) < 10:
        return "building pattern recognition"
    
    recent_losses = sum(1 for trade in trades[-10:] if trade.get('rScore', 0) < 0)
    
    if recent_losses > 6:
        return "high loss frequency detected"
    elif recent_losses < 3:
        return "low risk period"
    else:
        return "normal risk levels"

def analyze_drawdowns(trades):
    """Analyze drawdown patterns"""
    if not trades:
        return {'current': 0, 'avg_recovery': 0}
    
    # Simplified drawdown analysis
    cumulative = 0
    peak = 0
    current_dd = 0
    
    for trade in trades:
        cumulative += trade.get('rScore', 0)
        if cumulative > peak:
            peak = cumulative
        current_dd = peak - cumulative
    
    return {
        'current': current_dd,
        'avg_recovery': 7  # Simplified
    }

def calculate_volatility_metrics(trades):
    """Calculate volatility metrics"""
    if len(trades) < 5:
        return {'returns': 0, 'comparison': 'insufficient data'}
    
    returns = [trade.get('rScore', 0) for trade in trades]
    mean_return = sum(returns) / len(returns)
    variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
    volatility = variance ** 0.5
    
    return {
        'returns': volatility,
        'comparison': 'stable'  # Simplified
    }

def calculate_risk_metrics(trades):
    """Calculate risk-related metrics"""
    if not trades:
        return {'max_consecutive_losses': 0, 'sizing_analysis': 'no data'}
    
    # Calculate consecutive losses
    max_consecutive = 0
    current_consecutive = 0
    
    for trade in trades:
        if trade.get('rScore', 0) < 0:
            current_consecutive += 1
            max_consecutive = max(max_consecutive, current_consecutive)
        else:
            current_consecutive = 0
    
    return {
        'max_consecutive_losses': max_consecutive,
        'sizing_analysis': 'standard'
    }

# New positive analysis functions
def determine_positive_trend(trades):
    """Determine positive performance trend"""
    if len(trades) < 3:
        return "building momentum"
    
    recent_performance = sum(trade.get('rScore', 0) for trade in trades[-5:])
    if recent_performance > 1:
        return "strong upward momentum"
    elif recent_performance > 0:
        return "positive trajectory"
    else:
        return "consolidating for next move"

def get_system_status(metrics):
    """Get positive system status"""
    win_rate = metrics.get('winRate', '50%')
    if isinstance(win_rate, str):
        win_rate = float(win_rate.replace('%', ''))
    
    if win_rate >= 60:
        return "performing excellently"
    elif win_rate >= 50:
        return "showing solid consistency"
    else:
        return "building foundation"

def analyze_performance_strengths(trades):
    """Analyze performance strengths positively"""
    if not trades:
        return "establishing baseline"
    
    wins = sum(1 for trade in trades if trade.get('rScore', 0) > 0)
    win_rate = (wins / len(trades)) * 100 if trades else 0
    
    if win_rate >= 60:
        return "consistently profitable with strong execution"
    elif win_rate >= 50:
        return "balanced approach with steady progress"
    else:
        return "learning phase with valuable experience gained"

def identify_growth_opportunities(trades, metrics):
    """Identify positive growth opportunities"""
    opportunities = []
    
    if len(trades) > 20:
        opportunities.append("sufficient data for optimization")
    if metrics.get('sharpeRatio', 0) > 1:
        opportunities.append("strong risk-adjusted returns")
    if metrics.get('profitFactor', 1) > 1.2:
        opportunities.append("profitable system ready for scaling")
    
    return ", ".join(opportunities) if opportunities else "multiple optimization pathways available"

def assess_execution_quality(trades):
    """Assess execution quality positively"""
    if not trades:
        return "establishing execution standards"
    
    # Simple assessment based on trade consistency
    if len(trades) > 50:
        return "experienced execution with consistent approach"
    elif len(trades) > 20:
        return "developing strong execution habits"
    else:
        return "building execution foundation"

def assess_risk_management(trades):
    """Assess risk management positively"""
    if not trades:
        return "implementing protective measures"
    
    # Check for extreme losses
    extreme_losses = sum(1 for trade in trades if trade.get('rScore', 0) < -3)
    
    if extreme_losses == 0:
        return "excellent risk control"
    elif extreme_losses < len(trades) * 0.1:
        return "solid protective measures"
    else:
        return "refining risk parameters"

def assess_scaling_readiness(metrics):
    """Assess scaling readiness positively"""
    readiness_factors = []
    
    if metrics.get('consistency', 0) > 0.7:
        readiness_factors.append("consistent performance")
    if metrics.get('sharpeRatio', 0) > 1:
        readiness_factors.append("strong risk-adjusted returns")
    if metrics.get('maxDrawdown', 100) < 20:
        readiness_factors.append("controlled drawdowns")
    
    return ", ".join(readiness_factors) if readiness_factors else "building scaling foundation"

def analyze_protection_strengths(trades):
    """Analyze protection strengths"""
    if not trades:
        return "protective framework initializing"
    
    # Analyze risk control
    avg_loss = sum(abs(trade.get('rScore', 0)) for trade in trades if trade.get('rScore', 0) < 0)
    avg_loss = avg_loss / max(1, sum(1 for trade in trades if trade.get('rScore', 0) < 0))
    
    if avg_loss <= 1:
        return "excellent loss control maintaining account stability"
    elif avg_loss <= 2:
        return "solid risk management with controlled exposure"
    else:
        return "protective measures being optimized"

def assess_account_stability(trades):
    """Assess account stability"""
    if not trades:
        return "stable foundation"
    
    # Simple stability assessment
    recent_trades = trades[-10:] if len(trades) >= 10 else trades
    volatility = len([t for t in recent_trades if abs(t.get('rScore', 0)) > 2])
    
    if volatility <= 2:
        return "highly stable with consistent performance"
    elif volatility <= 4:
        return "stable with managed volatility"
    else:
        return "stabilizing with optimization in progress"

def analyze_recovery_patterns(trades):
    """Analyze recovery patterns positively"""
    if len(trades) < 5:
        return "building recovery data"
    
    # Simple recovery analysis
    recovery_count = 0
    for i in range(1, len(trades)):
        if trades[i-1].get('rScore', 0) < 0 and trades[i].get('rScore', 0) > 0:
            recovery_count += 1
    
    if recovery_count > len(trades) * 0.3:
        return "excellent recovery capability"
    elif recovery_count > len(trades) * 0.2:
        return "solid bounce-back patterns"
    else:
        return "developing resilience patterns"

def identify_growth_enablers(trades, metrics):
    """Identify growth enablers"""
    enablers = []
    
    if len(trades) > 30:
        enablers.append("substantial experience base")
    if metrics.get('expectancy', 0) > 0:
        enablers.append("positive expectancy system")
    if calculate_win_rate(trades) >= 50:
        enablers.append("balanced win rate")
    
    return ", ".join(enablers) if enablers else "multiple growth pathways available"

def assess_risk_reward_balance(trades):
    """Assess risk-reward balance"""
    if not trades:
        return "optimizing balance"
    
    avg_win = sum(trade.get('rScore', 0) for trade in trades if trade.get('rScore', 0) > 0)
    avg_loss = sum(abs(trade.get('rScore', 0)) for trade in trades if trade.get('rScore', 0) < 0)
    
    wins = sum(1 for trade in trades if trade.get('rScore', 0) > 0)
    losses = sum(1 for trade in trades if trade.get('rScore', 0) < 0)
    
    if wins > 0 and losses > 0:
        avg_win = avg_win / wins
        avg_loss = avg_loss / losses
        ratio = avg_win / avg_loss if avg_loss > 0 else 1
        
        if ratio >= 1.5:
            return "excellent risk-reward optimization"
        elif ratio >= 1:
            return "balanced risk-reward approach"
        else:
            return "refining risk-reward parameters"
    
    return "establishing risk-reward baseline"

def assess_expansion_readiness(metrics):
    """Assess expansion readiness"""
    readiness_score = 0
    
    if metrics.get('profitFactor', 1) > 1.2:
        readiness_score += 1
    if metrics.get('sharpeRatio', 0) > 0.5:
        readiness_score += 1
    if metrics.get('maxDrawdown', 100) < 25:
        readiness_score += 1
    
    if readiness_score >= 2:
        return "ready for strategic expansion"
    elif readiness_score >= 1:
        return "approaching expansion readiness"
    else:
        return "building expansion foundation"

# Signal Analysis Helper Functions
def build_signal_context(signals):
    """Build comprehensive signal analysis context"""
    if not signals:
        return "No signal data available"
    
    # Signal type analysis
    signal_performance = {}
    session_performance = {}
    be_analysis = {}
    
    for signal in signals:
        # Signal type performance
        sig_type = signal.get('signalType', 'Unknown')
        if sig_type not in signal_performance:
            signal_performance[sig_type] = []
        signal_performance[sig_type].append(signal.get('mfe', 0))
        
        # Session performance
        session = signal.get('session', 'Unknown')
        if session not in session_performance:
            session_performance[session] = []
        session_performance[session].append(signal.get('mfe', 0))
        
        # Breakeven analysis
        be_level = f"{signal.get('breakeven', 0)}R"
        if be_level not in be_analysis:
            be_analysis[be_level] = []
        be_analysis[be_level].append(signal.get('mfe', 0))
    
    context = f"""SIGNAL ANALYSIS DATA ({len(signals)} signals):
    
    SIGNAL TYPE PERFORMANCE:
    """
    
    for sig_type, mfes in signal_performance.items():
        avg_mfe = sum(mfes) / len(mfes)
        win_rate = len([m for m in mfes if m > 0]) / len(mfes) * 100
        context += f"\n    {sig_type}: {avg_mfe:.2f}R avg, {win_rate:.1f}% win rate ({len(mfes)} signals)"
    
    context += "\n\n    SESSION PERFORMANCE:"
    for session, mfes in session_performance.items():
        avg_mfe = sum(mfes) / len(mfes)
        context += f"\n    {session}: {avg_mfe:.2f}R avg ({len(mfes)} signals)"
    
    context += "\n\n    BREAKEVEN ANALYSIS:"
    for be_level, mfes in be_analysis.items():
        avg_mfe = sum(mfes) / len(mfes)
        context += f"\n    {be_level}: {avg_mfe:.2f}R avg ({len(mfes)} signals)"
    
    return context

def build_focused_context(signals, focus_area):
    """Build focused analysis context for specific area"""
    if not signals:
        return "No signal data for focused analysis"
    
    if focus_area == 'signals':
        # Focus on signal type comparison
        fvg_signals = [s for s in signals if 'FVG' in s.get('signalType', '') and 'IFVG' not in s.get('signalType', '')]
        ifvg_signals = [s for s in signals if 'IFVG' in s.get('signalType', '')]
        
        fvg_avg = sum([s.get('mfe', 0) for s in fvg_signals]) / len(fvg_signals) if fvg_signals else 0
        ifvg_avg = sum([s.get('mfe', 0) for s in ifvg_signals]) / len(ifvg_signals) if ifvg_signals else 0
        
        return f"""SIGNAL TYPE FOCUS:
        FVG Signals: {len(fvg_signals)} trades, {fvg_avg:.2f}R average
        IFVG Signals: {len(ifvg_signals)} trades, {ifvg_avg:.2f}R average
        Performance Gap: {abs(fvg_avg - ifvg_avg):.2f}R difference"""
    
    elif focus_area == 'sessions':
        # Focus on session optimization
        london_signals = [s for s in signals if s.get('session') == 'London']
        ny_am_signals = [s for s in signals if s.get('session') == 'NY AM']
        
        london_avg = sum([s.get('mfe', 0) for s in london_signals]) / len(london_signals) if london_signals else 0
        ny_avg = sum([s.get('mfe', 0) for s in ny_am_signals]) / len(ny_am_signals) if ny_am_signals else 0
        
        return f"""SESSION FOCUS:
        London: {len(london_signals)} signals, {london_avg:.2f}R average
        NY AM: {len(ny_am_signals)} signals, {ny_avg:.2f}R average
        Best performing sessions need optimization focus"""
    
    elif focus_area == 'breakeven':
        # Focus on breakeven strategy
        no_be = [s for s in signals if s.get('breakeven', 0) == 0]
        with_be = [s for s in signals if s.get('breakeven', 0) > 0]
        
        no_be_avg = sum([s.get('mfe', 0) for s in no_be]) / len(no_be) if no_be else 0
        be_avg = sum([s.get('mfe', 0) for s in with_be]) / len(with_be) if with_be else 0
        
        return f"""BREAKEVEN FOCUS:
        No BE: {len(no_be)} signals, {no_be_avg:.2f}R average
        With BE: {len(with_be)} signals, {be_avg:.2f}R average
        BE Impact: {be_avg - no_be_avg:.2f}R difference"""
    
    return "General signal analysis context"

# Market Analysis Helper Functions
def build_user_trading_context(trades):
    """Build context about user's ICT liquidity grab strategy"""
    if not trades:
        return "ICT liquidity grab scalper building systematic edge on NQ futures"
    
    # Analyze trading patterns specific to ICT strategy
    sessions = [t.get('session', 'UNKNOWN') for t in trades]
    best_session = max(set(sessions), key=sessions.count) if sessions else 'LONDON'
    
    win_rate = len([t for t in trades if t.get('rScore', 0) > 0]) / len(trades) * 100 if trades else 50
    avg_r_target = sum([abs(t.get('rScore', 1)) for t in trades]) / len(trades) if trades else 2
    
    # Calculate breakeven frequency (indicator of tight risk management)
    breakevens = len([t for t in trades if t.get('breakeven', False)])
    be_rate = (breakevens / len(trades) * 100) if trades else 0
    
    return f"""ICT Liquidity Grab Scalper Profile:
    - NQ futures specialist using 1H bias + 1min execution
    - {win_rate:.0f}% win rate with {avg_r_target:.1f}R average target
    - {be_rate:.0f}% breakeven rate (tight risk management)
    - Optimal session: {best_session}
    - Strategy: FVG/IFVG entries after pivot sweeps
    - Risk: SL below/above FVG base, 1:1 breakeven, testing R-targets"""

def parse_market_analysis(ai_response):
    """Parse AI response for structured data"""
    response_lower = ai_response.lower()
    
    # Extract bias
    bias = 'NEUTRAL'
    if 'long' in response_lower and 'bias' in response_lower:
        bias = 'LONG'
    elif 'short' in response_lower and 'bias' in response_lower:
        bias = 'SHORT'
    
    # Extract confidence
    confidence = '75%'
    import re
    conf_match = re.search(r'(\d+)%', ai_response)
    if conf_match:
        confidence = conf_match.group(0)
    
    # Extract alerts
    alerts = []
    if 'alert' in response_lower or 'warning' in response_lower:
        alerts.append('Market alert detected in analysis')
    
    return {
        'bias': bias,
        'confidence': confidence,
        'alerts': alerts
    }

# Positive response parsing functions
def extract_positive_health_score(response):
    """Extract positive system health score from AI response"""
    response_lower = response.lower()
    if any(word in response_lower for word in ['excellent', 'outstanding', 'exceptional']):
        return 'Excellent (90+)'
    elif any(word in response_lower for word in ['strong', 'solid', 'good', 'healthy']):
        return 'Strong (80-89)'
    elif any(word in response_lower for word in ['growing', 'building', 'developing']):
        return 'Growing (70-79)'
    else:
        return 'Optimizing (65+)'

def extract_positive_adaptation_score(response):
    """Extract positive adaptation insights from AI response"""
    response_lower = response.lower()
    if any(word in response_lower for word in ['accelerating', 'expanding', 'scaling']):
        return 'Accelerating (85+)'
    elif any(word in response_lower for word in ['improving', 'growing', 'advancing']):
        return 'Advancing (75-84)'
    elif any(word in response_lower for word in ['stable', 'consistent', 'steady']):
        return 'Steady (65-74)'
    else:
        return 'Evolving (60+)'

def extract_positive_next_action(response):
    """Extract positive next action recommendation"""
    response_lower = response.lower()
    actions = {
        'scale': 'Scale Operations',
        'expand': 'Expand Strategy',
        'optimize': 'Optimize Systems',
        'grow': 'Accelerate Growth',
        'build': 'Build Momentum',
        'enhance': 'Enhance Performance',
        'continue': 'Continue Excellence'
    }
    
    for keyword, action in actions.items():
        if keyword in response_lower:
            return action
    
    return 'Maintain Momentum'

def extract_positive_recommendation(response):
    """Extract positive main recommendation from AI response"""
    sentences = response.split('.')
    for sentence in sentences:
        if any(word in sentence.lower() for word in ['opportunity', 'growth', 'optimize', 'enhance', 'build', 'scale']):
            return sentence.strip()
    
    return sentences[0].strip() if sentences else "Continue building on current strengths for sustained growth"

if __name__ == '__main__':
    port = int(environ.get('PORT', 8080))
    debug_mode = environ.get('DEBUG', 'False').lower() == 'true'
    host = '127.0.0.1'  # Localhost only
    logger.info(f"Starting server on {host}:{port}, debug={debug_mode}")
    app.run(host=host, port=port, debug=debug_mode)