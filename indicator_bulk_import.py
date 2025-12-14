"""
Indicator Bulk Import System
Import the 2,124 signals from indicator into database
"""

from flask import request, jsonify
import psycopg2
import psycopg2.extras
import os
from datetime import datetime

def register_bulk_import_endpoint(app):
    """Register bulk import endpoint"""
    
    @app.route('/api/indicator-import/bulk', methods=['POST'])
    def bulk_import_signals():
        """
        Import signals from indicator in bulk
        Expects: {signals: [{trade_id, date, direction, entry, stop, be_mfe, no_be_mfe, mae, completed}, ...]}
        """
        try:
            data = request.get_json()
            signals = data.get('signals', [])
            
            if not signals:
                return jsonify({'success': False, 'error': 'No signals provided'}), 400
            
            database_url = os.getenv('DATABASE_URL')
            conn = psycopg2.connect(database_url)
            cur = conn.cursor()
            
            imported = 0
            skipped = 0
            
            for signal in signals:
                trade_id = signal.get('trade_id')
                
                # Check if already exists
                cur.execute("SELECT COUNT(*) FROM automated_signals WHERE trade_id = %s AND event_type = 'ENTRY'", (trade_id,))
                exists = cur.fetchone()[0] > 0
                
                if exists:
                    skipped += 1
                    continue
                
                # Parse date/time from trade_id
                parts = trade_id.split('_')
                date_str = parts[0]  # YYYYMMDD
                time_str = parts[1][:6]  # HHMMSS
                
                signal_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                signal_time = f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"
                
                # Insert ENTRY event
                cur.execute("""
                    INSERT INTO automated_signals (
                        trade_id, event_type, timestamp,
                        direction, entry_price, stop_loss,
                        signal_date, signal_time,
                        data_source, confidence_score
                    ) VALUES (
                        %s, 'ENTRY', NOW(),
                        %s, %s, %s,
                        %s, %s,
                        'indicator_historical', 1.0
                    )
                """, (
                    trade_id,
                    'LONG' if signal.get('direction') == 'Bullish' else 'SHORT',
                    signal.get('entry'),
                    signal.get('stop'),
                    signal_date,
                    signal_time
                ))
                
                # Insert final MFE_UPDATE with indicator's MFE values
                cur.execute("""
                    INSERT INTO automated_signals (
                        trade_id, event_type, timestamp,
                        be_mfe, no_be_mfe, mae_global_r,
                        data_source, confidence_score
                    ) VALUES (
                        %s, 'MFE_UPDATE', NOW(),
                        %s, %s, %s,
                        'indicator_historical', 1.0
                    )
                """, (
                    trade_id,
                    signal.get('be_mfe'),
                    signal.get('no_be_mfe'),
                    signal.get('mae')
                ))
                
                # If completed, insert EXIT event
                if signal.get('completed'):
                    cur.execute("""
                        INSERT INTO automated_signals (
                            trade_id, event_type, timestamp,
                            exit_price, final_mfe,
                            data_source, confidence_score
                        ) VALUES (
                            %s, 'EXIT_SL', NOW(),
                            %s, %s,
                            'indicator_historical', 1.0
                        )
                    """, (
                        trade_id,
                        signal.get('stop'),  # Stopped at stop loss
                        signal.get('no_be_mfe')  # Final MFE
                    ))
                
                imported += 1
            
            conn.commit()
            cur.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'imported': imported,
                'skipped': skipped,
                'total': len(signals)
            }), 200
            
        except Exception as e:
            print(f"❌ Bulk import error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    print("✅ Bulk import endpoint registered")
    
    @app.route('/api/indicator-import/all-signals', methods=['POST'])
    def bulk_import_all_signals():
        """
        Import ALL signals (every triangle) from indicator
        Expects: {signals: [{signal_time, direction, status, confirmation_time, bars_to_confirm}, ...]}
        """
        try:
            data = request.get_json()
            signals = data.get('signals', [])
            
            if not signals:
                return jsonify({'success': False, 'error': 'No signals provided'}), 400
            
            database_url = os.getenv('DATABASE_URL')
            conn = psycopg2.connect(database_url)
            cur = conn.cursor()
            
            imported = 0
            skipped = 0
            
            for signal in signals:
                # Build trade_id from signal time and direction
                signal_time = signal.get('signal_time')  # Timestamp in ms
                direction = signal.get('direction')
                
                # Parse timestamp to build trade_id
                from datetime import datetime
                dt = datetime.fromtimestamp(signal_time / 1000)
                trade_id = dt.strftime("%Y%m%d_%H%M%S000_") + ("BULLISH" if direction == "Bullish" else "BEARISH")
                
                # Check if already exists
                cur.execute("SELECT COUNT(*) FROM automated_signals WHERE trade_id = %s AND event_type = 'SIGNAL_CREATED'", (trade_id,))
                exists = cur.fetchone()[0] > 0
                
                if exists:
                    skipped += 1
                    continue
                
                # Insert SIGNAL_CREATED event
                signal_date = dt.strftime("%Y-%m-%d")
                signal_time_str = dt.strftime("%H:%M:%S")
                
                cur.execute("""
                    INSERT INTO automated_signals (
                        trade_id, event_type, timestamp,
                        direction, signal_date, signal_time,
                        data_source, confidence_score
                    ) VALUES (
                        %s, 'SIGNAL_CREATED', %s,
                        %s, %s, %s,
                        'indicator_historical', 1.0
                    )
                """, (
                    trade_id,
                    dt,
                    direction,
                    signal_date,
                    signal_time_str
                ))
                
                # If cancelled, insert CANCELLED event
                if signal.get('status') == 'CANCELLED':
                    cur.execute("""
                        INSERT INTO automated_signals (
                            trade_id, event_type, timestamp,
                            direction,
                            data_source, confidence_score
                        ) VALUES (
                            %s, 'CANCELLED', %s,
                            %s,
                            'indicator_historical', 1.0
                        )
                    """, (trade_id, dt, direction))
                
                imported += 1
            
            conn.commit()
            cur.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'imported': imported,
                'skipped': skipped,
                'total': len(signals)
            }), 200
            
        except Exception as e:
            print(f"❌ All signals import error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    print("✅ All signals import endpoint registered")
