#!/usr/bin/env python3
"""
Ultimate ICT Trading System with real–time WebSocket updates
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict

import pytz
from flask import Flask, request, jsonify
from flask_cors import CORS
from jinja2 import Template
from flask_socketio import SocketIO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UltimateICTSystem:
    def __init__(self):
        self.ny_tz = pytz.timezone('America/New_York')

        # Initialize multi-timeframe states
        self.market_states = {
            tf: {'state': 'BULL_ERL_TO_IRL', 'trend': 'Counter', 'confidence': 0.7}
            for tf in ['M','W','D','4H','1H','15M','5M','1M']
        }

        # Structure zones & opportunities
        self.active_zones = []
        self.opportunities = []
        self.current_price = 0.0
        self.symbol = 'NQ1!'

        # Flask & SocketIO setup
        self.app = Flask(__name__)
        CORS(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self._setup_routes()

    def receive_state_data(self, data: Dict):
        try:
            # alias "state_1" → "state_1M"
            if 'state_1' in data and 'state_1M' not in data:
                data['state_1M'] = data.pop('state_1')

            for tf in self.market_states:
                key = f'state_{tf}'
                if key in data:
                    s = data[key]
                    trend = 'Pro' if 'IRL_TO_ERL' in s else 'Counter'
                    conf  = 0.8 if 'STRONG' in s else 0.6
                    self.market_states[tf] = {
                        'state':      s,
                        'trend':      trend,
                        'confidence': conf
                    }
            self._analyze_opportunities()

            # push update to all clients
            self.socketio.emit('update', self.get_analysis())
            return True
        except Exception as e:
            logger.error("State data error", exc_info=True)
            return False

    def receive_structure_data(self, data: Dict):
        try:
            # update symbol dynamically
            if 'symbol' in data:
                self.symbol = data['symbol']

            self.active_zones = []
            for zt in ['fvgs','order_blocks','liquidity_levels']:
                for z in data.get(zt, []):
                    zone = {
                        'type':      zt.rstrip('s').upper(),
                        'direction': z.get('direction','BULL'),
                        'top':       float(z.get('top',0)),
                        'bottom':    float(z.get('bottom',0)),
                        'active':    z.get('active',True),
                        'strength':  float(z.get('strength',0.5))
                    }
                    self.active_zones.append(zone)

            if 'current_price' in data:
                self.current_price = float(data['current_price'])

            self._analyze_opportunities()

            # push update to all clients
            self.socketio.emit('update', self.get_analysis())
            return True
        except Exception as e:
            logger.error("Structure data error", exc_info=True)
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
                    'signal_type'     : 'LONG' if zone['direction']=='BULL' else 'SHORT',
                    'strength'        : conf['strength'],
                    'confluence_score': conf['score'],
                    'probability'     : min(0.5 + conf['score']*0.4, 0.95),
                    'risk_reward'     : 2.5,
                    'entry_zone'      : zone,
                    'reasoning'       : conf['reasoning']
                }
                self.opportunities.append(opp)
        self.opportunities.sort(key=lambda x: x['confluence_score'], reverse=True)

    def _get_alignments(self):
        aligns = {
            'strong_bullish': [], 'strong_bearish': [],
            'weak_bullish'  : [], 'weak_bearish'  : []
        }
        pairs = [('M','W'),('W','D'),('D','4H'),('4H','1H'),
                 ('1H','15M'),('15M','5M'),('5M','1M')]
        for h,l in pairs:
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
        score     = zone['strength'] * 0.4
        reasoning = [f"{zone['type']} strength: {zone['strength']:.2f}"]

        if zone['direction']=='BULL':
            s,w = len(aligns['strong_bullish']), len(aligns['weak_bullish'])
            if s>=2:
                score+=0.4; strength='STRONG'; reasoning.append(f"Strong bullish alignment ({s} pairs)")
            elif s>=1 or w>=2:
                score+=0.2; strength='WEAK';   reasoning.append("Moderate bullish alignment")
            else:
                strength='COUNTER'
        else:
            s,w = len(aligns['strong_bearish']), len(aligns['weak_bearish'])
            if s>=2:
                score+=0.4; strength='STRONG'; reasoning.append(f"Strong bearish alignment ({s} pairs)")
            elif s>=1 or w>=2:
                score+=0.2; strength='WEAK';   reasoning.append("Moderate bearish alignment")
            else:
                strength='COUNTER'

        return {
            'score'    : min(score,1.0),
            'strength' : strength,
            'reasoning': ' | '.join(reasoning)
        }

    def get_analysis(self):
        return {
            'timestamp'     : datetime.now(self.ny_tz).isoformat(),
            'symbol'        : self.symbol,
            'current_price' : self.current_price,
            'market_states' : self.market_states,
            'opportunities' : self.opportunities[:5],
            'summary'       : {
                'total_opportunities': len(self.opportunities),
                'strong_signals'     : len([o for o in self.opportunities if o['strength']=='STRONG']),
                'active_zones'       : len([z for z in self.active_zones if z['active']]),
                'bullish_bias'       : len([s for s in self.market_states.values() if 'BULL' in s['state']]),
                'bearish_bias'       : len([s for s in self.market_states.values() if 'BEAR' in s['state']])
            }
        }

    def _setup_routes(self):
        html_template = """
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
    .opportunity { background: #0f172a; padding: 15px; margin: 10px 0; border-left: 4px solid #10b981; border-radius: 6px; }
    .strong { border-left-color: #10b981; } .weak { border-left-color: #f59e0b; } .counter { border-left-color: #ef4444; }
    .state-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; }
    .state-box { background: #0f172a; padding: 10px; text-align: center; border-radius: 4px; }
    .bull { border-left: 3px solid #10b981; } .bear { border-left: 3px solid #ef4444; }
    .price { color: #10b981; font-weight: bold; font-size: 1.5em; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🎯 ULTIMATE ICT TRADING SYSTEM</h1>
      <p>
        <strong id="symbol">{{ analysis.symbol }}</strong> –
        <span id="price" class="price">${{ "%.2f"|format(analysis.current_price) }}</span>
      </p>
    </div>
    <div class="grid">
      <div class="section">
        <h2>🚀 TOP OPPORTUNITIES</h2>
        <div id="opportunities">
        {% for opp in analysis.opportunities %}
          <div class="opportunity {{ opp.strength.lower() }}">
            <strong>{{ opp.signal_type }} – {{ opp.strength }}</strong><br>
            <small>Confluence: {{ "%.0f"|format(opp.confluence_score*100) }}% |
                   Probability: {{ "%.0f"|format(opp.probability*100) }}% |
                   R:R {{ "%.1f"|format(opp.risk_reward) }}:1</small><br>
            <small>{{ opp.entry_zone.type }} @ {{ "%.2f"|format(opp.entry_zone.top) }}–
                   {{ "%.2f"|format(opp.entry_zone.bottom) }}</small><br>
            <small>{{ opp.reasoning }}</small>
          </div>
        {% endfor %}
        </div>
      </div>
      <div class="section">
        <h2>📊 MARKET STATES</h2>
        <div class="state-grid" id="states">
        {% for tf, state in analysis.market_states.items() %}
          <div class="state-box {{ 'bull' if 'BULL' in state.state else 'bear' }}">
            <strong>{{ tf }}</strong><br>
            <small><em>{{ state.state }}</em></small><br>
            <small>{{ state.trend }}</small><br>
            <small>{{ "%.0f"|format(state.confidence*100) }}%</small>
          </div>
        {% endfor %}
        </div>
      </div>
    </div>
  </div>

  <!-- Socket.IO client -->
  <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
  <script>
    const socket = io();
    socket.on('update', data => {
      // update header
      document.getElementById('symbol').textContent = data.symbol;
      document.getElementById('price').textContent = '$' + data.current_price.toFixed(2);

      // render opportunities
      const oppCont = document.getElementById('opportunities');
      oppCont.innerHTML = '';
      data.opportunities.forEach(o => {
        const div = document.createElement('div');
        div.className = 'opportunity ' + o.strength.toLowerCase();
        div.innerHTML = `
          <strong>${o.signal_type} – ${o.strength}</strong><br>
          <small>Confluence: ${Math.round(o.confluence_score*100)}% |
                 Probability: ${Math.round(o.probability*100)}% |
                 R:R ${o.risk_reward.toFixed(1)}:1</small><br>
          <small>${o.entry_zone.type} @ ${o.entry_zone.top.toFixed(2)}–
                 ${o.entry_zone.bottom.toFixed(2)}</small><br>
          <small>${o.reasoning}</small>
        `;
        oppCont.appendChild(div);
      });

      // render states
      const stateCont = document.getElementById('states');
      stateCont.innerHTML = '';
      Object.entries(data.market_states).forEach(([tf,s]) => {
        const box = document.createElement('div');
        box.className = 'state-box ' + (s.state.includes('BULL') ? 'bull' : 'bear');
        box.innerHTML = `
          <strong>${tf}</strong><br>
          <small><em>${s.state}</em></small><br>
          <small>${s.trend}</small><br>
          <small>${Math.round(s.confidence*100)}%</small>
        `;
        stateCont.appendChild(box);
      });
    });
  </script>
</body>
</html>
        """

        @self.app.route('/')
        def dashboard():
            return Template(html_template).render(analysis=self.get_analysis())

        @self.app.route('/receive_states', methods=['POST'])
        def receive_states():
            raw = request.data.decode('utf-8', errors='replace').strip()
            logger.info(f"[STATE] Raw body: {raw}")

            if raw.upper().startswith("STRUCTURE:"):
                payload = raw.split(":",1)[1].strip()
                try:
                    data = json.loads(payload)
                    ok = self.receive_structure_data(data)
                    return jsonify({'status':'structure_ok' if ok else 'structure_error'}),200
                except Exception as e:
                    return jsonify({'status':'error','message':str(e)}),400

            elif raw.upper().startswith("STATES:"):
                payload = raw.split(":",1)[1].strip()
                try:
                    data = json.loads(payload)
                    ok = self.receive_state_data(data)
                    return jsonify({'status':'states_ok' if ok else 'states_error'}),200
                except Exception as e:
                    return jsonify({'status':'error','message':str(e)}),400

            else:
                try:
                    data = json.loads(raw)
                    ok = self.receive_state_data(data)
                    return jsonify({'status':'fallback_ok' if ok else 'fallback_error'}),200
                except Exception as e:
                    return jsonify({'status':'error','message':str(e)}),400

        @self.app.route('/receive_states', methods=['POST'])
        def receive_states():
            raw = request.data.decode('utf-8', errors='replace').strip()
            logger.info(f"[STATE] Raw body: {raw}")

            # STRUCTURE-prefixed payload?
        if raw.upper().startswith("STRUCTURE:"):
            payload = raw.split(":", 1)[1].strip()
            try:
                data = json.loads(payload)
                logger.info(f"[STRUCTURE] Parsed JSON: {data}")
                ok = self.receive_structure_data(data)
                status = 'structure_ok' if ok else 'structure_error'
                return jsonify({'status': status}), 200
            except Exception as e:
                logger.error(f"[STRUCTURE] JSON error: {e}", exc_info=True)
                return jsonify({
                    'status': 'error',
                    'message': f"STRUCTURE parse failed: {e}"
                }), 400

        # STATES-prefixed payload?
        elif raw.upper().startswith("STATES:"):
            payload = raw.split(":", 1)[1].strip()
            try:
                data = json.loads(payload)
                logger.info(f"[STATES] Parsed JSON: {data}")
                ok = self.receive_state_data(data)
                status = 'states_ok' if ok else 'states_error'
                return jsonify({'status': status}), 200
            except Exception as e:
                logger.error(f"[STATES] JSON error: {e}", exc_info=True)
                return jsonify({
                    'status': 'error',
                    'message': f"STATES parse failed: {e}"
                }), 400

        # Fallback: try raw JSON
        else:
            try:
                data = json.loads(raw)
                logger.info(f"[FALLBACK] Parsed JSON: {data}")
                ok = self.receive_state_data(data)
                status = 'fallback_ok' if ok else 'fallback_error'
                return jsonify({'status': status}), 200
            except Exception as e:
                logger.error(f"[FALLBACK] JSON error: {e}", exc_info=True)
                return jsonify({
                    'status': 'error',
                    'message': f"Fallback parse failed: {e}"
                }), 400