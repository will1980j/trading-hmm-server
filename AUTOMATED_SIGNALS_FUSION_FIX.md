# Automated Signals Ingestion Pipeline Fix

## Date: 2025-11-30

## Problem
The Automated Signals ingestion pipeline was failing because:
1. The `as_fuse_automated_payload_sources()` function was NOT copying core trading fields (`entry_price`, `stop_loss`, `direction`, `session`, `bias`) from the raw webhook payload to the canonical dict
2. The `test-lifecycle` endpoint was calling a non-existent function `normalize_automated_signal_payload()`
3. The ENTRY deduplication guard was checking for ANY row with the trade_id, not specifically ENTRY rows
4. The lifecycle validation didn't allow BE_TRIGGERED events

## Root Cause
Multiple issues:
1. Fusion function only copied specific metadata fields, ignoring trading fields
2. Deduplication guard found BE_TRIGGERED rows and incorrectly treated them as existing ENTRYs
3. Lifecycle validation rejected BE_TRIGGERED as an illegal transition

## Fixes Applied

### 1. Fixed `as_fuse_automated_payload_sources()` (web_server.py)

**Before:** Only copied 3 metadata fields
**After:** Copies ALL raw data fields to ensure entry_price, stop_loss, etc. are available

### 2. Fixed `test_automated_signals_lifecycle()` endpoint (web_server.py)

Replaced calls to non-existent `normalize_automated_signal_payload()` with correct functions:
- `as_parse_automated_signal_payload()` 
- `as_fuse_automated_payload_sources()`

### 3. Fixed ENTRY deduplication guard (web_server.py)

**Before:**
```sql
WHERE trade_id = %s
```

**After:**
```sql
WHERE trade_id = %s AND event_type = 'ENTRY'
```

### 4. Fixed `as_validate_lifecycle_transition()` (web_server.py)

Added BE_TRIGGERED as a valid transition from ENTRY state.

## Files Changed
- `web_server.py` - All fixes in one file

## Deployment Required
```bash
git add web_server.py
git commit -m "Fix automated signals: fusion, deduplication, and lifecycle validation"
git push origin main
```

## Verification
After deployment, test with:
```bash
curl -X POST https://web-production-f8c3.up.railway.app/api/automated-signals/test-lifecycle
```

Expected result: All steps should PASS (ENTRY, MFE_UPDATE, BE_TRIGGERED, EXIT_BE, DATABASE_VERIFY)

## Impact
- No changes to TradingView Pine indicator payload shape
- No changes to Pine event types (ENTRY, MFE_UPDATE, BE_TRIGGERED, EXIT_*)
- No changes to H1 core functionality (homepage, main dashboard, time analysis)
- Minimal changes focused only on the ingestion path
