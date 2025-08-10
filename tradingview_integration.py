# TradingView Integration Options

# Option 1: Webhook Integration (Recommended)
@app.route('/api/tradingview-webhook', methods=['POST'])
@login_required
def tradingview_webhook():
    """Receive trade alerts from TradingView Pine Script"""
    try:
        data = request.get_json()
        
        # Parse TradingView alert format
        trade = {
            'symbol': data.get('ticker', 'NQ1!'),
            'action': data.get('action', 'BUY'),  # BUY/SELL
            'price': float(data.get('price', 0)),
            'quantity': int(data.get('quantity', 1)),
            'timestamp': data.get('time', datetime.now().isoformat()),
            'strategy': data.get('strategy', 'TradingView'),
            'message': data.get('message', '')
        }
        
        # Convert to your format
        formatted_trade = {
            'date': trade['timestamp'][:10],
            'bias': 'LONG' if trade['action'] == 'BUY' else 'SHORT',
            'session': determine_session(trade['timestamp']),
            'entryPrice': trade['price'],
            'positionSize': trade['quantity'],
            'source': 'TradingView'
        }
        
        # Store in database
        db.store_signal({
            'symbol': trade['symbol'],
            'type': formatted_trade['bias'],
            'entry': formatted_trade['entryPrice'],
            'confidence': 0.8,
            'reason': f"TradingView {trade['strategy']} - {trade['message']}"
        })
        
        return jsonify({"status": "success"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def determine_session(timestamp):
    """Determine trading session from timestamp"""
    hour = datetime.fromisoformat(timestamp.replace('Z', '')).hour
    if 0 <= hour < 8: return 'ASIA'
    elif 8 <= hour < 13: return 'LONDON'
    elif 13 <= hour < 16: return 'NY PRE MARKET'
    elif 16 <= hour < 20: return 'NEW YORK AM'
    else: return 'NEW YORK PM'

# Option 2: Broker API Integration
@app.route('/api/sync-broker-trades')
@login_required
def sync_broker_trades():
    """Sync trades from broker API (Interactive Brokers, etc.)"""
    try:
        # Example for Interactive Brokers
        from ib_insync import IB, util
        
        ib = IB()
        ib.connect('127.0.0.1', 7497, clientId=1)
        
        # Get executed trades
        fills = ib.fills()
        
        for fill in fills[-10:]:  # Last 10 trades
            trade = {
                'date': fill.time.date().isoformat(),
                'bias': 'LONG' if fill.execution.side == 'BOT' else 'SHORT',
                'entryPrice': fill.execution.price,
                'positionSize': fill.execution.shares,
                'commission': fill.commissionReport.commission,
                'symbol': fill.contract.symbol
            }
            
            # Store in database
            db.store_signal({
                'symbol': trade['symbol'],
                'type': trade['bias'],
                'entry': trade['entryPrice'],
                'confidence': 0.9,
                'reason': f"Broker execution - {fill.execution.orderId}"
            })
        
        ib.disconnect()
        return jsonify({"status": "success", "trades_synced": len(fills)})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500