#!/usr/bin/env python3
"""Remove webhook/telemetry code but KEEP export system."""

def clean_indicator():
    with open('complete_automated_trading_system.pine', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    cleaned = []
    skip_until_marker = None
    in_export_section = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Detect export sections - NEVER skip these
        if 'EXPORT V2 - BULLETPROOF SYSTEM' in line or 'ALL SIGNALS EXPORT V2' in line:
            in_export_section = True
        
        # Exit export section when we hit table code
        if in_export_section and 'SIGNAL LIST TABLE' in line:
            in_export_section = False
        
        # If in export section, always keep
        if in_export_section:
            cleaned.append(line)
            i += 1
            continue
        
        # Skip mode - looking for end marker
        if skip_until_marker:
            if skip_until_marker in line:
                skip_until_marker = None
            i += 1
            continue
        
        # Remove telemetry config
        if any(x in line for x in ['telemetry_schema_version', 'telemetry_engine_version',
                                     'telemetry_strategy_name', 'telemetry_strategy_id',
                                     'telemetry_strategy_version', 'telemetry_symbol_override']):
            if 'input.string' in line or 'input.symbol' in line:
                i += 1
                continue
        
        # Remove telemetry variables
        if line.strip().startswith('var') and 'telemetry_' in line:
            i += 1
            continue
        
        # Remove webhook tracking arrays
        if any(x in line for x in ['active_signal_ids', 'active_signal_indices',
                                     'be_trigger_sent_flags', 'completion_sent_flags',
                                     'be_exit_sent_flags', 'sl_exit_sent_flags']):
            if 'array.new' in line or 'var array' in line or 'var bool webhook_sent' in line:
                i += 1
                continue
        
        # Remove helper functions (but keep essential ones)
        if line.strip().startswith('f_buildPayload('):
            skip_until_marker = 'jsonWrap(p)'
            i += 1
            continue
        
        if line.strip().startswith('f_targetsJson(') or line.strip().startswith('f_setupJson(') or \
           line.strip().startswith('f_marketStateJson('):
            # Skip to next blank line
            while i < len(lines) and lines[i].strip() != '':
                i += 1
            continue
        
        if line.strip().startswith('jsonField(') or line.strip().startswith('jsonWrap('):
            # Skip to next blank line
            while i < len(lines) and lines[i].strip() != '':
                i += 1
            continue
        
        # Remove f_symbol (only for webhooks)
        if 'f_symbol()' in line and '=>' in line:
            while i < len(lines) and 'telemetry_symbol_override' not in lines[i]:
                i += 1
            i += 1  # Skip the line with telemetry_symbol_override too
            continue
        
        # Remove TELEMETRY ENGINE sections
        if 'TELEMETRY ENGINE' in line and '========' in line:
            skip_until_marker = '// END TELEMETRY'
            i += 1
            continue
        
        # Remove webhook sections
        if 'SIGNAL_CREATED WEBHOOKS' in line:
            skip_until_marker = '// CANCELLED SIGNAL WEBHOOKS'
            i += 1
            continue
        
        if 'CANCELLED SIGNAL WEBHOOKS' in line:
            skip_until_marker = '// 1. SIGNAL CREATION WEBHOOK'
            i += 1
            continue
        
        if '// 1. SIGNAL CREATION WEBHOOK' in line:
            skip_until_marker = '// TEST: Send heartbeat'
            i += 1
            continue
        
        if '// TEST: Send heartbeat' in line:
            # Skip heartbeat block (next 3-4 lines)
            i += 1
            while i < len(lines) and lines[i].strip() != '' and '// 2.' not in lines[i]:
                i += 1
            continue
        
        if '// 2. MFE UPDATE WEBHOOK' in line:
            skip_until_marker = '// ============================================================================\n// TELEMETRY ENGINE'
            i += 1
            continue
        
        if '// 3. BE TRIGGER WEBHOOK' in line:
            skip_until_marker = '// 4. DUAL EXIT WEBHOOKS'
            i += 1
            continue
        
        if '// 4. DUAL EXIT WEBHOOKS' in line:
            skip_until_marker = '// ============================================================================\n// TELEMETRY ENGINE — SAFETY RESET'
            i += 1
            continue
        
        # Remove find_signal_index helper
        if 'find_signal_index(' in line and 'int found_index' in (lines[i+1] if i+1 < len(lines) else ''):
            while i < len(lines) and 'found_index' not in lines[i]:
                i += 1
            i += 1  # Skip the return line too
            continue
        
        # Remove telemetry assignments
        if 'telemetry_' in line and ':=' in line:
            i += 1
            continue
        
        # Keep everything else
        cleaned.append(line)
        i += 1
    
    # Write cleaned version
    with open('complete_automated_trading_system.pine', 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned))
    
    print(f"✅ Cleaned indicator (preserved export system)!")
    print(f"   Original: {len(lines)} lines")
    print(f"   Cleaned: {len(cleaned)} lines")
    print(f"   Removed: {len(lines) - len(cleaned)} lines ({100*(len(lines)-len(cleaned))/len(lines):.1f}%)")

if __name__ == '__main__':
    clean_indicator()
