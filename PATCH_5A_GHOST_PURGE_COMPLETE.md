# ✅ PATCH 5A: Ghost Trade Purge Endpoint Complete

## Endpoint Added: `/api/automated-signals/purge-ghosts`

### Purpose
Removes malformed "ghost" trades from the `automated_signals` table that:
- Have NULL or empty `trade_id`
- Have legacy comma-separated `trade_id` format
- Show up in dashboard but fail detail queries with 404
- Cannot be deleted through normal delete operations

---

## Implementation Details

### Location
**File:** `web_server.py`
**Line:** ~11275 (after bulk-delete endpoint)

### Route Definition
```python
@app.route('/api/automated-signals/purge-ghosts', methods=['POST'])
@login_required
def purge_ghost_trades():
```

### Ghost Trade Criteria
Identifies and deletes rows where:
1. `trade_id IS NULL`
2. `trade_id = ''` (empty string)
3. `trade_id LIKE '%,%'` (contains commas - legacy format)

### SQL Query
```sql
SELECT id
FROM automated_signals
WHERE trade_id IS NULL
   OR trade_id = ''
   OR trade_id LIKE '%,%'
```

### Deletion Method
- Collects all ghost row IDs first
- Performs bulk delete by primary key using `id = ANY(%s)`
- Commits transaction
- Returns count of deleted rows

---

## API Specification

### Request
**Method:** `POST`
**URL:** `/api/automated-signals/purge-ghosts`
**Auth:** Required (`@login_required`)
**Body:** None (no parameters needed)

### Response (Success)
```json
{
  "success": true,
  "deleted": 42,
  "criteria": {
    "trade_id_null_or_empty": true,
    "trade_id_contains_commas": true
  }
}
```
**Status Code:** `200`

### Response (Error)
```json
{
  "success": false,
  "error": "Error message here"
}
```
**Status Code:** `500`

---

## Usage

### From Frontend (JavaScript)
```javascript
async function purgeGhostTrades() {
    try {
        const response = await fetch('/api/automated-signals/purge-ghosts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log(`Purged ${result.deleted} ghost trades`);
            // Refresh dashboard
            loadDashboardData();
        } else {
            console.error('Purge failed:', result.error);
        }
    } catch (error) {
        console.error('Purge request failed:', error);
    }
}
```

### From Python (Testing)
```python
import requests

response = requests.post(
    'https://web-production-cd33.up.railway.app/api/automated-signals/purge-ghosts',
    headers={'Content-Type': 'application/json'}
)

result = response.json()
print(f"Deleted {result['deleted']} ghost trades")
```

### From cURL
```bash
curl -X POST \
  https://web-production-cd33.up.railway.app/api/automated-signals/purge-ghosts \
  -H "Content-Type: application/json" \
  -b cookies.txt
```

---

## Error Handling

### Database Connection Failure
```json
{
  "success": false,
  "error": "DATABASE_URL not configured"
}
```

### SQL Execution Error
```json
{
  "success": false,
  "error": "SQL error details"
}
```

### Logging
All errors logged with full stack trace:
```python
logger.error(f"Ghost purge error: {str(e)}", exc_info=True)
```

---

## Safety Features

1. **Authentication Required:** `@login_required` decorator prevents unauthorized access
2. **Transaction Safety:** Uses commit/rollback for data integrity
3. **Selective Deletion:** Only deletes rows matching specific ghost criteria
4. **ID-Based Deletion:** Uses primary key for precise targeting
5. **Logging:** All operations logged for audit trail

---

## Testing Checklist

- [ ] Endpoint accessible at `/api/automated-signals/purge-ghosts`
- [ ] Requires authentication (401 without login)
- [ ] Returns correct JSON structure
- [ ] Deletes NULL trade_id rows
- [ ] Deletes empty string trade_id rows
- [ ] Deletes comma-containing trade_id rows
- [ ] Returns accurate deleted count
- [ ] Logs operations correctly
- [ ] Handles database errors gracefully
- [ ] Dashboard refreshes after purge

---

## Integration with Dashboard

### Add Purge Button
```html
<button onclick="purgeGhostTrades()" class="btn btn-warning">
    <i class="fas fa-ghost"></i> Purge Ghost Trades
</button>
```

### Add Confirmation Dialog
```javascript
function confirmPurgeGhosts() {
    if (confirm('This will permanently delete all malformed trades. Continue?')) {
        purgeGhostTrades();
    }
}
```

---

## Deployment Status

**Status:** ✅ READY FOR DEPLOYMENT

**Changes Made:**
- Added new endpoint to `web_server.py`
- No database schema changes required
- No frontend changes required (optional enhancement)

**Next Steps:**
1. Commit changes to Git
2. Push to GitHub (triggers Railway auto-deploy)
3. Test endpoint on production
4. Optionally add UI button to dashboard

---

## Verification

After deployment, verify with:
```bash
# Check endpoint exists
curl -X POST https://web-production-cd33.up.railway.app/api/automated-signals/purge-ghosts

# Should return authentication error (expected)
# Then test with authenticated session
```

**Expected Result:** Ghost trades removed, dashboard shows clean data.
