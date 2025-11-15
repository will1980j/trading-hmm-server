# CRITICAL MFE TRACKING LOGIC ISSUES FOUND

## Problems Identified:

### 1. **All Trades Showing as COMPLETED**
**Root Cause:** Stop loss detection only runs when `track_be_mfe = true`
- Lines 648-650: `if track_be_mfe and not sig_no_be_stopped`
- When `track_be_mfe = false` (default), stop detection NEVER runs
- But completion check at line 708 still tries to use `sig_be_stopped` and `sig_no_be_stopped` flags
- These flags remain `false` forever, so trades never complete properly

### 2. **BE MFE Always Equals No BE MFE**
**Root Cause:** Enforcement rule at line 740 caps BE MFE to No BE MFE
- Line 740: `float capped_be_mfe = math.min(current_mfe, sig_mfe)`
- This is CORRECT logic: BE MFE should never exceed No BE MFE
- BUT: The issue is that when BE triggers, both values become equal
- Then they stay equal because BE MFE stops updating when BE=1 strategy stops

### 3. **Incorrect Completion Logic**
**Root Cause:** Mixed logic between tracked flags and current bar checks
- Line 708: Uses `sig_be_stopped or sig_no_be_stopped` when `track_be_mfe = true`
- Line 712-715: Uses `low <= sig_stop` when `track_be_mfe = false`
- The second check only looks at CURRENT bar, not historical extreme prices
- Should ALWAYS use tracked extreme prices (`sig_lowest_low` / `sig_highest_high`)

## The Fix:

### Change 1: Make stop detection run ALWAYS (not just when track_be_mfe = true)

**Current (BROKEN):**
```pinescript
if track_be_mfe and not sig_no_be_stopped
    if low <= sig_stop
        array.set(signal_no_be_stopped, i, true)
```

**Fixed:**
```pinescript
// Always track No BE stop (regardless of track_be_mfe setting)
if not sig_no_be_stopped
    if sig_dir == "Bullish" and low <= sig_stop
        array.set(signal_no_be_stopped, i, true)
        sig_no_be_stopped := true
    else if sig_dir == "Bearish" and high >= sig_stop
        array.set(signal_no_be_stopped, i, true)
        sig_no_be_stopped := true

// Only track BE stop if BE tracking is enabled
if track_be_mfe and sig_be_triggered and not sig_be_stopped
    if sig_dir == "Bullish" and low <= sig_entry
        array.set(signal_be_stopped, i, true)
        sig_be_stopped := true
    else if sig_dir == "Bearish" and high >= sig_entry
        array.set(signal_be_stopped, i, true)
        sig_be_stopped := true
```

### Change 2: Fix completion logic to use tracked flags consistently

**Current (BROKEN):**
```pinescript
if track_be_mfe
    trade_stopped_out := sig_be_stopped or sig_no_be_stopped
else
    if sig_dir == "Bullish"
        trade_stopped_out := low <= sig_stop
    else
        trade_stopped_out := high >= sig_stop
```

**Fixed:**
```pinescript
// ALWAYS use tracked flags (they're now always updated)
if track_be_mfe
    // With BE tracking: complete if EITHER strategy stopped
    trade_stopped_out := sig_be_stopped or sig_no_be_stopped
else
    // Without BE tracking: complete if No BE strategy stopped
    trade_stopped_out := sig_no_be_stopped
```

### Change 3: Clarify BE MFE capping logic (this is actually CORRECT)

The rule that BE MFE can never exceed No BE MFE is CORRECT because:
- BE=1 strategy moves stop to entry at +1R
- No BE strategy keeps original stop
- If price goes to +5R then retraces to +1R (entry):
  - BE=1 stops out at +1R (BE MFE = 1.0R)
  - No BE continues running (No BE MFE = 5.0R)
- This is the INTENDED behavior

## Summary:

The main issue is that stop detection was conditional on `track_be_mfe` setting, but it should ALWAYS run. The `track_be_mfe` setting should only control:
1. Whether BE=1 strategy is tracked (separate from No BE)
2. Whether BE MFE values are displayed in labels
3. Whether BE-specific webhooks are sent

It should NOT control whether basic stop loss detection happens!
