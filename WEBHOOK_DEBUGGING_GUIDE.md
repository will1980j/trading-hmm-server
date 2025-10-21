# TradingView Webhook Signal Debugging Guide

## Issue: Only Bullish Signals Received

### Quick Diagnostic Steps

1. **Check Webhook Monitor Dashboard**
   - Navigate to: `http://your-server/webhook-monitor`
   - View signal counts for Bullish vs Bearish
   - Check "Last Received" timestamps

2. **Run Diagnostic Endpoint**
   ```bash
   curl http://your-server/api/webhook-diagnostic
   ```

3. **Test Both Signal Types**
   - Click "Test Bullish Signal" button
   - Click "Test Bearish Signal" button
   - Verify both appear in dashboard

### Common Issues & Solutions

#### Issue 1: TradingView Alert Not Configured for Bearish
**Symptom**: Only bullish signals in logs
**Solution**: 
- Check TradingView alert conditions
- Ensure alert triggers on BOTH bias changes
- Alert message should include: `"bias":"{{plot("bias")}}"`

#### Issue 2: Webhook URL Incorrect
**Symptom**: No signals at all
**Solution**:
- Verify webhook URL: `https://your-server.com/api/live-signals`
- Check TradingView webhook settings
- Test with: `curl -X POST https://your-server.com/api/live-signals -d "SIGNAL:Bearish:20500:75:ALIGNED:ALIGNED:2024-01-15T10:00:00"`

#### Issue 3: Signal Parsing Error
**Symptom**: Signals received but not processed
**Solution**:
- Check server logs for parsing errors
- View `/api/webhook-failures` for error messages
- Verify signal format matches expected pattern

### TradingView Alert Configuration

#### Correct Alert Message Format
```javascript
{
  "bias": "{{plot("bias")}}",
  "price": {{close}},
  "strength": 75,
  "htf_status": "ALIGNED",
  "htf_aligned": true,
  "symbol": "{{ticker}}"
}
```

#### Alert Conditions
- **Condition**: `bias` changes value
- **Trigger**: Once Per Bar Close
- **Expiration**: Open-ended
- **Webhook URL**: `https://your-server.com/api/live-signals`

### Server-Side Logging

#### View Raw Webhook Logs
```sql
SELECT * FROM webhook_debug_log 
ORDER BY received_at DESC 
LIMIT 20;
```

#### View Signal Processing Logs
```sql
SELECT bias, status, COUNT(*) 
FROM signal_processing_log 
WHERE processed_at > NOW() - INTERVAL '24 hours'
GROUP BY bias, status;
```

#### Check for Filtering Issues
```sql
-- Should show both Bullish and Bearish
SELECT bias, COUNT(*) as count
FROM live_signals
WHERE timestamp > NOW() - INTERVAL '1 hour'
GROUP BY bias;
```

### Testing Workflow

1. **Test Server Reception**
   ```bash
   # Test Bullish
   curl -X POST http://localhost:5000/api/live-signals \
     -H "Content-Type: text/plain" \
     -d "SIGNAL:Bullish:20500:75:ALIGNED:ALIGNED:2024-01-15T10:00:00"
   
   # Test Bearish
   curl -X POST http://localhost:5000/api/live-signals \
     -H "Content-Type: text/plain" \
     -d "SIGNAL:Bearish:20500:75:ALIGNED:ALIGNED:2024-01-15T10:00:00"
   ```

2. **Verify Database Storage**
   ```sql
   SELECT bias, symbol, price, timestamp 
   FROM live_signals 
   ORDER BY timestamp DESC 
   LIMIT 10;
   ```

3. **Check Signal Lab Population**
   ```sql
   SELECT bias, session, created_at 
   FROM signal_lab_trades 
   WHERE active_trade = true 
   ORDER BY created_at DESC;
   ```

### Monitoring Endpoints

- **Webhook Monitor**: `/webhook-monitor`
- **Signal Stats**: `/api/webhook-stats`
- **Health Check**: `/api/webhook-health`
- **Failures**: `/api/webhook-failures`
- **Diagnostic**: `/api/webhook-diagnostic`

### Expected Behavior

✅ **Healthy System**:
- Both Bullish and Bearish signals received
- Signal processing success rate > 95%
- No alerts in webhook health check
- Both signal types in last hour

❌ **Problem Indicators**:
- Only one signal type received
- High failure rate in processing log
- Alerts for missing signal types
- Large time gap between signal types

### Debug Checklist

- [ ] Webhook URL correct in TradingView
- [ ] Alert triggers on both bias changes
- [ ] Server logs show both signal types
- [ ] Database contains both signal types
- [ ] No filtering logic blocking signals
- [ ] Test signals work for both types
- [ ] ML predictions work for both types

### Contact Points

If issue persists after following this guide:
1. Check server logs: `tail -f server.log | grep "WEBHOOK"`
2. Review webhook debug logs in database
3. Test with manual curl commands
4. Verify TradingView alert is actually triggering
