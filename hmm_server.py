#!/usr/bin/env python3
"""
Ultimate ICT Trading System — Flask + live dashboard + webhook parser
"""

import logging, json, os
from datetime import datetime

import pytz
from flask import Flask, request, jsonify
from flask_cors import CORS

# Database integration
try:
    from database.railway_db import RailwayDB
    db = RailwayDB()
    db_enabled = True
    logging.info("Database connected")
except Exception as e:
    logging.error(f"Database connection failed: {e}")
    db = None
    db_enabled = False


# ─── Setup ─────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
local_tz = pytz.timezone("Australia/Sydney")

app = Flask(__name__)
CORS(app)

# ─── Globals ────────────────────────────────────────────────────────────────
market_states = {
    tf: {"state": "BULL_ERL_TO_IRL", "trend": "Counter", "confidence": 0.7}
    for tf in ["M","W","D","4H","1H","15M","5M","1M"]
}
active_zones = []
opportunities  = []
price_history  = []
symbol         = "NQ1!"
current_price  = 0.0

dashboard_metrics = {
    "symbol": "", "timeframe": "", "state": "",
    "bullFVG": 0, "bearFVG": 0,
    "bullOB": 0,  "bearOB": 0
}

# ─── Core Logic ─────────────────────────────────────────────────────────────
def analyze_opportunities():
    global opportunities
    opps = []
    # simple confluence: count zones in line with trend
    for z in active_zones:
        if not z["active"]: continue
        score = z["strength"]
        opp = {
            "signal_type": "LONG" if z["direction"]=="BULL" else "SHORT",
            "strength": "STRONG" if score>0.7 else ("WEAK" if score>0.4 else "COUNTER"),
            "confluence_score": min(score,1.0),
            "probability": min(0.5 + score*0.4, 0.95),
            "risk_reward": 2.5,
            "entry_zone": z,
            "reasoning": f"{z['type']} @{z['top']:.2f}-{z['bottom']:.2f}"
        }
        opps.append(opp)
        
        # Store in database if available
        if db_enabled and db:
            try:
                db.store_signal({
                    'symbol': symbol,
                    'type': opp['signal_type'],
                    'entry': (z['top'] + z['bottom']) / 2,
                    'confidence': score,
                    'reason': opp['reasoning']
                })
            except Exception as e:
                logger.error(f"Database store error: {e}")
                
    opportunities = sorted(opps, key=lambda o: o["confluence_score"], reverse=True)

def get_analysis():
    price_history.append(current_price)
    price_history[:] = price_history[-20:]
    return {
        "timestamp": datetime.now(local_tz).strftime("%Y-%m-%d %H:%M:%S %Z"),
        "symbol": symbol, "current_price": current_price,
        "price_history": price_history,
        "market_states": market_states,
        "opportunities": opportunities[:5],
        "dashboard": dashboard_metrics,
        "summary": {
            "total_opportunities": len(opportunities),
            "active_zones": len([z for z in active_zones if z["active"]]),
            "bullish_bias": len([s for s in market_states.values() if "BULL" in s["state"]]),
            "bearish_bias": len([s for s in market_states.values() if "BEAR" in s["state"]])
        }
    }

# ─── Routes ────────────────────────────────────────────────────────────────

@app.route('/health')
def health():
    return "OK", 200

@app.route('/receive_states', methods=['POST'])
def receive_states_route():
    try:
        data = request.get_json(force=True)
        # normalize 1 → 1M
        if "state_1" in data and "state_1M" not in data:
            data["state_1M"] = data.pop("state_1")
        for tf in market_states:
            key = f"state_{tf}"
            if key in data:
                val = data[key]
                market_states[tf] = {
                    "state": val,
                    "trend": "Pro" if "IRL_TO_ERL" in val else "Counter",
                    "confidence": 0.8 if "STRONG" in val else 0.6
                }
        analyze_opportunities()
        return jsonify(status="states_ok"), 200
    except Exception as e:
        logger.exception("Error in /receive_states")
        return jsonify(error=str(e)), 500

@app.route('/receive_structure', methods=['POST'])
def receive_structure_route():
    try:
        data = request.get_json(force=True)
        global symbol, current_price, active_zones
        symbol = data.get("symbol", symbol)
        current_price = float(data.get("current_price", current_price))
        active_zones = []
        for zt in ["fvgs","order_blocks","liquidity_levels"]:
            for z in data.get(zt, []):
                active_zones.append({
                    "type": zt.rstrip("s").upper(),
                    "direction": z.get("direction","BULL"),
                    "top": float(z.get("top",0)),
                    "bottom": float(z.get("bottom",0)),
                    "active": bool(z.get("active",True)),
                    "strength": float(z.get("strength",0.5))
                })
        analyze_opportunities()
        return jsonify(status="structure_ok"), 200
    except Exception as e:
        logger.exception("Error in /receive_structure")
        return jsonify(error=str(e)), 500

@app.route('/webhook', methods=['POST'])
def receive_alert():
    raw = request.data.decode('utf-8', errors='replace').strip()
    logger.info("Webhook payload (%d bytes): %s", len(raw), raw)

    # Try pure JSON
    data = None
    try:
        data = json.loads(raw)
    except Exception:
        pass

    # STATES
    if data and any(k.startswith("state_") for k in data):
        return receive_states_route()

    # STRUCTURE
    if data and ("symbol" in data and ("fvgs" in data or "order_blocks" in data)):
        return receive_structure_route()

    # Prefixed handlers
    prefix, json_str = (raw.split(":",1)+["",""])[0].upper(), raw.split(":",1)[1].strip()
    if prefix == "STATES":
        try: data = json.loads(json_str)
        except: return jsonify(error="bad states"),400
        return receive_states_route()
    if prefix == "STRUCTURE":
        try: data = json.loads(json_str)
        except: return jsonify(error="bad structure"),400
        return receive_structure_route()
    if prefix == "DASHBOARD":
        try:
            dash = json.loads(json_str)
            global dashboard_metrics
            dashboard_metrics = dash
            return jsonify(status="dashboard_ok"),200
        except: return jsonify(error="bad dashboard"),400

    return jsonify(error="unknown payload"), 400
@app.route("/", methods=["GET"])
def index():
    # This is the “basic HTML” page that polls /api/analysis every 15 s
    return """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="15">
  <title>ICT Trading System</title>
</head>
<body>
  <h1>ICT Trading System</h1>
  <div>Symbol: <span id="sym">-</span></div>
  <div>Price:  <span id="prc">-</span></div>
  <pre id="out"></pre>

  <script>
    async function update() {
      const res = await fetch('/api/analysis');
      const data = await res.json();
      document.getElementById('sym').textContent = data.symbol;
      document.getElementById('prc').textContent = data.current_price;
      document.getElementById('out').textContent = JSON.stringify(data, null, 2);
    }
    update();
    setInterval(update, 15000);
  </script>
</body>
</html>
"""


@app.route('/api/analysis')
def api_analysis():
    return jsonify(get_analysis()),200

# ─── Launch ────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get("PORT",5000))
    print(f"Starting on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)