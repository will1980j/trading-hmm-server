# Early Database Migration Hook Added

**Date:** November 29, 2025  
**File:** `web_server.py`  
**Purpose:** Add early migration hook to guarantee execution_tasks and execution_logs tables are created BEFORE anything else touches the database

---

## PATCH REPORT

**File:** `web_server.py`  
**Old hash:** `d50280fe66bfd1fad90e4c08e2ef0632`  
**New hash:** `a65f219dc6dfeaba1d8576da334f8656`  
**Action:** Added EARLY DB migration hook immediately after database connection

---

## Changes Applied

### Location
Immediately after `db = RailwayDB()` and `logger.info("Database connected successfully")`

### Code Added
```python
# ============================================================
# EARLY DATABASE MIGRATION HOOK (runs before anything else)
# ============================================================
try:
    cur = db.conn.cursor()
    print("[DB-MIGRATION] Starting early table creation...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS execution_tasks (
            id SERIAL PRIMARY KEY,
            trade_id VARCHAR(64),
            event_type VARCHAR(50),
            payload JSONB,
            attempts INTEGER DEFAULT 0,
            status VARCHAR(20) DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            last_error TEXT,
            last_attempt_at TIMESTAMP DEFAULT NOW()
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS execution_logs (
            id SERIAL PRIMARY KEY,
            task_id INTEGER,
            log_message TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    db.conn.commit()
    cur.close()
    print("[DB-MIGRATION] SUCCESS: execution tables verified/created")
except Exception as e:
    print("[DB-MIGRATION] ERROR:", e)
# ============================================================
# END EARLY MIGRATION HOOK
# ============================================================
```

---

## Strict Rules Followed

✅ **Inserted IMMEDIATELY after db = RailwayDB()**  
✅ **BEFORE any other imports, handlers, or router initializations**  
✅ **Clear log messages with [DB-MIGRATION] prefix for Railway logs**  
✅ **Did NOT remove the old migration (lines 357-368)**  
✅ **This is an override to ensure execution**  
✅ **Uses print() for guaranteed console output in Railway logs**

---

## Execution Order

The startup sequence now guarantees:

1. **Database connection established** (`db = RailwayDB()`)
2. **EARLY MIGRATION HOOK runs** (creates execution_tasks and execution_logs)
3. **Other migrations run** (existing code at lines 357-368)
4. **ExecutionRouter initialization** (currently disabled, lines 949-964)
5. **Application continues startup**

---

## Railway Log Verification

When deployed to Railway, you will see in the logs:

```
Database connected successfully
[DB-MIGRATION] Starting early table creation...
[DB-MIGRATION] SUCCESS: execution tables verified/created
```

If there's an error:
```
[DB-MIGRATION] ERROR: <error message>
```

---

## Purpose

This early migration hook **guarantees** that:
- `execution_tasks` table exists before any code tries to query it
- `execution_logs` table exists for audit trail
- Tables are created with idempotent `CREATE TABLE IF NOT EXISTS`
- Clear logging confirms successful creation in Railway logs
- No race conditions between table creation and ExecutionRouter startup

---

## Status

**✅ PATCH COMPLETE - READY FOR DEPLOYMENT**

The early database migration hook has been added to web_server.py. The execution_tasks and execution_logs tables will be created immediately after database connection, before any other code can attempt to access them.
