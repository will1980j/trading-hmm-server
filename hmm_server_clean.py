#!/usr/bin/env python3
"""
Clean Trading Dashboard Server
"""

import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import logging
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingHMM:
    def __init__(self):
        self.model = GaussianMixture(n_components=4, covariance_type="full", max_iter=200, random_state=42)
        self.states = ['Ranging', 'Accumulation', 'Markup', 'Distribution']
        self.is_trained = False
        self.observation_history = []
        self.scaler = None
        self.feature_importance = np.zeros(14)
        self.training_score = 0.0
        self.validation_score = 0.0
        
    def prepare_features(self, data):
        try:
            features = np.array([
                data.get('volume_ratio', 1.0),
                data.get('price_momentum', 0.0),
                data.get('time_of_day', 12) / 24.0,
                data.get('day_of_week', 3) / 7.0,
                data.get('trend_strength', 0.0) / 100.0,
                data.get('support_distance', 5.0) / 100.0,
                data.get('resistance_distance', 5.0) / 100.0,
                data.get('pattern_sequence_score', 1.0),
                data.get('market_regime_score', 0.0),
                data.get('volatility_percentile', 50.0) / 100.0,
                data.get('volume_profile', 1.0),
                data.get('price_position', 0.5),
                data.get('momentum_divergence', 0.0),
                data.get('atr_value', 1.0) / data.get('current_price', 1.0) * 1000
            ]).reshape(1, -1)
            return features
        except Exception as e:
            logger.error(f"Feature preparation error: {e}")
            return np.array([[1.0, 0.0, 0.5, 0.4, 0.0, 0.05, 0.05, 1.0, 0.0, 0.5, 1.0, 0.5, 0.0, 0.001]])
    
    def train_model(self, historical_data):
        try:
            if len(historical_data) < 10:
                logger.warning("Not enough data for training")
                return False
                
            features = []
            for data_point in historical_data:
                feat = self.prepare_features(data_point).flatten()
                features.append(feat)
            
            X = np.array(features)
            self.model.fit(X)
            self.is_trained = True
            logger.info(f"HMM trained on {len(historical_data)} observations")
            return True
            
        except Exception as e:
            logger.error(f"Training error: {e}")
            return False
    
    def predict_state(self, current_data):
        try:
            X = self.prepare_features(current_data)
            
            if not self.is_trained:
                pattern_strength = current_data.get('pattern_strength', 0.5)
                volume_ratio = current_data.get('volume_ratio', 1.0)
                
                if volume_ratio > 1.5 and pattern_strength > 0.7:
                    state = 2
                    confidence = 0.75
                elif volume_ratio > 1.2 and pattern_strength > 0.6:
                    state = 1
                    confidence = 0.65
                elif pattern_strength < 0.4:
                    state = 0
                    confidence = 0.6
                else:
                    state = 3
                    confidence = 0.55
                    
                probabilities = [0.25, 0.25, 0.25, 0.25]
                probabilities[state] = confidence
                
            else:
                if self.scaler is not None:
                    X = self.scaler.transform(X)
                
                state_probs = self.model.predict_proba(X)
                predicted_states = self.model.predict(X)
                
                state = int(predicted_states[0])
                confidence = float(np.max(state_probs[0]))
                probabilities = state_probs[0].tolist()
            
            self.observation_history.append(current_data)
            if len(self.observation_history) > 1000:
                self.observation_history = self.observation_history[-500:]
            
            return {
                'state': state,
                'state_name': self.states[state],
                'confidence': round(confidence, 3),
                'probabilities': [round(p, 3) for p in probabilities],
                'is_trained': self.is_trained,
                'observations_count': len(self.observation_history)
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {
                'state': 0,
                'state_name': 'Ranging',
                'confidence': 0.5,
                'probabilities': [0.25, 0.25, 0.25, 0.25],
                'is_trained': False,
                'error': str(e)
            }

# Initialize Flask app and HMM
app = Flask(__name__)
CORS(app)
hmm_engine = TradingHMM()

# Trade Logging System
trade_log = []
signal_log = []
performance_stats = {
    'total_trades': 0,
    'winning_trades': 0,
    'losing_trades': 0,
    'total_pnl': 0.0,
    'best_patterns': {},
    'confidence_accuracy': {},
    'pending_signals': 0
}

@app.route('/', methods=['GET'])
def dashboard():
    """Clean trading dashboard"""
    total_trades = performance_stats['total_trades']
    win_rate = (performance_stats['winning_trades'] / total_trades * 100) if total_trades > 0 else 0
    avg_rr = sum([t.get('actual_rr', 0) for t in trade_log]) / len(trade_log) if trade_log else 0
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Trading System Dashboard</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
            * {{ box-sizing: border-box; }}
            body {{ font-family: 'Inter', sans-serif; margin: 0; background: #0f172a; color: #cbd5e1; min-height: 100vh; }}
            .container {{ max-width: 1400px; margin: 0 auto; padding: 24px; }}
            .header {{ text-align: center; margin-bottom: 32px; border-bottom: 1px solid #334155; padding-bottom: 24px; }}
            .header h1 {{ font-size: 2em; font-weight: 300; color: #f8fafc; margin: 0; }}
            .section {{ background: #1e293b; padding: 24px; margin: 20px 0; border-radius: 8px; border: 1px solid #334155; }}
            .section h2 {{ color: #f1f5f9; margin: 0 0 20px 0; font-size: 1.1em; font-weight: 500; text-transform: uppercase; }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }}
            .stat-box {{ background: #0f172a; padding: 20px; border-radius: 6px; text-align: center; border: 1px solid #334155; }}
            .stat-box h3 {{ color: #94a3b8; margin: 0 0 10px 0; font-size: 0.8em; text-transform: uppercase; }}
            .stat-box p {{ font-size: 1.8em; font-weight: 600; margin: 0; color: #f8fafc; }}
            .success {{ color: #10b981; }}
            .warning {{ color: #f59e0b; }}
            .error {{ color: #ef4444; }}
            button {{ background: #334155; color: #f1f5f9; padding: 12px 20px; border: 1px solid #475569; border-radius: 6px; cursor: pointer; font-weight: 500; font-family: inherit; transition: all 0.2s ease; }}
            button:hover {{ background: #475569; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>TRADING SYSTEM DASHBOARD</h1>
                <p style="color: #64748b; margin: 5px 0;">Performance Analytics & Signal Management</p>
            </div>
            
            <div class="section">
                <h2>System Status</h2>
                <div class="stats">
                    <div class="stat-box">
                        <h3>Model Status</h3>
                        <p class="success">{'TRAINED' if hmm_engine.is_trained else 'LEARNING'}</p>
                    </div>
                    <div class="stat-box">
                        <h3>Total Trades</h3>
                        <p>{total_trades}</p>
                    </div>
                    <div class="stat-box">
                        <h3>Win Rate</h3>
                        <p class="{'success' if win_rate > 60 else 'warning' if win_rate > 40 else 'error'}">{win_rate:.1f}%</p>
                    </div>
                    <div class="stat-box">
                        <h3>Avg R:R</h3>
                        <p class="{'success' if avg_rr > 2 else 'warning' if avg_rr > 1 else 'error'}">{avg_rr:.2f}</p>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>Signal Management</h2>
                <div>No pending signals</div>
                <button onclick="location.reload()">REFRESH DATA</button>
            </div>
        </div>
    </body>
    </html>
    '''
    return html

@app.route('/predict', methods=['POST'])
def predict():
    """Main prediction endpoint"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        result = hmm_engine.predict_state(data)
        logger.info(f"Prediction: {result['state_name']} ({result['confidence']})")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Prediction endpoint error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai-insights', methods=['POST'])
def ai_insights():
    """Enhanced AI insights with business intelligence"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        prompt = data.get('prompt', '')
        context_data = data.get('data', {})
        
        # Analyze the prompt to determine response type
        prompt_lower = prompt.lower()
        
        # Generate intelligent response based on context
        if 'tax' in prompt_lower or 'accounting' in prompt_lower:
            insight = generate_tax_advice(prompt, context_data)
        elif 'prop' in prompt_lower or 'challenge' in prompt_lower:
            insight = generate_prop_firm_advice(prompt, context_data)
        elif 'property' in prompt_lower or 'invest' in prompt_lower:
            insight = generate_investment_advice(prompt, context_data)
        elif 'business' in prompt_lower or 'scale' in prompt_lower:
            insight = generate_business_advice(prompt, context_data)
        elif 'trade' in prompt_lower or 'ict' in prompt_lower:
            insight = generate_trading_advice(prompt, context_data)
        else:
            insight = generate_strategic_advice(prompt, context_data)
        
        return jsonify({
            'status': 'success',
            'insight': insight,
            'context': determine_context_type(prompt)
        })
        
    except Exception as e:
        logger.error(f"AI insights error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

def determine_context_type(prompt):
    """Determine the context type for the response"""
    prompt_lower = prompt.lower()
    if 'tax' in prompt_lower: return 'Australian Tax & Accounting'
    if 'prop' in prompt_lower: return 'Prop Firm Strategy'
    if 'property' in prompt_lower: return 'Property Investment'
    if 'business' in prompt_lower: return 'Business Growth'
    if 'trade' in prompt_lower: return 'Trading Performance'
    return 'Strategic Planning'

def generate_tax_advice(prompt, data):
    """Generate Australian tax optimization advice"""
    trading_data = data.get('tradingData', [])
    total_profit = sum([t.get('profit', 0) for t in trading_data])
    
    advice = f"🇦🇺 **AUSTRALIAN TAX OPTIMIZATION**\n\n"
    
    if total_profit > 100000:
        advice += "📊 **RECOMMENDED STRUCTURE:** Company + Discretionary Trust\n"
        advice += f"• Current trading profit: ${total_profit:,.0f}\n"
        advice += "• Potential tax savings: 15-25% through structure optimization\n"
        advice += "• Company tax rate: 25-30% vs personal rates up to 47%\n\n"
        
        advice += "💡 **IMMEDIATE ACTIONS:**\n"
        advice += "• Set up trading company for business income treatment\n"
        advice += "• Establish discretionary trust for income distribution\n"
        advice += "• Maximize super contributions ($27,500 concessional)\n"
        advice += "• Track all deductible expenses (software, data, equipment)\n\n"
    else:
        advice += "📊 **CURRENT STRUCTURE:** Optimize as sole trader initially\n"
        advice += f"• Trading profit: ${total_profit:,.0f}\n"
        advice += "• Focus on expense deductions and super contributions\n\n"
    
    advice += "📋 **DEDUCTIBLE EXPENSES:**\n"
    advice += "• Trading software & data feeds\n"
    advice += "• Home office expenses (percentage basis)\n"
    advice += "• Computer equipment & hardware\n"
    advice += "• Professional development & education\n"
    advice += "• Accounting & legal fees\n\n"
    
    advice += "⚖️ **COMPLIANCE:** Maintain detailed records, quarterly BAS if GST registered"
    
    return advice

def generate_prop_firm_advice(prompt, data):
    """Generate prop firm strategy advice"""
    prop_firms = data.get('propFirms', [])
    funded_count = len([f for f in prop_firms if f.get('status') == 'funded'])
    challenge_count = len([f for f in prop_firms if f.get('status') == 'challenge'])
    
    advice = f"🏆 **PROP FIRM MASTERY STRATEGY**\n\n"
    advice += f"📊 **CURRENT STATUS:**\n"
    advice += f"• Funded accounts: {funded_count}\n"
    advice += f"• Active challenges: {challenge_count}\n\n"
    
    if funded_count < 3:
        advice += "🎯 **PRIORITY:** Scale to 3+ funded accounts\n\n"
        advice += "💡 **CHALLENGE OPTIMIZATION:**\n"
        advice += "• Risk only 0.5-1% per trade in Phase 1\n"
        advice += "• Focus on consistency over large profits\n"
        advice += "• Trade only during London/NY overlap\n"
        advice += "• Avoid high-impact news events\n\n"
        
        advice += "🏅 **RECOMMENDED FIRMS:**\n"
        advice += "• FTMO: Most established, reliable payouts\n"
        advice += "• FundedNext: Largest account sizes available\n"
        advice += "• MyForexFunds: Fast payouts, good support\n\n"
    else:
        advice += "🚀 **SCALING PHASE:** Optimize funded account management\n\n"
        advice += "💰 **PROFIT OPTIMIZATION:**\n"
        advice += "• Scale position sizes gradually\n"
        advice += "• Compound profits intelligently\n"
        advice += "• Consider larger account challenges\n\n"
    
    advice += "📈 **ICT CONCEPTS FOR PROP FIRMS:**\n"
    advice += "• Focus on institutional order flow\n"
    advice += "• Trade fair value gaps and order blocks\n"
    advice += "• Use market structure for entries\n"
    advice += "• Maintain strict risk management\n\n"
    
    advice += "⚡ **NEXT STEPS:** Pass 2 more challenges this month, optimize tax structure for profits"
    
    return advice

def generate_investment_advice(prompt, data):
    """Generate property and investment advice"""
    trading_data = data.get('tradingData', [])
    total_profit = sum([t.get('profit', 0) for t in trading_data])
    
    advice = f"🏠 **PROPERTY & INVESTMENT STRATEGY**\n\n"
    advice += f"💰 **AVAILABLE CAPITAL:** ${total_profit:,.0f} from trading\n\n"
    
    if total_profit > 50000:
        advice += "🎯 **READY FOR PROPERTY INVESTMENT**\n\n"
        advice += "🇦🇺 **AUSTRALIAN MARKETS:**\n"
        advice += "• Brisbane: 4-6% yield, growth potential, infrastructure development\n"
        advice += "• Melbourne: 3-5% yield, cultural hub, steady growth\n"
        advice += "• Sydney: 2-4% yield, premium locations, capital growth focus\n\n"
        
        advice += "💡 **FINANCING STRATEGY:**\n"
        advice += "• Use trading profits as deposit (20% minimum)\n"
        advice += "• Interest-only loans for investment properties\n"
        advice += "• Offset accounts for tax efficiency\n"
        advice += "• Consider company/trust structure for ownership\n\n"
        
        advice += "🌍 **GLOBAL OPPORTUNITIES:**\n"
        advice += "• USA: Strong rental yields, established markets\n"
        advice += "• Singapore: Asian gateway, stable government\n"
        advice += "• Dubai: Tax-free jurisdiction, tourism growth\n\n"
    else:
        advice += "📈 **BUILD CAPITAL FIRST**\n"
        advice += "• Target $50K+ for property deposit\n"
        advice += "• Continue scaling prop firm operations\n"
        advice += "• Consider REITs for immediate exposure\n\n"
    
    advice += "🎯 **DIVERSIFICATION STRATEGY:**\n"
    advice += "• 40% Property, 40% Stocks, 20% Alternatives\n"
    advice += "• Geographic spread: Australia, US, Asia\n"
    advice += "• Currency hedging for international investments\n\n"
    
    advice += "⚡ **NEXT STEPS:** Secure pre-approval, research growth corridors, optimize tax structure"
    
    return advice

def generate_business_advice(prompt, data):
    """Generate business growth and scaling advice"""
    trading_data = data.get('tradingData', [])
    prop_firms = data.get('propFirms', [])
    
    advice = f"🚀 **BUSINESS SCALING STRATEGY**\n\n"
    
    advice += "💼 **REVENUE DIVERSIFICATION:**\n"
    advice += "• Trading: Multiple prop firm accounts\n"
    advice += "• Education: ICT courses & mentoring\n"
    advice += "• Technology: Custom trading tools\n"
    advice += "• Consulting: Help others pass challenges\n\n"
    
    advice += "⚙️ **OPERATIONAL EFFICIENCY:**\n"
    advice += "• Automate trade management & risk controls\n"
    advice += "• Integrate accounting & reporting systems\n"
    advice += "• Streamline customer onboarding\n"
    advice += "• Document all processes & strategies\n\n"
    
    advice += "👥 **TEAM BUILDING:**\n"
    advice += "• Hire specialist accountant for tax optimization\n"
    advice += "• Consider virtual assistant for admin tasks\n"
    advice += "• Partner with complementary service providers\n\n"
    
    advice += "📊 **PERFORMANCE METRICS:**\n"
    advice += "• Track revenue per stream\n"
    advice += "• Monitor customer acquisition costs\n"
    advice += "• Measure operational efficiency gains\n\n"
    
    advice += "⚡ **IMMEDIATE FOCUS:** Scale prop firm operations, optimize tax structure, develop education products"
    
    return advice

def generate_trading_advice(prompt, data):
    """Generate trading performance advice"""
    trading_data = data.get('tradingData', [])
    if not trading_data:
        return "📊 **TRADING ANALYSIS:** No recent trading data available. Start logging trades for personalized insights."
    
    wins = len([t for t in trading_data if t.get('outcome') == 'win'])
    total = len(trading_data)
    win_rate = (wins / total * 100) if total > 0 else 0
    avg_profit = sum([t.get('profit', 0) for t in trading_data]) / total if total > 0 else 0
    
    advice = f"📊 **TRADING PERFORMANCE ANALYSIS**\n\n"
    advice += f"📈 **CURRENT METRICS:**\n"
    advice += f"• Win Rate: {win_rate:.1f}% ({wins}/{total} trades)\n"
    advice += f"• Average P&L: ${avg_profit:.2f}\n"
    advice += f"• Total Trades: {total}\n\n"
    
    if win_rate > 60:
        advice += "🏆 **EXCELLENT PERFORMANCE:** You're trading at institutional level\n\n"
        advice += "🎯 **OPTIMIZATION FOCUS:**\n"
        advice += "• Scale position sizes gradually\n"
        advice += "• Add more prop firm accounts\n"
        advice += "• Document your edge for consistency\n\n"
    elif win_rate > 45:
        advice += "✅ **SOLID PERFORMANCE:** Good foundation to build on\n\n"
        advice += "🎯 **IMPROVEMENT AREAS:**\n"
        advice += "• Refine entry criteria for higher probability\n"
        advice += "• Focus on risk-reward optimization\n"
        advice += "• Analyze losing trades for patterns\n\n"
    else:
        advice += "⚠️ **NEEDS IMPROVEMENT:** Focus on consistency first\n\n"
        advice += "🎯 **PRIORITY ACTIONS:**\n"
        advice += "• Reduce position sizes until consistent\n"
        advice += "• Back to basics: market structure & ICT concepts\n"
        advice += "• Paper trade new strategies before live\n\n"
    
    advice += "💡 **ICT CONCEPTS TO MASTER:**\n"
    advice += "• Fair Value Gaps for precise entries\n"
    advice += "• Order Blocks for institutional levels\n"
    advice += "• Market Structure for trend direction\n"
    advice += "• Liquidity concepts for stop placement\n\n"
    
    advice += "⚡ **NEXT STEPS:** Focus on consistency, document your edge, scale gradually"
    
    return advice

def generate_strategic_advice(prompt, data):
    """Generate strategic planning advice"""
    advice = f"🎯 **STRATEGIC EMPIRE PLANNING**\n\n"
    
    advice += "📋 **SHORT-TERM (3 months):**\n"
    advice += "• Pass 3+ prop firm challenges\n"
    advice += "• Optimize tax structure (company + trust)\n"
    advice += "• Build 6-month emergency fund\n"
    advice += "• Document all trading processes\n\n"
    
    advice += "🚀 **MEDIUM-TERM (12 months):**\n"
    advice += "• Diversify revenue streams (education, tools)\n"
    advice += "• Acquire first investment property\n"
    advice += "• Build automated trading systems\n"
    advice += "• Hire specialist team members\n\n"
    
    advice += "🏆 **LONG-TERM (3+ years):**\n"
    advice += "• Build $10M+ net worth\n"
    advice += "• Create passive income streams\n"
    advice += "• Establish generational wealth structures\n"
    advice += "• Consider business exit strategies\n\n"
    
    advice += "⚖️ **RISK MANAGEMENT:**\n"
    advice += "• Never risk >2% per trade\n"
    advice += "• Diversify across multiple income sources\n"
    advice += "• Maintain adequate insurance coverage\n"
    advice += "• Hedge against major market downturns\n\n"
    
    advice += "⚡ **IMMEDIATE PRIORITY:** Scale prop firm operations while optimizing tax efficiency"
    
    return advice

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'HMM Server Running',
        'is_trained': hmm_engine.is_trained,
        'observations': len(hmm_engine.observation_history)
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Starting Trading Dashboard Server...")
    app.run(host='0.0.0.0', port=port, debug=False)