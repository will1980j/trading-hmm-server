# ✅ Step 3 Complete - Indicator Export Importer Added

## Files Created/Modified

### 1. New Module Created
**File:** `services/indicator_export_importer.py`
**Purpose:** Idempotent importer for INDICATOR_EXPORT_V2 batches

### 2. File Modified
**File:** `automated_signals_api_robust.py`
**Added:** Import route `POST /api/indicator-export/import/<batch_id>`

## Importer Function

### import_indicator_export_v2(batch_id: int) -> dict

**Purpose:** Import INDICATOR_EXPORT_V2 batch into confirmed_signals_ledger

**Process:**
1. Load batch payload_json from indicator_export_batches by id
2. For each signal in payload.signals:
   - Validate required fields (trade_id, triangle_time, direction)
   - Coerce numeric fields safely (entry, stop, be_mfe, no_be_mfe, mae)
   - Ensure mae <= 0.0 (clamp and log warning if > 0)
   - Parse date string to date object
   - Upsert into confirmed_signals_ledger using trade_id
3. Return counts: inserted, updated, skipped_invalid

**Logging:**
- `[INDICATOR_IMPORT_V2]` prefix on all logs
- ✅ Batch loaded
- ✅ Signal counts
- ✅ MAE clamping warnings
- ✅ Validation errors
- ✅ Insert/update counts
- ✅ Database errors

**Idempotent:**
- Uses `ON CONFLICT (trade_id) DO UPDATE`
- Safe to re-run on same batch
- Updates existing records with latest data
- Returns (xmax = 0) to detect insert vs update

## API Route

### POST /api/indicator-export/import/<batch_id>

**Purpose:** Lightweight route to trigger import of a specific batch

**Request:**
```bash
POST /api/indicator-export/import/123
```

**Response (Success):**
```json
{
  "success": true,
  "batch_id": 123,
  "inserted": 10,
  "updated": 5,
  "skipped_invalid": 0,
  "total_processed": 15
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "error details",
  "inserted": 0,
  "updated": 0,
  "skipped_invalid": 0
}
```

## Importer Code

```python
def import_indicator_export_v2(batch_id: int) -> dict:
    """Import INDICATOR_EXPORT_V2 batch into confirmed_signals_ledger."""
    
    # Load batch payload
    # For each signal:
    #   - Validate required fields
    #   - Coerce numeric fields
    #   - Clamp MAE to <= 0.0
    #   - Upsert into confirmed_signals_ledger
    # Return counts
```

**Key Features:**
- Validates required fields (trade_id, triangle_time, direction)
- Safe numeric coercion (handles None, invalid values)
- MAE clamping with warning logs
- Idempotent upserts (ON CONFLICT DO UPDATE)
- Comprehensive logging
- Returns detailed counts

## Route Code

```python
@app.route('/api/indicator-export/import/<int:batch_id>', methods=['POST'])
def import_indicator_batch(batch_id):
    """Import a specific batch into confirmed_signals_ledger."""
    from services.indicator_export_importer import import_indicator_export_v2
    
    result = import_indicator_export_v2(batch_id)
    
    if result.get('success'):
        return jsonify(result), 200
    else:
        return jsonify(result), 500
```

## Testing

### Test Import Flow:

**Step 1: Send batch to webhook**
```bash
curl -X POST https://web-production-f8c3.up.railway.app/api/indicator-export \
  -H "Content-Type: application/json" \
  -d @test_batch.json
```

**Response:**
```json
{"status": "success", "batch_id": 123, ...}
```

**Step 2: Trigger import**
```bash
curl -X POST https://web-production-f8c3.up.railway.app/api/indicator-export/import/123
```

**Response:**
```json
{"success": true, "inserted": 10, "updated": 5, ...}
```

**Step 3: Verify data**
```sql
SELECT * FROM confirmed_signals_ledger ORDER BY triangle_time_ms DESC LIMIT 10;
```

## Validation Rules

### Required Fields
- `trade_id` - Must be present
- `triangle_time` - Must be present
- `direction` - Must be present

### Numeric Fields (Safe Coercion)
- `entry` - Coerced to float or None
- `stop` - Coerced to float or None
- `be_mfe` - Coerced to float or None
- `no_be_mfe` - Coerced to float or None
- `mae` - Coerced to float or None, clamped to <= 0.0

### Optional Fields
- `confirmation_time` - Can be None
- `date` - Parsed from string, can be None
- `session` - Can be None
- `completed` - Defaults to False

## Error Handling

### Invalid Signals
- Missing required fields → Skip with warning
- Invalid numeric values → Store as None
- MAE > 0 → Clamp to 0.0 with warning

### Database Errors
- Connection failures → Return 500
- Query errors → Rollback and return 500
- All errors logged

### Idempotency
- Duplicate batches → Handled by webhook endpoint
- Duplicate trade_ids → Updated with latest data
- Safe to re-run imports

## Next Steps

After deployment:
1. **Run migration** - Create tables
2. **Deploy code** - Push to Railway
3. **Test webhook** - Send test batch
4. **Test import** - Trigger import via API
5. **Verify data** - Check confirmed_signals_ledger
6. **Step 4** - Add ALL_SIGNALS_EXPORT importer
7. **Step 5** - Auto-trigger imports on webhook receipt

## Notes

- Importer is idempotent (safe to re-run)
- MAE validation ensures data quality
- Comprehensive logging for debugging
- Returns detailed counts for monitoring
- No data loss (skipped signals logged)

**Importer ready for deployment.** 🚀
