# TradingView Alert Setup Guide - SIGNAL_CREATED Webhooks

## Current Situation

**Problem:** Indicator code sends SIGNAL_CREATED webhooks, but TradingView alerts are not configured to actually send them.

**Evidence:**
- ✅ Indicator has SIGNAL_CREATED webhook code (lines 1299-1314)
- ✅ Backend has handle_signal_created function
- ❌ Database has 0 SIGNAL_CREATED events
- ❌ All Signals tab is empty

**Solution:** Configure TradingView alerts to send SIGNAL_CREATED webhooks

---

## Step-by-Step Alert Setup

### Step 1: Open TradingView Chart

1. Go to TradingView
2. Open your chart with the indicator: `complete_automated_trading_system`
3. Ensure indicator is loaded and showing triangles

### Step 2: Create Alert for SIGNAL_CREATED

1. Click the **Alert** icon (clock with bell) in the top toolbar
2. Click **+ Create Alert** button

### Step 3: Configure Alert Condition

**Condition Settings:**
- **Select:** Your indicator name (`complete_automated_trading_system`)
- **Condition:** `Any alert() function call`
- **Options:** Leave default (Once Per Bar Close)

### Step 4: Configure Alert Actions

**Alert Name:**
```
Automated Signals - SIGNAL_CREATED
```

**Message:**
```
{{strategy.order.alert_message}}
```

**Webhook URL:**
```
https://web-production-f8c3.up.railway.app/api/automated-signals/webhook
```

**Important Settings:**
- ✅ Check "Webhook URL"
- ✅ Ensure "Once Per Bar Close" is selected
- ✅ Set expiration to "Open-ended"

### Step 5: Save Alert

1. Click **Create** button
2. Verify alert appears in your alert list
3. Check that webhook URL is shown

---

## Verification Steps

### Immediate Verification (Within 1 Minute)

**Wait for next triangle to appear, then:**

1. **Check TradingView Alert Log:**
   - Click Alert icon
   - Look for recent alert firing
   - Should see "Automated Signals - SIGNAL_CREATED" fired

2. **Check Database:**
```bash
python -c "import psycopg2; import os; from dotenv import load_dotenv; load_dotenv(); conn = psycopg2.connect(os.getenv('DATABASE_URL')); cur = conn.cursor(); cur.execute('SELECT COUNT(*) FROM automated_signals WHERE event_type = \\'SIGNAL_CREATED\\''); print(f'SIGNAL_CREATED count: {cur.fetchone()[0]}'); cur.close(); conn.close()"
```

**Expected:** Count should be > 0

3. **Check All Signals Tab:**
   - Go to: https://web-production-f8c3.up.railway.app/automated-signals
   - Click "All Signals" tab
   - Should see signals appearing

### After 1 Hour of Trading

**Run gap detection:**
```bash
python test_hybrid_sync_status.py
```

**Expected Results:**
```
Total Gaps: ~7 (down from 86)
Health Score: 90+/100 (up from 0)

Gap Breakdown:
  no_htf_alignment: 0     ✅ (was 36)
  no_confirmation_time: 0 ✅ (was 36)
  no_mfe_update: 7        (active trades - normal)
  no_mae: 2               (active trades - normal)
  no_targets: 0           ✅ (was 5)
```

---

## Troubleshooting

### Alert Not Firing

**Check:**
1. Is indicator loaded on chart?
2. Are triangles appearing?
3. Is alert enabled (not paused)?
4. Is alert expiration set correctly?

**Fix:**
- Reload indicator
- Recreate alert
- Check TradingView subscription allows webhooks

### Webhook Not Reaching Backend

**Check Railway Logs:**
1. Go to Railway dashboard
2. View logs
3. Search for "SIGNAL_CREATED"
4. Look for webhook reception logs

**If no logs:**
- Verify webhook URL is correct
- Check Railway deployment is running
- Test webhook manually (see below)

### Manual Webhook Test

**Send test SIGNAL_CREATED webhook:**
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
      "m15": "Bullish",
      "m5": "Bullish",
      "m1": "Bullish"
    },
    "event_timestamp": "2025-12-13T12:00:00"
  }'
```

**Check if it was stored:**
```bash
python check_signal_created_detailed.py
```

### Database Shows 0 SIGNAL_CREATED After Alert Fires

**Possible causes:**
1. Backend not handling SIGNAL_CREATED properly
2. Lifecycle enforcement blocking it
3. Database connection issue

**Debug:**
```bash
# Check Railway logs for errors
# Look for "SIGNAL_CREATED" and any error messages

# Check if backend is running
curl https://web-production-f8c3.up.railway.app/health

# Test manual webhook (above)
```

---

## Expected Behavior After Setup

### Immediate (First Signal)

1. **Triangle appears on chart**
2. **Alert fires** (visible in TradingView alert log)
3. **Webhook sent** to Railway
4. **SIGNAL_CREATED event stored** in database
5. **All Signals tab shows signal** (pending confirmation)

### After Confirmation

1. **Confirmation happens** (bullish candle closes above signal high)
2. **ENTRY webhook sent**
3. **All Signals tab updates** signal to "CONFIRMED"
4. **Bars to confirmation calculated** (ENTRY timestamp - SIGNAL_CREATED timestamp)

### After Cancellation

1. **Opposite signal appears** before confirmation
2. **CANCELLED webhook sent**
3. **All Signals tab updates** signal to "CANCELLED"
4. **New SIGNAL_CREATED** for opposite direction

### Hybrid Sync Service (Every 2 Minutes)

1. **Detects any gaps** in data
2. **Uses SIGNAL_CREATED** to fill HTF alignment gaps (Tier 0)
3. **Calculates confirmation_time** from timestamps
4. **Health score improves** to 90+

---

## Success Metrics

### Before Alert Setup
- SIGNAL_CREATED events: 0
- All Signals tab: Empty
- Total gaps: 86
- Health score: 0/100
- HTF alignment gaps: 36
- Confirmation time gaps: 36

### After Alert Setup (1 Hour)
- SIGNAL_CREATED events: 10+ (depending on market activity)
- All Signals tab: Showing all triangles
- Total gaps: ~7
- Health score: 90+/100
- HTF alignment gaps: 0 ✅
- Confirmation time gaps: 0 ✅

---

## Alert Configuration Checklist

- [ ] Alert created on TradingView
- [ ] Condition: "Any alert() function call"
- [ ] Frequency: "Once Per Bar Close"
- [ ] Message: `{{strategy.order.alert_message}}`
- [ ] Webhook URL configured
- [ ] Webhook URL correct: `https://web-production-f8c3.up.railway.app/api/automated-signals/webhook`
- [ ] Expiration: "Open-ended"
- [ ] Alert enabled (not paused)
- [ ] Alert appears in alert list
- [ ] First alert fired successfully
- [ ] Database shows SIGNAL_CREATED events
- [ ] All Signals tab populated
- [ ] Gap detection shows improvement

---

## Next Steps After Alert Setup

1. **Wait for 1 hour of trading** to collect signals
2. **Run gap detection** to verify improvement
3. **Check All Signals tab** for complete data
4. **Monitor health score** (should be 90+)
5. **Verify hybrid sync** is filling remaining gaps

---

## Support

### Check System Status
```bash
python test_hybrid_sync_status.py
```

### Check SIGNAL_CREATED Events
```bash
python check_signal_created_detailed.py
```

### Check All Signals API
```bash
curl https://web-production-f8c3.up.railway.app/api/automated-signals/all-signals
```

### View Railway Logs
```
https://railway.app/project/[your-project-id]/logs
```

Filter for: "SIGNAL_CREATED" or "webhook"

---

**Once alerts are configured, the entire hybrid sync system will activate and data quality will dramatically improve!**
