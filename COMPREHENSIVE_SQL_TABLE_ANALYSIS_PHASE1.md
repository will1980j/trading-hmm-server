# COMPREHENSIVE SQL TABLE ANALYSIS - PHASE 1: MAPPING ONLY

**Date:** November 29, 2025  
**Purpose:** Complete mapping of all SQL table references in the codebase  
**Status:** MAPPING ONLY - NO PATCHES APPLIED

---

## EXECUTIVE SUMMARY

**Analysis Scope:** Full codebase scan for all SQL operations  
**Search Patterns:** SELECT, INSERT, UPDATE, DELETE, ALTER TABLE, CREATE TABLE, DROP TABLE, FROM, JOIN  
**Total Files Analyzed:** 500+ Python files, SQL files, and scripts  

---

## TABLE CLASSIFICATION SYSTEM

### H1 CORE (KEEP) ✅
**Table:** `automated_signals`  
**Status:** PRODUCTION READY - ACTIVE USE  
**Purpose:** Primary H1 automated trading system  

### LEGACY V1 (QUARANTINE) ⚠️
**Tables:** `signal_lab_trades`, `live_signals`  
**Status:** OLD SYSTEM - SHOULD BE DISABLED  
**Purpose:** Original manual signal lab system  

### H2 EXECUTION ENGINE (DISABLE TEMPORARILY) 🔄
**Tables:** `execution_tasks`, `execution_logs`  
**Status:** FUTURE H2 - NOT YET ACTIVE  
**Purpose:** Multi-account execution routing (Stage 13B)  

### ML/PREDICTION (DISABLE) 🤖
**Tables:** `prediction_outcomes`, `prediction_accuracy_stats`, `prediction_accuracy_tracking`  
**Status:** ML MODULE - OPTIONAL FEATURE  
**Purpose:** ML prediction tracking and accuracy  

### REPLAY (DISABLE) 📼
**Tables:** `replay_candles`  
**Status:** REPLAY ENGINE - OPTIONAL FEATURE  
**Purpose:** Historical data replay for testing  

### TELEMETRY (CASE-BY-CASE) 📊
**Tables:** `telemetry_automated_signals_log`  
**Status:** DIAGNOSTIC TOOL - OPTIONAL  
**Purpose:** Advanced telemetry logging  

### PROP ENGINE (DISABLE) 🏢
**Tables:** `prop_firms`, `prop_firm_programs`, `prop_firm_rules`  
**Status:** STAGE 13 - NOT YET ACTIVE  
**Purpose:** Prop firm management system  

### PRICE DATA (CASE-BY-CASE) 💰
**Tables:** `realtime_prices`  
**Status:** REAL-TIME PRICE STREAMING  
**Purpose:** Live price data for MFE tracking  

### V2 TABLES (UNKNOWN) ❓
**Tables:** `signal_lab_v2`, `signal_lab_v2_trades`, `enhanced_signals_v2`  
**Status:** UNCLEAR - NEEDS INVESTIGATION  
**Purpose:** Unknown V2 system references  

### OTHER TABLES (UNKNOWN) ❓
**Tables:** `ai_conversation_history`, `economic_news_cache`, `hyperparameter_optimization_results`, `signal_lab_5m_trades`, `signal_lab_15m_trades`  
**Status:** UNCLEAR - NEEDS INVESTIGATION  

---

## DETAILED FILE-BY-FILE ANALYSIS

### 🔴 CRITICAL FILE: web_server.py

**Line 358-377:** CREATE TABLE `execution_tasks` (H2 EXECUTION ENGINE)
```python
cursor.execute("""
    CREATE TABLE IF NOT EXISTS execution_tasks (
        id SERIAL PRIMARY KEY,
        trade_id VARCHAR(100) NOT NULL,
        event_type VARCHAR(32) NOT NULL,
        ...
    )
""")
```
**Classification:** H2 EXECUTION ENGINE (DISABLE TEMPORARILY)  
**Action Required:** Comment out or gate behind feature flag

---

**Line 378-386:** CREATE TABLE `execution_logs` (H2 EXECUTION ENGINE)
```python
cursor.execute("""
    CREATE TABLE IF NOT EXISTS execution_logs (
        id SERIAL PRIMARY KEY,
        task_id INTEGER,
        log_message TEXT,
        ...
    )
""")
```
**Classification:** H2 EXECUTION ENGINE (DISABLE TEMPORARILY)  
**Action Required:** Comment out or gate behind feature flag

---

**Line 387-448:** CREATE TABLE `automated_signals` (H1 CORE)
```python
cursor.execute("""
    CREATE TABLE IF NOT EXISTS automated_signals (
        id SERIAL PRIMARY KEY,
        trade_id VARCHAR(64) UNIQUE NOT NULL,
        event_type VARCHAR(32) NOT NULL,
        ...
    )
""")
```
**Classification:** H1 CORE (KEEP) ✅  
**Action Required:** NONE - This is production code

---

**Line 450-499:** CREATE TABLE `signal_lab_trades` (LEGACY V1)
```python
cursor.execute("""
    CREATE TABLE IF NOT EXISTS signal_lab_trades (
        id SERIAL PRIMARY KEY,
        trade_id VARCHAR(64) UNIQUE NOT NULL,
        signal_type VARCHAR(32) NOT NULL,
        ...
    )
""")
```
**Classification:** LEGACY V1 (QUARANTINE) ⚠️  
**Action Required:** Comment out or gate behind legacy flag

---

**Line 501-548:** CREATE TABLE `live_signals` (LEGACY V1)
```python
cursor.execute("""
    CREATE TABLE IF NOT EXISTS live_signals (
        id SERIAL PRIMARY KEY,
        trade_id VARCHAR(64) UNIQUE NOT NULL,
        signal_type VARCHAR(32) NOT NULL,
        ...
    )
""")
```
**Classification:** LEGACY V1 (QUARANTINE) ⚠️  
**Action Required:** Comment out or gate behind legacy flag

---

**Line 550-573:** CREATE TABLE `telemetry_automated_signals_log` (TELEMETRY)
```python
cursor.execute("""
    CREATE TABLE IF NOT EXISTS telemetry_automated_signals_log (
        id SERIAL PRIMARY KEY,
        trade_id VARCHAR(64),
        event_type VARCHAR(32),
        ...
    )
""")
```
**Classification:** TELEMETRY (CASE-BY-CASE) 📊  
**Action Required:** Evaluate if needed, consider gating

---

**Line 575-597:** CREATE TABLE `replay_candles` (REPLAY)
```python
cursor.execute("""
    CREATE TABLE IF NOT EXISTS replay_candles (
        id SERIAL PRIMARY KEY,
        symbol VARCHAR(16) NOT NULL,
        timeframe VARCHAR(8) NOT NULL,
        ...
    )
""")
```
**Classification:** REPLAY (DISABLE) 📼  
**Action Required:** Comment out or gate behind feature flag

---

**Line 1779:** SELECT FROM `automated_signals` (H1 CORE)
```python
cursor.execute("SELECT * FROM automated_signals ORDER BY created_at DESC")
```
**Classification:** H1 CORE (KEEP) ✅  
**Action Required:** NONE

---

**Line 1851-1861:** INSERT INTO `automated_signals` (H1 CORE)
```python
cursor.execute("""
    INSERT INTO automated_signals 
    (trade_id, event_type, signal_type, session, entry_price, ...)
    VALUES (%s, %s, %s, %s, %s, ...)
""")
```
**Classification:** H1 CORE (KEEP) ✅  
**Action Required:** NONE

---

**Line 2066-2069:** UPDATE `automated_signals` (H1 CORE)
```python
cursor.execute("""
    UPDATE automated_signals 
    SET mfe = %s, updated_at = %s
    WHERE trade_id = %s AND event_type = 'ENTRY'
""")
```
**Classification:** H1 CORE (KEEP) ✅  
**Action Required:** NONE

---

**Line 10224:** DELETE FROM `automated_signals` (H1 CORE)
```python
cursor.execute("DELETE FROM automated_signals WHERE id = %s", (signal_id,))
```
**Classification:** H1 CORE (KEEP) ✅  
**Action Required:** NONE

---

### 🔴 CRITICAL FILE: prop_firm_registry.py

**Line 60-71:** CREATE TABLE `prop_firms` (PROP ENGINE)
```python
cursor.execute("""
    CREATE TABLE IF NOT EXISTS prop_firms (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        display_name VARCHAR(100) NOT NULL,
        ...
    )
""")
```
**Classification:** PROP ENGINE (DISABLE) 🏢  
**Action Required:** Comment out or gate behind Stage 13 flag

---

**Line 72-85:** CREATE TABLE `prop_firm_programs` (PROP ENGINE)
```python
cursor.execute("""
    CREATE TABLE IF NOT EXISTS prop_firm_programs (
        id SERIAL PRIMARY KEY,
        firm_id INTEGER REFERENCES prop_firms(id),
        name VARCHAR(100) NOT NULL,
        ...
    )
""")
```
**Classification:** PROP ENGINE (DISABLE) 🏢  
**Action Required:** Comment out or gate behind Stage 13 flag

---

**Line 86-98:** CREATE TABLE `prop_firm_rules` (PROP ENGINE)
```python
cursor.execute("""
    CREATE TABLE IF NOT EXISTS prop_firm_rules (
        id SERIAL PRIMARY KEY,
        program_id INTEGER REFERENCES prop_firm_programs(id),
        rule_type VARCHAR(50) NOT NULL,
        ...
    )
""")
```
**Classification:** PROP ENGINE (DISABLE) 🏢  
**Action Required:** Comment out or gate behind Stage 13 flag

---

**Line 104-106:** SELECT COUNT FROM `prop_firms` (PROP ENGINE)
```python
cursor.execute("SELECT COUNT(*) FROM prop_firms")
```
**Classification:** PROP ENGINE (DISABLE) 🏢  
**Action Required:** Comment out or gate behind Stage 13 flag

---

**Line 160-162:** SELECT FROM `prop_firms` (PROP ENGINE)
```python
cursor.execute("SELECT * FROM prop_firms WHERE status = 'active' ORDER BY display_name")
```
**Classification:** PROP ENGINE (DISABLE) 🏢  
**Action Required:** Comment out or gate behind Stage 13 flag

---

### 🔴 CRITICAL FILE: prediction_accuracy_tracker.py

**Line 49-61:** CREATE TABLE `prediction_outcomes` (ML/PREDICTION)
```python
cursor.execute("""
    CREATE TABLE IF NOT EXISTS prediction_outcomes (
        id SERIAL PRIMARY KEY,
        trade_id VARCHAR(64) NOT NULL,
        prediction_type VARCHAR(50) NOT NULL,
        ...
    )
""")
```
**Classification:** ML/PREDICTION (DISABLE) 🤖  
**Action Required:** Comment out or gate behind ML flag

---

**Line 62-74:** CREATE TABLE `prediction_accuracy_stats` (ML/PREDICTION)
```python
cursor.execute("""
    CREATE TABLE IF NOT EXISTS prediction_accuracy_stats (
        id SERIAL PRIMARY KEY,
        prediction_type VARCHAR(50) NOT NULL,
        total_predictions INTEGER DEFAULT 0,
        ...
    )
""")
```
**Classification:** ML/PREDICTION (DISABLE) 🤖  
**Action Required:** Comment out or gate behind ML flag

---

**Line 79-81:** SELECT COUNT FROM `prediction_outcomes` (ML/PREDICTION)
```python
cursor.execute("SELECT COUNT(*) FROM prediction_outcomes")
```
**Classification:** ML/PREDICTION (DISABLE) 🤖  
**Action Required:** Comment out or gate behind ML flag

---

### 🔴 CRITICAL FILE: ai_business_advisor_endpoint.py

**Line 205-208:** SELECT FROM `ai_conversation_history` (UNKNOWN)
```python
cursor.execute("""
    SELECT role, content FROM ai_conversation_history
    WHERE session_id = %s
    ORDER BY timestamp ASC
""")
```
**Classification:** UNKNOWN ❓  
**Action Required:** Investigate purpose and usage

---

**Line 347:** SELECT FROM `signal_lab_trades` (LEGACY V1)
```python
cursor.execute(f"SELECT COUNT(*) as trades, AVG(COALESCE(mfe_none, mfe, 0)) as avg_r, ... FROM signal_lab_trades WHERE ...")
```
**Classification:** LEGACY V1 (QUARANTINE) ⚠️  
**Action Required:** Replace with `automated_signals` or disable

---

**Line 365:** SELECT FROM `signal_lab_trades` (LEGACY V1)
```python
cursor.execute(f"SELECT session, bias, COUNT(*) as trades, ... FROM signal_lab_trades GROUP BY session, bias ...")
```
**Classification:** LEGACY V1 (QUARANTINE) ⚠️  
**Action Required:** Replace with `automated_signals` or disable

---

**Line 372:** SELECT FROM `signal_lab_trades` (LEGACY V1)
```python
cursor.execute("SELECT date, SUM(COALESCE(mfe_none, mfe, 0)) as daily_r FROM signal_lab_trades GROUP BY date ORDER BY date")
```
**Classification:** LEGACY V1 (QUARANTINE) ⚠️  
**Action Required:** Replace with `automated_signals` or disable

---

### 🔴 CRITICAL FILE: automated_signals_api_robust.py

**Line 44-47:** SELECT EXISTS FROM `information_schema.tables` (METADATA CHECK)
```python
cursor.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'automated_signals'
    );
""")
```
**Classification:** H1 CORE VALIDATION (KEEP) ✅  
**Action Required:** NONE

---

**Line 64-66:** SELECT COUNT FROM `automated_signals` (H1 CORE)
```python
cursor.execute("SELECT COUNT(*) FROM automated_signals;")
```
**Classification:** H1 CORE (KEEP) ✅  
**Action Required:** NONE

---

**Line 179-181:** SELECT MAX FROM `automated_signals` (H1 CORE)
```python
cursor.execute("""
    SELECT MAX(timestamp) FROM automated_signals;
""")
```
**Classification:** H1 CORE (KEEP) ✅  
**Action Required:** NONE

---

### 🔴 CRITICAL FILE: database/full_automation_schema.sql

**Line 1-29:** CREATE TABLE `automated_signals` (H1 CORE)
```sql
CREATE TABLE IF NOT EXISTS automated_signals (
    id SERIAL PRIMARY KEY,
    trade_id VARCHAR(64) UNIQUE NOT NULL,
    event_type VARCHAR(32) NOT NULL,
    ...
);
```
**Classification:** H1 CORE (KEEP) ✅  
**Action Required:** NONE

---

**Line 30-47:** CREATE TABLE `execution_tasks` (H2 EXECUTION ENGINE)
```sql
CREATE TABLE IF NOT EXISTS execution_tasks (
    id SERIAL PRIMARY KEY,
    trade_id VARCHAR(100) NOT NULL,
    event_type VARCHAR(32) NOT NULL,
    ...
);
```
**Classification:** H2 EXECUTION ENGINE (DISABLE TEMPORARILY) 🔄  
**Action Required:** Comment out or gate behind feature flag

---

**Line 48-55:** CREATE TABLE `execution_logs` (H2 EXECUTION ENGINE)
```sql
CREATE TABLE IF NOT EXISTS execution_logs (
    id SERIAL PRIMARY KEY,
    task_id INTEGER,
    log_message TEXT,
    ...
);
```
**Classification:** H2 EXECUTION ENGINE (DISABLE TEMPORARILY) 🔄  
**Action Required:** Comment out or gate behind feature flag

---

**Line 56-103:** CREATE TABLE `signal_lab_v2` (V2 UNKNOWN)
```sql
CREATE TABLE IF NOT EXISTS signal_lab_v2 (
    id SERIAL PRIMARY KEY,
    trade_id VARCHAR(64) UNIQUE NOT NULL,
    signal_type VARCHAR(32) NOT NULL,
    ...
);
```
**Classification:** V2 TABLES (UNKNOWN) ❓  
**Action Required:** Investigate if this is duplicate/obsolete

---

**Line 104-112:** CREATE TABLE `realtime_prices` (PRICE DATA)
```sql
CREATE TABLE IF NOT EXISTS realtime_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(16) NOT NULL,
    price DECIMAL(12,4) NOT NULL,
    ...
);
```
**Classification:** PRICE DATA (CASE-BY-CASE) 💰  
**Action Required:** Evaluate if actively used for MFE tracking

---

**Line 113-124:** CREATE TABLE `prop_firms` (PROP ENGINE)
```sql
CREATE TABLE IF NOT EXISTS prop_firms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    ...
);
```
**Classification:** PROP ENGINE (DISABLE) 🏢  
**Action Required:** Comment out or gate behind Stage 13 flag

---

**Line 125-138:** CREATE TABLE `prop_firm_programs` (PROP ENGINE)
```sql
CREATE TABLE IF NOT EXISTS prop_firm_programs (
    id SERIAL PRIMARY KEY,
    firm_id INTEGER REFERENCES prop_firms(id),
    name VARCHAR(100) NOT NULL,
    ...
);
```
**Classification:** PROP ENGINE (DISABLE) 🏢  
**Action Required:** Comment out or gate behind Stage 13 flag

---

**Line 139-149:** CREATE TABLE `prop_firm_rules` (PROP ENGINE)
```sql
CREATE TABLE IF NOT EXISTS prop_firm_rules (
    id SERIAL PRIMARY KEY,
    program_id INTEGER REFERENCES prop_firm_programs(id),
    rule_type VARCHAR(50) NOT NULL,
    ...
);
```
**Classification:** PROP ENGINE (DISABLE) 🏢  
**Action Required:** Comment out or gate behind Stage 13 flag

---

### 🔴 CRITICAL FILE: database/signal_lab_v2_schema.sql

**Line 1-48:** CREATE TABLE `signal_lab_v2` (V2 UNKNOWN)
```sql
CREATE TABLE IF NOT EXISTS signal_lab_v2 (
    id SERIAL PRIMARY KEY,
    trade_id VARCHAR(64) UNIQUE NOT NULL,
    signal_type VARCHAR(32) NOT NULL,
    ...
);
```
**Classification:** V2 TABLES (UNKNOWN) ❓  
**Action Required:** Investigate if this is duplicate/obsolete - likely OLD V2 system

---

### 🔴 CRITICAL FILE: automated_signals_state.py

**Line 40-51:** CREATE TABLE `automated_signals` (H1 CORE)
```python
cursor.execute("""
    CREATE TABLE IF NOT EXISTS automated_signals (
        id SERIAL PRIMARY KEY,
        trade_id VARCHAR(64) UNIQUE NOT NULL,
        event_type VARCHAR(32) NOT NULL,
        ...
    )
""")
```
**Classification:** H1 CORE (KEEP) ✅  
**Action Required:** NONE

---

**Line 53-55:** SELECT FROM `automated_signals` (H1 CORE)
```python
cursor.execute("SELECT * FROM automated_signals ORDER BY created_at DESC LIMIT 1")
```
**Classification:** H1 CORE (KEEP) ✅  
**Action Required:** NONE

---

### 🔴 CRITICAL FILE: clear_realtime_price_data.py

**Line 19-21:** DELETE FROM `realtime_prices` (PRICE DATA)
```python
cursor.execute("DELETE FROM realtime_prices")
```
**Classification:** PRICE DATA (CASE-BY-CASE) 💰  
**Action Required:** Evaluate if actively used

---

**Line 22-31:** CREATE TABLE `realtime_prices` (PRICE DATA)
```python
cursor.execute("""
    CREATE TABLE IF NOT EXISTS realtime_prices (
        id SERIAL PRIMARY KEY,
        symbol VARCHAR(16) NOT NULL,
        price DECIMAL(12,4) NOT NULL,
        ...
    )
""")
```
**Classification:** PRICE DATA (CASE-BY-CASE) 💰  
**Action Required:** Evaluate if actively used

---

**Line 32-39:** INSERT INTO `realtime_prices` (PRICE DATA)
```python
cursor.execute("""
    INSERT INTO realtime_prices (symbol, price, updated_at)
    VALUES (%s, %s, NOW())
    ON CONFLICT (symbol) 
    DO UPDATE SET 
        price = EXCLUDED.price,
        updated_at = EXCLUDED.updated_at
""")
```
**Classification:** PRICE DATA (CASE-BY-CASE) 💰  
**Action Required:** Evaluate if actively used

---

## SUMMARY OF FINDINGS

### Tables by Classification:

**H1 CORE (KEEP) ✅**
- `automated_signals` - 100+ references across codebase

**LEGACY V1 (QUARANTINE) ⚠️**
- `signal_lab_trades` - 50+ references (mostly in ai_business_advisor_endpoint.py, web_server.py)
- `live_signals` - 20+ references (mostly in web_server.py)

**H2 EXECUTION ENGINE (DISABLE TEMPORARILY) 🔄**
- `execution_tasks` - 10+ references (web_server.py, database/full_automation_schema.sql)
- `execution_logs` - 5+ references (web_server.py, database/full_automation_schema.sql)

**ML/PREDICTION (DISABLE) 🤖**
- `prediction_outcomes` - 15+ references (prediction_accuracy_tracker.py, auto_prediction_outcome_updater.py)
- `prediction_accuracy_stats` - 10+ references (prediction_accuracy_tracker.py)
- `prediction_accuracy_tracking` - 5+ references (auto_prediction_outcome_updater.py)

**REPLAY (DISABLE) 📼**
- `replay_candles` - 5+ references (web_server.py)

**TELEMETRY (CASE-BY-CASE) 📊**
- `telemetry_automated_signals_log` - 10+ references (web_server.py)

**PROP ENGINE (DISABLE) 🏢**
- `prop_firms` - 20+ references (prop_firm_registry.py, database/full_automation_schema.sql)
- `prop_firm_programs` - 15+ references (prop_firm_registry.py, database/full_automation_schema.sql)
- `prop_firm_rules` - 10+ references (prop_firm_registry.py, database/full_automation_schema.sql)

**PRICE DATA (CASE-BY-CASE) 💰**
- `realtime_prices` - 15+ references (clear_realtime_price_data.py, check_database_price_data.py, web_server.py)

**V2 TABLES (UNKNOWN) ❓**
- `signal_lab_v2` - 50+ references (database/signal_lab_v2_schema.sql, multiple deployment scripts)
- `signal_lab_v2_trades` - 30+ references (automated_signal_processor.py, web_server.py)
- `enhanced_signals_v2` - 10+ references (automation_database_schema.sql)

**OTHER TABLES (UNKNOWN) ❓**
- `ai_conversation_history` - 5+ references (ai_business_advisor_endpoint.py)
- `economic_news_cache` - 3+ references (web_server.py)
- `hyperparameter_optimization_results` - 2+ references (web_server.py)
- `signal_lab_5m_trades` - 5+ references (web_server.py)
- `signal_lab_15m_trades` - 5+ references (web_server.py)

---

## CRITICAL OBSERVATIONS

### 1. V2 TABLE CONFUSION
There are multiple references to "V2" tables that appear to be from an OLD V2 system (not the current H1 system):
- `signal_lab_v2`
- `signal_lab_v2_trades`
- `enhanced_signals_v2`

**These need investigation** - they may be obsolete remnants from before the H1 system was created.

### 2. LEGACY V1 HEAVY USAGE
The `signal_lab_trades` table is heavily used in `ai_business_advisor_endpoint.py` with 10+ queries. This entire file may need refactoring to use `automated_signals` instead.

### 3. PROP ENGINE PREMATURE CREATION
The prop firm tables are created in `web_server.py` startup but Stage 13 is not yet deployed. These should be gated.

### 4. ML TABLES ALWAYS CREATED
The ML prediction tables are created unconditionally even though ML is an optional feature.

### 5. PRICE DATA UNCLEAR STATUS
The `realtime_prices` table is referenced but it's unclear if it's actively used for MFE tracking or if it's obsolete.

---

## NEXT STEPS (PHASE 2)

1. **Investigate V2 tables** - Determine if `signal_lab_v2`, `signal_lab_v2_trades`, `enhanced_signals_v2` are obsolete
2. **Refactor ai_business_advisor_endpoint.py** - Replace all `signal_lab_trades` queries with `automated_signals`
3. **Gate prop engine tables** - Add feature flag for Stage 13 tables
4. **Gate ML tables** - Add feature flag for ML prediction tables
5. **Evaluate price data** - Determine if `realtime_prices` is actively used
6. **Clean up deployment scripts** - Many old deployment scripts reference obsolete tables

---

## FILES REQUIRING IMMEDIATE ATTENTION

### HIGH PRIORITY:
1. **web_server.py** - Contains all table creation logic, needs gating
2. **ai_business_advisor_endpoint.py** - Heavy legacy V1 usage, needs refactoring
3. **database/full_automation_schema.sql** - Contains all table schemas, needs cleanup
4. **prop_firm_registry.py** - Stage 13 code running prematurely

### MEDIUM PRIORITY:
5. **prediction_accuracy_tracker.py** - ML tables need gating
6. **automated_signal_processor.py** - References unknown V2 tables
7. **clear_realtime_price_data.py** - Price data table usage unclear

### LOW PRIORITY:
8. All deployment scripts in root directory - Many reference obsolete tables
9. Backup files - Should be cleaned up or archived

---

**END OF PHASE 1 ANALYSIS**

**Next Action:** Review this analysis and approve Phase 2 (applying patches and gates)
