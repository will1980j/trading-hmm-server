# Automated Signals Schema Gap Analysis (H1.7)

## Overview

This document analyzes the gap between the documented `automated_signals` schema in `docs/db_schema_reference.md` and the actual code-level implementation in `web_server.py`. It provides field-by-field disposition recommendations and a proposed clean H1.7 schema.

---

## 1. Schema Comparison Table

### Documented Schema vs Code Schema

| Field | Documented Type | Code Type | Status | Disposition |
|-------|-----------------|-----------|--------|-------------|
| `id` | SERIAL PRIMARY KEY | SERIAL PRIMARY KEY | ✅ Match | **KEEP** |
| `trade_id` | VARCHAR(64) NOT NULL | VARCHAR(100) NOT NULL | ⚠️ Size mismatch | **KEEP** (standardize to 64) |
| `event_type` | VARCHAR(32) NOT NULL | VARCHAR(20) NOT NULL | ⚠️ Size mismatch | **KEEP** (standardize to 32) |
| `timestamp` | TIMESTAMPTZ NOT NULL | BIGINT | ⚠️ Type mismatch | **KEEP** (use TIMESTAMPTZ) |
| `signal_date` | DATE | Not in CREATE | ❌ Missing | **KEEP** (add to schema) |
| `signal_time` | TIMETZ | Not in CREATE | ❌ Missing | **KEEP** (add to schema) |
| `direction` | VARCHAR(16) | VARCHAR(10) | ⚠️ Size mismatch | **KEEP** (standardize to 16) |
| `session` | VARCHAR(16) | VARCHAR(20) | ⚠️ Size mismatch | **KEEP** (standardize to 20) |
| `bias` | VARCHAR(32) | VARCHAR(20) | ⚠️ Size mismatch | **KEEP** (standardize to 32) |
| `entry_price` | NUMERIC(12,4) | DECIMAL(10,2) | ⚠️ Type/precision | **KEEP** (use NUMERIC(12,4)) |
| `stop_loss` | NUMERIC(12,4) | DECIMAL(10,2) | ⚠️ Type/precision | **KEEP** (use NUMERIC(12,4)) |
| `current_price` | NUMERIC(12,4) | DECIMAL(10,2) | ⚠️ Type/precision | **KEEP** (use NUMERIC(12,4)) |
| `exit_price` | NUMERIC(12,4) | DECIMAL(10,2) | ⚠️ Type/precision | **KEEP** (use NUMERIC(12,4)) |
| `mfe` | NUMERIC(10,4) | DECIMAL(10,4) | ✅ Match | **KEEP** |
| `no_be_mfe` | NUMERIC(10,4) | FLOAT | ⚠️ Type mismatch | **KEEP** (use NUMERIC(10,4)) |
| `be_mfe` | NUMERIC(10,4) | FLOAT | ⚠️ Type mismatch | **KEEP** (use NUMERIC(10,4)) |
| `final_mfe` | NUMERIC(10,4) | DECIMAL(10,4) | ✅ Match | **KEEP** |
| `risk_distance` | NUMERIC(12,4) | DECIMAL(10,2) | ⚠️ Type/precision | **KEEP** (use NUMERIC(12,4)) |
| `targets` | JSONB | Not present | ❌ Missing | **KEEP** (add to schema) |
| `telemetry` | JSONB | Added via ALTER | ⚠️ Partial | **KEEP** |

### Undocumented Fields in Code (Require Disposition)

| Field | Code Type | Source | Disposition | Destination |
|-------|-----------|--------|-------------|-------------|
| `target_1r` | DECIMAL(10,2) | CREATE TABLE | **MOVE** | `targets` JSONB |
| `target_2r` | DECIMAL(10,2) | CREATE TABLE | **MOVE** | `targets` JSONB |
| `target_3r` | DECIMAL(10,2) | CREATE TABLE | **MOVE** | `targets` JSONB |
| `target_5r` | DECIMAL(10,2) | CREATE TABLE | **MOVE** | `targets` JSONB |
| `target_10r` | DECIMAL(10,2) | CREATE TABLE | **MOVE** | `targets` JSONB |
| `target_20r` | DECIMAL(10,2) | CREATE TABLE | **MOVE** | `targets` JSONB |
| `account_size` | DECIMAL(15,2) | CREATE TABLE | **MOVE** | `telemetry` JSONB |
| `risk_percent` | DECIMAL(5,2) | CREATE TABLE | **MOVE** | `telemetry` JSONB |
| `contracts` | INTEGER | CREATE TABLE | **MOVE** | `telemetry` JSONB |
| `risk_amount` | DECIMAL(10,2) | CREATE TABLE | **MOVE** | `telemetry` JSONB |
| `created_at` | TIMESTAMP | CREATE TABLE | **DELETE** | Redundant with `timestamp` |
| `lifecycle_state` | VARCHAR(40) | ALTER TABLE | **MOVE** | Separate lifecycle table (H2) |
| `lifecycle_seq` | INTEGER | ALTER TABLE | **MOVE** | Separate lifecycle table (H2) |
| `lifecycle_entered_at` | TIMESTAMP | ALTER TABLE | **MOVE** | Separate lifecycle table (H2) |
| `lifecycle_updated_at` | TIMESTAMP | ALTER TABLE | **MOVE** | Separate lifecycle table (H2) |

---

## 2. Field Disposition Summary

### KEEP (Core H1.7 Schema) - 20 fields

These fields belong in the final `automated_signals` table:

| Field | Final Type | Notes |
|-------|------------|-------|
| `id` | SERIAL PRIMARY KEY | Identity |
| `trade_id` | VARCHAR(64) NOT NULL | Trade identifier |
| `event_type` | VARCHAR(32) NOT NULL | ENTRY, MFE_UPDATE, EXIT, etc. |
| `timestamp` | TIMESTAMPTZ NOT NULL | Event timestamp |
| `signal_date` | DATE | Extracted date for partitioning |
| `signal_time` | TIMETZ | Extracted time for analysis |
| `direction` | VARCHAR(16) | Bullish/Bearish |
| `session` | VARCHAR(20) | ASIA, LONDON, NY AM, etc. |
| `bias` | VARCHAR(32) | HTF bias alignment |
| `entry_price` | NUMERIC(12,4) | Entry price |
| `stop_loss` | NUMERIC(12,4) | Stop loss price |
| `current_price` | NUMERIC(12,4) | Current/latest price |
| `exit_price` | NUMERIC(12,4) | Exit price (on completion) |
| `mfe` | NUMERIC(10,4) | Maximum favorable excursion |
| `no_be_mfe` | NUMERIC(10,4) | MFE without break-even |
| `be_mfe` | NUMERIC(10,4) | MFE with break-even |
| `final_mfe` | NUMERIC(10,4) | Final MFE at resolution |
| `risk_distance` | NUMERIC(12,4) | Entry to stop distance |
| `targets` | JSONB | R-multiple targets (1R-20R) |
| `telemetry` | JSONB | Position sizing, context data |

### MOVE (To Other Tables) - 10 fields

| Field | Current Location | Target Location | Rationale |
|-------|------------------|-----------------|-----------|
| `target_1r` through `target_20r` | automated_signals | `targets` JSONB column | Consolidate into single JSONB |
| `account_size` | automated_signals | `telemetry` JSONB | Position sizing metadata |
| `risk_percent` | automated_signals | `telemetry` JSONB | Position sizing metadata |
| `contracts` | automated_signals | `telemetry` JSONB | Position sizing metadata |
| `risk_amount` | automated_signals | `telemetry` JSONB | Position sizing metadata |
| `lifecycle_state` | automated_signals | H2 lifecycle table | State machine tracking |
| `lifecycle_seq` | automated_signals | H2 lifecycle table | State machine tracking |
| `lifecycle_entered_at` | automated_signals | H2 lifecycle table | State machine tracking |
| `lifecycle_updated_at` | automated_signals | H2 lifecycle table | State machine tracking |

### DELETE (Legacy/Unused) - 1 field

| Field | Reason |
|-------|--------|
| `created_at` | Redundant with `timestamp` column |

---

## 3. Missing Fields Analysis

### Required in Final Schema (Missing from Code CREATE TABLE)

| Field | Required Type | Currently | Action Needed |
|-------|---------------|-----------|---------------|
| `signal_date` | DATE | Added via ALTER in some scripts | Add to CREATE TABLE |
| `signal_time` | TIMETZ | Added via ALTER in some scripts | Add to CREATE TABLE |
| `targets` | JSONB | Not present | Add to CREATE TABLE |
| `telemetry` | JSONB | Added via ALTER (phase5) | Add to CREATE TABLE |

---

## 4. Undocumented Fields That Should NOT Remain

These fields exist in code but should be removed or relocated:

| Field | Current Status | Recommendation |
|-------|----------------|----------------|
| `target_1r` | Individual column | Consolidate into `targets` JSONB |
| `target_2r` | Individual column | Consolidate into `targets` JSONB |
| `target_3r` | Individual column | Consolidate into `targets` JSONB |
| `target_5r` | Individual column | Consolidate into `targets` JSONB |
| `target_10r` | Individual column | Consolidate into `targets` JSONB |
| `target_20r` | Individual column | Consolidate into `targets` JSONB |
| `account_size` | Individual column | Move to `telemetry` JSONB |
| `risk_percent` | Individual column | Move to `telemetry` JSONB |
| `contracts` | Individual column | Move to `telemetry` JSONB |
| `risk_amount` | Individual column | Move to `telemetry` JSONB |
| `created_at` | Redundant timestamp | Remove (use `timestamp`) |
| `lifecycle_*` | State machine columns | Move to H2 lifecycle table |

---

## 5. Proposed `automated_signals_v2` Schema (Clean H1.7)

```sql
-- ============================================================
-- AUTOMATED_SIGNALS_V2 - Clean H1.7 Foundation Schema
-- ============================================================
-- This is the canonical schema for the automated signals table.
-- All lifecycle events for every trade are stored here.
-- ============================================================

CREATE TABLE automated_signals_v2 (
    -- Identity
    id SERIAL PRIMARY KEY,
    
    -- Core Trade Identification
    trade_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(32) NOT NULL,
    
    -- Timestamps
    timestamp TIMESTAMPTZ NOT NULL,
    signal_date DATE,
    signal_time TIMETZ,
    
    -- Trade Classification
    direction VARCHAR(16),
    session VARCHAR(20),
    bias VARCHAR(32),
    
    -- Price Data
    entry_price NUMERIC(12,4),
    stop_loss NUMERIC(12,4),
    current_price NUMERIC(12,4),
    exit_price NUMERIC(12,4),
    
    -- MFE Tracking
    mfe NUMERIC(10,4),
    no_be_mfe NUMERIC(10,4),
    be_mfe NUMERIC(10,4),
    final_mfe NUMERIC(10,4),
    
    -- Risk Calculation
    risk_distance NUMERIC(12,4),
    
    -- Structured Data (JSONB)
    targets JSONB,      -- {"1R": 21050.25, "2R": 21075.50, ..., "20R": 21500.00}
    telemetry JSONB     -- {"account_size": 50000, "risk_percent": 1.0, "contracts": 2, ...}
);

-- ============================================================
-- INDEXES (H1.7 Indexing Plan)
-- ============================================================

CREATE INDEX idx_automated_signals_v2_trade_id 
    ON automated_signals_v2(trade_id);

CREATE INDEX idx_automated_signals_v2_timestamp 
    ON automated_signals_v2(timestamp DESC);

CREATE INDEX idx_automated_signals_v2_event_type 
    ON automated_signals_v2(event_type);

CREATE INDEX idx_automated_signals_v2_session_timestamp 
    ON automated_signals_v2(session, timestamp DESC);

CREATE INDEX idx_automated_signals_v2_signal_date 
    ON automated_signals_v2(signal_date);

CREATE INDEX idx_automated_signals_v2_direction 
    ON automated_signals_v2(direction);

-- ============================================================
-- COMMENTS
-- ============================================================

COMMENT ON TABLE automated_signals_v2 IS 
    'H1.7 Foundation: Lifecycle event store for all automated trades';

COMMENT ON COLUMN automated_signals_v2.trade_id IS 
    'Unique trade identifier (format: YYYYMMDD_HHMMSS_DIRECTION)';

COMMENT ON COLUMN automated_signals_v2.event_type IS 
    'Event type: ENTRY, MFE_UPDATE, BE_TRIGGERED, EXIT_SL, EXIT_TARGET';

COMMENT ON COLUMN automated_signals_v2.targets IS 
    'JSONB containing R-multiple price targets (1R through 20R)';

COMMENT ON COLUMN automated_signals_v2.telemetry IS 
    'JSONB containing position sizing and market context metadata';
```

---

## 6. Safe Migration Path

### Step 1: Create `automated_signals_v2` Table

```sql
-- Create new table with clean schema
-- Run this FIRST before any other migration steps

CREATE TABLE automated_signals_v2 (
    id SERIAL PRIMARY KEY,
    trade_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(32) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    signal_date DATE,
    signal_time TIMETZ,
    direction VARCHAR(16),
    session VARCHAR(20),
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

-- Create indexes
CREATE INDEX idx_asv2_trade_id ON automated_signals_v2(trade_id);
CREATE INDEX idx_asv2_timestamp ON automated_signals_v2(timestamp DESC);
CREATE INDEX idx_asv2_event_type ON automated_signals_v2(event_type);
```

### Step 2: Dual-Write During Transition (Optional)

```python
# In webhook handler, write to BOTH tables during transition period
# This ensures no data loss during migration

def handle_webhook(payload):
    # Write to old table (existing logic)
    insert_to_automated_signals(payload)
    
    # Write to new table (parallel)
    insert_to_automated_signals_v2(payload)
```

**Duration:** 1-2 weeks of parallel writes to validate data consistency.

### Step 3: Migrate Historical Rows

```sql
-- Migrate historical data from automated_signals to automated_signals_v2
-- Run during low-traffic period

INSERT INTO automated_signals_v2 (
    trade_id,
    event_type,
    timestamp,
    signal_date,
    signal_time,
    direction,
    session,
    bias,
    entry_price,
    stop_loss,
    current_price,
    exit_price,
    mfe,
    no_be_mfe,
    be_mfe,
    final_mfe,
    risk_distance,
    targets,
    telemetry
)
SELECT 
    trade_id,
    event_type,
    -- Convert BIGINT timestamp to TIMESTAMPTZ
    to_timestamp(timestamp / 1000.0) AT TIME ZONE 'America/New_York',
    -- Extract date/time
    (to_timestamp(timestamp / 1000.0) AT TIME ZONE 'America/New_York')::DATE,
    (to_timestamp(timestamp / 1000.0) AT TIME ZONE 'America/New_York')::TIMETZ,
    direction,
    session,
    bias,
    entry_price,
    stop_loss,
    current_price,
    exit_price,
    mfe,
    no_be_mfe,
    be_mfe,
    final_mfe,
    risk_distance,
    -- Consolidate target columns into JSONB
    jsonb_build_object(
        '1R', target_1r,
        '2R', target_2r,
        '3R', target_3r,
        '5R', target_5r,
        '10R', target_10r,
        '20R', target_20r
    ),
    -- Consolidate position sizing into telemetry JSONB
    jsonb_build_object(
        'account_size', account_size,
        'risk_percent', risk_percent,
        'contracts', contracts,
        'risk_amount', risk_amount
    )
FROM automated_signals
WHERE trade_id NOT IN (SELECT trade_id FROM automated_signals_v2);
```

### Step 4: Swap References

```python
# Phase 4A: Update API endpoints to read from v2
# File: web_server.py

# Before:
# cursor.execute("SELECT * FROM automated_signals WHERE ...")

# After:
# cursor.execute("SELECT * FROM automated_signals_v2 WHERE ...")

# Phase 4B: Update webhook handler to write to v2 only
# Remove dual-write logic

# Phase 4C: Rename tables (final cutover)
# ALTER TABLE automated_signals RENAME TO automated_signals_legacy;
# ALTER TABLE automated_signals_v2 RENAME TO automated_signals;

# Phase 4D: Drop legacy table (after validation period)
# DROP TABLE automated_signals_legacy;
```

---

## 7. Migration Timeline

| Phase | Duration | Description |
|-------|----------|-------------|
| **Step 1** | Day 1 | Create `automated_signals_v2` table |
| **Step 2** | Days 2-14 | Dual-write period (optional) |
| **Step 3** | Day 15 | Migrate historical data |
| **Step 4A** | Day 16 | Switch reads to v2 |
| **Step 4B** | Day 17 | Switch writes to v2 only |
| **Step 4C** | Day 18 | Rename tables |
| **Step 4D** | Day 30+ | Drop legacy table |

---

## 8. Validation Checklist

Before completing migration:

- [ ] Row counts match between old and new tables
- [ ] All trade_ids present in both tables
- [ ] Timestamp conversion verified (BIGINT → TIMESTAMPTZ)
- [ ] JSONB consolidation verified (targets, telemetry)
- [ ] API endpoints return identical data
- [ ] Dashboard displays correctly
- [ ] WebSocket events work correctly
- [ ] No data loss during dual-write period

---

## Notes

- This document is for analysis and planning only
- NO backend code or database tables were modified
- All changes require explicit approval before implementation
- Migration should be tested in staging environment first

---

**Document Created:** 2025-11-29
**Status:** ANALYSIS ONLY - NO PATCHES APPLIED
