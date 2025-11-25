# 📝 HOMEPAGE STATS ENDPOINT - CHANGES SUMMARY

## Modified Files

### 1. `web_server.py`
**Lines Added:** ~120 lines (after line 1372)

**New Endpoint:**
```python
@app.route('/api/homepage-stats', methods=['GET'])
def get_homepage_stats():
    """
    Unified homepage statistics endpoint
    Returns: current_session, signals_today, last_signal_time, webhook_health, server_time_ny
    Data source: automated_signals table (TradingView ingestion pipeline)
    """
```

**Key Features:**
- Server-side session calculation (7 sessions: ASIA, LONDON, NY PRE, NY AM, NY LUNCH, NY PM, CLOSED)
- Real-time signals count from `automated_signals` table
- Last signal timestamp with timezone conversion (UTC → Eastern)
- Webhook health based on signal freshness (OK/WARNING/CRITICAL/NO_DATA)
- Comprehensive error handling

---

### 2. `static/js/homepage.js`
**Lines Modified:** ~35 lines (lines 248-280)

**Old Code (REMOVED):**
```javascript
// Two separate API calls to non-existent endpoints
const statusResponse = await fetch('/api/system-status');
const statsResponse = await fetch('/api/signals/stats/today');
```

**New Code (ADDED):**
```javascript
// Single unified API call
const response = await fetch('/api/homepage-stats');
const data = await response.json();

// Map response to systemStatus object
systemStatus.current_session = data.current_session || '--';
systemStatus.signals_today = data.signals_today || 0;
systemStatus.last_signal = data.last_signal_time || '--';
systemStatus.webhook_health = data.webhook_health || 'unknown';
```

---

### 3. `test_homepage_stats_endpoint.py` (NEW FILE)
**Purpose:** Test script to verify endpoint functionality

**Tests:**
- HTTP status code
- Response time
- Required fields presence
- Session validation
- Webhook health validation
- Signals count validation

---

## API Response Format

```json
{
  "current_session": "NY AM",
  "signals_today": 14,
  "last_signal_time": "2025-11-26T14:32:10-05:00",
  "webhook_health": "OK",
  "server_time_ny": "2025-11-26T14:45:01-05:00"
}
```

---

## Data Flow

```
TradingView Webhook
    ↓
/api/automated-signals/webhook
    ↓
automated_signals table (PostgreSQL)
    ↓
/api/homepage-stats (NEW)
    ↓
Homepage JavaScript
    ↓
DOM Updates (statusSession, statusSignals, statusLastSignal, statusWebhook)
```

---

## Verification Steps

### 1. Test API Directly
```bash
curl https://web-production-cd33.up.railway.app/api/homepage-stats
```

### 2. Run Test Script
```bash
python test_homepage_stats_endpoint.py
```

### 3. Test Homepage
```
1. Visit: https://web-production-cd33.up.railway.app/homepage
2. Open browser console (F12)
3. Verify no errors
4. Check stats display
5. Wait 15 seconds for refresh
```

---

## Deployment Checklist

- [x] Backend endpoint created
- [x] Frontend JavaScript updated
- [x] Old endpoints removed
- [x] Test script created
- [x] Documentation complete
- [ ] Deploy to Railway
- [ ] Test on production
- [ ] Verify stats update
- [ ] Confirm session accuracy

---

## Success Criteria

✅ **Implementation Complete:**
- Endpoint returns all 5 required fields
- Uses real data from `automated_signals` table
- No mock or fake data
- Error handling implemented
- JavaScript updated
- Old endpoints removed

⏳ **Deployment Pending:**
- Test on Railway production
- Verify homepage displays stats
- Confirm 15-second refresh works
- Validate session accuracy

---

**Ready for deployment via GitHub Desktop → Railway auto-deploy**
