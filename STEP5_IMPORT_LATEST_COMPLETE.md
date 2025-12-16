# ✅ Step 5 Complete - Import Latest Endpoint Added

## File Modified
**File:** `automated_signals_api_robust.py`
**Route Added:** `POST /api/indicator-export/import-latest`

## Route Code

```python
@app.route('/api/indicator-export/import-latest', methods=['POST'])
def import_latest_indicator_data():
    """
    Import latest valid batches for both INDICATOR_EXPORT_V2 and ALL_SIGNALS_EXPORT.
    Finds most recent valid batch for each type and imports them.
    """
    import psycopg2
    from services.indicator_export_importer import import_indicator_export_v2, import_all_signals_export
    
    logger.info("[INDICATOR_IMPORT_LATEST] Starting import of latest batches")
    
    # Find latest INDICATOR_EXPORT_V2 batch (is_valid=true)
    # Find latest ALL_SIGNALS_EXPORT batch (is_valid=true)
    # Call both importers
    # Return combined response
```

## Behavior

1. **Find Latest Batches:**
   - Query `indicator_export_batches` for latest `INDICATOR_EXPORT_V2` where `is_valid=true`
   - Query `indicator_export_batches` for latest `ALL_SIGNALS_EXPORT` where `is_valid=true`

2. **Import Both:**
   - Call `import_indicator_export_v2(batch_id)` if found
   - Call `import_all_signals_export(batch_id)` if found

3. **Return Combined Response:**
   - Includes batch_ids and results for both imports
   - Shows counts for each import

## Response Example

### Success Response:
```json
{
  "success": true,
  "confirmed_signals": {
    "batch_id": 45,
    "result": {
      "success": true,
      "batch_id": 45,
      "inserted": 10,
      "updated": 290,
      "skipped_invalid": 0,
      "total_processed": 300
    }
  },
  "all_signals": {
    "batch_id": 78,
    "result": {
      "success": true,
      "batch_id": 78,
      "inserted": 50,
      "updated": 1526,
      "skipped_invalid": 0,
      "total_processed": 1576
    }
  }
}
```

### Partial Success (Only One Batch Found):
```json
{
  "success": true,
  "confirmed_signals": {
    "batch_id": 45,
    "result": {...}
  },
  "all_signals": null
}
```

### Error Response:
```json
{
  "success": false,
  "error": "error details"
}
```

## Logging

All logs use `[INDICATOR_IMPORT_LATEST]` prefix:
- ✅ Starting import
- ✅ Found batch IDs
- ✅ Importing each batch
- ✅ Import complete with results
- ✅ Errors

## Usage

### Manual Trigger:
```bash
curl -X POST https://web-production-f8c3.up.railway.app/api/indicator-export/import-latest
```

### From Dashboard:
```javascript
// "Import Now" button
async function importLatestData() {
    const response = await fetch('/api/indicator-export/import-latest', {
        method: 'POST'
    });
    const result = await response.json();
    console.log('Import complete:', result);
}
```

### Automated (Cron/Scheduler):
```python
# Run every 5 minutes
import requests
response = requests.post('https://web-production-f8c3.up.railway.app/api/indicator-export/import-latest')
print(response.json())
```

## Features

- ✅ Finds latest valid batches automatically
- ✅ Imports both confirmed and all signals
- ✅ Returns combined results
- ✅ Handles missing batches gracefully
- ✅ Comprehensive logging
- ✅ Single endpoint for complete import

## Testing

### Test Flow:
1. **Send exports from indicator** (creates batches)
2. **Call import-latest endpoint**
3. **Check response** (should show counts)
4. **Verify data** (query ledger tables)

### Verification Queries:
```sql
-- Check latest batches
SELECT id, event_type, batch_number, received_at, is_valid
FROM indicator_export_batches
WHERE is_valid = true
ORDER BY received_at DESC
LIMIT 10;

-- Check confirmed signals
SELECT COUNT(*), MAX(updated_at) 
FROM confirmed_signals_ledger;

-- Check all signals
SELECT COUNT(*), MAX(updated_at) 
FROM all_signals_ledger;
```

## Next Steps

After deployment:
1. **Run migration** - Create tables
2. **Deploy code** - Push to Railway
3. **Test webhook** - Send batches from indicator
4. **Test import-latest** - Trigger import
5. **Verify data** - Check ledger tables
6. **Add to dashboard** - "Import Now" button
7. **Optional:** Auto-trigger on webhook receipt

## Summary

**Complete Import System:**
- ✅ Webhook endpoint receives batches
- ✅ Raw storage in indicator_export_batches
- ✅ Importer for INDICATOR_EXPORT_V2
- ✅ Importer for ALL_SIGNALS_EXPORT
- ✅ Import-latest convenience endpoint
- ✅ All idempotent and logged

**Ready for deployment and testing.** 🚀
