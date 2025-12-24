"""
Robust Automated Signals API
Production-grade implementation with comprehensive error handling
"""
# INTEGRITY_REPAIR_TIMESTAMPS_ACTIVE
from flask import jsonify, request
from datetime import datetime, timedelta
import pytz
import logging

logger = logging.getLogger(__name__)

def register_automated_signals_api_robust(app, db):
    """Register robust API endpoints with comprehensive error handling"""
    logger.warning("[ROBUST_API_REGISTRATION] Starting registration of all robust API endpoints including repair routes")
    
    # Register repair endpoints FIRST to ensure they're always available
    @app.route('/api/automated-signals/integrity-repair/lifecycle', methods=['POST'])
    def repair_lifecycle():
        """Applies lifecycle reconstruction to all trades."""
        import psycopg2, os
        from psycopg2.extras import RealDictCursor
        from automated_signals_state import repair_trade_lifecycle
        
        db = os.environ.get("DATABASE_PUBLIC_URL") or os.environ.get("DATABASE_URL")
        conn = psycopg2.connect(db)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT id, trade_id, event_type, timestamp, signal_date,
                   signal_time, mfe, be_mfe, no_be_mfe, raw_payload
            FROM automated_signals
            ORDER BY trade_id, timestamp ASC;
        """)
        rows = cursor.fetchall()
        
        # group by trade_id
        grouped = {}
        for r in rows:
            grouped.setdefault(r["trade_id"], []).append(dict(r))
        
        total_fixed = 0
        for tid, events in grouped.items():
            repaired, changed = repair_trade_lifecycle(events)
            if not changed:
                continue
            
            total_fixed += 1
            
            # delete old events
            cursor.execute("DELETE FROM automated_signals WHERE trade_id = %s", (tid,))
            
            # insert repaired events
            for ev in repaired:
                cursor.execute("""
                    INSERT INTO automated_signals
                        (trade_id, event_type, timestamp, signal_date, signal_time,
                         mfe, be_mfe, no_be_mfe, raw_payload)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    tid, ev.get("event_type"), ev.get("timestamp"),
                    ev.get("signal_date"), ev.get("signal_time"),
                    ev.get("mfe"), ev.get("be_mfe"), ev.get("no_be_mfe"),
                    ev.get("raw_payload"),
                ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"success": True, "fixed_lifecycles": total_fixed}), 200
    
    @app.route('/api/automated-signals/integrity-repair/timestamps', methods=['POST'])
    def repair_entry_timestamps():
        """
        Repairs missing signal_date and signal_time for ENTRY events.
        Uses reconstruction logic from recover_missing_entry_timestamps().
        """
        logger.warning("[REPAIR_TIMESTAMPS] Endpoint called - route is registered!")
        import psycopg2
        from psycopg2.extras import RealDictCursor
        import os
        from automated_signals_state import recover_missing_entry_timestamps
        
        db = os.environ.get("DATABASE_PUBLIC_URL") or os.environ.get("DATABASE_URL")
        conn = psycopg2.connect(db)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT
                id, trade_id, event_type, signal_date, signal_time, raw_payload, timestamp
            FROM automated_signals
            ORDER BY trade_id, timestamp ASC;
        """)
        rows = cursor.fetchall()
        
        grouped = {}
        for r in rows:
            grouped.setdefault(r["trade_id"], []).append(r)
        
        total_fixed = 0
        for trade_id, events in grouped.items():
            needs_update, new_date, new_time = recover_missing_entry_timestamps(events)
            if not needs_update:
                continue
            
            cursor.execute("""
                UPDATE automated_signals
                SET signal_date = %s, signal_time = %s
                WHERE trade_id = %s AND event_type = 'ENTRY';
            """, (new_date, new_time, trade_id))
            total_fixed += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "fixed_entries": total_fixed
        }), 200
    
    @app.route('/api/automated-signals/integrity-repair/mae', methods=['POST'])
    def repair_missing_mae():
        """
        Repairs missing MAE (Maximum Adverse Excursion) for completed trades.
        Uses reconstruction logic from recover_missing_mae().
        """
        logger.warning("[REPAIR_MAE] Endpoint called - route is registered!")
        import psycopg2
        from psycopg2.extras import RealDictCursor
        import os
        from automated_signals_state import recover_missing_mae
        
        db = os.environ.get("DATABASE_PUBLIC_URL") or os.environ.get("DATABASE_URL")
        conn = psycopg2.connect(db)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT * FROM automated_signals
            ORDER BY trade_id, timestamp ASC;
        """)
        rows = cursor.fetchall()
        
        grouped = {}
        for r in rows:
            grouped.setdefault(r["trade_id"], []).append(r)
        
        repairs = []
        fixed = 0
        for tid, events in grouped.items():
            needs_update, old_mae, new_mae = recover_missing_mae(events)
            if not needs_update:
                continue
            
            cursor.execute("""
                UPDATE automated_signals
                SET mae_global_r = %s
                WHERE trade_id = %s AND event_type LIKE 'EXIT%%';
            """, (new_mae, tid))
            repairs.append({"trade_id": tid, "old": old_mae, "new": new_mae})
            fixed += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "fixed_trades": fixed,
            "repairs": repairs
        }), 200
    
    logger.warning("[ROBUST_API_REGISTRATION] ✅ Repair routes registered successfully")
    
    @app.route('/api/automated-signals/stats')
    def get_stats_robust():
        """
        Get dashboard statistics with robust error handling
        Returns basic stats for health checks and quick overview
        """
        try:
            cursor = db.conn.cursor()
            
            # Check if table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'automated_signals'
                );
            """)
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                return jsonify({
                    'success': True,
                    'stats': _get_empty_stats(),
                    'message': 'Table not initialized'
                }), 200
            
            # STEP 1: Query most recent webhook timestamp
            cursor.execute("""
                SELECT MAX(timestamp) FROM automated_signals;
            """)
            last_ts = cursor.fetchone()[0]
            
            # STEP 2: Compute webhook_healthy status
            if last_ts is not None:
                now_utc = datetime.now(pytz.UTC)
                # Ensure last_ts is timezone-aware
                if last_ts.tzinfo is None:
                    last_ts = pytz.UTC.localize(last_ts)
                delta_sec = (now_utc - last_ts).total_seconds()
                webhook_healthy = delta_sec < 90
            else:
                webhook_healthy = False
                delta_sec = None
            
            # Get basic counts
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(DISTINCT trade_id) as unique_trades,
                    COUNT(CASE WHEN event_type = 'ENTRY' THEN 1 END) as entries,
                    COUNT(CASE WHEN event_type LIKE 'EXIT_%' THEN 1 END) as exits
                FROM automated_signals;
            """)
            row = cursor.fetchone()
            
            stats = {
                'total_signals': row[0] if row else 0,
                'unique_trades': row[1] if row else 0,
                'entries': row[2] if row else 0,
                'exits': row[3] if row else 0,
                'active_count': (row[2] - row[3]) if row else 0,
                'completed_count': row[3] if row else 0,
                'webhook_healthy': webhook_healthy,
                'last_webhook_timestamp': last_ts.isoformat() if last_ts else None,
                'seconds_since_last_webhook': round(delta_sec, 1) if delta_sec is not None else None
            }
            
            return jsonify({
                'success': True,
                'stats': stats,
                'timestamp': datetime.now(pytz.UTC).isoformat()
            }), 200
            
        except Exception as e:
            logger.error(f"Stats error: {e}", exc_info=True)
            return jsonify({
                'success': True,
                'stats': _get_empty_stats(),
                'error': str(e)
            }), 200


    @app.route('/api/automated-signals/trade-detail/<trade_id>')
    def get_trade_detail(trade_id):
        """
        Get detailed trade information with full telemetry data
        """
        try:
            import os
            import psycopg2
            from psycopg2.extras import RealDictCursor
            from automated_signals_state import build_trade_state
            
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                return jsonify({
                    'success': False,
                    'error': 'no_database_url'
                }), 500
            
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get all events for this trade
            cursor.execute("""
                SELECT 
                    id, trade_id, event_type, direction, entry_price,
                    stop_loss, session, bias, risk_distance,
                    current_price, mfe, be_mfe, no_be_mfe,
                    exit_price, final_mfe,
                    signal_date, signal_time, timestamp
                FROM automated_signals
                WHERE trade_id = %s
                ORDER BY timestamp ASC
            """, (trade_id,))
            
            rows = cursor.fetchall()
            
            if not rows:
                cursor.close()
                conn.close()
                return jsonify({
                    'success': False,
                    'error': 'trade_not_found',
                    'message': f'Trade {trade_id} not found'
                }), 404
            
            # Convert to events list - keep datetime objects for build_trade_state
            events = []
            for row in rows:
                event = dict(row)
                events.append(event)
            
            # Get ENTRY event for core data
            entry_event = next((e for e in events if e.get('event_type') == 'ENTRY'), None)
            
            # Build trade state (for status and aggregated fields)
            trade_state = build_trade_state(events) if events else None
            
            if not trade_state:
                trade_state = {
                    'trade_id': trade_id,
                    'status': 'UNKNOWN',
                    'direction': entry_event.get('direction') if entry_event else 'UNKNOWN'
                }
            
            # Helper to safely convert to float
            def safe_float(val):
                if val is None:
                    return None
                try:
                    return float(val)
                except (TypeError, ValueError):
                    return None
            
            # Get latest MFE values
            latest_mfe = next((e for e in reversed(events) if e.get('event_type') == 'MFE_UPDATE'), None)
            exit_event = next((e for e in reversed(events) if e.get('event_type', '').startswith('EXIT')), None)
            
            # Build detailed response - use ENTRY event data directly
            detail = {
                'trade_id': trade_state['trade_id'],
                'direction': entry_event.get('direction') if entry_event else trade_state.get('direction'),
                'session': entry_event.get('session') if entry_event else trade_state.get('session'),
                'status': trade_state.get('status'),
                'entry_price': safe_float(entry_event.get('entry_price')) if entry_event else None,
                'stop_loss': safe_float(entry_event.get('stop_loss')) if entry_event else None,
                'risk_distance': safe_float(entry_event.get('risk_distance')) if entry_event else None,
                'current_mfe': safe_float(latest_mfe.get('no_be_mfe')) if latest_mfe else None,
                'be_mfe': safe_float(latest_mfe.get('be_mfe')) if latest_mfe else None,
                'no_be_mfe': safe_float(latest_mfe.get('no_be_mfe')) if latest_mfe else None,
                'mae_global_R': safe_float(latest_mfe.get('mae_global_r')) if latest_mfe else None,
                'final_mfe': safe_float(exit_event.get('final_mfe')) if exit_event else None,
                'exit_price': safe_float(exit_event.get('exit_price')) if exit_event else None,
                'exit_reason': trade_state.get('completed_reason'),
                'be_triggered': any(e.get('event_type') == 'BE_TRIGGERED' for e in events),
                'targets': trade_state.get('targets'),
                'setup': {
                    'family': trade_state.get('setup_family'),
                    'variant': trade_state.get('setup_variant'),
                    'id': trade_state.get('setup_id'),
                    'signal_strength': trade_state.get('setup_strength')
                },
                'market_state_entry': {
                    'trend_regime': trade_state.get('market_trend_regime'),
                    'volatility_regime': trade_state.get('market_vol_regime')
                },
                'events': []
            }
            
            # Add events timeline - use raw events from database
            for event in events:
                # Safely convert timestamp
                ts = event.get('timestamp')
                ts_str = ts.isoformat() if hasattr(ts, 'isoformat') else str(ts) if ts else None
                
                event_data = {
                    'event_type': event.get('event_type'),
                    'timestamp': ts_str,
                    'be_mfe': safe_float(event.get('be_mfe')),
                    'no_be_mfe': safe_float(event.get('no_be_mfe')),
                    'mfe': safe_float(event.get('mfe')),
                    'mae_global_r': safe_float(event.get('mae_global_r')),
                    'current_price': safe_float(event.get('current_price')),
                    'exit_price': safe_float(event.get('exit_price')),
                    'entry_price': safe_float(event.get('entry_price')),
                    'stop_loss': safe_float(event.get('stop_loss'))
                }
                
                detail['events'].append(event_data)
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'data': detail,
                'timestamp': datetime.now(pytz.UTC).isoformat()
            }), 200
            
        except Exception as e:
            logger.error(f"Trade detail error: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': 'query_failed',
                'message': str(e)
            }), 500


    @app.route('/api/automated-signals/daily-calendar')
    def get_daily_calendar():
        """Get daily trade data from confirmed_signals_ledger"""
        try:
            import os
            import psycopg2
            
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                return jsonify({'success': False, 'error': 'no_database_url'}), 500
            
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    date,
                    COUNT(*) as trade_count,
                    COUNT(*) FILTER (WHERE completed = false) as active_count,
                    COUNT(*) FILTER (WHERE completed = true) as completed_count,
                    AVG(no_be_mfe) FILTER (WHERE completed = true) as avg_mfe
                FROM confirmed_signals_ledger
                WHERE date IS NOT NULL
                AND date >= CURRENT_DATE - INTERVAL '90 days'
                GROUP BY date
                ORDER BY date DESC
            """)
            
            daily_data = {}
            for row in cursor.fetchall():
                date_str = row[0].isoformat() if row[0] else None
                if date_str:
                    daily_data[date_str] = {
                        'trade_count': row[1],
                        'active_count': row[2],
                        'completed_count': row[3],
                        'avg_mfe': float(row[4]) if row[4] else 0.0
                    }
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'daily_data': daily_data
            })
            
        except Exception as e:
            logger.error(f"Error fetching daily calendar: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500



    # Register indicator export routes
    register_indicator_export_routes(app)
    logger.warning("[ROBUST_API_REGISTRATION] ✅ Indicator export routes registered")

def _get_active_trades_robust(cursor, has_signal_time):
    """Get active trades with telemetry support"""
    try:
        # Import state builder
        from automated_signals_state import build_trade_state
        
        # Get all trade_ids for active trades
        cursor.execute("""
            SELECT trade_id
            FROM (
                SELECT trade_id, MAX(timestamp) AS last_event
                FROM automated_signals
                WHERE event_type = 'ENTRY'
                AND trade_id NOT IN (
                    SELECT trade_id FROM automated_signals 
                    WHERE event_type LIKE 'EXIT_%'
                )
                GROUP BY trade_id
            ) AS sub
            ORDER BY sub.last_event DESC
            LIMIT 100;
        """)
        
        trade_ids = [row[0] for row in cursor.fetchall()]
        
        active_trades = []
        
        for trade_id in trade_ids:
            # Get all events for this trade
            cursor.execute("""
                SELECT 
                    trade_id, event_type, direction, entry_price,
                    stop_loss, session, bias, risk_distance, targets,
                    current_price, mfe, be_mfe, no_be_mfe,
                    exit_price, final_mfe,
                    signal_date, signal_time, timestamp,
                    telemetry
                FROM automated_signals
                WHERE trade_id = %s
                ORDER BY timestamp ASC
            """, (trade_id,))
            
            events = []
            for row in cursor.fetchall():
                event = dict(row)
                # Convert datetime objects to strings
                if event.get('signal_date'):
                    event['signal_date'] = event['signal_date'].isoformat()
                if event.get('signal_time'):
                    event['signal_time'] = event['signal_time'].isoformat()
                if event.get('timestamp'):
                    event['timestamp'] = event['timestamp'].isoformat()
                events.append(event)
            
            # Build trade state using telemetry-aware builder
            trade_state = build_trade_state(events)
            
            if trade_state:
                # Convert to API format
                trade = {
                    'id': events[0].get('id') if events else None,
                    'trade_id': trade_state['trade_id'],
                    'direction': trade_state['direction'],
                    'session': trade_state['session'],
                    'status': trade_state['status'],
                    'entry_price': float(trade_state['entry_price']) if trade_state['entry_price'] else None,
                    'stop_loss': float(trade_state['stop_loss']) if trade_state['stop_loss'] else None,
                    'current_mfe': float(trade_state['current_mfe']) if trade_state['current_mfe'] else None,
                    'final_mfe': float(trade_state['final_mfe']) if trade_state['final_mfe'] else None,
                    'exit_price': float(trade_state['exit_price']) if trade_state['exit_price'] else None,
                    'exit_reason': trade_state['exit_reason'],
                    'be_triggered': trade_state['be_triggered'],
                    'targets': trade_state['targets'],
                    'setup': trade_state['setup'],
                    'market_state': trade_state['market_state'],
                    'timestamp': events[0]['timestamp'] if events else None
                }
                
                # Add date for calendar
                if trade.get('timestamp'):
                    try:
                        ts = datetime.fromisoformat(trade['timestamp'].replace('Z', '+00:00'))
                        eastern = pytz.timezone('America/New_York')
                        ts_eastern = ts.astimezone(eastern)
                        trade['date'] = ts_eastern.strftime('%Y-%m-%d')
                    except:
                        pass
                
                active_trades.append(trade)
        
        return active_trades
        
    except Exception as e:
        import logging
        logging.error(f"Error getting active trades: {e}", exc_info=True)
        return []


def _get_completed_trades_robust(cursor, has_signal_time):
    """Get completed trades with telemetry support"""
    try:
        # Import state builder
        from automated_signals_state import build_trade_state
        
        # Get all trade_ids for completed trades
        cursor.execute("""
            SELECT trade_id
            FROM (
                SELECT trade_id, MAX(timestamp) AS last_event
                FROM automated_signals
                WHERE event_type LIKE 'EXIT_%'
                GROUP BY trade_id
            ) AS sub
            ORDER BY sub.last_event DESC
            LIMIT 100;
        """)
        
        trade_ids = [row[0] for row in cursor.fetchall()]
        
        completed_trades = []
        
        for trade_id in trade_ids:
            # Get all events for this trade
            cursor.execute("""
                SELECT 
                    trade_id, event_type, direction, entry_price,
                    stop_loss, session, bias, risk_distance, targets,
                    current_price, mfe, be_mfe, no_be_mfe,
                    exit_price, final_mfe,
                    signal_date, signal_time, timestamp,
                    telemetry
                FROM automated_signals
                WHERE trade_id = %s
                ORDER BY timestamp ASC
            """, (trade_id,))
            
            events = []
            for row in cursor.fetchall():
                event = dict(row)
                # Convert datetime objects to strings
                if event.get('signal_date'):
                    event['signal_date'] = event['signal_date'].isoformat()
                if event.get('signal_time'):
                    event['signal_time'] = event['signal_time'].isoformat()
                if event.get('timestamp'):
                    event['timestamp'] = event['timestamp'].isoformat()
                events.append(event)
            
            # Build trade state using telemetry-aware builder
            trade_state = build_trade_state(events)
            
            if trade_state and trade_state['status'] == 'COMPLETED':
                # Convert to API format
                trade = {
                    'id': events[0].get('id') if events else None,
                    'trade_id': trade_state['trade_id'],
                    'direction': trade_state['direction'],
                    'session': trade_state['session'],
                    'status': trade_state['status'],
                    'entry_price': float(trade_state['entry_price']) if trade_state['entry_price'] else None,
                    'stop_loss': float(trade_state['stop_loss']) if trade_state['stop_loss'] else None,
                    'current_mfe': float(trade_state['current_mfe']) if trade_state['current_mfe'] else None,
                    'final_mfe': float(trade_state['final_mfe']) if trade_state['final_mfe'] else None,
                    'exit_price': float(trade_state['exit_price']) if trade_state['exit_price'] else None,
                    'exit_reason': trade_state['exit_reason'],
                    'be_triggered': trade_state['be_triggered'],
                    'targets': trade_state['targets'],
                    'setup': trade_state['setup'],
                    'market_state': trade_state['market_state'],
                    'timestamp': events[0]['timestamp'] if events else None
                }
                
                # Add date for calendar
                if trade.get('timestamp'):
                    try:
                        ts = datetime.fromisoformat(trade['timestamp'].replace('Z', '+00:00'))
                        eastern = pytz.timezone('America/New_York')
                        ts_eastern = ts.astimezone(eastern)
                        trade['date'] = ts_eastern.strftime('%Y-%m-%d')
                    except:
                        pass
                
                completed_trades.append(trade)
        
        return completed_trades
        
    except Exception as e:
        import logging
        logging.error(f"Error getting completed trades: {e}", exc_info=True)
        return []


def _calculate_stats_robust(cursor, active_trades, completed_trades):
    """Calculate statistics with robust error handling"""
    try:
        total_signals = len(active_trades) + len(completed_trades)
        active_count = len(active_trades)
        completed_count = len(completed_trades)
        
        # Calculate MFE statistics
        all_mfes = []
        for trade in active_trades:
            if trade.get('current_mfe'):
                all_mfes.append(trade['current_mfe'])
        for trade in completed_trades:
            if trade.get('final_mfe'):
                all_mfes.append(trade['final_mfe'])
        
        avg_mfe = sum(all_mfes) / len(all_mfes) if all_mfes else 0.0
        
        # Calculate win rate (trades that hit targets)
        wins = sum(1 for t in completed_trades if t.get('exit_type') == 'EXIT_TARGET')
        win_rate = (wins / completed_count * 100) if completed_count > 0 else 0.0
        
        return {
            'total_signals': total_signals,
            'active_count': active_count,
            'completed_count': completed_count,
            'pending_count': 0,  # For future use
            'avg_mfe': round(avg_mfe, 2),
            'win_count': wins,
            'win_rate': round(win_rate, 1),
            'success_rate': round(win_rate, 1)
        }
        
    except Exception as e:
        logger.error(f"Error calculating stats: {e}", exc_info=True)
        return _get_empty_stats()

def _get_hourly_distribution_robust(cursor):
    """Get hourly distribution with error handling"""
    try:
        cursor.execute("""
            SELECT 
                EXTRACT(HOUR FROM timestamp AT TIME ZONE 'America/New_York') as hour,
                COUNT(*) as count
            FROM automated_signals
            WHERE event_type = 'ENTRY'
            AND timestamp > NOW() - INTERVAL '30 days'
            GROUP BY hour
            ORDER BY hour;
        """)
        
        distribution = {}
        for row in cursor.fetchall():
            hour = int(row[0])
            count = row[1]
            distribution[str(hour)] = count
        
        return distribution
        
    except Exception as e:
        logger.error(f"Error getting hourly distribution: {e}", exc_info=True)
        return {}

    @app.route('/api/automated-signals/integrity-v2')
    def get_integrity_report():
        """
        Returns full integrity results for all trades using the new
        check_trade_integrity() and build_integrity_report_for_trade() engine.
        """
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            from automated_signals_state import build_trade_state, build_integrity_report_for_trade
            import os
            
            database_url = os.environ.get('DATABASE_URL')
            logger.warning(f"[INTEGRITY_DB_URL] Using DATABASE_URL = {database_url}")
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Fetch all events for all trades
            cursor.execute("""
                SELECT
                    id, trade_id, event_type, direction, entry_price,
                    stop_loss, session, bias, risk_distance,
                    current_price, mfe, be_mfe, no_be_mfe,
                    exit_price, final_mfe,
                    signal_date, signal_time, timestamp
                FROM automated_signals
                ORDER BY trade_id, timestamp ASC;
            """)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Group by trade_id
            grouped = {}
            for r in rows:
                tid = r["trade_id"]
                grouped.setdefault(tid, []).append(r)
            
            issues = []
            for trade_id, evs in grouped.items():
                state = build_trade_state(evs)
                if not state:
                    continue
                
                rep = build_integrity_report_for_trade(evs, state)
                issues.append({
                    "trade_id": trade_id,
                    "healthy": rep["healthy"],
                    "failures": rep["all_failures"],
                    "categories": rep["categories"]
                })
            
            return jsonify({"issues": issues}), 200
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

def _get_session_breakdown_robust(cursor):
    """Get session breakdown with error handling"""
    try:
        cursor.execute("""
            SELECT 
                session,
                COUNT(*) as count,
                AVG(CAST(mfe AS FLOAT)) as avg_mfe
            FROM automated_signals
            WHERE event_type = 'ENTRY'
            AND timestamp > NOW() - INTERVAL '30 days'
            GROUP BY session
            ORDER BY count DESC;
        """)
        
        breakdown = {}
        for row in cursor.fetchall():
            session = row[0] or 'Unknown'
            breakdown[session] = {
                'count': row[1],
                'avg_mfe': round(float(row[2]) if row[2] else 0.0, 2)
            }
        
        return breakdown
        
    except Exception as e:
        logger.error(f"Error getting session breakdown: {e}", exc_info=True)
        return {}

def _format_duration(duration):
    """Format timedelta as human-readable string"""
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def _get_empty_stats():
    """Return empty stats structure"""
    return {
        'total_signals': 0,
        'active_count': 0,
        'completed_count': 0,
        'pending_count': 0,
        'avg_mfe': 0.0,
        'win_count': 0,
        'win_rate': 0.0,
        'success_rate': 0.0
    }


def _get_empty_stats_ultra():
    """Return empty stats structure for Ultra dashboard"""
    return {
        'today_count': 0,
        'active_count': 0,
        'completed_count': 0,
        'last_webhook_timestamp': None,
        'webhook_healthy': False,
        'avg_mfe': 0.0,
        'win_rate': 0.0
    }

    
    @app.route('/api/automated-signals/trades-by-date/<date>')
    def get_trades_by_date(date):
        """Get all trades for a specific date"""
        try:
            import os
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            database_url = os.environ.get('DATABASE_URL')
            conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
            cursor = conn.cursor()
            
            # Get trades for this date
            cursor.execute("""
                SELECT 
                    trade_id,
                    direction,
                    entry_price,
                    stop_loss,
                    session,
                    signal_date,
                    signal_time,
                    be_mfe,
                    no_be_mfe,
                    mae_global_r
                FROM automated_signals
                WHERE signal_date = %s
                AND event_type = 'ENTRY'
                ORDER BY signal_time
            """, (date,))
            
            trades = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Convert to JSON-serializable
            trades_list = []
            for trade in trades:
                trades_list.append({
                    'trade_id': trade['trade_id'],
                    'direction': trade['direction'],
                    'entry': float(trade['entry_price']) if trade['entry_price'] else None,
                    'stop': float(trade['stop_loss']) if trade['stop_loss'] else None,
                    'session': trade['session'],
                    'time': trade['signal_time'].strftime('%H:%M:%S') if trade['signal_time'] else None,
                    'be_mfe': float(trade['be_mfe']) if trade['be_mfe'] else 0.0,
                    'no_be_mfe': float(trade['no_be_mfe']) if trade['no_be_mfe'] else 0.0,
                    'mae': float(trade['mae_global_r']) if trade['mae_global_r'] else 0.0
                })
            
            return jsonify({
                'success': True,
                'date': date,
                'trades': trades_list,
                'count': len(trades_list)
            }), 200
            
        except Exception as e:
            print(f"❌ Trades by date error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    

def register_indicator_export_routes(app):
    """
    Register indicator-export ingestion/import/ledger/reconciliation routes.
    Called from register_automated_signals_api_robust().
    """
    from zoneinfo import ZoneInfo
    
    def extract_symbol(payload: dict) -> str:
        """Extract symbol from payload with fallback priority"""
        # Top-level keys
        if payload.get('symbol'):
            return payload['symbol']
        if payload.get('ticker'):
            return payload['ticker']
        if payload.get('exchange'):
            return payload['exchange']
        
        # First signal fallback
        signals = payload.get('signals', [])
        if isinstance(signals, list) and len(signals) > 0:
            first = signals[0]
            if isinstance(first, dict):
                if first.get('symbol'):
                    return first['symbol']
                if first.get('ticker'):
                    return first['ticker']
                if first.get('exchange'):
                    return first['exchange']
        
        return 'unknown'
    
    @app.route('/api/indicator-export', methods=['POST'])
    def indicator_export_webhook():
        """
        Receive TradingView indicator export batches.
        Stores raw batch in indicator_export_batches table.
        """
        import json
        import hashlib
        import psycopg2
        from psycopg2.extras import Json
        from flask import request
        import os
        
        logger.info("[INDICATOR_EXPORT] Received request")
        
        # Shared secret check (header or query param)
        expected_token = os.environ.get('INDICATOR_EXPORT_TOKEN')
        if expected_token:
            header_token = request.headers.get('X-Indicator-Token')
            query_token = request.args.get('token')
            
            if not (header_token == expected_token or query_token == expected_token):
                logger.warning("[INDICATOR_EXPORT] ❌ Unauthorized: Invalid or missing token")
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
        else:
            # Dev mode - log warning once
            if not hasattr(indicator_export_webhook, '_warned_no_token'):
                logger.warning("[INDICATOR_EXPORT] ⚠️  INDICATOR_EXPORT_TOKEN not set - running in dev mode (no auth)")
                indicator_export_webhook._warned_no_token = True
        
        # Capture raw request data BEFORE parsing
        ct = request.headers.get("Content-Type", "")
        raw = request.get_data(as_text=True) or ""
        raw_len = len(raw)
        
        # Parse JSON body
        try:
            data = request.get_json(force=True)
        except Exception as e:
            # Log detailed error with raw payload info (truncated for safety)
            logger.error("[INDICATOR_EXPORT] Invalid JSON ct=%s len=%d head=%s", ct, raw_len, raw[:1500])
            
            # Return detailed error response (without token)
            return jsonify({
                'success': False,
                'error': 'invalid_json',
                'content_type': ct,
                'body_len': raw_len,
                'body_head': raw[:500]
            }), 400
        
        # Compute SHA256 hash (stable canonicalization)
        payload_str = json.dumps(data, sort_keys=True)
        payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()
        
        # Extract envelope fields
        event_type = data.get('event_type')
        batch_number = data.get('batch_number')
        total_signals = data.get('total_signals')
        raw_signals = data.get('signals', [])
        
        # Normalize signals for MFE_UPDATE_BATCH BEFORE validation
        signals = raw_signals
        if event_type == "MFE_UPDATE_BATCH":
            if isinstance(raw_signals, dict):
                signals = [raw_signals]
            elif isinstance(raw_signals, str):
                try:
                    parsed = json.loads(raw_signals)
                    if isinstance(parsed, list):
                        signals = parsed
                    elif isinstance(parsed, dict):
                        signals = [parsed]
                    else:
                        signals = []
                except:
                    signals = []
            elif isinstance(raw_signals, list):
                signals = raw_signals
            else:
                signals = []
            
            logger.info(f"[INDICATOR_EXPORT] MFE_NORMALIZED signals_type={type(raw_signals).__name__} signals_count={len(signals)}")
        
        # Compute batch_size from normalized signals
        batch_size = len(signals) if event_type == "MFE_UPDATE_BATCH" else data.get('batch_size')
        
        # Determine symbol for logging
        symbol_log = extract_symbol(data)
        
        # Check if OHLC present
        has_ohlc = all(k in data for k in ['bar_ts', 'open', 'high', 'low', 'close'])
        bar_ts_log = data.get('bar_ts') if has_ohlc else None
        
        logger.info(f"[INDICATOR_EXPORT] event_type={event_type}, batch={batch_number}, size={batch_size}, hash={payload_hash[:8]}, symbol={symbol_log}, has_ohlc={has_ohlc}, bar_ts={bar_ts_log}")
        
        # Validate event_type
        valid_types = ['INDICATOR_EXPORT_V2', 'ALL_SIGNALS_EXPORT', 'MFE_UPDATE_BATCH', 'UNIFIED_SNAPSHOT_V1']
        is_valid = event_type in valid_types and isinstance(signals, list)
        validation_error = None if is_valid else f"Invalid {event_type}: event_type={event_type} signals_type={type(signals).__name__}"
        
        # Dry-run mode - validate without inserting
        dry_run = request.args.get('dry_run') == '1'
        if dry_run:
            first_signal_keys = None
            if isinstance(signals, list) and len(signals) > 0:
                first_signal = signals[0]
                if isinstance(first_signal, dict):
                    first_signal_keys = list(first_signal.keys())[:30]
            
            logger.info(f"[INDICATOR_EXPORT_DRYRUN] event_type={event_type}, is_valid={is_valid}, validation_error={validation_error}, signals_len={len(signals) if isinstance(signals, list) else None}, first_signal_keys={first_signal_keys}")
            
            return jsonify({
                'dry_run': True,
                'is_valid': is_valid,
                'validation_error': validation_error,
                'event_type': event_type,
                'signals_is_array': isinstance(signals, list),
                'signals_len': len(signals) if isinstance(signals, list) else None,
                'first_signal_keys': first_signal_keys
            }), 200
        
        # Insert into database
        try:
            DATABASE_URL = os.environ.get('DATABASE_PUBLIC_URL') or os.environ.get('DATABASE_URL')
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            
            # UNIFIED_SNAPSHOT_V1 special handling (dedupe by bar_ts, not batch hash)
            if event_type == "UNIFIED_SNAPSHOT_V1":
                stored_price_bar = False
                signals_upserted = 0
                
                # Process OHLC if present
                if all(k in data for k in ['bar_ts', 'open', 'high', 'low', 'close']):
                    try:
                        from services.price_snapshot_processor import process_price_snapshot, canonical_symbol
                        snapshot_result = process_price_snapshot({
                            'symbol': canonical_symbol(extract_symbol(data)),
                            'timeframe': data.get('timeframe', '1m'),
                            'bar_ts': data['bar_ts'],
                            'open': data['open'],
                            'high': data['high'],
                            'low': data['low'],
                            'close': data['close']
                        })
                        
                        stored_price_bar = True
                        logger.info(f"[UNIFIED_SNAPSHOT_V1] Price bar stored: {snapshot_result}")
                    except Exception as snap_err:
                        logger.error(f"[UNIFIED_SNAPSHOT_V1] Price bar failed: {snap_err}")
                
                # Upsert signals directly into confirmed_signals_ledger
                backfilled_symbol_count = 0
                backfilled_symbol_trade_ids = []
                
                if isinstance(signals, list) and len(signals) > 0:
                    from datetime import datetime as dt
                    from zoneinfo import ZoneInfo
                    
                    for signal in signals:
                        trade_id = signal.get('trade_id')
                        if not trade_id:
                            continue
                        
                        triangle_time_ms = signal.get('triangle_time_ms') or signal.get('triangle_time')
                        if not triangle_time_ms:
                            logger.warning(f"[UNIFIED_SNAPSHOT_V1] Missing triangle_time for {trade_id}")
                            continue
                        
                        try:
                            triangle_time_ms = int(triangle_time_ms)
                        except (ValueError, TypeError):
                            continue
                        
                        confirmation_time_ms = signal.get('confirmation_time_ms') or signal.get('confirmation_time')
                        try:
                            confirmation_time_ms = int(confirmation_time_ms) if confirmation_time_ms else None
                        except (ValueError, TypeError):
                            confirmation_time_ms = None
                        
                        date_str = signal.get('date')
                        date_obj = None
                        if date_str:
                            try:
                                date_obj = dt.strptime(date_str, '%Y-%m-%d').date()
                            except:
                                pass
                        
                        session = signal.get('session')
                        direction = signal.get('direction')
                        
                        try:
                            entry = float(signal['entry']) if signal.get('entry') else None
                        except (ValueError, TypeError):
                            entry = None
                        
                        try:
                            stop = float(signal['stop']) if signal.get('stop') else None
                        except (ValueError, TypeError):
                            stop = None
                        
                        try:
                            be_mfe = float(signal['be_mfe']) if signal.get('be_mfe') else None
                        except (ValueError, TypeError):
                            be_mfe = None
                        
                        try:
                            no_be_mfe = float(signal['no_be_mfe']) if signal.get('no_be_mfe') else None
                        except (ValueError, TypeError):
                            no_be_mfe = None
                        
                        try:
                            mae = float(signal['mae']) if signal.get('mae') else None
                            if mae and mae > 0.0:
                                mae = 0.0
                        except (ValueError, TypeError):
                            mae = None
                        
                        completed_raw = signal.get('completed')
                        if isinstance(completed_raw, str):
                            completed = completed_raw.lower() == 'true'
                        elif isinstance(completed_raw, bool):
                            completed = completed_raw
                        else:
                            completed = None
                        
                        symbol_val = signal.get('symbol') or data.get('symbol') or signal.get('exchange') or data.get('exchange') or ''
                        
                        # Canonicalize symbol
                        from services.price_snapshot_processor import canonical_symbol
                        symbol_val = canonical_symbol(symbol_val) if symbol_val else ''
                        if symbol_val.lower() == 'unknown':
                            symbol_val = ''
                        
                        cursor.execute("""
                            INSERT INTO confirmed_signals_ledger 
                            (trade_id, triangle_time_ms, confirmation_time_ms, date, session, direction, 
                             entry, stop, be_mfe, no_be_mfe, mae, completed, symbol, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                            ON CONFLICT (trade_id) DO UPDATE SET
                                triangle_time_ms = COALESCE(EXCLUDED.triangle_time_ms, confirmed_signals_ledger.triangle_time_ms),
                                confirmation_time_ms = COALESCE(EXCLUDED.confirmation_time_ms, confirmed_signals_ledger.confirmation_time_ms),
                                date = COALESCE(EXCLUDED.date, confirmed_signals_ledger.date),
                                session = COALESCE(EXCLUDED.session, confirmed_signals_ledger.session),
                                direction = COALESCE(EXCLUDED.direction, confirmed_signals_ledger.direction),
                                entry = COALESCE(EXCLUDED.entry, confirmed_signals_ledger.entry),
                                stop = COALESCE(EXCLUDED.stop, confirmed_signals_ledger.stop),
                                be_mfe = COALESCE(EXCLUDED.be_mfe, confirmed_signals_ledger.be_mfe),
                                no_be_mfe = COALESCE(EXCLUDED.no_be_mfe, confirmed_signals_ledger.no_be_mfe),
                                mae = COALESCE(EXCLUDED.mae, confirmed_signals_ledger.mae),
                                completed = COALESCE(EXCLUDED.completed, confirmed_signals_ledger.completed),
                                symbol = COALESCE(NULLIF(confirmed_signals_ledger.symbol,''), EXCLUDED.symbol),
                                updated_at = NOW()
                            RETURNING (confirmed_signals_ledger.symbol IS NULL OR confirmed_signals_ledger.symbol='') AS was_empty_symbol
                        """, (trade_id, triangle_time_ms, confirmation_time_ms, date_obj, session, direction,
                              entry, stop, be_mfe, no_be_mfe, mae, completed, symbol_val))
                        
                        result = cursor.fetchone()
                        if result and result[0] and symbol_val:
                            backfilled_symbol_count += 1
                            if len(backfilled_symbol_trade_ids) < 10:
                                backfilled_symbol_trade_ids.append(trade_id)
                        
                        signals_upserted += 1
                    
                    conn.commit()
                    logger.info(f"[UNIFIED_SNAPSHOT_V1] signals_len={len(signals)}, upserted={signals_upserted}, symbol={extract_symbol(data)}, timeframe={data.get('timeframe')}")
                
                # Process triangles_delta if present
                triangles_delta = data.get('triangles_delta', [])
                if isinstance(triangles_delta, list) and len(triangles_delta) > 0:
                    logger.info(f"[UNIFIED_SNAPSHOT_V1] Processing triangles_delta, count={len(triangles_delta)}")
                    
                    triangles_inserted = 0
                    triangles_updated = 0
                    
                    for triangle in triangles_delta:
                        trade_id = triangle.get('trade_id')
                        if not trade_id:
                            continue
                        
                        # Coerce triangle_time_ms
                        try:
                            triangle_time_ms = int(triangle.get('triangle_time'))
                        except (ValueError, TypeError):
                            logger.warning(f"[UNIFIED_SNAPSHOT_V1] Invalid triangle_time for {trade_id}")
                            continue
                        
                        # Coerce confirmation_time_ms
                        try:
                            confirmation_time_ms = int(triangle['confirmation_time']) if triangle.get('confirmation_time') else None
                        except (ValueError, TypeError):
                            confirmation_time_ms = None
                        
                        # Coerce bars_to_confirm
                        try:
                            bars_to_confirm = int(triangle['bars_to_confirm']) if triangle.get('bars_to_confirm') else None
                        except (ValueError, TypeError):
                            bars_to_confirm = None
                        
                        direction = triangle.get('direction')
                        status = triangle.get('status')
                        session = triangle.get('session')
                        
                        # Coerce numeric fields
                        try:
                            entry_price = float(triangle['entry']) if triangle.get('entry') and triangle.get('entry') != 'null' else None
                        except (ValueError, TypeError):
                            entry_price = None
                        
                        try:
                            stop_loss = float(triangle['stop']) if triangle.get('stop') and triangle.get('stop') != 'null' else None
                        except (ValueError, TypeError):
                            stop_loss = None
                        
                        try:
                            risk_points = float(triangle['risk']) if triangle.get('risk') and triangle.get('risk') != 'null' else None
                        except (ValueError, TypeError):
                            risk_points = None
                        
                        # HTF fields
                        htf_daily = triangle.get('htf_daily') if triangle.get('htf_daily') != 'null' else None
                        htf_4h = triangle.get('htf_4h') if triangle.get('htf_4h') != 'null' else None
                        htf_1h = triangle.get('htf_1h') if triangle.get('htf_1h') != 'null' else None
                        htf_15m = triangle.get('htf_15m') if triangle.get('htf_15m') != 'null' else None
                        htf_5m = triangle.get('htf_5m') if triangle.get('htf_5m') != 'null' else None
                        
                        # Upsert into all_signals_ledger
                        cursor.execute("""
                            INSERT INTO all_signals_ledger 
                            (trade_id, triangle_time_ms, confirmation_time_ms, direction, status, 
                             bars_to_confirm, session, entry_price, stop_loss, risk_points,
                             htf_daily, htf_4h, htf_1h, htf_15m, htf_5m,
                             updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                            ON CONFLICT (trade_id) DO UPDATE SET
                                status = EXCLUDED.status,
                                confirmation_time_ms = COALESCE(EXCLUDED.confirmation_time_ms, all_signals_ledger.confirmation_time_ms),
                                bars_to_confirm = COALESCE(EXCLUDED.bars_to_confirm, all_signals_ledger.bars_to_confirm),
                                session = COALESCE(EXCLUDED.session, all_signals_ledger.session),
                                entry_price = COALESCE(EXCLUDED.entry_price, all_signals_ledger.entry_price),
                                stop_loss = COALESCE(EXCLUDED.stop_loss, all_signals_ledger.stop_loss),
                                risk_points = COALESCE(EXCLUDED.risk_points, all_signals_ledger.risk_points),
                                htf_daily = COALESCE(EXCLUDED.htf_daily, all_signals_ledger.htf_daily),
                                htf_4h = COALESCE(EXCLUDED.htf_4h, all_signals_ledger.htf_4h),
                                htf_1h = COALESCE(EXCLUDED.htf_1h, all_signals_ledger.htf_1h),
                                htf_15m = COALESCE(EXCLUDED.htf_15m, all_signals_ledger.htf_15m),
                                htf_5m = COALESCE(EXCLUDED.htf_5m, all_signals_ledger.htf_5m),
                                updated_at = NOW()
                            RETURNING (xmax = 0) AS inserted
                        """, (trade_id, triangle_time_ms, confirmation_time_ms, direction, status,
                              bars_to_confirm, session, entry_price, stop_loss, risk_points,
                              htf_daily, htf_4h, htf_1h, htf_15m, htf_5m))
                        
                        result = cursor.fetchone()
                        if result and result[0]:
                            triangles_inserted += 1
                        else:
                            triangles_updated += 1
                    
                    conn.commit()
                    logger.info(f"[UNIFIED_SNAPSHOT_V1] triangles_delta processed: inserted={triangles_inserted}, updated={triangles_updated}")
                
                cursor.close()
                conn.close()
                
                return jsonify({
                    'event_type': 'UNIFIED_SNAPSHOT_V1',
                    'status': 'ok',
                    'stored_price_bar': stored_price_bar,
                    'signals_processed': len(signals) if isinstance(signals, list) else 0,
                    'signals_upserted': signals_upserted,
                    'triangles_delta_processed': len(triangles_delta) if isinstance(triangles_delta, list) else 0,
                    'triangles_inserted': triangles_inserted if 'triangles_inserted' in locals() else 0,
                    'triangles_updated': triangles_updated if 'triangles_updated' in locals() else 0,
                    'backfilled_symbol_count': backfilled_symbol_count,
                    'backfilled_symbol_trade_ids': backfilled_symbol_trade_ids
                }), 200
            
            # Standard event types (existing logic)
            # Process price snapshot if present
            if all(k in data for k in ['bar_ts', 'open', 'high', 'low', 'close']):
                try:
                    from services.price_snapshot_processor import process_price_snapshot
                    snapshot_result = process_price_snapshot({
                        'symbol': extract_symbol(data),
                        'timeframe': data.get('timeframe', '1m'),
                        'bar_ts': data['bar_ts'],
                        'open': data['open'],
                        'high': data['high'],
                        'low': data['low'],
                        'close': data['close']
                    })
                    logger.info(f"[INDICATOR_EXPORT] Price snapshot processed: {snapshot_result}")
                except Exception as snap_err:
                    logger.error(f"[INDICATOR_EXPORT] Price snapshot failed: {snap_err}")
            
            cursor.execute("""
                INSERT INTO indicator_export_batches 
                (event_type, batch_number, batch_size, total_signals, payload_json, payload_sha256, is_valid, validation_error)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (event_type, payload_sha256) DO NOTHING
                RETURNING id
            """, (event_type, batch_number, batch_size, total_signals, Json(data), payload_hash, is_valid, validation_error))
            
            result = cursor.fetchone()
            
            if result:
                batch_id = result[0]
                conn.commit()
                logger.info(f"[INDICATOR_EXPORT] ✅ Stored batch_id={batch_id}, signals={len(signals)}")
                
                cursor.close()
                conn.close()
                
                # Auto-import if enabled
                auto_import_enabled = os.environ.get('AUTO_IMPORT_INDICATOR_EXPORT', '').lower() in ['1', 'true', 'yes']
                auto_import_result = None
                
                if auto_import_enabled and is_valid:
                    logger.info(f"[INDICATOR_EXPORT_AUTOIMPORT] Starting auto-import for batch_id={batch_id}, event_type={event_type}")
                    
                    try:
                        if event_type == "ALL_SIGNALS_EXPORT":
                            from services.indicator_export_importer import import_all_signals_export
                            import_result = import_all_signals_export(batch_id)
                        elif event_type in ["INDICATOR_EXPORT_V2", "UNIFIED_SNAPSHOT_V1"]:
                            from services.indicator_export_importer import import_indicator_export_v2
                            import_result = import_indicator_export_v2(batch_id)
                        elif event_type == "MFE_UPDATE_BATCH":
                            # Auto-import MFE batch into confirmed_signals_ledger
                            processed = 0
                            upserted = 0
                            skipped = 0
                            
                            conn_import = psycopg2.connect(DATABASE_URL)
                            cursor_import = conn_import.cursor()
                            
                            for signal in signals:
                                trade_id = signal.get('trade_id')
                                if not trade_id:
                                    skipped += 1
                                    continue
                                
                                # Extract triangle_time_ms
                                triangle_time_ms = signal.get('triangle_time_ms') or signal.get('triangle_time')
                                if not triangle_time_ms:
                                    logger.warning(f"[MFE_IMPORT] missing triangle_time trade_id={trade_id}")
                                    skipped += 1
                                    continue
                                
                                try:
                                    triangle_time_ms = int(triangle_time_ms)
                                except (ValueError, TypeError):
                                    logger.warning(f"[MFE_IMPORT] invalid triangle_time trade_id={trade_id}")
                                    skipped += 1
                                    continue
                                
                                # Parse values (default None to avoid overwriting with zeros)
                                be_mfe_val = None
                                no_be_mfe_val = None
                                mae_val = None
                                
                                try:
                                    if signal.get('be_mfe') is not None:
                                        be_mfe_val = float(signal.get('be_mfe'))
                                except (ValueError, TypeError):
                                    be_mfe_val = None
                                
                                try:
                                    if signal.get('no_be_mfe') is not None:
                                        no_be_mfe_val = float(signal.get('no_be_mfe'))
                                except (ValueError, TypeError):
                                    no_be_mfe_val = None
                                
                                try:
                                    mae_raw = signal.get('mae_global_r') or signal.get('mae')
                                    if mae_raw is not None:
                                        mae_val = float(mae_raw)
                                        if mae_val > 0.0:
                                            mae_val = 0.0
                                except (ValueError, TypeError):
                                    mae_val = None
                                
                                # Upsert
                                symbol_val = signal.get('symbol') or data.get('symbol') or signal.get('exchange') or data.get('exchange') or ''
                                
                                # Canonicalize and reject 'unknown'
                                from services.price_snapshot_processor import canonical_symbol
                                symbol_val = canonical_symbol(symbol_val) if symbol_val else ''
                                if symbol_val.lower() == 'unknown':
                                    symbol_val = ''
                                
                                cursor_import.execute("""
                                    INSERT INTO confirmed_signals_ledger 
                                    (trade_id, triangle_time_ms, be_mfe, no_be_mfe, mae, direction, session, symbol, updated_at, last_seen_batch_id)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s)
                                    ON CONFLICT (trade_id) DO UPDATE SET
                                        triangle_time_ms = COALESCE(EXCLUDED.triangle_time_ms, confirmed_signals_ledger.triangle_time_ms),
                                        be_mfe = COALESCE(EXCLUDED.be_mfe, confirmed_signals_ledger.be_mfe),
                                        no_be_mfe = COALESCE(EXCLUDED.no_be_mfe, confirmed_signals_ledger.no_be_mfe),
                                        mae = COALESCE(EXCLUDED.mae, confirmed_signals_ledger.mae),
                                        direction = COALESCE(EXCLUDED.direction, confirmed_signals_ledger.direction),
                                        session = COALESCE(EXCLUDED.session, confirmed_signals_ledger.session),
                                        symbol = COALESCE(EXCLUDED.symbol, confirmed_signals_ledger.symbol),
                                        updated_at = NOW(),
                                        last_seen_batch_id = EXCLUDED.last_seen_batch_id
                                """, (trade_id, triangle_time_ms, be_mfe_val, no_be_mfe_val, mae_val, 
                                      signal.get('direction'), signal.get('session'), symbol_val, batch_id))
                                
                                processed += 1
                                upserted += 1
                            
                            conn_import.commit()
                            cursor_import.close()
                            conn_import.close()
                            
                            logger.info(f"[INDICATOR_EXPORT_AUTOIMPORT_MFE] ✅ batch_id={batch_id}, processed={processed}, upserted={upserted}, skipped={skipped}")
                            import_result = {'success': True, 'inserted': 0, 'updated': upserted, 'skipped_invalid': skipped}
                        else:
                            import_result = None
                        
                        if import_result:
                            logger.info(f"[INDICATOR_EXPORT_AUTOIMPORT] ✅ batch_id={batch_id}, event_type={event_type}, success={import_result.get('success')}, inserted={import_result.get('inserted', 0)}, updated={import_result.get('updated', 0)}, skipped={import_result.get('skipped_invalid', 0)}")
                            auto_import_result = {
                                'success': import_result.get('success', False),
                                'inserted': import_result.get('inserted', 0),
                                'updated': import_result.get('updated', 0),
                                'skipped_invalid': import_result.get('skipped_invalid', 0)
                            }
                    except Exception as import_error:
                        logger.error(f"[INDICATOR_EXPORT_AUTOIMPORT] ❌ Auto-import failed for batch_id={batch_id}: {import_error}")
                        auto_import_result = {
                            'success': False,
                            'inserted': 0,
                            'updated': 0,
                            'skipped_invalid': 0
                        }
                
                response = {
                    'status': 'success',
                    'batch_id': batch_id,
                    'event_type': event_type,
                    'batch_number': batch_number,
                    'signals_count': len(signals)
                }
                
                if auto_import_result:
                    response['auto_import'] = auto_import_result
                
                return jsonify(response), 200
            else:
                # Duplicate detected
                conn.rollback()
                cursor.close()
                conn.close()
                
                logger.info(f"[INDICATOR_EXPORT] ⚠️  Duplicate batch detected (hash={payload_hash[:8]})")
                return jsonify({
                    'status': 'duplicate',
                    'event_type': event_type,
                    'batch_number': batch_number,
                    'signals_count': len(signals)
                }), 200
                
        except Exception as e:
            logger.error(f"[INDICATOR_EXPORT] ❌ Database error: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/indicator-export/import/<int:batch_id>', methods=['POST'])
    def import_indicator_batch(batch_id):
        """
        Import a specific batch from indicator_export_batches into confirmed_signals_ledger.
        Lightweight route that calls the importer function.
        """
        from services.indicator_export_importer import import_indicator_export_v2
        
        logger.info(f"[INDICATOR_IMPORT_V2] Import requested for batch_id={batch_id}")
        
        try:
            result = import_indicator_export_v2(batch_id)
            
            if result.get('success'):
                logger.info(f"[INDICATOR_IMPORT_V2] ✅ Import complete: {result}")
                return jsonify(result), 200
            else:
                logger.error(f"[INDICATOR_IMPORT_V2] ❌ Import failed: {result}")
                return jsonify(result), 500
                
        except Exception as e:
            logger.error(f"[INDICATOR_IMPORT_V2] ❌ Exception: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'inserted': 0,
                'updated': 0,
                'skipped_invalid': 0
            }), 500
    
    @app.route('/api/all-signals/import/<int:batch_id>', methods=['POST'])
    def import_all_signals_batch(batch_id):
        """
        Import ALL_SIGNALS_EXPORT batch into all_signals_ledger.
        Lightweight route that calls the importer function.
        """
        from services.indicator_export_importer import import_all_signals_export
        
        logger.info(f"[ALL_SIGNALS_IMPORT] Import requested for batch_id={batch_id}")
        
        try:
            result = import_all_signals_export(batch_id)
            
            if result.get('success'):
                logger.info(f"[ALL_SIGNALS_IMPORT] ✅ Import complete: {result}")
                return jsonify(result), 200
            else:
                logger.error(f"[ALL_SIGNALS_IMPORT] ❌ Import failed: {result}")
                return jsonify(result), 500
                
        except Exception as e:
            logger.error(f"[ALL_SIGNALS_IMPORT] ❌ Exception: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'inserted': 0,
                'updated': 0,
                'skipped_invalid': 0
            }), 500
    
    @app.route('/api/indicator-export/import-latest', methods=['POST'])
    def import_latest_indicator_data():
        """
        Import latest valid batches for both INDICATOR_EXPORT_V2 and ALL_SIGNALS_EXPORT.
        Finds most recent valid batch for each type and imports them.
        """
        import os
        import psycopg2
        from services.indicator_export_importer import import_indicator_export_v2, import_all_signals_export
        
        logger.info("[INDICATOR_IMPORT_LATEST] Starting import of latest batches")
        
        try:
            DATABASE_URL = os.environ.get('DATABASE_PUBLIC_URL') or os.environ.get('DATABASE_URL')
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            
            # Find latest INDICATOR_EXPORT_V2 batch
            cursor.execute("""
                SELECT id FROM indicator_export_batches
                WHERE event_type = 'INDICATOR_EXPORT_V2' AND is_valid = true
                ORDER BY received_at DESC
                LIMIT 1
            """)
            confirmed_row = cursor.fetchone()
            confirmed_batch_id = confirmed_row[0] if confirmed_row else None
            
            # Find latest ALL_SIGNALS_EXPORT batch
            cursor.execute("""
                SELECT id FROM indicator_export_batches
                WHERE event_type = 'ALL_SIGNALS_EXPORT' AND is_valid = true
                ORDER BY received_at DESC
                LIMIT 1
            """)
            all_signals_row = cursor.fetchone()
            all_signals_batch_id = all_signals_row[0] if all_signals_row else None
            
            cursor.close()
            conn.close()
            
            logger.info(f"[INDICATOR_IMPORT_LATEST] Found batches: confirmed={confirmed_batch_id}, all_signals={all_signals_batch_id}")
            
            # Import both batches
            confirmed_result = None
            all_signals_result = None
            
            if confirmed_batch_id:
                logger.info(f"[INDICATOR_IMPORT_LATEST] Importing INDICATOR_EXPORT_V2 batch {confirmed_batch_id}")
                confirmed_result = import_indicator_export_v2(confirmed_batch_id)
            
            if all_signals_batch_id:
                logger.info(f"[INDICATOR_IMPORT_LATEST] Importing ALL_SIGNALS_EXPORT batch {all_signals_batch_id}")
                all_signals_result = import_all_signals_export(all_signals_batch_id)
            
            # Build combined response
            response = {
                'success': True,
                'confirmed_signals': {
                    'batch_id': confirmed_batch_id,
                    'result': confirmed_result
                } if confirmed_result else None,
                'all_signals': {
                    'batch_id': all_signals_batch_id,
                    'result': all_signals_result
                } if all_signals_result else None
            }
            
            logger.info(f"[INDICATOR_IMPORT_LATEST] ✅ Import complete: {response}")
            
            return jsonify(response), 200
            
        except Exception as e:
            logger.error(f"[INDICATOR_IMPORT_LATEST] ❌ Exception: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/all-signals/data', methods=['GET'])
    def get_all_signals_data():
        """
        Get All Signals data from all_signals_ledger.
        Returns triangle-canonical data for All Signals tab.
        """
        import os
        import psycopg2
        from psycopg2.extras import RealDictCursor
        from decimal import Decimal
        from datetime import datetime
        from flask import request
        
        # Parse pagination params
        limit = min(request.args.get('limit', 1000, type=int), 5000)
        offset = request.args.get('offset', 0, type=int)
        
        logger.info("[ALL_SIGNALS_DATA] start limit=%s offset=%s", limit, offset)
        
        conn = None
        cursor = None
        
        try:
            DATABASE_URL = os.environ.get('DATABASE_PUBLIC_URL') or os.environ.get('DATABASE_URL')
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get total count
            cursor.execute("SELECT COUNT(*) AS total FROM all_signals_ledger")
            total_row = cursor.fetchone()
            total = total_row['total'] if total_row and 'total' in total_row else 0
            
            # Query all_signals_ledger with pagination, enriching CONFIRMED rows from confirmed_signals_ledger
            cursor.execute("""
                SELECT 
                    a.trade_id,
                    a.triangle_time_ms,
                    a.confirmation_time_ms,
                    a.direction,
                    a.status,
                    a.bars_to_confirm,
                    a.session,
                    COALESCE(c.entry, a.entry_price) AS entry_price,
                    COALESCE(c.stop, a.stop_loss) AS stop_loss,
                    CASE 
                        WHEN c.entry IS NOT NULL AND c.stop IS NOT NULL THEN ABS(c.entry - c.stop)
                        ELSE a.risk_points
                    END AS risk_points,
                    a.htf_daily,
                    a.htf_4h,
                    a.htf_1h,
                    a.htf_15m,
                    a.htf_5m,
                    a.htf_1m,
                    c.be_mfe,
                    c.no_be_mfe,
                    c.mae,
                    c.completed,
                    a.updated_at
                FROM all_signals_ledger a
                LEFT JOIN confirmed_signals_ledger c ON a.trade_id = c.trade_id
                ORDER BY a.triangle_time_ms DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))
            
            rows = cursor.fetchall()
            logger.info("[ALL_SIGNALS_DATA] rows=%d", len(rows))
            
            # Convert to JSON-serializable format
            signals = []
            for row in rows:
                # Convert triangle_time_ms to date and time strings (America/New_York)
                if row['triangle_time_ms']:
                    from zoneinfo import ZoneInfo
                    dt = datetime.fromtimestamp(row['triangle_time_ms'] / 1000, tz=ZoneInfo("America/New_York"))
                    date_str = dt.strftime('%Y-%m-%d')
                    time_str = dt.strftime('%H:%M:%S')
                else:
                    date_str = None
                    time_str = None
                
                signal = {
                    'trade_id': row['trade_id'],
                    'date': date_str,
                    'time': time_str,
                    'triangle_time_ms': row['triangle_time_ms'],
                    'confirmation_time_ms': row['confirmation_time_ms'],
                    'direction': row['direction'],
                    'status': row['status'],
                    'bars_to_confirm': row['bars_to_confirm'],
                    'session': row['session'],
                    'entry': float(row['entry_price']) if row.get('entry_price') is not None else None,
                    'stop': float(row['stop_loss']) if row.get('stop_loss') is not None else None,
                    'risk': float(row['risk_points']) if row.get('risk_points') is not None else None,
                    'htf_daily': row['htf_daily'],
                    'htf_4h': row['htf_4h'],
                    'htf_1h': row['htf_1h'],
                    'htf_15m': row['htf_15m'],
                    'htf_5m': row['htf_5m'],
                    'htf_1m': row['htf_1m'],
                    'be_mfe': float(row['be_mfe']) if row.get('be_mfe') is not None else None,
                    'no_be_mfe': float(row['no_be_mfe']) if row.get('no_be_mfe') is not None else None,
                    'mae': float(row['mae']) if row.get('mae') is not None else None,
                    'completed': row.get('completed'),
                    'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
                }
                signals.append(signal)
            
            # Get freshness metrics (reuse same cursor, connection still open)
            cursor.execute("""
                SELECT 
                    MAX(triangle_time_ms) as max_triangle_time_ms,
                    MAX(updated_at) as max_updated_at
                FROM all_signals_ledger
            """)
            freshness = cursor.fetchone()
            max_triangle_time_ms = freshness[0] if freshness else None
            max_updated_at = freshness[1].isoformat() if freshness and freshness[1] else None
            
            logger.info(f"[ALL_SIGNALS_DATA] ✅ Returned {len(signals)} signals (total={total}, limit={limit}, offset={offset})")
            
            return jsonify({
                'success': True,
                'signals': signals,
                'count': len(signals),
                'total': total,
                'limit': limit,
                'offset': offset,
                'max_triangle_time_ms': max_triangle_time_ms,
                'max_updated_at': max_updated_at,
                'source_table': 'all_signals_ledger',
                'handler_marker': 'ALL_SIGNALS_DATA_FIX_20251224_A'
            }), 200
            
        except Exception as e:
            logger.exception("[ALL_SIGNALS_DATA] ❌ Error")
            return jsonify({
                'success': False,
                'error': str(e),
                'signals': [],
                'count': 0
            }), 500
            
        finally:
            # Always close cursor and connection
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @app.route('/api/all-signals/stats', methods=['GET'])
    def get_all_signals_stats():
        """
        Get lightweight stats for all_signals_ledger.
        Returns: total count, max triangle_time_ms, max updated_at.
        """
        import os
        import psycopg2
        
        logger.info("[ALL_SIGNALS_STATS] Fetching stats")
        
        try:
            DATABASE_URL = os.environ.get('DATABASE_PUBLIC_URL') or os.environ.get('DATABASE_URL')
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    MAX(triangle_time_ms) as max_triangle_time_ms,
                    MAX(updated_at) as max_updated_at
                FROM all_signals_ledger
            """)
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if row:
                total, max_triangle_time_ms, max_updated_at = row
                return jsonify({
                    'success': True,
                    'total': total or 0,
                    'max_triangle_time_ms': max_triangle_time_ms,
                    'max_updated_at': max_updated_at.isoformat() if max_updated_at else None
                }), 200
            else:
                return jsonify({
                    'success': True,
                    'total': 0,
                    'max_triangle_time_ms': None,
                    'max_updated_at': None
                }), 200
                
        except Exception as e:
            logger.error(f"[ALL_SIGNALS_STATS] ❌ Error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/all-signals/cancelled', methods=['GET'])
    def get_cancelled_signals():
        """Get cancelled signals from all_signals_ledger."""
        import os
        import psycopg2
        from psycopg2.extras import RealDictCursor
        from datetime import datetime
        
        logger.info("[CANCELLED_SIGNALS] Fetching cancelled signals")
        
        try:
            DATABASE_URL = os.environ.get('DATABASE_PUBLIC_URL') or os.environ.get('DATABASE_URL')
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT 
                    trade_id, triangle_time_ms, direction, session,
                    htf_daily, htf_4h, htf_1h, htf_15m, htf_5m, htf_1m,
                    updated_at
                FROM all_signals_ledger
                WHERE status = 'CANCELLED'
                ORDER BY triangle_time_ms DESC
                LIMIT 500
            """)
            
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            signals = []
            for row in rows:
                dt = datetime.fromtimestamp(row['triangle_time_ms'] / 1000, tz=ZoneInfo("America/New_York")) if row['triangle_time_ms'] else None
                signals.append({
                    'trade_id': row['trade_id'],
                    'date': dt.strftime('%Y-%m-%d') if dt else None,
                    'time': dt.strftime('%H:%M:%S') if dt else None,
                    'direction': row['direction'],
                    'session': row['session'],
                    'htf_daily': row['htf_daily'],
                    'htf_4h': row['htf_4h'],
                    'htf_1h': row['htf_1h'],
                    'htf_15m': row['htf_15m'],
                    'htf_5m': row['htf_5m'],
                    'htf_1m': row['htf_1m']
                })
            
            logger.info(f"[CANCELLED_SIGNALS] ✅ Returned {len(signals)} cancelled signals")
            return jsonify({'success': True, 'signals': signals, 'count': len(signals)}), 200
            
        except Exception as e:
            logger.error(f"[CANCELLED_SIGNALS] ❌ Error: {e}")
            return jsonify({'success': False, 'error': str(e), 'signals': [], 'count': 0}), 500
    
    @app.route('/api/all-signals/confirmed', methods=['GET'])
    def get_confirmed_signals():
        """Get confirmed signals with MFE/MAE data (LEFT JOIN to preserve all confirmed)."""
        import os
        import psycopg2
        from psycopg2.extras import RealDictCursor
        from datetime import datetime
        
        logger.info("[CONFIRMED_SIGNALS] Fetching confirmed signals")
        
        try:
            DATABASE_URL = os.environ.get('DATABASE_PUBLIC_URL') or os.environ.get('DATABASE_URL')
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT 
                    a.trade_id,
                    a.triangle_time_ms,
                    a.confirmation_time_ms,
                    a.direction,
                    a.status,
                    a.session,
                    COALESCE(c.entry, a.entry_price) AS entry_price_out,
                    COALESCE(c.stop, a.stop_loss) AS stop_loss_out,
                    COALESCE(a.risk_points, CASE WHEN c.entry IS NOT NULL AND c.stop IS NOT NULL THEN ABS(c.entry - c.stop) ELSE NULL END) AS risk_points_out,
                    c.be_mfe,
                    c.no_be_mfe,
                    c.mae,
                    c.completed,
                    a.updated_at
                FROM all_signals_ledger a
                LEFT JOIN confirmed_signals_ledger c ON a.trade_id = c.trade_id
                WHERE a.status = 'CONFIRMED'
                ORDER BY a.triangle_time_ms DESC
                LIMIT 1000
            """)
            
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            signals = []
            for row in rows:
                dt = datetime.fromtimestamp(row['triangle_time_ms'] / 1000, tz=ZoneInfo("America/New_York")) if row['triangle_time_ms'] else None
                signals.append({
                    'trade_id': row['trade_id'],
                    'date': dt.strftime('%Y-%m-%d') if dt else None,
                    'time': dt.strftime('%H:%M:%S') if dt else None,
                    'direction': row['direction'],
                    'session': row['session'],
                    'entry': float(row['entry_price_out']) if row['entry_price_out'] is not None else None,
                    'stop': float(row['stop_loss_out']) if row['stop_loss_out'] is not None else None,
                    'risk': float(row['risk_points_out']) if row['risk_points_out'] is not None else None,
                    'be_mfe': float(row['be_mfe']) if row['be_mfe'] else None,
                    'no_be_mfe': float(row['no_be_mfe']) if row['no_be_mfe'] else None,
                    'mae': float(row['mae']) if row['mae'] else None,
                    'completed': row['completed']
                })
            
            logger.info(f"[CONFIRMED_SIGNALS] ✅ Returned {len(signals)} confirmed signals")
            return jsonify({'success': True, 'signals': signals, 'count': len(signals)}), 200
            
        except Exception as e:
            logger.error(f"[CONFIRMED_SIGNALS] ❌ Error: {e}")
            return jsonify({'success': False, 'error': str(e), 'signals': [], 'count': 0}), 500
    
    @app.route('/api/all-signals/completed', methods=['GET'])
    def get_completed_signals():
        """Get completed signals (status=COMPLETED or confirmed_signals.completed=true)."""
        import os
        import psycopg2
        from psycopg2.extras import RealDictCursor
        from datetime import datetime
        
        logger.info("[COMPLETED_SIGNALS] Fetching completed signals")
        
        try:
            DATABASE_URL = os.environ.get('DATABASE_PUBLIC_URL') or os.environ.get('DATABASE_URL')
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT 
                    a.trade_id,
                    a.triangle_time_ms,
                    a.confirmation_time_ms,
                    a.direction,
                    a.status,
                    a.session,
                    COALESCE(c.entry, a.entry_price) AS entry_price_out,
                    COALESCE(c.stop, a.stop_loss) AS stop_loss_out,
                    COALESCE(a.risk_points, CASE WHEN c.entry IS NOT NULL AND c.stop IS NOT NULL THEN ABS(c.entry - c.stop) ELSE NULL END) AS risk_points_out,
                    c.be_mfe,
                    c.no_be_mfe,
                    c.mae,
                    c.completed,
                    a.updated_at
                FROM all_signals_ledger a
                LEFT JOIN confirmed_signals_ledger c ON a.trade_id = c.trade_id
                WHERE a.status = 'COMPLETED' OR c.completed = true
                ORDER BY a.triangle_time_ms DESC
                LIMIT 1000
            """)
            
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            signals = []
            for row in rows:
                dt = datetime.fromtimestamp(row['triangle_time_ms'] / 1000, tz=ZoneInfo("America/New_York")) if row['triangle_time_ms'] else None
                signals.append({
                    'trade_id': row['trade_id'],
                    'date': dt.strftime('%Y-%m-%d') if dt else None,
                    'time': dt.strftime('%H:%M:%S') if dt else None,
                    'direction': row['direction'],
                    'session': row['session'],
                    'entry': float(row['entry_price_out']) if row['entry_price_out'] is not None else None,
                    'stop': float(row['stop_loss_out']) if row['stop_loss_out'] is not None else None,
                    'risk': float(row['risk_points_out']) if row['risk_points_out'] is not None else None,
                    'be_mfe': float(row['be_mfe']) if row['be_mfe'] else None,
                    'no_be_mfe': float(row['no_be_mfe']) if row['no_be_mfe'] else None,
                    'mae': float(row['mae']) if row['mae'] else None,
                    'completed': row['completed']
                })
            
            logger.info(f"[COMPLETED_SIGNALS] ✅ Returned {len(signals)} completed signals")
            return jsonify({'success': True, 'signals': signals, 'count': len(signals)}), 200
            
        except Exception as e:
            logger.error(f"[COMPLETED_SIGNALS] ❌ Error: {e}")
            return jsonify({'success': False, 'error': str(e), 'signals': [], 'count': 0}), 500
    
    @app.route('/api/data-quality/indicator-health', methods=['GET'])
    def get_indicator_health():
        """Return indicator data flow health summary with v2 ledgers + price snapshots"""
        import os
        import psycopg2
        from psycopg2.extras import RealDictCursor
        from datetime import datetime, timezone
        
        logger.info("[DQ_HEALTH] Fetching indicator health")
        
        try:
            DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('DATABASE_PUBLIC_URL')
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            now = datetime.now(timezone.utc)
            
            # Latest batch timestamps
            cursor.execute("SELECT received_at FROM indicator_export_batches WHERE event_type='UNIFIED_SNAPSHOT_V1' AND is_valid=true ORDER BY received_at DESC LIMIT 1")
            unified_row = cursor.fetchone()
            latest_unified = unified_row['received_at'] if unified_row else None
            
            cursor.execute("SELECT received_at FROM indicator_export_batches WHERE event_type='MFE_UPDATE_BATCH' AND is_valid=true ORDER BY received_at DESC LIMIT 1")
            mfe_row = cursor.fetchone()
            latest_mfe = mfe_row['received_at'] if mfe_row else None
            
            cursor.execute("SELECT received_at FROM indicator_export_batches WHERE event_type='INDICATOR_EXPORT_V2' AND is_valid=true ORDER BY received_at DESC LIMIT 1")
            v2_row = cursor.fetchone()
            latest_v2 = v2_row['received_at'] if v2_row else None
            
            # Price snapshots
            cursor.execute("SELECT MAX(received_at) as max_ts, COUNT(*) as cnt FROM price_snapshots WHERE received_at >= NOW() - INTERVAL '60 minutes'")
            price_row = cursor.fetchone()
            latest_price = price_row['max_ts'] if price_row else None
            count_price_60m = price_row['cnt'] if price_row else 0
            
            # Recent counts (60 minutes)
            cursor.execute("SELECT COUNT(*) as cnt FROM indicator_export_batches WHERE event_type='UNIFIED_SNAPSHOT_V1' AND is_valid=true AND received_at >= NOW() - INTERVAL '60 minutes'")
            unified_count_row = cursor.fetchone()
            count_unified_60m = unified_count_row['cnt'] if unified_count_row else 0
            
            cursor.execute("SELECT COUNT(*) as cnt FROM indicator_export_batches WHERE event_type='MFE_UPDATE_BATCH' AND is_valid=true AND received_at >= NOW() - INTERVAL '60 minutes'")
            mfe_count_row = cursor.fetchone()
            count_mfe_60m = mfe_count_row['cnt'] if mfe_count_row else 0
            
            # Ledger freshness
            cursor.execute("SELECT MAX(updated_at) as max_ts FROM confirmed_signals_ledger")
            conf_ledger_row = cursor.fetchone()
            max_conf_ledger = conf_ledger_row['max_ts'] if conf_ledger_row else None
            
            cursor.close()
            conn.close()
            
            # Compute lag seconds
            def compute_lag(ts):
                if ts is None:
                    return None
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                return int((now - ts).total_seconds())
            
            unified_lag = compute_lag(latest_unified)
            mfe_lag = compute_lag(latest_mfe)
            v2_lag = compute_lag(latest_v2)
            price_lag = compute_lag(latest_price)
            conf_lag = compute_lag(max_conf_ledger)
            
            # Traffic light logic - GREEN if ANY stream is fresh
            active_lags = [l for l in [unified_lag, mfe_lag, v2_lag, price_lag, conf_lag] if l is not None]
            
            if not active_lags:
                traffic_light = "RED"
            elif min(active_lags) <= 180:
                traffic_light = "GREEN"
            elif min(active_lags) <= 600:
                traffic_light = "AMBER"
            else:
                traffic_light = "RED"
            
            logger.info(f"[DQ_HEALTH] ✅ Traffic light: {traffic_light}")
            
            return jsonify({
                'success': True,
                'now': now.isoformat(),
                'traffic_light': traffic_light,
                'streams': {
                    'unified_snapshot_v1': {
                        'last_received_at': latest_unified.isoformat() if latest_unified else None,
                        'lag_seconds': unified_lag,
                        'count_60m': count_unified_60m
                    },
                    'mfe_update_batch': {
                        'last_received_at': latest_mfe.isoformat() if latest_mfe else None,
                        'lag_seconds': mfe_lag,
                        'count_60m': count_mfe_60m
                    },
                    'indicator_export_v2': {
                        'last_received_at': latest_v2.isoformat() if latest_v2 else None,
                        'lag_seconds': v2_lag
                    },
                    'price_snapshots': {
                        'last_received_at': latest_price.isoformat() if latest_price else None,
                        'lag_seconds': price_lag,
                        'count_60m': count_price_60m
                    }
                },
                'ledgers': {
                    'confirmed_signals_ledger': {
                        'max_updated_at': max_conf_ledger.isoformat() if max_conf_ledger else None,
                        'lag_seconds': conf_lag
                    }
                }
            }), 200
            
        except Exception as e:
            logger.error(f"[DQ_HEALTH] ❌ Error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/data-quality/reconcile-indicator', methods=['POST'])
    def reconcile_indicator_data():
        """
        Run indicator reconciliation for a specific date (default today).
        Compares canonical tables and flags issues.
        """
        from flask import request
        from services.indicator_reconciliation import run_indicator_reconciliation
        
        # Get optional date parameter
        data = request.get_json() if request.is_json else {}
        date_yyyymmdd = data.get('date') if data else None
        
        logger.info(f"[RECONCILE_INDICATOR] Reconciliation requested for date={date_yyyymmdd or 'today'}")
        
        try:
            result = run_indicator_reconciliation(date_yyyymmdd)
            
            if result.get('success'):
                logger.info(f"[RECONCILE_INDICATOR] ✅ Reconciliation complete: {result}")
                return jsonify(result), 200
            else:
                logger.error(f"[RECONCILE_INDICATOR] ❌ Reconciliation failed: {result}")
                return jsonify(result), 500
                
        except Exception as e:
            logger.error(f"[RECONCILE_INDICATOR] ❌ Exception: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'total_signals': 0,
                'issues': {}
            }), 500
    
    @app.route('/api/indicator-export/batches', methods=['GET'])
    def get_indicator_batches():
        """Get list of indicator export batches."""
        import os
        import psycopg2
        from psycopg2.extras import RealDictCursor
        from flask import request
        
        limit = request.args.get('limit', 20, type=int)
        
        logger.info(f"[INDICATOR_BATCHES] Fetching batches (limit={limit})")
        
        try:
            DATABASE_URL = os.environ.get('DATABASE_PUBLIC_URL') or os.environ.get('DATABASE_URL')
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT 
                    id, received_at, event_type, batch_number, batch_size, 
                    total_signals, is_valid, validation_error
                FROM indicator_export_batches
                ORDER BY received_at DESC
                LIMIT %s
            """, (limit,))
            
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            batches = []
            for row in rows:
                batches.append({
                    'id': row['id'],
                    'received_at': row['received_at'].isoformat() if row['received_at'] else None,
                    'event_type': row['event_type'],
                    'batch_number': row['batch_number'],
                    'batch_size': row['batch_size'],
                    'total_signals': row['total_signals'],
                    'is_valid': row['is_valid'],
                    'validation_error': row['validation_error']
                })
            
            logger.info(f"[INDICATOR_BATCHES] ✅ Returned {len(batches)} batches")
            return jsonify({'success': True, 'batches': batches, 'count': len(batches)}), 200
            
        except Exception as e:
            logger.error(f"[INDICATOR_BATCHES] ❌ Error: {e}")
            return jsonify({'success': False, 'error': str(e), 'batches': [], 'count': 0}), 500
    
    @app.route('/api/indicator-export/debug/batch/<int:batch_id>', methods=['GET'])
    def debug_batch_payload(batch_id):
        """Inspect raw payload of a specific batch for debugging."""
        import os
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        logger.info(f"[INDICATOR_EXPORT_DEBUG_BATCH] Inspecting batch_id={batch_id}")
        
        try:
            DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('DATABASE_PUBLIC_URL')
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT id, received_at, event_type, is_valid, validation_error, payload_json
                FROM indicator_export_batches
                WHERE id = %s
                LIMIT 1
            """, (batch_id,))
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not row:
                return jsonify({'success': False, 'error': 'not_found'}), 404
            
            payload = row['payload_json'] or {}
            signals_raw = payload.get('signals')
            
            # Determine signals type and preview
            signals_type = type(signals_raw).__name__
            signals_preview = None
            
            if isinstance(signals_raw, list):
                signals_preview = signals_raw[0] if len(signals_raw) > 0 else None
            elif isinstance(signals_raw, dict):
                signals_preview = signals_raw
            elif isinstance(signals_raw, str):
                signals_preview = signals_raw[:200]
            
            logger.info(f"[INDICATOR_EXPORT_DEBUG_BATCH] batch_id={batch_id}, signals_type={signals_type}")
            
            return jsonify({
                'success': True,
                'id': row['id'],
                'received_at': row['received_at'].isoformat() if row['received_at'] else None,
                'event_type': row['event_type'],
                'is_valid': row['is_valid'],
                'validation_error': row['validation_error'],
                'signals_type': signals_type,
                'signals_preview': signals_preview,
                'payload_keys': list(payload.keys())
            }), 200
            
        except Exception as e:
            logger.error(f"[INDICATOR_EXPORT_DEBUG_BATCH] ❌ Exception: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/indicator-live/debug/last-valid-mfe', methods=['GET'])
    def debug_last_valid_mfe():
        """Get the latest valid MFE_UPDATE_BATCH for quick verification."""
        import os
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        logger.info("[LIVE_MFE_DEBUG] Fetching last valid MFE batch")
        
        try:
            DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('DATABASE_PUBLIC_URL')
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT id, received_at, batch_size, validation_error, payload_json
                FROM indicator_export_batches
                WHERE event_type = 'MFE_UPDATE_BATCH' AND is_valid = true
                ORDER BY received_at DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not row:
                return jsonify({'success': False, 'error': 'no_valid_mfe_batches'}), 404
            
            payload = row['payload_json'] or {}
            signals = payload.get('signals', [])
            signal_preview = signals[0] if isinstance(signals, list) and len(signals) > 0 else None
            
            logger.info(f"[LIVE_MFE_DEBUG] Found batch_id={row['id']}, batch_size={row['batch_size']}")
            
            return jsonify({
                'success': True,
                'id': row['id'],
                'received_at': row['received_at'].isoformat() if row['received_at'] else None,
                'batch_size': row['batch_size'],
                'validation_error': row['validation_error'],
                'signal_preview': signal_preview
            }), 200
            
        except Exception as e:
            logger.error(f"[LIVE_MFE_DEBUG] ❌ Exception: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/indicator-export/import-confirmed-run', methods=['POST'])
    def import_confirmed_run():
        """Import all batches for the most recent INDICATOR_EXPORT_V2 export run."""
        import os
        import psycopg2
        from services.indicator_export_importer import import_indicator_export_v2
        
        logger.info("[INDICATOR_IMPORT_RUN] Starting import of confirmed signals run")
        
        try:
            DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('DATABASE_PUBLIC_URL')
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            
            # Find latest batch number
            cursor.execute("""
                SELECT batch_number FROM indicator_export_batches
                WHERE event_type='INDICATOR_EXPORT_V2' AND is_valid=true
                ORDER BY received_at DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            if not row:
                cursor.close()
                conn.close()
                logger.warning("[INDICATOR_IMPORT_RUN] No valid batches found")
                return jsonify({'success': False, 'error': 'no_batches'}), 200
            
            latest_batch_number = row[0]
            logger.info(f"[INDICATOR_IMPORT_RUN] Latest batch_number={latest_batch_number}")
            
            # Get all batches for this run
            cursor.execute("""
                SELECT id, batch_number FROM indicator_export_batches
                WHERE event_type='INDICATOR_EXPORT_V2'
                  AND is_valid=true
                  AND batch_number <= %s
                ORDER BY batch_number ASC, received_at ASC
            """, (latest_batch_number,))
            
            batches = cursor.fetchall()
            cursor.close()
            conn.close()
            
            logger.info(f"[INDICATOR_IMPORT_RUN] Found {len(batches)} batches to import")
            
            # Import each batch
            inserted_total = 0
            updated_total = 0
            skipped_invalid_total = 0
            batches_imported = 0
            
            for batch_id, batch_num in batches:
                logger.info(f"[INDICATOR_IMPORT_RUN] Importing batch {batch_num} (id={batch_id})")
                result = import_indicator_export_v2(batch_id)
                
                if result.get('success'):
                    inserted_total += result.get('inserted', 0)
                    updated_total += result.get('updated', 0)
                    skipped_invalid_total += result.get('skipped_invalid', 0)
                    batches_imported += 1
            
            logger.info(f"[INDICATOR_IMPORT_RUN] ✅ Complete: batches={batches_imported}, inserted={inserted_total}, updated={updated_total}")
            
            return jsonify({
                'success': True,
                'latest_batch_number': latest_batch_number,
                'batches_imported': batches_imported,
                'inserted': inserted_total,
                'updated': updated_total,
                'skipped_invalid': skipped_invalid_total
            }), 200
            
        except Exception as e:
            logger.error(f"[INDICATOR_IMPORT_RUN] ❌ Exception: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/indicator-export/import-all-confirmed-batches', methods=['POST'])
    def import_all_confirmed_batches():
        """Import all received INDICATOR_EXPORT_V2 batches by ID."""
        import os
        import psycopg2
        from services.indicator_export_importer import import_indicator_export_v2
        
        logger.info("[INDICATOR_IMPORT_ALL_CONFIRMED] Starting import of all confirmed batches")
        
        try:
            DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('DATABASE_PUBLIC_URL')
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id FROM indicator_export_batches
                WHERE event_type='INDICATOR_EXPORT_V2' AND is_valid=true
                ORDER BY id ASC
            """)
            
            batch_ids = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            
            logger.info(f"[INDICATOR_IMPORT_ALL_CONFIRMED] Found {len(batch_ids)} batches to import")
            
            # Create single connection for all imports
            import_conn = psycopg2.connect(DATABASE_URL)
            
            inserted_total = 0
            updated_total = 0
            skipped_invalid_total = 0
            batches_imported = 0
            failed_batches = []
            
            for batch_id in batch_ids:
                logger.info(f"[INDICATOR_IMPORT_ALL_CONFIRMED] Importing batch id={batch_id}")
                
                try:
                    result = import_indicator_export_v2(batch_id, conn=import_conn)
                    
                    if result.get('success'):
                        inserted_total += result.get('inserted', 0)
                        updated_total += result.get('updated', 0)
                        skipped_invalid_total += result.get('skipped_invalid', 0)
                        batches_imported += 1
                    else:
                        failed_batches.append(batch_id)
                except Exception as batch_error:
                    logger.error(f"[INDICATOR_IMPORT_ALL_CONFIRMED] Batch {batch_id} exception: {batch_error}")
                    failed_batches.append(batch_id)
            
            import_conn.close()
            
            if failed_batches:
                logger.warning(f"[INDICATOR_IMPORT_ALL_CONFIRMED] ⚠️  {len(failed_batches)} batches failed")
            
            logger.info(f"[INDICATOR_IMPORT_ALL_CONFIRMED] ✅ Complete: batches={batches_imported}, inserted={inserted_total}, updated={updated_total}")
            
            return jsonify({
                'success': True,
                'batches_imported': batches_imported,
                'inserted': inserted_total,
                'updated': updated_total,
                'skipped_invalid': skipped_invalid_total,
                'failed_batches': failed_batches,
                'failed_count': len(failed_batches)
            }), 200
            
        except Exception as e:
            logger.error(f"[INDICATOR_IMPORT_ALL_CONFIRMED] ❌ Exception: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/indicator-export/import-all-all-signals-batches', methods=['POST'])
    def import_all_all_signals_batches():
        """Import all received ALL_SIGNALS_EXPORT batches by ID."""
        import os
        import psycopg2
        from services.indicator_export_importer import import_all_signals_export
        
        logger.info("[ALL_SIGNALS_IMPORT_ALL] Starting import of all ALL_SIGNALS batches")
        
        try:
            DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('DATABASE_PUBLIC_URL')
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id FROM indicator_export_batches
                WHERE event_type='ALL_SIGNALS_EXPORT' AND is_valid=true
                ORDER BY id ASC
            """)
            
            batch_ids = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            
            logger.info(f"[ALL_SIGNALS_IMPORT_ALL] Found {len(batch_ids)} batches to import")
            
            inserted_total = 0
            updated_total = 0
            skipped_invalid_total = 0
            batches_imported = 0
            failed_batches = []
            
            for batch_id in batch_ids:
                logger.info(f"[ALL_SIGNALS_IMPORT_ALL] Importing batch id={batch_id}")
                
                try:
                    result = import_all_signals_export(batch_id)
                    
                    if result.get('success'):
                        inserted_total += result.get('inserted', 0)
                        updated_total += result.get('updated', 0)
                        skipped_invalid_total += result.get('skipped_invalid', 0)
                        batches_imported += 1
                    else:
                        failed_batches.append(batch_id)
                except Exception as batch_error:
                    logger.error(f"[ALL_SIGNALS_IMPORT_ALL] Batch {batch_id} exception: {batch_error}")
                    failed_batches.append(batch_id)
            
            if failed_batches:
                logger.warning(f"[ALL_SIGNALS_IMPORT_ALL] ⚠️  {len(failed_batches)} batches failed")
            
            logger.info(f"[ALL_SIGNALS_IMPORT_ALL] ✅ Complete: batches={batches_imported}, inserted={inserted_total}, updated={updated_total}")
            
            return jsonify({
                'success': True,
                'batches_imported': batches_imported,
                'inserted': inserted_total,
                'updated': updated_total,
                'skipped_invalid': skipped_invalid_total,
                'failed_batches': failed_batches,
                'failed_count': len(failed_batches)
            }), 200
            
        except Exception as e:
            logger.error(f"[ALL_SIGNALS_IMPORT_ALL] ❌ Exception: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/data-quality/missing-confirmed', methods=['GET'])
    def get_missing_confirmed():
        """Get list of CONFIRMED trades missing from confirmed_signals_ledger for a date."""
        import os
        import psycopg2
        from flask import request
        from datetime import datetime
        from zoneinfo import ZoneInfo
        
        date_param = request.args.get('date')
        if not date_param:
            return jsonify({'success': False, 'error': 'date parameter required (YYYYMMDD)'}), 400
        
        try:
            target_date = datetime.strptime(date_param, '%Y%m%d').date()
        except ValueError:
            return jsonify({'success': False, 'error': 'invalid date format (use YYYYMMDD)'}), 400
        
        logger.info(f"[DQ_MISSING_CONFIRMED] Checking missing confirmed for date={date_param}")
        
        try:
            DATABASE_URL = os.environ.get('DATABASE_PUBLIC_URL') or os.environ.get('DATABASE_URL')
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            
            # Convert date to NY timezone ms range
            tz = ZoneInfo("America/New_York")
            start_dt = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0, tzinfo=tz)
            end_dt = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59, 999999, tzinfo=tz)
            start_ms = int(start_dt.timestamp() * 1000)
            end_ms = int(end_dt.timestamp() * 1000)
            
            cursor.execute("""
                SELECT a.trade_id
                FROM all_signals_ledger a
                LEFT JOIN confirmed_signals_ledger c ON a.trade_id = c.trade_id
                WHERE a.status = 'CONFIRMED'
                  AND a.triangle_time_ms BETWEEN %s AND %s
                  AND c.trade_id IS NULL
                ORDER BY a.triangle_time_ms ASC
            """, (start_ms, end_ms))
            
            missing_trade_ids = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            
            logger.info(f"[DQ_MISSING_CONFIRMED] Found {len(missing_trade_ids)} missing confirmed trades")
            
            return jsonify({
                'success': True,
                'date': date_param,
                'missing_count': len(missing_trade_ids),
                'missing_trade_ids': missing_trade_ids
            }), 200
            
        except Exception as e:
            logger.error(f"[DQ_MISSING_CONFIRMED] ❌ Exception: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/indicator-export/debug/find-trade', methods=['GET'])
    def debug_find_trade():
        """Search raw batches for a trade_id in INDICATOR_EXPORT_V2 signals."""
        import os
        import psycopg2
        from flask import request
        
        trade_id = request.args.get('trade_id')
        if not trade_id:
            return jsonify({'success': False, 'error': 'trade_id parameter required'}), 400
        
        logger.info(f"[INDICATOR_DEBUG_FIND_TRADE] Searching for trade_id={trade_id}")
        
        try:
            DATABASE_URL = os.environ.get('DATABASE_PUBLIC_URL') or os.environ.get('DATABASE_URL')
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            
            # Find batches containing this trade_id
            cursor.execute("""
                SELECT b.id, b.batch_number, b.received_at
                FROM indicator_export_batches b
                WHERE b.event_type = 'INDICATOR_EXPORT_V2'
                  AND b.is_valid = true
                  AND EXISTS (
                    SELECT 1
                    FROM jsonb_array_elements(b.payload_json->'signals') s
                    WHERE s->>'trade_id' = %s
                  )
                ORDER BY b.batch_number ASC, b.received_at ASC
            """, (trade_id,))
            
            found_batches = []
            for row in cursor.fetchall():
                found_batches.append({
                    'id': row[0],
                    'batch_number': row[1],
                    'received_at': row[2].isoformat() if row[2] else None
                })
            
            # Get example signal
            cursor.execute("""
                SELECT s
                FROM indicator_export_batches b,
                     LATERAL jsonb_array_elements(b.payload_json->'signals') s
                WHERE b.event_type = 'INDICATOR_EXPORT_V2'
                  AND b.is_valid = true
                  AND s->>'trade_id' = %s
                ORDER BY b.batch_number ASC, b.received_at ASC
                LIMIT 1
            """, (trade_id,))
            
            example_row = cursor.fetchone()
            example_signal = example_row[0] if example_row else None
            
            cursor.close()
            conn.close()
            
            logger.info(f"[INDICATOR_DEBUG_FIND_TRADE] Found in {len(found_batches)} batches")
            
            return jsonify({
                'success': True,
                'trade_id': trade_id,
                'found_count': len(found_batches),
                'found_batches': found_batches,
                'example_signal': example_signal
            }), 200
            
        except Exception as e:
            logger.error(f"[INDICATOR_DEBUG_FIND_TRADE] ❌ Exception: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/indicator-live/debug/find-mfe-trade', methods=['GET'])
    def debug_find_mfe_trade():
        """Find which MFE_UPDATE_BATCH batches contain a specific trade_id."""
        import os
        import psycopg2
        from psycopg2.extras import RealDictCursor
        from flask import request
        
        trade_id = request.args.get('trade_id')
        if not trade_id:
            return jsonify({'success': False, 'error': 'missing_trade_id'}), 400
        
        logger.info(f"[LIVE_MFE_DEBUG] Searching for trade_id: {trade_id}")
        
        try:
            DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('DATABASE_PUBLIC_URL')
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Search last 300 MFE_UPDATE_BATCH batches
            cursor.execute("""
                SELECT id, received_at, batch_size, payload_json
                FROM indicator_export_batches
                WHERE event_type = 'MFE_UPDATE_BATCH' AND is_valid = true
                ORDER BY received_at DESC
                LIMIT 300
            """)
            
            rows = cursor.fetchall()
            found_batches = []
            example_signal = None
            
            for row in rows:
                payload = row['payload_json']
                if payload and 'signals' in payload:
                    signals = payload.get('signals', [])
                    for sig in signals:
                        if sig.get('trade_id') == trade_id:
                            found_batches.append({
                                'id': row['id'],
                                'received_at': row['received_at'].isoformat() if row['received_at'] else None,
                                'batch_size': row['batch_size']
                            })
                            if example_signal is None:
                                example_signal = sig
                            break
            
            cursor.close()
            conn.close()
            
            logger.info(f"[LIVE_MFE_DEBUG] Found {len(found_batches)} batches containing {trade_id}")
            
            return jsonify({
                'success': True,
                'trade_id': trade_id,
                'found_count': len(found_batches),
                'found_batches': found_batches,
                'example_signal': example_signal
            }), 200
            
        except Exception as e:
            logger.error(f"[LIVE_MFE_DEBUG] ❌ Exception: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/indicator-live/mfe-batch', methods=['POST'])
    def live_mfe_batch():
        """Receive live MFE/MAE updates for active trades."""
        import os
        import json
        import hashlib
        import psycopg2
        from psycopg2.extras import Json
        from flask import request
        
        logger.info("[LIVE_MFE_BATCH] Received request")
        
        # Auth check
        expected_token = os.environ.get('INDICATOR_EXPORT_TOKEN')
        if expected_token:
            header_token = request.headers.get('X-Indicator-Token')
            query_token = request.args.get('token')
            
            if not (header_token == expected_token or query_token == expected_token):
                logger.warning("[LIVE_MFE_BATCH] ❌ Unauthorized")
                return jsonify({'success': False, 'error': 'unauthorized'}), 401
        
        # Parse JSON
        try:
            data = request.get_json(force=True)
        except Exception as e:
            logger.error(f"[LIVE_MFE_BATCH] Invalid JSON: {e}")
            return jsonify({'success': False, 'error': 'Invalid JSON'}), 400
        
        # Validate
        event_type = data.get('event_type')
        signals = data.get('signals', [])
        
        is_valid = event_type == "MFE_UPDATE_BATCH" and isinstance(signals, list)
        validation_error = None if is_valid else "Invalid event_type or signals not array"
        
        # Compute hash
        payload_str = json.dumps(data, sort_keys=True)
        payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()
        
        logger.info(f"[LIVE_MFE_BATCH] event_type={event_type}, signals={len(signals)}, hash={payload_hash[:8]}")
        
        # Store raw batch
        try:
            DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('DATABASE_PUBLIC_URL')
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO indicator_export_batches 
                (event_type, batch_number, batch_size, total_signals, payload_json, payload_sha256, is_valid, validation_error)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (event_type, payload_sha256) DO NOTHING
                RETURNING id
            """, ("MFE_UPDATE_BATCH", None, len(signals), None, Json(data), payload_hash, is_valid, validation_error))
            
            result = cursor.fetchone()
            batch_status = "ok"
            
            if not result:
                # Duplicate batch - fetch existing batch_id and continue processing
                logger.info(f"[LIVE_MFE_BATCH] ⚠️  Duplicate batch detected, fetching existing batch_id")
                cursor.execute("""
                    SELECT id FROM indicator_export_batches 
                    WHERE event_type = %s AND payload_sha256 = %s 
                    ORDER BY received_at DESC LIMIT 1
                """, ("MFE_UPDATE_BATCH", payload_hash))
                existing = cursor.fetchone()
                batch_id = existing[0] if existing else None
                batch_status = "duplicate_processed"
                logger.info(f"[LIVE_MFE_BATCH] Fetched existing batch_id={batch_id}, continuing to process signals")
            else:
                batch_id = result[0]
                conn.commit()
                logger.info(f"[LIVE_MFE_BATCH] ✅ Stored new batch_id={batch_id}")
            
            # If invalid, return early without processing
            if not is_valid:
                cursor.close()
                conn.close()
                logger.warning(f"[LIVE_MFE_BATCH] Invalid batch stored, not processing signals")
                return jsonify({
                    'success': True,
                    'status': 'stored_invalid',
                    'batch_id': batch_id,
                    'processed': 0,
                    'upserted': 0,
                    'skipped': 0
                }), 200
            
            # Process signals (always, even for duplicates)
            processed = 0
            upserted = 0
            skipped = 0
            
            for signal in signals:
                trade_id = signal.get('trade_id')
                if not trade_id:
                    skipped += 1
                    continue
                
                # Parse triangle_time_ms (source: triangle_time in payload)
                triangle_time_ms = None
                try:
                    if signal.get('triangle_time') is not None:
                        triangle_time_ms = int(signal.get('triangle_time'))
                except (ValueError, TypeError):
                    pass
                
                # Parse entry/stop (may arrive as entry_price/stop_loss)
                entry = None
                stop = None
                try:
                    entry_val = signal.get('entry_price') or signal.get('entry')
                    if entry_val is not None:
                        entry = float(entry_val)
                except (ValueError, TypeError):
                    pass
                
                try:
                    stop_val = signal.get('stop_loss') or signal.get('stop')
                    if stop_val is not None:
                        stop = float(stop_val)
                except (ValueError, TypeError):
                    pass
                
                # Parse be_mfe/no_be_mfe/mae (safe float conversion, default to 0.0)
                be_mfe_val = 0.0
                no_be_mfe_val = 0.0
                mae_val = 0.0
                
                try:
                    if signal.get('be_mfe') is not None:
                        be_mfe_val = float(signal.get('be_mfe'))
                except (ValueError, TypeError):
                    be_mfe_val = 0.0
                
                try:
                    if signal.get('no_be_mfe') is not None:
                        no_be_mfe_val = float(signal.get('no_be_mfe'))
                except (ValueError, TypeError):
                    no_be_mfe_val = 0.0
                
                try:
                    mae_raw = signal.get('mae_global_r') or signal.get('mae')
                    if mae_raw is not None:
                        mae_val = float(mae_raw)
                        # Clamp MAE to <= 0.0
                        if mae_val > 0.0:
                            logger.warning(f"[LIVE_MFE_BATCH] MAE > 0 for {trade_id}: {mae_val}, clamping to 0.0")
                            mae_val = 0.0
                except (ValueError, TypeError):
                    mae_val = 0.0
                
                # Upsert into confirmed_signals_ledger
                symbol_val = signal.get('symbol') or payload.get('symbol') or signal.get('exchange') or payload.get('exchange') or 'unknown'
                cursor.execute("""
                    INSERT INTO confirmed_signals_ledger 
                    (trade_id, triangle_time_ms, direction, session, entry, stop, be_mfe, no_be_mfe, mae, symbol, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (trade_id) DO UPDATE SET
                        triangle_time_ms = COALESCE(EXCLUDED.triangle_time_ms, confirmed_signals_ledger.triangle_time_ms),
                        direction = COALESCE(EXCLUDED.direction, confirmed_signals_ledger.direction),
                        session = COALESCE(EXCLUDED.session, confirmed_signals_ledger.session),
                        entry = COALESCE(EXCLUDED.entry, confirmed_signals_ledger.entry),
                        stop = COALESCE(EXCLUDED.stop, confirmed_signals_ledger.stop),
                        be_mfe = COALESCE(EXCLUDED.be_mfe, confirmed_signals_ledger.be_mfe),
                        no_be_mfe = COALESCE(EXCLUDED.no_be_mfe, confirmed_signals_ledger.no_be_mfe),
                        mae = COALESCE(EXCLUDED.mae, confirmed_signals_ledger.mae),
                        symbol = COALESCE(EXCLUDED.symbol, confirmed_signals_ledger.symbol),
                        updated_at = NOW()
                """, (trade_id, triangle_time_ms, signal.get('direction'), signal.get('session'), 
                      entry, stop, be_mfe_val, no_be_mfe_val, mae_val, symbol_val))
                
                processed += 1
                upserted += 1
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"[LIVE_MFE_BATCH] ✅ Processed {processed}, upserted {upserted}, skipped {skipped}")
            
            return jsonify({
                'success': True,
                'status': batch_status,
                'batch_id': batch_id,
                'processed': processed,
                'upserted': upserted,
                'skipped': skipped
            }), 200
            
        except Exception as e:
            logger.error(f"[LIVE_MFE_BATCH] ❌ Exception: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/indicator-live/debug/confirmed/<trade_id>', methods=['GET'])
    def debug_confirmed_ledger(trade_id):
        """Get confirmed_signals_ledger row for a trade_id."""
        import os
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        try:
            DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('DATABASE_PUBLIC_URL')
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("SELECT * FROM confirmed_signals_ledger WHERE trade_id = %s", (trade_id,))
            row = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if not row:
                return jsonify({'success': True, 'found': False}), 200
            
            # Convert to JSON-serializable
            result = {}
            for key, value in row.items():
                if hasattr(value, 'isoformat'):
                    result[key] = value.isoformat()
                elif isinstance(value, (int, float)):
                    result[key] = float(value) if value is not None else None
                else:
                    result[key] = value
            
            return jsonify({'success': True, 'found': True, 'data': result}), 200
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/admin/backfill-ledger-symbol', methods=['POST'])
    def backfill_ledger_symbol():
        """Backfill confirmed_signals_ledger.symbol for rows where symbol is NULL or empty"""
        import os
        import psycopg2
        
        # Token auth
        expected_token = os.environ.get('INDICATOR_EXPORT_TOKEN')
        if expected_token:
            query_token = request.args.get('token')
            if query_token != expected_token:
                return jsonify({'error': 'unauthorized'}), 401
        
        data = request.get_json() or {}
        lookback_hours = data.get('lookback_hours', 168)
        limit_trade_ids = data.get('limit_trade_ids', 10)
        
        try:
            DATABASE_URL = os.environ.get('DATABASE_URL')
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            
            # Backfill symbol
            cur.execute("""
                WITH src AS (
                    SELECT trade_id,
                           MAX(symbol) FILTER (WHERE symbol IS NOT NULL AND symbol <> '') AS sym
                    FROM confirmed_signals_ledger
                    WHERE updated_at >= NOW() - INTERVAL '%s hours'
                    GROUP BY trade_id
                ),
                upd AS (
                    UPDATE confirmed_signals_ledger l
                    SET symbol = COALESCE(NULLIF(l.symbol,''), src.sym)
                    FROM src
                    WHERE l.trade_id = src.trade_id
                      AND (l.symbol IS NULL OR l.symbol = '')
                      AND src.sym IS NOT NULL
                    RETURNING l.trade_id
                )
                SELECT trade_id FROM upd
            """, (lookback_hours,))
            
            updated_trade_ids = [row[0] for row in cur.fetchall()]
            updated_symbol_count = len(updated_trade_ids)
            
            conn.commit()
            cur.close()
            conn.close()
            
            return jsonify({
                'status': 'ok',
                'updated_symbol_count': updated_symbol_count,
                'updated_timeframe_count': 0,
                'sample_trade_ids': updated_trade_ids[:limit_trade_ids],
                'lookback_hours': lookback_hours
            }), 200
            
        except Exception as e:
            logger.error(f"[ADMIN_BACKFILL] Error: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    # TEMP DEBUG - REMOVE LATER
    @app.route('/api/debug/sql', methods=['GET'])
    def debug_sql():
        """Execute SELECT-only queries for debugging"""
        import os
        import psycopg2
        from psycopg2.extras import RealDictCursor
        from decimal import Decimal
        from datetime import datetime, date, time
        from uuid import UUID
        
        def serialize_value(v):
            """Safe serialization for any DB type"""
            if v is None:
                return None
            if isinstance(v, Decimal):
                return float(v)
            if isinstance(v, (datetime, date, time)):
                return v.isoformat()
            if isinstance(v, UUID):
                return str(v)
            if isinstance(v, (bytes, bytearray)):
                return v.hex()
            return v
        
        # Parse params
        token = request.args.get('token', '')
        sql = request.args.get('sql', '')
        
        if not sql:
            return jsonify({'success': False, 'error': 'missing sql'}), 400
        
        # Token auth
        expected_token = os.environ.get('INDICATOR_EXPORT_TOKEN')
        if expected_token and token != expected_token:
            return jsonify({'success': False, 'error': 'unauthorized'}), 401
        
        # Security: only SELECT
        s = sql.lstrip()
        if not s.upper().startswith('SELECT'):
            return jsonify({'success': False, 'error': 'only SELECT allowed'}), 400
        
        # Limit results
        if 'LIMIT' not in s.upper():
            s = s.rstrip(';') + ' LIMIT 100'
        
        try:
            DATABASE_URL = os.environ.get('DATABASE_URL')
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute(s)
            rows = cur.fetchall()
            
            columns = [desc.name for desc in cur.description] if cur.description else []
            
            # Convert to JSON-serializable
            result_rows = []
            for row in rows:
                row_dict = {key: serialize_value(value) for key, value in row.items()}
                result_rows.append(row_dict)
            
            cur.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'row_count': len(result_rows),
                'columns': columns,
                'rows': result_rows
            }), 200
            
        except Exception as e:
            logger.exception("[DEBUG_SQL] failed sql=%s", sql[:200])
            return jsonify({
                'success': False,
                'error': 'debug_sql_failed',
                'message': str(e),
                'sql_preview': sql[:200]
            }), 500


    @app.route('/api/admin/backfill/missing-symbols', methods=['POST'])
    def backfill_missing_symbols():
        """Backfill confirmed_signals_ledger.symbol for NULL/empty rows"""
        import os
        import psycopg2
        
        # Token auth
        expected_token = os.environ.get('INDICATOR_EXPORT_TOKEN')
        if expected_token:
            query_token = request.args.get('token')
            if query_token != expected_token:
                return jsonify({'success': False, 'error': 'unauthorized'}), 401
        
        data = request.get_json() or {}
        days = max(1, min(60, data.get('days', 7)))
        symbol = data.get('symbol', 'MNQ1!')
        
        try:
            DATABASE_URL = os.environ.get('DATABASE_URL')
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            
            # Count before update
            cur.execute("""
                SELECT 
                    COUNT(*) FILTER (WHERE symbol IS NULL) as null_count,
                    COUNT(*) FILTER (WHERE symbol = '') as empty_count,
                    COUNT(*) FILTER (WHERE symbol ILIKE 'unknown') as unknown_count
                FROM confirmed_signals_ledger
                WHERE (symbol IS NULL OR symbol = '' OR symbol ILIKE 'unknown')
                AND updated_at >= NOW() - INTERVAL '%s days'
            """, (days,))
            counts = cur.fetchone()
            
            # Update
            cur.execute("""
                UPDATE confirmed_signals_ledger
                SET symbol = %s
                WHERE (symbol IS NULL OR symbol = '' OR symbol ILIKE 'unknown')
                AND updated_at >= NOW() - INTERVAL '%s days'
            """, (symbol, days))
            
            updated_rows = cur.rowcount
            conn.commit()
            
            logger.info(f"[ADMIN_BACKFILL] Updated {updated_rows} rows with symbol={symbol}, days={days}")
            
            cur.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'updated_rows': updated_rows,
                'updated_unknown_rows': counts[2] if counts else 0,
                'updated_empty_rows': counts[1] if counts else 0,
                'updated_null_rows': counts[0] if counts else 0,
                'days': days,
                'symbol': symbol
            }), 200
            
        except Exception as e:
            logger.exception("[ADMIN_BACKFILL] Error")
            return jsonify({'success': False, 'error': str(e)}), 500
