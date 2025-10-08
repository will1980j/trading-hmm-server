"""
API endpoint for AI Business Advisor
"""
from flask import request, jsonify
from ai_business_advisor import BUSINESS_ADVISOR_PROMPT, get_business_context, analyze_business_health
import requests
from os import environ

def register_advisor_routes(app, db):
    
    @app.route('/api/ai-business-advisor', methods=['POST'])
    def ai_business_advisor():
        """Strategic business advice endpoint"""
        try:
            data = request.get_json()
            question = data.get('question', 'Analyze my business and provide growth strategy')
            
            # Gather business intelligence
            context = get_business_context(db)
            health = analyze_business_health(context)
            
            # Build comprehensive context
            business_intel = f"""
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
            
            # Use GPT-4 (or GPT-5 when available)
            model = environ.get('AI_ADVISOR_MODEL', 'gpt-4')  # Set AI_ADVISOR_MODEL=gpt-5 in .env when released
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
                json={
                    'model': model,
                    'messages': [
                        {'role': 'system', 'content': BUSINESS_ADVISOR_PROMPT},
                        {'role': 'user', 'content': business_intel}
                    ],
                    'max_tokens': 800,
                    'temperature': 0.7
                },
                timeout=30
            )
            
            ai_response = response.json()['choices'][0]['message']['content']
            
            return jsonify({
                'advice': ai_response,
                'business_health': health,
                'context': context,
                'status': 'success'
            })
            
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
