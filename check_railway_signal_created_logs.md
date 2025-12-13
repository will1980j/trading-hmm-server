# Checking Railway Logs for SIGNAL_CREATED

## Issue
- Indicator IS sending SIGNAL_CREATED webhooks (code confirmed)
- Database has 0 SIGNAL_CREATED events
- All 36 ENTRY events have no corresponding SIGNAL_CREATED

## Possible Causes

### 1. Alert Not Configured on TradingView
**Check:** Are the SIGNAL_CREATED alerts actually set up on TradingView?
- Go to TradingView chart
- Check Alert list
- Look for alerts with "SIGNAL_CREATED" in the message
- Verify webhook URL is configured

### 2. Webhook URL Not Set
**Check:** Does the SIGNAL_CREATED alert have the webhook URL?
- Alert should point to: `https://web-production-f8c3.up.railway.app/api/automated-signals/webhook`
- Verify it's not pointing to old/wrong URL

### 3. Backend Not Handling SIGNAL_CREATED
**Check:** Is the backend properly routing SIGNAL_CREATED events?
- Code shows `handle_signal_created` function exists
- Need to verify it's being called

### 4. Lifecycle Enforcement Blocking
**Check:** Is lifecycle enforcement rejecting SIGNAL_CREATED?
- Code shows: `if new_event_type in ("ENTRY", "signal_created", "SIGNAL_CREATED"): return None`
- This suggests SIGNAL_CREATED should be allowed

## Investigation Steps

### Step 1: Check TradingView Alerts
1. Open TradingView chart with indicator
2. Click Alert icon
3. Look for alerts containing "SIGNAL_CREATED"
4. Verify webhook URL is set
5. Check if alerts are firing (alert log)

### Step 2: Check Railway Logs
1. Go to Railway dashboard
2. View logs for last 24 hours
3. Search for "SIGNAL_CREATED"
4. Look for webhook reception logs
5. Check for any errors

### Step 3: Test SIGNAL_CREATED Webhook Manually
```bash
curl -X POST https://web-production-f8c3.up.railway.app/api/automated-signals/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "SIGNAL_CREATED",
    "trade_id": "20251213_120000000_BULLISH",
    "direction": "Bullish",
    "session": "NY AM",
    "signal_date": "2025-12-13",
    "signal_time": "12:00:00",
    "htf_alignment": {
      "daily": "Bullish",
      "h1": "Bullish",
      "m15": "Bullish"
    },
    "event_timestamp": "2025-12-13T12:00:00"
  }'
```

### Step 4: Check Database After Manual Test
```bash
python -c "import psycopg2; import os; from dotenv import load_dotenv; load_dotenv(); conn = psycopg2.connect(os.getenv('DATABASE_URL')); cur = conn.cursor(); cur.execute('SELECT COUNT(*) FROM automated_signals WHERE event_type = \\'SIGNAL_CREATED\\''); print(f'SIGNAL_CREATED count: {cur.fetchone()[0]}'); cur.close(); conn.close()"
```

## Most Likely Cause

**The SIGNAL_CREATED alerts are probably not configured on TradingView.**

Even though the indicator code sends SIGNAL_CREATED webhooks, the alerts need to be manually set up on TradingView with:
1. Alert condition: "Any alert() function call"
2. Webhook URL configured
3. Alert message: {{strategy.order.alert_message}} or similar

## Solution

### If Alerts Not Configured:
1. Open TradingView chart
2. Add alert for indicator
3. Set condition to "Any alert() function call"
4. Set webhook URL
5. Enable alert

### If Alerts Configured But Not Working:
1. Check Railway logs for errors
2. Verify webhook URL is correct
3. Test manual webhook (Step 3 above)
4. Check backend routing logic

## Expected Behavior After Fix

Once SIGNAL_CREATED alerts are properly configured:
- Every triangle should create a SIGNAL_CREATED event
- Database should show SIGNAL_CREATED events
- Gap count should drop from 86 to ~7
- Health score should jump to 90+
- All Signals tab should show complete data
