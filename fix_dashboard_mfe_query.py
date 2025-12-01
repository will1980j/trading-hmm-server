#!/usr/bin/env python3
"""
Fix Dashboard MFE Query - December 1, 2025

The handle_mfe_update function UPDATES the ENTRY row's be_mfe/no_be_mfe columns.
But the dashboard query looks for separate MFE_UPDATE event rows.

Fix: Change dashboard query to get MFE values directly from the ENTRY row.
"""

def fix_dashboard_query():
    with open('web_server.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # The current query uses a CTE to join MFE_UPDATE events
    # But MFE values are stored on the ENTRY row itself
    
    old_query = '''        # Get all ENTRY signals with latest MFE values (active trades)
        cursor.execute("""
            WITH latest_mfe AS (
                SELECT DISTINCT ON (trade_id) 
                    trade_id, be_mfe, no_be_mfe
                FROM automated_signals
                WHERE event_type = 'MFE_UPDATE'
                ORDER BY trade_id, timestamp DESC
            ),
            trade_direction AS (
                SELECT DISTINCT ON (trade_id)
                    trade_id, direction, entry_price, stop_loss, session, bias
                FROM automated_signals
                WHERE direction IS NOT NULL
                ORDER BY trade_id, timestamp ASC
            )
            SELECT e.id, e.trade_id, e.event_type, 
                   COALESCE(e.direction, d.direction) as direction,
                   COALESCE(e.entry_price, d.entry_price) as entry_price,
                   COALESCE(e.stop_loss, d.stop_loss) as stop_loss,
                   COALESCE(e.session, d.session) as session,
                   COALESCE(e.bias, d.bias) as bias,
                   e.timestamp, e.signal_date, e.signal_time,
                   COALESCE(m.be_mfe, 0.0) as be_mfe,
                   COALESCE(m.no_be_mfe, 0.0) as no_be_mfe
            FROM automated_signals e
            LEFT JOIN latest_mfe m ON e.trade_id = m.trade_id
            LEFT JOIN trade_direction d ON e.trade_id = d.trade_id
            WHERE e.event_type = 'ENTRY'
            AND NOT EXISTS (
                SELECT 1 FROM automated_signals ex
                WHERE ex.trade_id = e.trade_id
                AND ex.event_type LIKE 'EXIT_%'
            )
            ORDER BY e.timestamp DESC
            LIMIT 100
        """)'''
    
    # New query: Get MFE directly from ENTRY row (where handle_mfe_update stores it)
    new_query = '''        # Get all ENTRY signals with MFE values (active trades)
        # NOTE: MFE values are stored directly on the ENTRY row by handle_mfe_update
        cursor.execute("""
            SELECT e.id, e.trade_id, e.event_type, 
                   e.direction,
                   e.entry_price,
                   e.stop_loss,
                   e.session,
                   e.bias,
                   e.timestamp, 
                   e.signal_date, 
                   e.signal_time,
                   COALESCE(e.be_mfe, 0.0) as be_mfe,
                   COALESCE(e.no_be_mfe, 0.0) as no_be_mfe,
                   e.current_price
            FROM automated_signals e
            WHERE e.event_type = 'ENTRY'
            AND NOT EXISTS (
                SELECT 1 FROM automated_signals ex
                WHERE ex.trade_id = e.trade_id
                AND ex.event_type LIKE 'EXIT_%'
            )
            ORDER BY e.timestamp DESC
            LIMIT 100
        """)'''
    
    if old_query in content:
        content = content.replace(old_query, new_query)
        print("✅ Fixed active trades query to get MFE from ENTRY row")
    else:
        print("⚠️ Could not find active trades query pattern")
        # Try a more flexible search
        if 'WITH latest_mfe AS' in content and 'event_type = \'MFE_UPDATE\'' in content:
            print("   Found MFE_UPDATE CTE - needs manual fix")
    
    # Also fix the result parsing to match new query
    old_parsing = '''        active_trades = []
        for row in cursor.fetchall():
            active_trades.append({
                "id": row[0],
                "trade_id": row[1],
                "event_type": row[2],
                "direction": row[3],
                "entry_price": float(row[4]) if row[4] else None,
                "stop_loss": float(row[5]) if row[5] else None,
                "session": row[6],
                "bias": row[7],
                "timestamp": row[8].isoformat() if row[8] else None,
                "date": row[9].isoformat() if row[9] else None,
                "time": row[10].isoformat() if row[10] else None,
                "be_mfe": float(row[11]) if row[11] is not None else 0.0,
                "no_be_mfe": float(row[12]) if row[12] is not None else 0.0,
                "status": "ACTIVE",
                "trade_status": "ACTIVE"
            })'''
    
    new_parsing = '''        active_trades = []
        for row in cursor.fetchall():
            active_trades.append({
                "id": row[0],
                "trade_id": row[1],
                "event_type": row[2],
                "direction": row[3],
                "entry_price": float(row[4]) if row[4] else None,
                "stop_loss": float(row[5]) if row[5] else None,
                "session": row[6],
                "bias": row[7],
                "timestamp": row[8].isoformat() if row[8] else None,
                "signal_date": row[9].isoformat() if row[9] else None,
                "signal_time": row[10].isoformat() if row[10] else None,
                "be_mfe": float(row[11]) if row[11] is not None else 0.0,
                "no_be_mfe": float(row[12]) if row[12] is not None else 0.0,
                "current_price": float(row[13]) if row[13] else None,
                "status": "ACTIVE",
                "trade_status": "ACTIVE"
            })'''
    
    if old_parsing in content:
        content = content.replace(old_parsing, new_parsing)
        print("✅ Fixed active trades result parsing")
    else:
        print("⚠️ Could not find active trades parsing pattern")
    
    # Fix completed trades query too - get final MFE from EXIT row
    old_completed = '''        # Get all EXIT signals (completed trades) with MFE values
        cursor.execute("""
            WITH trade_direction AS (
                SELECT DISTINCT ON (trade_id)
                    trade_id, direction, entry_price, stop_loss, session, bias
                FROM automated_signals
                WHERE direction IS NOT NULL
                ORDER BY trade_id, timestamp ASC
            )
            SELECT e.id, e.trade_id, e.event_type,
                   COALESCE(e.direction, d.direction) as direction,
                   COALESCE(e.entry_price, d.entry_price) as entry_price,
                   COALESCE(e.stop_loss, d.stop_loss) as stop_loss,
                   COALESCE(e.session, d.session) as session,
                   COALESCE(e.bias, d.bias) as bias,
                   e.timestamp, 
                   COALESCE(e.be_mfe, 0.0) as be_mfe,
                   COALESCE(e.no_be_mfe, 0.0) as no_be_mfe
            FROM automated_signals e
            LEFT JOIN trade_direction d ON e.trade_id = d.trade_id
            WHERE e.event_type LIKE 'EXIT_%'
            ORDER BY e.timestamp DESC
            LIMIT 100
        """)'''
    
    new_completed = '''        # Get all EXIT signals (completed trades) with MFE values
        # Join with ENTRY to get signal_date, signal_time, and entry details
        cursor.execute("""
            SELECT ex.id, ex.trade_id, ex.event_type,
                   COALESCE(en.direction, ex.direction) as direction,
                   COALESCE(en.entry_price, ex.entry_price) as entry_price,
                   COALESCE(en.stop_loss, ex.stop_loss) as stop_loss,
                   COALESCE(en.session, ex.session) as session,
                   COALESCE(en.bias, ex.bias) as bias,
                   ex.timestamp as exit_timestamp,
                   en.signal_date,
                   en.signal_time,
                   en.timestamp as entry_timestamp,
                   COALESCE(ex.be_mfe, en.be_mfe, 0.0) as be_mfe,
                   COALESCE(ex.no_be_mfe, en.no_be_mfe, 0.0) as no_be_mfe,
                   COALESCE(ex.final_mfe, ex.no_be_mfe, en.no_be_mfe, 0.0) as final_mfe
            FROM automated_signals ex
            LEFT JOIN automated_signals en ON ex.trade_id = en.trade_id AND en.event_type = 'ENTRY'
            WHERE ex.event_type LIKE 'EXIT_%%'
            ORDER BY ex.timestamp DESC
            LIMIT 100
        """)'''
    
    if old_completed in content:
        content = content.replace(old_completed, new_completed)
        print("✅ Fixed completed trades query")
    else:
        print("⚠️ Could not find completed trades query pattern")
    
    # Fix completed trades parsing
    old_completed_parsing = '''        completed_trades = []
        for row in cursor.fetchall():
            completed_trades.append({
                "id": row[0],
                "trade_id": row[1],
                "event_type": row[2],
                "direction": row[3],
                "entry_price": float(row[4]) if row[4] else None,
                "stop_loss": float(row[5]) if row[5] else None,
                "session": row[6],
                "bias": row[7],
                "timestamp": row[8].isoformat() if row[8] else None,
                "be_mfe": float(row[9]) if row[9] is not None else 0.0,
                "no_be_mfe": float(row[10]) if row[10] is not None else 0.0,
                "status": "COMPLETED",
                "trade_status": "COMPLETED"
            })'''
    
    new_completed_parsing = '''        completed_trades = []
        for row in cursor.fetchall():
            completed_trades.append({
                "id": row[0],
                "trade_id": row[1],
                "event_type": row[2],
                "direction": row[3],
                "entry_price": float(row[4]) if row[4] else None,
                "stop_loss": float(row[5]) if row[5] else None,
                "session": row[6],
                "bias": row[7],
                "exit_timestamp": row[8].isoformat() if row[8] else None,
                "signal_date": row[9].isoformat() if row[9] else None,
                "signal_time": row[10].isoformat() if row[10] else None,
                "entry_timestamp": row[11].isoformat() if row[11] else None,
                "be_mfe": float(row[12]) if row[12] is not None else 0.0,
                "no_be_mfe": float(row[13]) if row[13] is not None else 0.0,
                "final_mfe": float(row[14]) if row[14] is not None else 0.0,
                "status": "COMPLETED",
                "trade_status": "COMPLETED"
            })'''
    
    if old_completed_parsing in content:
        content = content.replace(old_completed_parsing, new_completed_parsing)
        print("✅ Fixed completed trades result parsing")
    else:
        print("⚠️ Could not find completed trades parsing pattern")
    
    if content != original:
        with open('web_server.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("\n✅ web_server.py updated successfully")
        return True
    else:
        print("\n⚠️ No changes made to web_server.py")
        return False

if __name__ == '__main__':
    fix_dashboard_query()
