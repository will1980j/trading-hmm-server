# Phase C: Timestamp Semantics Fix - COMPLETE

**Date:** 2025-12-28  
**Status:** ✅ FIXED - Parity achieved for TV 19:14-19:15

---

## Problem

Triangle timestamps were off by one bar due to incorrect timestamp semantics:
- **Clean table** (`market_bars_ohlcv_1m_clean`): `ts` = bar OPEN time (matches TradingView)
- **Legacy table** (`market_bars_ohlcv_1m`): `ts` = bar CLOSE time (Databento default)

The backfill script was treating ALL tables as if `ts` = bar CLOSE time, causing a 1-bar shift.

**Before fix:**
- TV 19:13 → BEAR (wrong)
- TV 19:14 → BULL (wrong, should be BEAR)
- TV 19:15 → NO TRIANGLE (wrong, should be BULL)

---

## Solution

### Timestamp Semantics Detection

Added logic to detect which table is being used and apply correct timestamp semantics:

```python
# Determine timestamp semantics based on table
# Clean table: ts = bar OPEN time (matches TradingView)
# Legacy table: ts = bar CLOSE time (Databento default)
ts_is_open_time = use_clean_table
```

### Timestamp Conversion

```python
# Compute bar timestamps based on table semantics
if ts_is_open_time:
    # Clean table: ts = bar OPEN time
    bar_open_ts = bar_tuple[0]
    bar_close_ts = bar_tuple[0] + BAR_INTERVAL
else:
    # Legacy table: ts = bar CLOSE time
    bar_open_ts = bar_tuple[0] - BAR_INTERVAL
    bar_close_ts = bar_tuple[0]
```

### Triangle Timestamp

```python
# Triangle timestamp = bar OPEN time (matches TradingView)
triangle_events.append((
    symbol, bar_open_ts, 'BULL',  # bar_open_ts, not bar_close_ts
    ...
))
```

---

## Verification

### After Fix

```
Triangle Results (TV 19:13-19:15):
============================================================
TV 19:13 -> NO TRIANGLE
TV 19:14 -> RED BEAR triangle
TV 19:15 -> BLUE BULL triangle
============================================================
```

**✅ PERFECT MATCH with TradingView ground truth!**

---

## Key Changes

### File Modified
- `scripts/phase_c_backfill_triangles.py`

### Changes Made

1. **Added timestamp semantics detection:**
   - `ts_is_open_time = use_clean_table`
   - Logs: "Timestamp semantics: ts = bar OPEN/CLOSE time"

2. **Updated timestamp conversion:**
   - Clean table: `bar_open_ts = ts`, `bar_close_ts = ts + 1min`
   - Legacy table: `bar_close_ts = ts`, `bar_open_ts = ts - 1min`

3. **Fixed insert range check:**
   - Uses `bar_open_ts` for eligibility check
   - Ensures triangles are only generated for bars within insert range

4. **Fixed triangle timestamp:**
   - Always stores `bar_open_ts` in `triangle_events_v1.ts`
   - Matches TradingView candle timestamp convention

5. **Updated PURGE window:**
   - Already correct (uses insert_open_start/end)
   - No changes needed

---

## Debug Mode

Debug mode remains available via `DEBUG_TS` environment variable:

```bash
$env:DEBUG_TS="2025-12-02T00:14:00Z"
$env:PURGE="1"
python scripts/phase_c_backfill_triangles.py GLBX.MDP3:NQ 2025-12-02 2025-12-02 5 2025-11-30T23:00:00Z
```

**Debug output includes:**
- Bar timestamps (open/close)
- OHLC values
- Bias before/after
- BiasEngine state (ATH/ATL, array sizes)
- Bias change triggers
- Triangle generation decision

---

## Technical Details

### Why Two Different Semantics?

**Legacy Table (`market_bars_ohlcv_1m`):**
- Ingested from Databento DBN files
- Databento convention: `ts_event` = bar CLOSE time
- Historical data uses this convention

**Clean Table (`market_bars_ohlcv_1m_clean`):**
- Re-ingested with validation
- Aligned to TradingView convention: `ts` = bar OPEN time
- Simplifies parity testing

### TradingView Convention

In TradingView:
- Candle labeled "19:14" opens at 19:14:00 and closes at 19:14:59
- Triangles appear on the candle where bias changes
- Triangle timestamp = candle OPEN time

### Database Convention

In `triangle_events_v1`:
- `ts` = bar OPEN time (TradingView timestamp)
- Matches TradingView candle labels
- Enables direct comparison with TV screenshots

---

## Backfill Statistics

**Run:** 2025-12-02 (full day)
- Bars processed: 1,741
- Bad bars skipped: 0 (clean table has no corruption!)
- Triangles generated: 35
- Inserted: 35 rows

---

## Success Criteria

✅ TV 19:13 → NO TRIANGLE  
✅ TV 19:14 → RED BEAR triangle  
✅ TV 19:15 → BLUE BULL triangle  

**Status:** ✅ PARITY ACHIEVED for TV 19:14-19:15 window

---

## Files Modified

1. **scripts/phase_c_backfill_triangles.py**
   - Added timestamp semantics detection
   - Fixed timestamp conversion logic
   - Updated insert range check
   - Fixed triangle timestamp storage

2. **market_parity/get_bias_fvg_ifvg.py**
   - Reverted incorrect bias logic change
   - Kept debug mode support

---

## Next Steps

1. ✅ Verify parity for full forensic window (18:55-19:15)
2. ⏳ Expand clean table to cover more dates
3. ⏳ Run full historical backfill with clean data
4. ⏳ Validate parity across multiple days

---

**Status:** ✅ Timestamp semantics fixed - TV 19:14 BEAR and 19:15 BULL confirmed
