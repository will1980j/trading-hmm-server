---
inclusion: always
---

# 📘 ROADMAP SYNCHRONIZATION PROTOCOL

**Last Updated:** 2025-12-28
**Purpose:** Single source of truth for system state and execution permissions

---

## 🎯 CORE EXECUTION RULE — FOCUS BEFORE EXPANSION

### System Architecture vs Execution Permission

**The system is architected to support:**
- Multi-symbol execution (NQ, ES, YM, RTY, CL, GC, etc.)
- Multi-timeframe analysis (1m, 5m, 15m, 1h, 4h, daily)
- Automated signal processing and portfolio intelligence

**However, expansion is explicitly PROHIBITED until roadmap-defined success criteria are met.**

### Priority Order (Non-Negotiable)

1. **Edge Validation** - Prove profitability on single symbol, single timeframe
2. **Funding** - Secure capital for live trading operations
3. **Operational Stability** - Demonstrate consistent execution without errors
4. **Expansion** - Only after above criteria are met and signed off

### Current Execution Scope (LOCKED)

**PERMITTED:**
- NQ (NASDAQ-100 E-mini) only
- 1-minute timeframe only
- Manual signal validation and entry
- Historical analysis and backtesting

**PROHIBITED:**
- Additional symbols (ES, YM, RTY, CL, GC, etc.)
- Additional timeframes (5m, 15m, 1h, 4h, daily)
- Automated signal execution
- Portfolio-level intelligence

**Expansion requires explicit Phase E completion and user sign-off.**

---

## ⚠️ CRITICAL: USER APPROVAL REQUIRED

**Module completion is SOLELY decided by the user based on:**
- Live market testing
- Real signal validation
- User's explicit approval

**Kiro will NEVER mark a module complete without explicit user confirmation.**

---

## 🏛️ ROADMAP GOVERNANCE RULES

### Single Source of Truth
- **The roadmap is the authoritative system state**
- All work must be reflected in roadmap updates
- No work is complete until roadmap is updated
- Roadmap status overrides all other documentation

### Phase Completion Requirements
1. **Verification Artifacts Required:**
   - Test results proving success criteria met
   - Documentation of implementation details
   - Locked decisions documented
   - Known limitations identified

2. **Sign-Off Process:**
   - User must explicitly approve phase completion
   - All success criteria must be met
   - Verification artifacts must be provided
   - Roadmap must be updated before moving to next phase

3. **Phase Dependencies:**
   - No work on Phase N+1 until Phase N is signed off
   - Locked decisions from completed phases cannot be violated
   - Later phases must respect earlier phase constraints

### Locked Decisions
- **Once a phase is complete, its core decisions are LOCKED**
- Later phases cannot change locked decisions without explicit approval
- Locked decisions must be documented in phase summary
- Violations of locked decisions require phase re-opening

---

## 🔄 SYNCHRONIZATION WORKFLOW

When user confirms a module is COMPLETE:

### 1. User says "Mark [module] complete"
### 2. Kiro updates `roadmap_state.py` (set `"done": True`)
### 3. Kiro updates `UNIFIED_ROADMAP.md` (mark ✅)
### 4. User deploys via GitHub Desktop
### 5. Homepage reflects changes automatically

---

## 🎯 CURRENT SESSION FOCUS

**Active Phase:** Phase E - NQ 1-Minute Edge Validation (IN PROGRESS)
**Execution Scope:** NQ only, 1-minute only, manual validation
**Blocking Issues:** None
**Next Phase:** Phase F - Expansion (LOCKED until Phase E criteria met)

---

## 📊 MARKET PARITY PROJECT STATUS

### Phase A — Deterministic Replay Foundation ✅ COMPLETE
**Objective:** Establish deterministic replay capability for historical market data

**Success Criteria Met:**
- ✅ Active dataset version tracking implemented
- ✅ Dataset version IDs backfilled for all bars
- ✅ Deterministic replay service operational
- ✅ Phase A gate verification passing

**Artifacts:**
- `database/run_phase_a_active_versions_migration.py`
- `scripts/backfill_dataset_version_ids.py`
- `services/deterministic_replay.py`
- `tests/verify_phase_a_gate.py`

**Locked Decisions:**
- Dataset versioning is mandatory for all historical data
- Active version tracking must be maintained
- Replay must be deterministic and reproducible

---

### Phase B — Indicator Parity Modules ✅ COMPLETE
**Objective:** Achieve exact parity between Pine Script indicator and Python modules

**Success Criteria Met:**
- ✅ Module 1 (Engulfing) - 100% parity
- ✅ Module 2 (GetBias FVG/IFVG) - 100% parity
- ✅ Module 3 (HTF Bias) - 100% parity
- ✅ Module 4 (HTF Alignment) - 100% parity
- ✅ Module 5 (Signal Generation) - 100% parity
- ✅ All unit tests passing

**Artifacts:**
- `market_parity/engulfing.py` + `tests/test_engulfing.py`
- `market_parity/get_bias_fvg_ifvg.py` + `tests/test_get_bias_fvg_ifvg.py`
- `market_parity/htf_bias.py` + `tests/test_htf_bias.py`
- `market_parity/htf_alignment.py` + `tests/test_htf_alignment.py`
- `market_parity/signal_generation.py` + `tests/test_signal_generation.py`
- `docs/PHASE_B_INDICATOR_PARITY_SPEC.md`
- `docs/PHASE_B_MODULES_1_2_3_COMPLETE.md`

**Locked Decisions:**
- Python modules must maintain exact parity with Pine Script
- No approximations or simplifications allowed
- All bias logic must match Pine get_bias() exactly
- Module interfaces are frozen (breaking changes require phase re-opening)

---

### Phase C — Triangle Backfill & Parity Testing ✅ COMPLETE
**Objective:** Generate historical triangle events from clean OHLCV data and achieve parity with TradingView

**Success Criteria Met:**
- ✅ Clean OHLCV overlay table created (`market_bars_ohlcv_1m_clean`)
- ✅ Data hygiene rules eliminate 2564x corruption (SMALL_RANGE_BIG_GAP_150, FLAT_DISCONTINUITY_50)
- ✅ Timestamp semantics fixed (clean table ts = bar OPEN time)
- ✅ Triangle backfill script operational with auto-detection of table type
- ✅ Parity achieved for TV 19:14-19:15 window (BEAR at 19:14, BULL at 19:15)
- ✅ Batch insert with automatic reconnection for large ingestion runs
- ✅ Databento continuous symbology mapping (GLBX.MDP3:NQ → NQ.v.0)

**Artifacts:**
- `database/phase_c_clean_ohlcv_overlay_schema.sql`
- `database/phase_c_triangle_events_schema.sql`
- `scripts/phase_c_backfill_triangles.py`
- `scripts/phase_c_reingest_clean_1m.py`
- `scripts/phase_c_verify_clean_data.py`
- `PHASE_C_PARITY_ACHIEVED.md`
- `PHASE_C_TIMESTAMP_SEMANTICS_FIX_COMPLETE.md`
- `PHASE_C_BATCH_INSERT_PATCH_COMPLETE.md`
- `SMALL_RANGE_BIG_GAP_HYGIENE_COMPLETE.md`

**Locked Decisions:**
- Clean table (`market_bars_ohlcv_1m_clean`) uses ts = bar OPEN time (TradingView convention)
- Legacy table (`market_bars_ohlcv_1m`) uses ts = bar CLOSE time (Databento convention)
- Triangle timestamps (`triangle_events_v1.ts`) = bar OPEN time (matches TradingView)
- Data hygiene rules: OHLC_INTEGRITY, PRICE_LT_1000, DISCONTINUITY_500, SMALL_RANGE_BIG_GAP_150, FLAT_DISCONTINUITY_50
- Databento continuous symbology: ROOT.ROLL_RULE.RANK (e.g., NQ.v.0)
- Batch insert size: 500 rows with automatic reconnection
- No median-based filtering (preserves legitimate price action)

**Known Limitations:**
- Requires Databento API key for clean data re-ingestion
- Clean table currently covers limited date range (2025-11-30 to 2025-12-02)
- Legacy table still contains corrupted data (not modified)

---

### Phase D.0 — Multi-Symbol Foundation Hardening ✅ COMPLETE
**Objective:** Add minimum scaffolding for multi-market scalability without future refactors

**Success Criteria Met:**
- ✅ Symbol registry created with 4 default symbols (NQ, ES, YM, RTY)
- ✅ Triangle source tracking added (source_table, logic_version columns)
- ✅ Clean-only policy enforced (legacy table requires --allow-legacy flag)
- ✅ Clean ingest run logging implemented
- ✅ All migrations executed successfully
- ✅ Backfill script updated and verified

**Artifacts:**
- `database/phase_d0_symbol_registry_schema.sql`
- `database/phase_d0_triangle_source_tracking.sql`
- `database/phase_d0_clean_ingest_runs_schema.sql`
- `database/run_phase_d0_symbol_registry_migration.py`
- `database/run_phase_d0_triangle_source_migration.py`
- `database/run_phase_d0_clean_ingest_migration.py`
- `PHASE_D0_MULTI_SYMBOL_FOUNDATION_COMPLETE.md`

**Locked Decisions:**
- Symbol registry schema is canonical for all symbols
- Triangle source tracking is mandatory for all new triangles
- Clean table is required by default (legacy requires explicit flag)
- Ingest run logging is automatic for all re-ingestion operations
- Git hash is preferred logic version (fallback to LOGIC_VERSION env var)

**Known Limitations:**
- Symbol registry requires manual INSERT for new symbols
- Source tracking columns are nullable (backward compatibility)
- Clean-only policy can be bypassed with --allow-legacy flag

---

### Phase D.1 — Symbol Registry Generalization ✅ COMPLETE
**Objective:** Make symbol_registry support any asset class without future schema changes

**Success Criteria Met:**
- ✅ Added 6 metadata columns (vendor_dataset, schema_name, venue, asset_class, timezone, session_profile)
- ✅ All columns nullable for backward compatibility
- ✅ Existing symbols updated with metadata (venue=CME, asset_class=equity_index)
- ✅ Reingest script uses generalized registry fields
- ✅ Safe defaults for missing metadata
- ✅ Future-proofing validated (can support CL, GC, 6E, BTC without schema changes)

**Artifacts:**
- `database/phase_d1_symbol_registry_generalization.sql`
- `database/run_phase_d1_symbol_registry_migration.py`
- `PHASE_D1_REGISTRY_GENERALIZATION_COMPLETE.md`

**Locked Decisions:**
- Metadata columns: vendor_dataset, schema_name, venue, asset_class, timezone, session_profile
- All metadata columns are TEXT and nullable
- COALESCE pattern for fallback (schema_name → schema, vendor_dataset → dataset)
- Metadata is optional (not required for ingestion)
- Column naming follows industry standards

**Known Limitations:**
- Metadata must be manually populated for new symbols
- Session profiles not yet implemented (placeholder for future)
- Timezone handling not yet integrated with session logic

---

### Phase D.2 — Robust Batch Insert & Historical Backfill ✅ COMPLETE
**Objective:** Enable large-scale historical backfill without database disconnects

**Success Criteria Met:**
- ✅ Replaced executemany with execute_values batch insert (10-50x faster)
- ✅ Batch size 500 events with commit per batch
- ✅ Automatic reconnection on OperationalError with 1 retry
- ✅ Progress reporting every 10 batches
- ✅ Simplified hygiene for clean table (OHLC_INTEGRITY + PRICE_LT_1000 only)
- ✅ Full hygiene retained for legacy table
- ✅ Verified: 0 bad bars skipped on clean table
- ✅ Verified: 178 triangles inserted successfully with 0 retries

**Artifacts:**
- `scripts/phase_c_backfill_triangles.py` (updated with batch insert + reconnection)
- `PHASE_D1_BACKFILL_BATCH_INSERT_COMPLETE.md`

**Locked Decisions:**
- Batch insert size: 500 events per batch
- Commit frequency: After each batch
- Reconnection strategy: Automatic with 1 retry per batch
- Clean table hygiene: OHLC_INTEGRITY + PRICE_LT_1000 only
- Legacy table hygiene: Full (DISCONTINUITY_500, SMALL_RANGE_BIG_GAP_150, FLAT_DISCONTINUITY_50)
- Progress reporting: Every 10 batches

**Known Limitations:**
- Max 1 retry per batch (may fail on persistent connection issues)
- No partial batch recovery (entire batch retried)
- Progress reporting granularity: 10 batches (5,000 events)

**Scope Note:** Complete for NQ (GLBX.MDP3:NQ); multi-symbol historical expansion deferred to Phase F.2

---

### Phase D.3 — Historical Serving Layer & Quality Gates ✅ COMPLETE

**Objective:** Define and implement canonical historical read-contract surfaces with quality gates

**Execution Scope:**
- Multi-symbol capable by design (symbol param required)
- Validated on NQ only
- Backend API only (no dashboards, no real-time, no ML)

**Success Criteria Met:**
- ✅ Historical API v1 endpoints implemented under /api/hist/v1/*
- ✅ World endpoint returns complete state at single timestamp
- ✅ Bars, bias, triangles, dataset endpoints operational
- ✅ Quality gates: coverage, alignment, determinism
- ✅ Contract tests implemented and passing
- ✅ Blueprint registered in web_server.py
- ✅ TradingView timestamp semantics enforced (ts = bar OPEN time)
- ✅ Safe server-side limits protect database

**Artifacts:**
- `api/historical_v1.py` - Complete API implementation with 8 endpoints
- `tests/test_historical_v1_api.py` - Contract tests (5 tests)
- `web_server.py` - Blueprint registration added

**Endpoints Implemented:**
- `GET /api/hist/v1/world` - Single timestamp world state (ohlcv + bias + triangles)
- `GET /api/hist/v1/bars` - OHLCV bars window (1m only)
- `GET /api/hist/v1/bias` - HTF bias series with forward-fill
- `GET /api/hist/v1/triangles/events` - Deterministic triangle events
- `GET /api/hist/v1/dataset` - Analytics-friendly joined rows
- `GET /api/hist/v1/quality/coverage` - Data coverage verification
- `GET /api/hist/v1/quality/alignment` - Timestamp alignment verification
- `GET /api/hist/v1/quality/determinism` - Deterministic hash verification

**Contract Tests:**
- ✅ World endpoint returns correct bias stack for known timestamp
- ✅ Dataset row count equals bars in window
- ✅ Determinism hash identical across repeated calls
- ✅ Alignment checks pass for known good range
- ✅ Coverage checks pass for known good range

**Locked Decisions:**
- All endpoints require symbol parameter (multi-symbol capable)
- Timestamps are RFC3339 format, UTC timezone
- ts = bar OPEN time (TradingView semantics)
- 1m alignment enforced with 409 error if misaligned
- Safe limits: bars/bias 50k max, triangles 10k max, dataset 50k max
- Dataset defaults to triangles_count (not full triangle payloads)
- Quality gates return pass boolean + detailed metrics
- No authentication required (read-only, internal use)

**Known Limitations:**
- Only 1m timeframe implemented (5m/15m/1h/4h/daily deferred)
- Contract tests require running server instance
- Quality gates are informational (no enforcement actions)

**Verification Commands:**
```bash
# Test world endpoint
curl "http://localhost:5000/api/hist/v1/world?symbol=GLBX.MDP3:NQ&ts=2025-12-02T00:14:00Z"

# Test quality coverage
curl "http://localhost:5000/api/hist/v1/quality/coverage?symbol=GLBX.MDP3:NQ&start=2025-12-02T00:10:00Z&end=2025-12-02T00:30:00Z"

# Run contract tests
python tests/test_historical_v1_api.py
```

---**Success Criteria:**
- [ ] `/api/hist/v1/world` - Single timestamp world state
- [ ] `/api/hist/v1/bars` - OHLCV bars window
- [ ] `/api/hist/v1/bias` - HTF bias timeline
- [ ] `/api/hist/v1/triangles/events` - Triangle events window
- [ ] `/api/hist/v1/dataset` - Analytics-friendly joined rows
- [ ] `/api/hist/v1/quality/coverage` - Data coverage validation
- [ ] `/api/hist/v1/quality/alignment` - Timestamp alignment validation
- [ ] `/api/hist/v1/quality/determinism` - Deterministic hash validation
- [ ] Contract tests pass for all endpoints
- [ ] Quality gates return pass=true for known good range

**Current Status:** IN PROGRESS

---

### Phase E — NQ 1-Minute Edge Validation 🔄 ACTIVE

**Objective:** Prove trading edge, consistency, and funding readiness on NQ 1-minute ONLY before any expansion

**Execution Scope (LOCKED):**
- Symbol: NQ (NASDAQ-100 E-mini) ONLY
- Timeframe: 1-minute ONLY
- Method: Manual signal validation and entry
- Analysis: Historical backtesting and live forward testing

**Prerequisites Completed:**
- ✅ HTF bias series persisted (`bias_series_1m_v1`) - COMPLETE
- ✅ Signal Contract V1 Wave 1 - COMPLETE

**Wave 1 Artifacts:**
- `database/signal_contract_v1_wave1_migration.sql` - Schema migration
- `database/run_signal_contract_v1_wave1_migration.py` - Migration runner
- `services/signal_contract_v1_mapper.py` - Field mapping logic
- `api/signals_debug_v1.py` - Debug endpoints
- `web_server.py` - Updated webhook handler with Wave 1 fields

**Wave 1 Verification:**
```bash
# Run migration
python database/run_signal_contract_v1_wave1_migration.py

# Run backfill for existing rows
python database/backfill_signal_contract_v1_wave1.py --limit 10000

# Test debug endpoints
curl "http://localhost:5000/api/signals/v1/debug/last?limit=5"
curl "http://localhost:5000/api/signals/v1/debug/trade/TRADE_ID_HERE"
```

**Wave 1 Backfill:** Completed for last 10,000 rows (symbol, status, timestamps, BE fields populated)

**Debug Endpoints Available:**
- `GET /api/signals/v1/debug/last?limit=20` - Last N events with Wave 1 fields
- `GET /api/signals/v1/debug/trade/{trade_id}` - Event timeline for specific trade
- `GET /api/signals/v1/all` - All signals (one row per trade_id, latest state)

**Example Usage:**
```bash
# All signals for NQ
curl "http://localhost:5000/api/signals/v1/all?symbol=GLBX.MDP3:NQ&limit=100"

# Filter by status
curl "http://localhost:5000/api/signals/v1/all?symbol=GLBX.MDP3:NQ&status=EXITED,CONFIRMED&limit=50"

# PowerShell
Invoke-RestMethod "http://localhost:5000/api/signals/v1/all?symbol=GLBX.MDP3:NQ&limit=10" | ConvertTo-Json -Depth 5
```

**Artifacts:**
- `database/phase_e_htf_bias_series_schema.sql`
- `database/run_phase_e_htf_bias_series_migration.py`
- `scripts/phase_e_backfill_bias_series.py`
- `scripts/phase_e_verify_bias_series_window.py`

**Verification Commands:**
```bash
# Backfill bias series
python scripts/phase_e_backfill_bias_series.py GLBX.MDP3:NQ 2025-12-02 2025-12-02 5

# Verify window
python scripts/phase_e_verify_bias_series_window.py GLBX.MDP3:NQ 2025-12-02T00:10:00Z 2025-12-02T00:30:00Z
```

**Explicitly Prohibited:**
- ❌ Adding ES, YM, RTY, or any other symbols
- ❌ Adding 5m, 15m, 1h, 4h, or daily timeframes
- ❌ Automated signal execution
- ❌ Portfolio-level intelligence
- ❌ ML/AI enhancements

**Current Status:** IN PROGRESS

### Phase E — Success Criteria (Required for Expansion)

**ALL criteria must be met before multi-symbol or multi-timeframe expansion is permitted.**

#### 1. Trading Performance (Objective & Verifiable)

- [ ] **Sustained Profitability:** Positive net P&L over minimum 3 consecutive months
- [ ] **Positive Expectancy:** Average profit per trade > 0 after all fees and slippage
- [ ] **Minimum Sample Size:** 100+ completed trades executed and recorded
- [ ] **Win Rate Target:** Achieved or exceeded predefined win rate threshold
- [ ] **R-Multiple Target:** Average R-multiple meets or exceeds strategy design
- [ ] **Drawdown Control:** Maximum drawdown stays within predefined acceptable limits
- [ ] **Recovery Demonstrated:** Recovered from at least one significant drawdown period

#### 2. Operational Stability (Objective & Verifiable)

- [ ] **Signal Parity Maintained:** Live TradingView signals match Python backfill 100%
- [ ] **Zero Data Integrity Issues:** No unresolved data corruption or backfill errors
- [ ] **Clean Table Coverage:** Full historical range available in `market_bars_ohlcv_1m_clean`
- [ ] **Triangle Accuracy:** All historical triangles verified against TradingView
- [ ] **Risk Rules Enforced:** Position sizing and risk limits applied without manual overrides
- [ ] **30-Day Stability:** Minimum 30 consecutive trading days without operational failures
- [ ] **Error-Free Execution:** No missed signals, no data gaps, no system crashes

#### 3. Capital Readiness (Objective & Verifiable)

- [ ] **Funded Account:** Prop firm account funded OR personal capital deployed (minimum $5,000)
- [ ] **Position Sizing Fixed:** Contract size and risk per trade clearly defined and repeatable
- [ ] **Risk Budget Defined:** Maximum daily loss, weekly loss, and monthly loss limits established
- [ ] **Capital Allocation Plan:** Clear plan for scaling capital as performance proves out
- [ ] **Fee Structure Understood:** All commissions, platform fees, and slippage accounted for

#### 4. Psychological & Execution Load (Subjective but Critical)

- [ ] **Strategy Executable:** Can execute signals without cognitive overload or decision paralysis
- [ ] **No Impulse to Expand:** No urge to add symbols or timeframes to "fix" performance
- [ ] **Stress Tested:** Strategy proven under high volatility, low volatility, and trending conditions
- [ ] **Confidence Established:** User confident in edge, execution, and risk management
- [ ] **Discipline Maintained:** Able to follow rules consistently without emotional overrides

### Phase E — Expansion Gate (Final Rule)

**Multi-symbol and multi-timeframe expansion is NOT permitted until:**
1. ALL Phase E success criteria are met
2. User explicitly approves: "Mark Phase E complete"
3. User explicitly unlocks expansion: "Unlock Phase F"

**Expansion without meeting ALL criteria is PROHIBITED.**

**Rationale:** Premature expansion dilutes focus, increases risk, and destroys edges. Prove profitability on one symbol/timeframe before scaling.

---

### Phase F.1 — Multi-Timeframe Expansion 🔒 LOCKED (Requires Phase E Sign-Off)

### Phase F.1 — Multi-Timeframe Expansion 🔒 LOCKED (Requires Phase E Sign-Off)

**Objective:** Expand to 5m, 15m, 1h, 4h, daily timeframes on NQ

**Prerequisites:**
- ✅ Phase E must be complete and signed off
- ⏳ All Phase E success criteria met
- ⏳ User explicit approval: "Unlock Phase F.1"

**Scope:** NQ only, multiple timeframes

**Status:** LOCKED - No work permitted until Phase E complete

---

### Phase F.2 — Multi-Symbol Expansion 🔒 LOCKED (Requires Phase F.1 Sign-Off)

**Objective:** Expand to ES, YM, RTY symbols on 1-minute timeframe

**Prerequisites:**
- ✅ Phase F.1 must be complete and signed off
- ⏳ Multi-timeframe proven on NQ
- ⏳ User explicit approval: "Unlock Phase F.2"

**Scope:** Multiple symbols, 1-minute only initially

**Status:** LOCKED - No work permitted until Phase F.1 complete

---

### Phase G — Automation & Portfolio Intelligence 🔒 LOCKED (Requires Phase F.2 Sign-Off)

**Objective:** Automated signal execution and portfolio-level intelligence

**Prerequisites:**
- ✅ Phase F.2 must be complete and signed off
- ⏳ Multi-symbol proven
- ⏳ Capital allocated for automation
- ⏳ User explicit approval: "Unlock Phase G"

**Scope:** Automation, portfolio management, advanced intelligence

**Status:** LOCKED - No work permitted until Phase F.2 complete

---

## 📊 LEVEL 1 COMPLETION (from roadmap_state.py)

### H1.1 — Core Platform Foundation ✅ COMPLETE (7/7 modules)
- `h1_1_homepage_command_center` ✅
- `h1_1_automated_signals_engine` ✅
- `h1_1_automated_signals_dashboard` ✅
- `h1_1_realtime_event_processor` ✅
- `h1_1_automated_signals_storage` ✅
- `h1_1_webhook_pipeline` ✅
- `h1_1_data_integrity_checker` ✅

### H1.2 — Main Dashboard ✅ COMPLETE
- `h1_2_main_dashboard` ✅

### H1.3 — Time Analysis ✅ COMPLETE
- `h1_3_time_analysis` ✅

### H1.4 — Automated Signals Dashboard Redesign ⏳ PLANNED
- `h1_4_automated_signals_dashboard_redesign` ❌

### H1.5 — Financial Summary ⏳ PLANNED
- `h1_5_financial_summary` ❌

### H1.6 — Reporting Center ⏳ PLANNED
- `h1_6_reporting_center` ❌

### H1.7 — Database Foundation ⏳ PLANNED
- `h1_7_database_foundation` ❌

---

## 🔧 RECENT CHANGES LOG

### 2025-12-28
- **Phase D.3 - Historical Serving Layer & Quality Gates COMPLETE**
  - Implemented 8 REST endpoints under /api/hist/v1/*
  - World, bars, bias, triangles, dataset endpoints operational
  - Quality gates: coverage, alignment, determinism
  - Contract tests implemented (5 tests)
  - Multi-symbol capable, NQ verified
  - TradingView timestamp semantics enforced
  - Status: ✅ Complete, awaiting user sign-off

- **Phase D.2 - Robust Batch Insert & Historical Backfill COMPLETE**
  - Replaced executemany with execute_values (10-50x faster)
  - Batch size 500 with commit per batch
  - Automatic reconnection with 1 retry per batch
  - Simplified hygiene for clean table (0 bad bars skipped)
  - Progress reporting every 10 batches
  - Verified: 178 triangles, 0 retries, <1 second
  - Status: ✅ Complete, awaiting user sign-off

- **Phase D.1 - Symbol Registry Generalization COMPLETE**
  - Added 6 metadata columns (vendor_dataset, schema_name, venue, asset_class, timezone, session_profile)
  - All columns nullable for backward compatibility
  - Existing symbols updated with CME/equity_index metadata
  - Reingest script uses generalized registry
  - Future-proofing validated (CL, GC, 6E, BTC ready)
  - Status: ✅ Complete, awaiting user sign-off

- **Phase D.0 - Multi-Symbol Foundation Hardening COMPLETE**
  - Symbol registry created with 4 default symbols
  - Triangle source tracking added (source_table, logic_version)
  - Clean-only policy enforced (legacy requires --allow-legacy)
  - Clean ingest run logging implemented
  - All migrations executed and verified
  - Status: ✅ Complete, awaiting user sign-off

- **Phase C - Triangle Backfill & Parity Testing COMPLETE**
  - Clean OHLCV overlay table created with validation
  - Data hygiene rules eliminate 2564x corruption
  - Timestamp semantics fixed (clean table ts = bar OPEN time)
  - Parity achieved: TV 19:14 BEAR, TV 19:15 BULL
  - Batch insert with automatic reconnection implemented
  - Databento continuous symbology mapping fixed
  - Status: ✅ Complete, awaiting user sign-off

### 2025-11-30
- **EXIT_BE 500 Error - ROOT CAUSE FOUND & FIXED**
  - File: `web_server.py`
  - **Root Cause:** `handle_mfe_update` was doing `SET event_type = 'MFE_UPDATE'` which overwrote the original `'ENTRY'` event_type. Lifecycle validation then couldn't find `'ENTRY'` in history.
  - **Fix 1:** Removed `event_type = 'MFE_UPDATE'` from the UPDATE statement - now preserves original `'ENTRY'`
  - **Fix 2:** Added lifecycle validation to `handle_be_trigger` function
  - Status: ✅ Fixed locally, needs deploy

---

## 🚀 DEPLOYMENT QUEUE

### Phase D.2 Artifacts (Ready for Sign-Off)
1. ✅ Batch insert with execute_values (500 events/batch)
2. ✅ Automatic reconnection with retry logic
3. ✅ Simplified hygiene for clean table
4. ✅ Progress reporting every 10 batches

### Phase D.1 Artifacts (Ready for Sign-Off)
1. ✅ Symbol registry generalized with 6 metadata columns
2. ✅ Backward compatibility maintained (all nullable)
3. ✅ Existing symbols updated with metadata
4. ✅ Reingest script uses generalized fields

### Phase D.0 Artifacts (Ready for Sign-Off)
1. ✅ Symbol registry with 4 default symbols
2. ✅ Triangle source tracking (source_table, logic_version)
3. ✅ Clean-only policy enforcement
4. ✅ Clean ingest run logging

### Phase C Artifacts (Ready for Sign-Off)
1. ✅ Clean OHLCV overlay infrastructure
2. ✅ Triangle backfill with parity verification
3. ✅ Data hygiene rules (2564x corruption eliminated)
4. ✅ Timestamp semantics fix (bar OPEN time alignment)
5. ✅ Batch insert with reconnection (robust large-scale ingestion)

### Automated Signals Fixes (Previous Work)
1. ✅ MFE_UPDATE event_type preservation fix in `web_server.py` - READY TO DEPLOY
2. ✅ BE_TRIGGERED lifecycle validation added - READY TO DEPLOY

---

## 📁 KEY FILES FOR ROADMAP SYNC

| Purpose | File |
|---------|------|
| **Master Data** | `roadmap_state.py` |
| **Documentation** | `UNIFIED_ROADMAP.md` |
| **Homepage Template** | `templates/homepage_video_background.html` |
| **Homepage JS** | `static/js/homepage.js` |
| **Homepage CSS** | `static/css/homepage.css` |

---

## 🚨🚨🚨 CRITICAL: AUTOMATED SIGNALS DASHBOARD FILES 🚨🚨🚨

**The `/automated-signals` route serves `automated_signals_ultra.html`, NOT `automated_signals_dashboard.html`!**

| What to Edit | Correct File |
|--------------|--------------|
| **Template** | `templates/automated_signals_ultra.html` |
| **JavaScript** | `static/js/automated_signals_ultra.js` |
| **CSS** | `static/css/automated_signals_ultra.css` |

**🚫 WRONG FILE:** `templates/automated_signals_dashboard.html` - NOT SERVED BY ANY ROUTE

**ALWAYS check `web_server.py` to verify which template a route serves before editing!**

---

## 🔗 MODULE COMPLETION CHECKLIST

When marking a module complete, verify:
- [ ] `roadmap_state.py` has `"done": True`
- [ ] `UNIFIED_ROADMAP.md` shows ✅ COMPLETE
- [ ] Code is committed and pushed
- [ ] Railway deployment succeeded
- [ ] Homepage shows updated progress %
