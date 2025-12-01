# Dashboard Fixes - December 1, 2025

## Issues Fixed

### 1. Signal Time Not Matching TradingView Signal Candle
**Problem:** `signal_date` and `signal_time` were using `CURRENT_DATE` and `CURRENT_TIME` (database server time) instead of the actual signal candle time from TradingView.

**Fix:** Modified `handle_entry_signal` to:
- Parse `date` and `time` fields from webhook payload
- Store parsed values in `signal_date` and `signal_time` columns
- Falls back to NULL if not provided (instead of server time)

### 2. MFE Values Showing 0 for Active Trades
**Problem:** 
- Dashboard query was looking for separate `MFE_UPDATE` event rows
- `handle_mfe_update` was updating the ENTRY row directly
- **ROOT CAUSE:** Indicator sends `mfe_R` field, but handler was looking for `be_mfe`/`no_be_mfe`

**Fix:** 
- Modified dashboard query to get MFE directly from ENTRY row
- **Fixed `handle_mfe_update`** to parse `mfe_R` field from indicator payload
- **Fixed `signal_normalization.py`** to normalize `mfe_R` to `be_mfe`/`no_be_mfe`

### 3. Session Not Updating Correctly
**Problem:** Session was being stored on ENTRY but not propagated properly.

**Fix:** Dashboard query now gets session directly from ENTRY row.

### 4. Age Calculation for Active/Completed Trades
**Problem:** Age was calculated from `timestamp` (webhook receipt time) instead of `signal_time`.

**Fix:** Dashboard now returns:
- `signal_date` and `signal_time` for proper age calculation
- `entry_timestamp` for completed trades
- `exit_timestamp` for completed trades

### 5. Lifecycle R Journey Not Showing
**Problem:** Trade detail endpoint returns events but MFE_UPDATE events have NULL values.

**Root Cause:** Same as #2 - `mfe_R` field wasn't being parsed.

**Fix:** With the `mfe_R` parsing fix, future MFE_UPDATE events will have proper values.

## Files Modified
- `web_server.py`:
  - `handle_entry_signal()` - Fixed signal_date/signal_time storage
  - `get_automated_signals_dashboard_data()` - Fixed queries and result parsing

## API Response Changes

### Active Trades Now Include:
```json
{
  "trade_id": "...",
  "signal_date": "2025-12-01",
  "signal_time": "10:30:00",
  "be_mfe": 0.5,
  "no_be_mfe": 0.75,
  "current_price": 21500.00,
  "session": "NY AM",
  ...
}
```

### Completed Trades Now Include:
```json
{
  "trade_id": "...",
  "signal_date": "2025-12-01",
  "signal_time": "10:30:00",
  "entry_timestamp": "2025-12-01T10:31:00",
  "exit_timestamp": "2025-12-01T11:15:00",
  "be_mfe": 1.0,
  "no_be_mfe": 1.5,
  "final_mfe": 1.5,
  ...
}
```

## Deployment Required
These changes need to be deployed to Railway via GitHub Desktop.

## Frontend Changes Needed
The dashboard frontend may need updates to:
1. Use `signal_time` for Age calculation instead of `timestamp`
2. Display refresh indicator (currently 7 seconds, should show visual feedback)
3. Update lifecycle visualization to use proper event data


## Root Cause Analysis

The TradingView indicator (`complete_automated_trading_system.pine`) sends MFE values in the `mfe_R` field:

```json
{
  "event_type": "MFE_UPDATE",
  "trade_id": "20251201_103000000_BULLISH",
  "mfe_R": 0.75,
  ...
}
```

But the webhook handler was looking for `be_mfe` and `no_be_mfe` fields:

```python
# OLD (broken)
be_mfe = float(data.get('be_mfe', 0))
no_be_mfe = float(data.get('no_be_mfe', 0))

# NEW (fixed)
be_mfe = float(data.get('be_mfe') or data.get('mfe_R') or data.get('mfe') or 0)
no_be_mfe = float(data.get('no_be_mfe') or data.get('mfe_R') or data.get('mfe') or 0)
```

## Files Modified

1. **web_server.py**:
   - `handle_entry_signal()` - Fixed signal_date/signal_time storage
   - `handle_mfe_update()` - Fixed mfe_R field parsing
   - `get_automated_signals_dashboard_data()` - Fixed queries and result parsing

2. **signal_normalization.py**:
   - `normalize_signal_payload()` - Added mfe_R field normalization

## Deployment Required

These changes need to be deployed to Railway via GitHub Desktop:

1. Commit changes with message: "Fix dashboard MFE display and signal time issues"
2. Push to main branch
3. Railway will auto-deploy

## Testing After Deployment

1. Send a test MFE_UPDATE webhook to verify mfe_R is parsed
2. Check dashboard shows non-zero MFE for active trades
3. Verify signal_time matches TradingView signal candle time
4. Check Age column shows correct values

## Note on Historical Data

Existing MFE_UPDATE events in the database have NULL/0 values because they were processed before this fix. Only new events will have correct MFE values.

## Additional Fixes Applied

### 6. Parse event_timestamp for signal_date/signal_time
The indicator sends `event_timestamp` in ISO format, not separate `date`/`time` fields.
Fixed `handle_entry_signal` to parse `event_timestamp` and extract date/time.

### 7. Fallback to trade_id for date/time
Added fallback logic to extract signal date/time from trade_id format (`YYYYMMDD_HHMMSS000_DIRECTION`) when not stored in database.

### 8. Purged Orphaned Trades
Deleted 20 orphaned trades (426 events) from Nov 21 that were stuck as "ACTIVE" because they never received EXIT events. These were 9+ days old and cluttering the dashboard.

## Root Cause of "Many Active Trades"

The dashboard was showing old orphaned trades from Nov 21 that never received EXIT events. These trades appeared as "ACTIVE" with:
- Incorrect times (showing Nov 21 times, not today)
- 0 MFE values (no MFE_UPDATE events received)
- 11+ hour "Age" (actually 9+ days old)

**Solution:** Purged stale data and fixed the backend to properly parse timestamps.

## TradingView Webhook Status

⚠️ **No webhooks received today (Dec 1)** - The indicator may not be sending alerts or the webhook URL may need verification in TradingView alert settings.
