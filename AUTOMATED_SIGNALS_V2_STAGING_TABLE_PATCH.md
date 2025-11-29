# ✅ STRICT PATCH REPORT: automated_signals_v2 Staging Table

## File Hash Changes
| Metric | Value |
|--------|-------|
| **OLD HASH** | `58D97D4C8D2292EFFB3D54A2F781B788` |
| **NEW HASH** | `DE9B7F8649E274200256C7A641C1BC37` |
| **File** | `web_server.py` |

---

## Patch Details

### 1. Feature Flag Addition
**Location:** Line 63 (after `ENABLE_TELEMETRY_LEGACY`)

```python
ENABLE_SCHEMA_V2 = os.environ.get("ENABLE_SCHEMA_V2", "false").lower() == "true"
```

**Default:** `false` (table creation skipped until manually enabled)

---

### 2. Table Creation Block
**Location:** Lines 11522-11548 (within `create_automated_signals_table()` function)

**Insertion Point:** After lifecycle columns ALTER TABLE, before `conn.commit()`

```python
# Create automated_signals_v2 staging table (H1.7 Foundation - GATED)
# This is an INACTIVE staging table for future migration planning only
# NOT referenced by any application code, NOT replacing automated_signals
if ENABLE_SCHEMA_V2:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS automated_signals_v2 (
            id SERIAL PRIMARY KEY,
            trade_id VARCHAR(64) NOT NULL,
            event_type VARCHAR(32) NOT NULL,
            timestamp TIMESTAMPTZ NOT NULL,
            signal_date DATE,
            signal_time TIMETZ,
            direction VARCHAR(16),
            session VARCHAR(16),
            bias VARCHAR(32),
            entry_price NUMERIC(12,4),
            stop_loss NUMERIC(12,4),
            current_price NUMERIC(12,4),
            exit_price NUMERIC(12,4),
            mfe NUMERIC(10,4),
            no_be_mfe NUMERIC(10,4),
            be_mfe NUMERIC(10,4),
            final_mfe NUMERIC(10,4),
            risk_distance NUMERIC(12,4),
            targets JSONB,
            telemetry JSONB
        );
    ''')
```

---

## Verification Checklist

| Check | Status | Evidence |
|-------|--------|----------|
| **Feature flag added** | ✅ | Line 63: `ENABLE_SCHEMA_V2 = os.environ.get(...)` |
| **Default is false** | ✅ | `"false"` in default parameter |
| **Table creation gated** | ✅ | `if ENABLE_SCHEMA_V2:` guard |
| **Schema matches spec** | ✅ | All 20 columns exactly as specified |
| **No INSERT references** | ✅ | All INSERTs use `automated_signals` only |
| **No SELECT references** | ✅ | All SELECTs use `automated_signals` only |
| **No API references** | ✅ | `automated_signals_v2` only in CREATE TABLE |
| **No dual-writing** | ✅ | No runtime logic touches v2 table |

---

## Impact Assessment

| Component | Modified? | Notes |
|-----------|-----------|-------|
| **Ingestion Logic** | ❌ NO | All webhook handlers unchanged |
| **API Endpoints** | ❌ NO | All routes use original table |
| **H1 Modules** | ❌ NO | No functional changes |
| **Runtime Paths** | ❌ NO | No dual-writing or migrations |
| **Database Setup** | ✅ YES | Added gated table creation only |

---

## Activation Instructions

To activate the staging table (when ready for migration planning):

```bash
# Set environment variable
export ENABLE_SCHEMA_V2=true

# Restart application or call the table creation endpoint
curl -X POST https://web-production-cd33.up.railway.app/api/create-automated-signals-table
```

**⚠️ WARNING:** This only creates the empty staging table. No data will be written to it until explicit migration logic is implemented.

---

## Status

**✅ STRICT PATCH APPLIED SUCCESSFULLY**

- Table creation is **INACTIVE** by default
- No application logic modified
- Safe for production deployment
- Ready for future migration planning

---

*Patch applied: November 29, 2025*
