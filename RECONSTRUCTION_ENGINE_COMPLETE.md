# ✅ RECONSTRUCTION ENGINE PATCH APPLIED — STRICT MODE VERIFIED

**File modified:** `web_server.py`

## Functions Added:

### 1. Helper Function: `reconstruct_automated_trades(limit=100, trade_id=None)` (~Line 11346)
**Location:** Immediately after `debug_automated_signals()` endpoint

**Purpose:** Read-only reconstruction engine that rebuilds per-trade lifecycle view from raw `automated_signals` events

**Key Features:**
- **Read-only:** NEVER mutates any database rows
- **Event grouping:** Groups all events by `trade_id` and rebuilds canonical trade view
- **Lifecycle-aware:** Uses `lifecycle_state` and `lifecycle_seq` when available
- **Ghost filtering:** Skips malformed trade_ids (NULL, empty, or containing commas)
- **Event timeline:** Preserves full event history for each trade
- **Max MFE tracking:** Tracks maximum BE and No-BE MFE values across all events

**Processing Logic:**
1. Fetches up to 2000 most recent events from `automated_signals`
2. Processes events oldest→newest to ensure first ENTRY and last EXIT win
3. Groups events by `trade_id` into trade objects
4. Captures canonical entry/exit prices and timestamps
5. Tracks max MFE values for both BE and No-BE strategies
6. Preserves latest lifecycle state using highest `lifecycle_seq`
7. Sorts trades by exit/entry timestamp (newest first)
8. Applies trade-level limit (default 100)
9. Derives high-level status from `lifecycle_state`

**Return Structure:**
```python
{
    "success": True/False,
    "count": <number of trades>,
    "trades": [
        {
            "trade_id": "...",
            "direction": "Bullish/Bearish",
            "session": "...",
            "bias": "...",
            "entry_price": <float>,
            "stop_loss": <float>,
            "exit_price": <float>,
            "entry_timestamp": "ISO timestamp",
            "exit_timestamp": "ISO timestamp",
            "final_be_mfe": <float>,
            "final_no_be_mfe": <float>,
            "max_no_be_mfe": <float>,
            "max_be_mfe": <float>,
            "lifecycle_state": "ACTIVE/EXITED",
            "lifecycle_seq": <int>,
            "lifecycle_entered_at": "ISO timestamp",
            "lifecycle_updated_at": "ISO timestamp",
            "status": "ACTIVE/COMPLETED",
            "events": [
                {
                    "id": <int>,
                    "event_type": "ENTRY/MFE_UPDATE/EXIT_*",
                    "timestamp": "ISO timestamp",
                    "mfe": <float>,
                    "be_mfe": <float>,
                    "no_be_mfe": <float>,
                    "exit_price": <float>,
                    "current_price": <float>
                }
            ]
        }
    ]
}
```

### 2. Public Endpoint: `/api/automated-signals/reconstruct` (GET) (~Line 11546)
**Location:** Immediately after `reconstruct_automated_trades()` helper

**Purpose:** Public API endpoint for accessing reconstructed trade lifecycle views

**Authentication:** `@login_required` decorator applied

**Query Parameters:**
- `trade_id` (optional): Filter to specific trade
- `limit` (optional): Max number of trades to return (default: 100)

**Response:** JSON with reconstructed trades (same structure as helper function)

**Error Handling:**
- Returns 500 status code on errors
- Logs errors with full traceback
- Returns structured error response with `success: False`

## Verification Checklist:

✅ **No existing functions modified** - Only added new code
✅ **No imports added** - Reuses existing `psycopg2`, `RealDictCursor`, `logger`
✅ **No renaming** - All existing code unchanged
✅ **No reformatting** - Only inserted new blocks
✅ **Correct insertion point** - After `debug_automated_signals()` as specified
✅ **Read-only operation** - NEVER mutates `automated_signals` table
✅ **Lifecycle-aware** - Uses `lifecycle_state` and `lifecycle_seq` columns
✅ **Ghost filtering** - Skips malformed trade_ids
✅ **Event preservation** - Full event timeline included in response
✅ **Defensive coding** - Handles NULL values, missing fields, type conversions
✅ **Error handling** - Try/finally with connection cleanup

## Integration Points:

### Trade Notebook Modal
The reconstruction endpoint can be called by the Trade Notebook modal to fetch complete trade lifecycle data:

```javascript
// In asOpenTradeNotebook(tradeId)
const resp = await fetch(`/api/automated-signals/reconstruct?trade_id=${encodeURIComponent(tradeId)}`);
const data = await resp.json();
if (data.success && data.trades.length > 0) {
    const trade = data.trades[0];
    // trade.events contains full timeline
    // trade.lifecycle_state, lifecycle_seq available
    // trade.max_no_be_mfe, max_be_mfe for diagnostics
}
```

### Ultra Dashboard
The reconstruction endpoint can replace or supplement the existing hub-data endpoint:

```javascript
// Alternative to /api/automated-signals/hub-data
const resp = await fetch('/api/automated-signals/reconstruct?limit=100');
const data = await resp.json();
if (data.success) {
    // data.trades contains lifecycle-aware trade objects
    // Each trade has full event timeline
    // Lifecycle state machine data included
}
```

### Diagnostics & Debugging
The reconstruction endpoint provides institutional-grade forensics:

```python
# Test reconstruction for specific trade
import requests
resp = requests.get(
    'https://web-production-cd33.up.railway.app/api/automated-signals/reconstruct',
    params={'trade_id': '20251121_143022_Bullish'},
    cookies={'session': 'your_session_cookie'}
)
data = resp.json()
print(f"Trade has {len(data['trades'][0]['events'])} events")
print(f"Lifecycle state: {data['trades'][0]['lifecycle_state']}")
print(f"Max No-BE MFE: {data['trades'][0]['max_no_be_mfe']}")
```

## Expected Behavior:

**Query all trades:**
```
GET /api/automated-signals/reconstruct?limit=50
→ Returns 50 most recent trades with full lifecycle data
```

**Query specific trade:**
```
GET /api/automated-signals/reconstruct?trade_id=20251121_143022_Bullish
→ Returns single trade with complete event timeline
```

**Error cases:**
- Missing DATABASE_URL → Returns error with success: False
- Database connection failure → Returns error with 500 status
- Malformed trade_id → Skipped in results (ghost filtering)
- No trades found → Returns empty trades array with success: True

## Files Modified:

- `web_server.py` - Added reconstruction helper + endpoint

## Files NOT Modified:

- No other files changed
- No existing functions modified
- No imports added (reuses existing)
- No database schema changes

The reconstruction engine provides institutional-grade, read-only trade lifecycle reconstruction with full event preservation and lifecycle state machine awareness.
