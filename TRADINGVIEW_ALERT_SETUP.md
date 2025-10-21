# TradingView Alert Configuration Guide

## Problem: Only Bullish Signals Received

### Root Cause
Most likely: **Single alert configured for bullish only** OR **Alert condition doesn't trigger for bearish**

## ✅ Correct Setup (Two Separate Alerts)

### Alert 1: Bullish Signals
**Condition:** `bias crosses over 0.5` (or your bullish condition)
**Alert Name:** `NQ Bullish Signal`
**Webhook URL:** `https://your-app.railway.app/api/live-signals`
**Message:**
```
SIGNAL:Bullish:{{close}}:75:ALIGNED:ALIGNED:{{time}}
```

### Alert 2: Bearish Signals  
**Condition:** `bias crosses under 0.5` (or your bearish condition)
**Alert Name:** `NQ Bearish Signal`
**Webhook URL:** `https://your-app.railway.app/api/live-signals`
**Message:**
```
SIGNAL:Bearish:{{close}}:75:ALIGNED:ALIGNED:{{time}}
```

## 🔍 Quick Diagnostic

### Check Your Current Alert
1. Open TradingView
2. Click Alert icon (clock)
3. Check how many alerts you have for this chart
4. **If only 1 alert exists** → That's the problem!

### Verify Alert Triggers
Look at alert condition:
- ❌ `bias == 1` → Only triggers for bullish
- ❌ `bias > 0` → Only triggers for bullish  
- ✅ `bias crosses over 0.5` → Triggers when going bullish
- ✅ `bias crosses under 0.5` → Triggers when going bearish

## 📝 Step-by-Step Setup

### Step 1: Create Bullish Alert
1. Right-click chart → Add Alert
2. **Condition:** Your indicator crosses over threshold
3. **Options:** Once Per Bar Close
4. **Alert actions:** ✅ Webhook URL
5. **Webhook URL:** `https://your-app.railway.app/api/live-signals`
6. **Message:** `SIGNAL:Bullish:{{close}}:75:ALIGNED:ALIGNED:{{time}}`
7. Click **Create**

### Step 2: Create Bearish Alert
1. Right-click chart → Add Alert (again)
2. **Condition:** Your indicator crosses under threshold
3. **Options:** Once Per Bar Close
4. **Alert actions:** ✅ Webhook URL
5. **Webhook URL:** `https://your-app.railway.app/api/live-signals`
6. **Message:** `SIGNAL:Bearish:{{close}}:75:ALIGNED:ALIGNED:{{time}}`
7. Click **Create**

### Step 3: Verify Both Alerts Exist
Check alert list - you should see:
- ✅ NQ Bullish Signal
- ✅ NQ Bearish Signal

## 🧪 Test Your Alerts

### Test 1: Manual Trigger
1. In TradingView, click alert → "..." → Test
2. Check webhook monitor dashboard
3. Should see signal appear immediately

### Test 2: Historical Replay
1. Use TradingView replay feature
2. Play through historical data
3. Verify both alert types trigger

### Test 3: Webhook Direct Test
```bash
# Test your webhook URL works
curl -X POST https://your-app.railway.app/api/live-signals \
  -d "SIGNAL:Bearish:20500:75:ALIGNED:ALIGNED:2024-01-15T10:00:00"
```

## 🎯 Alert Message Format

### Simple Format (Recommended)
```
SIGNAL:{{plot("bias")}}:{{close}}:75:ALIGNED:ALIGNED:{{time}}
```

This works if your indicator plots "Bullish" or "Bearish" directly.

### Conditional Format
```
SIGNAL:{{plot("bias") > 0.5 ? "Bullish" : "Bearish"}}:{{close}}:75:ALIGNED:ALIGNED:{{time}}
```

### JSON Format (Alternative)
```json
{"bias":"{{plot("bias") > 0.5 ? "Bullish" : "Bearish"}}","price":{{close}},"symbol":"{{ticker}}"}
```

## ⚠️ Common Mistakes

### Mistake 1: Single Alert with Condition
❌ **Wrong:**
- Condition: `bias != 0`
- Message: `SIGNAL:{{plot("bias")}}:...`

**Problem:** Alert only triggers once when bias changes, not for each direction.

✅ **Correct:** Two separate alerts with specific cross conditions.

### Mistake 2: Wrong Condition Logic
❌ **Wrong:**
- Bullish: `bias == 1`
- Bearish: `bias == -1`

**Problem:** Misses signals if bias uses different values.

✅ **Correct:**
- Bullish: `bias crosses over 0.5`
- Bearish: `bias crosses under 0.5`

### Mistake 3: Same Alert Name
❌ **Wrong:** Both alerts named "NQ Signal"

**Problem:** Can't distinguish which is which.

✅ **Correct:** 
- "NQ Bullish Signal"
- "NQ Bearish Signal"

## 🔧 Troubleshooting

### Issue: Alert Created But Not Triggering

**Check:**
1. Alert is active (not paused)
2. Condition actually occurs in market
3. "Once Per Bar Close" is selected
4. Chart timeframe matches alert timeframe

### Issue: Alert Triggers But Webhook Not Received

**Check:**
1. Webhook URL is correct (no typos)
2. URL starts with `https://`
3. Test webhook with curl command
4. Check Railway logs for incoming requests

### Issue: Webhook Received But Wrong Bias

**Check:**
1. Alert message format
2. `{{plot("bias")}}` returns correct value
3. Server parsing logic matches format

## 📊 Validation Checklist

- [ ] Two separate alerts created (bullish + bearish)
- [ ] Both alerts have identical webhook URLs
- [ ] Alert conditions use "crosses over/under"
- [ ] Alert messages include bias identifier
- [ ] Both alerts set to "Once Per Bar Close"
- [ ] Alerts are active (not paused)
- [ ] Webhook URL tested with curl
- [ ] Both test signals appear in webhook monitor
- [ ] Historical replay triggers both alerts

## 🎓 Pine Script Example

If you're writing the indicator:

```pinescript
//@version=5
indicator("Bias Detector", overlay=true)

// Your bias calculation
bias = close > sma(close, 20) ? 1 : -1

// Plot for alert reference
plot(bias, "Bias", display=display.none)

// Visual markers
plotshape(ta.crossover(bias, 0), "Bullish", shape.triangleup, location.belowbar, color.green, size=size.small)
plotshape(ta.crossunder(bias, 0), "Bearish", shape.triangledown, location.abovebar, color.red, size=size.small)

// Alert conditions
alertcondition(ta.crossover(bias, 0), "Bullish Signal", "Bullish")
alertcondition(ta.crossunder(bias, 0), "Bearish Signal", "Bearish")
```

Then create alerts using these conditions.

## 🚀 Quick Fix

**If you only have 1 alert:**

1. Delete existing alert
2. Create TWO new alerts:
   - One for bullish (crosses over)
   - One for bearish (crosses under)
3. Both with same webhook URL
4. Test both with replay feature

## 📞 Support

After setup, verify in webhook monitor:
- Go to: `https://your-app.railway.app/webhook-monitor`
- Should see both Bullish and Bearish counts increasing
- Last received timestamps should be recent for both

**Still having issues?**
Check `/api/webhook-diagnostic` to see exact signal breakdown.
