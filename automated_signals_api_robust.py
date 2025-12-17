"""
Robust Automated Signals API
Production-grade implementation with comprehensive error handling
"""
# INTEGRITY_REPAIR_TIMESTAMPS_ACTIVE
from flask import jsonify
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
    
    @app.route('/api/automated-signals/dashboard-data')
    def get_dashboard_data_robust():
        """
        Get complete dashboard data from automated_signals table.
        
        STRICT PATCH:
        - Returns ALL active trades (no limit) so they never disappear
        - Returns capped completed trades (last 500) for pagination
        - Only uses automated_signals table
        - NO legacy tables: live_signals, signal_lab_trades, enhanced_signals_v2
        """
        try:
            import os
            import psycopg2
            from psycopg2.extras import RealDictCursor
            from decimal import Decimal
            
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                return jsonify({
                    'success': False,
                    'error': 'no_database_url',
                    'active_trades': [],
                    'completed_trades': [],
                    'stats': _get_empty_stats_ultra()
                }), 500
            
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()
            
            # Check table existence
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'automated_signals'
                );
            """)
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                logger.warning("automated_signals table does not exist")
                cursor.close()
                conn.close()
                return jsonify({
                    'success': False,
                    'error': 'table_not_found',
                    'active_trades': [],
                    'completed_trades': [],
                    'stats': _get_empty_stats_ultra()
                }), 200
            
            cursor.close()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Helper to convert row to JSON-serializable dict
            def row_to_dict(row):
                result = {}
                for key, value in row.items():
                    if isinstance(value, Decimal):
                        result[key] = float(value)
                    elif hasattr(value, 'isoformat'):
                        result[key] = value.isoformat()
                    else:
                        result[key] = value
                return result
            
            # ============================================
            # STEP 1: Load ALL ACTIVE trades (NO LIMIT)
            # ACTIVE = trades without any EXIT event
            # FIX: Properly aggregate ENTRY data with latest MFE
            # ============================================
            cursor.execute("""
                WITH entry_data AS (
                    SELECT 
                        trade_id,
                        direction,
                        entry_price,
                        stop_loss,
                        session,
                        bias,
                        signal_date,
                        signal_time,
                        timestamp as entry_timestamp
                    FROM automated_signals
                    WHERE event_type = 'ENTRY'
                ),
                latest_mfe AS (
                    SELECT DISTINCT ON (trade_id)
                        trade_id,
                        mfe,
                        be_mfe,
                        no_be_mfe,
                        current_price,
                        mae_global_r,
                        direction,
                        session,
                        timestamp as last_update
                    FROM automated_signals
                    WHERE event_type = 'MFE_UPDATE'
                    ORDER BY trade_id, timestamp DESC
                ),
                active_trade_ids AS (
                    -- Only include signals with ENTRY event (proper trades)
                    -- A trade is ACTIVE if No-BE strategy is still running
                    -- A trade is COMPLETE only when EXIT_SL occurs (both strategies stopped)
                    -- EXIT_BE means BE strategy stopped, but No-BE continues → still ACTIVE
                    SELECT DISTINCT trade_id
                    FROM automated_signals
                    WHERE event_type = 'ENTRY'
                    AND trade_id NOT IN (
                        SELECT DISTINCT trade_id 
                        FROM automated_signals 
                        WHERE event_type IN ('EXIT_STOP_LOSS', 'EXIT_SL')
                        -- Note: EXIT_BE is NOT included here because No-BE strategy continues
                    )
                )
                SELECT 
                    a.trade_id,
                    'ACTIVE' as trade_status,
                    COALESCE(e.direction, m.direction) as direction,
                    e.entry_price,
                    e.stop_loss,
                    COALESCE(e.session, m.session) as session,
                    e.bias,
                    e.signal_date,
                    e.signal_time,
                    COALESCE(e.entry_timestamp, m.last_update) as timestamp,
                    e.entry_timestamp as entry_ts,
                    COALESCE(e.entry_timestamp, m.last_update) as event_ts,
                    COALESCE(m.mfe, 0) as mfe,
                    COALESCE(m.be_mfe, 0) as be_mfe,
                    COALESCE(m.no_be_mfe, 0) as no_be_mfe,
                    m.current_price,
                    COALESCE(m.mae_global_r, 0) as mae_global_r,
                    NULL as final_mfe
                FROM active_trade_ids a
                LEFT JOIN entry_data e ON a.trade_id = e.trade_id
                LEFT JOIN latest_mfe m ON a.trade_id = m.trade_id
                ORDER BY COALESCE(e.entry_timestamp, m.last_update) DESC
            """)
            active_rows = cursor.fetchall()
            active_trades = [row_to_dict(row) for row in active_rows]
            
            # ============================================
            # STEP 2: Load ALL COMPLETED trades (NO LIMIT)
            # COMPLETED = trades with EXIT event
            # FIX: Join ENTRY data with EXIT data for complete info
            # ============================================
            cursor.execute("""
                WITH entry_data AS (
                    SELECT 
                        trade_id,
                        direction,
                        entry_price,
                        stop_loss,
                        session,
                        bias,
                        signal_date,
                        signal_time,
                        timestamp as entry_timestamp
                    FROM automated_signals
                    WHERE event_type = 'ENTRY'
                ),
                exit_data AS (
                    -- Only include EXIT_SL (both strategies stopped)
                    -- EXIT_BE means BE stopped but No-BE continues → not completed yet
                    SELECT 
                        trade_id,
                        event_type as exit_type,
                        final_mfe,
                        timestamp as exit_timestamp
                    FROM automated_signals
                    WHERE event_type IN ('EXIT_STOP_LOSS', 'EXIT_SL')
                    -- Note: EXIT_BE and EXIT_BREAK_EVEN excluded (trade still active)
                ),
                latest_mfe_completed AS (
                    SELECT DISTINCT ON (trade_id)
                        trade_id,
                        mfe,
                        be_mfe,
                        no_be_mfe,
                        mae_global_r
                    FROM automated_signals
                    WHERE event_type = 'MFE_UPDATE'
                    ORDER BY trade_id, timestamp DESC
                )
                SELECT 
                    x.trade_id,
                    x.exit_type as event_type,
                    'COMPLETED' as trade_status,
                    COALESCE(e.direction, 'UNKNOWN') as direction,
                    e.entry_price,
                    e.stop_loss,
                    e.session,
                    e.bias,
                    e.signal_date,
                    e.signal_time,
                    x.exit_timestamp as timestamp,
                    e.entry_timestamp as entry_ts,
                    x.exit_timestamp as exit_ts,
                    COALESCE(m.mfe, 0) as mfe,
                    COALESCE(m.be_mfe, 0) as be_mfe,
                    COALESCE(m.no_be_mfe, 0) as no_be_mfe,
                    COALESCE(m.mae_global_r, 0) as mae_global_r,
                    x.final_mfe
                FROM exit_data x
                LEFT JOIN entry_data e ON x.trade_id = e.trade_id
                LEFT JOIN latest_mfe_completed m ON x.trade_id = m.trade_id
                ORDER BY x.exit_timestamp DESC
            """)
            completed_rows = cursor.fetchall()
            completed_trades = [row_to_dict(row) for row in completed_rows]
            
            # ============================================
            # STEP 3: Calculate stats
            # ============================================
            
            # Today's count (Eastern Time)
            cursor.execute("""
                SELECT COUNT(DISTINCT trade_id) as count
                FROM automated_signals
                WHERE event_type = 'ENTRY'
                AND timestamp AT TIME ZONE 'America/New_York' >= CURRENT_DATE AT TIME ZONE 'America/New_York'
            """)
            today_count = cursor.fetchone()['count'] or 0
            
            # Active count (unique trades without EXIT_SL)
            # A trade is ACTIVE if No-BE strategy is still running
            # EXIT_BE means BE stopped, but No-BE continues → still ACTIVE
            cursor.execute("""
                SELECT COUNT(DISTINCT trade_id) as count
                FROM automated_signals
                WHERE event_type = 'ENTRY'
                AND trade_id NOT IN (
                    SELECT DISTINCT trade_id 
                    FROM automated_signals 
                    WHERE event_type IN ('EXIT_STOP_LOSS', 'EXIT_SL')
                    -- Note: EXIT_BE is NOT included because No-BE strategy continues
                )
            """)
            active_count = cursor.fetchone()['count'] or 0
            
            # Completed count (total, not just returned)
            # Only count trades with EXIT_SL (both strategies stopped)
            cursor.execute("""
                SELECT COUNT(DISTINCT trade_id) as count
                FROM automated_signals
                WHERE event_type IN ('EXIT_STOP_LOSS', 'EXIT_SL')
                -- Note: EXIT_BE excluded (trade still active with No-BE)
            """)
            completed_count = cursor.fetchone()['count'] or 0
            
            # Last webhook timestamp
            cursor.execute("""
                SELECT MAX(timestamp) as last_ts FROM automated_signals
            """)
            last_ts_row = cursor.fetchone()
            last_webhook_timestamp = last_ts_row['last_ts'].isoformat() if last_ts_row and last_ts_row['last_ts'] else None
            
            # Webhook healthy check (within 5 minutes = 300 seconds)
            webhook_healthy = False
            if last_ts_row and last_ts_row['last_ts']:
                last_ts = last_ts_row['last_ts']
                if last_ts.tzinfo is None:
                    last_ts = pytz.UTC.localize(last_ts)
                now_utc = datetime.now(pytz.UTC)
                delta_sec = (now_utc - last_ts).total_seconds()
                webhook_healthy = delta_sec < 300
            
            # Average MFE from completed trades (only EXIT_SL - both strategies stopped)
            cursor.execute("""
                SELECT AVG(COALESCE(final_mfe, mfe)) as avg_mfe
                FROM automated_signals
                WHERE event_type IN ('EXIT_STOP_LOSS', 'EXIT_SL')
                -- Note: Only trades where both strategies stopped
            """)
            avg_mfe_row = cursor.fetchone()
            avg_mfe = float(avg_mfe_row['avg_mfe']) if avg_mfe_row and avg_mfe_row['avg_mfe'] else 0.0
            
            # Win rate (final_mfe > 0 is a win) - only completed trades
            cursor.execute("""
                SELECT 
                    COUNT(*) FILTER (WHERE COALESCE(final_mfe, mfe, 0) > 0) as wins,
                    COUNT(*) as total
                FROM automated_signals
                WHERE event_type IN ('EXIT_STOP_LOSS', 'EXIT_SL')
                -- Note: Only trades where both strategies stopped
            """)
            win_row = cursor.fetchone()
            wins = win_row['wins'] or 0
            total_exits = win_row['total'] or 0
            win_rate = (wins / total_exits * 100) if total_exits > 0 else 0.0
            
            stats = {
                'today_count': today_count,
                'active_count': active_count,
                'completed_count': completed_count,
                'last_webhook_timestamp': last_webhook_timestamp,
                'webhook_healthy': webhook_healthy,
                'avg_mfe': round(avg_mfe, 2),
                'win_rate': round(win_rate, 1)
            }
            
            cursor.close()
            conn.close()
            
            # Build response matching Ultra JS expectations
            response = jsonify({
                'success': True,
                'active_trades': active_trades,
                'completed_trades': completed_trades,
                'stats': stats,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
            
            # Cache-busting headers
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            
            return response, 200
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error(f"Dashboard data error: {error_msg}", exc_info=True)
            return jsonify({
                'success': False,
                'error': 'query_failed',
                'message': error_msg,
                'active_trades': [],
                'completed_trades': [],
                'stats': _get_empty_stats_ultra()
            }), 200
    
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
        """Get daily trade data for calendar view with completed and active counts"""
        try:
            import os
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                return jsonify({'success': False, 'error': 'no_database_url'}), 500
            
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get completed trades per day (last 90 days)
            # JOIN EXIT with ENTRY to get signal_date
            cursor.execute("""
                SELECT 
                    e.signal_date as date,
                    COUNT(DISTINCT x.trade_id) as completed_count,
                    AVG(COALESCE(x.final_mfe, x.no_be_mfe, x.mfe, 0)) as avg_mfe
                FROM automated_signals x
                INNER JOIN automated_signals e ON x.trade_id = e.trade_id AND e.event_type = 'ENTRY'
                WHERE x.event_type IN ('EXIT_STOP_LOSS', 'EXIT_SL')
                AND e.signal_date >= CURRENT_DATE - INTERVAL '90 days'
                AND e.signal_date IS NOT NULL
                GROUP BY e.signal_date
            """)
            completed_by_date = {row['date'].isoformat() if hasattr(row['date'], 'isoformat') else str(row['date']): row for row in cursor.fetchall()}
            
            # Get active trades per day (entry date, no EXIT_SL yet)
            # Group by signal_date (actual signal time), not import timestamp
            cursor.execute("""
                SELECT 
                    e.signal_date as date,
                    COUNT(DISTINCT e.trade_id) as active_count
                FROM automated_signals e
                WHERE e.event_type = 'ENTRY'
                AND e.signal_date >= CURRENT_DATE - INTERVAL '90 days'
                AND e.signal_date IS NOT NULL
                AND e.trade_id NOT IN (
                    SELECT DISTINCT trade_id 
                    FROM automated_signals 
                    WHERE event_type IN ('EXIT_STOP_LOSS', 'EXIT_SL')
                )
                GROUP BY e.signal_date
            """)
            active_by_date = {row['date'].isoformat() if hasattr(row['date'], 'isoformat') else str(row['date']): row['active_count'] for row in cursor.fetchall()}
            
            cursor.close()
            conn.close()
            
            # Merge data
            all_dates = set(completed_by_date.keys()) | set(active_by_date.keys())
            daily_data = {}
            
            for date_str in all_dates:
                completed_info = completed_by_date.get(date_str, {})
                daily_data[date_str] = {
                    'completed_count': completed_info.get('completed_count', 0) if completed_info else 0,
                    'active_count': active_by_date.get(date_str, 0),
                    'avg_mfe': float(completed_info.get('avg_mfe', 0)) if completed_info and completed_info.get('avg_mfe') else 0,
                    'trade_count': (completed_info.get('completed_count', 0) if completed_info else 0) + active_by_date.get(date_str, 0)
                }
            
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
        
        # Parse JSON body
        try:
            data = request.get_json(force=True)
        except Exception as e:
            logger.error(f"[INDICATOR_EXPORT] Invalid JSON: {e}")
            return jsonify({'status': 'error', 'message': 'Invalid JSON'}), 400
        
        # Compute SHA256 hash (stable canonicalization)
        payload_str = json.dumps(data, sort_keys=True)
        payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()
        
        # Extract envelope fields
        event_type = data.get('event_type')
        batch_number = data.get('batch_number')
        batch_size = data.get('batch_size')
        total_signals = data.get('total_signals')
        signals = data.get('signals', [])
        
        logger.info(f"[INDICATOR_EXPORT] event_type={event_type}, batch={batch_number}, size={batch_size}, hash={payload_hash[:8]}")
        
        # Validate event_type
        valid_types = ['INDICATOR_EXPORT_V2', 'ALL_SIGNALS_EXPORT']
        is_valid = event_type in valid_types and isinstance(signals, list)
        validation_error = None if is_valid else f"Invalid event_type or signals not array"
        
        # Insert into database
        try:
            DATABASE_URL = os.environ.get('DATABASE_PUBLIC_URL') or os.environ.get('DATABASE_URL')
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            
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
                
                return jsonify({
                    'status': 'success',
                    'batch_id': batch_id,
                    'event_type': event_type,
                    'batch_number': batch_number,
                    'signals_count': len(signals)
                }), 200
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
        
        logger.info("[ALL_SIGNALS_DATA] Fetching all signals from ledger")
        
        try:
            DATABASE_URL = os.environ.get('DATABASE_PUBLIC_URL') or os.environ.get('DATABASE_URL')
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Query all_signals_ledger
            cursor.execute("""
                SELECT 
                    trade_id,
                    triangle_time_ms,
                    confirmation_time_ms,
                    direction,
                    status,
                    bars_to_confirm,
                    session,
                    entry_price,
                    stop_loss,
                    risk_points,
                    htf_daily,
                    htf_4h,
                    htf_1h,
                    htf_15m,
                    htf_5m,
                    htf_1m,
                    updated_at
                FROM all_signals_ledger
                ORDER BY triangle_time_ms DESC
                LIMIT 1000
            """)
            
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
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
                    'entry': float(row['entry_price']) if row['entry_price'] else None,
                    'stop': float(row['stop_loss']) if row['stop_loss'] else None,
                    'risk': float(row['risk_points']) if row['risk_points'] else None,
                    'htf_daily': row['htf_daily'],
                    'htf_4h': row['htf_4h'],
                    'htf_1h': row['htf_1h'],
                    'htf_15m': row['htf_15m'],
                    'htf_5m': row['htf_5m'],
                    'htf_1m': row['htf_1m'],
                    'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
                }
                signals.append(signal)
            
            logger.info(f"[ALL_SIGNALS_DATA] ✅ Returned {len(signals)} signals")
            
            return jsonify({
                'success': True,
                'signals': signals,
                'count': len(signals)
            }), 200
            
        except Exception as e:
            logger.error(f"[ALL_SIGNALS_DATA] ❌ Error: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'signals': [],
                'count': 0
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
                    a.entry_price,
                    a.stop_loss,
                    a.risk_points,
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
                    'entry': float(row['entry_price']) if row['entry_price'] else None,
                    'stop': float(row['stop_loss']) if row['stop_loss'] else None,
                    'risk': float(row['risk_points']) if row['risk_points'] else None,
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
                    a.entry_price,
                    a.stop_loss,
                    a.risk_points,
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
                    'entry': float(row['entry_price']) if row['entry_price'] else None,
                    'stop': float(row['stop_loss']) if row['stop_loss'] else None,
                    'risk': float(row['risk_points']) if row['risk_points'] else None,
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
