# Legacy Module Gating Analysis

**Date:** November 29, 2025  
**Purpose:** Identify all legacy modules in web_server.py that query non-existent tables in clean database

---

## PROBLEM STATEMENT

The new Railway database is clean and only contains:
- `automated_signals` table (H1 module)
- `execution_tasks` table (Stage 13B)
- `execution_logs` table (Stage 13B)

All other legacy tables do NOT exist:
- `signal_lab_trades` (legacy V1)
- `live_signals` (legacy V1)
- `telemetry_automated_signals_log` (telemetry)
- `replay_candles` (replay engine)
- ML/prediction tables
- Prop firm tables

When these legacy modules try to query non-existent tables, they cause:
- "relation does not exist" errors
- "transaction aborted" errors
- Database startup failures
- Automated Signals ingestion failures

---

## SOLUTION APPROACH

Add environment flag gating to disable legacy modules:

```python
ENABLE_LEGACY = os.environ.get("ENABLE_LEGACY", "false")

if ENABLE_LEGACY == "true":
    # Legacy module initialization
    initialize_legacy_module()
else:
    logger.warning("⚠️ Legacy module disabled for clean DB startup")
```

---

## MODULES TO GATE

### 1. Prediction Accuracy Tracker (Lines ~795-820)
**Location:** After realtime_handler initialization  
**Tables:** ML prediction tables  
**Code:**
```python
from prediction_accuracy_tracker import PredictionAccuracyTracker
prediction_tracker = PredictionAccuracyTracker(db, socketio, auto_start_monitoring=ml_training_enabled)
```

### 2. PropFirmRegistry (Lines ~974-982)
**Location:** After database initialization  
**Tables:** Prop firm tables (firms, programs, rules)  
**Code:**
```python
prop_registry = PropFirmRegistry(db)
prop_registry.ensure_schema_and_seed()
```

### 3. Legacy Signal Lab Migrations
**Location:** Database startup migrations  
**Tables:** `signal_lab_trades`, `live_signals`  
**Search needed:** Column additions, table creations for V1 tables

### 4. Telemetry Tables
**Location:** Database startup migrations  
**Tables:** `telemetry_automated_signals_log`  
**Search needed:** Telemetry table creation

### 5. Replay Engine Tables
**Location:** Database startup migrations  
**Tables:** `replay_candles`  
**Search needed:** Replay table creation

### 6. Phase 2A Signal V2 Preview
**Location:** Unknown - needs search  
**Tables:** `live_signals` references  
**Search needed:** Phase 2A modules

---

## IMPLEMENTATION STRATEGY

### Option A: Comprehensive Gating (RECOMMENDED)
1. Add `ENABLE_LEGACY` flag at top of web_server.py
2. Wrap each legacy initializer with flag check
3. Preserve all code (no deletions)
4. Add clear logging for disabled modules

### Option B: Targeted Gating
1. Only gate the most problematic modules
2. Leave less critical modules active
3. Risk: May still hit non-existent tables

### Option C: Create Legacy Module File
1. Move all legacy initializers to separate file
2. Import conditionally based on flag
3. Cleaner but more invasive

---

## RECOMMENDATION

**Use Option A** with this implementation:

1. Add flag at top (after imports):
```python
# Legacy module gating for clean database startup
ENABLE_LEGACY = os.environ.get("ENABLE_LEGACY", "false")
logger.info(f"Legacy modules: {'ENABLED' if ENABLE_LEGACY == 'true' else 'DISABLED'}")
```

2. Wrap each legacy initializer:
```python
if ENABLE_LEGACY == "true":
    # Original legacy code here
    pass
else:
    logger.warning("⚠️ [Module Name] disabled - legacy tables not present")
    # Set to None or safe default
    module_var = None
```

3. Update dependent code to check for None before using legacy modules

---

## NEXT STEPS

1. **Search web_server.py** for all table creation/migration code
2. **Identify** which tables are legacy vs H1
3. **Create patch** wrapping all legacy initializers
4. **Test** that H1 (automated_signals) still works
5. **Deploy** with ENABLE_LEGACY=false

---

## RISK ASSESSMENT

**Low Risk:**
- Prediction tracker gating
- PropFirmRegistry gating
- Replay engine gating

**Medium Risk:**
- Signal lab migrations (may affect H1 if not careful)
- Telemetry gating (may affect H1 telemetry)

**High Risk:**
- Phase 2A modules (unknown dependencies)
- Any module that H1 depends on

---

## STATUS

**Analysis Phase:** Complete  
**Implementation Phase:** Pending user approval  
**Testing Phase:** Not started  
**Deployment Phase:** Not started

This is a large change that requires careful implementation to avoid breaking H1 (automated_signals) functionality.
