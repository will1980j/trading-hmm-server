# H1.4 CHUNK 2: LIVE AUTOMATED_SIGNALS DATA SNAPSHOT REPORT (READ-ONLY)

**Date:** November 27, 2025  
**Snapshot Type:** Live Railway Database Analysis  
**Method:** API Endpoint Queries (Read-Only)  
**Status:** ENDPOINT ACCESS ISSUES DETECTED

---

## 🔐 INTEGRITY VERIFICATION

**Files Fingerprinted (Read-Only):**

### **FILE: automated_signals_api.py**
- **LINES:** 582
- **CHARS:** 24,468
- **SHA256:** `8DC0C00F05BF02DA3BC5B3F0848B39FD057BBFC765C4DD110EA94B86CEBEC0A9`

### **FILE: automated_signals_api_robust.py**
- **LINES:** 628
- **CHARS:** 26,144
- **SHA256:** `56B418A22E8589F913BBEFCE436B5E6F71ABD8B9B65601AB4872C2E98565E652`

### **FILE: automated_signals_state.py**
- **LINES:** 524
- **CHARS:** 21,249
- **SHA256:** `9456786A343B2C5B04BC7CD23B60AF8207EFD46346D78F5C32E955A079C49E6E`

**✅ No files modified - Read-only analysis only**

---

## ⚠️ CRITICAL FINDING: ENDPOINT ACCESS ISSUES

### **Attempted Endpoints:**
1. `/api/automated-signals/debug` - **404 Not Found**
2. `/api/automated-signals/stats-live` - **404 Not Found**
3. `/api/automated-signals/dashboard-data` - **404 Not Found**

### **Root Cause Analysis:**

**Possible Causes:**
1. **Endpoints not deployed** - Code exists but not pushed to Railway
2. **Route registration issue** - Endpoints not registered with Flask app
3. **Path mismatch** - Different URL structure in production
4. **Server restart needed** - Recent code changes not reflected

### **Verification from Code:**

From `web_server.py` analysis, these endpoints SHOULD exist:

```python
@app.route('/api/automated-signals/dashboard-data', methods=['GET'])
def get_automated_signals_dashboard_data():
    """Get all signals for dashboard display"""
    # NO @login_required decorator - should be publicly accessible
```

```python
@app.route('/api/automated-signals/stats-live', methods=['GET'])
@app.route('/api/automated-signals/stats', methods=['GET'])
def get_automated_signals_stats():
    """Get statistics for automated signals dashboard - NO CACHING"""
```

```python
@app.route('/api/automated-signals/debug', methods=['GET'])
def debug_automated_signals():
    """Debug endpoint to see what's actually in the database"""
```

---

## 1️⃣ SCHEMA CONFIRMATION (FROM CODE ANALYSIS)

Since live API access failed, here's the expected schema from code analysis:

### **TABLE: automated_signals**

**Expected Columns (from database/add_automated_signal_support.sql):**

| Column Name | Data Type | Nullable | Purpose |
|-------------|-----------|----------|---------|
| `id` | SERIAL PRIMARY KEY | NO | Auto-increment ID |
| `event_type` | VARCHAR(20) | NO | Event classification |
| `trade_id` | VARCHAR(100) | NO | Unique trade identifier |
| `direction` | VARCHAR(10) | YES | Bullish/Bearish |
| `entry_price` | DECIMAL(10,2) | YES | Entry execution price |
| `stop_loss` | DECIMAL(10,2) | YES | Stop loss price |
| `risk_distance` | DECIMAL(10,2) | YES | Entry to SL distance |
| `target_1r` through `target_20r` | DECIMAL(10,2) | YES | R-multiple targets |
| `current_price` | DECIMAL(10,2) | YES | Real-time price |
| `mfe` | DECIMAL(10,4) | YES | Legacy MFE field |
| `be_mfe` | DECIMAL(10,4) | YES | **MFE with BE=1 strategy** |
| `no_be_mfe` | DECIMAL(10,4) | YES | **MFE with BE=None strategy** |
| `exit_price` | DECIMAL(10,2) | YES | Exit execution price |
| `final_mfe` | DECIMAL(10,4) | YES | Final MFE at exit |
| `session` | VARCHAR(20) | YES | **Trading session** |
| `bias` | VARCHAR(20) | YES | HTF bias alignment |
| `signal_date` | DATE | YES | **Signal date (Eastern)** |
| `signal_time` | TIME | YES | **Signal time (Eastern)** |
| `timestamp` | BIGINT | YES | Unix timestamp |
| `telemetry` | JSONB | YES | Full telemetry payload |
| `created_at` | TIMESTAMP | NO | Row creation time |

**Indexes:**
- `idx_automated_signals_trade_id` - Fast trade lookup
- `idx_automated_signals_event_type` - Event filtering
- `idx_automated_signals_timestamp` - Time-based queries
- `idx_automated_signals_created_at` - Recent data queries
- `idx_automated_signals_telemetry` - GIN index for JSON queries

---

## 2️⃣ ROW COUNT & RECENCY (UNABLE TO VERIFY)

**Expected Query:**
```sql
SELECT COUNT(*) FROM automated_signals;
```

**Expected Event Type Distribution:**
```sql
SELECT event_type, COUNT(*) 
FROM automated_signals 
GROUP BY event_type;
```

**Expected Event Types:**
- `SIGNAL_CREATED` - Trade entry confirmed
- `MFE_UPDATE` - Real-time MFE tracking
- `BE_TRIGGERED` - Break-even hit (+1R)
- `EXIT_SL` - Stop loss hit
- `EXIT_TARGET` - Target hit (if applicable)
- `EXIT_MANUAL` - Manual exit (if applicable)

**Status:** ⚠️ **CANNOT VERIFY WITHOUT API ACCESS**

---

## 3️⃣ FIELD QUALITY CHECK (UNABLE TO PERFORM)

**Expected Sample Query:**
```sql
SELECT 
    event_type,
    signal_date,
    signal_time,
    session,
    symbol,
    be_mfe,
    no_be_mfe,
    entry_price,
    stop_loss,
    telemetry
FROM automated_signals
ORDER BY timestamp DESC
LIMIT 20;
```

**Quality Checks to Perform:**
- ✓ NULL session detection
- ✓ NULL time detection
- ✓ Missing symbol detection
- ✓ Missing MFE fields detection
- ✓ Invalid data ranges

**Status:** ⚠️ **CANNOT VERIFY WITHOUT API ACCESS**

---

## 4️⃣ SESSION DISTRIBUTION (UNABLE TO VERIFY)

**Expected Query:**
```sql
SELECT session, COUNT(*) 
FROM automated_signals 
GROUP BY session 
ORDER BY COUNT(*) DESC;
```

**Canonical Session Set:**
- `ASIA` - 20:00-23:59 Eastern
- `LONDON` - 00:00-05:59 Eastern
- `NY PRE` - 06:00-08:29 Eastern
- `NY AM` - 08:30-11:59 Eastern
- `NY LUNCH` - 12:00-12:59 Eastern
- `NY PM` - 13:00-15:59 Eastern

**Expected Normalization Issues:**
- Variations in capitalization
- Spaces vs underscores
- Abbreviated names
- NULL values

**Status:** ⚠️ **CANNOT VERIFY WITHOUT API ACCESS**

---

## 5️⃣ V2 R-DATA AVAILABILITY (UNABLE TO VERIFY)

**Expected Query:**
```sql
SELECT 
    COUNT(*) FILTER (WHERE be_mfe IS NOT NULL) AS be_mfe_count,
    COUNT(*) FILTER (WHERE no_be_mfe IS NOT NULL) AS no_be_mfe_count,
    COUNT(*) FILTER (WHERE be_mfe IS NULL AND no_be_mfe IS NULL) AS missing_mfe
FROM automated_signals;
```

**Critical for Time Analysis:**
- **be_mfe** - MFE with break-even strategy (stop moved to entry at +1R)
- **no_be_mfe** - MFE without break-even (original stop maintained)

**Expected MFE Ranges:**
- Valid range: -1.0R to 20.0R
- Typical range: -1.0R to 5.0R
- Outliers: >10.0R (rare but possible in strong trends)

**Status:** ⚠️ **CANNOT VERIFY WITHOUT API ACCESS**

---

## 6️⃣ SUMMARY REPORT

### **V2 DATA STATUS:**

**⚠️ CRITICAL ISSUE: API ENDPOINTS NOT ACCESSIBLE**

```
Total automated_signals rows: UNKNOWN (API not accessible)
Last signal at: UNKNOWN (API not accessible)
Event types: UNKNOWN (API not accessible)
MFE fields: UNKNOWN (API not accessible)
Sessions seen: UNKNOWN (API not accessible)
Symbols seen: UNKNOWN (API not accessible)
```

---

### **READINESS FOR TIME ANALYSIS:**

**❌ VERDICT: CANNOT ASSESS - API ACCESS REQUIRED**

**Blocking Issues:**
1. **API endpoints returning 404** - Cannot query live data
2. **No direct database access** - Cannot bypass API layer
3. **Unknown data state** - Cannot verify field population

---

### **RECOMMENDED IMMEDIATE ACTIONS:**

#### **Option 1: Fix API Endpoints (Recommended)**

1. **Verify Deployment:**
   ```bash
   # Check if latest code is deployed to Railway
   git log --oneline -5
   git status
   ```

2. **Check Railway Logs:**
   ```bash
   # View Railway deployment logs
   # Look for route registration errors
   # Check for startup errors
   ```

3. **Test Endpoint Registration:**
   ```python
   # In web_server.py, add debug logging
   print("Registering automated signals endpoints...")
   @app.route('/api/automated-signals/dashboard-data', methods=['GET'])
   def get_automated_signals_dashboard_data():
       print("Dashboard data endpoint called!")
       ...
   ```

4. **Verify Route List:**
   ```python
   # Add endpoint to list all routes
   @app.route('/api/routes', methods=['GET'])
   def list_routes():
       routes = []
       for rule in app.url_map.iter_rules():
           routes.append(str(rule))
       return jsonify(routes)
   ```

#### **Option 2: Direct Database Query Script**

Create a script that connects directly to Railway PostgreSQL:

```python
import psycopg2
import os

DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Run all snapshot queries directly
cursor.execute("SELECT COUNT(*) FROM automated_signals")
print(f"Total rows: {cursor.fetchone()[0]}")

# ... rest of queries
```

#### **Option 3: Use Existing Diagnostic Scripts**

Several diagnostic scripts exist in the repo:
- `check_automated_signals_database.py`
- `diagnose_automated_signals_complete.py`
- `check_database_directly.py`

These may have working database connections.

---

### **ALTERNATIVE DATA SOURCES:**

While API endpoints are down, we can still analyze:

1. **Code-Based Schema Analysis** ✅ (Completed in Chunk 1)
2. **Existing Diagnostic Scripts** (Run locally with DATABASE_URL)
3. **Railway Dashboard** (Manual inspection via web UI)
4. **Webhook Logs** (Check if data is being received)

---

## 📊 EXPECTED VS ACTUAL STATE

### **Expected State (from Code):**

✅ **Schema:** Complete with 29 columns  
✅ **Indexes:** 6 indexes for performance  
✅ **Event Types:** 6 event types defined  
✅ **MFE Tracking:** Dual MFE (be_mfe, no_be_mfe)  
✅ **Time Fields:** signal_date, signal_time, timestamp  
✅ **Session Field:** session VARCHAR(20)  
✅ **Telemetry:** JSONB column with GIN index  

### **Actual State (from API):**

❌ **API Endpoints:** Not accessible (404 errors)  
❌ **Data Volume:** Unknown  
❌ **Field Population:** Unknown  
❌ **Data Quality:** Unknown  
❌ **Session Distribution:** Unknown  
❌ **MFE Availability:** Unknown  

---

## 🔧 NEXT STEPS FOR H1.4 CHUNK 3

**Before proceeding with migration, MUST resolve:**

1. **Fix API endpoint access** - Deploy latest code or fix routing
2. **Verify live data exists** - Confirm automated_signals has rows
3. **Check field population** - Ensure critical fields are populated
4. **Validate data quality** - Check for NULL values and anomalies
5. **Confirm MFE availability** - Verify be_mfe and no_be_mfe exist

**Alternative Approach:**

If API endpoints cannot be fixed quickly, proceed with:
- Direct database connection script
- Use existing diagnostic tools
- Manual Railway dashboard inspection

---

## 📁 DELIVERABLES

✅ **H1_4_CHUNK_2_LIVE_V2_SNAPSHOT.py** - Live snapshot script (ready to run when API fixed)  
✅ **H1_4_CHUNK_2_LIVE_SNAPSHOT_REPORT.md** - This comprehensive report  
✅ **File fingerprints** - SHA256 hashes verified (no modifications)  
✅ **Expected schema documented** - Complete column list from code  
✅ **Query templates** - Ready to execute when access restored  

---

## 🔐 INTEGRITY CONFIRMATION

**Audit Type:** READ-ONLY ✅  
**Files Modified:** 0 ✅  
**Database Writes:** 0 ✅  
**Roadmap Changes:** 0 ✅  

**Files Read (Fingerprinted):**
- ✅ automated_signals_api.py
- ✅ automated_signals_api_robust.py
- ✅ automated_signals_state.py
- ✅ web_server.py (grep search only)

**No modifications made to any files.**

---

**END OF H1.4 CHUNK 2 SNAPSHOT REPORT**

*Generated: November 27, 2025*  
*Status: API Access Issues - Cannot Complete Live Snapshot*  
*Recommendation: Fix API endpoints or use direct database connection*  
*Next Chunk: H1.4 Chunk 3 - Pending resolution of data access*
