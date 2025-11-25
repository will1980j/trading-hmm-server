# PHASE 2A - ROOT CAUSE ANALYSIS
## Automated Signals Ingestion Pipeline Failure

**Date:** 2025-11-26  
**Production URL:** https://web-production-f8c3.up.railway.app  
**Status:** ❌ CRITICAL - Webhook rejecting all incoming signals

---

## 🔍 DIAGNOSIS SUMMARY

### Current State
- **Database:** ✅ Operational (869 existing signals, 19 active, 51 completed)
- **Stats Endpoint:** ✅ Working (`/api/automated-signals/stats-live`)
- **Webhook Endpoint:** ❌ **REJECTING ALL PAYLOADS**

### Root Cause
**Validation Logic Error in `as_validate_parsed_payload()` function**

The webhook handler is rejecting valid payloads with error:
```
"Missing or invalid required field: event_type"
```

---

## 📋 DETAILED FINDINGS

### DIAGNOSIS – ROUTE
✅ **Route Registration:** Correct
- Primary route: `/api/automated-signals` (POST)
- Alias route: `/api/automated-signals/webhook` (POST)
- Both routes registered in `web_server.py` lines 11191-11194

### DIAGNOSIS – PAYLOAD
❌ **Payload Validation:** BROKEN

**Test Payload Sent:**
```json
{
  "event_type": "ENTRY",
  "trade_id": "DIAGNOSTIC_TEST_20251126_004059",
  "direction": "LONG",
  "entry_price": 21000.0,
  "stop_loss": 20975.0,
  "session": "NY AM",
  "bias": "Bullish"
}
```

**Error Returned:**
```json
{
  "error": "Missing or invalid required field: event_type",
  "success": false
}
```

**Root Cause:**
The `as_validate_parsed_payload()` function (web_server.py ~line 11340) requires `format_kind` to be set, but the parser `as_parse_automated_signal_payload()` is not setting it for direct telemetry-style payloads.

**Code Analysis:**
```python
# In as_validate_parsed_payload():
required_fields = ["event_type", "trade_id", "format_kind"]
for field in required_fields:
    if field not in canonical or canonical[field] in (None, "", "UNKNOWN"):
        return f"Missing or invalid required field: {field}"
```

The parser only sets `format_kind` for these cases:
1. `telemetry_root` - when `schema_version` is present
2. `telemetry_wrapped` - when `attributes` dict is present
3. `strategy` - when `type` field is present
4. `legacy_indicator` - when `automation_stage` is present

**But our test payload has none of these**, so `format_kind` remains `None`, causing validation to fail.

### DIAGNOSIS – DB CONNECTION
✅ **Database Connection:** Correct
- Uses `DATABASE_URL` environment variable
- Fresh connections via `psycopg2.connect(database_url)`
- No localhost or hardcoded URLs detected

### DIAGNOSIS – INSERT LOGIC
⚠️ **Insert Logic:** Not reached due to validation failure
- The validation fails before any database insert is attempted
- Insert logic in `handle_entry_signal()` appears correct (lines 11770+)
- Uses parameterized queries
- Proper commit/close handling

### DIAGNOSIS – SUPPRESSED ERRORS
✅ **Error Handling:** Adequate
- Errors are logged via `logger.error()`
- Exceptions are caught and returned as JSON
- No silent try/except blocks that swallow errors

---

## 🔧 REQUIRED FIXES

### Fix 1: Parser Logic (CRITICAL)
**File:** `web_server.py`  
**Function:** `as_parse_automated_signal_payload()`  
**Issue:** Not setting `format_kind` for direct telemetry payloads

**Solution:** Add fallback logic to detect direct telemetry format:
```python
# After all format detection, add fallback:
if format_kind is None and event_type and trade_id:
    format_kind = "direct_telemetry"
    normalized = True
```

### Fix 2: Validation Logic (CRITICAL)
**File:** `web_server.py`  
**Function:** `as_validate_parsed_payload()`  
**Issue:** Too strict - rejects valid payloads

**Solution:** Make `format_kind` optional or provide better fallback:
```python
# Allow format_kind to be optional if event_type and trade_id are valid
if "format_kind" not in canonical or not canonical["format_kind"]:
    if canonical.get("event_type") and canonical.get("trade_id"):
        canonical["format_kind"] = "unknown_valid"
```

### Fix 3: Payload Field Mapping (ENHANCEMENT)
**Issue:** TradingView may send different field names

**Solution:** Add field normalization:
- `signal_id` → `trade_id`
- `sl_price` → `stop_loss`
- `bias` → `direction` mapping

### Fix 4: Logging Enhancement (ENHANCEMENT)
**Issue:** Need better visibility into webhook failures

**Solution:** Add detailed logging at each validation step

---

## 📊 CURRENT SCHEMA

**Table:** `automated_signals`

**Columns (from schema file):**
```sql
id SERIAL PRIMARY KEY
event_type VARCHAR(20) NOT NULL
trade_id VARCHAR(100) NOT NULL
direction VARCHAR(10)
entry_price DECIMAL(10, 2)
stop_loss DECIMAL(10, 2)
risk_distance DECIMAL(10, 2)
target_1r through target_20r DECIMAL(10, 2)
current_price DECIMAL(10, 2)
mfe DECIMAL(10, 4)
be_mfe DECIMAL(10, 4)  -- Added later
no_be_mfe DECIMAL(10, 4)  -- Added later
exit_price DECIMAL(10, 2)
final_mfe DECIMAL(10, 4)
session VARCHAR(20)
bias VARCHAR(20)
signal_date DATE  -- Added later
signal_time TIME  -- Added later
timestamp BIGINT
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**Indexes:**
- `idx_automated_signals_trade_id`
- `idx_automated_signals_event_type`
- `idx_automated_signals_timestamp`
- `idx_automated_signals_created_at`

---

## ✅ VERIFICATION CHECKLIST

After fixes are applied:

- [ ] Test webhook with direct telemetry payload
- [ ] Test webhook with strategy format payload
- [ ] Test webhook with indicator format payload
- [ ] Verify signal count increases in stats endpoint
- [ ] Check Railway logs for successful inserts
- [ ] Test all 4 event types: ENTRY, MFE_UPDATE, BE_TRIGGERED, EXIT_SL
- [ ] Verify dashboard displays new signals
- [ ] Test with actual TradingView webhook

---

## 🚀 DEPLOYMENT PLAN

1. Apply fixes to `web_server.py`
2. Run local tests with `phase2a_test_suite.py`
3. Commit changes via GitHub Desktop
4. Push to main branch (triggers Railway auto-deploy)
5. Wait 2-3 minutes for deployment
6. Run production verification with `phase2a_diagnostic_complete.py`
7. Monitor Railway logs for any errors
8. Test with live TradingView webhook

---

## 📝 NOTES

- The database already has 869 signals, so the system was working previously
- The validation logic may have been added recently and broke the ingestion
- The stats endpoint works correctly, confirming database connectivity
- No changes needed to database schema
- No changes needed to stats endpoint
- Focus is purely on webhook validation logic

---

**Status:** Ready for implementation  
**Priority:** CRITICAL  
**Estimated Fix Time:** 30 minutes  
**Testing Time:** 15 minutes  
**Total Time to Production:** ~1 hour
