#!/usr/bin/env python3
"""
Ultimate ICT Trading System
Multi-TF state tracker + opportunity analyzer + real-time WebSocket dashboard
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict

import pytz
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from jinja2 import Template

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UltimateICTSystem:
    def __init__(self):
        self.ny_tz = pytz.timezone('America/New_York')

        # Initialize multi-TF states
        self.market_states = {
            tf: {'state': 'BULL_ERL_TO_IRL', 'trend': 'Counter', 'confidence': 0.7}
            for tf in ['M', 'W', 'D', '4H', '1H', '15M', '5M', '1M']
        }

        # Zones & opportunities
        self.active_zones = []
        self.opportunities = []
        self.current_price = 0.0
        self.symbol = 'NQ1!'

        # Flask + SocketIO
        self.app = Flask(__name__)
        CORS(self.app)
        # use eventlet mode
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='eventlet')

        self._setup_routes()

    # ─── Receive & parse STATE alerts ───────────────────────────────────────────────
    def receive_state_data(self, data: Dict):
        try:
            # alias old key if needed
            if 'state_1' in data and 'state_1M' not in data:
                data['state_1M'] = data.pop('state_1')

            for tf in self.market_states:
                key = f'state_{tf}'
                if key in data:
                    state_str = data[key]
                    trend = 'Pro' if 'IRL_TO_ERL' in state_str else 'Counter'
                    confidence = 0.8 if 'STRONG' in state_str else 0.6
                    self.market_states[tf] = {
                        'state': state_str,
                        'trend': trend,
                        'confidence': confidence
                    }

            # recalc opportunities
            self._analyze_opportunities()

            # push to all connected clients
            self.socketio.emit('update', self.get_analysis())
            return True

        except Exception:
            logger.exception("Error in receive_state_data")
            return False

    # ─── Receive & parse STRUCTURE alerts ──────────────────────────────────────────
    def receive_structure_data(self, data: Dict):
        try:
            # dynamic symbol
            if 'symbol' in data:
                self.symbol = data['symbol']

            # rebuild zones arrays
            self.active_zones = []
            for zt in ['fvgs', 'order_blocks', 'liquidity_levels']:
                for z in data.get(zt, []):
                    self.active_zones.append({
                        'type':      zt.rstrip('s').upper(),
                        'direction': z.get('direction', 'BULL'),
                        'top':       float(z.get('top', 0)),
                        'bottom':    float(z.get('bottom', 0)),
                        'active':    bool(z.get('active', True)),
                        'strength':  float(z.get('strength', 0.5))
                    })

            if 'current_price' in data:
                self.current_price = float(data['current_price'])

            self._analyze_opportunities()
            self.socketio.emit('update', self.get_analysis())
            return True

        except Exception:
            logger.exception("Error in receive_structure_data")
            return False

    # ─── Analyze confluence & build top opportunities ──────────────────────────────
    def _analyze_opportunities(self):
        self.opportunities = []
        aligns = self._get_alignments()

        for zone in self.active_zones:
            if not zone['active']:
                continue
            conf = self._calculate_confluence(zone, aligns)
            if conf['score'] >= 0.5:
                opp = {
                    'signal_type': 'LONG' if zone['direction'] == 'BULL' else 'SHORT',
                    'strength': conf['strength'],
                    'confluence_score': conf['score'],
                    'probability': min(0.5 + conf['score'] * 0.4, 0.95),
                    'risk_reward': 2.5,
                    'entry_zone': zone,
                    'reasoning': conf['reasoning']
                }
                self.opportunities.append(opp)

        # sort descending by confluence
        self.opportunities.sort(key=lambda x: x['confluence_score'], reverse=True)

    # ─── Helper: build TF alignment pairs ────────────────────────────────────────────
    def _get_alignments(self):
        aligns = {
            'strong_bullish': [], 'strong_bearish': [],
            'weak_bullish': [],   'weak_bearish': []
        }
        pairs = [('M','W'),('W','D'),('D','4H'),('4H','1H'),
                 ('1H','15M'),('15M','5M'),('5M','1M')]

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

    # ─── Helper: score each zone’s confluence ───────────────────────────────────────
    def _calculate_confluence(self, zone, aligns):
        score = zone['strength'] * 0.4
        reasoning = [f"{zone['type']} strength: {zone['strength']:.2f}"]

        if zone['direction'] == 'BULL':
            s = len(aligns['strong_bullish'])
            w = len(aligns['weak_bullish'])
            if s >= 2:
                score += 0.4
                strength = 'STRONG'
                reasoning.append(f"Strong bullish alignment ({s} pairs)")
            elif s >= 1 or w >= 2:
                score += 0.2
                strength = 'WEAK'
                reasoning.append("Moderate bullish alignment")
            else:
                strength = 'COUNTER'
        else:
            s = len(aligns['strong_bearish'])
            w = len(aligns['weak_bearish'])
            if s >= 2:
                score += 0.4
                strength = 'STRONG'
                reasoning.append(f"Strong bearish alignment ({s} pairs)")
            elif s >= 1 or w >= 2:
                score += 0.2
                strength = 'WEAK'
                reasoning.append("Moderate bearish alignment")
            else:
                strength = 'COUNTER'

        return {
            'score': min(score, 1.0),
            'strength': strength,
            'reasoning': ' | '.join(reasoning)
        }

    # ─── Bundle up everything for front-end ─────────────────────────────────────────
    def get_analysis(self):
        return {
            'timestamp': datetime.now(self.ny_tz).isoformat(),
            'symbol': self.symbol,
            'current_price': self.current_price,
            'market_states': self.market_states,
            'opportunities': self.opportunities[:5],
            'summary': {
                'total_opportunities': len(self.opportunities),
                'strong_signals': len([o for o in self.opportunities if o['strength']=='STRONG']),
                'active_zones': len([z for z in self.active_zones if z['active']]),
                'bullish_bias': len([s for s in self.market_states.values() if 'BULL' in s['state']]),
                'bearish_bias': len([s for s in self.market_states.values() if 'BEAR' in s['state']])
            }
        }

    # ─── HTTP & WebSocket routes + Jinja template ───────────────────────────────────
    def _setup_routes(self):
        html_template = """
<!DOCTYPE html>
<html>
<head>
  <title>Ultimate ICT Trading System</title>
  <style>
    body { font-family:'Segoe UI',sans-serif; background:#0a0e1a; color:#e2e8f0; margin:0; padding:20px; }
    .header { text-align:center; margin-bottom:30px; border-bottom:2px solid #1e293b; padding-bottom:20px; }
    .header h1 { color:#f1f5f9; font-size:2.5em; margin:0; }
    .opportunity { background:#0f172a; padding:15px; margin:10px 0; border-radius:6px; border-left:4px solid; }
    .strong { border-color:#10b981; } .weak { border-color:#f59e0b; } .counter { border-color:#ef4444; }
    .state-box { background:#0f172a; padding:10px; text-align:center; border-radius:4px; margin:5px; }
    .bull { border-left:3px solid #10b981; } .bear { border-left:3px solid #ef4444; }
    #grid { display:grid; grid-template-columns:1fr 1fr; gap:20px; }
    #states { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; }
  </style>
</head>
<body>
  <div class="header">
    <h1>🎯 ULTIMATE ICT TRADING SYSTEM</h1>
    <p>
      <strong id="symbol">{{ analysis.symbol }}</strong> –
      <span id="price">${{ "%.2f"|format(analysis.current_price) }}</span>
    </p>
  </div>
  <div id="grid">
    <div>
      <h2>🚀 TOP OPPORTUNITIES</h2>
      <div id="opportunities">
      {% for opp in analysis.opportunities %}
        <div class="opportunity {{ opp.strength.lower() }}">
          <strong>{{ opp.signal_type }} – {{ opp.strength }}</strong><br>
          <small>Confluence: {{ "%.0f"|format(opp.confluence_score*100) }}%</small><br>
          <small>{{ opp.entry_zone.type }} @ {{ "%.2f"|format(opp.entry_zone.top) }}–{{ "%.2f"|format(opp.entry_zone.bottom) }}</small>
        </div>
      {% endfor %}
      </div>
    </div>
    <div>
      <h2>📊 MARKET STATES</h2>
      <div id="states">
      {% for tf, s in analysis.market_states.items() %}
        <div class="state-box {{ 'bull' if 'BULL' in s.state else 'bear' }}">
          <strong>{{ tf }}</strong><br>
          <small><em>{{ s.state }}</em></small><br>
          <small>{{ s.trend }}</small>
        </div>
      {% endfor %}
      </div>
    </div>
  </div>

  <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
  <script>
    const socket = io();
    socket.on('update', data => {
      // Header
      document.getElementById('symbol').textContent = data.symbol;
      document.getElementById('price').textContent  = '$' + data.current_price.toFixed(2);

      // Opportunities
      const opps = document.getElementById('opportunities');
      opps.innerHTML = '';
      data.opportunities.forEach(o => {
        const d = document.createElement('div');
        d.className = 'opportunity ' + o.strength.toLowerCase();
        d.innerHTML = `
          <strong>${o.signal_type} – ${o.strength}</strong><br>
          <small>Confluence: ${Math.round(o.confluence_score*100)}%</small><br>
          <small>${o.entry_zone.type} @ ${o.entry_zone.top.toFixed(2)}–${o.entry_zone.bottom.toFixed(2)}</small>
        `;
        opps.appendChild(d);
      });

      // States
      const st = document.getElementById('states');
      st.innerHTML = '';
      Object.entries(data.market_states).forEach(([tf,s]) => {
        const b = document.createElement('div');
        b.className = 'state-box ' + (s.state.includes('BULL') ? 'bull' : 'bear');
        b.innerHTML = `
          <strong>${tf}</strong><br>
          <small><em>${s.state}</em></small><br>
          <small>${s.trend}</small>
        `;
        st.appendChild(b);
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
            # STRUCTURE:
            if raw.upper().startswith("STRUCTURE:"):
                payload = raw.split(":",1)[1]
                data = json.loads(payload)
                self.receive_structure_data(data)
                return jsonify(status='structure_ok'), 200

            # STATES:
            if raw.upper().startswith("STATES:"):
                payload = raw.split(":",1)[1]
                data = json.loads(payload)
                self.receive_state_data(data)
                return jsonify(status='states_ok'), 200

            # fallback JSON
            data = json.loads(raw)
            self.receive_state_data(data)
            return jsonify(status='fallback_ok'), 200

        @self.app.route('/receive_structure', methods=['POST'])
        def receive_structure():
            data = request.get_json(force=True) or {}
            self.receive_structure_data(data)
            return jsonify(status='structure_ok'), 200

        @self.app.route('/api/analysis', methods=['GET'])
        def api_analysis():
            return jsonify(self.get_analysis()), 200


# instantiate and expose for Gunicorn
system = UltimateICTSystem()
app = system.app
socketio = system.socketio

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting Ultimate ICT System with WebSockets on port {port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=False)