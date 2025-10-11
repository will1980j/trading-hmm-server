"""
API endpoint for AI Business Advisor
"""
from flask import request, jsonify
from ai_business_advisor import BUSINESS_ADVISOR_PROMPT, get_business_context, analyze_business_health
from site_structure_context import get_site_context_for_ai
import requests
from os import environ
import uuid
from datetime import datetime, timedelta

def register_advisor_routes(app, db):
    
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
            
            # Build comprehensive context
            business_intel = f"""
{site_structure}

CURRENT BUSINESS STATE:
- Overall Health Score: {health['overall_score']}/100
- Trading Volume: {context['total_trades_30d']} trades (30 days)
- ML Integration: {health['ml_integration_score']}% coverage
- Consistency: {health['consistency_score']}/100

SESSION PERFORMANCE:
{chr(10).join([f"- {s['session']}: {s['session_trades']} trades, {s['win_rate']*100:.1f}% win rate" for s in context['session_performance']])}

RECENT TREND (7 days):
{chr(10).join([f"- {r['date']}: {r['daily_r']:.2f}R" for r in context['recent_trend']])}

TRADER'S QUESTION: {question}
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
                    'max_tokens': 1000,
                    'temperature': 0.9
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
        cursor = db.cursor(dictionary=True)
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
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO ai_conversation_history (session_id, role, content)
            VALUES (%s, %s, %s)
        """, (session_id, role, content))
        db.commit()
        cursor.close()
    except Exception as e:
        print(f"Error saving conversation: {e}")
