# Automated Signals Ingestion Pipeline Fix

## Date: 2025-11-30

## Problem
The Automated Signals ingestion pipeline was failing because:
1. The `as_fuse_automated_payload_sources()` function was NOT copying core trading fields (`entry_price`, `stop_loss`, `direction`, `session`, `bias`) from the raw webhook payload to the canonical dict
2. The `test-lifecycle` endpoint was calling a non-existent function `normalize_automated_signal_payload()`

## Root Cause
The fusion function only copied specific metadata fields (`strategy_name`, `strategy_version`, `engine_version`) but ignored all other fields. This meant `entry_price` and `stop_loss` were never passed to `handle_entry_signal()`, causing the "Entry price and stop loss must be non-zero" error.

## Fixes Applied

### 1. Fixed `as_fuse_automated_payload_sources()` (web_server.py)

**Before:**
```python
# 1. Strategy metadata (if exists)
if isinstance(raw_data, dict):
    for k in ("strategy_name", "strategy_version", "engine_version"):
        if k in raw_data and k not in fused:
            fused[k] = raw_data[k]
```

**After:**
```python
# 1. Copy ALL raw data fields that aren't already in fused
# This ensures entry_price, stop_loss, direction, session, bias, etc. are available
if isinstance(raw_data, dict):
    for k, v in raw_data.items():
        if k not in fused and k != "attributes":
            fused[k] = v
```

### 2. Fixed `test_automated_signals_lifecycle()` endpoint (web_server.py)

Replaced all calls to non-existent `normalize_automated_signal_payload()` with the correct functions:
- `as_parse_automated_signal_payload()` - parses the payload
- `as_fuse_automated_payload_sources()` - fuses raw data with parsed canonical

## Files Changed
- `web_server.py` - Fixed fusion function and test-lifecycle endpoint

## Deployment Required
These changes need to be deployed to Railway:

```bash
git add web_server.py
git commit -m "Fix automated signals fusion to copy all raw data fields"
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
- No changes to Pine event types
- No changes to H1 core functionality (homepage, main dashboard, time analysis)
- Minimal changes focused only on the ingestion path
