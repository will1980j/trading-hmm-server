# DEPLOY SYSTEM HEALTH MONITOR TO RAILWAY

## Files Created (Ready for GitHub Commit):

### 1. Backend API
- **`system_health_api.py`** - Health check API with 5 component checks

### 2. Dashboard Integration  
- **`templates/automated_signals_dashboard.html`** - Updated with health monitor UI

### 3. Web Server Integration
- **`web_server.py`** - Needs manual integration (see below)

## DEPLOYMENT STEPS:

### Step 1: Integrate Health API into web_server.py

Open `web_server.py` and add these two lines:

**At the top with other imports (around line 10-20):**
```python
from system_health_api import register_system_health_api
```

**After `register_automated_signals_api(app, db)` call (search for this line):**
```python
register_system_health_api(app, db)
```

### Step 2: Update Dashboard HTML

Run this Python script locally to inject the health monitor into the dashboard:

```python
python deploy_system_health_monitor.py
```

This will update `templates/automated_signals_dashboard.html` with the health monitor UI.

### Step 3: Commit to GitHub

**Using GitHub Desktop:**

1. Open GitHub Desktop
2. You should see these changed files:
   - `system_health_api.py` (new file)
   - `web_server.py` (modified - health API integration)
   - `templates/automated_signals_dashboard.html` (modified - health monitor UI)
   - `complete_automated_trading_system.pine` (modified - MFE fix)

3. **Commit Message:**
   ```
   Add System Health Monitor + Fix Indicator MFE Tracking
   
   - Add comprehensive system health monitoring API
   - Add compact health status bar to dashboard
   - Fix indicator to track MFE for all active trades
   - Remove sig_is_realtime and entry_sent restrictions
   ```

4. Click "Commit to main"
5. Click "Push origin"

### Step 4: Wait for Railway Deployment

Railway will automatically:
1. Detect the push to main branch
2. Build the new version (2-3 minutes)
3. Deploy to production
4. Restart the Flask app

**Monitor deployment:**
- Go to Railway dashboard
- Watch the deployment logs
- Wait for "Deployment successful" message

### Step 5: Verify on Production

Once deployed, visit:
```
https://web-production-cd33.up.railway.app/automated-signals-dashboard
```

You should see:
- ✅ Compact health status bar at the top
- ✅ 5 component badges (Database, Webhooks, Events, Data, API)
- ✅ Animated pulse indicator
- ✅ Click "Details" to expand full diagnostics
- ✅ Auto-refresh every 60 seconds

### Step 6: Update TradingView Indicator

1. Open TradingView
2. Open the chart with your indicator
3. Click indicator name → "Edit" (or Ctrl+E)
4. Replace ALL code with updated `complete_automated_trading_system.pine`
5. Click "Save" → "Add to Chart"
6. Verify alert is still active and configured correctly

## WHAT THE HEALTH MONITOR CHECKS:

### 1. Database Health
- ✅ PostgreSQL connection active
- ✅ Table `automated_signals` exists
- ✅ Required columns present (be_mfe, no_be_mfe, signal_date, signal_time)
- ✅ Query performance < 2 seconds
- ✅ Row count

### 2. Webhook Health
- ✅ Last webhook received (< 5 minutes = healthy)
- ✅ Webhooks received in last hour
- ✅ Event type breakdown (ENTRY, MFE_UPDATE, BE_TRIGGERED, EXIT)
- ⚠️ Warning if no webhooks for 5+ minutes
- ❌ Critical if no webhooks for 10+ minutes

### 3. Event Flow Health
- ✅ Active trades count
- ✅ Trades with MFE updates
- ✅ MFE coverage percentage
- ✅ Completed trades today
- ⚠️ Warning if MFE coverage < 80%

### 4. Data Freshness
- ✅ Last MFE update timestamp
- ✅ Last ENTRY timestamp
- ⚠️ Warning if MFE updates > 2 minutes old

### 5. API Performance
- ✅ Dashboard API response time
- ✅ HTTP status code
- ⚠️ Warning if response time > 2 seconds
- ❌ Critical if API returns errors

## VISUAL DESIGN:

**Compact Status Bar** (60px height):
```
[●] SYSTEM STATUS  |  [●] Database 234ms  [●] Webhooks 45s ago  [●] Events 92% MFE  [●] Data 1m old  [●] API 412ms  |  [Details] [Refresh]
```

**Expandable Details** (slides down when clicked):
```
┌─────────────────────────────────────────────────────────────┐
│ DATABASE          │ WEBHOOKS         │ EVENT FLOW          │
│ Status: Healthy   │ Status: Healthy  │ Status: Warning     │
│ Connected: Yes    │ Last: 45s ago    │ Active: 13 trades   │
│ Query: 234ms      │ Hour: 156        │ With MFE: 12        │
│ Rows: 1,234       │ ENTRY: 13        │ Coverage: 92%       │
│                   │ MFE_UPDATE: 128  │ Completed: 49       │
└─────────────────────────────────────────────────────────────┘
```

## TROUBLESHOOTING:

### If health monitor doesn't appear:
1. Check Railway deployment logs for errors
2. Verify `system_health_api.py` was deployed
3. Check browser console for JavaScript errors
4. Hard refresh browser (Ctrl+Shift+R)

### If health checks show critical:
1. Click "Details" to see specific issues
2. Check Railway logs for backend errors
3. Verify database connection in Railway dashboard
4. Check TradingView alert is active

### If MFE values still show "-":
1. Wait 1-2 minutes after indicator update
2. Check TradingView alert log for MFE_UPDATE events
3. Verify indicator was saved and reloaded
4. Check Railway logs for incoming webhooks

## DEPLOYMENT TIMELINE:

- **Commit to GitHub:** 30 seconds
- **Railway Build:** 2-3 minutes
- **Railway Deploy:** 30 seconds
- **Total:** ~3-4 minutes from commit to live

## SUCCESS CRITERIA:

✅ Health monitor visible at top of dashboard
✅ All 5 components showing status
✅ Pulse indicator animating
✅ Details expand/collapse working
✅ Auto-refresh every 60 seconds
✅ MFE values updating for all active trades
✅ No JavaScript errors in browser console

---

**Ready to deploy? Follow Steps 1-6 above!**
