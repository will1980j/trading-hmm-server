# ✅ EXPORT NOT WORKING? - SIMPLE CHECKLIST

**Follow these steps in order. Stop when export starts working.**

---

## STEP 1: Enable Position Sizing Table (SEE PROGRESS)

**Why:** Export progress only shows when this is enabled

```
TradingView → Indicator Settings → Display
✅ Show Position Sizing Table
Click OK
```

**Look for:** Position table appears on chart (bottom right)

---

## STEP 2: Verify ENABLE_EXPORT is Checked

```
TradingView → Indicator Settings → Export
✅ Enable Bulk Export (MUST BE CHECKED)
Delay Between Batches = 0
Click OK
```

**Look for:** Export progress in position table

---

## STEP 3: Verify Alert Exists

```
TradingView → Alerts tab (bell icon)
Should see: "Indicator Export" or similar
Status: Active (green)
```

**If missing:** Create alert (see EXPORT_QUICK_REFERENCE.md)

---

## STEP 4: Verify Alert Configuration

```
Click alert → Edit
Condition: NQ_FVG_CORE_TELEMETRY_V1
Message: {{strategy.order.alert_message}}
Webhook: https://web-production-f8c3.up.railway.app/api/indicator-inspector/receive
Frequency: Once Per Bar Close
```

**Fix any mismatches**

---

## STEP 5: Verify Chart is Live

```
✅ Chart is open
✅ Indicator is loaded
✅ Bars are closing (watch time)
✅ Not in replay mode
```

---

## STEP 6: Wait for Bar Close

**Export only sends on bar close**

```
1m chart = 1 bar per minute
Wait for next bar to close
Check position table for progress update
```

---

## STEP 7: Check if Running (Even if Invisible)

```bash
python check_if_export_running.py
```

**This monitors backend for 30 seconds**

---

## STEP 8: Reset if Needed

**If export already ran once:**

```
Indicator Settings → Debug
Array Version = 2 (change number)
Click OK
This resets export state
```

---

## 🎯 QUICK TEST

**Run this to verify backend is ready:**

```bash
python check_export_status.py
```

**Should see:** ✅ Webhook endpoint is working!

---

## 📊 WHAT SUCCESS LOOKS LIKE

**In Position Table:**
```
📤 EXPORT: Batch 1/107 (20/2124 signals)
```

**Updates each bar:**
```
📤 EXPORT: Batch 2/107 (40/2124 signals)
📤 EXPORT: Batch 3/107 (60/2124 signals)
...
```

**When complete:**
```
📤 EXPORT: ✅ COMPLETE (2124/2124 signals)
```

---

## 🚨 MOST COMMON MISTAKE

**You enabled ENABLE_EXPORT but can't see progress because Position Sizing Table is disabled!**

**Solution:** Enable Position Sizing Table (Step 1)

---

**Still stuck? Read EXPORT_TROUBLESHOOTING.md for detailed diagnosis** 🔧
