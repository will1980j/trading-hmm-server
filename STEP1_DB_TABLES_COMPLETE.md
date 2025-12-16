# ✅ Step 1 Complete - Database Tables Added

## Files Created

### 1. Schema File
**File:** `database/indicator_export_schema.sql`
**Purpose:** SQL definitions for indicator export tables

### 2. Migration Script
**File:** `database/run_indicator_export_migration.py`
**Purpose:** Python script to execute the migration

## Tables Added

### A) indicator_export_batches (Raw Envelope Storage)
**Purpose:** Immutable audit trail of "what TradingView actually said"

```sql
CREATE TABLE IF NOT EXISTS indicator_export_batches (
    id BIGSERIAL PRIMARY KEY,
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source TEXT NOT NULL DEFAULT 'tradingview',
    event_type TEXT NOT NULL,  -- INDICATOR_EXPORT_V2, ALL_SIGNALS_EXPORT
    batch_number INTEGER NULL,
    batch_size INTEGER NULL,
    total_signals INTEGER NULL,
    payload_json JSONB NOT NULL,  -- Full request body
    payload_sha256 TEXT NOT NULL,  -- Deduplication hash
    is_valid BOOLEAN DEFAULT FALSE,
    validation_error TEXT NULL,
    UNIQUE(event_type, payload_sha256)
);
```

**Indexes:**
- `idx_export_batches_received_at` (DESC)
- `idx_export_batches_event_type`
- `idx_export_batches_is_valid`

### B) all_signals_ledger (Canonical All Signals Table)
**Purpose:** Triangle-keyed truth table for "All Signals" tab

```sql
CREATE TABLE IF NOT EXISTS all_signals_ledger (
    trade_id TEXT PRIMARY KEY,  -- Triangle-canonical ID
    triangle_time_ms BIGINT NOT NULL,
    confirmation_time_ms BIGINT NULL,
    direction TEXT NOT NULL,  -- Bullish/Bearish
    status TEXT NOT NULL,  -- PENDING/CONFIRMED/CANCELLED/COMPLETED
    bars_to_confirm INTEGER NULL,
    session TEXT NULL,
    entry_price NUMERIC(10, 2) NULL,
    stop_loss NUMERIC(10, 2) NULL,
    risk_points NUMERIC(10, 2) NULL,
    htf_daily TEXT NULL,
    htf_4h TEXT NULL,
    htf_1h TEXT NULL,
    htf_15m TEXT NULL,
    htf_5m TEXT NULL,
    htf_1m TEXT NULL,
    last_seen_batch_id BIGINT NULL REFERENCES indicator_export_batches(id),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**Indexes:**
- `idx_all_signals_triangle_time` (DESC)
- `idx_all_signals_status`
- `idx_all_signals_direction`
- `idx_all_signals_updated_at` (DESC)

### C) confirmed_signals_ledger (Canonical Confirmed Signals Table)
**Purpose:** Triangle-keyed truth table for "Confirmed Signals" tab with MFE/MAE

```sql
CREATE TABLE IF NOT EXISTS confirmed_signals_ledger (
    trade_id TEXT PRIMARY KEY,  -- Triangle-canonical ID
    triangle_time_ms BIGINT NOT NULL,
    confirmation_time_ms BIGINT NULL,
    date DATE NULL,
    session TEXT NULL,
    direction TEXT NOT NULL,  -- Bullish/Bearish
    entry NUMERIC(10, 2) NULL,
    stop NUMERIC(10, 2) NULL,
    be_mfe NUMERIC(10, 4) NULL,
    no_be_mfe NUMERIC(10, 4) NULL,
    mae NUMERIC(10, 4) NULL,
    completed BOOLEAN NULL,
    last_seen_batch_id BIGINT NULL REFERENCES indicator_export_batches(id),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**Indexes:**
- `idx_confirmed_signals_date` (DESC)
- `idx_confirmed_signals_session`
- `idx_confirmed_signals_completed`
- `idx_confirmed_signals_triangle_time` (DESC)
- `idx_confirmed_signals_updated_at` (DESC)

## Existing Table

### automated_signals (Already Exists)
**Location:** `database/add_automated_signal_support.sql`
**Purpose:** Event-based storage (multiple rows per trade_id)
**Status:** No changes made (as instructed)

## Architecture

### Two-Layer Design
1. **Raw Layer** - `indicator_export_batches`
   - Immutable storage
   - Full payload preservation
   - Deduplication via SHA256
   - Validation tracking

2. **Canonical Layer** - `all_signals_ledger` + `confirmed_signals_ledger`
   - Triangle-keyed (one row per trade_id)
   - Dashboard truth tables
   - Idempotent updates
   - References back to raw batches

## How to Run Migration

### Option 1: Python Script
```bash
python database/run_indicator_export_migration.py
```

### Option 2: Direct SQL
```bash
# Copy SQL from database/indicator_export_schema.sql
# Paste into Railway PostgreSQL console
# Execute
```

### Option 3: Via Web Endpoint (if you have one)
```python
# Add to web_server.py if needed
@app.route('/api/admin/run-migration')
def run_migration():
    # Execute schema SQL
    pass
```

## Verification

After running migration, verify:
```sql
-- Check tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_name IN ('indicator_export_batches', 'all_signals_ledger', 'confirmed_signals_ledger');

-- Check indexes exist
SELECT tablename, indexname FROM pg_indexes 
WHERE tablename IN ('indicator_export_batches', 'all_signals_ledger', 'confirmed_signals_ledger');

-- Check row counts (should be 0 initially)
SELECT 'indicator_export_batches' as table_name, COUNT(*) FROM indicator_export_batches
UNION ALL
SELECT 'all_signals_ledger', COUNT(*) FROM all_signals_ledger
UNION ALL
SELECT 'confirmed_signals_ledger', COUNT(*) FROM confirmed_signals_ledger;
```

## Next Steps

After tables are created:
1. **Step 2:** Create import endpoint to receive indicator exports
2. **Step 3:** Parse and validate incoming batches
3. **Step 4:** Upsert into canonical ledgers
4. **Step 5:** Update dashboard to query ledgers

## Notes

- All tables use `IF NOT EXISTS` (safe to re-run)
- No existing tables modified
- No data loss risk
- Idempotent migration
- Foreign key constraints ensure referential integrity
- Indexes optimize dashboard queries

**Ready to run migration.** 🚀
