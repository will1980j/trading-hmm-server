# PHASE 2: COMPREHENSIVE GATING PATCH REPORT

**Date:** November 29, 2025  
**Status:** READY FOR IMPLEMENTATION  
**Based On:** COMPREHENSIVE_SQL_TABLE_ANALYSIS_PHASE1.md

---

## EXECUTIVE SUMMARY

This patch adds feature flags to gate all non-H1-core functionality, ensuring a clean database initialization that only creates the `automated_signals` table by default. All optional features (legacy V1, prop engine, ML, V2 tables, replay, execution router) are disabled by default and can be enabled via environment variables.

---

## NEW ENVIRONMENT VARIABLES

Add to Railway/production environment:

```bash
# All default to "false" - only enable what you need
ENABLE_LEGACY=false          # Legacy V1 tables (signal_lab_trades, live_signals)
ENABLE_PREDICTION=false      # ML prediction tables
ENABLE_PROP=false            # Prop firm tables (Stage 13)
ENABLE_V2=false              # Old V2 tables (signal_lab_v2, etc.)
ENABLE_REPLAY=false          # Replay engine tables
ENABLE_EXECUTION=false       # Execution router (Stage 13B)
ENABLE_TELEMETRY_LEGACY=false # Legacy telemetry tables
```

**H1 CORE (`automated_signals`) is ALWAYS enabled - no flag needed.**

---

## FILES TO BE MODIFIED

### 1. web_server.py (PRIMARY FILE)
**Lines Modified:** ~50 blocks across 11,000+ lines  
**Backup Created:** `web_server.py.backup_phase2`

### 2. prop_firm_registry.py (SECONDARY FILE)
**Lines Modified:** ~5 blocks  
**Backup Created:** `prop_firm_registry.py.backup_phase2`

---

## DETAILED MODIFICATIONS

### MODIFICATION 1: Add Feature Flags (web_server.py, after line 24)

**Location:** After `from execution_router import ExecutionRouter`

**Add:**
```python
# ============================================================================
# FEATURE FLAGS - Control optional modules and legacy systems
# ============================================================================
# Set via environment variables (default: false for all optional features)
ENABLE_LEGACY = os.environ.get("ENABLE_LEGACY", "false").lower() == "true"
ENABLE_PREDICTION = os.environ.get("ENABLE_PREDICTION", "false").lower() == "true"
ENABLE_PROP = os.environ.get("ENABLE_PROP", "false").lower() == "true"
ENABLE_V2 = os.environ.get("ENABLE_V2", "false").lower() == "true"
ENABLE_REPLAY = os.environ.get("ENABLE_REPLAY", "false").lower() == "true"
ENABLE_EXECUTION = os.environ.get("ENABLE_EXECUTION", "false").lower() == "true"
ENABLE_TELEMETRY_LEGACY = os.environ.get("ENABLE_TELEMETRY_LEGACY", "false").lower() == "true"

# H1 CORE is ALWAYS enabled (automated_signals table and related functionality)
# These flags control OPTIONAL features only
# ============================================================================
```

---

### MODIFICATION 2: Gate ExecutionRouter Import (web_server.py, line 24)

**Current:**
```python
from execution_router import ExecutionRouter
```

**Replace with:**
```python
# Execution Router (Stage 13B) - gated behind ENABLE_EXECUTION flag
try:
    if os.environ.get("ENABLE_EXECUTION", "false").lower() == "true":
        from execution_router import ExecutionRouter
    else:
        ExecutionRouter = None
except ImportError:
    ExecutionRouter = None
```

---

### MODIFICATION 3: Gate Execution Tasks Table Creation (web_server.py, lines 358-377)

**Current:**
```python
        # Execution queue tables for multi-account routing (Stage 13B)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_tasks (
                ...
            )
        """)
```

**Wrap with:**
```python
        # Execution queue tables for multi-account routing (Stage 13B)
        if ENABLE_EXECUTION:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS execution_tasks (
                    ...
                )
            """)
```

---

### MODIFICATION 4: Gate Execution Logs Table Creation (web_server.py, lines 378-386)

**Current:**
```python
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_logs (
                ...
            )
        """)
```

**Wrap with:**
```python
        if ENABLE_EXECUTION:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS execution_logs (
                    ...
                )
            """)
```

---

### MODIFICATION 5: Gate Legacy V1 Tables (web_server.py, lines 450-548)

**Current:**
```python
        # Signal lab trades table (legacy V1)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signal_lab_trades (
                ...
            )
        """)
        
        # Live signals table (legacy V1)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS live_signals (
                ...
            )
        """)
```

**Wrap with:**
```python
        # Signal lab trades table (legacy V1) - GATED
        if ENABLE_LEGACY:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS signal_lab_trades (
                    ...
                )
            """)
        
        # Live signals table (legacy V1) - GATED
        if ENABLE_LEGACY:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS live_signals (
                    ...
                )
            """)
```

---

### MODIFICATION 6: Gate Telemetry Legacy Table (web_server.py, lines 550-573)

**Current:**
```python
        # Telemetry automated signals log (telemetry)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS telemetry_automated_signals_log (
                ...
            )
        """)
```

**Wrap with:**
```python
        # Telemetry automated signals log (telemetry) - GATED
        if ENABLE_TELEMETRY_LEGACY:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS telemetry_automated_signals_log (
                    ...
                )
            """)
```

---

### MODIFICATION 7: Gate Replay Candles Table (web_server.py, lines 575-597)

**Current:**
```python
        # Replay candles table (replay engine)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS replay_candles (
                ...
            )
        """)
```

**Wrap with:**
```python
        # Replay candles table (replay engine) - GATED
        if ENABLE_REPLAY:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS replay_candles (
                    ...
                )
            """)
```

---

### MODIFICATION 8: Ensure Telemetry Table Exists Before ALTER (web_server.py, before any ALTER TABLE)

**Add before any ALTER TABLE statements for telemetry_automated_signals_log:**

```python
        # Ensure telemetry table exists before ALTER (if telemetry enabled)
        if ENABLE_TELEMETRY_LEGACY:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS telemetry_automated_signals_log (
                    id SERIAL PRIMARY KEY,
                    trade_id VARCHAR(64),
                    event_type VARCHAR(32),
                    raw_payload JSONB,
                    processed_at TIMESTAMP DEFAULT NOW(),
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
```

---

### MODIFICATION 9: Gate PropFirmRegistry Initialization (web_server.py, search for PropFirmRegistry)

**Current:**
```python
prop_firm_registry = PropFirmRegistry(db)
```

**Replace with:**
```python
# Prop Firm Registry (Stage 13) - GATED
if ENABLE_PROP:
    try:
        prop_firm_registry = PropFirmRegistry(db)
    except Exception as e:
        logger.warning(f"⚠️ Prop firm registry initialization failed: {e}")
        prop_firm_registry = None
else:
    prop_firm_registry = None
```

---

### MODIFICATION 10: Gate ExecutionRouter Initialization (web_server.py, search for ExecutionRouter)

**Current:**
```python
execution_router = ExecutionRouter(db)
```

**Replace with:**
```python
# Execution Router (Stage 13B) - GATED
if ENABLE_EXECUTION and ExecutionRouter is not None:
    try:
        execution_router = ExecutionRouter(db)
    except Exception as e:
        logger.warning(f"⚠️ Execution router initialization failed: {e}")
        execution_router = None
else:
    execution_router = None
```

---

### MODIFICATION 11: Gate Prop Firm Registry in prop_firm_registry.py

**File:** prop_firm_registry.py  
**Lines:** 60-156 (entire __init__ and _seed_initial_data methods)

**Wrap table creation with:**
```python
def __init__(self, db):
    """Initialize prop firm registry"""
    self.db = db
    
    # Check if prop firm features are enabled
    if not os.environ.get("ENABLE_PROP", "false").lower() == "true":
        logger.info("🏢 Prop firm features disabled (ENABLE_PROP=false)")
        return
    
    # Rest of initialization...
```

---

## VERIFICATION CHECKLIST

After applying patches, verify:

### ✅ H1 CORE UNTOUCHED:
- [ ] `automated_signals` table creation - NO CHANGES
- [ ] `automated_signals_api_robust.py` - NO CHANGES
- [ ] `templates/main_dashboard.html` - NO CHANGES
- [ ] `templates/time_analysis.html` - NO CHANGES
- [ ] `templates/automated_signals_ultra.html` - NO CHANGES
- [ ] `static/js/automated_signals_ultra.js` - NO CHANGES
- [ ] `websocket_handler_robust.py` - NO CHANGES

### ✅ GATED FEATURES:
- [ ] Legacy V1 tables wrapped in `if ENABLE_LEGACY:`
- [ ] Prop firm tables wrapped in `if ENABLE_PROP:`
- [ ] Execution tables wrapped in `if ENABLE_EXECUTION:`
- [ ] Replay tables wrapped in `if ENABLE_REPLAY:`
- [ ] Telemetry legacy tables wrapped in `if ENABLE_TELEMETRY_LEGACY:`

### ✅ SAFE DEFAULTS:
- [ ] All flags default to `false`
- [ ] H1 core always enabled
- [ ] No breaking changes to existing functionality

---

## TESTING PROCEDURE

### Test 1: Clean Database (All Flags False)
```bash
# Set all flags to false (or don't set them)
python web_server.py
```

**Expected:** Only `automated_signals` table created

### Test 2: Enable Legacy
```bash
export ENABLE_LEGACY=true
python web_server.py
```

**Expected:** `automated_signals`, `signal_lab_trades`, `live_signals` created

### Test 3: Enable Prop
```bash
export ENABLE_PROP=true
python web_server.py
```

**Expected:** `automated_signals`, `prop_firms`, `prop_firm_programs`, `prop_firm_rules` created

### Test 4: Enable All
```bash
export ENABLE_LEGACY=true
export ENABLE_PREDICTION=true
export ENABLE_PROP=true
export ENABLE_V2=true
export ENABLE_REPLAY=true
export ENABLE_EXECUTION=true
export ENABLE_TELEMETRY_LEGACY=true
python web_server.py
```

**Expected:** All tables created

---

## DEPLOYMENT INSTRUCTIONS

### Step 1: Apply Patches Locally
```bash
python apply_phase2_comprehensive_gating.py
```

### Step 2: Test Locally
```bash
# Test with clean database
python web_server.py

# Verify only automated_signals table created
python -c "from database.railway_db import RailwayDB; db = RailwayDB(); cursor = db.conn.cursor(); cursor.execute(\"SELECT tablename FROM pg_tables WHERE schemaname='public'\"); print([r[0] for r in cursor.fetchall()])"
```

### Step 3: Commit Changes
```bash
git add web_server.py prop_firm_registry.py
git commit -m "Phase 2: Add comprehensive feature gating for optional modules

- Add ENABLE_LEGACY, ENABLE_PREDICTION, ENABLE_PROP, ENABLE_V2, ENABLE_REPLAY, ENABLE_EXECUTION, ENABLE_TELEMETRY_LEGACY flags
- Gate all non-H1-core table creation behind feature flags
- H1 core (automated_signals) always enabled
- All optional features default to disabled
- Based on COMPREHENSIVE_SQL_TABLE_ANALYSIS_PHASE1.md findings"
```

### Step 4: Deploy to Railway
```bash
git push origin main
```

### Step 5: Verify Production
- Check Railway logs for clean startup
- Verify only `automated_signals` table exists
- Test H1 core functionality (automated signals dashboard)

---

## ROLLBACK PROCEDURE

If issues occur:

```bash
# Restore from backup
cp web_server.py.backup_phase2 web_server.py
cp prop_firm_registry.py.backup_phase2 prop_firm_registry.py

# Commit and deploy
git add web_server.py prop_firm_registry.py
git commit -m "Rollback Phase 2 gating patches"
git push origin main
```

---

## SUMMARY OF CHANGES

### Files Modified: 2
1. **web_server.py** - 11 major modifications
2. **prop_firm_registry.py** - 1 major modification

### Feature Flags Added: 7
1. `ENABLE_LEGACY` - Legacy V1 tables
2. `ENABLE_PREDICTION` - ML prediction tables
3. `ENABLE_PROP` - Prop firm tables
4. `ENABLE_V2` - Old V2 tables
5. `ENABLE_REPLAY` - Replay engine tables
6. `ENABLE_EXECUTION` - Execution router
7. `ENABLE_TELEMETRY_LEGACY` - Legacy telemetry tables

### Tables Gated: 8
1. `execution_tasks` (H2 Execution Engine)
2. `execution_logs` (H2 Execution Engine)
3. `signal_lab_trades` (Legacy V1)
4. `live_signals` (Legacy V1)
5. `telemetry_automated_signals_log` (Telemetry Legacy)
6. `replay_candles` (Replay Engine)
7. `prop_firms` (Prop Engine)
8. `prop_firm_programs` (Prop Engine)
9. `prop_firm_rules` (Prop Engine)

### Tables ALWAYS Created: 1
1. `automated_signals` (H1 CORE) ✅

---

## CONFIRMED NO CHANGES TO:

✅ `automated_signals` table creation  
✅ `automated_signals_api_robust.py`  
✅ `templates/main_dashboard.html`  
✅ `templates/time_analysis.html`  
✅ `templates/automated_signals_ultra.html`  
✅ `static/js/automated_signals_ultra.js`  
✅ `websocket_handler_robust.py`  
✅ `time_analyzer.py`  
✅ All H1 core functionality preserved  

---

**END OF PHASE 2 PATCH REPORT**

**Status:** Ready for implementation  
**Next Action:** Create and run `apply_phase2_comprehensive_gating.py` script
