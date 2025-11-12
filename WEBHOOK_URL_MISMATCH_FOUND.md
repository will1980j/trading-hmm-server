# WEBHOOK URL MISMATCH FOUND

## The Problem:

**Indicator is sending to:** `/api/automated-signals/webhook`
**Backend endpoint is:** `/api/automated-signals`

This is why you're getting 405 Method Not Allowed!

## The Evidence:

1. **Diagnostic shows:** Last webhook was 1 day, 19 hours ago
2. **No ENTRY events:** Only MFE_UPDATE, BE_TRIGGERED, EXIT events
3. **405 Error:** When testing `/api/automated-signals/webhook`
4. **Backend code:** Shows endpoint is `/api/automated-signals` (line 10353 in web_server.py)

## The Fix:

### Option 1: Update TradingView Alert (RECOMMENDED)
Change webhook URL in TradingView alert to:
```
https://web-production-cd33.up.railway.app/api/automated-signals
```

### Option 2: Add Route Alias in Backend
Add this to web_server.py:
```python
@app.route('/api/automated-signals/webhook', methods=['POST'])
def automated_signals_webhook_alias():
    """Alias for backward compatibility"""
    return automated_signals_webhook()
```

## Why This Happened:

The indicator code comments and documentation reference `/api/automated-signals/webhook`, but the actual Flask route is `/api/automated-signals`. This mismatch means TradingView alerts are hitting a non-existent endpoint.

## Immediate Action Required:

1. Check your TradingView alert settings
2. Verify the webhook URL
3. Update to correct URL: `https://web-production-cd33.up.railway.app/api/automated-signals`
4. Save alert
5. Wait for next signal confirmation
6. Verify webhook reception in database

## How to Verify Alert Settings:

1. Open TradingView
2. Click bell icon (Alerts)
3. Find "Automated Trading Signals" or similar alert
4. Click edit (pencil icon)
5. Scroll to "Notifications" section
6. Check "Webhook URL" field
7. Should be: `https://web-production-cd33.up.railway.app/api/automated-signals`
8. NOT: `https://web-production-cd33.up.railway.app/api/automated-signals/webhook`

## Expected Result:

Once URL is corrected, confirmed signals will immediately start appearing in the database and dashboard.
