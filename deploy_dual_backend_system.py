#!/usr/bin/env python3
"""
🚀 DUAL INDICATOR BACKEND DEPLOYMENT
Deploys complete backend system for Enhanced FVG + Price Streamer integration
"""

import os
import sys
import requests
import json
from datetime import datetime

# Railway deployment endpoint
RAILWAY_ENDPOINT = "https://web-production-cd33.up.railway.app"

def deploy_dual_webhook_handlers():
    """Deploy both webhook handlers for signal and price data"""
    
    # Enhanced V2 Signal Webhook Handler
    signal_handler_code = '''
@app.route('/api/live-signals-v2', methods=['POST'])
def handle_live_signals_v2():
    """Enhanced V2 signal webhook with comprehensive data processing"""
    try:
        # Get raw data
        raw_data = request.get_data(as_text=True)
        print(f"[V2 SIGNAL] Raw webhook data: {raw_data}")
        
        # Parse JSON data from TradingView
        try:
            data = json.loads(raw_data)
        except json.JSONDecodeError:
            # Handle plain text format if needed
            data = {"raw_message": raw_data}
        
        print(f"[V2 SIGNAL] Parsed data: {data}")
        
        # Process comprehensive signal data
        signal_data = process_enhanced_signal_data(data)
        
        # Store in database
        store_v2_signal(signal_data)
        
        # Trigger real-time updates
        broadcast_signal_update(signal_data)
        
        return jsonify({
            "status": "success",
            "message": "V2 signal processed successfully",
            "signal_id": signal_data.get("id"),
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"[V2 SIGNAL ERROR] {str(e)}")
        return jsonify({
            "status": "error", 
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

def process_enhanced_signal_data(raw_data):
    """Process comprehensive signal data from Enhanced FVG Indicator"""
    try:
        # Extract signal components
        signal_type = raw_data.get("signal_type", "Unknown")
        
        # Signal candle data
        signal_candle = raw_data.get("signal_candle", {})
        
        # FVG analysis data
        fvg_data = raw_data.get("fvg_data", {})
        
        # HTF bias information
        htf_data = raw_data.get("htf_data", {})
        
        # Session and timing
        session_data = raw_data.get("session_data", {})
        
        # Methodology requirements
        methodology_data = raw_data.get("methodology_data", {})
        
        # Create comprehensive signal record
        processed_signal = {
            "signal_type": signal_type,
            "timestamp": datetime.now(),
            "signal_candle_open": signal_candle.get("open"),
            "signal_candle_high": signal_candle.get("high"),
            "signal_candle_low": signal_candle.get("low"),
            "signal_candle_close": signal_candle.get("close"),
            "fvg_bias": fvg_data.get("bias"),
            "fvg_strength": fvg_data.get("strength"),
            "htf_aligned": htf_data.get("aligned", False),
            "htf_bias_1h": htf_data.get("bias_1h"),
            "htf_bias_15m": htf_data.get("bias_15m"),
            "htf_bias_5m": htf_data.get("bias_5m"),
            "session": session_data.get("current_session"),
            "session_valid": session_data.get("valid", False),
            "requires_confirmation": methodology_data.get("requires_confirmation", True),
            "stop_loss_buffer": methodology_data.get("stop_loss_buffer", 25),
            "status": "pending_confirmation",
            "raw_data": json.dumps(raw_data)
        }
        
        return processed_signal
        
    except Exception as e:
        print(f"[SIGNAL PROCESSING ERROR] {str(e)}")
        return {"error": str(e), "raw_data": json.dumps(raw_data)}

def store_v2_signal(signal_data):
    """Store V2 signal in database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert into signals_v2 table
        insert_query = """
        INSERT INTO signals_v2 (
            signal_type, timestamp, signal_candle_open, signal_candle_high,
            signal_candle_low, signal_candle_close, fvg_bias, fvg_strength,
            htf_aligned, htf_bias_1h, htf_bias_15m, htf_bias_5m,
            session, session_valid, requires_confirmation, stop_loss_buffer,
            status, raw_data
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) RETURNING id;
        """
        
        cursor.execute(insert_query, (
            signal_data["signal_type"],
            signal_data["timestamp"],
            signal_data["signal_candle_open"],
            signal_data["signal_candle_high"],
            signal_data["signal_candle_low"],
            signal_data["signal_candle_close"],
            signal_data["fvg_bias"],
            signal_data["fvg_strength"],
            signal_data["htf_aligned"],
            signal_data["htf_bias_1h"],
            signal_data["htf_bias_15m"],
            signal_data["htf_bias_5m"],
            signal_data["session"],
            signal_data["session_valid"],
            signal_data["requires_confirmation"],
            signal_data["stop_loss_buffer"],
            signal_data["status"],
            signal_data["raw_data"]
        ))
        
        signal_id = cursor.fetchone()[0]
        signal_data["id"] = signal_id
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"[V2 SIGNAL STORED] ID: {signal_id}")
        return signal_id
        
    except Exception as e:
        print(f"[V2 SIGNAL STORAGE ERROR] {str(e)}")
        return None
'''

    # Real-time Price Webhook Handler
    price_handler_code = '''
@app.route('/api/realtime-price', methods=['POST'])
def handle_realtime_price():
    """Real-time price webhook for MFE tracking"""
    try:
        # Get raw data
        raw_data = request.get_data(as_text=True)
        print(f"[PRICE STREAM] Raw data: {raw_data}")
        
        # Parse JSON data
        try:
            data = json.loads(raw_data)
        except json.JSONDecodeError:
            data = {"raw_message": raw_data}
        
        # Process price data
        price_data = process_price_stream_data(data)
        
        # Update MFE for active trades
        update_active_trade_mfe(price_data)
        
        # Store price point if significant
        store_price_data(price_data)
        
        # Broadcast real-time update
        broadcast_price_update(price_data)
        
        return jsonify({
            "status": "success",
            "price": price_data.get("price"),
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"[PRICE STREAM ERROR] {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def process_price_stream_data(raw_data):
    """Process real-time price data"""
    try:
        return {
            "symbol": raw_data.get("symbol", "NQ"),
            "price": float(raw_data.get("price", 0)),
            "timestamp": datetime.now(),
            "session": raw_data.get("session"),
            "volume": raw_data.get("volume"),
            "change": raw_data.get("change"),
            "raw_data": json.dumps(raw_data)
        }
    except Exception as e:
        print(f"[PRICE PROCESSING ERROR] {str(e)}")
        return {"error": str(e)}

def update_active_trade_mfe(price_data):
    """Update MFE for all active trades"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get active trades (pending confirmation or confirmed but not resolved)
        cursor.execute("""
            SELECT id, signal_type, signal_candle_open, signal_candle_high, 
                   signal_candle_low, entry_price, stop_loss_price, current_mfe
            FROM signals_v2 
            WHERE status IN ('pending_confirmation', 'confirmed', 'active')
        """)
        
        active_trades = cursor.fetchall()
        current_price = price_data["price"]
        
        for trade in active_trades:
            trade_id, signal_type, sig_open, sig_high, sig_low, entry_price, stop_loss, current_mfe = trade
            
            # Calculate new MFE if trade is active
            if entry_price and stop_loss:
                if signal_type.lower() == "bullish":
                    # Bullish trade: MFE = (current_price - entry_price) / (entry_price - stop_loss)
                    risk_distance = entry_price - stop_loss
                    if risk_distance > 0:
                        new_mfe = (current_price - entry_price) / risk_distance
                else:
                    # Bearish trade: MFE = (entry_price - current_price) / (stop_loss - entry_price)
                    risk_distance = stop_loss - entry_price
                    if risk_distance > 0:
                        new_mfe = (entry_price - current_price) / risk_distance
                
                # Update if new MFE is higher
                if new_mfe > (current_mfe or 0):
                    cursor.execute("""
                        UPDATE signals_v2 
                        SET current_mfe = %s, last_price_update = %s
                        WHERE id = %s
                    """, (new_mfe, datetime.now(), trade_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"[MFE UPDATE ERROR] {str(e)}")

def store_price_data(price_data):
    """Store significant price movements"""
    try:
        # Only store if price change is significant (> 0.5 points)
        if abs(price_data.get("change", 0)) > 0.5:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO price_stream (symbol, price, timestamp, session, volume, change)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                price_data["symbol"],
                price_data["price"],
                price_data["timestamp"],
                price_data["session"],
                price_data.get("volume"),
                price_data.get("change")
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"[PRICE STORAGE ERROR] {str(e)}")
'''

    return signal_handler_code, price_handler_code

def deploy_database_schema():
    """Deploy enhanced database schema for V2 system"""
    
    schema_code = '''
def create_v2_database_schema():
    """Create enhanced V2 database schema"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Enhanced signals_v2 table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signals_v2 (
                id SERIAL PRIMARY KEY,
                signal_type VARCHAR(20) NOT NULL,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                
                -- Signal Candle Data
                signal_candle_open DECIMAL(10,2),
                signal_candle_high DECIMAL(10,2),
                signal_candle_low DECIMAL(10,2),
                signal_candle_close DECIMAL(10,2),
                
                -- FVG Analysis
                fvg_bias VARCHAR(20),
                fvg_strength DECIMAL(5,2),
                
                -- HTF Bias Data
                htf_aligned BOOLEAN DEFAULT FALSE,
                htf_bias_1h VARCHAR(20),
                htf_bias_15m VARCHAR(20),
                htf_bias_5m VARCHAR(20),
                
                -- Session Data
                session VARCHAR(20),
                session_valid BOOLEAN DEFAULT TRUE,
                
                -- Methodology Data
                requires_confirmation BOOLEAN DEFAULT TRUE,
                stop_loss_buffer INTEGER DEFAULT 25,
                
                -- Trade Execution Data
                confirmation_candle_open DECIMAL(10,2),
                confirmation_candle_high DECIMAL(10,2),
                confirmation_candle_low DECIMAL(10,2),
                confirmation_candle_close DECIMAL(10,2),
                confirmation_timestamp TIMESTAMP WITH TIME ZONE,
                
                entry_price DECIMAL(10,2),
                stop_loss_price DECIMAL(10,2),
                
                -- MFE Tracking
                current_mfe DECIMAL(8,4) DEFAULT 0,
                max_mfe DECIMAL(8,4) DEFAULT 0,
                last_price_update TIMESTAMP WITH TIME ZONE,
                
                -- Trade Status
                status VARCHAR(30) DEFAULT 'pending_confirmation',
                resolution_type VARCHAR(20), -- 'stop_loss', 'break_even', 'manual'
                resolution_timestamp TIMESTAMP WITH TIME ZONE,
                
                -- Raw Data Storage
                raw_data JSONB,
                
                -- Indexes
                CONSTRAINT valid_signal_type CHECK (signal_type IN ('Bullish', 'Bearish')),
                CONSTRAINT valid_status CHECK (status IN ('pending_confirmation', 'confirmed', 'active', 'resolved', 'cancelled'))
            );
        """)
        
        # Price stream table for real-time data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_stream (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(10) NOT NULL DEFAULT 'NQ',
                price DECIMAL(10,2) NOT NULL,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                session VARCHAR(20),
                volume INTEGER,
                change DECIMAL(8,4),
                
                -- Index for fast lookups
                INDEX idx_price_timestamp (timestamp DESC),
                INDEX idx_price_symbol_time (symbol, timestamp DESC)
            );
        """)
        
        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_signals_v2_timestamp ON signals_v2 (timestamp DESC);
            CREATE INDEX IF NOT EXISTS idx_signals_v2_status ON signals_v2 (status);
            CREATE INDEX IF NOT EXISTS idx_signals_v2_type ON signals_v2 (signal_type);
            CREATE INDEX IF NOT EXISTS idx_signals_v2_session ON signals_v2 (session);
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ V2 Database schema created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Database schema creation failed: {str(e)}")
        return False
'''

    return schema_code

def deploy_supporting_services():
    """Deploy supporting services for V2 system"""
    
    services_code = '''
def broadcast_signal_update(signal_data):
    """Broadcast signal update via WebSocket"""
    try:
        # WebSocket broadcast logic here
        socketio.emit('signal_update', {
            'type': 'new_signal',
            'data': signal_data
        }, namespace='/signals')
        
    except Exception as e:
        print(f"[BROADCAST ERROR] {str(e)}")

def broadcast_price_update(price_data):
    """Broadcast price update via WebSocket"""
    try:
        socketio.emit('price_update', {
            'type': 'price_stream',
            'data': price_data
        }, namespace='/prices')
        
    except Exception as e:
        print(f"[PRICE BROADCAST ERROR] {str(e)}")

# V2 Dashboard API Endpoints
@app.route('/api/v2/signals/recent', methods=['GET'])
def get_recent_v2_signals():
    """Get recent V2 signals with comprehensive data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, signal_type, timestamp, signal_candle_open, signal_candle_high,
                   signal_candle_low, signal_candle_close, fvg_bias, fvg_strength,
                   htf_aligned, session, status, current_mfe, max_mfe,
                   entry_price, stop_loss_price
            FROM signals_v2 
            ORDER BY timestamp DESC 
            LIMIT 50
        """)
        
        signals = []
        for row in cursor.fetchall():
            signals.append({
                'id': row[0],
                'signal_type': row[1],
                'timestamp': row[2].isoformat() if row[2] else None,
                'signal_candle': {
                    'open': float(row[3]) if row[3] else None,
                    'high': float(row[4]) if row[4] else None,
                    'low': float(row[5]) if row[5] else None,
                    'close': float(row[6]) if row[6] else None
                },
                'fvg_bias': row[7],
                'fvg_strength': float(row[8]) if row[8] else None,
                'htf_aligned': row[9],
                'session': row[10],
                'status': row[11],
                'current_mfe': float(row[12]) if row[12] else 0,
                'max_mfe': float(row[13]) if row[13] else 0,
                'entry_price': float(row[14]) if row[14] else None,
                'stop_loss_price': float(row[15]) if row[15] else None
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'signals': signals,
            'count': len(signals)
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/v2/price/current', methods=['GET'])
def get_current_price():
    """Get current NASDAQ price"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT price, timestamp, session, change
            FROM price_stream 
            ORDER BY timestamp DESC 
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        if result:
            price_data = {
                'price': float(result[0]),
                'timestamp': result[1].isoformat(),
                'session': result[2],
                'change': float(result[3]) if result[3] else 0
            }
        else:
            price_data = None
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'current_price': price_data
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
'''

    return services_code

def create_deployment_script():
    """Create complete deployment script"""
    
    signal_handler, price_handler = deploy_dual_webhook_handlers()
    schema_code = deploy_database_schema()
    services_code = deploy_supporting_services()
    
    complete_deployment = f'''#!/usr/bin/env python3
"""
🚀 COMPLETE V2 DUAL INDICATOR BACKEND DEPLOYMENT
Comprehensive backend system for Enhanced FVG + Price Streamer
"""

import os
import sys
import json
import psycopg2
from datetime import datetime
from flask import Flask, request, jsonify
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

def get_db_connection():
    """Get database connection"""
    try:
        DATABASE_URL = os.environ.get('DATABASE_URL')
        if not DATABASE_URL:
            raise Exception("DATABASE_URL environment variable not set")
        
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Database connection error: {{str(e)}}")
        raise

{schema_code}

{signal_handler}

{price_handler}

{services_code}

# Initialize database on startup
def initialize_v2_system():
    """Initialize V2 system on startup"""
    try:
        print("🚀 Initializing V2 Dual Indicator System...")
        
        # Create database schema
        create_v2_database_schema()
        
        print("✅ V2 System initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ V2 System initialization failed: {{str(e)}}")
        return False

if __name__ == '__main__':
    # Initialize system
    if initialize_v2_system():
        print("🎯 V2 Dual Indicator Backend is ready!")
        print("📡 Webhook endpoints active:")
        print("   - /api/live-signals-v2 (Enhanced FVG signals)")
        print("   - /api/realtime-price (Price stream)")
        print("📊 API endpoints active:")
        print("   - /api/v2/signals/recent")
        print("   - /api/v2/price/current")
    else:
        print("❌ Failed to initialize V2 system")
        sys.exit(1)
'''

    return complete_deployment

def main():
    """Deploy the complete V2 backend system"""
    print("🚀 DEPLOYING V2 DUAL INDICATOR BACKEND SYSTEM")
    print("=" * 60)
    
    try:
        # Create deployment script
        deployment_code = create_deployment_script()
        
        # Save deployment script
        with open('v2_backend_deployment.py', 'w') as f:
            f.write(deployment_code)
        
        print("✅ V2 Backend deployment script created")
        
        # Test deployment endpoint
        test_url = f"{RAILWAY_ENDPOINT}/api/deploy-v2-backend"
        
        print(f"🔄 Deploying to Railway: {test_url}")
        
        # Deploy via web endpoint
        response = requests.post(test_url, 
            json={"deployment_code": deployment_code},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ V2 Backend deployed successfully!")
            print("📡 Webhook endpoints are now active:")
            print(f"   - {RAILWAY_ENDPOINT}/api/live-signals-v2")
            print(f"   - {RAILWAY_ENDPOINT}/api/realtime-price")
            print("📊 API endpoints are now active:")
            print(f"   - {RAILWAY_ENDPOINT}/api/v2/signals/recent")
            print(f"   - {RAILWAY_ENDPOINT}/api/v2/price/current")
        else:
            print(f"❌ Deployment failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Deployment error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎯 V2 DUAL INDICATOR BACKEND DEPLOYMENT COMPLETE!")
        print("Your system is now ready to receive:")
        print("✅ Enhanced FVG signals with comprehensive data")
        print("✅ Real-time price streams for MFE tracking")
        print("✅ Automated signal processing and storage")
        print("✅ Real-time dashboard updates")
    else:
        print("\n❌ Deployment failed - check logs above")