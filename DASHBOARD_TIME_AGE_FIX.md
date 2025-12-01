# Dashboard & Indicator Fixes - Dec 1, 2025

## Issues Reported
1. **COMPLETED vs ACTIVE mismatch**: Trade showing COMPLETED on dashboard but ACTIVE on chart
2. **Time display wrong**: Only showing on one trade, increasing per minute
3. **Age calculation wrong**: Showing 11 hours for one trade, nothing for other

## Root Causes Found & Fixed

### Issue 1: EXIT_BE Sent Incorrectly (INDICATOR BUG - FIXED)
**Root Cause:** The indicator was sending `EXIT_BE` for trades that never reached +1R.

When the original stop loss was hit BEFORE BE was triggered, the code set `be_stopped = true`. Then the completion webhook used `be_stopped` to determine the exit type, sending `EXIT_BE` even though BE was never triggered.

**Evidence:** Trade `20251201_053700000_BULLISH` had MFE of only 0.11R but received `EXIT_BE`. BE should only trigger after reaching +1R.

**Fix in `complete_automated_trading_system.pine`:**
```pinescript
// BEFORE (wrong):
string exit_event_type = be_stopped ? EVENT_EXIT_BREAK_EVEN : EVENT_EXIT_STOP_LOSS

// AFTER (correct):
bool actual_be_exit = be_stopped and sig_be_triggered
string exit_event_type = actual_be_exit ? EVENT_EXIT_BREAK_EVEN : EVENT_EXIT_STOP_LOSS
```

### Issue 2: Time Display (JS BUG - FIXED)
**Root Cause:** JS was using `row.timestamp` (UTC database insertion time) instead of `row.signal_time` (actual signal time from TradingView).

**Fix:** Now uses `signal_time` field which is already in Eastern Time.

### Issue 3: Age Calculation (JS BUG - FIXED)
**Root Cause:** JS was calculating age from UTC `timestamp` field.

**Fix:** Now calculates from `signal_date` + `signal_time` in Eastern Time.

## Files Changed
1. `complete_automated_trading_system.pine` - Fixed EXIT_BE logic
2. `static/js/automated_signals_ultra.js` - Fixed time display and age calculation

## Actions Required

### 1. Deploy to Railway
Commit and push to deploy the JavaScript fixes.

### 2. Update TradingView Indicator
Copy the fixed `complete_automated_trading_system.pine` to TradingView:
1. Open TradingView Pine Editor
2. Replace the indicator code with the fixed version
3. Save and apply to chart

### 3. Delete Incorrect Trades
Delete these incorrectly marked trades from the dashboard:
- `20251201_053700000_BULLISH` (EXIT_BE with only 0.11R MFE)
- `20251201_054000000_BEARISH` (EXIT_BE with only 0.53R MFE)
- `20251201_052400000_BULLISH` (may be correct if it actually reached +1R)

## Technical Summary

The core bug was in the completion webhook logic:
- `be_stopped` was set to `true` when original SL hit before BE triggered
- But the exit type check only looked at `be_stopped`, not whether BE was actually triggered
- This caused EXIT_BE to be sent for trades that never reached +1R

The fix adds a new check: `actual_be_exit = be_stopped and sig_be_triggered`
- EXIT_BE only sent if BE was actually triggered (reached +1R first)
- EXIT_SL sent for all other stop-outs
