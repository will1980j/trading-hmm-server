#!/usr/bin/env python3
"""
Ultimate ICT Trading System
Combines state-tracker + ssv6 + Patek methodology
"""

import pandas as pd
import numpy as np
from datetime import datetime
import pytz
from typing import Dict
import logging
import json
import os

from flask import Flask, request, jsonify
from flask_cors import CORS
from jinja2 import Template

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Exposed for Gunicorn
app = None

class UltimateICTSystem:
    def __init__(self):
        self.ny_tz = pytz.timezone('America/New_York')

        # Initialize multi-timeframe states
        self.market_states = {
            tf: {'state': 'BULL_ERL_TO_IRL', 'trend': 'Counter', 'confidence': 0.7}
            for tf in ['M', 'W', 'D', '4H', '1H', '15M', '5M', '1M']
        }

        # Structure zones & opportunities
        self.active_zones = []
        self.opportunities = []
        self.current_price = 0.0
        self.symbol = 'NQ1!'

        # Flask setup
        self.app = Flask(__name__)
        CORS(self.app)
        self._setup_routes()

        # Make available to Gunicorn
        global app
        app = self.app

    def receive_state_data(self, data: Dict):
        try:
            for tf in self.market_states:
                key = f'state_{tf}'
                if key in data:
                    state_str = data[key]
                    trend = 'Pro' if 'IRL_TO_ERL' in state_str else 'Counter'
                    confidence = 0.8 if 'STRONG' in state_str else 0.6
                    self.market_states[tf] = {
                        'state': state_str, 'trend': trend, 'confidence': confidence
                    }
            self._analyze_opportunities()
            return True
        except Exception as e:
            logger.error(f"State data error: {e}", exc_info=True)
            return False

    def receive_structure_data(self, data: Dict):
        try:
            self.active_zones = []
            for zone_type in ['fvgs', 'order_blocks', 'liquidity_levels']:
                if zone_type in data:
                    for z in data[zone_type]:
                        zone = {
                            'type': zone_type.rstrip('s').upper(),
                            'direction': z.get('direction', 'BULL'),
                            'top': float(z.get('top', 0)),
                            'bottom': float(z.get('bottom', 0)),
                            'active': z.get('active', True),
                            'strength': float(z.get('strength', 0.5))
                        }
                        self.active_zones.append(zone)
            if 'current_price' in data:
                self.current_price = float(data['current_price'])
            self._analyze_opportunities()
            return True
        except Exception as e:
            logger.error(f"Structure data error: {e}", exc_info=True)
            return False

    def _analyze_opportunities(self):
        self.opportunities = []
        aligns = self._get_alignments()
        for zone in self.active_zones:
            if not zone['active']:
                continue
            conf = self._calculate_confluence(zone, aligns)
            if conf['score'] >= 0.5:
                opp = {
                    'signal_type': 'LONG' if zone['direction']=='BULL' else 'SHORT',
                    'strength': conf['strength'],
                    'confluence_score': conf['score'],
                    'probability': min(0.5 + conf['score']*0.4, 0.95),
                    'risk_reward': 2.5,
                    'entry_zone': zone,
                    'reasoning': conf['reasoning']
                }
                self.opportunities.append(opp)
        self.opportunities.sort(key=lambda x: x['confluence_score'], reverse=True)

    def _get_alignments(self):
        aligns = {'strong_bullish':[], 'strong_bearish':[], 'weak_bullish':[], 'weak_bearish':[]}
        pairs = [('M','W'),('W','D'),('D','4H'),('4H','1H'),('1H','15M'),('15M','5M'),('5M','1M')]
        for h, l in pairs:
            hs = self.market_states[h]['state']
            ls = self.market_states[l]['state']
            if hs=='BULL_IRL_TO_ERL' and ls=='BULL_IRL_TO_ERL':
                aligns['strong_bullish'].append(f"{h}-{l}")
            elif hs=='BEAR_IRL_TO_ERL' and ls=='BEAR_IRL_TO_ERL':
                aligns['strong_bearish'].append(f"{h}-{l}")
            elif 'BULL' in hs and 'BULL' in ls:
                aligns['weak_bullish'].append(f"{h}-{l}")
            elif 'BEAR' in hs and 'BEAR' in ls:
                aligns['weak_bearish'].append(f"{h}-{l}")
        return aligns

    def _calculate_confluence(self, zone, aligns):
        score = zone['strength'] * 0.4
        reasoning = [f"{zone['type']} strength: {zone['strength']:.2f}"]
        if zone['direction']=='BULL':
            s = len(aligns['strong_bullish']); w = len(aligns['weak_bullish'])
            if s>=2:
                score+=0.4; strength='STRONG'; reasoning.append(f"Strong bullish alignment ({s} pairs)")
            elif s>=1 or w>=2:
                score+=0.2; strength='WEAK'; reasoning.append("Moderate bullish alignment")
            else:
                strength='COUNTER'
        else:
            s = len(aligns['strong_bearish']); w = len(aligns['weak_bearish'])
            if s>=2:
                score+=0.4; strength='STRONG'; reasoning.append(f"Strong bearish alignment ({s} pairs)")
            elif s>=1 or w>=2:
                score+=0.2; strength='WEAK'; reasoning.append("Moderate bearish alignment")
            else:
                strength='COUNTER'
        return {'score':min(score,1.0),'strength':strength,'reasoning':' | '.join(reasoning)}

    def get_analysis(self):
        return {
            'timestamp': datetime.now(self.ny_tz).isoformat(),
            'symbol': self.symbol,
            'current_price': self.current_price,
            'market_states': self.market_states,
            'opportunities': self.opportunities[:5],
            'summary':{
                'total_opportunities':len(self.opportunities),
                'strong_signals':len([o for o in self.opportunities if o['strength']=='STRONG']),
                'active_zones':len([z for z in self.active_zones if z['active']]),
                'bullish_bias':len([s for s in self.market_states.values() if 'BULL' in s['state']]),
                'bearish_bias':len([s for s in self.market_states.values() if 'BEAR' in s['state']])
            }
        }

    def _setup_routes(self):
        html_template = """
        <!DOCTYPE html>
        <html><head><title>Ultimate ICT Trading System</title>
        <style>
        body{font-family:'Segoe UI',sans-serif;background:#0a0e1a;color:#e2e8f0;margin:0;padding:20px;}
        .container{max-width:1600px;margin:0 auto;}
        .header{text-align:center;margin-bottom:30px;border-bottom:2px solid #1e293b;padding-bottom:20px;}
        .header h1{color:#f1f5f9;font-size:2.5em;margin:0;}
        .grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;margin:20px 0;}
        .section{background:#1e293b;padding:20px;border-radius:8px;border:1px solid #334155;}
        .section h2{color:#f8fafc;margin:0 0 15px;font-size:1.3em;border-bottom:1px solid #475569;padding-bottom:10px;}
        .opportunity{background:#0f172a;padding:15px;margin:10px 0;border-radius:6px;border-left:4px solid #10b981;}
        .strong{border-left-color:#10b981;}.weak{border-left-color:#f59e0b;}.counter{border-left-color:#ef4444;}
        .state-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;}
        .state-box{background:#0f172a;padding:10px;text-align:center;border-radius:4px;}
        .bull{border-left:3px solid #10b981;}.bear{border-left:3px solid #ef4444;}
        .price{color:#10b981;font-weight:bold;font-size:1.5em;}
        </style>
        </head><body>
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
                  <small>Confluence: {{ "%.0f"|format(opp.confluence_score*100) }}% |
                  Probability: {{ "%.0f"|format(opp.probability*100) }}% |
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
                    <small>{{ "%.0f"|format(state.confidence*100) }}%</small>
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
        </body></html>
        """

        @self.app.route('/')
        def dashboard():
            analysis = self.get_analysis()
            return Template(html_template).render(analysis=analysis)

        @self.app.route('/receive_states', methods=['POST'])
        def receive_states():
            raw = request.data.decode('utf-8', errors='replace').strip()
            logger.info(f"[STATE] Raw body: {raw}")

            if raw.upper().startswith("STRUCTURE:"):
                payload = raw.split(":",1)[1].strip()
                try:
                    data = json.loads(payload)
                    logger.info(f"[STRUCTURE] Parsed JSON: {data}")
                    ok = self.receive_structure_data(data)
                    return jsonify({'status':'structure_ok' if ok else 'structure_error'}),200
                except Exception as e:
                    logger.error(f"[STRUCTURE] JSON error: {e}", exc_info=True)
                    return jsonify({'status':'error','message':f"STRUCTURE parse failed: {e}"}),400

            elif raw.upper().startswith("STATES:"):
                payload = raw.split(":",1)[1].strip()
                try:
                    data = json.loads(payload)
                    logger.info(f"[STATES] Parsed JSON: {data}")
                    ok = self.receive_state_data(data)
                    return jsonify({'status':'states_ok' if ok else 'states_error'}),200
                except Exception as e:
                    logger.error(f"[STATES] JSON error: {e}", exc_info=True)
                    return jsonify({'status':'error','message':f"STATES parse failed: {e}"}),400

            else:
                try:
                    data = json.loads(raw)
                    logger.info(f"[FALLBACK] Parsed JSON: {data}")
                    ok = self.receive_state_data(data)
                    return jsonify({'status': 'fallback_ok' if ok else 'fallback_error'}), 200
                except Exception as e:
                    logger.error(f"[FALLBACK] JSON error: {e}", exc_info=True)
                    return jsonify({'status': 'error', 'message': f"Fallback parse failed: {e}"}), 400

        @self.app.route('/receive_structure', methods=['POST'])
        def receive_structure():
            try:
                data = request.get_json(force=True) or {}
                logger.info(f"[STRUCTURE] Raw JSON body: {data}")
                ok = self.receive_structure_data(data)
                return jsonify({'status': 'structure_ok' if ok else 'structure_error'}), 200
            except Exception as e:
                logger.error(f"[STRUCTURE] Error: {e}", exc_info=True)
                return jsonify({'status': 'error', 'message': str(e)}), 500

        @self.app.route('/test', methods=['GET'])
        def test_system():
            # load some test data
            self.receive_state_data({
                'state_W': 'BULL_IRL_TO_ERL',
                'state_D': 'BULL_IRL_TO_ERL',
                'state_4H': 'BULL_ERL_TO_IRL'
            })
            self.receive_structure_data({
                'current_price': 15250.50,
                'fvgs': [
                    {'direction': 'BULL', 'top': 15260, 'bottom': 15240, 'active': True, 'strength': 0.8}
                ]
            })
            return jsonify({
                'status': 'test_data_loaded',
                'opportunities': len(self.opportunities)
            }), 200

        @self.app.route('/api/analysis')
        def api_analysis():
            return jsonify(self.get_analysis()), 200

# Instantiate and expose for Gunicorn
system = UltimateICTSystem()
app = system.app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting Ultimate ICT System on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)