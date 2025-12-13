# Monday Morning Checklist - Hybrid Sync System

**When:** Market opens Monday  
**Goal:** Verify SIGNAL_CREATED webhooks flowing and system working

---

## ✅ Pre-Market Checklist

- [x] Database migrated
- [x] Backend code deployed
- [x] Hybrid sync service running
- [x] TradingView alert configured
- [x] Local testing passed

---

## 🕐 Market Open - First 5 Minutes

### 1. Wait for First Triangle
Watch TradingView chart for first triangle to appear

### 2. Check TradingView Alert Log
- Click Alert icon
- Verify "Automated Signals - SIGNAL_CREATED" fired
- Note the time

### 3. Check Database (30 seconds after alert)
```bash
python check_signal_created_detailed.py
```

**Expected:**
```
Total SIGNAL_CREATED events: 1+
```

**If 0:** Alert not configured or webhook URL wrong

### 4. Check All Signals Tab
Go to: https://web-production-f8c3.up.railway.app/automated-signals

Click "All Signals" tab

**Expected:** Signal appears with:
- Trade ID
- Direction
- Session
- HTF Alignment
- Status: PENDING or CONFIRMED

**If empty:** Check database first, then check API

---

## 🕐 After 1 Hour of Trading

### 5. Run Gap Detection
```bash
python test_hybrid_sync_status.py
```

**Expected:**
```
Total Gaps: ~7 (down from 86)
Health Score: 90+/100 (up from 0)

Gap Breakdown:
  no_htf_alignment: 0       ✅ (was 36)
  no_confirmation_time: 0   ✅ (was 36)
  no_mfe_update: 7          (active trades - normal)
  no_mae: 2                 (active trades - normal)
  no_targets: 0             ✅ (was 5)
```

**If gaps still high:** Check Railway logs for errors

### 6. Check All Signals Tab Completeness
- Should show 10+ signals
- Mix of PENDING, CONFIRMED, possibly CANCELLED
- All should have HTF alignment
- Confirmed signals should show bars_to_confirmation

### 7. Verify Reconciliation Working
```bash
python test_signal_created_reconciliation.py
```

**Expected:**
```
Signals with gaps fillable from SIGNAL_CREATED: 0
(or low number if any gaps remain)
```

---

## 🚨 Troubleshooting

### No SIGNAL_CREATED Events in Database

**Check 1:** TradingView Alert
- Is alert enabled?
- Did it fire? (check alert log)
- Is webhook URL correct?

**Check 2:** Railway Logs
```
https://railway.app/project/[project-id]/logs
```
Search for: "SIGNAL_CREATED"

**Check 3:** Manual Webhook Test
```bash
curl -X POST https://web-production-f8c3.up.railway.app/api/automated-signals/webhook \
  -H "Content-Type: application/json" \
  -d '{"event_type":"SIGNAL_CREATED","trade_id":"TEST_123","direction":"Bullish","session":"NY AM","signal_date":"2025-12-16","signal_time":"09:30:00","htf_alignment":{"daily":"Bullish"},"event_timestamp":"2025-12-16T09:30:00"}'
```

Then check database:
```bash
python check_signal_created_detailed.py
```

### All Signals Tab Empty

**Check 1:** Database has SIGNAL_CREATED?
```bash
python check_signal_created_detailed.py
```

**Check 2:** API Working?
```bash
curl https://web-production-f8c3.up.railway.app/api/automated-signals/all-signals
```

**Check 3:** Frontend Console
- Open browser console (F12)
- Look for JavaScript errors
- Check network tab for API calls

### Gaps Not Reducing

**Check 1:** Hybrid Sync Service Running?
```
Check Railway logs for "HYBRID SYNC CYCLE"
Should see entries every 2 minutes
```

**Check 2:** Reconciliation Errors?
```
Check Railway logs for "reconciliation" and "error"
```

**Check 3:** Run Manual Reconciliation
```bash
python test_signal_created_reconciliation.py
```

---

## 📊 Success Metrics

### Immediate (First Signal)
- [ ] SIGNAL_CREATED event in database
- [ ] All Signals tab shows signal
- [ ] No errors in Railway logs

### After 1 Hour
- [ ] 10+ SIGNAL_CREATED events
- [ ] All Signals tab populated
- [ ] Gaps reduced to ~7
- [ ] Health score 90+

### After 4 Hours
- [ ] 40+ SIGNAL_CREATED events
- [ ] All confirmed signals have complete data
- [ ] Health score stable at 90+
- [ ] No manual intervention needed

---

## 📞 Quick Commands

### Check SIGNAL_CREATED Count
```bash
python -c "import psycopg2; import os; from dotenv import load_dotenv; load_dotenv(); conn = psycopg2.connect(os.getenv('DATABASE_URL')); cur = conn.cursor(); cur.execute('SELECT COUNT(*) FROM automated_signals WHERE event_type = \\'SIGNAL_CREATED\\''); print(f'Count: {cur.fetchone()[0]}'); cur.close(); conn.close()"
```

### Check System Health
```bash
python test_hybrid_sync_status.py
```

### Check All Signals API
```bash
curl https://web-production-f8c3.up.railway.app/api/automated-signals/all-signals | python -m json.tool
```

### View Railway Logs
```
https://railway.app/project/[your-project-id]/logs
```

---

## 🎯 Expected Timeline

**9:30 AM** - Market opens, first triangle appears  
**9:31 AM** - SIGNAL_CREATED in database  
**9:32 AM** - All Signals tab shows first signal  
**10:30 AM** - 10+ signals collected  
**10:31 AM** - Run gap detection, verify improvement  
**1:00 PM** - Health score stable at 90+  
**4:00 PM** - Market closes, system proven

---

**The system is ready. See you Monday morning!** 🚀
