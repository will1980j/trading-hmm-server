# ✅ RAW BODY LOGGING ADDED

**Status:** Raw webhook body logging has been added to the automated signals webhook endpoint for debugging malformed JSON.

## Changes Made

**File:** `web_server.py`  
**Location:** Lines 10454-10455 (inside `automated_signals_webhook()` function)

### Code Added

```python
# Log raw body for debugging malformed JSON
raw_body = request.data.decode("utf-8", errors="ignore")
logger.error("🔎 RAW WEBHOOK BODY:\n" + raw_body)
```

### Placement

The logging was added **before** any JSON parsing attempts:

```python
def automated_signals_webhook():
    """
    Webhook endpoint for automated trading signals from TradingView
    ...
    """
    try:
        # Log raw body for debugging malformed JSON
        raw_body = request.data.decode("utf-8", errors="ignore")
        logger.error("🔎 RAW WEBHOOK BODY:\n" + raw_body)
        
        # First try the normal Flask JSON parsing
        data = None
        try:
            data = request.get_json(silent=True)
        except Exception:
            data = None
        
        # Fallback: if no JSON detected, try to decode raw body as JSON
        if data is None:
            raw = request.data.decode("utf-8") if request.data else ""
            ...
```

## Purpose

This logging helps diagnose webhook issues by:

1. **Capturing exact payload** - See exactly what TradingView sends
2. **Detecting malformed JSON** - Identify syntax errors in the payload
3. **Debugging Content-Type issues** - Verify the raw body content
4. **Troubleshooting encoding** - Uses `errors="ignore"` to handle any encoding issues

## Log Output Example

When a webhook is received, Railway logs will show:

```
🔎 RAW WEBHOOK BODY:
{"type":"ENTRY","signal_id":"20251121_143022_BULLISH","direction":"Bullish","entry_price":4156.25,"stop_loss":4131.00,"session":"NY AM","bias":"Bullish"}
```

## Benefits

✅ **Always logs** - Runs before any parsing, so captures all requests  
✅ **Error-safe** - Uses `errors="ignore"` to handle encoding issues  
✅ **Visible in Railway** - Shows up in Railway deployment logs  
✅ **Debugging aid** - Makes it easy to spot malformed JSON or unexpected formats  
✅ **No performance impact** - Minimal overhead for logging

## Viewing Logs

**On Railway:**
1. Go to Railway dashboard
2. Select your deployment
3. Click "Deployments" tab
4. Click "View Logs"
5. Search for "🔎 RAW WEBHOOK BODY"

**Example log search:**
```
🔎 RAW WEBHOOK BODY
```

## Note

This uses `logger.error()` (not `logger.info()`) to ensure it appears in Railway logs even with default log levels. This is intentional for debugging purposes.

## Deployment

Ready to deploy via:
1. Open GitHub Desktop
2. Stage changes to `web_server.py`
3. Commit: "Add raw body logging to webhook for debugging"
4. Push to main branch
5. Railway auto-deploys within 2-3 minutes

After deployment, all webhook requests will log their raw body for debugging!
