# TradingView Alert Quick Fix

## 🚨 Problem: Only Bullish Signals Received

### ✅ Solution: Create TWO Alerts

You need **2 separate alerts** in TradingView, not 1.

---

## 📋 Alert 1: Bullish

**Name:** `NQ Bullish Signal`

**Condition:** 
```
bias crosses over 0.5
```

**Webhook URL:**
```
https://your-app.railway.app/api/live-signals
```

**Message:**
```
SIGNAL:Bullish:{{close}}:75:ALIGNED:ALIGNED:{{time}}
```

**Options:**
- Trigger: Once Per Bar Close
- Expiration: Open-ended

---

## 📋 Alert 2: Bearish

**Name:** `NQ Bearish Signal`

**Condition:**
```
bias crosses under 0.5
```

**Webhook URL:**
```
https://your-app.railway.app/api/live-signals
```

**Message:**
```
SIGNAL:Bearish:{{close}}:75:ALIGNED:ALIGNED:{{time}}
```

**Options:**
- Trigger: Once Per Bar Close
- Expiration: Open-ended

---

## ✅ Verification

After creating both alerts:

1. **Check TradingView Alert List**
   - Should see 2 alerts
   - Both should be active (not paused)

2. **Test Webhook**
   ```bash
   curl -X POST https://your-app.railway.app/api/live-signals \
     -d "SIGNAL:Bearish:20500:75:ALIGNED:ALIGNED:2024-01-15T10:00:00"
   ```

3. **Check Webhook Monitor**
   - Go to: `https://your-app.railway.app/webhook-monitor`
   - Click "Test Bearish Signal"
   - Should see count increase

4. **Wait for Real Signals**
   - Monitor for 1 hour
   - Both Bullish and Bearish counts should increase

---

## 🔍 Common Mistakes

❌ **Only 1 alert with condition `bias != 0`**
- This only triggers once per change, not per direction

❌ **Alert message doesn't specify bias**
- Server can't tell if signal is bullish or bearish

❌ **Different webhook URLs**
- Both alerts must use same URL

❌ **Alert paused or expired**
- Check alert is active

---

## 📞 Still Not Working?

1. Check `/api/webhook-diagnostic`
2. Review TradingView alert history
3. Verify indicator actually plots both bias values
4. Test with historical replay in TradingView

---

## 🎯 Expected Result

**Webhook Monitor should show:**
- Bullish Received: 45
- Bearish Received: 38
- Last Bullish: 2 minutes ago
- Last Bearish: 5 minutes ago

Both counts should increase over time.
