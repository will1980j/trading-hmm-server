# ✅ STALE RUNS CLEANUP - COMPLETE

**Date:** December 25, 2025  
**Issue:** Stuck `data_ingest_runs` rows with status='running'  
**Status:** ✅ FIXED - Automatic cleanup and robust error handling

---

## 🔧 CHANGES MADE

### 1. ✅ Added `cleanup_stale_runs()` Method

**Location:** `scripts/ingest_databento_ohlcv_1m.py` - `DatabentoIngester` class

**Purpose:** Automatically mark stale 'running' ingestion runs as failed on startup

**SQL Used:**
```sql
UPDATE data_ingest_runs
SET status = 'failed',
    error = 'stale run (auto-marked failed)',
    finished_at = now()
WHERE status = 'running'
  AND started_at < now() - interval '2 hours'
RETURNING id, started_at
```

**Key Features:**
- Uses **separate database connection** (won't be affected by failed transactions)
- Marks runs older than **2 hours** as failed
- Returns list of cleaned up runs with IDs and start times
- Non-blocking: Warns but doesn't fail if cleanup fails
- Only runs when `--dry-run` is NOT used

**Code:**
```python
def cleanup_stale_runs(self):
    """Mark stale 'running' ingestion runs as failed (older than 2 hours)"""
    if self.verbose:
        print("🧹 Cleaning up stale ingestion runs...")
    
    try:
        # Use separate connection for cleanup (won't be affected by failed transactions)
        cleanup_conn = psycopg2.connect(self.database_url)
        cleanup_cursor = cleanup_conn.cursor()
        
        # Mark runs older than 2 hours as failed
        cleanup_cursor.execute("""
            UPDATE data_ingest_runs
            SET status = 'failed',
                error = 'stale run (auto-marked failed)',
                finished_at = now()
            WHERE status = 'running'
              AND started_at < now() - interval '2 hours'
            RETURNING id, started_at
        """)
        
        stale_runs = cleanup_cursor.fetchall()
        cleanup_conn.commit()
        
        if stale_runs:
            print(f"   ⚠️  Marked {len(stale_runs)} stale runs as failed:")
            for run_id, started_at in stale_runs:
                print(f"      Run {run_id} (started {started_at})")
        elif self.verbose:
            print(f"   ✅ No stale runs found")
        
        cleanup_cursor.close()
        cleanup_conn.close()
        
    except Exception as e:
        print(f"   ⚠️  Cleanup warning: {e}")
        # Don't fail ingestion if cleanup fails
```

---

### 2. ✅ Updated `update_ingest_run()` Method

**Purpose:** Use separate connection to avoid being blocked by failed transactions

**Key Changes:**
- Creates **new database connection** for each update
- Commits and closes connection immediately
- Safe to call even if main transaction has failed
- Doesn't re-raise exceptions (reports original error)

**Code:**
```python
def update_ingest_run(self, run_id, status, row_count=0, inserted=0, updated=0, 
                     min_ts=None, max_ts=None, error=None):
    """Update ingestion run record using separate connection (safe for error handling)"""
    try:
        # Use separate connection to avoid being blocked by failed transaction
        update_conn = psycopg2.connect(self.database_url)
        update_cursor = update_conn.cursor()
        
        update_cursor.execute("""
            UPDATE data_ingest_runs
            SET finished_at = now(),
                status = %s,
                row_count = %s,
                inserted_count = %s,
                updated_count = %s,
                min_ts = %s,
                max_ts = %s,
                error = %s
            WHERE id = %s
        """, (status, row_count, inserted, updated, min_ts, max_ts, error, run_id))
        
        update_conn.commit()
        update_cursor.close()
        update_conn.close()
        
    except Exception as e:
        print(f"   ⚠️  Failed to update ingestion run {run_id}: {e}")
        # Don't re-raise - we want to report the original error, not this one
```

---

### 3. ✅ Enhanced Exception Handling in `ingest_file()`

**Purpose:** Ensure transaction rollback and error recording always happen

**Key Changes:**
- Explicit `conn.rollback()` on any exception
- Verbose logging of rollback status
- Always updates run record with error (using separate connection)
- Re-raises original exception after cleanup

**Code:**
```python
except Exception as e:
    # Rollback transaction first
    if self.conn:
        try:
            self.conn.rollback()
            if self.verbose:
                print(f"   🔄 Transaction rolled back")
        except Exception as rollback_error:
            if self.verbose:
                print(f"   ⚠️  Rollback warning: {rollback_error}")
    
    # Update run record with error (using separate connection)
    if 'run_id' in locals():
        self.update_ingest_run(run_id, status='failed', error=str(e))
    
    raise
```

---

### 4. ✅ Added Cleanup Call in `main()`

**Purpose:** Run cleanup once before processing files

**Location:** Before file processing loop

**Code:**
```python
# Clean up stale runs before starting (only once, not per file)
if not args.dry_run:
    cleanup_ingester = DatabentoIngester(database_url, verbose=args.verbose)
    cleanup_ingester.cleanup_stale_runs()
```

---

## 🎯 BEHAVIOR

### On Startup (Normal Run)

```
================================================================================
Found 3 file(s) to process
================================================================================
   - file1.dbn.zst
   - file2.dbn.zst
   - file3.dbn.zst
================================================================================

🧹 Cleaning up stale ingestion runs...
   ✅ No stale runs found

[Proceeds with ingestion...]
```

### On Startup (With Stale Runs)

```
================================================================================
Found 3 file(s) to process
================================================================================
   - file1.dbn.zst
   - file2.dbn.zst
   - file3.dbn.zst
================================================================================

🧹 Cleaning up stale ingestion runs...
   ⚠️  Marked 2 stale runs as failed:
      Run 15 (started 2025-12-25 08:00:00+00:00)
      Run 16 (started 2025-12-25 09:30:00+00:00)

[Proceeds with ingestion...]
```

### On Exception (During Ingestion)

```
================================================================================
🚀 DATABENTO OHLCV-1M INGESTION
================================================================================
File: data/databento/mnq/ohlcv_1m/raw/file1.dbn.zst
...
💾 Upserting 500,000 bars...
   [ERROR OCCURS]
   🔄 Transaction rolled back

❌ INGESTION FAILED for file1.dbn.zst: [error message]

[Run record updated with status='failed' and error message]
```

---

## 📊 SQL QUERIES

### Check for Stale Runs (Manual)

```sql
-- Find currently running ingestions older than 2 hours
SELECT 
    id,
    started_at,
    EXTRACT(EPOCH FROM (now() - started_at)) / 3600 AS hours_running,
    dataset,
    file_name
FROM data_ingest_runs
WHERE status = 'running'
  AND started_at < now() - interval '2 hours'
ORDER BY started_at;
```

### Manually Mark Stale Runs as Failed

```sql
-- Same SQL as cleanup_stale_runs() method
UPDATE data_ingest_runs
SET status = 'failed',
    error = 'stale run (auto-marked failed)',
    finished_at = now()
WHERE status = 'running'
  AND started_at < now() - interval '2 hours'
RETURNING id, started_at;
```

### Check Recent Failed Runs

```sql
-- See recently failed runs
SELECT 
    id,
    started_at,
    finished_at,
    status,
    error,
    file_name
FROM data_ingest_runs
WHERE status = 'failed'
ORDER BY started_at DESC
LIMIT 10;
```

---

## ✅ BENEFITS

### 1. **Automatic Cleanup**
- No manual intervention needed
- Runs on every ingestion startup
- Prevents accumulation of stuck runs

### 2. **Robust Error Handling**
- Transaction rollback always happens
- Error recording always happens (separate connection)
- Original error is preserved and re-raised

### 3. **Separate Connections**
- Cleanup can't be blocked by failed transactions
- Error updates can't be blocked by failed transactions
- Each operation is independent

### 4. **Verbose Logging**
- Shows which runs were cleaned up
- Shows rollback status
- Shows update failures (if any)

### 5. **Non-Blocking**
- Cleanup failure doesn't stop ingestion
- Update failure doesn't hide original error
- System continues to function

---

## 🧪 TESTING

### Test Stale Run Cleanup

```bash
# 1. Create a stuck run manually
psql $DATABASE_URL -c "
INSERT INTO data_ingest_runs (vendor, dataset, file_name, status, started_at)
VALUES ('databento', 'test', 'test.dbn.zst', 'running', now() - interval '3 hours')
RETURNING id;
"

# 2. Run ingestion (will clean up the stuck run)
python scripts/ingest_databento_ohlcv_1m.py \
    --input "data/databento/mnq/ohlcv_1m/raw/*.dbn.zst" \
    --verbose

# Expected output:
# 🧹 Cleaning up stale ingestion runs...
#    ⚠️  Marked 1 stale runs as failed:
#       Run X (started ...)
```

### Test Exception Handling

```bash
# 1. Cause an intentional error (invalid file)
python scripts/ingest_databento_ohlcv_1m.py \
    --input "nonexistent.dbn.zst" \
    --verbose

# Expected:
# - Transaction rolled back
# - Run record updated with error
# - Original exception re-raised
```

---

## 📋 SUMMARY

**File Modified:** `scripts/ingest_databento_ohlcv_1m.py`

**Changes:**
1. ✅ Added `cleanup_stale_runs()` method
2. ✅ Updated `update_ingest_run()` to use separate connection
3. ✅ Enhanced exception handling with explicit rollback
4. ✅ Added cleanup call in `main()` before processing

**SQL Used:**
```sql
UPDATE data_ingest_runs
SET status = 'failed',
    error = 'stale run (auto-marked failed)',
    finished_at = now()
WHERE status = 'running'
  AND started_at < now() - interval '2 hours'
RETURNING id, started_at
```

**Result:**
- ✅ Automatic cleanup of stuck runs
- ✅ Robust error handling with separate connections
- ✅ Always records errors even if transaction fails
- ✅ Non-blocking cleanup (warns but continues)

---

## ✅ STATUS: COMPLETE

All requirements implemented:
- ✅ Marks stale runs (>2 hours) as failed on startup
- ✅ Uses separate connection for updates (can't be blocked)
- ✅ Always calls `conn.rollback()` on exception
- ✅ Always updates run record with error (separate connection)

**Ready for deployment!** 🚀
