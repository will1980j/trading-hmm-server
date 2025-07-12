#!/usr/bin/env python3
"""
Ultimate ICT Trading System
Combines state-tracker + ssv6 + Patek methodology
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Optional
import logging
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json

logger = logging.getLogger(__name__)

# Global app variable for gunicorn
app = None

class UltimateICTSystem:
    def __init__(self):
        self.ny_tz = pytz.timezone('America/New_York')
        
        # Multi-timeframe states
        self.market_states = {
            'M': {'state': 'BULL_ERL_TO_IRL', 'trend': 'Counter', 'confidence': 0.7},
            'W': {'state': 'BULL_ERL_TO_IRL', 'trend': 'Counter', 'confidence': 0.7},
            'D': {'state': 'BULL_ERL_TO_IRL', 'trend': 'Counter', 'confidence': 0.7},
            '4H': {'state': 'BULL_ERL_TO_IRL', 'trend': 'Counter', 'confidence': 0.7},
            '1H': {'state': 'BULL_ERL_TO_IRL', 'trend': 'Counter', 'confidence': 0.7},
            '15M': {'state': 'BULL_ERL_TO_IRL', 'trend': 'Counter', 'confidence': 0.7},
            '5M': {'state': 'BULL_ERL_TO_IRL', 'trend': 'Counter', 'confidence': 0.7},
            '1M': {'state': 'BULL_ERL_TO_IRL', 'trend': 'Counter', 'confidence': 0.7}
        }
        
        # Structure zones and opportunities
        self.active_zones = []
        self.opportunities = []
        self.current_price = 0.0
        self.symbol = 'NQ1!'
        
        # Flask app
        self.app = Flask(__name__)
        CORS(self.app)
        self._setup_routes()
        
        # Make app accessible at module level for gunicorn
        global app
        app = self.app
    
    def receive_state_data(self, data: Dict):
        """Receive multi-timeframe state data"""
        try:
            for tf in ['M', 'W', 'D', '4H', '1H', '15M', '5M', '1M']:
                if f'state_{tf}' in data:
                    state_str = data[f'state_{tf}']
                    trend = 'Pro' if 'IRL_TO_ERL' in state_str else 'Counter'
                    
                    self.market_states[tf] = {
                        'state': state_str,
                        'trend': trend,
                        'confidence': 0.8 if 'STRONG' in state_str else 0.6
                    }
            
            self._analyze_opportunities()
            return True
            
        except Exception as e:
            logger.error(f"State data error: {e}")
            return False
    
    def receive_structure_data(self, data: Dict):
        """Receive structure data from ssv6"""
        try:
            self.active_zones = []
            
            # Process zones
            for zone_type in ['fvgs', 'order_blocks', 'liquidity_levels']:
                if zone_type in data:
                    for zone_data in data[zone_type]:
                        zone = {
                            'type': zone_type.rstrip('s').upper(),
                            'direction': zone_data.get('direction', 'BULL'),
                            'top': float(zone_data.get('top', 0)),
                            'bottom': float(zone_data.get('bottom', 0)),
                            'active': zone_data.get('active', True),
                            'strength': float(zone_data.get('strength', 0.5))
                        }
                        self.active_zones.append(zone)
            
            if 'current_price' in data:
                self.current_price = float(data['current_price'])
            
            self._analyze_opportunities()
            return True
            
        except Exception as e:
            logger.error(f"Structure data error: {e}")
            return False
    
    def _analyze_opportunities(self):
        """Analyze trading opportunities"""
        self.opportunities = []
        
        # Get timeframe alignments
        alignments = self._get_alignments()
        
        # Analyze each zone
        for zone in self.active_zones:
            if not zone['active']:
                continue
            
            confluence = self._calculate_confluence(zone, alignments)
            
            if confluence['score'] >= 0.5:
                opportunity = {
                    'signal_type': 'LONG' if zone['direction'] == 'BULL' else 'SHORT',
                    'strength': confluence['strength'],
                    'confluence_score': confluence['score'],
                    'probability': min(0.5 + confluence['score'] * 0.4, 0.95),
                    'risk_reward': 2.5,
                    'entry_zone': zone,
                    'reasoning': confluence['reasoning']
                }
                self.opportunities.append(opportunity)
        
        # Sort by confluence
        self.opportunities.sort(key=lambda x: x['confluence_score'], reverse=True)
    
    def _get_alignments(self):
        """Get timeframe alignments"""
        alignments = {'strong_bullish': [], 'strong_bearish': [], 'weak_bullish': [], 'weak_bearish': []}
        
        pairs = [('M', 'W'), ('W', 'D'), ('D', '4H'), ('4H', '1H'), ('1H', '15M'), ('15M', '5M'), ('5M', '1M')]
        
        for higher, lower in pairs:
            h_state = self.market_states[higher]['state']
            l_state = self.market_states[lower]['state']
            
            if h_state == 'BULL_IRL_TO_ERL' and l_state == 'BULL_IRL_TO_ERL':
                alignments['strong_bullish'].append(f"{higher}-{lower}")
            elif h_state == 'BEAR_IRL_TO_ERL' and l_state == 'BEAR_IRL_TO_ERL':
                alignments['strong_bearish'].append(f"{higher}-{lower}")
            elif 'BULL' in h_state and 'BULL' in l_state:
                alignments['weak_bullish'].append(f"{higher}-{lower}")
            elif 'BEAR' in h_state and 'BEAR' in l_state:
                alignments['weak_bearish'].append(f"{higher}-{lower}")
        
        return alignments
    
    def _calculate_confluence(self, zone, alignments):
        """Calculate confluence score"""
        score = zone['strength'] * 0.4
        reasoning = [f"{zone['type']} strength: {zone['strength']:.2f}"]
        
        if zone['direction'] == 'BULL':
            strong = len(alignments['strong_bullish'])
            weak = len(alignments['weak_bullish'])
            
            if strong >= 2:
                score += 0.4
                strength = 'STRONG'
                reasoning.append(f"Strong bullish alignment ({strong} pairs)")
            elif strong >= 1 or weak >= 2:
                score += 0.2
                strength = 'WEAK'
                reasoning.append(f"Moderate bullish alignment")
            else:
                strength = 'COUNTER'
        else:
            strong = len(alignments['strong_bearish'])
            weak = len(alignments['weak_bearish'])
            
            if strong >= 2:
                score += 0.4
                strength = 'STRONG'
                reasoning.append(f"Strong bearish alignment ({strong} pairs)")
            elif strong >= 1 or weak >= 2:
                score += 0.2
                strength = 'WEAK'
                reasoning.append(f"Moderate bearish alignment")
            else:
                strength = 'COUNTER'
        
        return {
            'score': min(score, 1.0),
            'strength': strength,
            'reasoning': ' | '.join(reasoning)
        }
    
    def get_analysis(self):
        """Get complete analysis"""
        return {
            'timestamp': datetime.now(self.ny_tz).isoformat(),
            'symbol': self.symbol,
            'current_price': self.current_price,
            'market_states': self.market_states,
            'opportunities': self.opportunities[:5],
            'summary': {
                'total_opportunities': len(self.opportunities),
                'strong_signals': len([o for o in self.opportunities if o['strength'] == 'STRONG']),
                'active_zones': len([z for z in self.active_zones if z['active']]),
                'bullish_bias': len([s for s in self.market_states.values() if 'BULL' in s['state']]),
                'bearish_bias': len([s for s in self.market_states.values() if 'BEAR' in s['state']])
            }
        }
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def dashboard():
            analysis = self.get_analysis()
            
            html = '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Ultimate ICT Trading System</title>
                <style>
                    body { font-family: 'Segoe UI', sans-serif; background: #0a0e1a; color: #e2e8f0; margin: 0; padding: 20px; }
                    .container { max-width: 1600px; margin: 0 auto; }
                    .header { text-align: center; margin-bottom: 30px; border-bottom: 2px solid #1e293b; padding-bottom: 20px; }
                    .header h1 { color: #f1f5f9; font-size: 2.5em; margin: 0; }
                    .grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin: 20px 0; }
                    .section { background: #1e293b; padding: 20px; border-radius: 8px; border: 1px solid #334155; }
                    .section h2 { color: #f8fafc; margin: 0 0 15px 0; font-size: 1.3em; border-bottom: 1px solid #475569; padding-bottom: 10px; }
                    .opportunity { background: #0f172a; padding: 15px; margin: 10px 0; border-radius: 6px; border-left: 4px solid #10b981; }
                    .strong { border-left-color: #10b981; }
                    .weak { border-left-color: #f59e0b; }
                    .counter { border-left-color: #ef4444; }
                    .state-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
                    .state-box { background: #0f172a; padding: 10px; text-align: center; border-radius: 4px; }
                    .bull { border-left: 3px solid #10b981; }
                    .bear { border-left: 3px solid #ef4444; }
                    .price { color: #10b981; font-weight: bold; font-size: 1.5em; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎯 ULTIMATE ICT TRADING SYSTEM</h1>
                        <p>Multi-Timeframe State Analysis + Structure Zones + ICT Levels</p>
                        <p><strong>{{ analysis.symbol }}</strong> - <span class="price">${{ "%.2f"|format(analysis.current_price) }}</span></p>
                    </div>
                    
                    <div class="grid">
                        <div class="section">
                            <h2>🚀 TOP OPPORTUNITIES</h2>
                            {% for opp in analysis.opportunities %}
                            <div class="opportunity {{ opp.strength.lower() }}">
                                <strong>{{ opp.signal_type }} - {{ opp.strength }}</strong><br>
                                <small>Confluence: {{ "%.0f"|format(opp.confluence_score * 100) }}% | 
                                Probability: {{ "%.0f"|format(opp.probability * 100) }}% | 
                                R:R {{ "%.1f"|format(opp.risk_reward) }}:1</small><br>
                                <small>{{ opp.entry_zone.type }} @ {{ "%.2f"|format(opp.entry_zone.top) }}-{{ "%.2f"|format(opp.entry_zone.bottom) }}</small><br>
                                <small>{{ opp.reasoning }}</small>
                            </div>
                            {% endfor %}
                        </div>
                        
                        <div class="section">
                            <h2>📊 MARKET STATES</h2>
                            <div class="state-grid">
                                {% for tf, state in analysis.market_states.items() %}
                                <div class="state-box {{ 'bull' if 'BULL' in state.state else 'bear' }}">
                                    <strong>{{ tf }}</strong><br>
                                    <small>{{ state.trend }}</small><br>
                                    <small>{{ "%.0f"|format(state.confidence * 100) }}%</small>
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                        
                        <div class="section">
                            <h2>📈 SYSTEM SUMMARY</h2>
                            <p><strong>Total Opportunities:</strong> {{ analysis.summary.total_opportunities }}</p>
                            <p><strong>Strong Signals:</strong> {{ analysis.summary.strong_signals }}</p>
                            <p><strong>Active Zones:</strong> {{ analysis.summary.active_zones }}</p>
                            <p><strong>Bullish Timeframes:</strong> {{ analysis.summary.bullish_bias }}/8</p>
                            <p><strong>Bearish Timeframes:</strong> {{ analysis.summary.bearish_bias }}/8</p>
                            
                            <h3>🔗 Data Feeds</h3>
                            <p><strong>State Tracker:</strong> POST /receive_states</p>
                            <p><strong>Structure Data:</strong> POST /receive_structure</p>
                            <p><strong>Test System:</strong> GET /test</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            '''
            
            from jinja2 import Template
            template = Template(html)
            return template.render(analysis=analysis)
        
	@self.app.route('/receive_states', methods=['POST'])
	def receive_states():
    	    try:
        	data = request.get_json(force=True)
        	logger.info(f"[STATE] Received: {data}")
        	return jsonify({"status": "success"})
    	    except Exception as e:
        	logger.error(f"[STATE] Error: {e}", exc_info=True)
        	return jsonify({"status": "error", "message": str(e)}), 500

        
        @self.app.route('/receive_structure', methods=['POST'])
        def receive_structure():
            try:
                data = request.json or {}
                success = self.receive_structure_data(data)
                return jsonify({'status': 'success' if success else 'error'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/test', methods=['GET'])
        def test_system():
            # Add test data
            test_states = {
                'state_W': 'BULL_IRL_TO_ERL',
                'state_D': 'BULL_IRL_TO_ERL',
                'state_4H': 'BULL_ERL_TO_IRL'
            }
            self.receive_state_data(test_states)
            
            test_structure = {
                'current_price': 15250.50,
                'fvgs': [
                    {'direction': 'BULL', 'top': 15260, 'bottom': 15240, 'active': True, 'strength': 0.8}
                ]
            }
            self.receive_structure_data(test_structure)
            
            return jsonify({'status': 'test_data_loaded', 'opportunities': len(self.opportunities)})
        
        @self.app.route('/api/analysis')
        def api_analysis():
            return jsonify(self.get_analysis())

# Initialize system at module level for gunicorn
import os
logging.basicConfig(level=logging.INFO)
system = UltimateICTSystem()
app = system.app  # Make app available for gunicorn

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting Ultimate ICT System on port {port}")
    print(f"🎯 Dashboard: http://localhost:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=False)

import traceback

