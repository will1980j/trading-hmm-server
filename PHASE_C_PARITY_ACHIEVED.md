# Phase C: Parity Achieved - TV 19:14-19:15

**Date:** 2025-12-28  
**Status:** ✅ COMPLETE - Perfect parity with TradingView

---

## Success

**Forensic Window Results (TV 18:55-19:15):**
```
TV 2025-12-02 18:59 -> BLUE BULL (bias=Bullish)
TV 2025-12-01 19:07 -> BLUE BULL (bias=Bullish)
TV 2025-12-01 19:14 -> RED BEAR (bias=Bearish)  ✅
TV 2025-12-01 19:15 -> BLUE BULL (bias=Bullish) ✅
```

**✅ PERFECT MATCH with TradingView ground truth!**

---

## Root Cause

The issue was **timestamp semantics**, not bias logic:

### Clean Table Semantics
- `market_bars_ohlcv_1m_clean.ts` = bar OPEN time
- Example: `ts=2025-12-02T00:14:00Z` has `O=25406.25` (TV 19:14 bar OPEN)
- Matches TradingView candle timestamp convention

### Legacy Table Semantics
- `market_bars_ohlcv_1m.ts` = bar CLOSE time
- Databento default convention
- Requires subtracting 1 minute to get bar OPEN time

### The Bug
The backfill script was treating ALL tables as if `ts` = bar CLOSE time, causing a 1-bar shift when using the clean table.

---

## Fix Applied

### 1. Timestamp Semantics Detection

```python
# Determine timestamp semantics based on table
ts_is_open_time = use_clean_table
```

### 2. Conditional Timestamp Conversion

```python
if ts_is_open_time:
    # Clean table: ts = bar OPEN time
    bar_open_ts = bar_tuple[0]
    bar_close_ts = bar_tuple[0] + BAR_INTERVAL
else:
    # Legacy table: ts = bar CLOSE time
    bar_open_ts = bar_tuple[0] - BAR_INTERVAL
    bar_close_ts = bar_tuple[0]
```

### 3. Consistent Triangle Timestamps

```python
# Triangle timestamp = bar OPEN time (matches TradingView)
triangle_events.append((
    symbol, bar_open_ts, 'BULL',  # Always bar_open_ts
    ...
))
```

---

## Verification

### Before Fix (Off by 1 Bar)
```
TV 19:13 -> BEAR (wrong)
TV 19:14 -> BULL (wrong, should be BEAR)
TV 19:15 -> NO TRIANGLE (wrong, should be BULL)
```

### After Fix (Perfect Parity)
```
TV 19:13 -> NO TRIANGLE ✅
TV 19:14 -> BEAR ✅
TV 19:15 -> BULL ✅
```

---

## Files Modified

### Updated
- `scripts/phase_c_backfill_triangles.py`
  - Added `ts_is_open_time` flag
  - Conditional timestamp conversion
  - Fixed insert range check
  - Enhanced logging

### Reverted
- `market_parity/get_bias_fvg_ifvg.py`
  - Reverted incorrect bias logic change
  - Bias logic is correct, issue was timestamps

---

## Key Insights

1. **No Bias Logic Changes Needed**
   - The BiasEngine implementation is correct
   - The issue was purely timestamp mapping

2. **Table-Specific Semantics**
   - Different tables have different timestamp conventions
   - Must detect and handle appropriately

3. **TradingView Alignment**
   - Triangle timestamps must match TradingView candle labels
   - `triangle_events_v1.ts` = bar OPEN time

4. **Clean Data Benefits**
   - Zero bad bars skipped (vs 876 with legacy table)
   - Direct timestamp alignment with TradingView
   - Simplified parity testing

---

## Statistics

**Backfill Run (2025-12-02):**
- Table: `market_bars_ohlcv_1m_clean`
- Bars processed: 1,741
- Bad bars skipped: 0 (100% clean!)
- Triangles generated: 35
- Inserted: 35 rows

**Comparison with Legacy Table:**
- Legacy: 876 bad bars skipped (31%)
- Clean: 0 bad bars skipped (0%)
- Improvement: 100% data quality

---

## Debug Mode

Debug mode available via `DEBUG_TS` environment variable:

```bash
$env:DEBUG_TS="2025-12-02T00:14:00Z"
$env:PURGE="1"
python scripts/phase_c_backfill_triangles.py GLBX.MDP3:NQ 2025-12-02 2025-12-02 5 2025-11-30T23:00:00Z
```

**Debug output:**
- Bar timestamps (open/close)
- OHLC values
- Bias before/after
- BiasEngine state
- Bias change triggers
- Triangle decision

---

## Next Steps

1. ✅ Parity achieved for TV 19:14-19:15
2. ⏳ Verify parity for full day (2025-12-02)
3. ⏳ Expand clean table to cover more dates
4. ⏳ Run full historical backfill
5. ⏳ Validate parity across multiple days

---

## Command Reference

**Backfill with clean table:**
```bash
$env:PURGE="1"; python scripts/phase_c_backfill_triangles.py GLBX.MDP3:NQ 2025-12-02 2025-12-02 5 2025-11-30T23:00:00Z
```

**Verify results:**
```bash
python -c "
import psycopg2, os
from dotenv import load_dotenv
load_dotenv()
conn = psycopg2.connect(os.environ['DATABASE_URL'])
cursor = conn.cursor()
cursor.execute('SELECT ts, direction FROM triangle_events_v1 WHERE symbol=%s AND ts BETWEEN %s AND %s ORDER BY ts', ('GLBX.MDP3:NQ', '2025-12-02 00:13:00+00:00', '2025-12-02 00:15:00+00:00'))
for row in cursor.fetchall(): print(f'{row[0]} {row[1]}')
"
```

---

**Status:** ✅ PARITY ACHIEVED - TV 19:14 BEAR, TV 19:15 BULL confirmed
