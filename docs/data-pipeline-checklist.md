# Data Pipeline Checklist - UNIFIED_SNAPSHOT_V1

## TradingView Alert Payload Requirements

### Required Fields

**Top-Level:**
- `event_type`: Must be `"UNIFIED_SNAPSHOT_V1"`
- `symbol`: Use `syminfo.tickerid` (e.g., `"CME_MINI:MNQ1!"`) NOT `syminfo.ticker`
- `timeframe`: Must match backend expectation (currently `"1m"`)
- `bar_ts`: Unix timestamp in milliseconds, aligned to 1m bar open
- `open`: Bar open price (numeric)
- `high`: Bar high price (numeric)
- `low`: Bar low price (numeric)
- `close`: Bar close price (numeric)
- `signals`: Array of signal objects (may be empty `[]`)

### Signal Object Fields (if signals present)

Each signal in the `signals` array should include:
- `trade_id`: Canonical trade identifier
- `triangle_time`: Unix ms timestamp of signal triangle
- `confirmation_time`: Unix ms timestamp of confirmation (optional)
- `date`: Date string `"YYYY-MM-DD"`
- `direction`: `"Bullish"` or `"Bearish"`
- `session`: Trading session name
- `entry`: Entry price (numeric)
- `stop`: Stop loss price (numeric)
- `symbol`: Same as top-level symbol
- `be_mfe`: Break-even MFE value (numeric)
- `no_be_mfe`: No break-even MFE value (numeric)
- `mae`: Maximum adverse excursion (numeric, ≤ 0)
- `completed`: Boolean (`true` or `false`)

## Verification Steps

### 1. Check Price Snapshot Stream Health

**Endpoint:** `GET /api/data-quality/indicator-health`

**Expected:**
- `streams.price_snapshots.count_60m` should be ~60 (one per minute)
- `streams.price_snapshots.last_received_at` should be recent (< 2 minutes old)
- `streams.unified_snapshot_v1.count_60m` should be ~60
- `traffic_light` should be `"GREEN"`

### 2. Check Dashboard Live Metrics

**Endpoint:** `GET /api/automated-signals/dashboard-data`

**Expected:**
- `stats.matched_price_count` should rise toward `stats.active_count`
- `stats.active_missing_symbol_count` should be 0 or very low
- `stats.active_missing_timeframe_count` should be 0
- Active trades should have `last_price` and `last_price_ts` fields
- `last_price_ts` should advance every minute

### 3. Check Symbol Backfill

**Endpoint:** `GET /api/debug/sql?token=<token>&sql=SELECT COUNT(*) AS missing FROM confirmed_signals_ledger WHERE symbol IS NULL OR symbol = ''`

**Expected:**
- `rows[0].missing` should be 0 or decreasing

## Common Issues

### Symbol Mismatch
- **Problem:** `matched_price_count` stays 0
- **Cause:** Symbol format mismatch between payload and database
- **Fix:** Ensure TradingView uses `syminfo.tickerid` (includes exchange prefix)
- **Backend:** Canonical symbol normalization strips prefix after `:` for matching

### Stale Timestamps
- **Problem:** `last_price_ts` doesn't advance
- **Cause:** TradingView alert not running or not sending
- **Fix:** Verify alert is enabled and triggering on bar close

### Missing Symbol in Ledger
- **Problem:** `active_missing_symbol_count` > 0
- **Cause:** Old trades created before symbol field existed
- **Fix:** Run backfill endpoint: `POST /api/admin/backfill-ledger-symbol?token=<token>`

## Alert Configuration

**TradingView Alert Settings:**
- **Condition:** On bar close
- **Frequency:** Once per bar close
- **Webhook URL:** `https://web-production-f8c3.up.railway.app/api/indicator-export?token=nQ-EXPORT-9f3a2c71a9e44d0c`
- **Message:** JSON payload with all required fields above

**Pine Script Settings:**
- `ENABLE_UNIFIED_SNAPSHOT` = `true`
- `ENABLE_LIVE_CONFIRMED_EXPORT` = `false` (to avoid duplicate alerts)
- Timeframe: 1 minute chart
