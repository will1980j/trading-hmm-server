# Phase C: Databento Roll Rule Fix - COMPLETE

**Date:** 2025-12-28  
**Status:** ✅ FIXED - Ready for execution

---

## Problem

Previous patch incorrectly used `MDP3` as a roll rule. Databento roll rules are only:
- `c` = calendar roll
- `n` = next roll  
- `v` = volume roll (most common)

`MDP3` is a **dataset name**, not a roll rule.

---

## Solution

### Updated Symbol Conversion

**Function signature:**
```python
def to_databento_continuous(symbol: str, roll_rule: str = "v", rank: int = 0) -> str
```

**Conversion:**
- `GLBX.MDP3:NQ` + `roll_rule='v'` + `rank=0` → `NQ.v.0`
- `GLBX.MDP3:NQ` + `roll_rule='c'` + `rank=0` → `NQ.c.0`
- `GLBX.MDP3:NQ` + `roll_rule='n'` + `rank=1` → `NQ.n.1`

### CLI Arguments

**New usage:**
```bash
python scripts/phase_c_reingest_clean_1m.py SYMBOL START_TS END_TS [ROLL_RULE] [RANK]
```

**Defaults:**
- `ROLL_RULE` = `"v"` (volume roll)
- `RANK` = `0` (front month)

**Examples:**
```bash
# Use defaults (volume roll, front month)
python scripts/phase_c_reingest_clean_1m.py GLBX.MDP3:NQ 2025-11-30T23:00:00Z 2025-12-02T05:00:00Z

# Explicit volume roll, front month
python scripts/phase_c_reingest_clean_1m.py GLBX.MDP3:NQ 2025-11-30T23:00:00Z 2025-12-02T05:00:00Z v 0

# Calendar roll, front month
python scripts/phase_c_reingest_clean_1m.py GLBX.MDP3:NQ 2025-11-30T23:00:00Z 2025-12-02T05:00:00Z c 0

# Next roll, second month
python scripts/phase_c_reingest_clean_1m.py GLBX.MDP3:NQ 2025-11-30T23:00:00Z 2025-12-02T05:00:00Z n 1
```

---

## Verification

### Symbol Conversion Tests

```
✅ GLBX.MDP3:NQ (roll=v, rank=0) -> NQ.v.0
✅ GLBX.MDP3:NQ (roll=c, rank=0) -> NQ.c.0
✅ GLBX.MDP3:NQ (roll=n, rank=1) -> NQ.n.1
✅ NQ.v.0 (already correct) -> NQ.v.0
✅ NQ.c.0 (already correct) -> NQ.c.0
```

### Roll Rule Validation

Script validates roll rule at startup:
```python
if roll_rule not in ("c", "n", "v"):
    print(f"ERROR: Invalid roll rule '{roll_rule}'. Must be 'c', 'n', or 'v'")
    sys.exit(1)
```

---

## Enhanced Logging

**Output includes:**
```
DB symbol: GLBX.MDP3:NQ
Databento continuous: NQ.v.0
Roll rule: v (volume)
Rank: 0 (front month)
Range: 2025-11-30 23:00:00+00:00 to 2025-12-02 05:00:00+00:00
```

---

## Databento Roll Rules Explained

### Volume Roll (`v`) - DEFAULT
- **Most common** for liquid futures
- Rolls when volume shifts to next contract
- Minimizes slippage and tracking error
- **Recommended for NQ, ES, YM**

### Calendar Roll (`c`)
- Rolls on specific calendar dates
- Predictable roll schedule
- Used for less liquid contracts
- May have higher slippage

### Next Roll (`n`)
- Rolls to next available contract
- Simple sequential rolling
- Less common for major indices

---

## Next Steps

### 1. Add Databento API Key

```bash
# Add to .env file:
DATABENTO_API_KEY=your_databento_api_key_here
```

### 2. Run Re-Ingestion (Volume Roll, Front Month)

```bash
python scripts/phase_c_reingest_clean_1m.py GLBX.MDP3:NQ 2025-11-30T23:00:00Z 2025-12-02T05:00:00Z v 0
```

**Expected:**
- Queries Databento for `NQ.v.0`
- Inserts ~1,700 validated bars
- Skips ~64 invalid bars

### 3. Verify Clean Data

```bash
python scripts/phase_c_verify_clean_data.py
```

**Success criteria:**
```
TV 19:14 (UTC 2025-12-02 00:14:00+00:00):
  Actual:   O=25406.25 H=25408.75 L=25400.25 C=25402.50
  Expected: O=25406.25 H=25408.75 L=25400.25 C=25402.50
  ✅ MATCH
```

### 4. Run Backfill

```bash
$env:PURGE="1"; python scripts/phase_c_backfill_triangles.py GLBX.MDP3:NQ 2025-12-02 2025-12-02 5 2025-11-30T23:00:00Z
```

### 5. Verify Parity

```bash
python scripts/parity_v1_print_signal_window.py GLBX.MDP3:NQ 2025-12-02T18:55:00Z 2025-12-02T19:15:00Z
```

**Success:**
- 19:14 shows BEAR triangle
- 19:15 shows BULL triangle

---

## Files Modified

### Updated
- `scripts/phase_c_reingest_clean_1m.py`
  - Fixed `to_databento_continuous()` to use correct roll rules (c/n/v)
  - Added `roll_rule` and `rank` CLI arguments
  - Enhanced logging with roll rule details
  - Added roll rule validation

### Documentation
- `PHASE_C_DATABENTO_SYMBOLOGY_PATCH_COMPLETE.md` (updated)
- `PHASE_C_NEXT_STEPS.md` (updated)
- `PHASE_C_ROLL_RULE_FIX_COMPLETE.md` (this file)

---

## Key Changes Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Roll Rule** | `MDP3` (incorrect) | `v`/`c`/`n` (correct) |
| **Symbol** | `NQ.MDP3.0` | `NQ.v.0` |
| **CLI Args** | 3 required | 3 required + 2 optional |
| **Default Roll** | N/A | `v` (volume) |
| **Default Rank** | N/A | `0` (front month) |
| **Validation** | None | Roll rule validated |
| **Logging** | Basic | Enhanced with roll details |

---

## Success Metrics

- ✅ Symbol conversion fixed (c/n/v roll rules)
- ✅ CLI arguments added (roll_rule, rank)
- ✅ Roll rule validation implemented
- ✅ Enhanced logging with roll details
- ✅ All tests passing
- ⏳ Awaiting Databento API key
- ⏳ Awaiting clean data verification
- ⏳ Awaiting parity testing

---

**Status:** Fix complete and tested. Ready for execution with Databento API key.
