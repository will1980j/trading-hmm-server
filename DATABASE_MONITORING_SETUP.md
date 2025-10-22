# Database Health Monitoring System

## Overview
Comprehensive monitoring system to prevent and auto-fix database transaction issues.

## What Was Added

### 1. Enhanced Database Connection (`database/railway_db.py`)
- **Transaction status checking** - Detects aborted transactions
- **Auto-cleanup method** - `ensure_clean_transaction()`
- **Explicit isolation level** - READ COMMITTED
- **Initial rollback** - Starts with clean slate

### 2. Background Health Monitor (`database_health_monitor.py`)
Runs continuously in the background to:
- Check transaction status every 60 seconds
- Auto-fix aborted transactions
- Reconnect if connection drops
- Monitor signal flow
- Track statistics

**Features:**
- ✅ Automatic aborted transaction detection and rollback
- ✅ Connection health monitoring
- ✅ Signal flow tracking
- ✅ Auto-reconnection on failures
- ✅ Statistics tracking
- ✅ Runs as daemon thread (doesn't block server shutdown)

### 3. API Endpoints

#### `/api/db-health` (GET)
Check database health status
```json
{
  "status": "healthy",
  "transaction_status": "idle",
  "query_test": true,
  "signals": {
    "last_hour_count": 15,
    "last_signal": "2025-10-22T06:45:00"
  }
}
```

#### `/api/db-reset` (POST)
Emergency database reset (already existed, now enhanced)

### 4. Webhook Handler Improvements
- **Pre-check transaction state** before processing
- **Auto-rollback** on errors
- **Reconnection logic** if database is stuck
- **Better error logging**

## How It Works

### Startup Sequence
1. Server starts
2. Database connection established
3. Initial transaction rollback
4. Background monitor thread starts
5. Monitor checks health every 60 seconds

### When Aborted Transaction Detected
1. Monitor detects `TRANSACTION_STATUS_INERROR`
2. Automatically calls `conn.rollback()`
3. Logs the fix
4. Increments `aborted_transactions_fixed` counter
5. Next webhook will work normally

### When Connection Drops
1. Monitor detects connection failure
2. Attempts reconnection
3. Logs reconnection attempt
4. Increments `reconnections` counter
5. Continues monitoring

## Monitoring Statistics

The monitor tracks:
- **Total checks** - Number of health checks performed
- **Healthy checks** - Successful health checks
- **Aborted transactions fixed** - Auto-fixed transaction errors
- **Reconnections** - Database reconnection attempts
- **Errors** - Failed health checks

Stats are logged every 10 checks (every 10 minutes with 60s interval).

## Usage

### Check Database Health (API)
```bash
curl https://web-production-cd33.up.railway.app/api/db-health
```

### Reset Database (Emergency)
```bash
curl -X POST https://web-production-cd33.up.railway.app/api/db-reset
```

### Run Monitor Standalone (Local Testing)
```bash
python database_health_monitor.py
```

### Check Database Health (Local Script)
```bash
python check_database_health.py
```

## Configuration

### Monitor Check Interval
Default: 60 seconds

To change, edit `web_server.py`:
```python
monitor = DatabaseHealthMonitor(check_interval=30)  # 30 seconds
```

### Max Consecutive Errors
Default: 3

To change, edit `database_health_monitor.py`:
```python
self.max_consecutive_errors = 5  # Allow 5 errors before recovery
```

## Benefits

1. **Prevents stuck webhooks** - Auto-fixes aborted transactions
2. **Self-healing** - Reconnects automatically
3. **Visibility** - Track database health via API
4. **Proactive** - Detects issues before they affect users
5. **No manual intervention** - Fixes itself automatically

## Monitoring Dashboard Integration

The ML Intelligence Hub already shows webhook health. You can enhance it to show database health:

```javascript
// Add to ml_feature_dashboard.html
async function loadDatabaseHealth() {
    const response = await fetch('/api/db-health');
    const data = await response.json();
    // Display database status
}
```

## Troubleshooting

### If monitor isn't running:
1. Check Railway logs for "Database health monitor started"
2. Verify `db_enabled` is True
3. Check for startup errors

### If aborted transactions persist:
1. Check Railway logs for monitor activity
2. Manually call `/api/db-reset`
3. Check for code errors causing repeated failures

### If signals still not flowing:
1. Check `/api/db-health` endpoint
2. Verify TradingView alert is active
3. Check webhook URL in TradingView
4. Review Railway logs for webhook errors

## Next Steps

After deployment:
1. ✅ Monitor starts automatically
2. ✅ Check `/api/db-health` to verify
3. ✅ Watch Railway logs for monitor activity
4. ✅ Test webhook with TradingView signal
5. ✅ Signals should flow to ML dashboard

## Files Modified/Created

- ✅ `database/railway_db.py` - Enhanced connection class
- ✅ `database_health_monitor.py` - Background monitor
- ✅ `web_server.py` - Added monitor startup and API endpoints
- ✅ `check_database_health.py` - Diagnostic tool
- ✅ `DATABASE_MONITORING_SETUP.md` - This documentation

## Deploy Instructions

1. Commit all changes
2. Push to Railway (or redeploy)
3. Monitor will start automatically
4. Check logs for "Database health monitor started"
5. Test with: `python test_railway_webhook.py`
