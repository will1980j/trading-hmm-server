# Webhook Signal Debugging System

## Quick Start

### 1. Setup (One-time)
```bash
# Run setup script
setup_webhook_debug.bat

# Or manually:
python init_webhook_debug.py
```

### 2. Start Server
```bash
python web_server.py
```

### 3. Open Monitoring Dashboard
Navigate to: `http://localhost:5000/webhook-monitor`

### 4. Test Signal Reception
Click the test buttons in the dashboard:
- 🟢 Test Bullish Signal
- 🔴 Test Bearish Signal

Both should appear immediately in the signal log.

## Tools & Dashboards

### Web Dashboard
**URL:** `/webhook-monitor`

**Features:**
- Real-time signal counts (Bullish vs Bearish)
- Last received timestamps
- Health status alerts
- Test signal buttons
- Recent signal log
- Failed signal log
- Auto-refresh every 10 seconds

### Command-Line Log Viewer
```bash
# Follow logs in real-time
python webhook_log_viewer.py follow

# Show recent logs
python webhook_log_viewer.py recent

# Show processing logs
python webhook_log_viewer.py processing

# Show statistics
python webhook_log_viewer.py stats
```

### API Endpoints

#### GET `/api/webhook-stats`
Returns signal statistics for last 24 hours
```json
{
  "last_24h": [
    {"bias": "Bullish", "count": 45, "last_received": "2024-01-15T14:30:00"},
    {"bias": "Bearish", "count": 38, "last_received": "2024-01-15T14:28:00"}
  ],
  "last_bullish": "2024-01-15T14:30:00",
  "last_bearish": "2024-01-15T14:28:00"
}
```

#### GET `/api/webhook-health`
Health check for signal reception
```json
{
  "healthy": true,
  "alerts": [],
  "recent_signals": {
    "Bullish": 12,
    "Bearish": 10
  }
}
```

#### GET `/api/webhook-failures`
Recent failed signals
```json
{
  "failures": [
    {
      "bias": "Unknown",
      "symbol": "NQ1!",
      "error_message": "Invalid price format",
      "processed_at": "2024-01-15T14:25:00"
    }
  ]
}
```

#### GET `/api/webhook-diagnostic`
Comprehensive diagnostic
```json
{
  "timestamp": "2024-01-15T14:30:00",
  "database": "connected",
  "webhook_debugger": "active",
  "signal_pipeline": {
    "live_signals_24h": [...],
    "signal_lab_24h": [...],
    "last_hour": {
      "total": 22,
      "bullish": 12,
      "bearish": 10,
      "ratio": "12:10"
    }
  },
  "potential_issues": []
}
```

#### POST `/api/test-webhook-signal`
Test signal endpoint
```json
{
  "bias": "Bearish",
  "symbol": "NQ1!",
  "price": 20500.00
}
```

## Debugging Workflow

### Problem: Only Bullish Signals Received

#### Step 1: Verify Server Reception
1. Open `/webhook-monitor`
2. Check signal counts
3. Click "Test Bearish Signal"
4. Verify it appears in logs

**If test works:** Problem is in TradingView configuration
**If test fails:** Problem is in server code

#### Step 2: Check TradingView Configuration
1. Open TradingView alert settings
2. Verify alert condition triggers on BOTH bias changes
3. Check alert message format:
```javascript
{
  "bias": "{{plot("bias")}}",
  "price": {{close}},
  "symbol": "{{ticker}}"
}
```
4. Ensure webhook URL is correct: `https://your-server.com/api/live-signals`

#### Step 3: Monitor Real-Time Logs
```bash
# Terminal 1: Follow webhook logs
python webhook_log_viewer.py follow

# Terminal 2: Watch server logs
tail -f server.log | grep "WEBHOOK"
```

Look for:
- 🔥 WEBHOOK RECEIVED: [shows raw data]
- 📊 PARSED SIGNAL: bias=Bearish [shows parsed data]
- ✅ Signal stored: [shows successful storage]

#### Step 4: Check Database
```sql
-- Should show both signal types
SELECT bias, COUNT(*) as count, MAX(timestamp) as last_signal
FROM live_signals
WHERE timestamp > NOW() - INTERVAL '1 hour'
GROUP BY bias;
```

Expected result:
```
bias     | count | last_signal
---------|-------|------------------
Bullish  | 12    | 2024-01-15 14:30
Bearish  | 10    | 2024-01-15 14:28
```

#### Step 5: Review Failures
```bash
# Check failed signals
python webhook_log_viewer.py processing
```

Look for error messages that indicate why bearish signals might be failing.

## Common Issues

### Issue 1: TradingView Alert Not Triggering
**Symptoms:**
- Test signals work
- No real signals in logs
- TradingView shows alert as active

**Solution:**
- Check alert condition logic
- Verify indicator is plotting bias correctly
- Test alert manually in TradingView

### Issue 2: Signal Parsing Error
**Symptoms:**
- Webhook logs show received data
- Processing logs show failures
- Error message in failures log

**Solution:**
- Check signal format matches expected pattern
- Review error message in `/api/webhook-failures`
- Verify price format is numeric

### Issue 3: Database Connection Issue
**Symptoms:**
- Signals received but not stored
- Database errors in logs

**Solution:**
- Check database connection: `python -c "from database.railway_db import RailwayDB; RailwayDB()"`
- Verify tables exist: `python init_webhook_debug.py`
- Check database credentials

## Log Patterns

### Successful Bearish Signal
```
🔥 WEBHOOK RECEIVED: SIGNAL:Bearish:20500:75:ALIGNED:ALIGNED:2024-01-15T10:00:00
📊 PARSED SIGNAL: bias=Bearish, symbol=NQ1!, price=20500.0, htf=ALIGNED
✅ Signal stored: NQ1! Bearish at 20500.0 | Strength: 0% | Session: NY AM
```

### Failed Signal
```
🔥 WEBHOOK RECEIVED: [malformed data]
❌ ERROR capturing live signal: Invalid price format
```

### Missing Signal Type
```
⚠️ HEALTH ALERT: No bearish signals in last hour
```

## Monitoring Best Practices

1. **Check dashboard every hour** during trading hours
2. **Monitor health alerts** for missing signal types
3. **Review failure logs** daily
4. **Test both signal types** weekly
5. **Verify TradingView alerts** are triggering

## Success Metrics

✅ **Healthy System:**
- Both signal types received in last hour
- Success rate > 95%
- No health alerts
- Balanced signal ratio (roughly 50/50)

❌ **Problem Indicators:**
- Only one signal type in last hour
- Success rate < 90%
- Health alerts present
- Large imbalance in signal ratio

## Files Reference

### Core Files
- `webhook_debugger.py` - Debugging logic
- `webhook_monitor.html` - Web dashboard
- `webhook_log_viewer.py` - CLI log viewer
- `init_webhook_debug.py` - Database setup

### Documentation
- `WEBHOOK_DEBUGGING_GUIDE.md` - Detailed guide
- `WEBHOOK_FIX_SUMMARY.md` - Implementation summary
- `README_WEBHOOK_DEBUG.md` - This file

### Setup
- `setup_webhook_debug.bat` - Windows setup script
- `create_webhook_debug_tables.sql` - SQL schema

## Support Commands

```bash
# View recent webhook logs
python webhook_log_viewer.py recent

# Follow logs in real-time
python webhook_log_viewer.py follow

# Show signal statistics
python webhook_log_viewer.py stats

# Test database connection
python -c "from database.railway_db import RailwayDB; print('✅ Connected')"

# Reinitialize tables
python init_webhook_debug.py

# Check server health
curl http://localhost:5000/api/webhook-health
```

## Next Steps

1. ✅ Run setup: `setup_webhook_debug.bat`
2. ✅ Start server: `python web_server.py`
3. ✅ Open dashboard: `http://localhost:5000/webhook-monitor`
4. ✅ Test both signal types
5. ✅ Monitor for 1 hour
6. ✅ Verify both types received
7. ✅ Check TradingView if issues persist

## Contact

If issues persist after following this guide:
1. Check `/api/webhook-diagnostic` for detailed status
2. Review server logs for errors
3. Test with manual curl commands
4. Verify TradingView alert configuration
