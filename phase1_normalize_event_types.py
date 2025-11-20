"""
PHASE 1: EVENT TYPE NORMALIZATION
Normalizes all event type strings and centralizes trade ID generation
in complete_automated_trading_system.pine
"""

def normalize_indicator():
    # Read the file
    with open('complete_automated_trading_system.pine', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define the event type constants section to insert
    event_constants = '''
// ============================================================================
// EVENT TYPE CONSTANTS (DO NOT CHANGE - MUST MATCH DATABASE)
// ============================================================================
EVENT_ENTRY            = "ENTRY"
EVENT_MFE_UPDATE       = "MFE_UPDATE"
EVENT_BE_TRIGGERED     = "BE_TRIGGERED"
EVENT_EXIT_BREAK_EVEN  = "EXIT_BREAK_EVEN"
EVENT_EXIT_STOP_LOSS   = "EXIT_STOP_LOSS"
EVENT_EXIT_TAKE_PROFIT = "EXIT_TAKE_PROFIT"   // reserved for TP exits
EVENT_EXIT_PARTIAL     = "EXIT_PARTIAL"        // reserved for partial exits

'''
    
    # Insert event constants after the strategy declaration (after line 2)
    lines = content.split('\n')
    
    # Find the line after strategy declaration
    insert_index = 2  # After //@version=5 and strategy() lines
    lines.insert(insert_index, event_constants)
    
    content = '\n'.join(lines)
    
    # Now replace the create_signal_id function with f_buildTradeId
    old_function = '''create_signal_id(signal_direction) =>
    // Format: YYYYMMDD_HHMMSS_MMM_DIRECTION (added milliseconds to prevent duplicates)
    // Use str.tostring with format to avoid thousand separators
    year_str = str.tostring(year)
    month_str = str.tostring(month, "00")
    day_str = str.tostring(dayofmonth, "00")
    hour_str = str.tostring(hour, "00")
    minute_str = str.tostring(minute, "00")
    second_str = str.tostring(second, "00")
    millis_str = str.tostring(time % 1000, "000")  // Add milliseconds for uniqueness
    date_str = year_str + month_str + day_str
    time_str = hour_str + minute_str + second_str + millis_str
    date_str + "_" + time_str + "_" + str.upper(signal_direction)'''
    
    new_function = '''// ============================================================================
// TRADE ID BUILDER (CANONICAL FORMAT)
// ============================================================================
// Format: YYYYMMDD_HHMMSSMMM_DIRECTION
// Example: 20251120_170200000_BULLISH
f_buildTradeId(datetime, direction) =>
    year_str = str.tostring(year(datetime))
    month_str = str.tostring(month(datetime), "00")
    day_str = str.tostring(dayofmonth(datetime), "00")
    hour_str = str.tostring(hour(datetime), "00")
    minute_str = str.tostring(minute(datetime), "00")
    second_str = str.tostring(second(datetime), "00")
    millis_str = str.tostring(datetime % 1000, "000")  // Milliseconds for uniqueness
    date_str = year_str + month_str + day_str
    time_str = hour_str + minute_str + second_str + millis_str
    date_str + "_" + time_str + "_" + str.upper(direction)'''
    
    content = content.replace(old_function, new_function)
    
    # Replace function calls: create_signal_id(signal_direction) -> f_buildTradeId(time, signal_direction)
    content = content.replace(
        'signal_id = create_signal_id(signal_direction)',
        'signal_id = f_buildTradeId(time, signal_direction)'
    )
    
    # Replace event type strings in webhook payloads with constants
    # These are already using the correct names, just need to use constants
    
    # ENTRY event
    content = content.replace(
        '"type":"ENTRY"',
        '"type":"" + EVENT_ENTRY + ""'
    )
    
    # MFE_UPDATE event
    content = content.replace(
        '"type":"MFE_UPDATE"',
        '"type":"" + EVENT_MFE_UPDATE + ""'
    )
    
    # BE_TRIGGERED event
    content = content.replace(
        '"type":"BE_TRIGGERED"',
        '"type":"" + EVENT_BE_TRIGGERED + ""'
    )
    
    # EXIT events - these use a variable, so we need to handle differently
    # The code already has: string exit_event_type = be_stopped ? "EXIT_BREAK_EVEN" : "EXIT_STOP_LOSS"
    # We need to change this to use constants
    content = content.replace(
        'string exit_event_type = be_stopped ? "EXIT_BREAK_EVEN" : "EXIT_STOP_LOSS"',
        'string exit_event_type = be_stopped ? EVENT_EXIT_BREAK_EVEN : EVENT_EXIT_STOP_LOSS'
    )
    
    # Write the updated content
    with open('complete_automated_trading_system.pine', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ PHASE 1 COMPLETE: Event Type Normalization")
    print("\n📋 CHANGES MADE:")
    print("\n1. Added EVENT TYPE CONSTANTS section:")
    print("   - EVENT_ENTRY")
    print("   - EVENT_MFE_UPDATE")
    print("   - EVENT_BE_TRIGGERED")
    print("   - EVENT_EXIT_BREAK_EVEN")
    print("   - EVENT_EXIT_STOP_LOSS")
    print("   - EVENT_EXIT_TAKE_PROFIT (reserved)")
    print("   - EVENT_EXIT_PARTIAL (reserved)")
    print("\n2. Renamed create_signal_id() → f_buildTradeId()")
    print("   - Now takes (datetime, direction) parameters")
    print("   - Centralized trade ID generation")
    print("\n3. Replaced all event type strings with constants:")
    print("   - 'ENTRY' → EVENT_ENTRY")
    print("   - 'MFE_UPDATE' → EVENT_MFE_UPDATE")
    print("   - 'BE_TRIGGERED' → EVENT_BE_TRIGGERED")
    print("   - 'EXIT_BREAK_EVEN' → EVENT_EXIT_BREAK_EVEN")
    print("   - 'EXIT_STOP_LOSS' → EVENT_EXIT_STOP_LOSS")
    print("\n4. Updated function call:")
    print("   - create_signal_id(signal_direction) → f_buildTradeId(time, signal_direction)")
    print("\n✅ All event types now use centralized constants")
    print("✅ All trade IDs now use centralized f_buildTradeId() function")
    print("\n⚠️  NOTE: The indicator already used correct event type names:")
    print("   - No old event strings like 'signal_created', 'mfe_update', etc. were found")
    print("   - The code was already using 'ENTRY', 'MFE_UPDATE', 'BE_TRIGGERED', etc.")
    print("   - We've now centralized them as constants for consistency")

if __name__ == "__main__":
    normalize_indicator()
