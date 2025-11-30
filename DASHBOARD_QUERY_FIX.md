# Dashboard Query Fix - November 30, 2025

## Problem Identified

You weren't seeing signals on the dashboard because:

1. **Wrong URL**: The dashboard is at `/automated-signals` NOT `/automated-signals-dashboard`
2. **Query Bug**: The dashboard-data query was returning raw event rows instead of properly aggregated trade data
   - It returned multiple rows per trade (ENTRY, MFE_UPDATE, BE_TRIGGERED)
   - The first row shown might be a BE_TRIGGERED event with NULL direction/entry_price
   - Old trades from Nov 28 had incomplete data

## Fix Applied

Modified `automated_signals_api_robust.py`:

### Active Trades Query (BEFORE)
```sql
SELECT * FROM automated_signals
WHERE trade_id NOT IN (SELECT trade_id FROM ... WHERE event_type IN ('EXIT_...'))
AND event_type IN ('ENTRY', 'MFE_UPDATE', 'BE_TRIGGERED')
```
This returned ALL events, not aggregated trades.

### Active Trades Query (AFTER)
```sql
WITH entry_data AS (
    SELECT trade_id, direction, entry_price, stop_loss, session, bias, timestamp
    FROM automated_signals WHERE event_type = 'ENTRY'
),
latest_mfe AS (
    SELECT DISTINCT ON (trade_id) trade_id, mfe, be_mfe, no_be_mfe, current_price
    FROM automated_signals
    WHERE event_type IN ('ENTRY', 'MFE_UPDATE', 'BE_TRIGGERED')
    ORDER BY trade_id, timestamp DESC
),
active_trade_ids AS (
    SELECT DISTINCT trade_id FROM automated_signals
    WHERE event_type = 'ENTRY'
    AND trade_id NOT IN (SELECT trade_id FROM ... WHERE event_type IN ('EXIT_...'))
)
SELECT e.*, m.mfe, m.be_mfe, m.no_be_mfe
FROM active_trade_ids a
JOIN entry_data e ON a.trade_id = e.trade_id
LEFT JOIN latest_mfe m ON a.trade_id = m.trade_id
```

This properly:
- Gets ENTRY event data (direction, entry_price, stop_loss)
- Joins with latest MFE values
- Returns ONE row per trade with complete data

## Deployment Required

Commit and push to GitHub to deploy to Railway:
```
git add automated_signals_api_robust.py
git commit -m "Fix dashboard query to properly aggregate trade data"
git push
```

## Correct Dashboard URL

Access the dashboard at:
**https://web-production-f8c3.up.railway.app/automated-signals**

(NOT /automated-signals-dashboard)
