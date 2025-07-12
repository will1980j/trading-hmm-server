#!/usr/bin/env python3
"""
Ultimate ICT Trading System
Multi‐timeframe state tracker + opportunity analyzer + responsive Bootstrap dashboard
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
from jinja2 import Template

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UltimateICTSystem:
    def __init__(self):
        self.ny_tz = pytz.timezone('America/New_York')

        # Initialize multi‐timeframe states
        self.market_states = {
            tf: {'state': 'BULL_ERL_TO_IRL', 'trend': 'Counter', 'confidence': 0.7}
            for tf in ['M','W','D','4H','1H','15M','5M','1M']
        }

        # Zones & opportunities
        self.active_zones = []
        self.opportunities = []
        self.current_price = 0.0
        self.symbol = 'NQ1!'

        # Flask setup
        self.app = Flask(__name__)
        CORS(self.app)
        self._setup_routes()

    def receive_state_data(self, data: Dict):
        try:
            # alias old key if needed
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
            return True
        except Exception:
            logger.exception("Error in receive_state_data")
            return False

    def receive_structure_data(self, data: Dict):
        try:
            if 'symbol' in data:
                self.symbol = data['symbol']

            self.active_zones = []
            for zt in ['fvgs','order_blocks','liquidity_levels']:
                for z in data.get(zt, []):
                    self.active_zones.append({
                        'type':      zt.rstrip('s').upper(),
                        'direction': z.get('direction','BULL'),
                        'top':       float(z.get('top',0)),
                        'bottom':    float(z.get('bottom',0)),
                        'active':    bool(z.get('active',True)),
                        'strength':  float(z.get('strength',0.5))
                    })

            if 'current_price' in data:
                self.current_price = float(data['current_price'])

            self._analyze_opportunities()
            return True
        except Exception:
            logger.exception("Error in receive_structure_data")
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
                    'signal_type':    'LONG' if zone['direction']=='BULL' else 'SHORT',
                    'strength':       conf['strength'],
                    'confluence_score': conf['score'],
                    'probability':    min(0.5 + conf['score']*0.4, 0.95),
                    'risk_reward':    2.5,
                    'entry_zone':     zone,
                    'reasoning':      conf['reasoning']
                }
                self.opportunities.append(opp)
        self.opportunities.sort(key=lambda o: o['confluence_score'], reverse=True)

    def _get_alignments(self):
        aligns = {'strong_bullish':[], 'strong_bearish':[],
                  'weak_bullish':[],   'weak_bearish':[]}
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
            'score':      min(score,1.0),
            'strength':   strength,
            'reasoning':  ' | '.join(reasoning)
        }

    def get_analysis(self):
        return {
            'timestamp':     datetime.now(self.ny_tz).isoformat(),
            'symbol':        self.symbol,
            'current_price': self.current_price,
            'market_states': self.market_states,
            'opportunities': self.opportunities[:5],
            'summary': {
                'total_opportunities': len(self.opportunities),
                'strong_signals':      len([o for o in self.opportunities if o['strength']=='STRONG']),
                'active_zones':        len([z for z in self.active_zones if z['active']]),
                'bullish_bias':        len([s for s in self.market_states.values() if 'BULL' in s['state']]),
                'bearish_bias':        len([s for s in self.market_states.values() if 'BEAR' in s['state']])
            }
        }

    def _setup_routes(self):
        html_template = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="15">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Ultimate ICT Trading System</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { background:#0d1117; color:#c9d1d9; }
    .card-opportunity { border-left-width:4px !important; }
    .card-opportunity.strong { border-color:#10b981 !important; }
    .card-opportunity.weak   { border-color:#f59e0b !important; }
    .card-opportunity.counter{ border-color:#ef4444 !important; }
    .state-box { border-radius:4px; background:#161b22; padding:10px; }
    .state-box.bull { border-left:3px solid #10b981; }
    .state-box.bear { border-left:3px solid #ef4444; }
  </style>
</head>
<body>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4 border-bottom pb-3">
      <h1 class="h4">🎯 Ultimate ICT Trading System</h1>
      <div>
        <span class="fw-bold fs-5">{{ analysis.symbol }}</span>
        &nbsp;–&nbsp;
        <span class="fs-5 text-success">${{ "%.2f"|format(analysis.current_price) }}</span>
      </div>
    </div>
    <div class="row g-4">
      <div class="col-lg-8">
        <div class="card bg-dark mb-4">
          <div class="card-header bg-secondary text-white">🚀 Top Opportunities</div>
          <div class="card-body">
            {% for opp in analysis.opportunities %}
            <div class="card bg-dark mb-3 card-opportunity {{ opp.strength.lower() }}">
              <div class="card-body p-3 text-white">
                <h5 class="card-title">{{ opp.signal_type }} – {{ opp.strength }}</h5>
                <p class="mb-1 small">
                  Confluence: {{ "%.0f"|format(opp.confluence_score*100) }}% |
                  Probability: {{ "%.0f"|format(opp.probability*100) }}% |
                  R:R {{ "%.1f"|format(opp.risk_reward) }}:1
                </p>
                <p class="mb-1 small text-muted">
                  {{ opp.entry_zone.type }} @ {{ "%.2f"|format(opp.entry_zone.top) }}–{{ "%.2f"|format(opp.entry_zone.bottom) }}
                </p>
                <p class="small text-muted mb-0">{{ opp.reasoning }}</p>
              </div>
            </div>
            {% else %}
            <p class="text-muted">No opportunities right now.</p>
            {% endfor %}
          </div>
        </div>
      </div>
      <div class="col-lg-4">
        <div class="card bg-dark mb-4">
          <div class="card-header bg-secondary text-white">📊 Market States</div>
          <div class="card-body">
            <div class="row g-2">
              {% for tf, s in analysis.market_states.items() %}
              <div class="col-6">
                <div class="state-box {{ 'bull' if 'BULL' in s.state else 'bear' }}">
                  <strong>{{ tf }}</strong><br>
                  <small><em>{{ s.state }}</em></small><br>
                  <small>{{ s.trend }} {{ "%.0f"|format(s.confidence*100) }}%</small>
                </div>
              </div>
              {% endfor %}
            </div>
          </div>
        </div>
        <div class="card bg-dark">
          <div class="card-header bg-secondary text-white">📈 Summary</div>
          <div class="card-body small text-white">
            <p class="mb-1">Total Opps: {{ analysis.summary.total_opportunities }}</p>
            <p class="mb-1">Strong Signals: {{ analysis.summary.strong_signals }}</p>
            <p class="mb-1">Active Zones: {{ analysis.summary.active_zones }}</p>
            <p class="mb-1">Bullish TFs: {{ analysis.summary.bullish_bias }}/8</p>
            <p class="mb-0">Bearish TFs: {{ analysis.summary.bearish_bias }}/8</p>
          </div>
        </div>
      </div>
    </div>
  </div>
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
                payload = raw.split(":",1)[1].strip()
                self.receive_structure_data(json.loads(payload))
                return jsonify(status='structure_ok'), 200

            # STATES:
            if raw.upper().startswith("STATES:"):
                payload = raw.split(":",1)[1].strip()
                self.receive_state_data(json.loads(payload))
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


# Instantiate & expose for Gunicorn
system = UltimateICTSystem()
app = system.app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting Ultimate ICT System on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)