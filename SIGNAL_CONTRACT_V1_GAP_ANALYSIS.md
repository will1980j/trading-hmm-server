# Signal Contract V1 → Current System Gap Analysis

**Date:** 2025-12-28  
**Purpose:** Identify gaps between Signal Contract V1 requirements and current storage

---

## A. Current Storage Map

### Table 1: `triangle_events_v1` (Phase C - Historical Triangles)
**Purpose:** Historical triangle signals from backfill (candidate signals only)

**Columns:**
- `id` (BIGSERIAL PRIMARY KEY)
- `symbol` (TEXT) - Symbol identifier
- `ts` (TIMESTAMPTZ) - Bar OPEN time when triangle appeared
- `direction` (TEXT) - 'BULL' or 'BEAR'
- `bias_1m`, `bias_m5`, `bias_m15`, `bias_h1`, `bias_h4`, `bias_d1` (TEXT) - Bias context
- `htf_bullish`, `htf_bearish` (BOOLEAN) - HTF alignment flags
- `require_engulfing`, `require_sweep_engulfing`, `htf_aligned_only` (BOOLEAN) - Filter settings
- `source_table`, `logic_version` (TEXT) - Provenance tracking
- `created_at` (TIMESTAMPTZ)

**Represents:** Candidate signals (triangles) - NOT confirmed trades

### Table 2: `automated_signals` (Live Event Stream)
**Purpose:** Event-sourced storage for live TradingView webhook events

**Columns:**
- `id` (SERIAL PRIMARY KEY)
- `event_type` (VARCHAR(20)) - ENTRY, MFE_UPDATE, BE_TRIGGERED, EXIT_SL, EXIT_BE, etc.
- `trade_id` (VARCHAR(100)) - Trade identifier
- `direction` (VARCHAR(10)) - Direction
- `entry_price`, `stop_loss`, `risk_distance` (DECIMAL)
- `target_1r` through `target_20r` (DECIMAL) - R-multiple targets
- `current_price`, `mfe`, `exit_price`, `final_mfe` (DECIMAL)
- `session`, `bias` (VARCHAR)
- `account_size`, `risk_percent`, `contracts`, `risk_amount` (DECIMAL/INTEGER)
- `timestamp` (BIGINT) - Milliseconds timestamp
- `created_at` (TIMESTAMP)

**Represents:** Live trade events (real-time only, not historical)

### Table 3: `confirmed_signals_ledger` (Indicator Export)
**Purpose:** Canonical confirmed signals from indicator bulk export

**Columns:**
- `trade_id` (TEXT PRIMARY KEY) - Triangle-canonical ID
- `triangle_time_ms` (BIGINT) - Triangle timestamp (milliseconds)
- `confirmation_time_ms` (BIGINT) - Confirmation timestamp
- `date` (DATE), `session` (TEXT), `direction` (TEXT)
- `entry`, `stop` (NUMERIC) - Entry and stop prices
- `be_mfe`, `no_be_mfe`, `mae` (NUMERIC) - MFE/MAE metrics
- `completed` (BOOLEAN) - Trade completion status
- `last_seen_batch_id` (BIGINT), `updated_at` (TIMESTAMPTZ)

**Represents:** Confirmed signals with MFE tracking (from indicator export)

### Table 4: `all_signals_ledger` (Indicator Export)
**Purpose:** All triangles including pending/cancelled

**Columns:**
- `trade_id` (TEXT PRIMARY KEY)
- `triangle_time_ms` (BIGINT), `confirmation_time_ms` (BIGINT)
- `direction` (TEXT), `status` (TEXT) - PENDING/CONFIRMED/CANCELLED/COMPLETED
- `bars_to_confirm` (INTEGER)
- `session` (TEXT)
- `entry_price`, `stop_loss`, `risk_points` (NUMERIC)
- `htf_daily`, `htf_4h`, `htf_1h`, `htf_15m`, `htf_5m`, `htf_1m` (TEXT) - HTF bias context
- `last_seen_batch_id` (BIGINT), `updated_at` (TIMESTAMPTZ)

**Represents:** All signals with state tracking

### Table 5: `bias_series_1m_v1` (Phase E - HTF Bias Timeline)
**Purpose:** HTF bias values at every 1m timestamp

**Columns:**
- `symbol` (TEXT), `ts` (TIMESTAMPTZ) - 1m bar OPEN time
- `bias_1m`, `bias_5m`, `bias_15m`, `bias_1h`, `bias_4h`, `bias_1d` (TEXT)
- `source_table`, `logic_version` (TEXT)
- `created_at` (TIMESTAMPTZ)

**Represents:** Bias context timeline (not signal-specific)

---

## B. Field-by-Field Gap Matrix

| Contract Field | Current Source | Status | Notes | Fix Type |
|----------------|----------------|--------|-------|----------|
| **IDENTITY** |
| trade_id | automated_signals.trade_id | EXISTS | Format matches | - |
| symbol | triangle_events_v1.symbol | PARTIAL | Not in automated_signals | ADD COLUMN |
| direction | automated_signals.direction | EXISTS | Naming: "LONG"/"SHORT" vs "Bullish"/"Bearish" | RENAME/MAP |
| logic_version | triangle_events_v1.logic_version | PARTIAL | Not in automated_signals | ADD COLUMN |
| source | triangle_events_v1.source_table | PARTIAL | Not in automated_signals | ADD COLUMN |
| **TIMESTAMPS (BOTH OPEN & CLOSE)** |
| signal_bar_open_ts | triangle_events_v1.ts | EXISTS | ts = bar OPEN time | - |
| signal_bar_close_ts | - | MISSING | Not stored | DERIVE (ts + 1min) |
| confirmation_bar_open_ts | all_signals_ledger.confirmation_time_ms | PARTIAL | Milliseconds, semantics unclear | CHANGE SEMANTICS |
| confirmation_bar_close_ts | - | MISSING | Not stored | DERIVE or ADD |
| entry_bar_open_ts | - | MISSING | Not stored | ADD COLUMN |
| entry_bar_close_ts | - | MISSING | Not stored | DERIVE (entry_open + 1min) |
| exit_bar_open_ts | - | MISSING | Not stored | ADD COLUMN |
| exit_bar_close_ts | - | MISSING | Not stored | DERIVE (exit_open + 1min) |
| **SIGNAL CANDLE** |
| signal_candle_high | - | MISSING | Not stored | ADD COLUMN |
| signal_candle_low | - | MISSING | Not stored | ADD COLUMN |
| **STATE** |
| status | all_signals_ledger.status | EXISTS | PENDING/CONFIRMED/CANCELLED/COMPLETED | - |
| cancel_bar_open_ts | - | MISSING | Not stored | ADD COLUMN |
| cancel_reason | - | MISSING | Not stored | ADD COLUMN |
| **STOP + RISK** |
| stop_loss_price | automated_signals.stop_loss | EXISTS | - | - |
| buffer_points | - | MISSING | Not stored (hardcoded 0.25) | ADD COLUMN |
| risk_distance | automated_signals.risk_distance | EXISTS | - | - |
| contract_size | automated_signals.contracts | EXISTS | - | - |
| risk_percent | automated_signals.risk_percent | EXISTS | - | - |
| account_size | automated_signals.account_size | EXISTS | - | - |
| stop_anchor_type | - | MISSING | Not stored (pivot/bearish/etc) | ADD COLUMN |
| stop_anchor_bar_open_ts | - | MISSING | Not stored | ADD COLUMN |
| stop_anchor_price_raw | - | MISSING | Not stored | ADD COLUMN |
| **BIAS CONTEXT AT SIGNAL** |
| bias_1m | triangle_events_v1.bias_1m | EXISTS | At triangle time | - |
| bias_5m | triangle_events_v1.bias_m5 | EXISTS | At triangle time | - |
| bias_15m | triangle_events_v1.bias_m15 | EXISTS | At triangle time | - |
| bias_60m | triangle_events_v1.bias_h1 | EXISTS | Column name mismatch | RENAME/MAP |
| bias_240m | triangle_events_v1.bias_h4 | EXISTS | Column name mismatch | RENAME/MAP |
| bias_1d | triangle_events_v1.bias_d1 | EXISTS | At triangle time | - |
| htf_bullish | triangle_events_v1.htf_bullish | EXISTS | - | - |
| htf_bearish | triangle_events_v1.htf_bearish | EXISTS | - | - |
| session | automated_signals.session | PARTIAL | Not in triangle_events_v1 | ADD COLUMN |
| **BREAKEVEN** |
| be_enabled | - | MISSING | Not stored (assumed true) | ADD COLUMN |
| be_trigger_R | - | MISSING | Not stored (hardcoded 1.0) | ADD COLUMN |
| be_offset_points | - | MISSING | Not stored (hardcoded 0.0) | ADD COLUMN |
| be_triggered | - | PARTIAL | Inferred from BE_TRIGGERED event | ADD COLUMN |
| be_trigger_bar_open_ts | - | MISSING | Not stored | ADD COLUMN |
| be_trigger_bar_close_ts | - | MISSING | Not stored | DERIVE |
| **METRICS** |
| highest_high | - | MISSING | Not stored (only MFE result) | ADD COLUMN |
| lowest_low | - | MISSING | Not stored (only MFE result) | ADD COLUMN |
| mae_R | confirmed_signals_ledger.mae | EXISTS | - | - |
| mfe_no_be_R | confirmed_signals_ledger.no_be_mfe | EXISTS | - | - |
| mfe_be_R | confirmed_signals_ledger.be_mfe | EXISTS | - | - |
| **EXIT** |
| exit_price | automated_signals.exit_price | EXISTS | - | - |
| exit_reason | - | PARTIAL | Inferred from event_type | ADD COLUMN |
| duration_bars | - | MISSING | Not stored | DERIVE |
| **EVENT MODEL** |
| SIGNAL_CREATED | automated_signals.event_type | EXISTS | - | - |
| CONFIRMED | - | MISSING | No explicit event | ADD EVENT |
| ENTRY | automated_signals.event_type | EXISTS | - | - |
| MFE_UPDATE | automated_signals.event_type | EXISTS | - | - |
| BE_TRIGGERED | automated_signals.event_type | EXISTS | - | - |
| EXIT_SL/EXIT_BE | automated_signals.event_type | EXISTS | - | - |
| CANCELLED | - | MISSING | No explicit event | ADD EVENT |

---

## C. High-Risk Mismatches (Top 5)

### 1. Timestamp Semantics Ambiguity (CRITICAL)

**Issue:** Multiple timestamp representations with unclear semantics

**Current State:**
- `triangle_events_v1.ts` = bar OPEN time (documented)
- `automated_signals.timestamp` = milliseconds (semantics unclear - open? close? event time?)
- `all_signals_ledger.triangle_time_ms` = milliseconds (semantics unclear)
- `all_signals_ledger.confirmation_time_ms` = milliseconds (semantics unclear)

**Contract Requirement:** Store BOTH bar_open_ts AND bar_close_ts for signal, confirmation, entry, exit

**Risk:** Cannot deterministically reconstruct which bar's OHLC to use for calculations

**Fix:** Add explicit _bar_open_ts and _bar_close_ts columns, document semantics

### 2. Entry Price Update Timing (CRITICAL)

**Issue:** No storage of entry_bar_open_ts or tracking of when entry_price was updated from temporary to actual

**Current State:**
- `automated_signals.entry_price` exists but no timestamp
- Cannot verify if entry_price = confirmation close (temporary) or entry bar open (actual)

**Contract Requirement:** entry_bar_open_ts must be stored to know when actual entry occurred

**Risk:** Cannot reproduce entry timing, cannot verify MFE tracking start point

**Fix:** Add entry_bar_open_ts column, ensure entry_price update is tracked

### 3. Stop Provenance Missing (HIGH)

**Issue:** Stop loss price stored but no provenance (how it was calculated)

**Current State:**
- `automated_signals.stop_loss` exists
- No stop_anchor_type, stop_anchor_bar_open_ts, stop_anchor_price_raw
- Cannot reproduce stop calculation

**Contract Requirement:** Must store stop anchor details to reproduce stop placement

**Risk:** Cannot verify stop methodology compliance, cannot debug stop calculation errors

**Fix:** Add stop_anchor_type, stop_anchor_bar_open_ts, stop_anchor_price_raw columns

### 4. BE Trigger Ordering Ambiguity (HIGH)

**Issue:** BE_TRIGGERED event exists but no bar-level timestamps

**Current State:**
- BE_TRIGGERED event in automated_signals
- No be_trigger_bar_open_ts or be_trigger_bar_close_ts
- Cannot verify intrabar ordering (BE trigger before stop check)

**Contract Requirement:** be_trigger_bar_open_ts and be_trigger_bar_close_ts must be stored

**Risk:** Cannot verify BE trigger happened before stop hit on same bar

**Fix:** Add be_trigger_bar_open_ts, be_trigger_bar_close_ts columns

### 5. Extreme Tracking on Stop Bar (HIGH)

**Issue:** No storage of highest_high/lowest_low, cannot verify stop-bar extreme rule

**Current State:**
- Only MFE result stored (mfe_no_be, mfe_be)
- No highest_high or lowest_low stored
- Cannot verify extremes were NOT updated on stop bar

**Contract Requirement:** highest_high/lowest_low must be stored to verify extreme tracking

**Risk:** Cannot detect inflated MFE from stop bar extreme updates

**Fix:** Add highest_high, lowest_low columns

---

## D. Minimum Patch List (Ordered by Dependency)

### Patch 1: Timestamp Semantics Clarification (FOUNDATION)

**Target Tables:** automated_signals, all_signals_ledger, confirmed_signals_ledger

**Changes:**
1. Add columns with explicit semantics:
   - `signal_bar_open_ts` (TIMESTAMPTZ)
   - `confirmation_bar_open_ts` (TIMESTAMPTZ)
   - `entry_bar_open_ts` (TIMESTAMPTZ)
   - `exit_bar_open_ts` (TIMESTAMPTZ)

2. Document existing timestamp columns:
   - `automated_signals.timestamp` → Clarify if bar open/close/event time
   - `triangle_events_v1.ts` → Already documented as bar OPEN time

3. Add derivable close timestamps (computed columns or views):
   - `*_bar_close_ts` = `*_bar_open_ts` + INTERVAL '1 minute'

**Rationale:** Foundation for all other fixes - must know which bar's OHLC to use

### Patch 2: Signal Candle OHLC Storage (REQUIRED FOR CONFIRMATION)

**Target Tables:** automated_signals, all_signals_ledger

**Changes:**
1. Add columns:
   - `signal_candle_high` (NUMERIC)
   - `signal_candle_low` (NUMERIC)
   - `signal_candle_open` (NUMERIC) - Optional but useful
   - `signal_candle_close` (NUMERIC) - Optional but useful

**Rationale:** Required to verify confirmation logic (close > signal_candle_high for bullish)

### Patch 3: Stop Provenance Storage (REQUIRED FOR REPRODUCIBILITY)

**Target Tables:** automated_signals, confirmed_signals_ledger

**Changes:**
1. Add columns:
   - `stop_anchor_type` (TEXT) - 'PIVOT_3C', 'PIVOT_4C', 'BEARISH_CANDLE', 'SIGNAL_CANDLE'
   - `stop_anchor_bar_open_ts` (TIMESTAMPTZ) - Which bar's low/high was used
   - `stop_anchor_price_raw` (NUMERIC) - Raw pivot/candle price before buffer
   - `buffer_points` (NUMERIC) - Buffer applied (default 0.25)

**Rationale:** Required to reproduce stop calculation and verify methodology compliance

### Patch 4: Breakeven Tracking Enhancement (REQUIRED FOR DUAL MFE)

**Target Tables:** automated_signals

**Changes:**
1. Add columns:
   - `be_enabled` (BOOLEAN) - Whether BE strategy is active
   - `be_trigger_R` (NUMERIC) - R-multiple for BE trigger (default 1.0)
   - `be_offset_points` (NUMERIC) - BE offset from entry (default 0.0)
   - `be_triggered` (BOOLEAN) - Whether BE was triggered
   - `be_trigger_bar_open_ts` (TIMESTAMPTZ) - When BE triggered

2. Ensure BE_TRIGGERED event includes bar timestamps

**Rationale:** Required to verify BE trigger timing and intrabar ordering

### Patch 5: Extreme Tracking Storage (REQUIRED FOR MFE VERIFICATION)

**Target Tables:** automated_signals

**Changes:**
1. Add columns:
   - `highest_high` (NUMERIC) - For bullish trades
   - `lowest_low` (NUMERIC) - For bearish trades
   - `extremes_last_updated_bar_open_ts` (TIMESTAMPTZ) - Last update timestamp

2. Ensure MFE_UPDATE events include extremes

**Rationale:** Required to verify stop-bar extreme rule and MFE calculation

### Patch 6: State and Cancellation Tracking (REQUIRED FOR LIFECYCLE)

**Target Tables:** automated_signals, all_signals_ledger

**Changes:**
1. Add columns:
   - `status` (TEXT) - PENDING/CONFIRMED/CANCELLED/EXITED
   - `cancel_bar_open_ts` (TIMESTAMPTZ) - When cancelled
   - `cancel_reason` (TEXT) - Why cancelled

2. Add CANCELLED event type to automated_signals

**Rationale:** Required for complete lifecycle tracking

### Patch 7: Duration and Exit Reason (REQUIRED FOR ANALYSIS)

**Target Tables:** automated_signals

**Changes:**
1. Add columns:
   - `exit_reason` (TEXT) - EXIT_SL, EXIT_BE, EXIT_TP
   - `duration_bars` (INTEGER) - Entry to exit in bars

2. Ensure EXIT events include exit_reason explicitly

**Rationale:** Required for exit analysis and strategy comparison

---

## E. Summary Statistics

**Total Contract Fields:** 60+  
**Currently Exist:** ~25 (42%)  
**Partially Exist:** ~10 (17%)  
**Missing:** ~25 (42%)

**Critical Gaps:** 5 high-risk mismatches identified  
**Minimum Patches:** 7 ordered patches required

**Estimated Effort:**
- Patch 1-3: High priority, ~3-5 hours
- Patch 4-5: Medium priority, ~2-3 hours
- Patch 6-7: Low priority, ~1-2 hours

**Total:** ~6-10 hours of focused implementation

---

## F. Recommendations

### Immediate (Phase E Prerequisite)

1. **Implement Patch 1** - Timestamp semantics clarification
2. **Implement Patch 2** - Signal candle OHLC storage
3. **Implement Patch 5** - Extreme tracking storage

**Rationale:** These are required to verify current MFE calculations match indicator

### Short-Term (Phase E Enhancement)

1. **Implement Patch 3** - Stop provenance
2. **Implement Patch 4** - BE tracking enhancement

**Rationale:** Required for full reproducibility and debugging

### Medium-Term (Phase F Preparation)

1. **Implement Patch 6** - State and cancellation
2. **Implement Patch 7** - Duration and exit reason

**Rationale:** Required for complete lifecycle analysis

---

## G. Migration Strategy

### Option A: Extend Existing Tables (Recommended)

**Approach:** Add missing columns to automated_signals and related tables

**Pros:**
- Preserves existing data
- Backward compatible
- Incremental migration

**Cons:**
- Wide tables (60+ columns)
- Some columns nullable for old data

### Option B: New Unified Table

**Approach:** Create signal_lifecycle_v1 table with all contract fields

**Pros:**
- Clean schema
- All fields present
- Clear semantics

**Cons:**
- Requires data migration
- Breaking change
- Duplicate storage

**Recommendation:** Option A (extend existing) for Phase E, consider Option B for Phase F

---

**Status:** Gap analysis complete - 7 patches required for full Signal Contract V1 compliance
