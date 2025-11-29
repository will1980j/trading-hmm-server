# Automated Signals V2 Final Specification (H1.7)

## Document Purpose

This is the **authoritative final specification** for the `automated_signals_v2` table schema. It merges and supersedes:
- `docs/db_schema_reference.md` (H1.7 Foundation)
- `docs/automated_signals_schema_gap_analysis.md` (Gap Analysis)

All future development must conform to this specification.

---

## 1. Final Schema Definition

### 1.1 Table: `automated_signals_v2`

```sql
CREATE TABLE automated_signals_v2 (
    -- ═══════════════════════════════════════════════════════════════
    -- IDENTITY (Required)
    -- ═══════════════════════════════════════════════════════════════
    id                  SERIAL PRIMARY KEY,
    
    -- ═══════════════════════════════════════════════════════════════
    -- CORE TRADE IDENTIFICATION (Required)
    -- ═══════════════════════════════════════════════════════════════
    trade_id            VARCHAR(64) NOT NULL,
    event_type          VARCHAR(32) NOT NULL,
    
    -- ═══════════════════════════════════════════════════════════════
    -- TIMESTAMPS (Required: timestamp; Optional: signal_date, signal_time)
    -- ═══════════════════════════════════════════════════════════════
    timestamp           TIMESTAMPTZ NOT NULL,
    signal_date         DATE,
    signal_time         TIMETZ,
    
    -- ═══════════════════════════════════════════════════════════════
    -- TRADE CLASSIFICATION (Optional)
    -- ═══════════════════════════════════════════════════════════════
    direction           VARCHAR(16),
    session             VARCHAR(20),
    bias                VARCHAR(32),
    
    -- ═══════════════════════════════════════════════════════════════
    -- PRICE DATA (Optional - populated based on event_type)
    -- ═══════════════════════════════════════════════════════════════
    entry_price         NUMERIC(12,4),
    stop_loss           NUMERIC(12,4),
    current_price       NUMERIC(12,4),
    exit_price          NUMERIC(12,4),
    
    -- ═══════════════════════════════════════════════════════════════
    -- MFE TRACKING (Optional - populated based on event_type)
    -- ═══════════════════════════════════════════════════════════════
    mfe                 NUMERIC(10,4),
    no_be_mfe           NUMERIC(10,4),
    be_mfe              NUMERIC(10,4),
    final_mfe           NUMERIC(10,4),
    
    -- ═══════════════════════════════════════════════════════════════
    -- RISK CALCULATION (Optional)
    -- ═══════════════════════════════════════════════════════════════
    risk_distance       NUMERIC(12,4),
    
    -- ═══════════════════════════════════════════════════════════════
    -- STRUCTURED DATA (Optional - JSONB for flexibility)
    -- ═══════════════════════════════════════════════════════════════
    targets             JSONB,
    telemetry           JSONB
);
```

### 1.2 Column Specifications

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `id` | SERIAL PRIMARY KEY | ✅ Yes | Auto-incrementing row identifier |
| `trade_id` | VARCHAR(64) NOT NULL | ✅ Yes | Trade identifier (format: `YYYYMMDD_HHMMSS_DIRECTION`) |
| `event_type` | VARCHAR(32) NOT NULL | ✅ Yes | Event type (see Section 3) |
| `timestamp` | TIMESTAMPTZ NOT NULL | ✅ Yes | Event timestamp with timezone |
| `signal_date` | DATE | ❌ No | Extracted date for partitioning/filtering |
| `signal_time` | TIMETZ | ❌ No | Extracted time for analysis |
| `direction` | VARCHAR(16) | ❌ No | `Bullish` or `Bearish` |
| `session` | VARCHAR(20) | ❌ No | `ASIA`, `LONDON`, `NY PRE`, `NY AM`, `NY LUNCH`, `NY PM` |
| `bias` | VARCHAR(32) | ❌ No | HTF bias alignment |
| `entry_price` | NUMERIC(12,4) | ❌ No | Entry price (4 decimal precision) |
| `stop_loss` | NUMERIC(12,4) | ❌ No | Stop loss price |
| `current_price` | NUMERIC(12,4) | ❌ No | Current/latest price |
| `exit_price` | NUMERIC(12,4) | ❌ No | Exit price (on completion) |
| `mfe` | NUMERIC(10,4) | ❌ No | Maximum favorable excursion (R-multiple) |
| `no_be_mfe` | NUMERIC(10,4) | ❌ No | MFE without break-even strategy |
| `be_mfe` | NUMERIC(10,4) | ❌ No | MFE with break-even strategy |
| `final_mfe` | NUMERIC(10,4) | ❌ No | Final MFE at trade resolution |
| `risk_distance` | NUMERIC(12,4) | ❌ No | Entry to stop loss distance |
| `targets` | JSONB | ❌ No | R-multiple price targets |
| `telemetry` | JSONB | ❌ No | Position sizing and context metadata |

### 1.3 JSONB Structure: `targets`

```json
{
    "1R": 21050.2500,
    "2R": 21075.5000,
    "3R": 21100.7500,
    "5R": 21151.2500,
    "10R": 21277.5000,
    "20R": 21530.0000
}
```

**Requirements:**
- All values must be NUMERIC with 4 decimal precision
- Keys must be R-multiple labels (e.g., "1R", "2R", etc.)
- Minimum required: `1R` (break-even trigger)
- Maximum supported: `20R`

### 1.4 JSONB Structure: `telemetry`

```json
{
    "account_size": 50000.00,
    "risk_percent": 1.00,
    "contracts": 2,
    "risk_amount": 500.00,
    "htf_status": "Bullish",
    "htf_aligned": true,
    "signal_strength": 0.85,
    "atr": 25.50,
    "volatility": 0.0125,
    "indicator_version": "2.1.0",
    "webhook_source": "TradingView"
}
```

**Required Fields:**
- `account_size` (NUMERIC)
- `risk_percent` (NUMERIC)
- `contracts` (INTEGER)

**Optional Fields:**
- `risk_amount`, `htf_status`, `htf_aligned`, `signal_strength`, `atr`, `volatility`, `indicator_version`, `webhook_source`

---

## 2. Field Disposition Summary

### 2.1 KEEP Fields (Migrate Directly)

| Field | Source | Notes |
|-------|--------|-------|
| `id` | automated_signals | Identity column |
| `trade_id` | automated_signals | Standardize to VARCHAR(64) |
| `event_type` | automated_signals | Standardize to VARCHAR(32) |
| `timestamp` | automated_signals | Convert BIGINT → TIMESTAMPTZ |
| `direction` | automated_signals | Standardize to VARCHAR(16) |
| `session` | automated_signals | Keep VARCHAR(20) |
| `bias` | automated_signals | Standardize to VARCHAR(32) |
| `entry_price` | automated_signals | Convert to NUMERIC(12,4) |
| `stop_loss` | automated_signals | Convert to NUMERIC(12,4) |
| `current_price` | automated_signals | Convert to NUMERIC(12,4) |
| `exit_price` | automated_signals | Convert to NUMERIC(12,4) |
| `mfe` | automated_signals | Keep NUMERIC(10,4) |
| `no_be_mfe` | automated_signals | Convert FLOAT → NUMERIC(10,4) |
| `be_mfe` | automated_signals | Convert FLOAT → NUMERIC(10,4) |
| `final_mfe` | automated_signals | Keep NUMERIC(10,4) |
| `risk_distance` | automated_signals | Convert to NUMERIC(12,4) |

### 2.2 MOVE Fields (To JSONB or Other Tables)

| Field | Source | Destination | Rationale |
|-------|--------|-------------|-----------|
| `target_1r` | automated_signals | `targets` JSONB | Consolidate R-targets |
| `target_2r` | automated_signals | `targets` JSONB | Consolidate R-targets |
| `target_3r` | automated_signals | `targets` JSONB | Consolidate R-targets |
| `target_5r` | automated_signals | `targets` JSONB | Consolidate R-targets |
| `target_10r` | automated_signals | `targets` JSONB | Consolidate R-targets |
| `target_20r` | automated_signals | `targets` JSONB | Consolidate R-targets |
| `account_size` | automated_signals | `telemetry` JSONB | Position sizing metadata |
| `risk_percent` | automated_signals | `telemetry` JSONB | Position sizing metadata |
| `contracts` | automated_signals | `telemetry` JSONB | Position sizing metadata |
| `risk_amount` | automated_signals | `telemetry` JSONB | Position sizing metadata |
| `lifecycle_state` | automated_signals | H2 lifecycle table | State machine (future) |
| `lifecycle_seq` | automated_signals | H2 lifecycle table | State machine (future) |
| `lifecycle_entered_at` | automated_signals | H2 lifecycle table | State machine (future) |
| `lifecycle_updated_at` | automated_signals | H2 lifecycle table | State machine (future) |

### 2.3 DELETE Fields (Legacy/Unused)

| Field | Reason |
|-------|--------|
| `created_at` | Redundant with `timestamp` |

---

## 3. Lifecycle Constraints

### 3.1 Valid Event Types

| Event Type | Description | Required Fields |
|------------|-------------|-----------------|
| `ENTRY` | Trade entry confirmed | `trade_id`, `timestamp`, `direction`, `session`, `entry_price`, `stop_loss`, `risk_distance`, `targets` |
| `MFE_UPDATE` | MFE value updated | `trade_id`, `timestamp`, `current_price`, `mfe`, `be_mfe`, `no_be_mfe` |
| `BE_TRIGGERED` | Break-even triggered (+1R) | `trade_id`, `timestamp`, `current_price`, `be_mfe` |
| `EXIT_TARGET` | Exit at target | `trade_id`, `timestamp`, `exit_price`, `final_mfe` |
| `EXIT_SL` | Exit at stop loss | `trade_id`, `timestamp`, `exit_price`, `final_mfe` |

### 3.2 Event Ordering Rules

```
ENTRY → MFE_UPDATE* → (BE_TRIGGERED)? → (EXIT_TARGET | EXIT_SL)
```

**Constraints:**
1. Every trade MUST start with exactly one `ENTRY` event
2. `MFE_UPDATE` events can occur 0 or more times after `ENTRY`
3. `BE_TRIGGERED` can occur 0 or 1 time (only for BE=1 strategy)
4. Every trade MUST end with exactly one exit event (`EXIT_TARGET` or `EXIT_SL`)
5. No events allowed after exit event for same `trade_id`

### 3.3 Trade ID Invariants

| Rule | Description |
|------|-------------|
| **Format** | `YYYYMMDD_HHMMSS_DIRECTION` (e.g., `20251129_143052_Bullish`) |
| **Uniqueness** | `trade_id` + `event_type` + `timestamp` must be unique |
| **Immutability** | `trade_id` cannot change once assigned |
| **Consistency** | All events for a trade must have identical `trade_id` |

---

## 4. ML Compatibility Requirements

### 4.1 Required Data for Feature Extraction

| Feature Category | Required Columns | Notes |
|------------------|------------------|-------|
| **Price Features** | `entry_price`, `stop_loss`, `current_price`, `exit_price` | Must be NUMERIC for calculations |
| **MFE Features** | `mfe`, `be_mfe`, `no_be_mfe`, `final_mfe` | Must be NUMERIC(10,4) |
| **Risk Features** | `risk_distance`, `targets->>'1R'` | Used for R-multiple calculations |
| **Classification** | `direction`, `session`, `bias` | Categorical features |
| **Temporal** | `timestamp`, `signal_date`, `signal_time` | Time-based features |

### 4.2 Numeric Column Requirements

These columns MUST remain as NUMERIC types (not JSONB):

```
entry_price, stop_loss, current_price, exit_price,
mfe, be_mfe, no_be_mfe, final_mfe, risk_distance
```

**Rationale:** ML feature extraction requires direct numeric operations (AVG, SUM, statistical functions).

### 4.3 Telemetry Requirements for ML

The `telemetry` JSONB must include:

```json
{
    "signal_strength": 0.85,    // Required for confidence scoring
    "htf_aligned": true,        // Required for alignment features
    "atr": 25.50,               // Required for volatility normalization
    "volatility": 0.0125        // Required for regime detection
}
```

---

## 5. Execution Engine Compatibility (H2/H13)

### 5.1 Pre-Trade Check Fields

The execution engine (H13) requires these fields for pre-trade validation:

| Field | Purpose |
|-------|---------|
| `entry_price` | Order price validation |
| `stop_loss` | Risk limit validation |
| `risk_distance` | Position sizing calculation |
| `telemetry->>'account_size'` | Account balance check |
| `telemetry->>'risk_percent'` | Risk percentage validation |
| `telemetry->>'contracts'` | Contract limit check |
| `session` | Session filter validation |
| `direction` | Order direction |

### 5.2 Execution Engine Read Requirements

```sql
-- Execution engine query pattern
SELECT 
    trade_id,
    direction,
    entry_price,
    stop_loss,
    risk_distance,
    telemetry->>'account_size' as account_size,
    telemetry->>'risk_percent' as risk_percent,
    telemetry->>'contracts' as contracts
FROM automated_signals_v2
WHERE event_type = 'ENTRY'
  AND trade_id = $1;
```

### 5.3 Execution Tasks Integration

The `execution_tasks` table (H13) references `automated_signals_v2`:

```sql
-- execution_tasks.trade_id → automated_signals_v2.trade_id
-- No foreign key (loose coupling for resilience)
```

---

## 6. Dashboard & Analytics Compatibility

### 6.1 Automated Signals Ultra Dashboard

| Field | Usage |
|-------|-------|
| `trade_id` | Trade identification |
| `event_type` | Lifecycle state display |
| `timestamp` | Timeline visualization |
| `direction` | Bullish/Bearish indicator |
| `session` | Session badge |
| `entry_price` | Entry price display |
| `stop_loss` | Stop loss display |
| `current_price` | Live price (MFE_UPDATE events) |
| `mfe`, `be_mfe`, `no_be_mfe` | MFE gauges |
| `final_mfe` | Final outcome display |
| `targets` | R-target progress bars |

### 6.2 Main Dashboard (Homepage)

| Field | Usage |
|-------|-------|
| `trade_id` | Trade count |
| `event_type` | Active vs completed filtering |
| `session` | Session breakdown |
| `direction` | Win/loss by direction |
| `final_mfe` | Performance metrics |
| `signal_date` | Date filtering |

### 6.3 Lifecycle View

| Field | Usage |
|-------|-------|
| `trade_id` | Trade grouping |
| `event_type` | Event sequence |
| `timestamp` | Event timeline |
| `mfe`, `be_mfe`, `no_be_mfe` | MFE progression |
| `current_price` | Price journey |

---

## 7. Final SQL Schema

```sql
-- ════════════════════════════════════════════════════════════════════
-- AUTOMATED_SIGNALS_V2 - H1.7 Foundation Schema
-- ════════════════════════════════════════════════════════════════════
-- This is the AUTHORITATIVE schema for the automated signals table.
-- All lifecycle events for every trade are stored here.
-- ════════════════════════════════════════════════════════════════════

-- Drop existing table if recreating (CAUTION: data loss)
-- DROP TABLE IF EXISTS automated_signals_v2;

CREATE TABLE automated_signals_v2 (
    -- Identity
    id                  SERIAL PRIMARY KEY,
    
    -- Core Trade Identification (Required)
    trade_id            VARCHAR(64) NOT NULL,
    event_type          VARCHAR(32) NOT NULL,
    
    -- Timestamps
    timestamp           TIMESTAMPTZ NOT NULL,
    signal_date         DATE,
    signal_time         TIMETZ,
    
    -- Trade Classification
    direction           VARCHAR(16),
    session             VARCHAR(20),
    bias                VARCHAR(32),
    
    -- Price Data
    entry_price         NUMERIC(12,4),
    stop_loss           NUMERIC(12,4),
    current_price       NUMERIC(12,4),
    exit_price          NUMERIC(12,4),
    
    -- MFE Tracking
    mfe                 NUMERIC(10,4),
    no_be_mfe           NUMERIC(10,4),
    be_mfe              NUMERIC(10,4),
    final_mfe           NUMERIC(10,4),
    
    -- Risk Calculation
    risk_distance       NUMERIC(12,4),
    
    -- Structured Data (JSONB)
    targets             JSONB,
    telemetry           JSONB
);

-- ════════════════════════════════════════════════════════════════════
-- INDEXES
-- ════════════════════════════════════════════════════════════════════

-- Primary lookup index
CREATE INDEX idx_asv2_trade_id 
    ON automated_signals_v2(trade_id);

-- Time-series queries
CREATE INDEX idx_asv2_timestamp 
    ON automated_signals_v2(timestamp DESC);

-- Event type filtering
CREATE INDEX idx_asv2_event_type 
    ON automated_signals_v2(event_type);

-- Session analysis
CREATE INDEX idx_asv2_session_timestamp 
    ON automated_signals_v2(session, timestamp DESC);

-- Date partitioning support
CREATE INDEX idx_asv2_signal_date 
    ON automated_signals_v2(signal_date);

-- Direction filtering
CREATE INDEX idx_asv2_direction 
    ON automated_signals_v2(direction);

-- Composite index for dashboard queries
CREATE INDEX idx_asv2_trade_event 
    ON automated_signals_v2(trade_id, event_type, timestamp DESC);

-- ════════════════════════════════════════════════════════════════════
-- CONSTRAINTS
-- ════════════════════════════════════════════════════════════════════

-- Event type validation
ALTER TABLE automated_signals_v2 
ADD CONSTRAINT chk_event_type 
CHECK (event_type IN ('ENTRY', 'MFE_UPDATE', 'BE_TRIGGERED', 'EXIT_TARGET', 'EXIT_SL'));

-- Direction validation
ALTER TABLE automated_signals_v2 
ADD CONSTRAINT chk_direction 
CHECK (direction IS NULL OR direction IN ('Bullish', 'Bearish'));

-- Session validation
ALTER TABLE automated_signals_v2 
ADD CONSTRAINT chk_session 
CHECK (session IS NULL OR session IN ('ASIA', 'LONDON', 'NY PRE', 'NY AM', 'NY LUNCH', 'NY PM'));

-- ════════════════════════════════════════════════════════════════════
-- COMMENTS
-- ════════════════════════════════════════════════════════════════════

COMMENT ON TABLE automated_signals_v2 IS 
    'H1.7 Foundation: Lifecycle event store for all automated trades';

COMMENT ON COLUMN automated_signals_v2.trade_id IS 
    'Unique trade identifier (format: YYYYMMDD_HHMMSS_DIRECTION)';

COMMENT ON COLUMN automated_signals_v2.event_type IS 
    'Event type: ENTRY, MFE_UPDATE, BE_TRIGGERED, EXIT_TARGET, EXIT_SL';

COMMENT ON COLUMN automated_signals_v2.timestamp IS 
    'Event timestamp with timezone (America/New_York)';

COMMENT ON COLUMN automated_signals_v2.targets IS 
    'JSONB containing R-multiple price targets (1R through 20R)';

COMMENT ON COLUMN automated_signals_v2.telemetry IS 
    'JSONB containing position sizing and market context metadata';
```

---

## 8. Migration Plan

### 8.1 Step 1: Create New Table

```sql
-- Execute on Railway PostgreSQL
-- This creates the new table without affecting existing data

CREATE TABLE automated_signals_v2 (
    id                  SERIAL PRIMARY KEY,
    trade_id            VARCHAR(64) NOT NULL,
    event_type          VARCHAR(32) NOT NULL,
    timestamp           TIMESTAMPTZ NOT NULL,
    signal_date         DATE,
    signal_time         TIMETZ,
    direction           VARCHAR(16),
    session             VARCHAR(20),
    bias                VARCHAR(32),
    entry_price         NUMERIC(12,4),
    stop_loss           NUMERIC(12,4),
    current_price       NUMERIC(12,4),
    exit_price          NUMERIC(12,4),
    mfe                 NUMERIC(10,4),
    no_be_mfe           NUMERIC(10,4),
    be_mfe              NUMERIC(10,4),
    final_mfe           NUMERIC(10,4),
    risk_distance       NUMERIC(12,4),
    targets             JSONB,
    telemetry           JSONB
);

-- Create indexes
CREATE INDEX idx_asv2_trade_id ON automated_signals_v2(trade_id);
CREATE INDEX idx_asv2_timestamp ON automated_signals_v2(timestamp DESC);
CREATE INDEX idx_asv2_event_type ON automated_signals_v2(event_type);
CREATE INDEX idx_asv2_session_timestamp ON automated_signals_v2(session, timestamp DESC);
```

### 8.2 Step 2: Dual-Write Option

```python
# In webhook handler (web_server.py)
# Write to BOTH tables during transition period

def handle_automated_signal_webhook(payload):
    # Parse and validate payload
    event_data = parse_webhook_payload(payload)
    
    # Write to old table (existing logic)
    insert_to_automated_signals(event_data)
    
    # Write to new table (parallel)
    insert_to_automated_signals_v2(event_data)
    
    return {"status": "success", "dual_write": True}
```

**Duration:** 1-2 weeks of parallel writes to validate data consistency.

### 8.3 Step 3: Backfill Script Outline

```sql
-- Backfill historical data from automated_signals to automated_signals_v2
-- Run during low-traffic period (weekend)

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
    -- Extract date
    (to_timestamp(timestamp / 1000.0) AT TIME ZONE 'America/New_York')::DATE,
    -- Extract time
    (to_timestamp(timestamp / 1000.0) AT TIME ZONE 'America/New_York')::TIMETZ,
    direction,
    session,
    bias,
    entry_price::NUMERIC(12,4),
    stop_loss::NUMERIC(12,4),
    current_price::NUMERIC(12,4),
    exit_price::NUMERIC(12,4),
    mfe::NUMERIC(10,4),
    no_be_mfe::NUMERIC(10,4),
    be_mfe::NUMERIC(10,4),
    final_mfe::NUMERIC(10,4),
    risk_distance::NUMERIC(12,4),
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
WHERE trade_id NOT IN (SELECT DISTINCT trade_id FROM automated_signals_v2);
```

### 8.4 Step 4: Swap Active References

```python
# Phase 4A: Update API endpoints to read from v2
# File: web_server.py

# Before:
# cursor.execute("SELECT * FROM automated_signals WHERE ...")

# After:
# cursor.execute("SELECT * FROM automated_signals_v2 WHERE ...")
```

```python
# Phase 4B: Update webhook handler to write to v2 only
# Remove dual-write logic

def handle_automated_signal_webhook(payload):
    event_data = parse_webhook_payload(payload)
    insert_to_automated_signals_v2(event_data)  # V2 only
    return {"status": "success"}
```

### 8.5 Step 5: Archive Old Table

```sql
-- Phase 5A: Rename tables (final cutover)
ALTER TABLE automated_signals RENAME TO automated_signals_legacy;
ALTER TABLE automated_signals_v2 RENAME TO automated_signals;

-- Phase 5B: Drop legacy table (after 30-day validation period)
-- CAUTION: Irreversible
-- DROP TABLE automated_signals_legacy;
```

---

## 9. Migration Timeline

| Phase | Day | Description | Risk |
|-------|-----|-------------|------|
| **Step 1** | Day 1 | Create `automated_signals_v2` table | Low |
| **Step 2** | Days 2-14 | Dual-write period | Low |
| **Step 3** | Day 15 | Backfill historical data | Medium |
| **Step 4A** | Day 16 | Switch reads to v2 | Medium |
| **Step 4B** | Day 17 | Switch writes to v2 only | Medium |
| **Step 5A** | Day 18 | Rename tables | High |
| **Step 5B** | Day 48+ | Drop legacy table | High |

---

## 10. Validation Checklist

Before completing migration:

- [ ] Row counts match between old and new tables
- [ ] All `trade_id` values present in both tables
- [ ] Timestamp conversion verified (BIGINT → TIMESTAMPTZ)
- [ ] JSONB consolidation verified (`targets`, `telemetry`)
- [ ] API endpoints return identical data
- [ ] Ultra dashboard displays correctly
- [ ] Main dashboard displays correctly
- [ ] WebSocket events work correctly
- [ ] ML feature extraction works correctly
- [ ] No data loss during dual-write period
- [ ] Execution engine queries work correctly

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-29 | System | Initial specification |

---

**Status:** DOCUMENTATION ONLY - NO APPLICATION FILES MODIFIED
