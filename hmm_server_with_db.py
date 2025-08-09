#!/usr/bin/env python3
"""
HMM Server with Supabase Database Integration
"""

import logging, json, os
from datetime import datetime
import pytz
from flask import Flask, request, jsonify
from flask_cors import CORS
from database.railway_db import RailwayDB

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
local_tz = pytz.timezone("Australia/Sydney")

app = Flask(__name__)
CORS(app)

# Database with error handling
try:
    db = RailwayDB()
    db_connected = True
    logger.info("Railway PostgreSQL connected")
except Exception as e:
    logger.error(f"Database connection failed: {e}")
    db = None
    db_connected = False

# In-memory cache for performance
cache = {
    'current_prices': {},
    'active_zones': [],
    'opportunities': []
}

def analyze_opportunities():
    """Analyze opportunities and store in database"""
    try:
        opps = []
        for z in cache['active_zones']:
            if not z.get("active"): continue
            score = z.get("strength", 0.5)
            
            opp = {
                "signal_type": "LONG" if z.get("direction") == "BULL" else "SHORT",
                "strength": "STRONG" if score > 0.7 else ("WEAK" if score > 0.4 else "COUNTER"),
                "confluence_score": min(score, 1.0),
                "probability": min(0.5 + score * 0.4, 0.95),
                "risk_reward": 2.5,
                "entry_zone": z,
                "reasoning": f"{z.get('type', 'ZONE')} @{z.get('top', 0):.2f}-{z.get('bottom', 0):.2f}"
            }
            opps.append(opp)
            
            # Store signal in database if connected
            if db_connected and db:
                try:
                    db.store_signal({
                        'symbol': 'NQ1!',
                        'type': opp['signal_type'],
                        'entry': (z.get('top', 0) + z.get('bottom', 0)) / 2,
                        'confidence': score,
                        'reason': opp['reasoning']
                    })
                except Exception as e:
                    logger.error(f"Database store error: {e}")
        
        cache['opportunities'] = sorted(opps, key=lambda o: o["confluence_score"], reverse=True)
        
    except Exception as e:
        logger.error(f"Opportunity analysis error: {e}")

@app.route('/health')
def health():
    return "OK", 200

@app.route('/receive_states', methods=['POST'])
def receive_states_route():
    try:
        data = request.get_json(force=True)
        
        # Normalize timeframes
        if "state_1" in data and "state_1M" not in data:
            data["state_1M"] = data.pop("state_1")
        
        # Store market states in database as signals
        for tf in ['M', 'W', 'D', '4H', '1H', '15M', '5M', '1M']:
            key = f"state_{tf}"
            if key in data:
                db.store_signal({
                    'symbol': 'NQ1!',
                    'type': 'STATE_UPDATE',
                    'entry': 0,
                    'confidence': 0.8 if "STRONG" in data[key] else 0.6,
                    'reason': f"Market state: {data[key]} on {tf}"
                })
        
        analyze_opportunities()
        return jsonify(status="states_ok"), 200
        
    except Exception as e:
        logger.exception("Error in /receive_states")
        return jsonify(error=str(e)), 500

@app.route('/receive_structure', methods=['POST'])
def receive_structure_route():
    try:
        data = request.get_json(force=True)
        symbol = data.get("symbol", "NQ1!")
        current_price = float(data.get("current_price", 0))
        
        # Store current price
        cache['current_prices'][symbol] = current_price
        
        # Store market data
        if db_connected and db:
            try:
                logger.info(f"Storing market data: {symbol} @ {current_price}")
                result = db.store_market_data(symbol, {
                    'close': current_price,
                    'timestamp': datetime.now().isoformat()
                })
                logger.info(f"Market data stored: {result}")
            except Exception as e:
                logger.error(f"Failed to store market data: {e}")
        
        # Process zones
        cache['active_zones'] = []
        for zone_type in ["fvgs", "order_blocks", "liquidity_levels"]:
            for z in data.get(zone_type, []):
                zone = {
                    "type": zone_type.rstrip("s").upper(),
                    "direction": z.get("direction", "BULL"),
                    "top": float(z.get("top", 0)),
                    "bottom": float(z.get("bottom", 0)),
                    "active": bool(z.get("active", True)),
                    "strength": float(z.get("strength", 0.5))
                }
                cache['active_zones'].append(zone)
                
                # Store ICT level
                db.store_ict_level({
                    'symbol': symbol,
                    'type': zone['type'],
                    'top': zone['top'],
                    'bottom': zone['bottom'],
                    'strength': zone['strength'],
                    'active': zone['active']
                })
        
        analyze_opportunities()
        return jsonify(status="structure_ok"), 200
        
    except Exception as e:
        logger.exception("Error in /receive_structure")
        return jsonify(error=str(e)), 500

@app.route('/webhook', methods=['POST'])
def receive_alert():
    raw = request.data.decode('utf-8', errors='replace').strip()
    logger.info(f"Webhook payload: {raw}")
    
    try:
        data = json.loads(raw)
    except:
        return jsonify(error="Invalid JSON"), 400
    
    # Route to appropriate handler
    if any(k.startswith("state_") for k in data):
        return receive_states_route()
    elif "symbol" in data and ("fvgs" in data or "order_blocks" in data):
        return receive_structure_route()
    
    return jsonify(error="Unknown payload"), 400

@app.route('/api/analysis')
def api_analysis():
    try:
        symbol = "NQ1!"
        current_price = cache['current_prices'].get(symbol, 0.0)
        
        # Get recent data from database if connected
        price_history = []
        if db_connected and db:
            try:
                recent_data = db.get_recent_data(symbol, limit=20)
                price_history = [float(row['close']) for row in recent_data.data] if recent_data.data else []
            except Exception as e:
                logger.error(f"Database query error: {e}")
                price_history = [current_price] * 20  # Fallback
        
        return jsonify({
            "timestamp": datetime.now(local_tz).strftime("%Y-%m-%d %H:%M:%S %Z"),
            "symbol": symbol,
            "current_price": current_price,
            "price_history": price_history,
            "opportunities": cache['opportunities'][:5],
            "active_zones": len(cache['active_zones']),
            "database_status": "connected" if db_connected else "offline"
        })
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify(error=str(e)), 500

@app.route("/")
def index():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Trading System with Database</title>
    <meta http-equiv="refresh" content="15">
</head>
<body>
    <h1>🚀 Trading System with Supabase</h1>
    <div id="status">Loading...</div>
    <pre id="data"></pre>
    
    <script>
        async function update() {
            try {
                const res = await fetch('/api/analysis');
                const data = await res.json();
                document.getElementById('status').innerHTML = 
                    `${data.symbol} @ $${data.current_price} | DB: ${data.database_status}`;
                document.getElementById('data').textContent = JSON.stringify(data, null, 2);
            } catch(e) {
                document.getElementById('status').innerHTML = 'Error: ' + e.message;
            }
        }
        update();
        setInterval(update, 15000);
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Trading System with Database on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)