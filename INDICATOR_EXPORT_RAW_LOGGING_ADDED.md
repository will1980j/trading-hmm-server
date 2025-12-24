# Indicator Export Raw Payload Logging Added

## Problem
When `/api/indicator-export` receives invalid JSON from TradingView, we need to see exactly what was sent to diagnose the issue.

## Solution Implemented

### File Modified
**File:** `automated_signals_api_robust.py`
**Route:** `POST /api/indicator-export`
**Commit:** `2148a56` - "Log raw payload on indicator-export invalid JSON"

### Changes Made

#### 1. Capture Raw Request Data (Before JSON Parsing)
```python
# Capture raw request data BEFORE parsing
ct = request.headers.get("Content-Type", "")
raw = request.get_data(as_text=True) or ""
raw_len = len(raw)
```

#### 2. Enhanced Error Logging
```python
except Exception as e:
    # Log detailed error with raw payload info (truncated for safety)
    logger.error("[INDICATOR_EXPORT] Invalid JSON ct=%s len=%d head=%s", ct, raw_len, raw[:1500])
```

**Logs:**
- Content-Type header
- Total body length
- First 1500 characters of raw body

#### 3. Detailed Error Response
```python
return jsonify({
    'success': False,
    'error': 'invalid_json',
    'content_type': ct,
    'body_len': raw_len,
    'body_head': raw[:500]
}), 400
```

**Returns:**
- Content-Type header
- Total body length
- First 500 characters of raw body (truncated for safety)

### Security Considerations

✅ **Token Protection:** The token is checked BEFORE raw data capture, so it's never logged or returned in error responses.

✅ **Truncation:** Raw body is truncated to:
- 1500 chars in logs
- 500 chars in API response

✅ **No Sensitive Data:** Only captures what TradingView sends (public indicator data).

## Testing

### Test Invalid JSON
```bash
curl -X POST https://web-production-f8c3.up.railway.app/api/indicator-export?token=YOUR_TOKEN \
  -H "Content-Type: application/json" \
  -d "INVALID JSON HERE"
```

**Expected Response:**
```json
{
  "success": false,
  "error": "invalid_json",
  "content_type": "application/json",
  "body_len": 18,
  "body_head": "INVALID JSON HERE"
}
```

**Expected Log:**
```
[INDICATOR_EXPORT] Invalid JSON ct=application/json len=18 head=INVALID JSON HERE
```

### Test Valid JSON (Should Work Normally)
```bash
curl -X POST https://web-production-f8c3.up.railway.app/api/indicator-export?token=YOUR_TOKEN \
  -H "Content-Type: application/json" \
  -d '{"event_type":"INDICATOR_EXPORT_V2","signals":[]}'
```

**Expected:** Normal processing (no error logs)

## Diagnostic Use Cases

### Case 1: TradingView Sends Malformed JSON
**Symptom:** 400 errors in Railway logs
**Diagnosis:** Check logs for `[INDICATOR_EXPORT] Invalid JSON` with raw payload
**Fix:** Identify what TradingView is sending incorrectly

### Case 2: Wrong Content-Type
**Symptom:** JSON parsing fails
**Diagnosis:** Check `content_type` in error response
**Fix:** Verify TradingView alert is sending `application/json`

### Case 3: Truncated Payload
**Symptom:** Incomplete data
**Diagnosis:** Check `body_len` vs expected size
**Fix:** Investigate TradingView alert size limits

### Case 4: Encoding Issues
**Symptom:** Special characters causing parse errors
**Diagnosis:** Check `body_head` for encoding problems
**Fix:** Adjust indicator to avoid problematic characters

## What Gets Logged

### Success Case (No Logs)
```
[INDICATOR_EXPORT] Received request
[INDICATOR_EXPORT] event_type=INDICATOR_EXPORT_V2, batch=1, size=100, hash=abc12345, symbol=NQ, has_ohlc=False, bar_ts=None
```

### Error Case (With Raw Payload)
```
[INDICATOR_EXPORT] Received request
[INDICATOR_EXPORT] Invalid JSON ct=application/json len=1234 head={"event_type":"INDICATOR_EXPORT_V2","signals":[{"trade_id":"20251221_143000_Bullish"...
```

## Next Steps

1. ✅ Deploy to Railway (commit already made)
2. Monitor Railway logs for `[INDICATOR_EXPORT] Invalid JSON` messages
3. If errors occur, examine the `head=` portion to see what TradingView sent
4. Use the raw payload to reproduce and fix the issue

## Files Modified

- `automated_signals_api_robust.py` - Added raw payload capture and logging

## Syntax Verified

```bash
python -m py_compile automated_signals_api_robust.py
# Exit Code: 0 ✅
```

## Committed

```bash
git add automated_signals_api_robust.py
git commit -m "Log raw payload on indicator-export invalid JSON"
# Commit: 2148a56 ✅
```
