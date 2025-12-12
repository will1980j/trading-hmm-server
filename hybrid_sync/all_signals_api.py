"""
All Signals API - Shows every triangle (SIGNAL_CREATED events)
Includes pending, confirmed, and cancelled signals
"""

import psycopg2
import os
from flask import jsonify
from dotenv import load_dotenv

load_dotenv()

def register_all_signals_api(app):
    """Register All Signals API endpoint"""
    
    @app.route('/api/automated-signals/all-signals', methods=['GET'])
    def get_all_signals():
        """
        Get all signals (every triangle that appeared).
        Includes: SIGNAL_CREATED, matched with ENTRY (confirmation) or CANCELLED
        """
        try:
            database_url = os.getenv('DATABASE_URL')
            conn = psycopg2.connect(database_url)
            cur = conn.cursor()
            
            # Query all SIGNAL_CREATED events with their lifecycle
            cur.execute("""
                WITH signal_lifecycle AS (
                    SELECT 
                        sc.trade_id,
                        sc.timestamp as signal_time,
                        sc.direction,
                        sc.session,
                        sc.htf_alignment,
                        sc.signal_date,
                        sc.signal_time as signal_time_str,
                        -- Check if confirmed (has ENTRY)
                        EXISTS(
                            SELECT 1 FROM automated_signals e 
                            WHERE e.trade_id = sc.trade_id 
                            AND e.event_type = 'ENTRY'
                        ) as is_confirmed,
                        -- Check if cancelled
                        EXISTS(
                            SELECT 1 FROM automated_signals c 
                            WHERE c.trade_id = sc.trade_id 
                            AND c.event_type = 'CANCELLED'
                        ) as is_cancelled,
                        -- Get confirmation time if exists
                        (
                            SELECT e.timestamp 
                            FROM automated_signals e 
                            WHERE e.trade_id = sc.trade_id 
                            AND e.event_type = 'ENTRY' 
                            LIMIT 1
                        ) as confirmation_time,
                        -- Get entry data if confirmed
                        (
                            SELECT e.entry_price 
                            FROM automated_signals e 
                            WHERE e.trade_id = sc.trade_id 
                            AND e.event_type = 'ENTRY' 
                            LIMIT 1
                        ) as entry_price,
                        (
                            SELECT e.stop_loss 
                            FROM automated_signals e 
                            WHERE e.trade_id = sc.trade_id 
                            AND e.event_type = 'ENTRY' 
                            LIMIT 1
                        ) as stop_loss
                    FROM automated_signals sc
                    WHERE sc.event_type = 'SIGNAL_CREATED'
                    ORDER BY sc.timestamp DESC
                    LIMIT 500
                )
                SELECT 
                    trade_id,
                    signal_time,
                    direction,
                    session,
                    htf_alignment,
                    signal_date,
                    signal_time_str,
                    is_confirmed,
                    is_cancelled,
                    confirmation_time,
                    entry_price,
                    stop_loss,
                    CASE 
                        WHEN is_confirmed THEN 
                            EXTRACT(EPOCH FROM (confirmation_time - signal_time))/60
                        ELSE NULL
                    END as minutes_to_confirmation,
                    CASE
                        WHEN is_cancelled THEN 'CANCELLED'
                        WHEN is_confirmed THEN 'CONFIRMED'
                        ELSE 'PENDING'
                    END as status
                FROM signal_lifecycle
                ORDER BY signal_time DESC
            """)
            
            signals = []
            for row in cur.fetchall():
                signal = {
                    'trade_id': row[0],
                    'signal_time': row[1].isoformat() if row[1] else None,
                    'direction': row[2],
                    'session': row[3],
                    'htf_alignment': row[4],
                    'signal_date': row[5],
                    'signal_time_str': row[6],
                    'is_confirmed': row[7],
                    'is_cancelled': row[8],
                    'confirmation_time': row[9].isoformat() if row[9] else None,
                    'entry_price': float(row[10]) if row[10] else None,
                    'stop_loss': float(row[11]) if row[11] else None,
                    'minutes_to_confirmation': float(row[12]) if row[12] else None,
                    'bars_to_confirmation': int(row[12]) if row[12] else None,  # Approximate (1 bar = 1 minute)
                    'status': row[13]
                }
                signals.append(signal)
            
            cur.close()
            conn.close()
            
            # Calculate summary stats
            total = len(signals)
            confirmed = sum(1 for s in signals if s['is_confirmed'])
            cancelled = sum(1 for s in signals if s['is_cancelled'])
            pending = total - confirmed - cancelled
            
            return jsonify({
                'success': True,
                'signals': signals,
                'summary': {
                    'total': total,
                    'confirmed': confirmed,
                    'cancelled': cancelled,
                    'pending': pending,
                    'confirmation_rate': (confirmed / total * 100) if total > 0 else 0
                }
            }), 200
            
        except Exception as e:
            print(f"❌ All Signals API error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    print("✅ All Signals API registered")


def register_cancelled_signals_api(app):
    """Register Cancelled Signals API endpoint"""
    
    @app.route('/api/automated-signals/cancelled-signals', methods=['GET'])
    def get_cancelled_signals():
        """Get all cancelled signals"""
        try:
            database_url = os.getenv('DATABASE_URL')
            conn = psycopg2.connect(database_url)
            cur = conn.cursor()
            
            # Query CANCELLED events
            cur.execute("""
                SELECT 
                    c.trade_id,
                    c.timestamp as cancelled_time,
                    c.direction,
                    c.session,
                    c.signal_date,
                    c.signal_time,
                    c.raw_payload
                FROM automated_signals c
                WHERE c.event_type = 'CANCELLED'
                ORDER BY c.timestamp DESC
                LIMIT 200
            """)
            
            signals = []
            for row in cur.fetchall():
                payload = row[6] if row[6] else {}
                signal = {
                    'trade_id': row[0],
                    'cancelled_time': row[1].isoformat() if row[1] else None,
                    'direction': row[2],
                    'session': row[3],
                    'signal_date': row[4],
                    'signal_time_str': row[5],
                    'cancel_reason': payload.get('exit_reason', 'Opposite signal'),
                    'bars_pending': payload.get('bars_pending')
                }
                signals.append(signal)
            
            cur.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'signals': signals,
                'count': len(signals)
            }), 200
            
        except Exception as e:
            print(f"❌ Cancelled Signals API error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    print("✅ Cancelled Signals API registered")
