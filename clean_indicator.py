#!/usr/bin/env python3
"""Remove all webhook/telemetry code from indicator."""

def clean_indicator():
    with open('complete_automated_trading_system.pine', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    cleaned = []
    skip_mode = None
    skip_count = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Skip telemetry config inputs (lines 1455-1462)
        if 'telemetry_schema_version' in line or 'telemetry_engine_version' in line or \
           'telemetry_strategy_name' in line or 'telemetry_strategy_id' in line or \
           'telemetry_strategy_version' in line or 'telemetry_symbol_override' in line:
            i += 1
            continue
        
        # Skip telemetry variables (around line 230-250)
        if line.strip().startswith('var') and 'telemetry_' in line:
            i += 1
            continue
        
        # Skip webhook tracking arrays
        if 'active_signal_ids' in line or 'active_signal_indices' in line or \
           'be_trigger_sent_flags' in line or 'completion_sent_flags' in line or \
           'be_exit_sent_flags' in line or 'sl_exit_sent_flags' in line:
            if 'array.new' in line or 'var array' in line or 'var bool webhook_sent' in line:
                i += 1
                continue
        
        # Detect and skip large function blocks
        if skip_mode:
            if skip_mode in line:
                skip_mode = None
            i += 1
            continue
        
        # Skip f_buildPayload function (huge, only for webhooks)
        if line.strip().startswith('f_buildPayload('):
            skip_mode = 'jsonWrap(p)'
            i += 1
            continue
        
        # Skip other webhook helper functions
        if line.strip().startswith('f_targetsJson(') or line.strip().startswith('f_setupJson(') or \
           line.strip().startswith('f_marketStateJson(') or line.strip().startswith('jsonField(') or \
           line.strip().startswith('jsonWrap('):
            # Skip until next function or section
            skip_mode = '\n\n'
            i += 1
            continue
        
        # Skip f_symbol function (only for webhooks)
        if 'f_symbol()' in line and '=>' in line:
            skip_mode = 'telemetry_symbol_override'
            i += 1
            continue
        
        # Skip TELEMETRY sections
        if '// TELEMETRY' in line.upper() and '========' in line:
            # Look ahead to find end marker
            skip_mode = '// END TELEMETRY'
            i += 1
            continue
        
        # Skip webhook alert blocks
        if '// SIGNAL_CREATED WEBHOOKS' in line or '// CANCELLED SIGNAL WEBHOOKS' in line:
            skip_mode = '// ========='
            i += 1
            continue
        
        # Skip main webhook sections
        if '// 1. SIGNAL CREATION WEBHOOK' in line:
            skip_mode = '// TEST: Send heartbeat'
            i += 1
            continue
        
        # Skip heartbeat
        if '// TEST: Send heartbeat' in line:
            # Skip next 3 lines
            i += 4
            continue
        
        # Skip MFE UPDATE WEBHOOK section
        if '// 2. MFE UPDATE WEBHOOK' in line:
            skip_mode = '// ============================================================================\n// TELEMETRY ENGINE'
            i += 1
            continue
        
        # Skip BE TRIGGER WEBHOOK section
        if '// 3. BE TRIGGER WEBHOOK' in line:
            skip_mode = '// 4. DUAL EXIT WEBHOOKS'
            i += 1
            continue
        
        # Skip DUAL EXIT WEBHOOKS section
        if '// 4. DUAL EXIT WEBHOOKS' in line:
            skip_mode = '// ============================================================================\n// TELEMETRY ENGINE — SAFETY RESET'
            i += 1
            continue
        
        # Skip telemetry safety reset
        if 'TELEMETRY ENGINE — SAFETY RESET' in line:
            skip_mode = '// END TELEMETRY SAFETY RESET'
            i += 1
            continue
        
        # Skip individual alert calls (but keep export alerts)
        if 'alert(' in line and 'EXPORT' not in line:
            # Check if it's a webhook alert
            if any(x in line for x in ['signal_payload', 'cancel_payload', 'entry_payload', 
                                        'heartbeat', 'batch_envelope', 'debug_batch',
                                        'be_trigger_payload', 'be_payload', 'sl_payload',
                                        'exit_be_payload', 'exit_sl_payload']):
                i += 1
                continue
        
        # Skip telemetry initialization blocks
        if 'telemetry_active :=' in line or 'telemetry_trade_id :=' in line:
            # Skip until we see something that's not telemetry
            while i < len(lines) and ('telemetry_' in lines[i] or lines[i].strip() == ''):
                i += 1
            continue
        
        # Skip find_signal_index helper function
        if 'find_signal_index(' in line and 'int found_index' in lines[i+1] if i+1 < len(lines) else False:
            skip_mode = '    found_index'
            i += 1
            continue
        
        # Keep this line
        cleaned.append(line)
        i += 1
    
    # Write cleaned version
    with open('complete_automated_trading_system.pine', 'w', encoding='utf-8') as f:
        f.writelines(cleaned)
    
    print(f"✅ Cleaned indicator!")
    print(f"   Original: {len(lines)} lines")
    print(f"   Cleaned: {len(cleaned)} lines")
    print(f"   Removed: {len(lines) - len(cleaned)} lines ({100*(len(lines)-len(cleaned))/len(lines):.1f}%)")

if __name__ == '__main__':
    clean_indicator()
