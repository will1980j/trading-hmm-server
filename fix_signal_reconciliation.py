#!/usr/bin/env python3
"""
Fix Signal Lab vs Dashboard Reconciliation
Creates an endpoint to reconcile the discrepancy between Signal Lab and Dashboard
"""

# Add this endpoint to web_server.py

reconciliation_endpoint = '''
@app.route('/api/signal-lab-reconcile', methods=['GET', 'POST'])
@login_required
def reconcile_signal_lab_dashboard():
    """Reconcile Signal Lab and Dashboard data discrepancies"""
    try:
        if not db_enabled or not db:
            return jsonify({'error': 'Database not available'}), 500
        
        cursor = db.conn.cursor()
        
        if request.method == 'POST':
            # Fix discrepancies based on request
            action = request.json.get('action', 'analyze')
            
            if action == 'mark_completed':
                # Mark all trades with MFE data as completed (non-active)
                cursor.execute("""
                    UPDATE signal_lab_trades 
                    SET active_trade = false 
                    WHERE COALESCE(mfe_none, mfe, 0) != 0
                    AND COALESCE(active_trade, false) = true
                """)
                fixed_count = cursor.rowcount
                db.conn.commit()
                
                return jsonify({
                    'status': 'success',
                    'action': 'mark_completed',
                    'fixed_count': fixed_count,
                    'message': f'Marked {fixed_count} trades as completed'
                })
            
            elif action == 'sync_all':
                # Ensure all processed trades appear in dashboard
                cursor.execute("""
                    UPDATE signal_lab_trades 
                    SET active_trade = false 
                    WHERE COALESCE(mfe_none, mfe, 0) != 0
                """)
                synced_count = cursor.rowcount
                db.conn.commit()
                
                return jsonify({
                    'status': 'success',
                    'action': 'sync_all',
                    'synced_count': synced_count,
                    'message': f'Synced {synced_count} trades to dashboard'
                })
        
        # GET request - analyze discrepancies
        
        # Get all Signal Lab trades
        cursor.execute("""
            SELECT id, date, time, bias, session, signal_type,
                   COALESCE(mfe_none, mfe, 0) as mfe_value,
                   COALESCE(active_trade, false) as is_active,
                   created_at
            FROM signal_lab_trades 
            ORDER BY created_at DESC
        """)
        all_trades = cursor.fetchall()
        
        # Get Dashboard-visible trades (analysis_only=true logic)
        cursor.execute("""
            SELECT id, date, time, bias, session, signal_type,
                   COALESCE(mfe_none, mfe, 0) as mfe_value,
                   COALESCE(active_trade, false) as is_active,
                   created_at
            FROM signal_lab_trades 
            WHERE COALESCE(mfe_none, mfe, 0) != 0
            AND COALESCE(active_trade, false) = false
            ORDER BY created_at DESC
        """)
        dashboard_trades = cursor.fetchall()
        
        # Analyze discrepancies
        all_ids = {trade['id'] for trade in all_trades}
        dashboard_ids = {trade['id'] for trade in dashboard_trades}
        missing_ids = all_ids - dashboard_ids
        
        # Categorize missing trades
        missing_trades = [t for t in all_trades if t['id'] in missing_ids]
        
        categories = {
            'no_mfe': [],
            'active': [],
            'both': []
        }
        
        for trade in missing_trades:
            has_mfe = trade['mfe_value'] != 0
            is_active = trade['is_active']
            
            if not has_mfe and is_active:
                categories['both'].append(trade)
            elif not has_mfe:
                categories['no_mfe'].append(trade)
            elif is_active:
                categories['active'].append(trade)
        
        # Get date ranges
        all_dates = [t['date'] for t in all_trades if t['date']]
        dashboard_dates = [t['date'] for t in dashboard_trades if t['date']]
        
        analysis = {
            'total_trades': len(all_trades),
            'dashboard_trades': len(dashboard_trades),
            'discrepancy': len(missing_ids),
            'missing_categories': {
                'no_mfe_data': len(categories['no_mfe']),
                'active_trades': len(categories['active']),
                'both_issues': len(categories['both'])
            },
            'date_ranges': {
                'all_trades': {
                    'earliest': min(all_dates) if all_dates else None,
                    'latest': max(all_dates) if all_dates else None
                },
                'dashboard': {
                    'earliest': min(dashboard_dates) if dashboard_dates else None,
                    'latest': max(dashboard_dates) if dashboard_dates else None
                }
            },
            'sample_missing': [
                {
                    'id': t['id'],
                    'date': str(t['date']) if t['date'] else None,
                    'time': str(t['time']) if t['time'] else None,
                    'bias': t['bias'],
                    'mfe': float(t['mfe_value']),
                    'active': t['is_active']
                }
                for t in missing_trades[:10]
            ]
        }
        
        return jsonify({
            'status': 'success',
            'analysis': analysis,
            'recommendations': [
                'Mark completed trades as non-active' if categories['active'] else None,
                'Fill in MFE data for processed trades' if categories['no_mfe'] else None,
                'Review active trade management' if categories['both'] else None
            ]
        })
        
    except Exception as e:
        logger.error(f"Error in signal reconciliation: {str(e)}")
        return jsonify({'error': str(e)}), 500
'''

print("Signal Lab Reconciliation Endpoint")
print("=" * 50)
print("Add this endpoint to web_server.py to fix the discrepancy:")
print()
print(reconciliation_endpoint)
print()
print("USAGE:")
print("GET  /api/signal-lab-reconcile - Analyze discrepancies")
print("POST /api/signal-lab-reconcile - Fix discrepancies")
print("     {'action': 'mark_completed'} - Mark trades with MFE as completed")
print("     {'action': 'sync_all'} - Sync all processed trades to dashboard")