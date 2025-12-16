# Indicator Export Tables - Canonical Reference

## Table Names (Final)

All code uses these exact table names consistently:

### 1. indicator_export_batches
**Purpose:** Raw batch storage (immutable audit trail)
**Schema:** `database/indicator_export_schema.sql`
**Type:** Append-only, deduplication via SHA256

**Columns:**
- `id` (BIGSERIAL PK)
- `received_at` (TIMESTAMPTZ)
- `source` (TEXT, default 'tradingview')
- `event_type` (TEXT) - INDICATOR_EXPORT_V2 or ALL_SIGNALS_EXPORT
- `batch_number` (INTEGER)
- `batch_size` (INTEGER)
- `total_signals` (INTEGER)
- `payload_json` (JSONB) - Full request body
- `payload_sha256` (TEXT) - Deduplication hash
- `is_valid` (BOOLEAN)
- `validation_error` (TEXT)

**Unique Constraint:** (event_type, payload_sha256)

### 2. all_signals_ledger
**Purpose:** Canonical All Signals table (triangle-keyed)
**Schema:** `database/indicator_export_schema.sql`
**Type:** Upsert by trade_id

**Columns:**
- `trade_id` (TEXT PK) - Triangle-canonical ID
- `triangle_time_ms` (BIGINT) - When triangle appeared
- `confirmation_time_ms` (BIGINT) - When confirmed
- `direction` (TEXT) - Bullish/Bearish
- `status` (TEXT) - PENDING/CONFIRMED/CANCELLED/COMPLETED
- `bars_to_confirm` (INTEGER)
- `session` (TEXT)
- `entry_price` (NUMERIC)
- `stop_loss` (NUMERIC)
- `risk_points` (NUMERIC)
- `htf_daily` (TEXT)
- `htf_4h` (TEXT)
- `htf_1h` (TEXT)
- `htf_15m` (TEXT)
- `htf_5m` (TEXT)
- `htf_1m` (TEXT)
- `last_seen_batch_id` (BIGINT FK)
- `updated_at` (TIMESTAMPTZ)

### 3. confirmed_signals_ledger
**Purpose:** Canonical Confirmed Signals table with MFE/MAE
**Schema:** `database/indicator_export_schema.sql`
**Type:** Upsert by trade_id

**Columns:**
- `trade_id` (TEXT PK) - Triangle-canonical ID
- `triangle_time_ms` (BIGINT)
- `confirmation_time_ms` (BIGINT)
- `date` (DATE)
- `session` (TEXT)
- `direction` (TEXT)
- `entry` (NUMERIC)
- `stop` (NUMERIC)
- `be_mfe` (NUMERIC)
- `no_be_mfe` (NUMERIC)
- `mae` (NUMERIC)
- `completed` (BOOLEAN)
- `last_seen_batch_id` (BIGINT FK)
- `updated_at` (TIMESTAMPTZ)

## Existing Tables (Not Modified)

### automated_signals
**Purpose:** Event-based storage (multiple rows per trade_id)
**Schema:** `database/add_automated_signal_support.sql`
**Type:** Append-only events
**Status:** Still in use for Active/Completed trades (not changed)

### data_quality_reconciliations
**Purpose:** Reconciliation run records
**Schema:** `database/data_quality_schema.sql`
**Type:** Append-only
**Status:** Reused for indicator reconciliation

### data_quality_conflicts
**Purpose:** Data quality issues
**Schema:** `database/data_quality_schema.sql`
**Type:** Append-only
**Status:** Reused for indicator conflicts

## Usage by Module

### services/indicator_export_importer.py
- Reads: `indicator_export_batches`
- Writes: `confirmed_signals_ledger`, `all_signals_ledger`

### services/indicator_reconciliation.py
- Reads: `all_signals_ledger`, `confirmed_signals_ledger`
- Writes: `data_quality_reconciliations`, `data_quality_conflicts`

### automated_signals_api_robust.py
- Reads: All tables
- Writes: `indicator_export_batches` (webhook endpoint)

## Verification

All table names verified consistent across:
- ✅ Schema definitions
- ✅ Importer code
- ✅ Reconciliation code
- ✅ API endpoints
- ✅ Migration scripts

## Migration

Run once to create tables:
```bash
python database/run_indicator_export_migration.py
```

## Data Flow

```
TradingView Indicator
    ↓ (webhook)
indicator_export_batches (raw)
    ↓ (import)
all_signals_ledger + confirmed_signals_ledger (canonical)
    ↓ (query)
Dashboard APIs
    ↓ (display)
Frontend UI
```

## Notes

- All table names use underscore convention
- All use `_ledger` suffix for canonical tables
- All use `_batches` suffix for raw storage
- No naming conflicts or variations
- Consistent across all modules

**Table names verified consistent. System ready for deployment.** 🚀
