"""
Data Quality API Endpoints
Provides APIs for data quality monitoring, conflict resolution, and reconciliation tracking
"""

from flask import request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime, timedelta
from decimal import Decimal

def register_data_quality_api(app):
    """Register all data quality API endpoints"""
    
    def get_db_connection():
        """Get fresh database connection"""
        database_url = os.getenv('DATABASE_URL')
        return psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    
    # ========================================================================
    # 1. DATA QUALITY OVERVIEW
    # ========================================================================
    
    @app.route('/api/data-quality/overview', methods=['GET'])
    def get_data_quality_overview():
        """Get high-level data quality overview"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get latest reconciliation
            cursor.execute("""
                SELECT 
                    reconciliation_time as last_sync,
                    webhook_success_rate,
                    signals_in_database as signals_today,
                    missing_signals + incomplete_signals as gaps_filled,
                    status
                FROM data_quality_reconciliations
                ORDER BY reconciliation_time DESC
                LIMIT 1
            """)
            
            latest = cursor.fetchone()
            
            # Get pending conflicts count
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM data_quality_conflicts
                WHERE status = 'pending'
            """)
            
            conflicts = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if latest:
                return jsonify({
                    'success': True,
                    'last_sync': latest['last_sync'].isoformat() if latest['last_sync'] else None,
                    'status': latest['status'] or 'unknown',
                    'webhook_success_rate': float(latest['webhook_success_rate']) if latest['webhook_success_rate'] else 0.0,
                    'signals_today': latest['signals_today'] or 0,
                    'gaps_filled': latest['gaps_filled'] or 0,
                    'conflicts_pending': conflicts['count'] if conflicts else 0
                }), 200
            else:
                return jsonify({
                    'success': True,
                    'last_sync': None,
                    'status': 'no_data',
                    'webhook_success_rate': 0.0,
                    'signals_today': 0,
                    'gaps_filled': 0,
                    'conflicts_pending': 0
                }), 200
                
        except Exception as e:
            print(f"❌ Overview error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ========================================================================
    # 2. SYSTEM HEALTH STATUS
    # ========================================================================
    
    @app.route('/api/data-quality/health', methods=['GET'])
    def get_system_health():
        """Get real-time system health status"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check last webhook received
            cursor.execute("""
                SELECT MAX(timestamp) as last_webhook
                FROM automated_signals
                WHERE event_type IN ('ENTRY', 'MFE_UPDATE')
            """)
            
            webhook_data = cursor.fetchone()
            last_webhook = webhook_data['last_webhook'] if webhook_data else None
            
            # Calculate time since last webhook
            if last_webhook:
                time_diff = datetime.now() - last_webhook.replace(tzinfo=None)
                minutes_ago = int(time_diff.total_seconds() / 60)
                webhook_status = "active" if minutes_ago < 60 else "stale"
                last_received = f"{minutes_ago}m ago" if minutes_ago < 60 else f"{int(minutes_ago/60)}h ago"
            else:
                webhook_status = "unknown"
                last_received = "never"
            
            # Get last reconciliation
            cursor.execute("""
                SELECT reconciliation_time
                FROM data_quality_reconciliations
                ORDER BY reconciliation_time DESC
                LIMIT 1
            """)
            
            recon_data = cursor.fetchone()
            last_recon = recon_data['reconciliation_time'] if recon_data else None
            
            if last_recon:
                recon_diff = datetime.now() - last_recon.replace(tzinfo=None)
                hours_ago = int(recon_diff.total_seconds() / 3600)
                recon_status = "complete"
                last_run = f"{hours_ago}h ago" if hours_ago > 0 else "recently"
            else:
                recon_status = "never_run"
                last_run = "never"
            
            cursor.close()
            conn.close()
            
            # Calculate next sync time (11 PM ET today or tomorrow)
            now = datetime.now()
            next_sync = now.replace(hour=23, minute=0, second=0, microsecond=0)
            if now.hour >= 23:
                next_sync += timedelta(days=1)
            
            time_until = next_sync - now
            hours_until = int(time_until.total_seconds() / 3600)
            minutes_until = int((time_until.total_seconds() % 3600) / 60)
            
            return jsonify({
                'success': True,
                'webhooks': {
                    'status': webhook_status,
                    'last_received': last_received
                },
                'daily_export': {
                    'status': 'scheduled',
                    'next_run': '3:30 PM ET'
                },
                'reconciliation': {
                    'status': recon_status,
                    'last_run': last_run
                },
                'next_sync': f"{hours_until}h {minutes_until}m"
            }), 200
            
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ========================================================================
    # 3. CONFLICTS LIST
    # ========================================================================
    
    @app.route('/api/data-quality/conflicts', methods=['GET'])
    def get_conflicts():
        """Get list of data conflicts"""
        try:
            status = request.args.get('status', 'pending')
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    id,
                    trade_id,
                    conflict_type,
                    webhook_value,
                    indicator_value,
                    field_name,
                    severity,
                    status,
                    created_at
                FROM data_quality_conflicts
                WHERE status = %s
                ORDER BY severity DESC, created_at DESC
                LIMIT 50
            """, (status,))
            
            conflicts = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            # Convert to JSON-serializable format
            conflicts_list = []
            for conflict in conflicts:
                conflicts_list.append({
                    'id': conflict['id'],
                    'trade_id': conflict['trade_id'],
                    'conflict_type': conflict['conflict_type'],
                    'webhook_value': conflict['webhook_value'],
                    'indicator_value': conflict['indicator_value'],
                    'field_name': conflict['field_name'],
                    'severity': conflict['severity'],
                    'status': conflict['status'],
                    'created_at': conflict['created_at'].isoformat() if conflict['created_at'] else None
                })
            
            return jsonify({
                'success': True,
                'conflicts': conflicts_list,
                'count': len(conflicts_list)
            }), 200
            
        except Exception as e:
            print(f"❌ Conflicts list error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ========================================================================
    # 4. RESOLVE CONFLICT
    # ========================================================================
    
    @app.route('/api/data-quality/resolve', methods=['POST'])
    def resolve_conflict():
        """Resolve a data conflict"""
        try:
            data = request.get_json()
            conflict_id = data.get('conflict_id')
            resolution = data.get('resolution')  # trust_indicator, trust_webhook, ignore
            
            if not conflict_id or not resolution:
                return jsonify({'success': False, 'error': 'Missing required fields'}), 400
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get conflict details
            cursor.execute("""
                SELECT trade_id, field_name, indicator_value, webhook_value, conflict_type
                FROM data_quality_conflicts
                WHERE id = %s
            """, (conflict_id,))
            
            conflict = cursor.fetchone()
            
            if not conflict:
                cursor.close()
                conn.close()
                return jsonify({'success': False, 'error': 'Conflict not found'}), 404
            
            # Apply resolution
            updated_value = None
            
            if resolution == 'trust_indicator':
                # Update database with indicator value
                if conflict['field_name'] and conflict['indicator_value']:
                    cursor.execute(f"""
                        UPDATE automated_signals
                        SET {conflict['field_name']} = %s
                        WHERE trade_id = %s
                    """, (conflict['indicator_value'], conflict['trade_id']))
                    updated_value = conflict['indicator_value']
            
            elif resolution == 'trust_webhook':
                # Keep webhook value (no update needed)
                updated_value = conflict['webhook_value']
            
            # Mark conflict as resolved
            cursor.execute("""
                UPDATE data_quality_conflicts
                SET status = 'resolved',
                    resolution = %s,
                    resolved_at = NOW()
                WHERE id = %s
            """, (resolution, conflict_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'updated_value': updated_value,
                'message': f'Conflict resolved: {resolution}'
            }), 200
            
        except Exception as e:
            print(f"❌ Resolve conflict error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ========================================================================
    # 5. GAP ANALYSIS
    # ========================================================================
    
    @app.route('/api/data-quality/gaps', methods=['GET'])
    def get_gaps():
        """Get list of gaps that were auto-filled"""
        try:
            date_str = request.args.get('date')
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get conflicts that were auto-filled
            query = """
                SELECT 
                    trade_id,
                    conflict_type,
                    indicator_value as source_value,
                    resolved_at as filled_at,
                    'indicator' as source
                FROM data_quality_conflicts
                WHERE conflict_type IN ('missing_signal', 'missing_field')
                AND status = 'resolved'
                AND resolution = 'auto_filled'
            """
            
            params = []
            if date_str:
                query += " AND DATE(created_at) = %s"
                params.append(date_str)
            
            query += " ORDER BY resolved_at DESC LIMIT 50"
            
            cursor.execute(query, params)
            gaps = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            gaps_list = []
            for gap in gaps:
                gaps_list.append({
                    'trade_id': gap['trade_id'],
                    'source': gap['source'],
                    'auto_filled': True,
                    'filled_at': gap['filled_at'].isoformat() if gap['filled_at'] else None
                })
            
            return jsonify({
                'success': True,
                'missing_signals': gaps_list,
                'count': len(gaps_list)
            }), 200
            
        except Exception as e:
            print(f"❌ Gaps analysis error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ========================================================================
    # 6. HISTORICAL METRICS
    # ========================================================================
    
    @app.route('/api/data-quality/metrics', methods=['GET'])
    def get_metrics():
        """Get historical quality metrics"""
        try:
            days = int(request.args.get('days', 30))
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    metric_date,
                    webhook_success_rate,
                    signals_captured
                FROM data_quality_metrics
                WHERE metric_date >= CURRENT_DATE - INTERVAL '%s days'
                ORDER BY metric_date DESC
            """, (days,))
            
            metrics = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            metrics_list = []
            total_rate = 0
            count = 0
            best_day = None
            worst_day = None
            
            for metric in metrics:
                rate = float(metric['webhook_success_rate']) if metric['webhook_success_rate'] else 0.0
                
                metrics_list.append({
                    'date': metric['metric_date'].isoformat(),
                    'success_rate': rate,
                    'signals': metric['signals_captured'] or 0
                })
                
                total_rate += rate
                count += 1
                
                if best_day is None or rate > best_day['rate']:
                    best_day = {'date': metric['metric_date'].isoformat(), 'rate': rate}
                
                if worst_day is None or rate < worst_day['rate']:
                    worst_day = {'date': metric['metric_date'].isoformat(), 'rate': rate}
            
            average = round(total_rate / count, 1) if count > 0 else 0.0
            
            return jsonify({
                'success': True,
                'metrics': metrics_list,
                'average': average,
                'best_day': best_day,
                'worst_day': worst_day
            }), 200
            
        except Exception as e:
            print(f"❌ Metrics error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ========================================================================
    # 7. RECONCILIATION LOG
    # ========================================================================
    
    @app.route('/api/data-quality/reconciliations', methods=['GET'])
    def get_reconciliations():
        """Get reconciliation history"""
        try:
            limit = int(request.args.get('limit', 10))
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    reconciliation_date,
                    reconciliation_time,
                    status,
                    signals_in_indicator,
                    signals_in_database,
                    missing_signals,
                    incomplete_signals,
                    mfe_mismatches,
                    conflicts_requiring_review
                FROM data_quality_reconciliations
                ORDER BY reconciliation_time DESC
                LIMIT %s
            """, (limit,))
            
            reconciliations = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            recon_list = []
            for recon in reconciliations:
                recon_list.append({
                    'date': recon['reconciliation_date'].isoformat(),
                    'time': recon['reconciliation_time'].strftime('%H:%M'),
                    'status': recon['status'],
                    'signals': f"{recon['signals_in_database']}/{recon['signals_in_indicator']}",
                    'gaps_filled': (recon['missing_signals'] or 0) + (recon['incomplete_signals'] or 0),
                    'mfe_updated': recon['mfe_mismatches'] or 0,
                    'conflicts': recon['conflicts_requiring_review'] or 0
                })
            
            return jsonify({
                'success': True,
                'reconciliations': recon_list
            }), 200
            
        except Exception as e:
            print(f"❌ Reconciliations log error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ========================================================================
    # 8. TRIGGER MANUAL RECONCILIATION
    # ========================================================================
    
    @app.route('/api/data-quality/reconcile', methods=['POST'])
    def trigger_reconciliation():
        """Trigger manual reconciliation (placeholder for now)"""
        try:
            # TODO: Implement actual reconciliation logic in Phase 2
            job_id = f"rec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            return jsonify({
                'success': True,
                'job_id': job_id,
                'message': 'Manual reconciliation will be implemented in Phase 2'
            }), 200
            
        except Exception as e:
            print(f"❌ Trigger reconciliation error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    print("✅ Data Quality API endpoints registered")
