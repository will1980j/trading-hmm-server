#!/usr/bin/env python3
"""
Remove all webhook/telemetry code from indicator, keeping only export system.
This reduces complexity to allow compilation.
"""

import re

def remove_webhook_code():
    """Remove all webhook code from the indicator."""
    
    with open('complete_automated_trading_system.pine', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    skip_until = None
    
    for i, line in enumerate(lines):
        # Skip telemetry configuration inputs
        if 'telemetry_schema_version' in line or 'telemetry_engine_version' in line or \
           'telemetry_strategy_name' in line or 'telemetry_strategy_id' in line or \
           'telemetry_strategy_version' in line or 'telemetry_symbol_override' in line:
            continue
        
        # Skip telemetry variable declarations
        if line.strip().startswith('var bool telemetry_') or \
           line.strip().startswith('var string telemetry_') or \
           line.strip().startswith('var int telemetry_') or \
           line.strip().startswith('var float telemetry_'):
            continue
        
        # Skip webhook tracking arrays
        if 'active_signal_ids' in line or 'active_signal_indices' in line or \
           'be_trigger_sent_flags' in line or 'completion_sent_flags' in line or \
           'be_exit_sent_flags' in line or 'sl_exit_sent_flags' in line or \
           'webhook_sent_this_bar' in line:
            continue
        
        # Skip helper function definitions (but keep f_buildTradeId, f_isoTimestamp, f_sessionLabel, f_calcMaeR)
        if skip_until:
            if skip_until in line:
                skip_until = None
            continue
        
        if line.strip().startswith('f_buildPayload('):
            skip_until = '// END'
            continue
        if line.strip().startswith('f_targetsJson('):
            skip_until = '// END'
            continue
        if line.strip().startswith('f_setupJson('):
            skip_until = '// END'
            continue
        if line.strip().startswith('f_marketStateJson('):
            skip_until = '// END'
            continue
        if line.strip().startswith('jsonField('):
            skip_until = '// END'
            continue
        if line.strip().startswith('jsonWrap('):
            skip_until = '// END'
            continue
        
        # Comment out webhook alert() calls (but keep export alerts)
        if 'alert(' in line and 'INDICATOR_EXPORT' not in line and 'ALL_SIGNALS_EXPORT' not in line:
            # Check if this is a webhook alert (not export)
            if 'SIGNAL_CREATED' in line or 'CANCELLED' in line or 'ENTRY' in line or \
               'HEARTBEAT' in line or 'MFE_UPDATE' in line or 'BE_TRIGGERED' in line or \
               'EXIT_BE' in line or 'EXIT_SL' in line:
                new_lines.append('    // REMOVED: ' + line.strip())
                continue
        
        # Skip telemetry initialization blocks
        if '// ============================================================================' in line:
            next_line = lines[i+1] if i+1 < len(lines) else ''
            if 'TELEMETRY ENGINE' in next_line:
                skip_until = '// END TELEMETRY'
                continue
        
        # Skip webhook logic blocks
        if 'SIGNAL_CREATED WEBHOOKS' in line or 'CANCELLED SIGNAL WEBHOOKS' in line or \
           'SIGNAL CREATION WEBHOOK' in line or 'MFE UPDATE WEBHOOK' in line or \
           'BE TRIGGER WEBHOOK' in line or 'DUAL EXIT WEBHOOKS' in line:
            skip_until = '// ============================================================================'
            continue
        
        new_lines.append(line)
    
    # Write back
    with open('complete_automated_trading_system_SIMPLIFIED.pine', 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ Webhook code removed successfully!")
    print(f"Original lines: {len(lines)}")
    print(f"New lines: {len(new_lines)}")
    print(f"Removed: {len(lines) - len(new_lines)} lines")
    print("\nNew file: complete_automated_trading_system_SIMPLIFIED.pine")

if __name__ == '__main__':
    remove_webhook_code()
