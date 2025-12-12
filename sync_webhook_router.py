"""
Hybrid Signal Synchronization System - Webhook Router
Four specialized webhook endpoints for robust signal tracking
"""

import os
import hashlib
import json
from datetime import datetime
from flask import request, jsonify
import psycopg2
from dotenv import load_dotenv

load_dotenv()

class SyncWebhookRouter:
    """Routes and processes specialized sync webhooks"""
    
    def __init__(self, app, db):
        self.app = app
        self.db = db
        self.register_routes()
        
    def register_routes(self):
        """Register all 4 specialized webhook endpoints"""
        
        # Primary Webhook - Critical events (ENTRY, EXIT, BE_TRIGGERED)
        @self.app.route('/api/sync/primary', methods=['POST'])
        def sync_primary_webhook():
            return self.handle_primary_webhook()
        
        # Batch Webhook - High-frequency MFE updates
        @self.app.route('/api/sync/batch', methods=['POST'])
        def sync_batch_webhook():
            return self.handle_batch_webhook()
        
        # Polling Webhook - Gap-filling responses from indicator
        @self.app.route('/api/sync/polling', methods=['POST'])
        def sync_polling_webhook():
            return self.handle_polling_webhook()
        
        # Heartbeat Webhook - Health monitoring
        @self.app.route('/api/sync/heartbeat', methods=['POST'])
        def sync_heartbeat_webhook():
            return self.handle_heartbeat_webhook()
        
        print("✅ Hybrid Sync webhook routes registered")
    
    def validate_payload(self, payload, required_fields):
        """Validate payload has required fields"""
        missing = [f for f in required_fields if f not in payload]
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"
        return True, None
    
    def calculate_checksum(self, payload):
        """Calculate SHA-256 checksum of payload"""
        payload_str = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(payload_str.encode()).hexdigest()
    
    def handle_primary_webhook(self):
        """Handle critical events: ENTRY, EXIT, BE_TRIGGERED"""
        try:
            payload = request.get_json()
            
            # Validate
            event_type = payload.get('event_type')
            if event_type not in ['ENTRY', 'EXIT_BE', 'EXIT_SL', 'EXIT_STOP_LOSS', 'BE_TRIGGERED']:
                return jsonify({'success': False, 'error': 'Invalid event type for primary webhook'}), 400
            
            valid, error = self.validate_payload(payload, ['event_type', 'trade_id', 'event_timestamp'])
            if not valid:
                return jsonify({'success': False, 'error': error}), 400
            
            # Calculate checksum
            checksum = self.calculate_checksum(payload)
            
            # Add metadata
            payload['data_source'] = 'indicator_realtime'
            payload['confidence_score'] = 1.0
            payload['payload_checksum'] = checksum
            payload['received_at'] = datetime.utcnow().isoformat()
            
            # Log
            print(f"[PRIMARY] {event_type} for {payload['trade_id']}")
            
            # Forward to existing handler (maintains compatibility)
            from web_server import automated_signals_webhook
            return automated_signals_webhook()
            
        except Exception as e:
            print(f"❌ Primary webhook error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def handle_batch_webhook(self):
        """Handle high-frequency MFE updates"""
        try:
            payload = request.get_json()
            
            # Validate
            if payload.get('event_type') != 'MFE_UPDATE_BATCH':
                return jsonify({'success': False, 'error': 'Invalid event type for batch webhook'}), 400
            
            signals = payload.get('signals', [])
            batch_size = payload.get('batch_size', len(signals))
            skipped = payload.get('skipped', 0)
            
            if not signals:
                # Empty batch is OK (debugging)
                print(f"[BATCH] Empty batch received (debug mode)")
                return jsonify({'success': True, 'batch_processed': 0, 'debug': 'empty_batch'}), 200
            
            # Calculate batch checksum
            batch_checksum = self.calculate_checksum(payload)
            batch_timestamp = payload.get('timestamp')
            
            # Get sequence number (incremental per batch)
            database_url = os.getenv('DATABASE_URL')
            conn = psycopg2.connect(database_url)
            cur = conn.cursor()
            
            # Get next sequence number
            cur.execute("SELECT COALESCE(MAX(sequence_number), 0) + 1 FROM automated_signals")
            next_sequence = cur.fetchone()[0]
            
            success_count = 0
            for idx, signal in enumerate(signals):
                try:
                    # Parse timestamp
                    event_ts = batch_timestamp or signal.get('event_timestamp')
                    from dateutil import parser as date_parser
                    import pytz
                    
                    parsed_ts = date_parser.parse(event_ts)
                    if parsed_ts.tzinfo is None:
                        ny_zone = pytz.timezone('America/New_York')
                        parsed_ts = parsed_ts.replace(tzinfo=ny_zone)
                    
                    utc_ts = parsed_ts.astimezone(pytz.UTC)
                    ny_ts = parsed_ts.astimezone(pytz.timezone('America/New_York'))
                    signal_date = ny_ts.strftime('%Y-%m-%d')
                    signal_time = ny_ts.strftime('%H:%M:%S')
                    
                    # Insert MFE_UPDATE with enhanced metadata
                    cur.execute("""
                        INSERT INTO automated_signals (
                            trade_id, event_type, timestamp, 
                            be_mfe, no_be_mfe, mae_global_r,
                            signal_date, signal_time,
                            data_source, confidence_score, payload_checksum, sequence_number,
                            raw_payload
                        ) VALUES (
                            %s, 'MFE_UPDATE', %s,
                            %s, %s, %s,
                            %s, %s,
                            'indicator_realtime', 1.0, %s, %s,
                            %s
                        )
                    """, (
                        signal['trade_id'], utc_ts,
                        signal.get('be_mfe'), signal.get('no_be_mfe'), signal.get('mae_global_r'),
                        signal_date, signal_time,
                        batch_checksum, next_sequence + idx,
                        json.dumps(signal)
                    ))
                    
                    success_count += 1
                    
                except Exception as e:
                    print(f"  ⚠️ Signal {signal.get('trade_id')} failed: {e}")
                    # Log failure to audit trail
                    try:
                        cur.execute("""
                            INSERT INTO sync_audit_log (
                                trade_id, action_type, data_source, success, error_message
                            ) VALUES (%s, 'batch_insert_failed', 'indicator_realtime', FALSE, %s)
                        """, (signal.get('trade_id'), str(e)[:500]))
                    except:
                        pass
                    continue
            
            conn.commit()
            cur.close()
            conn.close()
            
            print(f"[BATCH] Processed {success_count}/{len(signals)} signals (skipped: {skipped})")
            
            return jsonify({
                'success': True,
                'batch_processed': success_count,
                'batch_size': batch_size,
                'signals_skipped': skipped,
                'checksum': batch_checksum
            }), 200
            
        except Exception as e:
            print(f"❌ Batch webhook error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def handle_polling_webhook(self):
        """Handle gap-filling responses from indicator"""
        try:
            payload = request.get_json()
            
            # Validate
            if payload.get('event_type') != 'POLLING_RESPONSE':
                return jsonify({'success': False, 'error': 'Invalid event type for polling webhook'}), 400
            
            signals = payload.get('signals', [])
            request_id = payload.get('request_id')
            
            print(f"[POLLING] Response received: {len(signals)} signals, request_id={request_id}")
            
            # Process each signal
            database_url = os.getenv('DATABASE_URL')
            conn = psycopg2.connect(database_url)
            cur = conn.cursor()
            
            success_count = 0
            for signal in signals:
                try:
                    trade_id = signal['trade_id']
                    
                    # Calculate checksum
                    checksum = self.calculate_checksum(signal)
                    
                    # Insert MFE_UPDATE with polling source
                    from dateutil import parser as date_parser
                    import pytz
                    
                    event_ts = signal.get('event_timestamp', payload.get('timestamp'))
                    parsed_ts = date_parser.parse(event_ts)
                    if parsed_ts.tzinfo is None:
                        ny_zone = pytz.timezone('America/New_York')
                        parsed_ts = parsed_ts.replace(tzinfo=ny_zone)
                    
                    utc_ts = parsed_ts.astimezone(pytz.UTC)
                    ny_ts = parsed_ts.astimezone(pytz.timezone('America/New_York'))
                    
                    cur.execute("""
                        INSERT INTO automated_signals (
                            trade_id, event_type, timestamp,
                            be_mfe, no_be_mfe, mae_global_r,
                            signal_date, signal_time,
                            data_source, confidence_score, payload_checksum,
                            raw_payload
                        ) VALUES (
                            %s, 'MFE_UPDATE', %s,
                            %s, %s, %s,
                            %s, %s,
                            'indicator_polling', 1.0, %s,
                            %s
                        )
                    """, (
                        trade_id, utc_ts,
                        signal.get('be_mfe'), signal.get('no_be_mfe'), signal.get('mae_global_r'),
                        ny_ts.strftime('%Y-%m-%d'), ny_ts.strftime('%H:%M:%S'),
                        checksum, json.dumps(signal)
                    ))
                    
                    # Log to audit trail
                    cur.execute("""
                        INSERT INTO sync_audit_log (
                            trade_id, action_type, data_source, 
                            fields_filled, confidence_score, success
                        ) VALUES (%s, 'polling_response', 'indicator_polling', %s, 1.0, TRUE)
                    """, (trade_id, json.dumps({'be_mfe': True, 'no_be_mfe': True, 'mae': True})))
                    
                    success_count += 1
                    
                except Exception as e:
                    print(f"  ⚠️ Signal {signal.get('trade_id')} failed: {e}")
                    continue
            
            conn.commit()
            cur.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'signals_processed': success_count,
                'request_id': request_id
            }), 200
            
        except Exception as e:
            print(f"❌ Polling webhook error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def handle_sync_request(self, payload):
        """Handle SYNC_REQUEST from indicator - send back active signals"""
        try:
            request_type = payload.get('request')
            lookback_hours = payload.get('lookback_hours', 48)
            
            if request_type != 'active_signals':
                return jsonify({'success': False, 'error': 'Unknown request type'}), 400
            
            print(f"[SYNC_REQUEST] Indicator requesting active signals (lookback: {lookback_hours}h)")
            
            # Query database for active signals
            database_url = os.getenv('DATABASE_URL')
            conn = psycopg2.connect(database_url)
            cur = conn.cursor()
            
            # Get active signals with entry data from last 48 hours
            cur.execute("""
                SELECT DISTINCT ON (e.trade_id)
                    e.trade_id,
                    e.entry_price,
                    e.stop_loss,
                    e.signal_date,
                    e.signal_time,
                    e.session,
                    e.direction,
                    e.timestamp
                FROM automated_signals e
                WHERE e.event_type = 'ENTRY'
                AND e.timestamp > NOW() - INTERVAL '%s hours'
                AND e.trade_id NOT IN (
                    SELECT DISTINCT trade_id 
                    FROM automated_signals 
                    WHERE event_type LIKE 'EXIT_%%'
                )
                AND e.entry_price IS NOT NULL
                AND e.stop_loss IS NOT NULL
                ORDER BY e.trade_id, e.timestamp DESC
            """, (lookback_hours,))
            
            signals = []
            for row in cur.fetchall():
                signals.append({
                    'trade_id': row[0],
                    'entry_price': float(row[1]),
                    'stop_loss': float(row[2]),
                    'signal_date': row[3],
                    'signal_time': row[4],
                    'session': row[5],
                    'direction': row[6],
                    'timestamp': row[7].isoformat()
                })
            
            cur.close()
            conn.close()
            
            print(f"[SYNC_RESPONSE] Sending {len(signals)} active signals to indicator")
            
            # Note: This response goes to logs, not back to indicator
            # Indicator cannot receive responses in PineScript
            # This is for monitoring/debugging only
            return jsonify({
                'success': True,
                'signal_count': len(signals),
                'signals': signals[:10],  # First 10 for logging
                'note': 'Full list logged for backend reconciliation'
            }), 200
            
        except Exception as e:
            print(f"❌ Sync request error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def handle_heartbeat_webhook(self):
        """Handle health monitoring heartbeats"""
        try:
            payload = request.get_json()
            
            # Handle SYNC_REQUEST
            if payload.get('event_type') == 'SYNC_REQUEST':
                return self.handle_sync_request(payload)
            
            # Validate
            if payload.get('event_type') not in ['HEARTBEAT', 'HEALTH_STATUS']:
                return jsonify({'success': False, 'error': 'Invalid event type for heartbeat webhook'}), 400
            
            signal_count = payload.get('signal_count', 0)
            indicator_version = payload.get('indicator_version', 'unknown')
            health_status = payload.get('health_status', 'OK')
            last_error = payload.get('last_error')
            
            print(f"[HEARTBEAT] Signals: {signal_count}, Version: {indicator_version}, Status: {health_status}")
            
            # Store heartbeat in database for monitoring
            database_url = os.getenv('DATABASE_URL')
            conn = psycopg2.connect(database_url)
            cur = conn.cursor()
            
            # Create heartbeat log table if not exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS indicator_heartbeat (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
                    signal_count INTEGER,
                    indicator_version VARCHAR(50),
                    health_status VARCHAR(20),
                    last_error TEXT,
                    payload JSONB
                )
            """)
            
            # Insert heartbeat
            cur.execute("""
                INSERT INTO indicator_heartbeat (
                    signal_count, indicator_version, health_status, last_error, payload
                ) VALUES (%s, %s, %s, %s, %s)
            """, (signal_count, indicator_version, health_status, last_error, json.dumps(payload)))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'received_at': datetime.utcnow().isoformat(),
                'signal_count': signal_count
            }), 200
            
        except Exception as e:
            print(f"❌ Heartbeat webhook error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

def register_sync_webhooks(app, db):
    """Register all sync webhook routes"""
    router = SyncWebhookRouter(app, db)
    return router
