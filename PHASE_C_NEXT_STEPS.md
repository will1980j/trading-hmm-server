# Phase C: Next Steps - Quick Reference

**Status:** ✅ All infrastructure ready - Awaiting Databento API key

---

## What's Complete

✅ Clean OHLCV overlay table created  
✅ Re-ingest script with Databento continuous symbology  
✅ Backfill script updated to use clean table  
✅ Verification script ready  
✅ Symbol conversion tested (`GLBX.MDP3:NQ` → `NQ.MDP3.0`)

---

## What's Needed

⚠️ **Databento API Key** - Required to re-ingest clean data from source

---

## Execution Steps

### 1. Add API Key to `.env`

```bash
# Add this line to .env file:
DATABENTO_API_KEY=your_databento_api_key_here
```

### 2. Re-Ingest Clean Data

```bash
python scripts/phase_c_reingest_clean_1m.py GLBX.MDP3:NQ 2025-11-30T23:00:00Z 2025-12-02T05:00:00Z v 0
```

**Arguments:**
- `GLBX.MDP3:NQ` - Internal symbol format
- `2025-11-30T23:00:00Z` - Start timestamp (UTC)
- `2025-12-02T05:00:00Z` - End timestamp (UTC)
- `v` - Roll rule (v=volume, c=calendar, n=next) [optional, default: v]
- `0` - Rank (0=front month, 1=second month) [optional, default: 0]

**Expected:** ~1,700 bars inserted with validation

### 3. Verify Clean Data

```bash
python scripts/phase_c_verify_clean_data.py
```

**Success:** Both TV 19:14 and 19:15 show ✅ MATCH

### 4. Run Backfill

```bash
$env:PURGE="1"; python scripts/phase_c_backfill_triangles.py GLBX.MDP3:NQ 2025-12-02 2025-12-02 5 2025-11-30T23:00:00Z
```

**Expected:** Uses clean table, generates ~154 triangles

### 5. Verify Parity

```bash
python scripts/parity_v1_print_signal_window.py GLBX.MDP3:NQ 2025-12-02T18:55:00Z 2025-12-02T19:15:00Z
```

**Success:** 19:14 shows BEAR triangle, 19:15 shows BULL triangle

---

## Key Files

| Purpose | File |
|---------|------|
| Re-ingest script | `scripts/phase_c_reingest_clean_1m.py` |
| Verification | `scripts/phase_c_verify_clean_data.py` |
| Backfill | `scripts/phase_c_backfill_triangles.py` |
| Forensic check | `scripts/parity_v1_print_signal_window.py` |

---

## Success Criteria

**TV 19:14 (UTC 00:14):**
- Expected: O=25406.25 H=25408.75 L=25400.25 C=25402.50
- Triangle: BEAR

**TV 19:15 (UTC 00:15):**
- Expected: O=25403.75 H=25409.75 L=25403.75 C=25406.75
- Triangle: BULL

---

## Troubleshooting

**Problem:** `ERROR: DATABENTO_API_KEY not set`  
**Solution:** Add key to `.env` file

**Problem:** `400 symbology_invalid_symbol`  
**Solution:** Already fixed - script now uses `NQ.MDP3.0` format

**Problem:** Verification shows MISMATCH  
**Solution:** Re-run re-ingest script to get fresh data from Databento

---

**Bottom Line:** Everything is ready. Just need the Databento API key to execute.
