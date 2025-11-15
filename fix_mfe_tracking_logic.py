"""
Fix MFE tracking logic in complete_automated_trading_system.pine

Issues:
1. Stop detection only runs when track_be_mfe = true
2. Completion logic uses wrong conditions when track_be_mfe = false
3. All trades showing as completed incorrectly

Solution:
- Make stop detection run ALWAYS (not conditional on track_be_mfe)
- Fix completion logic to use tracked flags consistently
- Separate BE tracking from basic stop loss detection
"""

# Read the indicator file
with open('complete_automated_trading_system.pine', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Make No BE stop detection run ALWAYS (around line 646-656)
old_no_be_stop_bull = """        // FIRST: Update stopped flags on ALL bars (not just incomplete trades)
        // CRITICAL: Flag updates run regardless of is_recent to ensure historical completion detection
        // CRITICAL FIX: Only check stops AFTER trade has entered (not on confirmation bar)
        if sig_has_entered and sig_dir == "Bullish"
            // Check if No BE strategy should be stopped out (original SL hit)
            if track_be_mfe and not sig_no_be_stopped
                if low <= sig_stop
                    array.set(signal_no_be_stopped, i, true)
                    sig_no_be_stopped := true
                    // CRITICAL: If original SL hit BEFORE BE triggered, BE=1 also stops
                    // Both strategies have same stop until +1R is achieved
                    if not sig_be_triggered
                        array.set(signal_be_stopped, i, true)
                        sig_be_stopped := true
            
            // Check if BE=1 strategy should be stopped out (entry hit after BE trigger)
            if track_be_mfe and sig_be_triggered and not sig_be_stopped
                if low <= sig_entry
                    array.set(signal_be_stopped, i, true)
                    sig_be_stopped := true"""

new_no_be_stop_bull = """        // FIRST: Update stopped flags on ALL bars (not just incomplete trades)
        // CRITICAL: Flag updates run regardless of is_recent to ensure historical completion detection
        // CRITICAL FIX: Only check stops AFTER trade has entered (not on confirmation bar)
        if sig_has_entered and sig_dir == "Bullish"
            // ALWAYS check if No BE strategy should be stopped out (original SL hit)
            // This runs regardless of track_be_mfe setting
            if not sig_no_be_stopped
                if low <= sig_stop
                    array.set(signal_no_be_stopped, i, true)
                    sig_no_be_stopped := true
                    // CRITICAL: If original SL hit BEFORE BE triggered, BE=1 also stops
                    // Both strategies have same stop until +1R is achieved
                    if track_be_mfe and not sig_be_triggered
                        array.set(signal_be_stopped, i, true)
                        sig_be_stopped := true
            
            // Check if BE=1 strategy should be stopped out (entry hit after BE trigger)
            // This only runs when BE tracking is enabled
            if track_be_mfe and sig_be_triggered and not sig_be_stopped
                if low <= sig_entry
                    array.set(signal_be_stopped, i, true)
                    sig_be_stopped := true"""

content = content.replace(old_no_be_stop_bull, new_no_be_stop_bull)

# Fix 2: Make No BE stop detection run ALWAYS for bearish (around line 675-690)
old_no_be_stop_bear = """        else  // Bearish
            // Check if No BE strategy should be stopped out (original SL hit)
            // CRITICAL FIX: Only check stops AFTER trade has entered (not on confirmation bar)
            if sig_has_entered and track_be_mfe and not sig_no_be_stopped
                if high >= sig_stop
                    array.set(signal_no_be_stopped, i, true)
                    sig_no_be_stopped := true
                    // CRITICAL: If original SL hit BEFORE BE triggered, BE=1 also stops
                    // Both strategies have same stop until +1R is achieved
                    if not sig_be_triggered
                        array.set(signal_be_stopped, i, true)
                        sig_be_stopped := true
            
            // Check if BE=1 strategy should be stopped out (entry hit after BE trigger)
            if sig_has_entered and track_be_mfe and sig_be_triggered and not sig_be_stopped
                if high >= sig_entry
                    array.set(signal_be_stopped, i, true)
                    sig_be_stopped := true"""

new_no_be_stop_bear = """        else  // Bearish
            // ALWAYS check if No BE strategy should be stopped out (original SL hit)
            // This runs regardless of track_be_mfe setting
            // CRITICAL FIX: Only check stops AFTER trade has entered (not on confirmation bar)
            if sig_has_entered and not sig_no_be_stopped
                if high >= sig_stop
                    array.set(signal_no_be_stopped, i, true)
                    sig_no_be_stopped := true
                    // CRITICAL: If original SL hit BEFORE BE triggered, BE=1 also stops
                    // Both strategies have same stop until +1R is achieved
                    if track_be_mfe and not sig_be_triggered
                        array.set(signal_be_stopped, i, true)
                        sig_be_stopped := true
            
            // Check if BE=1 strategy should be stopped out (entry hit after BE trigger)
            // This only runs when BE tracking is enabled
            if sig_has_entered and track_be_mfe and sig_be_triggered and not sig_be_stopped
                if high >= sig_entry
                    array.set(signal_be_stopped, i, true)
                    sig_be_stopped := true"""

content = content.replace(old_no_be_stop_bear, new_no_be_stop_bear)

# Fix 3: Fix completion logic to use tracked flags consistently (around line 704-715)
old_completion_logic = """        // THEN: Check if trade should be marked complete
        if is_recent
            bool trade_stopped_out = false
            if track_be_mfe
                // With BE tracking: complete if EITHER strategy stopped
                trade_stopped_out := sig_be_stopped or sig_no_be_stopped
            else
                // Without BE tracking: complete if original SL hit
                if sig_dir == "Bullish"
                    trade_stopped_out := low <= sig_stop
                else
                    trade_stopped_out := high >= sig_stop"""

new_completion_logic = """        // THEN: Check if trade should be marked complete
        if is_recent
            bool trade_stopped_out = false
            if track_be_mfe
                // With BE tracking: complete if EITHER strategy stopped
                trade_stopped_out := sig_be_stopped or sig_no_be_stopped
            else
                // Without BE tracking: complete if No BE strategy stopped
                // (sig_no_be_stopped is now always tracked regardless of track_be_mfe)
                trade_stopped_out := sig_no_be_stopped"""

content = content.replace(old_completion_logic, new_completion_logic)

# Write the fixed file
with open('complete_automated_trading_system.pine', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed MFE tracking logic in complete_automated_trading_system.pine")
print("\nChanges made:")
print("1. No BE stop detection now runs ALWAYS (not conditional on track_be_mfe)")
print("2. BE stop detection only runs when track_be_mfe = true")
print("3. Completion logic now uses tracked flags consistently")
print("\nResult:")
print("- Trades will only show as COMPLETED when stop loss is actually hit")
print("- BE MFE and No BE MFE will track independently")
print("- Active trades will remain active until stopped out")
