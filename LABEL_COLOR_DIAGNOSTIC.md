# Label Color Issue - Diagnostic Analysis

## Problem Statement
Historical trade labels are showing YELLOW (active) when they should show WHITE (complete).

## Root Cause Analysis

### The Fundamental Issue
Pine Script arrays don't persist state across historical bars the way we need. When TradingView replays history:

1. **Signal is added** → Flags initialized to `false`
2. **Bars replay forward** → Flag-setting logic should detect stop loss hits
3. **Label is drawn** → Should check flags and show white if complete

### Why Our Fixes Haven't Worked

**Attempt 1:** Check flags directly instead of signal_completes array
- **Problem:** Flags themselves aren't being set for historical data

**Attempt 2:** Remove `not sig_was_complete` condition from BE trigger detection
- **Problem:** BE trigger detection still requires `is_recent` check for MFE calculation

**Attempt 3:** Re-read flags from arrays after updates
- **Problem:** Flags aren't being updated in the first place

**Attempt 4:** Remove `is_recent` check from flag-setting logic
- **Problem:** This should have worked, but something else is blocking it

**Attempt 5:** Add missing bearish flag-setting logic
- **Problem:** Logic was added, but still not working

## The Real Problem

Looking at the code structure, I believe the issue is that **the loop only processes the last 20 signals** (line 519):

```pinescript
int start_idx = math.max(0, array.size(signal_entries) - 20)
for i = start_idx to array.size(signal_entries) - 1
```

This means:
- If you have 50 historical signals, only the last 20 are processed
- Signals 0-29 never enter the loop
- Their flags never get set
- Their labels stay yellow

## The Solution

We need to process ALL signals, not just the last 20. The performance optimization is preventing historical signals from being processed.

### Option 1: Remove the limit (may cause timeout)
Process all signals every bar - could be slow

### Option 2: One-time historical processing
On the first bar, process all signals to set their completion flags, then only process recent ones

### Option 3: Increase the limit
Process last 50 or 100 signals instead of 20

### Option 4: Different approach entirely
Instead of trying to maintain flags across bars, calculate completion status on-demand when drawing labels based on current price vs stop loss

## Recommended Fix

**Option 4** is most reliable: When drawing a label, check if the current bar's price has hit the stop loss, rather than relying on flags that may not have been set during historical replay.

This means:
- Remove all the flag arrays
- When drawing labels, calculate: "Has price ever hit the stop loss since this signal?"
- Use that calculation to determine label color

This avoids the entire problem of trying to maintain state across historical bars.
