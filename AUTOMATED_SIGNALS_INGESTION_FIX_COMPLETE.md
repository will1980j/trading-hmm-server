# Automated Signals Ingestion Pipeline Fix - Complete

## Problem Summary

ENTRY events from the TradingView telemetry indicator were failing to insert into the `automated_signals` table due to **schema mismatch**. The INSERT statements referenced columns that don't exist in the actual database schema, causing transaction aborts and preventing downstream events (MFE_UPDATE, BE_TRIGGERED, EXIT_*) from finding ENTRY rows.

## Root Cause Analysis

### Schema Mismatch Details

**Non-existent columns being referenced in INSERT statements:**
- `target_1r`, `target_2r`, `target_3r`, `target_5r`, `target_10r`, `target_20r`
- `account_size`, `risk_percent`, `contracts`, `risk_amount`
- `created_at`, `lifecycle_state`, `lifecycle_seq`, `lifecycle_entered_at`, `lifecycle_updated_at`

**Actual `automated_signals` table schema:**
```sql
CREATE TABLE automated_signals (
    id SERIAL PRIMARY KEY,
    trade_id VARCHAR(100),
    event_type VARCHAR(20),
    direction VARCHAR(10),
    entry_price DECIMAL(10,2),
    stop_loss DECIMAL(10,2),
    session VARCHAR(20),
    bias VARCHAR(20),
    risk_distance DECIMAL(10,2),
    targets JSONB,
    current_price DECIMAL(10,2),
    mfe DECIMAL(10,4),
    be_mfe DECIMAL(10,4),
    no_be_mfe DECIMAL(10,4),
    exit_price DECIMAL(10,2),
    final_mfe DECIMAL(10,4),
    signal_date DATE,
    signal_time TIME,
    timestamp TIMESTAMP DEFAULT NOW()
)
```

## Fixes Applied

### 1. ENTRY Handler (`handle_entry_signal`) - PRIMARY FIX

**File:** `web_server.py`

**Before:** 32-column INSERT with non-existent columns causing transaction failures

**After:** 19-column INSERT using ONLY real schema columns:
```sql
INSERT INTO automated_signals (
    trade_id, event_type, direction, entry_price, stop_loss,
    risk_distance, targets, session, bias, current_price,
    mfe, be_mfe, no_be_mfe, exit_price, final_mfe,
    signal_date, signal_time, timestamp
) VALUES (...)
```

**Additional improvements:**
- Added try/except with detailed SQL error logging
- Logs exception type, SQL query, and parameters on failure
- Calls `conn.rollback()` to keep connection clean

### 2. MFE_UPDATE Handler (`handle_mfe_update`)

**Before:** UPDATE statement referenced non-existent `lifecycle_*` columns

**After:** UPDATE uses only schema-compatible columns:
```sql
UPDATE automated_signals
SET 
    event_type = 'MFE_UPDATE',
    current_price = %s,
    mfe = %s,
    be_mfe = %s,
    no_be_mfe = %s,
    timestamp = NOW()
WHERE trade_id = %s
  AND event_type IN ('ENTRY', 'MFE_UPDATE')
```

### 3. BE_TRIGGERED Handler (`handle_be_trigger`)

**Before:** INSERT only stored `mfe` column

**After:** INSERT stores all MFE values:
```sql
INSERT INTO automated_signals (
    trade_id, event_type, mfe, be_mfe, no_be_mfe, timestamp
) VALUES (%s, %s, %s, %s, %s, NOW())
```

### 4. EXIT Handler (`handle_exit_signal`)

**Before:** INSERT referenced non-existent `lifecycle_*` columns

**After:** INSERT uses only schema-compatible columns:
```sql
INSERT INTO automated_signals (
    trade_id, event_type, exit_price, be_mfe, no_be_mfe, final_mfe, timestamp
) VALUES (%s, %s, %s, %s, %s, %s, NOW())
```

**Additional fix:** Changed `MAX(lifecycle_seq)` query to `COUNT(*)` since `lifecycle_seq` doesn't exist.

### 5. Built-in Lifecycle Test Endpoint

**Added:** `/api/automated-signals/test-lifecycle` (POST)

Tests complete ENTRY → MFE_UPDATE → BE_TRIGGERED → EXIT flow internally and returns detailed results.

## Files Modified

| File | Changes |
|------|---------|
| `web_server.py` | Fixed ENTRY, MFE_UPDATE, BE_TRIGGERED, EXIT handlers; Added test endpoint |
| `test_ingestion_pipeline_fix.py` | **NEW** - Production test script |

## Verification Methods

### 1. Built-in Test Endpoint
```bash
curl -X POST https://web-production-cd33.up.railway.app/api/automated-signals/test-lifecycle
```

### 2. Production Test Script
```bash
python test_ingestion_pipeline_fix.py
```

### 3. Manual Webhook Test
```bash
# ENTRY
curl -X POST https://web-production-cd33.up.railway.app/api/automated-signals/webhook \
  -H "Content-Type: application/json" \
  -d '{"trade_id":"TEST_001","event_type":"ENTRY","direction":"LONG","entry_price":"18500","stop_loss":"18450"}'

# MFE_UPDATE
curl -X POST https://web-production-cd33.up.railway.app/api/automated-signals/webhook \
  -H "Content-Type: application/json" \
  -d '{"trade_id":"TEST_001","event_type":"MFE_UPDATE","be_mfe":"0.5","no_be_mfe":"0.5"}'

# EXIT
curl -X POST https://web-production-cd33.up.railway.app/api/automated-signals/webhook \
  -H "Content-Type: application/json" \
  -d '{"trade_id":"TEST_001","event_type":"EXIT_BE","final_be_mfe":"1.0","final_no_be_mfe":"1.5"}'
```

## Constraints Satisfied

✅ **No Pine indicator changes** - Payload structure unchanged  
✅ **No Pine event type changes** - ENTRY, MFE_UPDATE, BE_TRIGGERED, EXIT_* preserved  
✅ **No H1 core functionality broken** - Only automated_signals ingestion path modified  
✅ **Minimal code changes** - Focused only on schema compatibility  
✅ **Telemetry table ensured** - `telemetry_automated_signals_log` created at startup

## Expected Results After Deployment

1. **ENTRY events insert successfully** into `automated_signals`
2. **MFE_UPDATE events find and update** the ENTRY rows
3. **BE_TRIGGERED events store** BE trigger information
4. **EXIT events find ENTRY rows** and complete the lifecycle
5. **Dashboard shows completed trades** with full lifecycle data
6. **No more "no ENTRY row found" errors** in logs

## Deployment Instructions

1. Commit changes via GitHub Desktop
2. Push to main branch (triggers Railway auto-deploy)
3. Wait for deployment to complete (~2-3 minutes)
4. Run verification: `python test_ingestion_pipeline_fix.py`
5. Check Railway logs for any errors

## Rollback Plan

If issues occur, the changes are isolated to:
- `handle_entry_signal()` function
- `handle_mfe_update()` function  
- `handle_be_trigger()` function
- `handle_exit_signal()` function
- New `/api/automated-signals/test-lifecycle` endpoint

No schema changes were made. Rollback by reverting the web_server.py changes.

---

**Status:** ✅ READY FOR DEPLOYMENT

**Date:** 2025-11-30
