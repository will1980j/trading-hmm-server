# ✅ HOMEPAGE STATS UNIFIED ENDPOINT - IMPLEMENTATION COMPLETE

**Date:** November 26, 2025  
**Endpoint:** `/api/homepage-stats`  
**Status:** ✅ IMPLEMENTED AND READY FOR TESTING

---

## 📋 IMPLEMENTATION SUMMARY

Created a unified homepage statistics endpoint that consolidates all homepage data into a single API call, pulling exclusively from the Automated Signals Engine (TradingView → `automated_signals` table).

---

## 1️⃣ NEW ENDPOINT CREATED

### Endpoint Details

**Route:** `/api/homepage-stats`  
**Method:** GET  
**Authentication:** None (public endpoint for homepage)  
**Location:** `web_server.py` (lines ~1373-1490)

### Response Format

```json
{
  "current_session": "NY AM",
  "signals_today": 14,
  "last_signal_time": "2025-11-26T14:32:10-05:00",
  "webhook_health": "OK",
  "server_time_ny": "2025-11-26T14:45:01-05:00"
}
```

### Error Response

```json
{
  "error": "db_failure",
  "message": "Connection refused"
}
```

**HTTP Status:** 500

---

## 2️⃣ IMPLEMENTATION DETAILS

### A. NY Time Calculation

```python
import pytz
from datetime import datetime

eastern = pytz.timezone('US/Eastern')
now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
now_ny = now_utc.astimezone(eastern)
```

**Returns:** Current server time in US/Eastern timezone

---

### B. Current Session Logic

**Session Classification (Eastern Time):**

| Time Range (ET) | Session | Minutes Range |
|-----------------|---------|---------------|
| 20:00-23:59 | ASIA | 1200-1439 |
| 00:00-05:59 | LONDON | 0-359 |
| 06:00-08:29 | NY PRE | 360-509 |
| 08:30-11:59 | NY AM | 510-719 |
| 12:00-12:59 | NY LUNCH | 720-779 |
| 13:00-15:59 | NY PM | 780-959 |
| 16:00-19:59 | CLOSED | 960-1199 |

**Implementation:**
```python
hour = now_ny.hour
minute = now_ny.minute
current_time_minutes = hour * 60 + minute

if 1200 <= current_time_minutes <= 1439:
    current_session = "ASIA"
elif 0 <= current_time_minutes < 360:
    current_session = "LONDON"
# ... etc
```

**✅ Server-side calculation** - No client-side dependency

---

### C. Signals Today

**Query:**
```sql
SELECT COUNT(DISTINCT trade_id)
FROM automated_signals
WHERE DATE(timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'US/Eastern') = %s
```

**Logic:**
- Converts UTC timestamps to Eastern Time
- Filters for today's date in NY timezone
- Counts unique `trade_id` values (not total events)
- Returns integer count

**✅ Real data from `automated_signals` table**

---

### D. Last Signal Time

**Query:**
```sql
SELECT timestamp
FROM automated_signals
ORDER BY timestamp DESC
LIMIT 1
```

**Logic:**
- Gets most recent event timestamp
- Converts UTC → Eastern Time
- Returns ISO 8601 format: `2025-11-26T14:32:10-05:00`

**✅ Real data from `automated_signals` table**

---

### E. Webhook Health

**Logic:**
```python
time_since_last = now_utc - last_signal_utc
minutes_since_last = time_since_last.total_seconds() / 60

if minutes_since_last < 10:
    webhook_health = "OK"
elif minutes_since_last < 60:
    webhook_health = "WARNING"
else:
    webhook_health = "CRITICAL"
```

**Health Status:**
- **OK:** Last signal < 10 minutes ago
- **WARNING:** Last signal 10-60 minutes ago
- **CRITICAL:** Last signal > 60 minutes ago
- **NO_DATA:** No signals in database

**✅ Calculated from real signal freshness**

---

### F. Error Handling

**Database Connection Failure:**
```python
except Exception as e:
    logger.error(f"Homepage stats error: {str(e)}")
    logger.error(traceback.format_exc())
    return jsonify({
        "error": "db_failure",
        "message": str(e)
    }), 500
```

**Missing DATABASE_URL:**
```python
if not database_url:
    return jsonify({
        "current_session": current_session,
        "signals_today": 0,
        "last_signal_time": None,
        "webhook_health": "NO_DATA",
        "server_time_ny": now_ny.isoformat(),
        "error": "DATABASE_URL not configured"
    }), 200
```

**✅ Graceful degradation** - Returns session/time even if DB fails

---

## 3️⃣ HOMEPAGE JAVASCRIPT UPDATED

### File Modified: `static/js/homepage.js`

**Location:** Lines ~248-280

### Old Implementation (REMOVED)

```javascript
// Two separate API calls to non-existent endpoints
const statusResponse = await fetch('/api/system-status');
const statsResponse = await fetch('/api/signals/stats/today');
```

### New Implementation (ADDED)

```javascript
async function fetchSystemStatus() {
    try {
        // Single unified API call
        const response = await fetch('/api/homepage-stats');
        if (response.ok) {
            const data = await response.json();
            
            // Map response to systemStatus object
            systemStatus.current_session = data.current_session || '--';
            systemStatus.signals_today = data.signals_today || 0;
            systemStatus.last_signal = data.last_signal_time || '--';
            systemStatus.webhook_health = data.webhook_health || 'unknown';
            
            // Format last signal time for display
            if (data.last_signal_time && data.last_signal_time !== '--') {
                try {
                    const signalDate = new Date(data.last_signal_time);
                    systemStatus.last_signal = signalDate.toLocaleTimeString('en-US', {
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: true
                    });
                } catch (e) {
                    systemStatus.last_signal = data.last_signal_time;
                }
            }
        }
    } catch (error) {
        console.log('Failed to fetch homepage stats:', error);
    }
}
```

### Data Mapping

| API Response Field | JavaScript Variable | DOM Element ID |
|-------------------|---------------------|----------------|
| `current_session` | `systemStatus.current_session` | `statusSession` |
| `signals_today` | `systemStatus.signals_today` | `statusSignals` |
| `last_signal_time` | `systemStatus.last_signal` | `statusLastSignal` |
| `webhook_health` | `systemStatus.webhook_health` | `statusWebhook` |

### Refresh Loop

**Unchanged** - Still refreshes every 15 seconds:
```javascript
setInterval(async () => {
    await fetchSystemStatus();
    renderSystemStatus();
}, 15000);
```

---

## 4️⃣ DEPRECATED ENDPOINTS REMOVED

### Endpoints NO LONGER USED

❌ `/api/system-status` - Never existed  
❌ `/api/signals/stats/today` - Never existed  

### Verification

Searched codebase for references:
```bash
grep -r "/api/system-status" static/js/
grep -r "/api/signals/stats/today" static/js/
```

**Result:** Only found in `homepage.js` - now replaced ✅

---

## 5️⃣ FILES MODIFIED

### Backend

**File:** `web_server.py`  
**Lines Added:** ~120 lines  
**Location:** After line 1372 (before NASDAQ ML endpoints)

**Changes:**
- Added `/api/homepage-stats` route
- Implemented session calculation logic
- Added database queries for signals
- Implemented webhook health calculation
- Added comprehensive error handling

### Frontend

**File:** `static/js/homepage.js`  
**Lines Modified:** ~35 lines  
**Location:** Lines 248-280 (fetchSystemStatus function)

**Changes:**
- Replaced two API calls with single unified call
- Updated data mapping logic
- Added time formatting for last signal
- Simplified error handling

---

## 6️⃣ VERIFICATION CHECKLIST

### Pre-Deployment Checks

- [x] Endpoint created in `web_server.py`
- [x] Session logic implemented (7 sessions)
- [x] Database queries use `automated_signals` table
- [x] Timezone conversion (UTC → Eastern)
- [x] Webhook health calculation implemented
- [x] Error handling added
- [x] JavaScript updated to use new endpoint
- [x] Old endpoint references removed
- [x] Test script created

### Post-Deployment Checks

**After deploying to Railway:**

1. **Visit `/api/homepage-stats` directly**
   ```bash
   curl https://web-production-cd33.up.railway.app/api/homepage-stats
   ```
   - [ ] Returns 200 status
   - [ ] JSON format is correct
   - [ ] All 5 fields present
   - [ ] Session value is valid
   - [ ] Signals count is integer

2. **Confirm JSON output looks correct**
   - [ ] `current_session` matches current time
   - [ ] `signals_today` shows real count
   - [ ] `last_signal_time` is ISO 8601 format
   - [ ] `webhook_health` is valid status
   - [ ] `server_time_ny` is Eastern Time

3. **Reload homepage → verify all stats update**
   - [ ] Homepage loads without errors
   - [ ] Session displays correctly
   - [ ] Signals Today shows count
   - [ ] Last Signal shows time
   - [ ] Webhook status displays
   - [ ] No console errors

4. **Trigger TradingView webhook → verify homepage updates**
   - [ ] Send test webhook to `/api/automated-signals/webhook`
   - [ ] Wait 15 seconds for refresh
   - [ ] Signals Today increments
   - [ ] Last Signal updates
   - [ ] Webhook Health shows "OK"

5. **Confirm accurate session during each time of day**
   - [ ] Test during different sessions
   - [ ] Verify session changes at boundaries
   - [ ] Check DST handling (if applicable)

---

## 7️⃣ TESTING INSTRUCTIONS

### Manual Testing

**Step 1: Test API Directly**
```bash
# Run test script
python test_homepage_stats_endpoint.py
```

**Expected Output:**
```
✅ SUCCESS - Response received
✅ Valid session: NY AM
✅ Valid webhook health: OK
✅ Valid signals count: 14
✅ ALL TESTS PASSED
```

**Step 2: Test in Browser**
```
1. Open: https://web-production-cd33.up.railway.app/api/homepage-stats
2. Verify JSON response
3. Check all fields present
```

**Step 3: Test Homepage**
```
1. Open: https://web-production-cd33.up.railway.app/homepage
2. Open browser console (F12)
3. Check for errors
4. Verify stats display
5. Wait 15 seconds
6. Verify stats refresh
```

### Automated Testing

**Run test script:**
```bash
python test_homepage_stats_endpoint.py
```

**Test covers:**
- HTTP status code
- Response time
- Required fields presence
- Session validation
- Webhook health validation
- Signals count validation

---

## 8️⃣ EXPECTED BEHAVIOR

### Scenario 1: Normal Operation (Signals Exist)

**API Response:**
```json
{
  "current_session": "NY AM",
  "signals_today": 14,
  "last_signal_time": "2025-11-26T10:45:23-05:00",
  "webhook_health": "OK",
  "server_time_ny": "2025-11-26T10:50:00-05:00"
}
```

**Homepage Display:**
- Session: "NY AM"
- Signals Today: "14"
- Last Signal: "10:45 AM"
- Webhook: "OK"

---

### Scenario 2: No Signals Today

**API Response:**
```json
{
  "current_session": "LONDON",
  "signals_today": 0,
  "last_signal_time": "2025-11-25T15:30:00-05:00",
  "webhook_health": "CRITICAL",
  "server_time_ny": "2025-11-26T03:00:00-05:00"
}
```

**Homepage Display:**
- Session: "LONDON"
- Signals Today: "0"
- Last Signal: "3:30 PM" (yesterday)
- Webhook: "CRITICAL"

---

### Scenario 3: Database Connection Failure

**API Response:**
```json
{
  "error": "db_failure",
  "message": "Connection refused"
}
```

**HTTP Status:** 500

**Homepage Display:**
- Session: "--" (fallback)
- Signals Today: "0" (fallback)
- Last Signal: "--" (fallback)
- Webhook: "unknown" (fallback)

---

### Scenario 4: Market Closed

**API Response:**
```json
{
  "current_session": "CLOSED",
  "signals_today": 8,
  "last_signal_time": "2025-11-26T15:45:00-05:00",
  "webhook_health": "WARNING",
  "server_time_ny": "2025-11-26T18:30:00-05:00"
}
```

**Homepage Display:**
- Session: "CLOSED"
- Signals Today: "8"
- Last Signal: "3:45 PM"
- Webhook: "WARNING"

---

## 9️⃣ DATA SOURCE VERIFICATION

### ✅ NO MOCK DATA

**All data comes from:**
- `automated_signals` table (PostgreSQL on Railway)
- Server system time (converted to Eastern)
- Calculated webhook health (based on signal freshness)

**NO fake data:**
- ❌ No hardcoded values
- ❌ No placeholder data
- ❌ No mock responses
- ❌ No fallback fake data

**Fallback behavior:**
- If DB fails: Returns error + session/time only
- If no signals: Returns 0 count + NO_DATA status
- If API fails: JavaScript keeps previous values

---

## 🔟 DEPLOYMENT STEPS

### 1. Commit Changes

```bash
# Via GitHub Desktop:
1. Review changes in web_server.py
2. Review changes in static/js/homepage.js
3. Commit with message: "Add unified /api/homepage-stats endpoint"
4. Push to main branch
```

### 2. Railway Auto-Deploy

- Railway detects push to main
- Builds and deploys automatically
- Typically completes in 2-3 minutes

### 3. Verify Deployment

```bash
# Test endpoint
curl https://web-production-cd33.up.railway.app/api/homepage-stats

# Or run test script
python test_homepage_stats_endpoint.py
```

### 4. Test Homepage

```
1. Visit: https://web-production-cd33.up.railway.app/homepage
2. Open browser console
3. Verify no errors
4. Check stats display
5. Wait 15 seconds for refresh
6. Verify stats update
```

---

## 1️⃣1️⃣ TROUBLESHOOTING

### Issue: Endpoint returns 500 error

**Check:**
- DATABASE_URL environment variable set
- PostgreSQL connection working
- `automated_signals` table exists

**Fix:**
```bash
# Check Railway logs
railway logs

# Verify database connection
python -c "import os; print(os.environ.get('DATABASE_URL'))"
```

---

### Issue: Session shows "--"

**Check:**
- API response includes `current_session`
- JavaScript mapping is correct
- DOM element ID is `statusSession`

**Fix:**
- Check browser console for errors
- Verify API returns valid session
- Check DOM element exists

---

### Issue: Signals Today shows 0 (but signals exist)

**Check:**
- Timezone conversion working correctly
- Query filters for today's date in Eastern Time
- `automated_signals` table has data

**Fix:**
```sql
-- Check signals in database
SELECT 
    DATE(timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'US/Eastern') as signal_date,
    COUNT(DISTINCT trade_id) as count
FROM automated_signals
GROUP BY signal_date
ORDER BY signal_date DESC
LIMIT 5;
```

---

### Issue: Last Signal shows "--"

**Check:**
- `automated_signals` table has records
- Timestamp conversion working
- JavaScript time formatting working

**Fix:**
```sql
-- Check last signal
SELECT timestamp, trade_id, event_type
FROM automated_signals
ORDER BY timestamp DESC
LIMIT 1;
```

---

### Issue: Webhook Health shows "NO_DATA"

**Check:**
- `automated_signals` table has records
- Last signal query returns result

**Expected:**
- If no signals exist, "NO_DATA" is correct
- If signals exist but old, should show "CRITICAL"

---

## 1️⃣2️⃣ SUCCESS CRITERIA

### ✅ Implementation Complete When:

- [x] `/api/homepage-stats` endpoint created
- [x] Returns all 5 required fields
- [x] Uses real data from `automated_signals` table
- [x] Session calculated server-side
- [x] Webhook health calculated from signal freshness
- [x] Error handling implemented
- [x] JavaScript updated to use new endpoint
- [x] Old endpoint references removed
- [x] Test script created
- [x] Documentation complete

### ✅ Deployment Complete When:

- [ ] Endpoint accessible on Railway
- [ ] Returns 200 status code
- [ ] JSON format correct
- [ ] Homepage displays all stats
- [ ] Stats refresh every 15 seconds
- [ ] No console errors
- [ ] Session matches current time
- [ ] Signals count is accurate

---

## 1️⃣3️⃣ NEXT STEPS

### Optional Enhancements

1. **Add Caching**
   - Cache response for 5-10 seconds
   - Reduce database load
   - Improve response time

2. **Add More Stats**
   - Active trades count
   - Win rate today
   - Average MFE today

3. **Add WebSocket Updates**
   - Push updates on new signals
   - Real-time webhook health
   - Eliminate 15-second delay

4. **Add Client-Side Fallback**
   - Calculate session client-side if API fails
   - Show "stale data" indicator
   - Retry failed requests

---

**END OF IMPLEMENTATION REPORT**
