# TradingView Alert Setup Guide

## 🚨 CRITICAL: Alerts Must Be Configured in TradingView

**The indicator code fires `alert()` calls, but TradingView needs you to CREATE AN ALERT that sends these to your webhook URL.**

---

## 📋 STEP-BY-STEP SETUP

### **Step 1: Add Indicator to Chart**
1. Open TradingView
2. Add "Complete Automated Trading System - FVG" indicator to chart
3. Verify triangles and MFE labels appear

### **Step 2: Create Alert**
1. Click the **Alert** button (clock icon) in TradingView
2. Click **"Create Alert"**

### **Step 3: Configure Alert Settings**

**Condition:**
- Select: **"Complete Automated Trading System - FVG"**
- Choose: **"alert() function calls only"**

**Alert Name:**
- Name it: `Automated Signals Webhook`

**Message:**
- Leave as: `{{strategy.order.alert_message}}`
- This will use the JSON payload from the indicator

**Webhook URL:**
```
https://web-production-cd33.up.railway.app/api/automated-signals/webhook
```

**Settings:**
- ✅ Check "Webhook URL"
- ✅ Paste the URL above
- ⚠️ **CRITICAL:** Set "Once Per Bar Close" (NOT "Once Per Bar")
- ✅ Check "Open-ended alert" (runs forever)

### **Step 4: Save Alert**
Click **"Create"** button

---

## ✅ VERIFICATION

### **After Creating Alert:**

1. **Wait for next signal** (blue/red triangle)
2. **Check TradingView Alert Log:**
   - Should see alert fire with JSON payload
   - Should show `"type":"ENTRY"` in the message

3. **Check Dashboard:**
   - Go to: `https://web-production-cd33.up.railway.app/automated-signals-dashboard`
   - Should see the signal appear in "Active Trades"

4. **Check for MFE Updates:**
   - Every bar (every minute on 1m chart)
   - TradingView alert log should show `"type":"MFE_UPDATE"`
   - Dashboard should update MFE values in real-time

---

## 🔍 TROUBLESHOOTING

### **Issue: No alerts firing at all**
**Solution:** Make sure alert is created and active (green dot in alert list)

### **Issue: Alerts firing but dashboard not updating**
**Check:**
1. Webhook URL is correct (copy/paste from above)
2. Alert is set to "alert() function calls only"
3. Message is `{{strategy.order.alert_message}}`
4. Railway backend is running (check Railway dashboard)

### **Issue: Only ENTRY alerts, no MFE_UPDATE**
**Check:**
1. Alert is set to "Once Per Bar Close" (not "Once Per Bar")
2. Indicator has active trades (check MFE labels on chart)
3. `active_signal_ids` array is being populated (indicator logic issue)

### **Issue: No EXIT alerts when trades close**
**Check:**
1. Trade actually hit stop loss (check chart)
2. EXIT webhook logic is correct in indicator
3. `active_signal_ids` array contains the signal

---

## 📊 EXPECTED ALERT FLOW

**For each trade:**

1. **ENTRY Alert** - When signal confirmed
   ```json
   {"type":"ENTRY","signal_id":"20251114_120000_BULLISH",...}
   ```

2. **MFE_UPDATE Alerts** - Every bar while active
   ```json
   {"type":"MFE_UPDATE","signal_id":"20251114_120000_BULLISH","be_mfe":0.5,...}
   ```

3. **BE_TRIGGERED Alert** - When +1R achieved (if enabled)
   ```json
   {"type":"BE_TRIGGERED","signal_id":"20251114_120000_BULLISH",...}
   ```

4. **EXIT Alert** - When stopped out
   ```json
   {"type":"EXIT_STOP_LOSS","signal_id":"20251114_120000_BULLISH",...}
   ```

---

## ⚠️ COMMON MISTAKES

1. ❌ **Not creating the alert** - Indicator alone doesn't send webhooks!
2. ❌ **Wrong webhook URL** - Must be exact URL above
3. ❌ **Wrong message format** - Must be `{{strategy.order.alert_message}}`
4. ❌ **"Once Per Bar" instead of "Once Per Bar Close"** - Causes duplicate alerts
5. ❌ **Alert not set to "Open-ended"** - Will stop after X bars

---

## 🎯 QUICK CHECK

**Is your alert configured correctly?**

- [ ] Alert created in TradingView
- [ ] Condition: "alert() function calls only"
- [ ] Message: `{{strategy.order.alert_message}}`
- [ ] Webhook URL: `https://web-production-cd33.up.railway.app/api/automated-signals/webhook`
- [ ] Frequency: "Once Per Bar Close"
- [ ] Duration: "Open-ended alert"
- [ ] Alert is active (green dot)

**If all checked, alerts should work!**

---

**Without the TradingView alert configured, the indicator will show alerts in the log but they won't reach your backend!**
