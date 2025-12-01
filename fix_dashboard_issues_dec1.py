#!/usr/bin/env python3
"""
Fix Dashboard Issues - December 1, 2025

Issues to fix:
1. signal_date/signal_time using CURRENT_DATE/CURRENT_TIME instead of webhook values
2. MFE values not being stored properly on MFE_UPDATE events
3. Session not being propagated to MFE_UPDATE events
4. Dashboard query not returning proper fields for Age calculation
"""

import re

def fix_web_server():
    with open('web_server.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # FIX 1: handle_entry_signal - Use webhook signal_date/signal_time instead of CURRENT_DATE/CURRENT_TIME
    # Find the INSERT statement and fix it
    
    # The current code has:
    # signal_date,
    # signal_time,
    # timestamp
    # ) VALUES (
    # ...
    # CURRENT_DATE,
    # CURRENT_TIME,
    # NOW()
    
    # We need to change it to use the actual values from the webhook
    
    old_insert_values = '''                NULL,
                0,
                0,
                0,
                NULL,
                0,
                CURRENT_DATE,
                CURRENT_TIME,
                NOW()'''
    
    new_insert_values = '''                NULL,
                0,
                0,
                0,
                NULL,
                0,
                %(signal_date)s,
                %(signal_time)s,
                NOW()'''
    
    if old_insert_values in content:
        content = content.replace(old_insert_values, new_insert_values)
        print("✅ Fixed INSERT to use webhook signal_date/signal_time")
    else:
        print("⚠️ Could not find INSERT values pattern to fix")
    
    # FIX 2: Add signal_date and signal_time to params dict
    old_params = '''        params = {
            "trade_id": trade_id,
            "direction": direction,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "risk_distance": risk_distance,
            "targets": dumps(targets) if targets else None,
            "session": session,
            "bias": bias or direction
        }'''
    
    new_params = '''        # Parse signal_date and signal_time from webhook
        parsed_signal_date = None
        parsed_signal_time = None
        if signal_date:
            try:
                from datetime import datetime as dt
                parsed_signal_date = dt.strptime(signal_date, '%Y-%m-%d').date()
            except:
                parsed_signal_date = None
        if signal_time:
            try:
                from datetime import datetime as dt
                parsed_signal_time = dt.strptime(signal_time, '%H:%M:%S').time()
            except:
                parsed_signal_time = None
        
        params = {
            "trade_id": trade_id,
            "direction": direction,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "risk_distance": risk_distance,
            "targets": dumps(targets) if targets else None,
            "session": session,
            "bias": bias or direction,
            "signal_date": parsed_signal_date,
            "signal_time": parsed_signal_time
        }'''
    
    if old_params in content:
        content = content.replace(old_params, new_params)
        print("✅ Fixed params to include signal_date/signal_time")
    else:
        print("⚠️ Could not find params pattern to fix")
    
    # FIX 3: Fix handle_mfe_update to store be_mfe and no_be_mfe properly
    # Find the handle_mfe_update function and ensure it stores the MFE values
    
    # Search for the MFE_UPDATE INSERT statement
    mfe_update_pattern = r'(def handle_mfe_update\(data\):.*?)(def handle_be_trigger)'
    match = re.search(mfe_update_pattern, content, re.DOTALL)
    
    if match:
        mfe_func = match.group(1)
        # Check if it's inserting be_mfe and no_be_mfe
        if 'be_mfe' not in mfe_func or 'INSERT INTO automated_signals' not in mfe_func:
            print("⚠️ handle_mfe_update may need manual review")
        else:
            print("✅ handle_mfe_update appears to have be_mfe fields")
    
    # FIX 4: Update dashboard query to return signal_time for Age calculation
    # The current query already returns signal_date and signal_time, but let's verify
    # and ensure the frontend gets what it needs
    
    # Check if dashboard query includes signal_time
    if 'e.signal_date, e.signal_time' in content:
        print("✅ Dashboard query already includes signal_date and signal_time")
    else:
        print("⚠️ Dashboard query may need signal_date/signal_time fields")
    
    if content != original:
        with open('web_server.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("\n✅ web_server.py updated successfully")
        return True
    else:
        print("\n⚠️ No changes made to web_server.py")
        return False

if __name__ == '__main__':
    fix_web_server()
