# Prop Firm Management API Endpoints
# Add these routes to your main Flask app

from flask import request, jsonify
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import os

# Database connection (use your existing connection)
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD'),
        port=os.getenv('DATABASE_PORT', 5432)
    )

# Overview Dashboard
@app.route('/api/prop-firm/overview', methods=['GET'])
def get_prop_firm_overview():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get total accounts
        cur.execute("SELECT COUNT(*) as total FROM prop_accounts WHERE status IN ('active', 'evaluation')")
        total_accounts = cur.fetchone()['total']
        
        # Get total equity (converted to AUD)
        cur.execute("""
            SELECT SUM(
                CASE 
                    WHEN pf.base_currency = 'AUD' THEN pa.equity
                    WHEN pf.base_currency = 'USD' THEN pa.equity * 1.48
                    ELSE pa.equity * 1.0
                END
            ) as total_equity
            FROM prop_accounts pa
            JOIN prop_firms pf ON pa.firm_id = pf.id
            WHERE pa.status IN ('active', 'evaluation')
        """)
        total_equity = cur.fetchone()['total_equity'] or 0
        
        # Get violations today
        cur.execute("""
            SELECT COUNT(*) as violations_today 
            FROM prop_violations 
            WHERE created_at >= CURRENT_DATE
        """)
        violations_today = cur.fetchone()['violations_today']
        
        # Get payouts ready (simplified)
        cur.execute("""
            SELECT COUNT(*) as payouts_ready 
            FROM prop_payouts 
            WHERE status = 'pending'
        """)
        payouts_ready = cur.fetchone()['payouts_ready']
        
        # Get recent activity
        cur.execute("""
            SELECT 
                pv.account_id,
                'Violation: ' || pv.violation_type as description,
                pv.created_at as timestamp
            FROM prop_violations pv
            ORDER BY pv.created_at DESC
            LIMIT 5
        """)
        recent_activity = cur.fetchall()
        
        # Get compliance alerts
        cur.execute("""
            SELECT 
                account_id,
                violation_type,
                created_at as timestamp
            FROM prop_violations
            WHERE resolved = FALSE
            ORDER BY created_at DESC
            LIMIT 5
        """)
        compliance_alerts = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'total_accounts': total_accounts,
            'total_equity': float(total_equity),
            'violations_today': violations_today,
            'payouts_ready': payouts_ready,
            'recent_activity': [dict(row) for row in recent_activity],
            'compliance_alerts': [dict(row) for row in compliance_alerts]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Firms Management
@app.route('/api/prop-firm/firms', methods=['GET'])
def get_prop_firms():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT 
                pf.*,
                COUNT(pa.id) as account_count
            FROM prop_firms pf
            LEFT JOIN prop_accounts pa ON pf.id = pa.firm_id
            GROUP BY pf.id
            ORDER BY pf.name
        """)
        firms = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify([dict(row) for row in firms])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prop-firm/firms', methods=['POST'])
def add_prop_firm():
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO prop_firms (name, base_currency, max_drawdown, daily_loss_limit, profit_target)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data['name'],
            data['base_currency'],
            data['max_drawdown'],
            data['daily_loss_limit'],
            data['profit_target']
        ))
        
        firm_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'id': firm_id, 'message': 'Firm added successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Accounts Management
@app.route('/api/prop-firm/accounts', methods=['GET'])
def get_prop_accounts():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT 
                pa.*,
                pf.name as firm_name,
                pf.base_currency,
                (pa.peak_equity - pa.equity) as drawdown
            FROM prop_accounts pa
            JOIN prop_firms pf ON pa.firm_id = pf.id
            ORDER BY pa.updated_at DESC
        """)
        accounts = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify([dict(row) for row in accounts])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prop-firm/accounts', methods=['POST'])
def add_prop_account():
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO prop_accounts (account_id, firm_id, balance, equity, peak_equity, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data['account_id'],
            data['firm_id'],
            data['balance'],
            data['balance'],  # Initial equity = balance
            data['balance'],  # Initial peak = balance
            data['status']
        ))
        
        account_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'id': account_id, 'message': 'Account added successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Compliance Management
@app.route('/api/prop-firm/violations', methods=['GET'])
def get_prop_violations():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT 
                pv.*,
                pf.name as firm_name
            FROM prop_violations pv
            JOIN prop_firms pf ON pv.firm_id = pf.id
            ORDER BY pv.created_at DESC
            LIMIT 50
        """)
        violations = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify([dict(row) for row in violations])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prop-firm/compliance-check', methods=['POST'])
def run_compliance_check():
    try:
        data = request.get_json()
        account_id = data['account_id']
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get account and firm details
        cur.execute("""
            SELECT pa.*, pf.*
            FROM prop_accounts pa
            JOIN prop_firms pf ON pa.firm_id = pf.id
            WHERE pa.account_id = %s
        """, (account_id,))
        
        account = cur.fetchone()
        if not account:
            return jsonify({'error': 'Account not found'}), 404
        
        violations = []
        
        # Check drawdown violation
        current_drawdown = account['peak_equity'] - account['equity']
        if current_drawdown > account['max_drawdown']:
            violations.append({
                'type': 'drawdown',
                'description': f'Drawdown ${current_drawdown:,.2f} exceeds limit ${account["max_drawdown"]:,.2f}'
            })
        
        # Check daily loss (simplified - would need actual daily calculation)
        if account['daily_loss_counter'] > account['daily_loss_limit']:
            violations.append({
                'type': 'daily_loss',
                'description': f'Daily loss ${account["daily_loss_counter"]:,.2f} exceeds limit ${account["daily_loss_limit"]:,.2f}'
            })
        
        # Check account status
        if account['status'] == 'violation':
            violations.append({
                'type': 'account_status',
                'description': 'Account is currently in violation status'
            })
        
        cur.close()
        conn.close()
        
        return jsonify({
            'account_id': account_id,
            'violations': violations,
            'compliant': len(violations) == 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Reports
@app.route('/api/prop-firm/daily-summary', methods=['GET'])
def get_daily_summary():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get today's summary (simplified)
        cur.execute("""
            SELECT 
                SUM(daily_pnl) as total_pnl,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as accounts_trading,
                0 as active_trades
            FROM prop_accounts
        """)
        summary = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return jsonify(dict(summary))
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prop-firm/payout-eligibility', methods=['GET'])
def get_payout_eligibility():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get accounts eligible for payout (simplified logic)
        cur.execute("""
            SELECT 
                pa.account_id,
                (pa.equity - pa.balance) as profit,
                CASE 
                    WHEN pa.equity > pa.balance AND pa.status = 'active' 
                    THEN TRUE 
                    ELSE FALSE 
                END as eligible
            FROM prop_accounts pa
            WHERE pa.equity > pa.balance
            ORDER BY profit DESC
        """)
        payouts = cur.fetchall()
        
        # Calculate payout amounts
        result = []
        for payout in payouts:
            amount = float(payout['profit']) * 0.8  # 80% split
            result.append({
                'account_id': payout['account_id'],
                'amount': amount,
                'eligible': payout['eligible']
            })
        
        cur.close()
        conn.close()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add route to serve the HTML page
@app.route('/prop-firm-management')
def prop_firm_management():
    return send_from_directory('.', 'prop_firm_management.html')

# Utility function to update account equity (for future webhook integration)
def update_account_equity(account_id, new_equity, pnl_change):
    """Update account equity and check for violations"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get current account state
        cur.execute("""
            SELECT pa.*, pf.max_drawdown, pf.daily_loss_limit
            FROM prop_accounts pa
            JOIN prop_firms pf ON pa.firm_id = pf.id
            WHERE pa.account_id = %s
        """, (account_id,))
        
        account = cur.fetchone()
        if not account:
            return False
        
        # Update peak equity if new high
        new_peak = max(account['peak_equity'], new_equity)
        
        # Update daily PnL counter
        new_daily_pnl = account['daily_pnl'] + pnl_change
        
        # Calculate new drawdown
        new_drawdown = new_peak - new_equity
        
        # Update account
        cur.execute("""
            UPDATE prop_accounts 
            SET equity = %s, peak_equity = %s, daily_pnl = %s, 
                current_drawdown = %s, updated_at = CURRENT_TIMESTAMP
            WHERE account_id = %s
        """, (new_equity, new_peak, new_daily_pnl, new_drawdown, account_id))
        
        # Check for violations
        violations = []
        
        if new_drawdown > account['max_drawdown']:
            violations.append(('drawdown', f'Drawdown ${new_drawdown:,.2f} exceeds limit'))
        
        if new_daily_pnl < -account['daily_loss_limit']:
            violations.append(('daily_loss', f'Daily loss ${abs(new_daily_pnl):,.2f} exceeds limit'))
        
        # Insert violations
        for violation_type, description in violations:
            cur.execute("""
                INSERT INTO prop_violations (account_id, firm_id, violation_type, description, violation_amount, limit_amount)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                account_id, 
                account['firm_id'], 
                violation_type, 
                description,
                new_drawdown if violation_type == 'drawdown' else abs(new_daily_pnl),
                account['max_drawdown'] if violation_type == 'drawdown' else account['daily_loss_limit']
            ))
        
        # Update account status if violations
        if violations:
            cur.execute("""
                UPDATE prop_accounts 
                SET status = 'violation' 
                WHERE account_id = %s
            """, (account_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error updating account equity: {e}")
        return False