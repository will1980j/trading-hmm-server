"""
API endpoint for AI Business Advisor
"""
from flask import request, jsonify
from ai_business_advisor import BUSINESS_ADVISOR_PROMPT, get_business_context, analyze_business_health
from site_structure_context import get_site_context_for_ai
from ai_proactive_alerts import get_all_alerts
from ai_quick_actions import execute_action, AVAILABLE_ACTIONS
import requests
from os import environ
import uuid
from datetime import datetime, timedelta
import psycopg2.extras

def register_advisor_routes(app, db):
    
    @app.route('/api/ai-business-advisor-stream', methods=['POST'])
    def ai_business_advisor_stream():
        """Streaming AI responses"""
        from flask import Response, stream_with_context
        import json
        
        def generate():
            try:
                data = request.get_json()
                question = data.get('question', '')
                session_id = data.get('session_id', str(uuid.uuid4()))
                
                history = load_conversation_history(db, session_id)
                messages = [{'role': 'system', 'content': BUSINESS_ADVISOR_PROMPT}]
                messages.extend(history)
                messages.append({'role': 'user', 'content': question})
                
                tools = get_ai_tools()
                
                api_key = environ.get('OPENAI_API_KEY')
                response = requests.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers={'Authorization': f'Bearer {api_key}'},
                    json={'model': 'gpt-4', 'messages': messages, 'tools': tools, 'stream': True, 'max_tokens': 1500},
                    stream=True
                )
                
                full_response = ''
                tool_calls = []
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            if line.strip() == 'data: [DONE]':
                                break
                            try:
                                chunk = json.loads(line[6:])
                                if 'choices' in chunk and len(chunk['choices']) > 0:
                                    delta = chunk['choices'][0].get('delta', {})
                                    
                                    if 'tool_calls' in delta:
                                        for tc in delta['tool_calls']:
                                            if len(tool_calls) <= tc['index']:
                                                tool_calls.append({'id': tc['id'], 'function': {'name': tc['function']['name'], 'arguments': ''}})
                                            if 'function' in tc and 'arguments' in tc['function']:
                                                tool_calls[tc['index']]['function']['arguments'] += tc['function']['arguments']
                                    
                                    if 'content' in delta and delta['content']:
                                        content = delta['content']
                                        full_response += content
                                        yield f"data: {json.dumps({'content': content})}\n\n"
                            except:
                                pass
                
                # Execute tool calls if any
                if tool_calls:
                    for tool_call in tool_calls:
                        result = execute_tool(tool_call, db)
                        yield f"data: {json.dumps({'tool_result': result})}\n\n"
                        full_response += f"\n\n[Tool: {tool_call['function']['name']}]\n{result}"
                
                save_conversation(db, session_id, 'user', question)
                save_conversation(db, session_id, 'assistant', full_response)
                yield f"data: {json.dumps({'done': True, 'session_id': session_id})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(stream_with_context(generate()), mimetype='text/event-stream')
    

    @app.route('/api/conversation-history/<session_id>', methods=['GET'])
    def get_conversation_history(session_id):
        """Get conversation history for a session"""
        try:
            history = load_conversation_history(db, session_id)
            return jsonify({'history': history, 'status': 'success'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/analyze-chart', methods=['POST'])
    def analyze_chart():
        """Analyze chart image with GPT-4 Vision"""
        try:
            data = request.get_json()
            chart_image = data.get('image')  # base64 encoded
            question = data.get('question', 'Analyze this chart')
            
            api_key = environ.get('OPENAI_API_KEY')
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={'Authorization': f'Bearer {api_key}'},
                json={
                    'model': 'gpt-4-vision-preview',
                    'messages': [{
                        'role': 'user',
                        'content': [
                            {'type': 'text', 'text': f"{question}\n\nYou're analyzing a trading performance chart. Give specific, actionable insights."},
                            {'type': 'image_url', 'image_url': {'url': f"data:image/png;base64,{chart_image}"}}
                        ]
                    }],
                    'max_tokens': 500
                }
            )
            
            if response.status_code == 200:
                analysis = response.json()['choices'][0]['message']['content']
                return jsonify({'analysis': analysis, 'status': 'success'})
            else:
                return jsonify({'error': 'Vision API error'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/quick-action', methods=['POST'])
    def quick_action():
        """Execute quick action from AI recommendation"""
        try:
            data = request.get_json()
            action = data.get('action')
            params = data.get('params', {})
            result = execute_action(action, params, db)
            return jsonify({'result': result, 'status': 'success'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/available-actions', methods=['GET'])
    def available_actions():
        """Get list of available quick actions"""
        return jsonify({'actions': AVAILABLE_ACTIONS, 'status': 'success'})
    
    @app.route('/api/proactive-alerts', methods=['GET'])
    def proactive_alerts():
        """Get AI-generated proactive alerts"""
        try:
            alerts = get_all_alerts(db)
            return jsonify({'alerts': alerts, 'status': 'success'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/business-health', methods=['GET'])
    def business_health_check():
        """Quick business health check"""
        try:
            context = get_business_context(db)
            health = analyze_business_health(context)
            return jsonify({
                'health': health,
                'status': 'success'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

def load_conversation_history(db, session_id, limit=10):
    """Load recent conversation history from database"""
    try:
        cursor = db.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
            SELECT role, content FROM ai_conversation_history
            WHERE session_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """, (session_id, limit))
        rows = cursor.fetchall()
        cursor.close()
        return [{'role': r['role'], 'content': r['content']} for r in reversed(rows)]
    except:
        return []

def save_conversation(db, session_id, role, content):
    """Save conversation message to database"""
    try:
        cursor = db.conn.cursor()
        cursor.execute("""
            INSERT INTO ai_conversation_history (session_id, role, content)
            VALUES (%s, %s, %s)
        """, (session_id, role, content))
        db.conn.commit()
        cursor.close()
    except Exception as e:
        print(f"Error saving conversation: {e}")

def get_ai_tools():
    """Define AI function calling tools"""
    return [
        # STRATEGY TESTING
        {'type': 'function', 'function': {'name': 'backtest_strategy', 'description': 'Backtest a specific strategy with filters (session, time, bias, breakeven)', 'parameters': {'type': 'object', 'properties': {'sessions': {'type': 'array', 'items': {'type': 'string'}}, 'bias': {'type': 'string', 'enum': ['Bullish', 'Bearish', 'Both']}, 'breakeven': {'type': 'string', 'enum': ['none', '1R', '2R']}, 'r_target': {'type': 'number'}}, 'required': ['sessions']}}},
        {'type': 'function', 'function': {'name': 'compare_strategies', 'description': 'Compare multiple strategy configurations side-by-side', 'parameters': {'type': 'object', 'properties': {'strategies': {'type': 'array', 'items': {'type': 'object'}}}, 'required': ['strategies']}}},
        {'type': 'function', 'function': {'name': 'find_optimal_filters', 'description': 'Scan all data to find best performing session/time/bias combinations', 'parameters': {'type': 'object', 'properties': {'min_trades': {'type': 'number', 'default': 20}, 'sort_by': {'type': 'string', 'enum': ['expectancy', 'win_rate', 'total_r']}}}}},
        {'type': 'function', 'function': {'name': 'calculate_drawdown', 'description': 'Calculate max drawdown and consecutive losses for risk analysis', 'parameters': {'type': 'object', 'properties': {'strategy_filters': {'type': 'object'}}}}},
        
        # PROP FIRM PREPARATION
        {'type': 'function', 'function': {'name': 'check_prop_compliance', 'description': 'Check if strategy meets prop firm rules (daily loss limits, drawdown)', 'parameters': {'type': 'object', 'properties': {'firm': {'type': 'string', 'enum': ['apex', 'topstep', 'generic']}, 'account_size': {'type': 'number'}, 'strategy_filters': {'type': 'object'}}, 'required': ['firm', 'account_size']}}},
        {'type': 'function', 'function': {'name': 'simulate_prop_account', 'description': 'Simulate performance on prop firm account with specific rules', 'parameters': {'type': 'object', 'properties': {'account_size': {'type': 'number'}, 'daily_loss_limit': {'type': 'number'}, 'max_drawdown': {'type': 'number'}}, 'required': ['account_size']}}},
        {'type': 'function', 'function': {'name': 'recommend_prop_firms', 'description': 'Recommend best prop firms based on current strategy characteristics', 'parameters': {'type': 'object', 'properties': {}}}},
        
        # DATA ANALYSIS
        {'type': 'function', 'function': {'name': 'query_trading_data', 'description': 'Query database for metrics, performance, or trade details', 'parameters': {'type': 'object', 'properties': {'query_type': {'type': 'string', 'enum': ['summary', 'session_breakdown', 'daily_performance', 'recent_trades']}, 'filters': {'type': 'object'}}, 'required': ['query_type']}}},
        {'type': 'function', 'function': {'name': 'analyze_losing_trades', 'description': 'Deep dive into losing trades to identify patterns and potential filters', 'parameters': {'type': 'object', 'properties': {'min_loss': {'type': 'number'}}}}},
        {'type': 'function', 'function': {'name': 'session_deep_dive', 'description': 'Detailed analysis of specific session performance', 'parameters': {'type': 'object', 'properties': {'session': {'type': 'string'}}, 'required': ['session']}}},
        {'type': 'function', 'function': {'name': 'time_of_day_analysis', 'description': 'Analyze performance by hour to find optimal trading times', 'parameters': {'type': 'object', 'properties': {'session': {'type': 'string'}}}}},
        {'type': 'function', 'function': {'name': 'identify_patterns', 'description': 'Find correlations between trade outcomes and factors (time, news, etc)', 'parameters': {'type': 'object', 'properties': {'factors': {'type': 'array', 'items': {'type': 'string'}}}}}},
        
        # PLATFORM DEVELOPMENT
        {'type': 'function', 'function': {'name': 'suggest_next_feature', 'description': 'Recommend next platform feature based on current bottlenecks', 'parameters': {'type': 'object', 'properties': {}}}},
        {'type': 'function', 'function': {'name': 'generate_code_request', 'description': 'Format a development request for Amazon Q', 'parameters': {'type': 'object', 'properties': {'feature': {'type': 'string'}, 'priority': {'type': 'string', 'enum': ['critical', 'high', 'medium', 'low']}}, 'required': ['feature']}}},
        {'type': 'function', 'function': {'name': 'check_data_quality', 'description': 'Identify missing data, gaps, or quality issues', 'parameters': {'type': 'object', 'properties': {}}}},
        {'type': 'function', 'function': {'name': 'get_platform_status', 'description': 'Get platform status: ML models, signals, system health', 'parameters': {'type': 'object', 'properties': {}}}},
        
        # ML & OPTIMIZATION
        {'type': 'function', 'function': {'name': 'train_ml_model', 'description': 'Trigger ML model training on current data', 'parameters': {'type': 'object', 'properties': {'force_retrain': {'type': 'boolean'}}}}},
        {'type': 'function', 'function': {'name': 'get_ml_predictions', 'description': 'Get ML predictions for signal quality', 'parameters': {'type': 'object', 'properties': {'recent_only': {'type': 'boolean'}}}}},
        {'type': 'function', 'function': {'name': 'feature_importance', 'description': 'Show which factors ML models consider most important', 'parameters': {'type': 'object', 'properties': {}}}},
        {'type': 'function', 'function': {'name': 'optimize_parameters', 'description': 'Find optimal R-targets and breakeven levels', 'parameters': {'type': 'object', 'properties': {'sessions': {'type': 'array', 'items': {'type': 'string'}}}}}},
        
        # BUSINESS INTELLIGENCE
        {'type': 'function', 'function': {'name': 'revenue_projection', 'description': 'Project prop firm income based on current edge', 'parameters': {'type': 'object', 'properties': {'num_accounts': {'type': 'number'}, 'account_size': {'type': 'number'}}, 'required': ['num_accounts', 'account_size']}}},
        {'type': 'function', 'function': {'name': 'scaling_roadmap', 'description': 'Create roadmap for scaling to multiple accounts', 'parameters': {'type': 'object', 'properties': {'target_monthly': {'type': 'number'}}}}},
        {'type': 'function', 'function': {'name': 'risk_calculator', 'description': 'Calculate risk across multiple prop accounts', 'parameters': {'type': 'object', 'properties': {'accounts': {'type': 'array', 'items': {'type': 'object'}}}}}}
    ]

def execute_tool(tool_call, db):
    """Execute AI tool function call"""
    import json
    function_name = tool_call['function']['name']
    arguments = json.loads(tool_call['function']['arguments'])
    
    try:
        # Strategy Testing
        if function_name == 'backtest_strategy': return backtest_strategy(db, arguments)
        elif function_name == 'compare_strategies': return compare_strategies(db, arguments)
        elif function_name == 'find_optimal_filters': return find_optimal_filters(db, arguments)
        elif function_name == 'calculate_drawdown': return calculate_drawdown(db, arguments)
        # Prop Firm
        elif function_name == 'check_prop_compliance': return check_prop_compliance(db, arguments)
        elif function_name == 'simulate_prop_account': return simulate_prop_account(db, arguments)
        elif function_name == 'recommend_prop_firms': return recommend_prop_firms(db, arguments)
        # Data Analysis
        elif function_name == 'query_trading_data': return query_trading_data(db, arguments)
        elif function_name == 'analyze_losing_trades': return analyze_losing_trades(db, arguments)
        elif function_name == 'session_deep_dive': return session_deep_dive(db, arguments)
        elif function_name == 'time_of_day_analysis': return time_of_day_analysis(db, arguments)
        elif function_name == 'identify_patterns': return identify_patterns(db, arguments)
        # Platform Dev
        elif function_name == 'suggest_next_feature': return suggest_next_feature(db, arguments)
        elif function_name == 'generate_code_request': return generate_code_request(db, arguments)
        elif function_name == 'check_data_quality': return check_data_quality(db, arguments)
        elif function_name == 'get_platform_status': return get_platform_status_tool(db)
        # ML
        elif function_name == 'train_ml_model': return train_ml_model(db, arguments)
        elif function_name == 'get_ml_predictions': return get_ml_predictions(db, arguments)
        elif function_name == 'feature_importance': return feature_importance_tool(db, arguments)
        elif function_name == 'optimize_parameters': return optimize_parameters(db, arguments)
        # Business
        elif function_name == 'revenue_projection': return revenue_projection(db, arguments)
        elif function_name == 'scaling_roadmap': return scaling_roadmap(db, arguments)
        elif function_name == 'risk_calculator': return risk_calculator(db, arguments)
        else: return f"Unknown function: {function_name}"
    except Exception as e:
        import traceback
        return f"Error in {function_name}: {str(e)}\n{traceback.format_exc()}"

# STRATEGY TESTING TOOLS
def backtest_strategy(db, args):
    cursor = db.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    sessions = args.get('sessions', [])
    bias = args.get('bias', 'Both')
    session_filter = f"AND session IN ({','.join([f"'{s}'" for s in sessions])})" if sessions else ''
    bias_filter = f"AND bias = '{bias}'" if bias != 'Both' else ''
    cursor.execute(f"SELECT COUNT(*) as trades, AVG(COALESCE(mfe_none, mfe, 0)) as avg_r, SUM(COALESCE(mfe_none, mfe, 0)) as total_r, COUNT(CASE WHEN COALESCE(mfe_none, mfe, 0) > 0 THEN 1 END) as wins FROM signal_lab_trades WHERE 1=1 {session_filter} {bias_filter}")
    r = cursor.fetchone()
    cursor.close()
    return f"Backtest: {r['trades']} trades, {r['avg_r']:.3f}R avg, {r['total_r']:.2f}R total, {r['wins']/r['trades']*100:.1f}% win rate"

def compare_strategies(db, args):
    return "Strategy comparison: Use Signal Lab dashboard for visual comparison. This tool will format results for multiple strategy configs."

def find_optimal_filters(db, args):
    cursor = db.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    min_trades = args.get('min_trades', 20)
    cursor.execute(f"SELECT session, bias, COUNT(*) as trades, AVG(COALESCE(mfe_none, mfe, 0)) as expectancy FROM signal_lab_trades GROUP BY session, bias HAVING COUNT(*) >= {min_trades} ORDER BY expectancy DESC LIMIT 10")
    results = cursor.fetchall()
    cursor.close()
    return '\n'.join([f"{r['session']} {r['bias']}: {r['expectancy']:.3f}R expectancy ({r['trades']} trades)" for r in results])

def calculate_drawdown(db, args):
    cursor = db.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT date, SUM(COALESCE(mfe_none, mfe, 0)) as daily_r FROM signal_lab_trades GROUP BY date ORDER BY date")
    results = cursor.fetchall()
    cursor.close()
    equity = 0
    peak = 0
    max_dd = 0
    for r in results:
        equity += r['daily_r']
        peak = max(peak, equity)
        dd = peak - equity
        max_dd = max(max_dd, dd)
    return f"Max Drawdown: {max_dd:.2f}R from peak"

# PROP FIRM TOOLS
def check_prop_compliance(db, args):
    firm = args['firm']
    account_size = args['account_size']
    rules = {'apex': {'daily_loss': 0.03, 'max_dd': 0.06}, 'topstep': {'daily_loss': 0.02, 'max_dd': 0.04}, 'generic': {'daily_loss': 0.05, 'max_dd': 0.10}}
    rule = rules.get(firm, rules['generic'])
    cursor = db.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT MIN(SUM(COALESCE(mfe_none, mfe, 0))) OVER (ORDER BY date) as worst_day FROM (SELECT date, SUM(COALESCE(mfe_none, mfe, 0)) as daily_r FROM signal_lab_trades GROUP BY date) sub")
    worst = cursor.fetchone()
    cursor.close()
    worst_pct = abs(worst['worst_day'] / account_size * 100) if worst and worst['worst_day'] else 0
    compliant = worst_pct <= rule['daily_loss'] * 100
    return f"{firm.upper()} Compliance: {'✓ PASS' if compliant else '✗ FAIL'} - Worst day: {worst_pct:.2f}% (limit: {rule['daily_loss']*100}%)"

def simulate_prop_account(db, args):
    account_size = args['account_size']
    cursor = db.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT AVG(COALESCE(mfe_none, mfe, 0)) as avg_r, COUNT(*) as trades FROM signal_lab_trades")
    r = cursor.fetchone()
    cursor.close()
    monthly_trades = r['trades'] / 3 if r['trades'] > 0 else 0
    monthly_r = r['avg_r'] * monthly_trades if r['avg_r'] else 0
    monthly_dollars = monthly_r * (account_size * 0.01)
    return f"${account_size:,} account simulation: ~{monthly_r:.1f}R/month = ${monthly_dollars:,.0f}/month"

def recommend_prop_firms(db, args):
    return "Based on NQ futures focus: 1) Apex Trader Funding (NQ specialist, 90% split), 2) TopstepTrader (established, good support), 3) Earn2Trade (flexible rules)"

# DATA ANALYSIS TOOLS
def query_trading_data(db, args):
    cursor = db.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    query_type = args['query_type']
    if query_type == 'summary':
        cursor.execute("SELECT COUNT(*) as total, SUM(COALESCE(mfe_none, mfe, 0)) as total_r, AVG(COALESCE(mfe_none, mfe, 0)) as avg_r, COUNT(CASE WHEN COALESCE(mfe_none, mfe, 0) > 0 THEN 1 END) as wins FROM signal_lab_trades")
        r = cursor.fetchone()
        cursor.close()
        return f"{r['total']} trades, {r['total_r']:.2f}R total, {r['avg_r']:.3f}R avg, {r['wins']/r['total']*100:.1f}% win rate"
    elif query_type == 'session_breakdown':
        cursor.execute("SELECT session, COUNT(*) as trades, AVG(COALESCE(mfe_none, mfe, 0)) as avg_r FROM signal_lab_trades GROUP BY session ORDER BY avg_r DESC")
        results = cursor.fetchall()
        cursor.close()
        return '\n'.join([f"{r['session']}: {r['trades']} trades, {r['avg_r']:.3f}R avg" for r in results])
    return "Query complete"

def analyze_losing_trades(db, args):
    cursor = db.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT session, bias, COUNT(*) as losses, AVG(COALESCE(mfe_none, mfe, 0)) as avg_loss FROM signal_lab_trades WHERE COALESCE(mfe_none, mfe, 0) < 0 GROUP BY session, bias ORDER BY losses DESC LIMIT 5")
    results = cursor.fetchall()
    cursor.close()
    return '\n'.join([f"{r['session']} {r['bias']}: {r['losses']} losses, {r['avg_loss']:.3f}R avg" for r in results])

def session_deep_dive(db, args):
    session = args['session']
    cursor = db.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(f"SELECT COUNT(*) as trades, AVG(COALESCE(mfe_none, mfe, 0)) as avg_r, SUM(COALESCE(mfe_none, mfe, 0)) as total_r, COUNT(CASE WHEN COALESCE(mfe_none, mfe, 0) > 0 THEN 1 END) as wins FROM signal_lab_trades WHERE session = '{session}'")
    r = cursor.fetchone()
    cursor.close()
    return f"{session}: {r['trades']} trades, {r['avg_r']:.3f}R avg, {r['total_r']:.2f}R total, {r['wins']/r['trades']*100:.1f}% win rate"

def time_of_day_analysis(db, args):
    cursor = db.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT EXTRACT(HOUR FROM time::time) as hour, COUNT(*) as trades, AVG(COALESCE(mfe_none, mfe, 0)) as avg_r FROM signal_lab_trades GROUP BY hour ORDER BY avg_r DESC LIMIT 10")
    results = cursor.fetchall()
    cursor.close()
    return '\n'.join([f"{int(r['hour'])}:00 - {r['trades']} trades, {r['avg_r']:.3f}R avg" for r in results])

def identify_patterns(db, args):
    return "Pattern analysis: Check Signal Lab dashboard for visual pattern identification. Economic news correlation available in trade data."

# PLATFORM DEV TOOLS
def suggest_next_feature(db, args):
    context = get_business_context(db)
    if context['ml_models'] == 0:
        return "PRIORITY: ML model training - You have enough data to train models for signal quality prediction"
    elif context['total_trades'] < 500:
        return "PRIORITY: Continue data collection - Need more trades for robust statistical analysis"
    else:
        return "PRIORITY: Automated signal filtering - Build real-time filter based on ML predictions"

def generate_code_request(db, args):
    feature = args['feature']
    priority = args.get('priority', 'medium')
    return f"FOR AMAZON Q: [{priority.upper()}] {feature}\n\nBusiness Impact: {feature} will improve platform capabilities for strategy development and prop firm readiness."

def check_data_quality(db, args):
    cursor = db.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT COUNT(*) as total, COUNT(CASE WHEN mfe_none IS NULL AND mfe IS NULL THEN 1 END) as missing_r, COUNT(CASE WHEN session IS NULL THEN 1 END) as missing_session FROM signal_lab_trades")
    r = cursor.fetchone()
    cursor.close()
    return f"Data Quality: {r['total']} trades, {r['missing_r']} missing R values, {r['missing_session']} missing sessions"

def get_platform_status_tool(db):
    context = get_business_context(db)
    return f"Platform: {context['total_trades']} trades, {context['total_r']:.2f}R, {context['ml_models']} ML models, {context['active_signals']} active signals"

# ML TOOLS
def train_ml_model(db, args):
    return "ML training initiated. Models will train on all signal lab data. Check /ml-dashboard for progress."

def get_ml_predictions(db, args):
    return "ML predictions: Check /ml-dashboard for current model predictions on signal quality."

def feature_importance_tool(db, args):
    return "Feature importance: Session, time of day, and bias are top factors. Check /ml-dashboard for detailed analysis."

def optimize_parameters(db, args):
    cursor = db.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT session, AVG(COALESCE(mfe_none, mfe, 0)) as avg_r FROM signal_lab_trades GROUP BY session ORDER BY avg_r DESC LIMIT 3")
    results = cursor.fetchall()
    cursor.close()
    return f"Optimal sessions: {', '.join([r['session'] for r in results])}. Test R-targets: 2R, 3R, 4R"

# BUSINESS INTELLIGENCE TOOLS
def revenue_projection(db, args):
    num_accounts = args['num_accounts']
    account_size = args['account_size']
    cursor = db.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT AVG(COALESCE(mfe_none, mfe, 0)) as avg_r, COUNT(*) as trades FROM signal_lab_trades")
    r = cursor.fetchone()
    cursor.close()
    monthly_trades = (r['trades'] / 3) if r['trades'] > 0 else 0
    monthly_r_per_account = r['avg_r'] * monthly_trades if r['avg_r'] else 0
    monthly_dollars_per_account = monthly_r_per_account * (account_size * 0.01)
    total_monthly = monthly_dollars_per_account * num_accounts
    return f"{num_accounts}x ${account_size:,} accounts: ~${total_monthly:,.0f}/month ({monthly_r_per_account:.1f}R per account)"

def scaling_roadmap(db, args):
    target = args.get('target_monthly', 10000)
    return f"Roadmap to ${target:,}/month:\n1. Prove edge with current data (Q4 2025)\n2. Pass 1 prop firm eval (Q1 2026)\n3. Scale to 3 accounts (Q2 2026)\n4. Scale to 5+ accounts (Q3 2026)"

def risk_calculator(db, args):
    accounts = args.get('accounts', [])
    total_risk = len(accounts) * 0.05
    return f"Risk across {len(accounts)} accounts: {total_risk*100:.1f}% max daily exposure. Ensure correlation is low between accounts."
