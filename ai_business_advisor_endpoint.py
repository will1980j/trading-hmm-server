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
                
                context = get_business_context(db)
                health = analyze_business_health(context)
                
                business_intel = f"""QUESTION: {question}

PLATFORM STATUS:
- Total Trades: {context['total_trades']:,}
- Total R: {context['total_r']:.2f}R  
- Win Rate: {context['win_rate']:.1f}%
- Active Signals: {context['active_signals']}
- Platform Health: {context['platform_health']}/100

RECENT PERFORMANCE:
{chr(10).join([f"- {d['date']}: {d['daily_r']:.2f}R ({d['trades']} trades)" for d in context['daily_performance'][:5]]) if context['daily_performance'] else 'No recent data'}
"""
                
                history = load_conversation_history(db, session_id)
                messages = [{'role': 'system', 'content': BUSINESS_ADVISOR_PROMPT}]
                messages.extend(history)
                messages.append({'role': 'user', 'content': business_intel})
                
                api_key = environ.get('OPENAI_API_KEY')
                response = requests.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers={'Authorization': f'Bearer {api_key}'},
                    json={'model': 'gpt-4', 'messages': messages, 'stream': True, 'max_tokens': 1000},
                    stream=True
                )
                
                full_response = ''
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
                                    if 'content' in delta:
                                        content = delta['content']
                                        full_response += content
                                        yield f"data: {json.dumps({'content': content})}\n\n"
                            except:
                                pass
                
                save_conversation(db, session_id, 'user', business_intel)
                save_conversation(db, session_id, 'assistant', full_response)
                yield f"data: {json.dumps({'done': True, 'session_id': session_id})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(stream_with_context(generate()), mimetype='text/event-stream')
    
    @app.route('/api/ai-business-advisor', methods=['POST'])
    def ai_business_advisor():
        """Strategic business advice endpoint with conversation memory"""
        try:
            data = request.get_json()
            question = data.get('question', 'Analyze my business and provide growth strategy')
            session_id = data.get('session_id', str(uuid.uuid4()))
            
            # Gather business intelligence
            context = get_business_context(db)
            health = analyze_business_health(context)
            site_structure = get_site_context_for_ai()
            
            # Build comprehensive business intelligence
            sessions_text = '\n'.join([f"- {s['session']}: {s['trades']} trades, {s['wins']} wins ({s['wins']/s['trades']*100:.1f}%), avg {s['avg_r']:.2f}R, last: {s['last_trade']}" for s in context['session_performance']]) if context['session_performance'] else 'No session data'
            
            daily_text = '\n'.join([f"- {d['date']}: {d['daily_r']:.2f}R ({d['trades']} trades, {d['wins']} wins)" for d in context['daily_performance'][:10]]) if context['daily_performance'] else 'No recent data'
            
            symbols_text = '\n'.join([f"- {s['symbol']}: {s['trades']} trades, {s['wins']/s['trades']*100:.1f}% win rate, {s['avg_r']:.2f}R avg" for s in context['symbol_performance'][:5]]) if context['symbol_performance'] else 'No symbol data'
            
            # Get infrastructure status
            import os
            db_url = os.environ.get('DATABASE_URL', 'Not configured')
            railway_env = 'Railway' if 'railway' in db_url.lower() else 'Local/Other'
            
            business_intel = f"""
QUESTION: {question}

RAW DATA OVERVIEW (Unfiltered):
- Total Signals Captured: {context['total_trades']:,}
- Raw R Total: {context['total_r']:.2f}R
- Raw Win Rate: {context['win_rate']:.1f}% (before optimization)
- Active Live Signals: {context['active_signals']}
- Platform Tools Available: Signal Lab, ML Models, Performance Analytics

REMEMBER: This is raw, unfiltered data. The real work is using the platform tools to identify the best setups and filter out the noise.

SESSION BREAKDOWN (Raw):
{sessions_text}

DAILY ACTIVITY (Raw):
{daily_text}

PLATFORM TOOLS FOR OPTIMIZATION:
{site_structure}

Note: Focus on helping analyze and filter this data rather than judging current raw performance.
"""
            
            # Call OpenAI for strategic advice
            api_key = environ.get('OPENAI_API_KEY')
            if not api_key:
                return jsonify({'error': 'OpenAI API key not configured'}), 500
            
            # Load conversation history from database
            history = load_conversation_history(db, session_id)
            
            # Build messages with history
            messages = [{'role': 'system', 'content': BUSINESS_ADVISOR_PROMPT}]
            messages.extend(history)
            messages.append({'role': 'user', 'content': business_intel})
            
            # Use GPT-4 (or GPT-5 when available)
            model = environ.get('AI_ADVISOR_MODEL', 'gpt-4')
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
                json={
                    'model': model,
                    'messages': messages,
                    'max_tokens': 800,
                    'temperature': 0.7
                },
                timeout=30
            )
            
            if response.status_code != 200:
                return jsonify({'error': f'OpenAI API error: {response.status_code}', 'details': response.text}), 500
            
            response_data = response.json()
            ai_response = response_data['choices'][0]['message']['content']
            
            # Save conversation to database
            save_conversation(db, session_id, 'user', business_intel)
            save_conversation(db, session_id, 'assistant', ai_response)
            
            return jsonify({
                'advice': ai_response,
                'business_health': health,
                'context': context,
                'session_id': session_id,
                'status': 'success'
            })
            
        except Exception as e:
            import traceback
            import logging
            logging.error(f"AI Business Advisor error: {str(e)}")
            logging.error(traceback.format_exc())
            return jsonify({
                'error': str(e),
                'details': traceback.format_exc()
            }), 500
    
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
