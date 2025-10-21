# Webhook Signal Filtering Fix - Implementation Summary

## Problem
Only receiving bullish signals from TradingView webhook, bearish signals missing.

## Solution Implemented

### 1. Comprehensive Logging System
**Files Created:**
- `webhook_debugger.py` - Core debugging class with signal tracking
- `init_webhook_debug.py` - Database table initialization
- `create_webhook_debug_tables.sql` - SQL schema

**Features:**
- Logs ALL incoming webhook requests (raw payload)
- Tracks signal processing success/failure
- Maintains counters for bullish vs bearish signals
- Records timestamps for last signal of each type

### 2. Webhook Monitoring Dashboard
**File:** `webhook_monitor.html`

**Features:**
- Real-time signal count display (Bullish vs Bearish)
- Last received timestamps for each signal type
- Health status alerts for missing signal types
- Test buttons to manually send both signal types
- Recent signal log (last 24 hours)
- Failed signal log with error messages
- Auto-refresh every 10 seconds

### 3. Enhanced Server Logging
**Modified:** `web_server.py`

**Changes:**
- Added webhook debugger initialization
- Enhanced logging in `/api/live-signals` endpoint
- Logs raw webhook data on reception
- Logs parsed signal data with bias
- Logs successful signal processing
- Logs failed signal processing with errors
- Added emoji markers for easy log scanning

### 4. New API Endpoints

#### `/webhook-monitor` (Dashboard)
Visual monitoring interface for signal reception

#### `/api/webhook-stats` (GET)
Returns signal statistics:
- Last 24h breakdown by bias
- Total counters
- Last received timestamps

#### `/api/webhook-health` (GET)
Health check for signal reception:
- Checks if both signal types received in last hour
- Returns alerts for missing signal types
- Recent signal counts

#### `/api/webhook-failures` (GET)
Returns recent failed signals with error messages

#### `/api/test-webhook-signal` (POST)
Test endpoint to manually send signals:
```json
{
  "bias": "Bearish",
  "symbol": "NQ1!",
  "price": 20500.00
}
```

#### `/api/webhook-diagnostic` (GET)
Comprehensive diagnostic:
- Database connection status
- Signal pipeline status
- 24h signal breakdown
- Last hour bias ratio
- Potential issues detection

### 5. Database Schema

**New Tables:**
```sql
webhook_debug_log
- id, raw_payload, parsed_data, source, received_at

signal_processing_log
- id, bias, symbol, price, status, error_message, processed_at
```

**New View:**
```sql
signal_stats_24h
- Aggregates signals by bias for last 24 hours
```

## Setup Instructions

### 1. Initialize Database Tables
```bash
python init_webhook_debug.py
```

### 2. Restart Server
The webhook debugger will auto-initialize on server start.

### 3. Access Monitoring Dashboard
Navigate to: `http://your-server/webhook-monitor`

### 4. Test Signal Reception
Click the test buttons:
- 🟢 Test Bullish Signal
- 🔴 Test Bearish Signal

Both should appear in the dashboard immediately.

## Debugging Workflow

### Step 1: Check Dashboard
1. Open `/webhook-monitor`
2. Look at signal counts
3. Check "Last Received" timestamps
4. Review health status alerts

### Step 2: Test Manually
1. Click "Test Bearish Signal"
2. Verify it appears in logs
3. Check database for entry

### Step 3: Check TradingView
If test signals work but real signals don't:
- Verify TradingView alert is configured for BOTH bias changes
- Check alert message includes `"bias":"{{plot("bias")}}"`
- Ensure alert is actually triggering (check TradingView alert log)

### Step 4: Review Server Logs
Look for these log entries:
```
🔥 WEBHOOK RECEIVED: [raw data]
📊 PARSED SIGNAL: bias=Bearish, symbol=NQ1!, price=20500
✅ Signal stored: NQ1! Bearish at 20500
```

### Step 5: Check Database
```sql
-- Should show both Bullish and Bearish
SELECT bias, COUNT(*) 
FROM signal_processing_log 
WHERE processed_at > NOW() - INTERVAL '1 hour'
GROUP BY bias;
```

## Expected Log Output

### Successful Bearish Signal:
```
🔥 WEBHOOK RECEIVED: SIGNAL:Bearish:20500:75:ALIGNED:ALIGNED:2024-01-15T10:00:00
📊 PARSED SIGNAL: bias=Bearish, symbol=NQ1!, price=20500.0, htf=ALIGNED
✅ Signal stored: NQ1! Bearish at 20500.0 | Strength: 0% | HTF: ALIGNED | Session: NY AM
```

### Failed Signal:
```
🔥 WEBHOOK RECEIVED: [malformed data]
❌ ERROR capturing live signal: [error message]
```

## Monitoring Metrics

### Healthy System:
- Bullish signals: > 0 in last hour
- Bearish signals: > 0 in last hour
- Success rate: > 95%
- No health alerts

### Problem Indicators:
- Only one signal type received
- Health alert: "No bearish signals in last hour"
- High failure count
- Large time gap between signal types

## Common Issues & Solutions

### Issue: No Bearish Signals
**Check:**
1. TradingView alert condition triggers on bias change
2. Alert message format includes bias field
3. Server logs show webhook reception
4. No parsing errors in logs

### Issue: Signals Received But Not Processed
**Check:**
1. `/api/webhook-failures` for error messages
2. Database connection status
3. Signal parsing logic
4. ML model availability

### Issue: Test Signals Work, Real Signals Don't
**Solution:**
- Problem is in TradingView configuration
- Check alert conditions
- Verify webhook URL
- Test alert manually in TradingView

## Files Modified/Created

### Created:
- `webhook_debugger.py` - Core debugging logic
- `webhook_monitor.html` - Monitoring dashboard
- `init_webhook_debug.py` - Database setup
- `create_webhook_debug_tables.sql` - SQL schema
- `WEBHOOK_DEBUGGING_GUIDE.md` - Detailed guide
- `WEBHOOK_FIX_SUMMARY.md` - This file

### Modified:
- `web_server.py` - Added logging and endpoints

## Next Steps

1. Run `python init_webhook_debug.py` to create tables
2. Restart server
3. Open `/webhook-monitor` dashboard
4. Test both signal types
5. Monitor for 1 hour
6. Check if both signal types are received
7. If only bullish signals, check TradingView alert configuration

## Success Criteria

✅ Both bullish and bearish signals appear in dashboard
✅ No health alerts for missing signal types
✅ Signal processing success rate > 95%
✅ Both signal types in database
✅ ML predictions work for both types

## Support

If issues persist:
1. Check server logs: `grep "WEBHOOK" server.log`
2. Review `/api/webhook-diagnostic` output
3. Test with curl commands (see debugging guide)
4. Verify TradingView alert is triggering
