# Phase D.3: Historical API v1 Reference

**Base URL:** `/api/hist/v1`  
**Authentication:** None (read-only, internal use)  
**Timestamp Format:** RFC3339 (UTC)  
**Timestamp Semantics:** ts = bar OPEN time (TradingView convention)

---

## Historical Data Endpoints

### GET /api/hist/v1/world

Get complete world state at a single timestamp.

**Parameters:**
- `symbol` (required): Symbol (e.g., GLBX.MDP3:NQ)
- `ts` (required): RFC3339 timestamp (bar OPEN time)
- `include` (optional): Comma-separated list (default: ohlcv,bias,triangles)

**Response:**
```json
{
  "timestamp": "2025-12-02T00:14:00Z",
  "timezone": "UTC",
  "symbol": "GLBX.MDP3:NQ",
  "ohlcv": {
    "open": 25406.25,
    "high": 25408.75,
    "low": 25400.25,
    "close": 25402.50,
    "volume": 1234
  },
  "bias": {
    "1m": "Bearish",
    "5m": "Bullish",
    "15m": "Neutral",
    "1h": "Neutral",
    "4h": "Neutral",
    "1d": "Neutral"
  },
  "triangles": [
    {
      "direction": "BEAR",
      "bias_1m": "Bearish",
      "htf_bullish": true,
      "htf_bearish": true
    }
  ]
}
```

**Errors:**
- 400: Missing required parameters or invalid format
- 404: No bar found at timestamp
- 409: Timestamp not aligned to 1m boundary

---

### GET /api/hist/v1/bars

Get OHLCV bars for a time range.

**Parameters:**
- `symbol` (required): Symbol
- `tf` (optional): Timeframe (default: 1m, only 1m implemented)
- `start` (required): Start timestamp (RFC3339)
- `end` (required): End timestamp (RFC3339)
- `limit` (optional): Max rows (default: 10000, max: 50000)

**Response:**
```json
{
  "symbol": "GLBX.MDP3:NQ",
  "timeframe": "1m",
  "start": "2025-12-02T00:10:00Z",
  "end": "2025-12-02T00:30:00Z",
  "count": 21,
  "bars": [
    {
      "ts": "2025-12-02T00:10:00Z",
      "open": 25410.00,
      "high": 25412.50,
      "low": 25408.00,
      "close": 25411.25,
      "volume": 1500
    }
  ]
}
```

---

### GET /api/hist/v1/bias

Get HTF bias series for a time range.

**Parameters:**
- `symbol` (required): Symbol
- `start` (required): Start timestamp (RFC3339)
- `end` (required): End timestamp (RFC3339)
- `tfs` (optional): Comma-separated timeframes (default: 5m,15m,60m,240m,1d)
- `format` (optional): Response format (default: columns)
- `limit` (optional): Max rows (default: 10000, max: 50000)

**Response:**
```json
{
  "symbol": "GLBX.MDP3:NQ",
  "start": "2025-12-02T00:10:00Z",
  "end": "2025-12-02T00:30:00Z",
  "count": 21,
  "rows": [
    {
      "ts": "2025-12-02T00:10:00Z",
      "bias_1m": "Bullish",
      "bias_5m": "Bullish",
      "bias_15m": "Neutral",
      "bias_1h": "Neutral",
      "bias_4h": "Neutral",
      "bias_1d": "Neutral"
    }
  ]
}
```

---

### GET /api/hist/v1/triangles/events

Get triangle events for a time range.

**Parameters:**
- `symbol` (required): Symbol
- `start` (required): Start timestamp (RFC3339)
- `end` (required): End timestamp (RFC3339)
- `types` (optional): Comma-separated types (BULL, BEAR)
- `limit` (optional): Max rows (default: 1000, max: 10000)

**Response:**
```json
{
  "symbol": "GLBX.MDP3:NQ",
  "start": "2025-12-02T00:10:00Z",
  "end": "2025-12-02T00:30:00Z",
  "count": 2,
  "events": [
    {
      "ts": "2025-12-02T00:14:00Z",
      "direction": "BEAR",
      "bias_1m": "Bearish",
      "bias_5m": "Bullish",
      "bias_15m": "Neutral",
      "bias_1h": "Neutral",
      "htf_bullish": true,
      "htf_bearish": true,
      "source_table": "market_bars_ohlcv_1m_clean",
      "logic_version": "c2c3716"
    }
  ]
}
```

---

### GET /api/hist/v1/dataset

Get analytics-friendly joined dataset (1 row per 1m bar).

**Parameters:**
- `symbol` (required): Symbol
- `start` (required): Start timestamp (RFC3339)
- `end` (required): End timestamp (RFC3339)
- `include` (optional): Comma-separated (default: ohlcv,bias,triangles_count)
- `limit` (optional): Max rows (default: 10000, max: 50000)

**Response:**
```json
{
  "symbol": "GLBX.MDP3:NQ",
  "start": "2025-12-02T00:10:00Z",
  "end": "2025-12-02T00:30:00Z",
  "count": 21,
  "rows": [
    {
      "ts": "2025-12-02T00:10:00Z",
      "open": 25410.00,
      "high": 25412.50,
      "low": 25408.00,
      "close": 25411.25,
      "volume": 1500,
      "bias_1m": "Bullish",
      "bias_5m": "Bullish",
      "bias_15m": "Neutral",
      "bias_1h": "Neutral",
      "bias_4h": "Neutral",
      "bias_1d": "Neutral",
      "triangles_count": 0
    }
  ]
}
```

**Note:** Default does NOT return full triangle payloads (too heavy). Only counts unless explicitly requested.

---

## Quality Gate Endpoints

### GET /api/hist/v1/quality/coverage

Check data coverage for a time range.

**Parameters:**
- `symbol` (required): Symbol
- `start` (required): Start timestamp (RFC3339)
- `end` (required): End timestamp (RFC3339)

**Response:**
```json
{
  "symbol": "GLBX.MDP3:NQ",
  "start": "2025-12-02T00:10:00Z",
  "end": "2025-12-02T00:30:00Z",
  "checks": {
    "bars_1m_present": {
      "pass": true,
      "missing_count": 0,
      "found": 21,
      "expected": 21
    },
    "bias_rows_present": {
      "pass": true,
      "missing_count": 0,
      "found": 21,
      "expected": 21
    },
    "triangles_backfilled": {
      "pass": true,
      "count": 2
    }
  },
  "pass": true
}
```

---

### GET /api/hist/v1/quality/alignment

Verify timestamp alignment and data consistency.

**Parameters:**
- `symbol` (required): Symbol
- `start` (required): Start timestamp (RFC3339)
- `end` (required): End timestamp (RFC3339)

**Response:**
```json
{
  "symbol": "GLBX.MDP3:NQ",
  "start": "2025-12-02T00:10:00Z",
  "end": "2025-12-02T00:30:00Z",
  "checks": {
    "timestamps_1m_aligned": {
      "pass": true,
      "misaligned_count": 0
    },
    "bias_timestamps_aligned": {
      "pass": true,
      "misaligned_count": 0
    },
    "no_unexpected_gaps": {
      "pass": true,
      "gap_count": 0,
      "note": "Gaps >5min detected (may be expected for overnight/weekend)"
    }
  },
  "pass": true
}
```

---

### GET /api/hist/v1/quality/determinism

Verify deterministic dataset hash for repeatability.

**Parameters:**
- `symbol` (required): Symbol
- `start` (required): Start timestamp (RFC3339)
- `end` (required): End timestamp (RFC3339)
- `include` (optional): What to hash (default: ohlcv,bias)

**Response:**
```json
{
  "symbol": "GLBX.MDP3:NQ",
  "start": "2025-12-02T00:10:00Z",
  "end": "2025-12-02T00:20:00Z",
  "dataset_hash": "a1b2c3d4e5f6g7h8",
  "row_count": 200,
  "pass": true
}
```

---

## Example Usage

### Get World State
```bash
curl "http://localhost:5000/api/hist/v1/world?symbol=GLBX.MDP3:NQ&ts=2025-12-02T00:14:00Z&include=ohlcv,bias,triangles"
```

### Get Bars Window
```bash
curl "http://localhost:5000/api/hist/v1/bars?symbol=GLBX.MDP3:NQ&start=2025-12-02T00:10:00Z&end=2025-12-02T00:30:00Z&limit=100"
```

### Get Bias Series
```bash
curl "http://localhost:5000/api/hist/v1/bias?symbol=GLBX.MDP3:NQ&start=2025-12-02T00:10:00Z&end=2025-12-02T00:30:00Z"
```

### Check Coverage
```bash
curl "http://localhost:5000/api/hist/v1/quality/coverage?symbol=GLBX.MDP3:NQ&start=2025-12-02T00:10:00Z&end=2025-12-02T00:30:00Z"
```

### Check Determinism
```bash
curl "http://localhost:5000/api/hist/v1/quality/determinism?symbol=GLBX.MDP3:NQ&start=2025-12-02T00:10:00Z&end=2025-12-02T00:20:00Z"
```

---

## Tables Backing Endpoints

| Endpoint | Primary Table | Secondary Tables |
|----------|---------------|------------------|
| world | market_bars_ohlcv_1m_clean | bias_series_1m_v1, triangle_events_v1 |
| bars | market_bars_ohlcv_1m_clean | - |
| bias | bias_series_1m_v1 | - |
| triangles/events | triangle_events_v1 | - |
| dataset | market_bars_ohlcv_1m_clean | bias_series_1m_v1, triangle_events_v1 |

---

## Contract Tests

Run with: `python tests/test_historical_v1_api.py`

**Tests:**
1. World endpoint returns correct bias stack
2. Dataset row count equals bars in window
3. Determinism hash identical across calls
4. Alignment checks pass for known range
5. Coverage checks pass for known range

**All tests must pass before Phase D.3 sign-off.**

---

**Status:** Phase D.3 complete - Historical API operational with quality gates
