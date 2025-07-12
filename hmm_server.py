#!/usr/bin/env python3
"""
Ultimate ICT Trading System
Multi‐timeframe state tracker + opportunity analyzer + polished Bootstrap dashboard
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

# ─── Global State ────────────────────────────────────────────────────────────
local_tz = pytz.timezone('Australia/Sydney')

market_states: Dict[str,Dict] = {
    tf: {'state':'BULL_ERL_TO_IRL','trend':'Counter','confidence':0.7}
    for tf in ['M','W','D','4H','1H','15M','5M','1M']
}

active_zones: list = []
opportunities: list = []
current_price: float = 0.0
symbol: str = 'NQ1!'
price_history: list = []   # for sparkline

# ─── Core Analysis Functions ────────────────────────────────────────────────
def analyze_opportunities():
    """Rebuild the top-opportunities list based on active_zones & market_states."""
    global opportunities
    opportunities = []
    aligns = get_alignments()

    for zone in active_zones:
        if not zone['active']:
            continue
        conf = calculate_confluence(zone, aligns)
        if conf['score'] >= 0.5:
            opportunities.append({
                'signal_type':     'LONG' if zone['direction']=='BULL' else 'SHORT',
                'strength':        conf['strength'],
                'confluence_score':conf['score'],
                'probability':     min(0.5 + conf['score']*0.4, 0.95),
                'risk_reward':     2.5,
                'entry_zone':      zone,
                'reasoning':       conf['reasoning']
            })

    opportunities.sort(key=lambda o: o['confluence_score'], reverse=True)

def get_alignments():
    """Return TF alignment buckets."""
    aligns = {
        'strong_bullish': [], 'strong_bearish': [],
        'weak_bullish':   [], 'weak_bearish':   []
    }
    pairs = [('M','W'),('W','D'),('D','4H'),('4H','1H'),
             ('1H','15M'),('15M','5M'),('5M','1M')]

    for h,l in pairs:
        hs = market_states[h]['state']
        ls = market_states[l]['state']
        if hs=='BULL_IRL_TO_ERL' and ls=='BULL_IRL_TO_ERL':
            aligns['strong_bullish'].append(f"{h}-{l}")
        elif hs=='BEAR_IRL_TO_ERL' and ls=='BEAR_IRL_TO_ERL':
            aligns['strong_bearish'].append(f"{h}-{l}")
        elif 'BULL' in hs and 'BULL' in ls:
            aligns['weak_bullish'].append(f"{h}-{l}")
        elif 'BEAR' in hs and 'BEAR' in ls:
            aligns['weak_bearish'].append(f"{h}-{l}")

    return aligns

def calculate_confluence(zone, aligns):
    """Score how well a zone aligns with multi‐TF trend."""
    score = zone['strength'] * 0.4
    reasoning = [f"{zone['type']} strength: {zone['strength']:.2f}"]

    if zone['direction']=='BULL':
        s = len(aligns['strong_bullish'])
        w = len(aligns['weak_bullish'])
        if s >= 2:
            score += 0.4
            strength = 'STRONG'
            reasoning.append(f"Strong bullish ({s} pairs)")
        elif s >= 1 or w >= 2:
            score += 0.2
            strength = 'WEAK'
            reasoning.append("Moderate bullish")
        else:
            strength = 'COUNTER'
    else:
        s = len(aligns['strong_bearish'])
        w = len(aligns['weak_bearish'])
        if s >= 2:
            score += 0.4
            strength = 'STRONG'
            reasoning.append(f"Strong bearish ({s} pairs)")
        elif s >= 1 or w >= 2:
            score += 0.2
            strength = 'WEAK'
            reasoning.append("Moderate bearish")
        else:
            strength = 'COUNTER'

    return {
        'score':     min(score, 1.0),
        'strength':  strength,
        'reasoning': ' | '.join(reasoning)
    }

def get_analysis():
    """Bundle up everything for the dashboard/API."""
    # update sparkline
    price_history.append(current_price)
    price_history[:] = price_history[-20:]

    return {
        'timestamp':      datetime.now(local_tz).strftime("%Y-%m-%d %H:%M:%S %Z"),
        'symbol':         symbol,
        'current_price':  current_price,
        'price_history':  price_history,
        'market_states':  market_states,
        'opportunities':  opportunities[:5],
        'summary': {
            'total_opportunities': len(opportunities),
            'strong_signals':       len([o for o in opportunities if o['strength']=='STRONG']),
            'active_zones':         len([z for z in active_zones if z['active']]),
            'bullish_bias':         len([s for s in market_states.values() if 'BULL' in s['state']]),
            'bearish_bias':         len([s for s in market_states.values() if 'BEAR' in s['state']])
        }
    }

# ─── Flask App & Routes (continued in Part 2) ─────────────────────────────────
app = Flask(__name__)
CORS(app)
# ─── HTML Template ─────────────────────────────────────────────────────────────
html_template = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="15">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Ultimate ICT Trading System</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
  <style>
    body.light { background:#f8f9fa; color:#212529; }
    body.dark  { background:#0d1117; color:#c9d1d9; }
    .card-opportunity { border-left-width:4px !important; }
    .card-opportunity.strong { border-color:#10b981 !important; }
    .card-opportunity.weak   { border-color:#f59e0b !important; }
    .card-opportunity.counter{ border-color:#ef4444 !important; }
    .state-box { border-radius:4px; padding:10px; }
    .state-box.bull { background:rgba(16,185,129,0.1); }
    .state-box.bear { background:rgba(239,68,68,0.1); }
    .card-body { line-height:1.4; }
    #ops .card-opportunity { margin-bottom:1rem; }
    footer { font-size:0.85rem; opacity:0.6; }

    /* Dark‐mode fixes */
    body.dark .card.bg-transparent {
      background-color: #161b22 !important;
      border: 1px solid #30363d !important;
    }
    body.dark .text-muted {
      color: #8b949e !important;
    }

    /* Light‐mode overrides */
    body.light .card.bg-transparent {
      background-color: #ffffff !important;
      border: 1px solid #dee2e6 !important;
    }
    body.light .text-muted {
      color: #6c757d !important;
    }
  </style>
</head>
<body class="dark">
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h1 class="h5">🎯 Ultimate ICT Trading System</h1>
      <div>
        <span class="fw-semibold">{{ analysis.symbol }}</span> –
        <span class="fw-bold text-success">${{ \"%.2f\"|format(analysis.current_price) }}</span>
        <button id="theme-toggle" class="btn btn-sm btn-outline-light ms-3">
          <i class="bi bi-moon-stars"></i>
        </button>
      </div>
    </div>
    <div class="mb-2 small text-muted">Updated: {{ analysis.timestamp }}</div>

    <!-- Sparkline -->
    <div style="width:200px; height:50px; margin-bottom:1rem;">
      <canvas id="sparkline" width="200" height="50"></canvas>
    </div>

    <div class="row gy-4 mt-3">
      <!-- Top Opportunities -->
      <div class="col-md-8">
        <div class="card bg-transparent border-0">
          <div class="card-header bg-secondary text-white">🚀 Top Opportunities</div>
          <div class="card-body" id="ops">
            {% if analysis.opportunities %}
              {% for opp in analysis.opportunities %}
                <div class="card bg-transparent border card-opportunity {{ opp.strength.lower() }}">
                  <div class="card-body">
                    <h6>{{ opp.signal_type }} – {{ opp.strength }}</h6>
                    <div class="small">
                      Confluence: {{ \"%.0f\"|format(opp.confluence_score*100) }}% |
                      Prob: {{ \"%.0f\"|format(opp.probability*100) }}% |
                      R:R {{ \"%.1f\"|format(opp.risk_reward) }}:1
                    </div>
                    <div class="small text-muted">
                      {{ opp.entry_zone.type }} @ {{ \"%.2f\"|format(opp.entry_zone.top) }}–
                      {{ \"%.2f\"|format(opp.entry_zone.bottom) }}
                    </div>
                    <div class="small text-muted">{{ opp.reasoning }}</div>
                  </div>
                </div>
              {% endfor %}
            {% else %}
              <div class="text-center text-muted py-5">
                <i class="bi bi-emoji-sleeping display-3"></i>
                <p>No current setups</p>
              </div>
            {% endif %}
          </div>
        </div>
      </div>

      <!-- Market States & Summary -->
      <div class="col-md-4">
        <div class="card bg-transparent border-0 mb-3">
          <div class="card-header bg-secondary text-white">📊 Market States</div>
          <div class="card-body">
            <div class="row g-2">
              {% for tf, s in analysis.market_states.items() %}
                <div class="col-6">
                  <div class="state-box {{ 'bull' if 'BULL' in s.state else 'bear' }}">
                    <strong>{{ tf }}</strong><br>
                    <small><em>{{ s.state }}</em></small><br>
                    <small>{{ s.trend }} {{ \"%.0f\"|format(s.confidence*100) }}%</small>
                  </div>
                </div>
              {% endfor %}
            </div>
          </div>
        </div>
        <div class="card bg-transparent border-0">
          <div class="card-header bg-secondary text-white">📈 Summary</div>
          <div class="card-body small">
            <div>Total Opps: {{ analysis.summary.total_opportunities }}</div>
            <div>Strong Signals: {{ analysis.summary.strong_signals }}</div>
            <div>Active Zones: {{ analysis.summary.active_zones }}</div>
            <div>Bullish TFs: {{ analysis.summary.bullish_bias }}/8</div>
            <div>Bearish TFs: {{ analysis.summary.bearish_bias }}/8</div>
          </div>
        </div>
      </div>
    </div>

    <footer class="mt-4 text-center">
      Data feeds: POST /receive_states | POST /receive_structure | GET /api/analysis
    </footer>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <script>
    // sparkline chart
    const spData = {{ analysis.price_history|tojson }};
    const ctx    = document.getElementById('sparkline').getContext('2d');
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: spData.map((_, i) => i+1),
        datasets:[{ data: spData, borderColor:'#10b981', borderWidth:1.5, pointRadius:0, tension:0.3 }]
      },
      options:{
        responsive:false,
        maintainAspectRatio:false,
        scales:{ x:{display:false}, y:{display:false} },
        plugins:{ legend:{display:false}, tooltip:{enabled:false} }
      }
    });

    // theme toggle
    const btn = document.getElementById('theme-toggle');
    btn.onclick = () => {
      document.body.classList.toggle('light');
      document.body.classList.toggle('dark');
      const icon = btn.querySelector('i');
      if (document.body.classList.contains('light')) {
        icon.className = 'bi bi-sun';
        localStorage.setItem('theme','light');
      } else {
        icon.className = 'bi bi-moon-stars';
        localStorage.setItem('theme','dark');
      }
    };
    if (localStorage.getItem('theme')==='light') {
      document.body.classList.replace('dark','light');
      btn.querySelector('i').className = 'bi bi-sun';
    }
  </script>
</body>
</html>
"""

# ─── Flask Routes ─────────────────────────────────────────────────────────────
@app.route('/')
def dashboard():
    return Template(html_template).render(analysis=get_analysis())

@app.route('/receive_states', methods=['POST'])
def receive_states():
    raw = request.data.decode('utf-8', errors='replace').strip()
    if raw.upper().startswith("STRUCTURE:"):
        payload = raw.split(":",1)[1]
        receive_structure(json.loads(payload))
        return jsonify(status='structure_ok'), 200
    if raw.upper().startswith("STATES:"):
        payload = raw.split(":",1)[1]
        receive_state(json.loads(payload))
        return jsonify(status='states_ok'), 200
    receive_state(json.loads(raw))
    return jsonify(status='fallback_ok'), 200

@app.route('/receive_structure', methods=['POST'])
def receive_structure_route():
    data = request.get_json(force=True) or {}
    receive_structure(data)
    return jsonify(status='structure_ok'), 200

@app.route('/api/analysis', methods=['GET'])
def api_analysis():
    return jsonify(get_analysis()), 200

# ─── Receive Helpers ─────────────────────────────────────────────────────────
def receive_state(data: Dict):
    global current_price
    receive_state_data(data)  # using the analysis function above

def receive_structure(data: Dict):
    global current_price
    receive_structure_data(data)  # your existing logic

# ─── Entrypoint ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting Ultimate ICT System on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)