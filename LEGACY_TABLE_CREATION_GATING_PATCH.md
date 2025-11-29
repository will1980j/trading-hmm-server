# ✅ STRICT PATCH REPORT: Legacy Table Creation Gating

## File Hash Changes
| Metric | Value |
|--------|-------|
| **OLD HASH** | `DE9B7F8649E274200256C7A641C1BC37` |
| **NEW HASH** | `172E7F6EC42F08A7F4F9165275AD461C` |
| **File** | `web_server.py` |

---

## Tables Gated

### 1. Prop Firm Tables (ENABLE_PROP)
**Location:** Lines ~9035-9105
**Gate:** `ENABLE_PROP`

| Table | Status |
|-------|--------|
| `prop_firms` | ✅ GATED |
| `prop_programs` | ✅ GATED |
| `prop_scaling_rules` | ✅ GATED |
| `economic_news_cache` | ✅ GATED |

### 2. Legacy Table ALTER Statements (ENABLE_LEGACY)
**Location:** Lines ~9107-9155
**Gate:** `ENABLE_LEGACY`

| Table | Operation | Status |
|-------|-----------|--------|
| `live_signals` | ALTER ADD htf_aligned, htf_status, session | ✅ GATED |
| `live_signals` | ALTER ADD market_context, context_quality_score | ✅ GATED |
| `signal_lab_trades` | ALTER ADD active_trade, htf_aligned | ✅ GATED |
| `signal_lab_trades` | ALTER ADD market_context, ml_prediction | ✅ GATED |

### 3. Dual-Indicator Schema (ENABLE_V2)
**Location:** Lines ~11207-11300
**Gate:** `ENABLE_V2` (via API endpoint `/api/deploy-dual-schema`)

| Table | Status |
|-------|--------|
| `realtime_prices` | ✅ GATED |
| `enhanced_signals_v2` | ✅ GATED |
| `realtime_mfe_updates` | ✅ GATED |

### 4. Replay Candles (ENABLE_REPLAY) - Already Gated
**Location:** Lines ~9160-9195
**Gate:** `ENABLE_REPLAY` (pre-existing)

| Table | Status |
|-------|--------|
| `replay_candles` | ✅ ALREADY GATED |

---

## H1 Core Tables - NOT GATED (Always Active)

| Table | Location | Status |
|-------|----------|--------|
| `automated_signals` | Lines 11501, 12215 | ✅ NOT GATED (H1 Core) |
| `telemetry_automated_signals_log` | Line 11909 | ✅ NOT GATED (H1 Core) |
| `automated_signals_v2` | Line 11548 | ✅ GATED by `ENABLE_SCHEMA_V2` (staging only) |
| `execution_tasks` | Lines 377, 429 | ✅ GATED by `ENABLE_EXECUTION` |
| `execution_logs` | Lines 391, 447 | ✅ GATED by `ENABLE_EXECUTION` |

---

## Gating Summary

| Flag | Default | Tables Controlled |
|------|---------|-------------------|
| `ENABLE_LEGACY` | `false` | live_signals ALTER, signal_lab_trades ALTER |
| `ENABLE_PROP` | `false` | prop_firms, prop_programs, prop_scaling_rules, economic_news_cache |
| `ENABLE_V2` | `false` | realtime_prices, enhanced_signals_v2, realtime_mfe_updates |
| `ENABLE_REPLAY` | `false` | replay_candles |
| `ENABLE_EXECUTION` | `false` | execution_tasks, execution_logs |
| `ENABLE_SCHEMA_V2` | `false` | automated_signals_v2 (staging) |

---

## Behavior When All Flags = false (Default)

**Tables Created on Startup:**
- ✅ `automated_signals` (H1 Core)
- ✅ `telemetry_automated_signals_log` (H1 Core)

**Tables NOT Created:**
- ❌ `prop_firms`, `prop_programs`, `prop_scaling_rules`
- ❌ `live_signals` ALTER statements skipped
- ❌ `signal_lab_trades` ALTER statements skipped
- ❌ `realtime_prices`, `enhanced_signals_v2`, `realtime_mfe_updates`
- ❌ `replay_candles`
- ❌ `execution_tasks`, `execution_logs`
- ❌ `automated_signals_v2` (staging)

---

## Confirmation: H1 Core Untouched

| Component | Modified? | Notes |
|-----------|-----------|-------|
| `automated_signals` CREATE | ❌ NO | Always runs |
| `automated_signals` ALTER (lifecycle) | ❌ NO | Always runs |
| `telemetry_automated_signals_log` | ❌ NO | Always runs |
| Webhook handlers | ❌ NO | Unchanged |
| API endpoints for automated_signals | ❌ NO | Unchanged |

---

## Status

**✅ STRICT PATCH APPLIED SUCCESSFULLY**

- All legacy table creation is GATED
- H1 core tables remain ACTIVE
- No startup errors when `ENABLE_LEGACY=false`
- Safe for production deployment

---

*Patch applied: November 29, 2025*
