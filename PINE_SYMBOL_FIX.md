# Pine Script Symbol Fix for UNIFIED_SNAPSHOT_V1

## Required Change

In your UNIFIED_SNAPSHOT_V1 payload builder, change the symbol field from `syminfo.ticker` to `syminfo.tickerid`:

```pinescript
string unified_payload = '{"event_type":"UNIFIED_SNAPSHOT_V1","symbol":"' + syminfo.tickerid + '","timeframe":"' + timeframe.period + '","bar_ts":' + str.tostring(time) + ',"open":' + f_num(open) + ',"high":' + f_num(high) + ',"low":' + f_num(low) + ',"close":' + f_num(close) + ',"signals":[' + unified_signals + ']}'
```

## Why

- `syminfo.ticker` returns just the contract code (e.g., `"MNQ1!"`)
- `syminfo.tickerid` returns the full identifier with exchange (e.g., `"CME_MINI:MNQ1!"`)

The backend canonical_symbol() function strips the exchange prefix for matching, but we need the full tickerid to ensure consistent symbol storage across all data sources.

## Expected Value

For NQ futures: `"CME_MINI:MNQ1!"` or `"CME_MINI:NQH2025"`

## Verification

After updating and restarting the alert:
- `/api/data-quality/indicator-health` → `price_snapshots.count_60m` should rise
- `/api/automated-signals/dashboard-data` → `stats.matched_price_count` should increase
- `/api/automated-signals/dashboard-data` → `stats.active_missing_symbol_count` should drop to 0
