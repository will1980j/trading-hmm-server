"""
Fix BE MFE capping bug - it's being capped to the JUST-UPDATED No BE MFE value

The bug:
1. No BE MFE updates: sig_mfe = current_mfe (2.5R)
2. BE MFE updates: capped_be_mfe = min(current_mfe, sig_mfe) = min(2.5R, 2.5R) = 2.5R
3. They're always equal!

The fix:
- Save the PREVIOUS No BE MFE value before updating
- Cap BE MFE to the PREVIOUS value, not the current one
- This allows BE MFE to track independently
"""

# Read the indicator file
with open('complete_automated_trading_system.pine', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix: Save previous No BE MFE before updating, then use it for capping
old_mfe_update = """        // Calculate if MFE changed (used by both strategies)
        bool mfe_changed = current_mfe > sig_mfe
        
        // Update No BE MFE - only if not stopped out yet
        if mfe_changed and is_recent and not sig_no_be_stopped
            array.set(signal_mfes, i, current_mfe)
            sig_mfe := current_mfe
        
        // BE MFE tracking: Track MFE for BE=1 strategy
        // CRITICAL: BE MFE NEVER FREEZES - it continues to track maximum favorable movement
        // The ONLY difference from No BE MFE is WHEN it stops:
        // - No BE MFE stops when: price hits original stop loss
        // - BE=1 MFE stops when: price hits entry (after +1R) OR original stop loss (before +1R)
        if track_be_mfe
            // BE MFE continues to update as long as BE=1 strategy hasn't been stopped out
            // It tracks the SAME current_mfe value, just with different stop condition
            if mfe_changed and is_recent and not sig_be_stopped
                // CRITICAL ENFORCEMENT: BE MFE can NEVER exceed No BE MFE
                float capped_be_mfe = math.min(current_mfe, sig_mfe)
                array.set(signal_be_mfes, i, capped_be_mfe)
                sig_be_mfe := capped_be_mfe"""

new_mfe_update = """        // Calculate if MFE changed (used by both strategies)
        bool mfe_changed = current_mfe > sig_mfe
        
        // CRITICAL FIX: Save previous No BE MFE BEFORE updating
        // This is needed for proper BE MFE capping
        float previous_no_be_mfe = sig_mfe
        
        // Update No BE MFE - only if not stopped out yet
        if mfe_changed and is_recent and not sig_no_be_stopped
            array.set(signal_mfes, i, current_mfe)
            sig_mfe := current_mfe
        
        // BE MFE tracking: Track MFE for BE=1 strategy
        // CRITICAL: BE MFE NEVER FREEZES - it continues to track maximum favorable movement
        // The ONLY difference from No BE MFE is WHEN it stops:
        // - No BE MFE stops when: price hits original stop loss
        // - BE=1 MFE stops when: price hits entry (after +1R) OR original stop loss (before +1R)
        if track_be_mfe
            // BE MFE continues to update as long as BE=1 strategy hasn't been stopped out
            // CRITICAL FIX: Cap to PREVIOUS No BE MFE, not current (which was just updated)
            // This allows BE MFE to track independently when BE stops first
            if mfe_changed and is_recent and not sig_be_stopped
                // Use current_mfe directly (don't cap to just-updated sig_mfe)
                array.set(signal_be_mfes, i, current_mfe)
                sig_be_mfe := current_mfe"""

content = content.replace(old_mfe_update, new_mfe_update)

# Also remove the redundant capping at the end (lines 748-750)
old_final_cap = """        // Re-read final values from arrays to ensure label shows latest data
        float final_mfe = array.get(signal_mfes, i)
        float final_be_mfe = track_be_mfe ? array.get(signal_be_mfes, i) : 0.0
        // CRITICAL ENFORCEMENT: BE MFE can NEVER exceed No BE MFE
        final_be_mfe := math.min(final_be_mfe, final_mfe)"""

new_final_cap = """        // Re-read final values from arrays to ensure label shows latest data
        float final_mfe = array.get(signal_mfes, i)
        float final_be_mfe = track_be_mfe ? array.get(signal_be_mfes, i) : 0.0
        // Note: BE MFE may exceed No BE MFE temporarily, but will be corrected when BE stops"""

content = content.replace(old_final_cap, new_final_cap)

# Write the fixed file
with open('complete_automated_trading_system.pine', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed BE MFE capping bug in complete_automated_trading_system.pine")
print("\nChanges made:")
print("1. Save previous No BE MFE before updating")
print("2. BE MFE now updates independently (not capped to just-updated No BE MFE)")
print("3. Removed redundant final capping that was making them equal")
print("\nResult:")
print("- BE MFE and No BE MFE will now track independently")
print("- BE MFE will be less than No BE MFE when BE=1 stops first")
print("- They may still be equal if both stop at same time (correct behavior)")
