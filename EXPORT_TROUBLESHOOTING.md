# 🔧 EXPORT TROUBLESHOOTING GUIDE

**Issue:** Export not working or can't see progress

---

## 🎯 QUICK DIAGNOSIS

Run these commands in order:

### 1. Check if backend is ready
```bash
python check_export_status.py
```

**Expected:** ✅ Webhook endpoint is working

### 2. Check if export is running (even if invisible)
```bash
python check_if_export_running.py
```

**Expected:** Either "Export is running!" or "No new signals received"

---

## ❌ PROBLEM: CAN'T SEE EXPORT PROGRESS

**Cause:** Export progress only shows when Position Sizing Table is enabled

**Solution:** Enable Position Sizing Table temporarily

### Steps:
1. Open TradingView indicator settings
2. Find "Display" section
3. Check ✅ "Show Position Sizing Table"
4. Click "OK"
5. Look for position table on chart (bottom right by default)
6. Export progress should show at bottom of table

**After export completes:**
- Uncheck "Show Position Sizing Table" to restore performance

---

## ❌ PROBLEM: EXPORT NOT STARTING

### Checklist:

#### 1. Verify ENABLE_EXPORT is checked
```
Indicator Settings → Export section
✅ Enable Bulk Export (must be checked)
Delay Between Batches = 0
Click OK to apply
```

#### 2. Verify alert exists and is active
```
TradingView → Alerts tab
Should see: "Indicator Export" (or similar name)
Status: Active (green)
```

#### 3. Verify alert configuration
```
Condition: NQ_FVG_CORE_TELEMETRY_V1
Message: {{strategy.order.alert_message}}
Webhook URL: https://web-production-f8c3.up.railway.app/api/indicator-inspector/receive
Frequency: Once Per Bar Close
```

#### 4. Verify chart is live
```
Chart is open in TradingView
Indicator is loaded on chart
Bars are closing (1m chart = 1 bar per minute)
Chart is receiving live data (not replay mode)
```

---

## ❌ PROBLEM: EXPORT ALREADY COMPLETED

**Symptom:** Export ran once but won't run again

**Cause:** `export_complete` flag is set to true

**Solution:** Reset export state

### Option 1: Change ARRAY_VERSION
```
Indicator Settings → Debug section
Array Version = 2 (or any different number)
Click OK
This resets all arrays including export state
```

### Option 2: Reload indicator
```
Remove indicator from chart
Re-add indicator to chart
Configure export settings again
```

---

## ❌ PROBLEM: ALERT NOT FIRING

### Diagnosis:

#### 1. Check alert status
```
TradingView → Alerts tab
Alert should be "Active" (green)
If "Paused" (yellow), click to resume
If "Expired" (red), recreate alert
```

#### 2. Test alert manually
```
Right-click alert → Test
Should see notification
Check Railway logs for webhook reception
```

#### 3. Verify webhook URL
```
Alert settings → Webhook URL
Must be EXACTLY:
https://web-production-f8c3.up.railway.app/api/indicator-inspector/receive

Common mistakes:
- Missing /api/
- Wrong endpoint name
- Extra spaces
- HTTP instead of HTTPS
```

---

## ❌ PROBLEM: SIGNALS NOT REACHING BACKEND

### Diagnosis:

#### 1. Check Railway logs
```
Railway dashboard → Logs
Look for: "INDICATOR_EXPORT"
Should see batch reception messages
```

#### 2. Test webhook directly
```bash
python check_export_status.py
```

Look for: "✅ Webhook endpoint is working!"

#### 3. Check alert message format
```
Alert message MUST be:
{{strategy.order.alert_message}}

NOT:
- {{strategy.order.alert_message
- strategy.order.alert_message}}
- Any other variation
```

---

## ❌ PROBLEM: EXPORT STUCK/FROZEN

### Symptoms:
- Progress shows same batch number
- No new signals arriving
- Export not completing

### Solutions:

#### 1. Check if chart is frozen
```
Verify bars are closing
Check chart connection status
Refresh chart if needed
```

#### 2. Check delay setting
```
Indicator Settings → Export
Delay Between Batches = 0 (for immediate export)
If set to 5, export waits 5 bars between batches
```

#### 3. Reset export
```
Disable ENABLE_EXPORT
Wait 1 bar
Enable ENABLE_EXPORT
Export should restart
```

---

## ✅ VERIFICATION STEPS

### After fixing issues:

#### 1. Verify export is running
```bash
python check_if_export_running.py
```

Should see: "✅ EXPORT IS RUNNING!"

#### 2. Monitor progress
```
Enable Position Sizing Table
Watch export progress update each bar
Should see: Batch X/107 incrementing
```

#### 3. Check backend reception
```bash
python check_export_status.py
```

Should see increasing signal count

#### 4. Wait for completion
```
Export completes when:
- Progress shows: ✅ COMPLETE
- Signals: 2124/2124
- All 107 batches sent
```

---

## 🎯 MOST COMMON ISSUES

### 1. Can't see progress (90% of issues)
**Fix:** Enable Position Sizing Table

### 2. ENABLE_EXPORT not checked
**Fix:** Check the checkbox and click OK

### 3. Alert not configured
**Fix:** Create alert with correct webhook URL

### 4. Wrong webhook URL
**Fix:** Use exact URL from guide

### 5. Chart not live
**Fix:** Ensure chart is open and receiving data

---

## 📞 STILL NOT WORKING?

### Run full diagnostic:
```bash
python check_export_status.py
python check_if_export_running.py
```

### Check these files:
- `EXPORT_FIX_NEEDED.md` - Display issue details
- `EXPORT_QUICK_REFERENCE.md` - Quick reference
- `INDICATOR_EXPORT_SETUP_GUIDE.md` - Full setup guide

### Manual verification:
1. Open indicator settings
2. Verify Export section exists
3. Verify ENABLE_EXPORT checkbox exists
4. Verify it's checked
5. Verify Delay = 0
6. Click OK
7. Enable Position Sizing Table
8. Look for export progress

---

**Most issues are simple: Either ENABLE_EXPORT isn't checked, or you can't see the progress because Position Sizing Table is disabled!** 🔧
