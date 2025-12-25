# Homepage Roadmap: Before vs After Comparison

## 📊 Visual Comparison

### BEFORE (TradingView-First)
```
┌─────────────────────────────────────────────────────────────┐
│ Phase 0: Databento Foundation (Phase 1A) ✅ COMPLETE        │
│ Description: Source of truth: Databento OHLCV-1m...         │
│ (5 modules • 100%)                                           │
│                                                              │
│ ✅ Databento dataset downloaded (MNQ OHLCV-1m)              │
│ ✅ DB schema migrated (market_bars_ohlcv_1m + ...)          │
│ ✅ Ingestion complete (2019–2025) — 2.34M bars              │
│ ✅ Stats endpoint live (/api/market-data/mnq/...)           │
│ ✅ Optional backfill: 2010–2019                             │  ← WRONG!
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Indicator Parity (Phase 1B) ⬜ PLANNED             │
│ (3 modules • 0%)                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Phase 5: Legacy / Optional (TradingView Alerts) ✅ COMPLETE │
│ (3 modules • 100%)                                           │
└─────────────────────────────────────────────────────────────┘
```

**Issues:**
- ❌ Phase 0 marked 100% complete but backfill is optional (not done)
- ❌ No live Databento stats displayed
- ❌ Template looking for phase_id '0.5' (doesn't exist)
- ❌ No clear distinction between core and legacy systems

---

### AFTER (Databento-First) ✅
```
┌─────────────────────────────────────────────────────────────┐
│ Phase 0: Databento Foundation (Phase 0–1A) ✅ 4/5 COMPLETE  │
│ Description: Source of truth: Databento OHLCV-1m.           │
│              TradingView: charting only.                     │
│ (5 modules • 80%)                                            │
│                                                              │
│ ✅ Databento dataset downloaded (MNQ OHLCV-1m)              │
│ ✅ DB schema migrated (market_bars_ohlcv_1m + ...)          │
│ ✅ Ingestion complete (2019–2025) — 2.34M bars (2338262)    │
│ ✅ Stats endpoint live (/api/market-data/mnq/...)           │
│ ⬜ Optional backfill: 2010–2019                             │  ← CORRECT!
│                                                              │
│ 📊 Live Dataset Stats                                        │
│ Bars: 2,338,262                                              │
│ Range: 2019-05-05 → 2025-12-22                              │
│ Latest: 2025-12-22 16:00 @ $25,930.50                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Indicator Parity (Phase 1B) ⬜ 0/3 PLANNED         │
│ (3 modules • 0%)                                             │
│                                                              │
│ ⬜ Python signal engine reproduces Pine outputs on 1m bars  │
│ ⬜ Bar-by-bar parity tests pass                             │
│ ⬜ Parity report visible on dashboard/homepage              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Phase 2: Strategy Discovery (Phase 2) ⬜ 0/2 PLANNED        │
│ (2 modules • 0%)                                             │
│                                                              │
│ ⬜ Feature store + labeling (MFE/MAE, sessions, regimes)    │
│ ⬜ Candidate strategy selection pipeline                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Phase 3: Dashboards (Phase 2–3) ⬜ 0/3 PLANNED              │
│ (3 modules • 0%)                                             │
│                                                              │
│ ⬜ Automated Signals Dashboard re-based on Databento        │
│ ⬜ Trades / MFE / MAE dashboards re-based on Databento      │
│ ⬜ Data Quality dashboard updated for Databento pipeline    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Phase 4: Automation & Execution (later) ⬜ 0/3 PLANNED      │
│ (3 modules • 0%)                                             │
│                                                              │
│ ⬜ Live bars ingestion (Databento live) using same schema   │
│ ⬜ Execution router + prop firm scaling                     │
│ ⬜ Copy trading framework                                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Phase 5: Legacy / Optional (TradingView Alerts)             │
│          ✅ 3/3 COMPLETE (DEPRECATED)                       │
│ (3 modules • 100%)                                           │
│                                                              │
│ ✅ TradingView webhook ingestion (legacy - optional)        │
│ ✅ Hybrid Signal Synchronization System (legacy - optional) │
│ ✅ Automated Signals Dashboard (legacy TradingView alerts)  │
└─────────────────────────────────────────────────────────────┘
```

**Improvements:**
- ✅ Phase 0 correctly shows 4/5 (80%) - backfill is optional
- ✅ Live Databento stats displayed with real data
- ✅ Template correctly references phase_id '0'
- ✅ Clear "Source of truth" banner
- ✅ TradingView marked as "Legacy/Optional (DEPRECATED)"
- ✅ All future phases clearly marked as PLANNED
- ✅ Explicit module counts and percentages

---

## 🔄 Architectural Shift

### Data Flow: BEFORE
```
TradingView Indicator
        ↓ (webhook)
   Automated Signals API
        ↓ (insert)
   automated_signals table
        ↓ (query)
   Dashboard Display
```
**Status:** ✅ Complete (marked as core system)

### Data Flow: AFTER
```
Databento OHLCV-1m Dataset (2019-2025)
        ↓ (ingestion)
   market_bars_ohlcv_1m table
        ↓ (query)
   Python Signal Engine (Phase 1B - PLANNED)
        ↓ (processing)
   Feature Store (Phase 2 - PLANNED)
        ↓ (analysis)
   Dashboards (Phase 3 - PLANNED)
```
**Status:** Phase 0 complete, Phases 1-3 planned

**TradingView:** Moved to Phase 5 (Legacy/Optional) - kept for charting only

---

## 📈 Completion Status Changes

| Phase | Before | After | Change |
|-------|--------|-------|--------|
| Phase 0 | 5/5 (100%) | 4/5 (80%) | ✅ Corrected (backfill optional) |
| Phase 1 | 0/3 (0%) | 0/3 (0%) | No change |
| Phase 2 | 0/2 (0%) | 0/2 (0%) | No change |
| Phase 3 | N/A | 0/3 (0%) | ✅ Added (dashboard rebase) |
| Phase 4 | N/A | 0/3 (0%) | ✅ Added (automation) |
| Phase 5 | 3/3 (100%) | 3/3 (100%) | ✅ Marked DEPRECATED |

---

## 🎯 Key Messaging Changes

### Phase 0 Description
**Before:** "Source of truth: Databento OHLCV-1m. TradingView: charting only."  
**After:** "Source of truth: Databento OHLCV-1m. TradingView: charting only."  
*(Same, but now with live stats to prove it)*

### Phase 5 Description
**Before:** "TradingView alert/webhook ingestion (deprecated for core analytics, kept as optional legacy)."  
**After:** "TradingView alert/webhook ingestion (deprecated for core analytics, kept as optional legacy)."  
*(Same, but now clearly marked DEPRECATED in title)*

### New Phase 3 (Dashboards)
**Added:** "Dashboards re-based on Databento truth layer."  
**Modules:**
- Automated Signals Dashboard re-based on Databento truth layer
- Trades / MFE / MAE dashboards re-based on Databento truth layer
- Data Quality dashboard updated for Databento pipeline

**Rationale:** Current dashboards use TradingView alerts (legacy). Need to rebase on Databento data.

---

## 🔍 Module Detail Changes

### Phase 0 Module Descriptions

| Module | Before | After |
|--------|--------|-------|
| databento_download | "Databento dataset downloaded (MNQ OHLCV-1m)" | "✅ Databento dataset downloaded (MNQ OHLCV-1m)" |
| schema_migration | "DB schema migrated (market_bars_ohlcv_1m + data_ingest_runs)" | "✅ DB schema migrated (market_bars_ohlcv_1m + data_ingest_runs)" |
| ingestion_complete | "Ingestion complete (2019–2025) — 2.34M bars" | "✅ Ingestion complete (2019–2025) — 2.34M bars (row_count 2338262)" |
| stats_endpoint | "Stats endpoint live (/api/market-data/mnq/ohlcv-1m/stats)" | "✅ Stats endpoint live (/api/market-data/mnq/ohlcv-1m/stats)" |
| backfill_optional | "Optional backfill: 2010–2019" | "⬜ Optional backfill: 2010–2019" |

**Changes:**
- ✅ Added checkmark/box emojis for visual clarity
- ✅ Added exact row_count to ingestion_complete
- ✅ Clearly marked backfill as incomplete (⬜)

---

## 🚀 User Experience Impact

### Before
- User sees Phase 0 as "100% complete"
- No live data to verify completion
- Unclear what "complete" means
- TradingView appears as core system

### After
- User sees Phase 0 as "80% complete" (4/5 modules)
- Live stats prove Databento data is real and current
- Clear distinction: 4 core modules done, 1 optional module pending
- TradingView clearly marked as "Legacy/Optional (DEPRECATED)"
- Clear roadmap progression: Phase 0 → 1 → 2 → 3 → 4

---

## 📊 Live Stats Display

### New Feature: Databento Stats Box
```
┌─────────────────────────────────────────┐
│ 📊 Live Dataset Stats                   │
│ Bars: 2,338,262                          │
│ Range: 2019-05-05 → 2025-12-22          │
│ Latest: 2025-12-22 16:00 @ $25,930.50   │
└─────────────────────────────────────────┘
```

**Data Source:** Direct PostgreSQL query to `market_bars_ohlcv_1m` table  
**Update Frequency:** Every page load (real-time)  
**Fallback:** "Stats unavailable (check API endpoint)" if query fails

---

## ✅ Summary

**What Changed:**
1. Phase 0 completion corrected from 100% to 80% (backfill optional)
2. Live Databento stats now displayed in Phase 0 card
3. Template fixed to reference correct phase_id ('0' not '0.5')
4. Phase 5 clearly marked as "DEPRECATED"
5. New Phases 3-4 added for future work
6. Module descriptions enhanced with emojis and exact counts

**Why It Matters:**
- Honest representation of system state
- Clear distinction between core (Databento) and legacy (TradingView)
- Live data proves completion claims
- Clear roadmap for future development

**User Benefit:**
- Accurate progress tracking
- Confidence in data quality
- Clear understanding of system architecture
- Transparent development roadmap
